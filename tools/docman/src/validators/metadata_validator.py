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
    """Validates metadata format in README.md files."""
    
    # Required metadata fields
    REQUIRED_FIELDS = {'Status', 'Version', 'Last Updated'}
    
    # Valid status values
    VALID_STATUSES = {
        '✅ Production Ready',
        '🚧 Draft', 
        '🚫 Deprecated',
        '⚠️ Experimental',
        '🔄 In Progress'
    }
    
    def __init__(self, repo_root: Path, ignore_patterns: Set[str] = None):
        """Initialize validator with repository root and ignore patterns."""
        self.repo_root = Path(repo_root)
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS.copy()
    
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
        
        # Check for missing required fields
        missing_fields = self.REQUIRED_FIELDS - set(metadata.keys())
        for field in missing_fields:
            violations.append(f'missing "{field}"')
        
        # Validate Status field if present
        if 'Status' in metadata:
            status = metadata['Status']
            if status not in self.VALID_STATUSES:
                violations.append(f'invalid status "{status}"')
        
        # Validate Version field format if present
        if 'Version' in metadata:
            version = metadata['Version']
            # Basic semantic version check (x.y.z)
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                violations.append(f'invalid version format "{version}" (expected x.y.z)')
        
        # Validate Last Updated field format if present
        if 'Last Updated' in metadata:
            date = metadata['Last Updated']
            # Basic ISO date check (YYYY-MM-DD)
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                violations.append(f'invalid date format "{date}" (expected YYYY-MM-DD)')
        
        return violations
    
    def validate_all_readmes(self) -> List[str]:
        """Validate metadata in all README.md files."""
        all_violations = []
        
        # Find all markdown files
        md_files = find_all_markdown_files(self.repo_root, self.ignore_patterns)
        
        # Filter to only README.md files
        readme_files = [f for f in md_files if f.name == 'README.md']
        
        for readme_file in readme_files:
            violations = self.validate_metadata(readme_file)
            if violations:
                # Make path relative to repo root
                relative_path = readme_file.relative_to(self.repo_root)
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
