#!/usr/bin/env python3
"""
DocMan CLI - Documentation Management Tool

A generic, example-driven Documentation Management CLI tool that can be dropped
into any monorepo to validate and maintain documentation standards.

Usage:
    python cli.py [OPTIONS] [REPO_PATH]

Options:
    --verbose, -v    Enable verbose output
    --fix           Automatically fix issues where possible
    --report        Generate detailed report
    --help, -h      Show this help message

Examples:
    python cli.py                    # Check current directory
    python cli.py /path/to/repo      # Check specific repository
    python cli.py --verbose --fix    # Check with verbose output and auto-fix
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils import find_all_directories, find_all_markdown_files
from src.indexer import DocumentationIndexer
from src.reporter import Reporter, ValidationResult
from src.validators.readme_validator import ReadmeValidator
from src.validators.metadata_validator import MetadataValidator
from src.validators.link_validator import LinkValidator


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
        help="Automatically fix issues where possible"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point for DocMan CLI."""
    args = parse_arguments()
    
    # Initialize components
    repo_path = Path(args.repo_path).resolve()
    reporter = Reporter(verbose=args.verbose)
    indexer = DocumentationIndexer(repo_path)
    
    if args.verbose:
        print(f"🔍 Analyzing repository: {repo_path}")
    
    # Initialize validation results
    results = ValidationResult(
        missing_readmes=[],
        metadata_violations=[],
        broken_links=[],
        date_bumps=[],
        new_index_entries=[]
    )
    
    # Step 2: README Presence Validation
    if args.verbose:
        print("📋 Checking README presence...")

    readme_validator = ReadmeValidator(repo_path)
    readme_violations = readme_validator.validate()
    results.missing_readmes = readme_violations

    if args.verbose and readme_violations:
        print(f"Found {len(readme_violations)} missing READMEs:")
        for violation in readme_violations:
            print(f"  {violation}")

    # Step 3: Metadata Format Enforcement
    if args.verbose:
        print("📋 Checking metadata format...")

    metadata_validator = MetadataValidator(repo_path)
    metadata_violations = metadata_validator.validate()
    results.metadata_violations = metadata_violations

    if args.verbose and metadata_violations:
        print(f"Found {len(metadata_violations)} metadata violations:")
        for violation in metadata_violations:
            print(f"  {violation}")

    # Step 4: Link & Date Integrity
    if args.verbose:
        print("🔗 Checking link integrity and date consistency...")

    link_validator = LinkValidator(repo_path)
    link_violations, date_issues = link_validator.validate()
    results.broken_links = link_violations
    results.date_bumps = date_issues  # Note: these are reports, not actual bumps

    if args.verbose and (link_violations or date_issues):
        if link_violations:
            print(f"Found {len(link_violations)} broken links:")
            for violation in link_violations:
                print(f"  {violation}")
        if date_issues:
            print(f"Found {len(date_issues)} date inconsistencies:")
            for issue in date_issues:
                print(f"  {issue}")

    # TODO: Implement remaining validation steps
    # Step 5: Index Management
    
    # Generate report and return exit code
    return reporter.print_summary(results)


if __name__ == "__main__":
    sys.exit(main())
