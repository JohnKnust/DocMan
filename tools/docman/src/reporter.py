"""
Report Generator for DocMan

Handles all output formatting and reporting functionality.
Provides terminal output with emojis and proper exit codes.
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Container for validation results."""
    missing_readmes: List[str]
    metadata_violations: List[str]
    broken_links: List[str]
    date_bumps: List[str]
    new_index_entries: List[str]


class Reporter:
    """Handles all reporting and output formatting."""
    
    def __init__(self, verbose: bool = False):
        """Initialize reporter with verbosity setting."""
        self.verbose = verbose
    
    def print_summary(self, results: ValidationResult) -> int:
        """Print terminal summary and return appropriate exit code."""
        print("\n" + "="*60)
        print("📊 DOCUMENTATION VALIDATION SUMMARY")
        print("="*60)

        # Print each section
        self.print_section("Missing READMEs", results.missing_readmes, "🚧")
        self.print_section("Metadata violations", results.metadata_violations, "🚧")
        self.print_section("Broken links", results.broken_links, "🚧")
        self.print_section("Date inconsistencies", results.date_bumps, "🚧")
        self.print_section("New index entries", results.new_index_entries, "✅")

        # Calculate total issues (date inconsistencies are warnings, not errors)
        total_issues = (len(results.missing_readmes) +
                       len(results.metadata_violations) +
                       len(results.broken_links))

        print("-"*60)
        if total_issues == 0:
            print("✅ All documentation checks passed!")
            return 0
        else:
            print(f"🚧 Found {total_issues} documentation issues")
            return 1

    def print_section(self, title: str, items: List[str], emoji: str) -> None:
        """Print a section of the report with emoji and items."""
        count = len(items)
        print(f"\n{emoji} {title} ({count})")

        if count > 0:
            for item in items:
                # Remove emoji from item if it's already there
                clean_item = item.replace("🚧 ", "").replace("✅ ", "")
                print(f"  • {clean_item}")
        else:
            print("  ✅ No issues found")
