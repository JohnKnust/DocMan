#!/usr/bin/env python3
"""
DocMan CLI - Documentation Management Tool

A generic, example-driven Documentation Management CLI tool that can be dropped
into any monorepo to validate and maintain documentation standards.

Usage:
    python cli.py [OPTIONS] [REPO_PATH]

Options:
    --verbose, -v       Enable verbose output
    --fix              Batch auto-fix: create missing README files with confirmation
    --report           Generate detailed report
    --create-config    Create standardized .docmanrc.template with defaults
    --help, -h         Show this help message

Examples:
    python cli.py                    # Check current directory
    python cli.py /path/to/repo      # Check specific repository
    python cli.py --verbose --fix    # Check with verbose output and auto-fix
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import load_config, create_config_template
from src.utils import find_all_directories, find_all_markdown_files
from src.indexer import DocumentationIndexer
from src.reporter import Reporter, ValidationResult
from src.validators.readme_validator import ReadmeValidator
from src.validators.metadata_validator import MetadataValidator
from src.validators.link_validator import LinkValidator
from src.autofix import AutoFixer


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DocMan - Documentation Management CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:")[1] if "Usage:" in __doc__ else ""
    )
    
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to repository root (default: current directory)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Batch auto-fix: create missing README files with user confirmation"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report"
    )

    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create a standardized .docmanrc.template file with default settings"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (overrides search)"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point for DocMan CLI."""
    args = parse_arguments()

    # Handle config template creation
    if args.create_config:
        template_path = create_config_template()
        print(f"✅ Created standardized configuration template: {template_path}")
        print("📝 This template contains DocMan's recommended default settings")
        print("💡 Copy to .docmanrc in your project root and customize as needed")
        return 0

    # Initialize auto-fixer if needed
    auto_fixer = None
    if args.fix:
        # We'll initialize this after loading config
        pass

    # Load configuration with optional override
    if args.config:
        os.environ['DOCMAN_CONFIG'] = args.config
    config = load_config()

    # Initialize components
    repo_path = Path(args.repo_path).resolve()
    reporter = Reporter(verbose=args.verbose or config.verbose_output)
    indexer = DocumentationIndexer(repo_path, config.ignore_patterns)

    # Initialize auto-fixer if --fix option is used
    if args.fix:
        auto_fixer = AutoFixer(repo_path, config)

    if args.verbose or config.verbose_output:
        print(f"🔍 Analyzing repository: {repo_path}")

        # Show configuration status
        if hasattr(config, '_is_fallback') and config._is_fallback:
            print(f"🔄 Configuration: FALLBACK mode (using template)")
            print(f"💡 Create .docmanrc in project root for custom settings")
        elif hasattr(config, '_config_path'):
            print(f"⚙️  Configuration: {config._config_path}")

        print(f"📋 Using ignore patterns: {sorted(config.ignore_patterns)}")
    
    # Initialize validation results
    results = ValidationResult(
        missing_readmes=[],
        metadata_violations=[],
        broken_links=[],
        date_bumps=[],
        new_index_entries=[]
    )
    
    # Step 2: README Presence Validation
    verbose = args.verbose or config.verbose_output
    if verbose:
        print("📋 Checking README presence...")

    readme_validator = ReadmeValidator(repo_path, config.ignore_patterns)
    readme_violations = readme_validator.validate()
    results.missing_readmes = readme_violations

    if verbose and readme_violations:
        print(f"Found {len(readme_violations)} missing READMEs:")
        for violation in readme_violations:
            print(f"  {violation}")

    # Apply auto-fixes if requested
    if args.fix and auto_fixer and readme_violations:
        print("\n🔧 Auto-fix: Creating missing README files...")
        missing_dirs = auto_fixer.get_missing_readme_directories(readme_violations)
        created_count = auto_fixer.fix_missing_readmes(missing_dirs, interactive=True)

        if created_count > 0:
            # Re-run README validation to update results
            readme_violations = readme_validator.validate()
            results.missing_readmes = readme_violations
            print(f"📊 Updated validation: {len(readme_violations)} missing READMEs remaining")

    # Step 3: Metadata Format Enforcement
    if verbose:
        print("📋 Checking metadata format...")

    metadata_validator = MetadataValidator(repo_path, config.ignore_patterns, config)
    metadata_violations = metadata_validator.validate()
    results.metadata_violations = metadata_violations

    if verbose and metadata_violations:
        print(f"Found {len(metadata_violations)} metadata violations:")
        for violation in metadata_violations:
            print(f"  {violation}")

    # Step 4: Link & Date Integrity
    if verbose:
        print("🔗 Checking link integrity and date consistency...")

    link_validator = LinkValidator(repo_path, config.ignore_patterns)
    link_violations, date_issues = link_validator.validate()
    results.broken_links = link_violations
    results.date_bumps = date_issues  # Note: these are reports, not actual bumps

    if verbose and (link_violations or date_issues):
        if link_violations:
            print(f"Found {len(link_violations)} broken links:")
            for violation in link_violations:
                print(f"  {violation}")
        if date_issues:
            print(f"Found {len(date_issues)} date inconsistencies:")
            for issue in date_issues:
                print(f"  {issue}")

    # Step 5: Index Management
    if verbose:
        print("📚 Managing documentation index...")

    # Find all markdown files for indexing (using config ignore patterns)
    all_md_files = find_all_markdown_files(repo_path, config.ignore_patterns)
    missing_from_index = indexer.find_missing_entries(all_md_files)

    # Update index if there are missing entries
    new_entries_count = 0
    if missing_from_index:
        if verbose:
            print(f"Found {len(missing_from_index)} files missing from index:")
            for missing_file in missing_from_index:
                relative_path = missing_file.relative_to(repo_path)
                print(f"  {relative_path}")

        new_entries_count = indexer.update_index(missing_from_index)
        if verbose and new_entries_count > 0:
            print(f"Added {new_entries_count} entries to DOCUMENTATION_INDEX.md")

    # Create summary entries for reporting
    index_entries = []
    for missing_file in missing_from_index:
        relative_path = missing_file.relative_to(repo_path)
        index_entries.append(f"✅ Added {relative_path} to index")

    results.new_index_entries = index_entries
    
    # Generate report and return exit code
    return reporter.print_summary(results)


if __name__ == "__main__":
    sys.exit(main())
