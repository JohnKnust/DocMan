"""
Unit tests for indexer module.

Tests for documentation index management functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from indexer import DocumentationIndexer


class TestDocumentationIndexer(unittest.TestCase):
    """Test cases for documentation indexer."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.test_dir)

        # Create test directory structure
        (self.test_dir / "apps").mkdir()
        (self.test_dir / "libs").mkdir()

        # Create some markdown files
        (self.test_dir / "README.md").write_text("""# Test Repo
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-12
""")

        (self.test_dir / "apps" / "README.md").write_text("""# Apps
**Status**: 🚧 Draft
**Version**: 0.5.0
**Last Updated**: 2025-06-10
""")

        (self.test_dir / "libs" / "README.md").write_text("""# Libs
**Status**: ✅ Production Ready
**Version**: 2.0.0
**Last Updated**: 2025-06-11
""")

        self.indexer = DocumentationIndexer(self.test_dir)

    def test_load_existing_index(self):
        """Test loading existing index entries."""
        # Create a sample index
        index_content = """# Documentation Index

## Project Root
- [README.md](README.md) – ✅ Production Ready – 2025-06-12

## Applications
- [apps/README.md](apps/README.md) – 🚧 Draft – 2025-06-10
"""
        self.indexer.index_file.write_text(index_content)

        indexed_files = self.indexer.load_existing_index()

        self.assertEqual(len(indexed_files), 2)
        self.assertIn("README.md", indexed_files)
        self.assertIn("apps/README.md", indexed_files)

    def test_find_missing_entries(self):
        """Test finding missing index entries."""
        # Create index with only one file
        index_content = """# Documentation Index

## Project Root
- [README.md](README.md) – ✅ Production Ready – 2025-06-12
"""
        self.indexer.index_file.write_text(index_content)

        # Find all markdown files
        from utils import find_all_markdown_files
        all_md_files = find_all_markdown_files(self.test_dir)

        missing = self.indexer.find_missing_entries(all_md_files)

        # Should find missing files (apps/README.md, libs/README.md, and possibly DOCUMENTATION_INDEX.md)
        self.assertGreaterEqual(len(missing), 2)
        missing_paths = [str(f.relative_to(self.test_dir)) for f in missing]
        self.assertIn("apps/README.md", missing_paths)
        self.assertIn("libs/README.md", missing_paths)

    def test_update_index(self):
        """Test updating the documentation index."""
        # Start with no index
        self.assertFalse(self.indexer.index_file.exists())

        # Find all markdown files
        from utils import find_all_markdown_files
        all_md_files = find_all_markdown_files(self.test_dir)

        # Update index
        updated_count = self.indexer.update_index(all_md_files)

        # Should have updated with all files
        self.assertEqual(updated_count, len(all_md_files))
        self.assertTrue(self.indexer.index_file.exists())

        # Check index content
        content = self.indexer.index_file.read_text()
        self.assertIn("# Documentation Index", content)
        self.assertIn("README.md", content)
        self.assertIn("apps/README.md", content)
        self.assertIn("libs/README.md", content)

    def test_categorize_file(self):
        """Test file categorization logic."""
        # Test different file paths
        apps_file = self.test_dir / "apps" / "README.md"
        libs_file = self.test_dir / "libs" / "README.md"
        root_file = self.test_dir / "README.md"
        tools_file = self.test_dir / "tools" / "README.md"

        self.assertEqual(self.indexer.categorize_file(apps_file), "Applications")
        self.assertEqual(self.indexer.categorize_file(libs_file), "Libraries")
        self.assertEqual(self.indexer.categorize_file(root_file), "Project Root")
        self.assertEqual(self.indexer.categorize_file(tools_file), "Tools")

    def test_parse_metadata_from_file(self):
        """Test metadata parsing from files."""
        metadata = self.indexer.parse_metadata_from_file(self.test_dir / "README.md")

        self.assertEqual(metadata["Status"], "✅ Production Ready")
        self.assertEqual(metadata["Version"], "1.0.0")
        self.assertEqual(metadata["Last Updated"], "2025-06-12")


if __name__ == '__main__':
    unittest.main()
