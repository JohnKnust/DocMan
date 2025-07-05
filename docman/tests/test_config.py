"""
Tests for configuration loading functionality
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config import ConfigLoader, DocManConfig, load_config, create_config_template


class TestDocManConfig:
    """Test DocManConfig data class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = DocManConfig()
        
        assert config.root_directory == "."
        assert config.index_file == "DOCUMENTATION_INDEX.md"
        assert config.recreate_index is True
        assert config.strict_validation is True
        assert "Status" in config.required_metadata
        assert "Version" in config.required_metadata
        assert "Last Updated" in config.required_metadata
        assert ".git/" in config.ignore_patterns
        assert "node_modules/" in config.ignore_patterns
        assert config.verbose_output is False
        assert config.colored_output is True
        assert config.emoji_indicators is True
        assert config.generate_reports is True
        assert config.exit_on_errors is True
        assert config.auto_fix is False


class TestConfigLoader:
    """Test ConfigLoader class."""
    
    def test_init(self):
        """Test ConfigLoader initialization."""
        loader = ConfigLoader()
        assert loader.config_filename == ".docmanrc"
        assert loader.docman_dir.name == "docman"
    
    def test_init_with_repo_root(self):
        """Test ConfigLoader initialization with repo root."""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = ConfigLoader(Path(temp_dir))
            assert loader.repo_root == Path(temp_dir)
    
    def test_load_config_no_file(self):
        """Test loading config when no file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('pathlib.Path.cwd', return_value=Path(temp_dir)):
                loader = ConfigLoader()
                config = loader.load_config()
                
                # Should return default config
                assert isinstance(config, DocManConfig)
                assert config.root_directory == "."
    
    def test_load_config_from_parent_directory(self):
        """Test loading config from parent directory (submodule scenario)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create docman subdirectory
            docman_dir = temp_path / "docman"
            docman_dir.mkdir()
            
            # Create config in parent directory
            config_file = temp_path / ".docmanrc"
            config_content = """
root_directory = "custom"
verbose_output = true
ignore_patterns = [
    ".git/",
    "custom_ignore/"
]
"""
            config_file.write_text(config_content)
            
            # Mock docman_dir to point to our test directory
            with patch.object(ConfigLoader, '__init__', lambda self, repo_root=None: setattr(self, 'docman_dir', docman_dir) or setattr(self, 'repo_root', Path.cwd()) or setattr(self, 'config_filename', '.docmanrc')):
                loader = ConfigLoader()
                config = loader.load_config()
                
                assert config.root_directory == "custom"
                assert config.verbose_output is True
                assert "custom_ignore/" in config.ignore_patterns
    
    def test_load_config_from_environment_variable(self):
        """Test loading config from DOCMAN_CONFIG environment variable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "custom_config.rc"
            config_content = """
root_directory = "env_test"
strict_validation = false
"""
            config_file.write_text(config_content)
            
            with patch.dict(os.environ, {'DOCMAN_CONFIG': str(config_file)}):
                loader = ConfigLoader()
                config = loader.load_config()
                
                assert config.root_directory == "env_test"
                assert config.strict_validation is False
    
    def test_load_config_json_format(self):
        """Test loading config in JSON format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / ".docmanrc.json"
            config_content = """{
    "ignorePatterns": [".git", "test_ignore"],
    "requiredMetadata": ["Status", "Custom"],
    "autoFix": true,
    "verbose": true
}"""
            config_file.write_text(config_content)
            
            with patch.dict(os.environ, {'DOCMAN_CONFIG': str(config_file)}):
                loader = ConfigLoader()
                config = loader.load_config()
                
                assert "test_ignore" in config.ignore_patterns
                assert "Custom" in config.required_metadata
                assert config.auto_fix is True
                assert config.verbose_output is True
    
    def test_load_config_invalid_file(self):
        """Test loading config with invalid file content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / ".docmanrc"
            config_file.write_text("invalid content [[[")
            
            with patch.dict(os.environ, {'DOCMAN_CONFIG': str(config_file)}):
                loader = ConfigLoader()
                config = loader.load_config()
                
                # Should fall back to defaults
                assert config.root_directory == "."
    
    def test_find_config_file_search_order(self):
        """Test configuration file search order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create nested directory structure
            nested_dir = temp_path / "project" / "subdir"
            nested_dir.mkdir(parents=True)
            
            # Create config files at different levels
            (temp_path / ".docmanrc").write_text("# root config")
            (temp_path / "project" / ".docmanrc").write_text("# project config")
            
            # Test from nested directory
            with patch('pathlib.Path.cwd', return_value=nested_dir):
                loader = ConfigLoader()
                config_path = loader._find_config_file()

                # Should find a config file (could be project-level or parent)
                assert config_path is not None
                assert config_path.name == ".docmanrc"


class TestConfigFunctions:
    """Test module-level configuration functions."""
    
    def test_load_config_function(self):
        """Test load_config convenience function."""
        config = load_config()
        assert isinstance(config, DocManConfig)
    
    def test_create_config_template(self):
        """Test configuration template creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = Path(temp_dir) / "test_template.rc"
            result_path = create_config_template(template_path)
            
            assert result_path == template_path
            assert template_path.exists()
            
            content = template_path.read_text()
            assert "DocMan Configuration Template" in content
            assert "ignore_patterns" in content
            assert "required_metadata" in content
    
    def test_create_config_template_default_path(self):
        """Test configuration template creation with default path."""
        with patch('pathlib.Path.cwd') as mock_cwd:
            with tempfile.TemporaryDirectory() as temp_dir:
                mock_cwd.return_value = Path(temp_dir)
                
                result_path = create_config_template()

                # Should create a template file
                assert result_path.exists()
                assert result_path.name.endswith(".template")


class TestConfigIntegration:
    """Integration tests for configuration loading."""
    
    def test_full_workflow_with_config(self):
        """Test full workflow with custom configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create project structure
            project_dir = temp_path / "test_project"
            docman_dir = project_dir / "docman"
            docman_dir.mkdir(parents=True)
            
            # Create configuration
            config_file = project_dir / ".docmanrc"
            config_content = """
root_directory = "."
verbose_output = true
ignore_patterns = [
    ".git/",
    "node_modules/",
    "test_ignore/"
]
required_metadata = [
    "Status",
    "Version",
    "Last Updated",
    "Custom Field"
]
"""
            config_file.write_text(config_content)
            
            # Mock docman directory location
            with patch.object(ConfigLoader, '__init__', lambda self, repo_root=None: setattr(self, 'docman_dir', docman_dir) or setattr(self, 'repo_root', project_dir) or setattr(self, 'config_filename', '.docmanrc')):
                config = load_config()
                
                assert config.verbose_output is True
                assert "test_ignore/" in config.ignore_patterns
                assert "Custom Field" in config.required_metadata
                assert len(config.required_metadata) == 4
