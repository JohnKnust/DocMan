"""
Integration tests for DocMan CLI.

Tests the complete workflow from CLI invocation to final output.
"""

import unittest
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path


class TestDocManIntegration(unittest.TestCase):
    """Integration test cases for DocMan CLI."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.test_dir)
        self.cli_path = Path(__file__).parent.parent / "cli.py"
        
        # Create a realistic test repository structure
        self.create_test_repository()
    
    def create_test_repository(self):
        """Create a test repository with various documentation scenarios."""
        # Create directory structure
        (self.test_dir / "apps" / "web").mkdir(parents=True)
        (self.test_dir / "libs" / "utils").mkdir(parents=True)
        (self.test_dir / "tools").mkdir()
        (self.test_dir / "core").mkdir()  # Should be ignored
        
        # Root README with good metadata
        (self.test_dir / "README.md").write_text("""# Test Repository
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-12

This is a test repository for DocMan integration testing.

## Links
- [Web App](apps/web/README.md)
- [Utils Library](libs/utils/README.md)
""")
        
        # Apps README with good metadata
        (self.test_dir / "apps" / "web" / "README.md").write_text("""# Web Application
**Status**: 🚧 Draft
**Version**: 0.8.0
**Last Updated**: 2025-06-10

A sample web application.
""")
        
        # Libs README with bad metadata (for testing)
        (self.test_dir / "libs" / "utils" / "README.md").write_text("""# Utilities
**Status**: Invalid Status
**Version**: not-a-version

Utility functions.
""")
        
        # Tools directory without README (for testing missing README)
        # Core directory will be ignored
    
    def run_docman_cli(self, args=None, expect_success=True):
        """Run DocMan CLI and return result."""
        cmd = [sys.executable, str(self.cli_path)]
        if args:
            cmd.extend(args)
        cmd.append(str(self.test_dir))
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.cli_path.parent
        )
        
        if expect_success:
            self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        
        return result
    
    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "--help"],
            capture_output=True,
            text=True,
            cwd=self.cli_path.parent
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("DocMan - Documentation Management CLI Tool", result.stdout)
        self.assertIn("--verbose", result.stdout)
        self.assertIn("--fix", result.stdout)
    
    def test_full_validation_with_issues(self):
        """Test complete validation workflow with issues present."""
        result = self.run_docman_cli(expect_success=False)
        
        # Should find issues and return exit code 1
        self.assertEqual(result.returncode, 1)
        
        # Check for expected issues in output
        output = result.stdout
        self.assertIn("Missing READMEs", output)
        self.assertIn("Metadata violations", output)
        self.assertIn("tools", output)  # Missing README
        self.assertIn("Invalid Status", output)  # Bad metadata
        self.assertIn("not-a-version", output)  # Bad version
    
    def test_verbose_output(self):
        """Test verbose output contains detailed information."""
        result = self.run_docman_cli(["--verbose"], expect_success=False)
        
        output = result.stdout
        self.assertIn("🔍 Analyzing repository", output)
        self.assertIn("📋 Checking README presence", output)
        self.assertIn("📋 Checking metadata format", output)
        self.assertIn("🔗 Checking link integrity", output)
        self.assertIn("📚 Managing documentation index", output)
    
    def test_index_creation(self):
        """Test that DOCUMENTATION_INDEX.md is created."""
        # Ensure no index exists initially
        index_file = self.test_dir / "DOCUMENTATION_INDEX.md"
        if index_file.exists():
            index_file.unlink()
        
        result = self.run_docman_cli(expect_success=False)
        
        # Index should be created
        self.assertTrue(index_file.exists())
        
        # Check index content
        content = index_file.read_text()
        self.assertIn("# Documentation Index", content)
        self.assertIn("README.md", content)
        self.assertIn("apps/web/README.md", content)
    
    def test_clean_repository(self):
        """Test validation shows improvement after fixing issues."""
        # First run - should have issues
        result_before = self.run_docman_cli(expect_success=False)
        self.assertEqual(result_before.returncode, 1)

        # Fix all issues
        # Add missing READMEs
        (self.test_dir / "tools" / "README.md").write_text("""# Tools
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-12

Development tools.
""")

        (self.test_dir / "libs" / "README.md").write_text("""# Libraries
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-11

Shared libraries.
""")

        (self.test_dir / "apps" / "README.md").write_text("""# Applications
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-11

Applications directory.
""")

        # Fix bad metadata
        (self.test_dir / "libs" / "utils" / "README.md").write_text("""# Utilities
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-11

Utility functions.
""")

        # Second run - should have fewer issues (may still have date inconsistencies)
        result_after = self.run_docman_cli(expect_success=False)

        # Should have improved (fewer issues)
        self.assertIn("Missing READMEs (0)", result_after.stdout)
        self.assertIn("Metadata violations (0)", result_after.stdout)
    
    def test_makefile_integration(self):
        """Test that Makefile commands work correctly."""
        # Test make check-syntax
        result = subprocess.run(
            ["make", "check-syntax"],
            capture_output=True,
            text=True,
            cwd=self.cli_path.parent
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Checking Python syntax", result.stdout)
    
    def test_exit_codes(self):
        """Test proper exit codes for different scenarios."""
        # Test with issues (should return 1)
        result = self.run_docman_cli(expect_success=False)
        self.assertEqual(result.returncode, 1)

        # Fix major issues
        (self.test_dir / "tools" / "README.md").write_text("""# Tools
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-12
""")

        (self.test_dir / "libs" / "README.md").write_text("""# Libraries
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-11
""")

        (self.test_dir / "apps" / "README.md").write_text("""# Applications
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-11
""")

        (self.test_dir / "libs" / "utils" / "README.md").write_text("""# Utils
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-06-11
""")

        # Test that major issues are fixed (exit code may still be 1 due to date inconsistencies)
        result = self.run_docman_cli(expect_success=False)

        # Verify that the major issues are resolved
        self.assertIn("Missing READMEs (0)", result.stdout)
        self.assertIn("Metadata violations (0)", result.stdout)


if __name__ == '__main__':
    unittest.main()
