"""
Unit tests for validators module.

Tests for README presence validation, metadata format enforcement,
link integrity checking, and date consistency validation.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validators.readme_validator import ReadmeValidator
from validators.metadata_validator import MetadataValidator
from validators.link_validator import LinkValidator


class TestValidators(unittest.TestCase):
    """Test cases for validation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.test_dir)

        # Create test directory structure
        (self.test_dir / "apps").mkdir()
        (self.test_dir / "libs").mkdir()
        (self.test_dir / "core").mkdir()  # Should be ignored

        # Create some README files
        (self.test_dir / "README.md").write_text("""# Test Repo
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-12

[Link to apps](apps/README.md)
""")

        (self.test_dir / "apps" / "README.md").write_text("""# Apps
**Status**: 🚧 Draft
**Version**: 0.5.0
**Last Updated**: 2025-06-10
""")

        # libs directory has no README (for testing)
        # core directory will be ignored

    def test_readme_presence_validation(self):
        """Test README presence validation."""
        validator = ReadmeValidator(self.test_dir)
        violations = validator.validate()

        # Should find missing README in libs directory
        self.assertEqual(len(violations), 1)
        self.assertIn("libs", violations[0])
        self.assertIn("Missing README", violations[0])

    def test_metadata_format_enforcement(self):
        """Test metadata format validation."""
        # Create README with bad metadata
        bad_readme = self.test_dir / "bad_metadata.md"
        bad_readme.write_text("""# Bad Metadata
**Status**: Invalid Status
**Version**: not-a-version
""")

        validator = MetadataValidator(self.test_dir)
        violations = validator.validate_metadata(bad_readme)

        # Should find multiple violations
        self.assertGreater(len(violations), 0)
        self.assertTrue(any("missing" in v and "Last Updated" in v for v in violations))
        self.assertTrue(any("invalid status" in v for v in violations))
        self.assertTrue(any("invalid version format" in v for v in violations))

    def test_link_integrity_checking(self):
        """Test link integrity validation."""
        # Create README with broken link
        broken_link_readme = self.test_dir / "broken_links.md"
        broken_link_readme.write_text("""# Broken Links
[Valid link](README.md)
[Broken link](nonexistent.md)
""")

        validator = LinkValidator(self.test_dir)
        violations = validator.validate_links_in_file(broken_link_readme)

        # Should find the broken link
        self.assertEqual(len(violations), 1)
        self.assertIn("nonexistent.md", violations[0])

    def test_date_consistency_validation(self):
        """Test date consistency validation."""
        # Create parent with older date than child
        (self.test_dir / "parent").mkdir()
        (self.test_dir / "parent" / "child").mkdir()

        (self.test_dir / "parent" / "README.md").write_text("""# Parent
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-01
""")

        (self.test_dir / "parent" / "child" / "README.md").write_text("""# Child
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-10
""")

        validator = LinkValidator(self.test_dir)
        _, date_issues = validator.validate()

        # Should find date inconsistency
        self.assertEqual(len(date_issues), 1)
        self.assertIn("older than child", date_issues[0])

    def test_metadata_parser_edge_cases(self):
        """Test metadata parser with edge cases."""
        # Test metadata in wrong section (should be ignored)
        edge_case_readme = self.test_dir / "edge_case.md"
        edge_case_readme.write_text("""# Title
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-12

## Documentation
- **Status**: This should be ignored
- **Version**: This too
""")

        validator = MetadataValidator(self.test_dir)
        violations = validator.validate_metadata(edge_case_readme)

        # Should have no violations (metadata is correctly parsed from top section)
        self.assertEqual(len(violations), 0)


if __name__ == '__main__':
    unittest.main()
