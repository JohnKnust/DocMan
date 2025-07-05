"""
Configuration management for DocMan

Handles loading and parsing of .docmanrc configuration files with flexible search paths.
Supports parent directory search, environment variable overrides, and fallback defaults.
Designed for use as a reusable submodule.
"""

from typing import Dict, List, Set, Any, Optional
from pathlib import Path
import os
import json
import configparser
from dataclasses import dataclass, field


@dataclass
class DocManConfig:
    """DocMan configuration data class."""
    
    # Core settings
    root_directory: str = "."
    index_file: str = "DOCUMENTATION_INDEX.md"
    recreate_index: bool = True
    
    # Validation settings
    strict_validation: bool = True
    required_metadata: List[str] = field(default_factory=lambda: ["Status", "Version", "Last Updated"])
    valid_statuses: List[str] = field(default_factory=lambda: [
        "✅ Production Ready",
        "🚧 Draft",
        "🚫 Deprecated",
        "⚠️ Experimental",
        "🔄 In Progress"
    ])
    
    # Ignore patterns
    ignore_patterns: Set[str] = field(default_factory=lambda: {
        ".git/",
        "node_modules/",
        "venv/",
        "__pycache__/",
        "vscode-extension/",
        "*.tmp",
        "*.log",
        "core"
    })
    
    # Output settings
    verbose_output: bool = False
    colored_output: bool = True
    emoji_indicators: bool = True
    
    # Reporting settings
    generate_reports: bool = True
    exit_on_errors: bool = True
    auto_fix: bool = False

    # Private attributes (set by ConfigLoader)
    _config_path: str = field(default="defaults", init=False)
    _is_fallback: bool = field(default=False, init=False)

    @property
    def config_path(self) -> str:
        """Get the path to the configuration file that was loaded."""
        return self._config_path

    @property
    def is_fallback(self) -> bool:
        """Check if the configuration is using fallback/template values."""
        return self._is_fallback


class ConfigLoader:
    """
    Loads DocMan configuration from various sources with flexible search strategy.
    
    Search order:
    1. Environment variable DOCMAN_CONFIG (if set)
    2. Parent directory of the DocMan submodule
    3. Current working directory
    4. Parent directories up to git root
    5. Default configuration (fallback)
    """
    
    def __init__(self, repo_root: Path = None):
        """Initialize config loader with repository root."""
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.config_filename = ".docmanrc"
        self.docman_dir = Path(__file__).parent.parent  # docman/ directory
    
    def load_config(self) -> DocManConfig:
        """Load configuration from file or return defaults."""
        config = DocManConfig()

        # Try to find and load configuration file
        config_path = self._find_config_file()
        is_fallback = False

        if config_path and config_path.exists():
            # Check if we're using the template as fallback
            is_fallback = config_path.name.endswith('.template')

            try:
                self._load_from_file(config, config_path)
                # Store fallback status in config for later use
                config._is_fallback = is_fallback
                config._config_path = str(config_path)

                # Always show fallback warning, even in non-verbose mode
                if is_fallback:
                    print(f"🔄 Using FALLBACK configuration from template: {config_path}")
                    print("💡 Create a .docmanrc file in your project root for custom settings")
                elif config.verbose_output:
                    print(f"✅ Loaded configuration from: {config_path}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to load config from {config_path}: {e}")
                print("Using default configuration.")
                config._is_fallback = False
                config._config_path = "defaults"
        else:
            config._is_fallback = False
            config._config_path = "defaults"
            if config.verbose_output:
                print("ℹ️  No configuration file found, using defaults.")

        return config
    
    def _find_config_file(self) -> Optional[Path]:
        """
        Find configuration file using flexible search strategy.

        Returns the first configuration file found in this order:
        1. DOCMAN_CONFIG environment variable path
        2. Parent of parent directory of DocMan submodule (for submodule usage)
        3. Parent directory of DocMan submodule
        4. Current working directory
        5. Parent directories up to git root
        """

        # 1. Check environment variable override
        env_config = os.environ.get('DOCMAN_CONFIG')
        if env_config:
            env_path = Path(env_config)
            if env_path.exists():
                return env_path
            else:
                print(f"⚠️  Warning: DOCMAN_CONFIG points to non-existent file: {env_path}")

        # 2. Check parent of parent directory (for submodule usage)
        # /path/to/project/.docmanrc (when DocMan is at /path/to/project/DocMan/docman/)
        grandparent_config = self.docman_dir.parent.parent / self.config_filename
        if grandparent_config.exists():
            return grandparent_config

        # 3. Check parent directory of DocMan submodule
        parent_config = self.docman_dir.parent / self.config_filename
        if parent_config.exists():
            return parent_config

        # 4. Check current working directory
        cwd_config = Path.cwd() / self.config_filename
        if cwd_config.exists():
            return cwd_config

        # 5. Search parent directories up to git root
        current = Path.cwd()
        for parent in current.parents:
            config_path = parent / self.config_filename
            if config_path.exists():
                return config_path

            # Stop at git root or filesystem root
            if (parent / ".git").exists() or parent == parent.parent:
                break

        # No configuration file found
        return None
    
    def _load_from_file(self, config: DocManConfig, config_path: Path):
        """Load configuration from file."""
        content = config_path.read_text(encoding='utf-8')

        # Try to parse as different formats
        if config_path.suffix.lower() == '.json':
            self._load_from_json(config, content)
        else:
            # Use custom parser for .docmanrc format
            self._load_from_custom_format(config, content)
    
    def _load_from_json(self, config: DocManConfig, content: str):
        """Load configuration from JSON format."""
        data = json.loads(content)
        
        # Map JSON keys to config attributes
        if "ignorePatterns" in data:
            config.ignore_patterns = set(data["ignorePatterns"])
        if "requiredMetadata" in data:
            config.required_metadata = data["requiredMetadata"]
        if "validStatuses" in data:
            config.valid_statuses = data["validStatuses"]
        if "autoFix" in data:
            config.auto_fix = data["autoFix"]
        if "verbose" in data:
            config.verbose_output = data["verbose"]
    
    def _load_from_ini(self, config: DocManConfig, content: str):
        """Load configuration from INI-style format."""
        parser = configparser.ConfigParser()

        # Handle files without section headers by adding a DEFAULT section
        if not content.strip().startswith('['):
            content = '[DEFAULT]\n' + content

        parser.read_string(content)

        # Parse sections
        if parser.has_section('DEFAULT') or len(parser.sections()) == 0:
            # Handle flat format (current .docmanrc style)
            section = parser['DEFAULT'] if parser.has_section('DEFAULT') else parser
            
            if 'ignore_patterns' in section:
                # Parse list format: ["item1", "item2"] or item1,item2
                patterns_str = section['ignore_patterns']
                try:
                    if patterns_str.startswith('[') and patterns_str.endswith(']'):
                        # JSON-style list
                        import ast
                        patterns = ast.literal_eval(patterns_str)
                        config.ignore_patterns = set(patterns)
                    else:
                        # Comma-separated
                        patterns = [p.strip().strip('"\'') for p in patterns_str.split(',')]
                        config.ignore_patterns = set(patterns)
                except (ValueError, SyntaxError):
                    # If parsing fails, try to parse as multi-line format
                    config.ignore_patterns = self._parse_multiline_list(content, 'ignore_patterns')

            if 'required_metadata' in section:
                metadata_str = section['required_metadata']
                try:
                    if metadata_str.startswith('[') and metadata_str.endswith(']'):
                        import ast
                        config.required_metadata = ast.literal_eval(metadata_str)
                except (ValueError, SyntaxError):
                    # If parsing fails, try to parse as multi-line format
                    config.required_metadata = self._parse_multiline_list(content, 'required_metadata')
            
            # Boolean settings
            for key, attr in [
                ('strict_validation', 'strict_validation'),
                ('verbose_output', 'verbose_output'),
                ('colored_output', 'colored_output'),
                ('emoji_indicators', 'emoji_indicators'),
                ('generate_reports', 'generate_reports'),
                ('exit_on_errors', 'exit_on_errors'),
                ('recreate_index', 'recreate_index')
            ]:
                if key in section:
                    setattr(config, attr, section.getboolean(key))
            
            # String settings
            for key, attr in [
                ('root_directory', 'root_directory'),
                ('index_file', 'index_file')
            ]:
                if key in section:
                    setattr(config, attr, section[key])

    def _parse_multiline_list(self, content: str, key: str) -> list:
        """Parse multiline list format from configuration content."""
        lines = content.split('\n')
        in_list = False
        items = []

        for line in lines:
            line = line.strip()

            if line.startswith(f'{key} = ['):
                in_list = True
                # Check if list ends on same line
                if line.endswith(']'):
                    # Single line list
                    list_content = line[len(f'{key} = ['):-1]
                    items = [item.strip().strip('"\'') for item in list_content.split(',') if item.strip()]
                    break
                continue

            if in_list:
                if line.endswith(']'):
                    # End of list
                    if line != ']':
                        # Last item on same line as closing bracket
                        item = line[:-1].strip().strip(',').strip('"\'')
                        if item:
                            items.append(item)
                    break
                elif line and not line.startswith('#'):
                    # List item
                    item = line.strip().strip(',').strip('"\'')
                    if item:
                        items.append(item)

        return items

    def _load_from_custom_format(self, config: DocManConfig, content: str):
        """Load configuration from custom .docmanrc format."""
        lines = content.split('\n')
        current_key = None
        current_list = []
        in_list = False

        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Handle key-value pairs
            if '=' in line and not in_list:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Handle different value types
                if value.lower() in ('true', 'false'):
                    # Boolean values
                    bool_value = value.lower() == 'true'
                    self._set_config_value(config, key, bool_value)
                elif value.startswith('[') and value.endswith(']'):
                    # Single-line list
                    list_content = value[1:-1]
                    if list_content.strip():
                        items = [item.strip().strip('"\'') for item in list_content.split(',')]
                        self._set_config_value(config, key, items)
                    else:
                        self._set_config_value(config, key, [])
                elif value.startswith('['):
                    # Multi-line list start
                    in_list = True
                    current_key = key
                    current_list = []
                    # Check if there's content on the same line
                    list_start = value[1:].strip()
                    if list_start and not list_start.endswith(','):
                        current_list.append(list_start.strip('"\''))
                elif value.startswith('"') and value.endswith('"'):
                    # String value
                    self._set_config_value(config, key, value[1:-1])
                else:
                    # Plain value
                    self._set_config_value(config, key, value.strip('"\''))

            elif in_list:
                # Handle list items
                if line.endswith(']'):
                    # End of list
                    if line != ']':
                        # Last item on same line as closing bracket
                        item = line[:-1].strip().strip(',').strip('"\'')
                        if item:
                            current_list.append(item)
                    self._set_config_value(config, current_key, current_list)
                    in_list = False
                    current_key = None
                    current_list = []
                else:
                    # List item
                    item = line.strip().strip(',').strip('"\'')
                    if item:
                        current_list.append(item)

    def _set_config_value(self, config: DocManConfig, key: str, value):
        """Set configuration value based on key."""
        key_mapping = {
            'root_directory': 'root_directory',
            'index_file': 'index_file',
            'recreate_index': 'recreate_index',
            'strict_validation': 'strict_validation',
            'required_metadata': 'required_metadata',
            'valid_statuses': 'valid_statuses',
            'ignore_patterns': 'ignore_patterns',
            'verbose_output': 'verbose_output',
            'colored_output': 'colored_output',
            'emoji_indicators': 'emoji_indicators',
            'generate_reports': 'generate_reports',
            'exit_on_errors': 'exit_on_errors',
            'version_pattern': 'version_pattern',
            'date_format': 'date_format'
        }

        if key in key_mapping:
            attr_name = key_mapping[key]
            if key == 'ignore_patterns':
                # Convert list to set for ignore patterns
                setattr(config, attr_name, set(value) if isinstance(value, list) else value)
            else:
                setattr(config, attr_name, value)


def load_config(repo_root: Path = None) -> DocManConfig:
    """Convenience function to load configuration."""
    loader = ConfigLoader(repo_root)
    return loader.load_config()


def create_config_template(output_path: Path = None) -> Path:
    """Create a configuration template file."""
    if output_path is None:
        # Create template in DocMan directory
        docman_dir = Path(__file__).parent.parent
        output_path = docman_dir.parent / ".docmanrc.template"
    
    template_content = """# DocMan Configuration Template
# Copy this file to .docmanrc in your project root and customize as needed
# 
# For submodule usage: Place this file in the parent directory of the docman/ folder
# Example structure:
#   your-project/
#   ├── .docmanrc          # This configuration file
#   ├── docman/            # DocMan submodule
#   └── your-files...

# Root directory for documentation scanning
root_directory = "."

# Index file management
index_file = "DOCUMENTATION_INDEX.md"
recreate_index = true

# Validation settings
strict_validation = true

# Required metadata fields in README files
required_metadata = [
    "Status",
    "Version",
    "Last Updated"
]

# Valid status values (customize these for your project)
# Note: The first value is used as default status when creating new README files
valid_statuses = [
    "✅ Production Ready",
    "🚧 Draft",
    "🚫 Deprecated",
    "⚠️ Experimental",
    "🔄 In Progress"
]

# Version format validation (currently hardcoded to semantic versioning)
# Supported: "semantic" (x.y.z format)
# Note: Only semantic versioning is currently implemented
version_pattern = "semantic"

# Date format validation (currently hardcoded to ISO format)
# Supported: "YYYY-MM-DD" (ISO 8601 Standard, international eindeutig)
# Note: Only YYYY-MM-DD format is currently implemented
date_format = "YYYY-MM-DD"

# Ignore patterns - directories and files to skip during scanning
ignore_patterns = [
    ".git/",
    "node_modules/",
    "venv/",
    "__pycache__/",
    "vscode-extension/",
    "*.tmp",
    "*.log"
]

# Output settings
verbose_output = false
colored_output = true
emoji_indicators = true

# Reporting settings
generate_reports = true
exit_on_errors = true
"""
    
    output_path.write_text(template_content, encoding='utf-8')
    return output_path
