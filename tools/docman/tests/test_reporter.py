"""
Unit tests for reporter module.

Tests for report generation and output formatting.
"""

import unittest
from io import StringIO
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from reporter import Reporter, ValidationResult


class TestReporter(unittest.TestCase):
    """Test cases for reporter functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.reporter = Reporter(verbose=False)

        # Capture stdout for testing
        self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        """Clean up after tests."""
        sys.stdout = self.held

    def test_print_summary_no_issues(self):
        """Test summary printing with no issues."""
        results = ValidationResult(
            missing_readmes=[],
            metadata_violations=[],
            broken_links=[],
            date_bumps=[],
            new_index_entries=[]
        )

        exit_code = self.reporter.print_summary(results)
        output = sys.stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("All documentation checks passed!", output)
        self.assertIn("📊 DOCUMENTATION VALIDATION SUMMARY", output)

    def test_print_summary_with_issues(self):
        """Test summary printing with issues."""
        results = ValidationResult(
            missing_readmes=["🚧 Missing README: apps"],
            metadata_violations=["🚧 Bad metadata in README.md: missing Version"],
            broken_links=["🚧 Broken link in README.md: nonexistent.md"],
            date_bumps=[],
            new_index_entries=[]
        )

        exit_code = self.reporter.print_summary(results)
        output = sys.stdout.getvalue()

        self.assertEqual(exit_code, 1)
        self.assertIn("Found 3 documentation issues", output)
        self.assertIn("Missing READMEs (1)", output)
        self.assertIn("Metadata violations (1)", output)
        self.assertIn("Broken links (1)", output)

    def test_print_section_with_items(self):
        """Test section printing with items."""
        items = ["Missing README: apps", "Missing README: libs"]

        self.reporter.print_section("Missing READMEs", items, "🚧")
        output = sys.stdout.getvalue()

        self.assertIn("🚧 Missing READMEs (2)", output)
        self.assertIn("Missing README: apps", output)
        self.assertIn("Missing README: libs", output)

    def test_print_section_no_items(self):
        """Test section printing with no items."""
        items = []

        self.reporter.print_section("Missing READMEs", items, "🚧")
        output = sys.stdout.getvalue()

        self.assertIn("🚧 Missing READMEs (0)", output)
        self.assertIn("✅ No issues found", output)

    def test_verbose_reporter(self):
        """Test verbose reporter initialization."""
        verbose_reporter = Reporter(verbose=True)
        self.assertTrue(verbose_reporter.verbose)

        normal_reporter = Reporter(verbose=False)
        self.assertFalse(normal_reporter.verbose)

    def test_validation_result_dataclass(self):
        """Test ValidationResult dataclass."""
        results = ValidationResult(
            missing_readmes=["test1"],
            metadata_violations=["test2"],
            broken_links=["test3"],
            date_bumps=["test4"],
            new_index_entries=["test5"]
        )

        self.assertEqual(len(results.missing_readmes), 1)
        self.assertEqual(len(results.metadata_violations), 1)
        self.assertEqual(len(results.broken_links), 1)
        self.assertEqual(len(results.date_bumps), 1)
        self.assertEqual(len(results.new_index_entries), 1)


if __name__ == '__main__':
    unittest.main()
