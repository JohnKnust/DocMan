"""
Metadata Format Validator

Validates that README.md files contain properly formatted metadata blocks
with required fields: Status, Version, and Last Updated.
"""

import re
from typing import List, Dict, Optional, Set
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils import find_all_markdown_files, should_ignore_path, DEFAULT_IGNORE_PATTERNS


class MetadataValidator:
    """Validates metadata format in markdown files."""

    # Default values (fallback when no config available)
    DEFAULT_REQUIRED_FIELDS = {'Status', 'Version', 'Last Updated'}
    DEFAULT_VALID_STATUSES = {
        '✅ Production Ready',
        '🚧 Draft',
        '🚫 Deprecated',
        '⚠️ Experimental',
        '🔄 In Progress'
    }

    # Files that don't require metadata
    METADATA_EXEMPT_FILES = {
        'CHANGELOG.md',
        'CHANGELOG',
        'LICENSE.md',
        'LICENSE',
        'CONTRIBUTING.md',
        'CODE_OF_CONDUCT.md',
        'SECURITY.md',
        'DOCUMENTATION_INDEX.md'
    }

    def __init__(self, repo_root: Path, ignore_patterns: Set[str] = None, config=None):
        """Initialize validator with repository root, ignore patterns, and config."""
        self.repo_root = Path(repo_root)
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS.copy()
        self.config = config

        # Set dynamic fields based on config
        if config and hasattr(config, 'required_metadata') and config.required_metadata:
            self.required_fields = set(config.required_metadata)
        else:
            self.required_fields = self.DEFAULT_REQUIRED_FIELDS.copy()

        if config and hasattr(config, 'valid_statuses') and config.valid_statuses:
            self.valid_statuses = config.valid_statuses  # Keep as list to preserve emoji order
        else:
            self.valid_statuses = list(self.DEFAULT_VALID_STATUSES)

        # Version and date patterns
        self.version_pattern = getattr(config, 'version_pattern', 'semantic') if config else 'semantic'
        self.date_format = getattr(config, 'date_format', 'YYYY-MM-DD') if config else 'YYYY-MM-DD'
    
    def parse_metadata_block(self, content: str) -> Dict[str, str]:
        """Parse metadata block from README content (only from the beginning)."""
        metadata = {}

        # Split content into lines and look for metadata only in the first section
        lines = content.split('\n')

        # Find the first heading (# Title) and only look for metadata before the next section
        in_metadata_section = False
        metadata_section_ended = False

        for line in lines:
            line = line.strip()

            # Skip empty lines and title
            if not line or line.startswith('# '):
                if line.startswith('# '):
                    in_metadata_section = True
                continue

            # Stop looking for metadata after the first ## section or other content
            if in_metadata_section and (line.startswith('## ') or
                                       (line and not line.startswith('**') and not metadata_section_ended)):
                if not line.startswith('**'):
                    metadata_section_ended = True
                    break

            # Look for metadata pattern: **Field**: Value
            if in_metadata_section and line.startswith('**') and '**:' in line:
                match = re.match(r'\*\*([^*]+)\*\*:\s*(.+)', line)
                if match:
                    field, value = match.groups()
                    metadata[field.strip()] = value.strip()

        return metadata
    
    def validate_metadata(self, file_path: Path) -> List[str]:
        """Validate metadata in a single README file."""
        violations = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            violations.append(f"Could not read file: {e}")
            return violations
        
        metadata = self.parse_metadata_block(content)
        
        # Check for missing required fields (dynamic based on config)
        missing_fields = self.required_fields - set(metadata.keys())
        for field in missing_fields:
            violations.append(f'missing "{field}"')

        # Validate Status field if present (dynamic based on config)
        if 'Status' in metadata:
            status = metadata['Status']
            if status not in self.valid_statuses:
                # Sort but preserve emoji order (don't sort alphabetically)
                valid_options = ', '.join(self.valid_statuses)
                violations.append(f'invalid status "{status}" (valid options: {valid_options})')
        
        # Validate Version field format if present (dynamic based on config)
        if 'Version' in metadata:
            version = metadata['Version']
            if self.version_pattern == 'semantic':
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    violations.append(f'invalid version format "{version}" (expected semantic versioning x.y.z)')
            else:
                # Custom pattern validation could be added here
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    violations.append(f'invalid version format "{version}" (check .docmanrc version_pattern)')

        # Validate Last Updated field format if present and not empty (dynamic based on config)
        if 'Last Updated' in metadata:
            date = metadata['Last Updated'].strip()
            # Only validate if date is not empty
            if date:
                if self.date_format == 'YYYY-MM-DD':
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                        violations.append(f'invalid date format "{date}" (expected YYYY-MM-DD ISO 8601 Standard, international eindeutig)')
                else:
                    # Custom date format validation could be added here
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                        violations.append(f'invalid date format "{date}" (check .docmanrc date_format: {self.date_format})')
        
        return violations
    
    def validate_all_readmes(self) -> List[str]:
        """Validate metadata in all README.md files."""
        all_violations = []
        
        # Find all markdown files
        md_files = find_all_markdown_files(self.repo_root, self.ignore_patterns)
        
        # All markdown files should have metadata (not just READMEs)
        markdown_files = md_files
        
        for markdown_file in markdown_files:
            # Skip files that don't require metadata
            if markdown_file.name in self.METADATA_EXEMPT_FILES:
                continue

            violations = self.validate_metadata(markdown_file)
            if violations:
                # Make path relative to repo root
                relative_path = markdown_file.relative_to(self.repo_root)
                for violation in violations:
                    all_violations.append(f"🚧 Bad metadata in {relative_path}: {violation}")
        
        return all_violations
    
    def validate(self) -> List[str]:
        """Run metadata validation and return list of violations."""
        return self.validate_all_readmes()
    
    def get_summary(self) -> str:
        """Get a summary of metadata validation results."""
        violations = self.validate()
        count = len(violations)
        
        if count == 0:
            return "✅ All README metadata is properly formatted"
        else:
            return f"🚧 {count} metadata violations found"
