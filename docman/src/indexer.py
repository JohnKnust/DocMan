"""
Documentation Index Manager

Handles creation and maintenance of DOCUMENTATION_INDEX.md files.
Manages the central index of all documentation files in the repository.
"""

from typing import List, Dict, Optional, Set
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from utils import find_all_markdown_files, should_ignore_path, DEFAULT_IGNORE_PATTERNS


class DocumentationIndexer:
    """Manages the DOCUMENTATION_INDEX.md file for a repository."""

    def __init__(self, repo_root: Path, ignore_patterns: Set[str] = None):
        """Initialize the indexer with repository root path."""
        self.repo_root = Path(repo_root)
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS
        # Only create index in the actual repository root
        self.index_file = self._find_repository_root() / "DOCUMENTATION_INDEX.md"

    def _find_repository_root(self) -> Path:
        """Find the actual repository root by looking for .git directory."""
        current = Path(self.repo_root).resolve()

        # Walk up the directory tree to find .git
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent

        # If no .git found, use the provided repo_root
        return Path(self.repo_root)
    
    def load_existing_index(self) -> Dict[str, str]:
        """Load existing index entries from DOCUMENTATION_INDEX.md."""
        indexed_files = {}

        if not self.index_file.exists():
            return indexed_files

        try:
            content = self.index_file.read_text(encoding='utf-8')

            # Parse markdown links in the index: [path](path)
            import re
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = re.findall(pattern, content)

            for title, path in matches:
                # Store the path as key for quick lookup
                indexed_files[path] = title

        except Exception:
            pass

        return indexed_files
    
    def find_missing_entries(self, all_md_files: List[Path]) -> List[Path]:
        """Find markdown files not listed in the index."""
        indexed_files = self.load_existing_index()
        missing_files = []

        for md_file in all_md_files:
            # Convert to relative path from repo root
            try:
                relative_path = md_file.relative_to(self.repo_root)
                relative_path_str = str(relative_path)

                # Check if this file is already indexed
                if relative_path_str not in indexed_files:
                    missing_files.append(md_file)

            except ValueError:
                # File is outside repo root, skip
                continue

        return missing_files
    
    def parse_metadata_from_file(self, file_path: Path) -> Dict[str, str]:
        """Parse metadata from a markdown file."""
        metadata = {'Status': '🚧 Draft', 'Version': '0.0.0', 'Last Updated': '2025-01-01'}

        try:
            content = file_path.read_text(encoding='utf-8')

            # Look for metadata in the first section after title
            import re
            lines = content.split('\n')
            in_metadata_section = False

            for line in lines:
                line = line.strip()

                if line.startswith('# '):
                    in_metadata_section = True
                    continue

                if in_metadata_section and (line.startswith('## ') or
                                           (line and not line.startswith('**') and not line.startswith('#'))):
                    if not line.startswith('**'):
                        break

                if in_metadata_section and line.startswith('**') and '**:' in line:
                    match = re.match(r'\*\*([^*]+)\*\*:\s*(.+)', line)
                    if match:
                        field, value = match.groups()
                        metadata[field.strip()] = value.strip()

        except Exception:
            pass

        return metadata

    def _get_section_name(self, file_path: Path) -> str:
        """Get section name for a file based on its directory structure."""
        relative_path = file_path.relative_to(self.repo_root)
        parts = relative_path.parts

        if len(parts) == 1:  # Root level
            return "Project Root"
        else:
            # Use the actual directory name with intelligent formatting
            dir_name = parts[0]

            # Convert to readable format: replace separators with spaces and use title case
            formatted_name = dir_name.replace('-', ' ').replace('_', ' ').title()

            return formatted_name

    def update_index(self, missing_files: List[Path]) -> int:
        """Rebuild the documentation index completely to ensure it's always correct and up-to-date."""
        # Always rebuild the index completely to ensure it's clean and uses current logic
        # Use the same ignore patterns as the CLI for consistency
        self._rebuild_index(self.ignore_patterns)

        # Return 0 since we always rebuild completely
        # The missing_files parameter is kept for compatibility but not used
        return 0

    def _generate_index_content(self, files: List[Path]) -> str:
        """Generate complete index content from list of files with simple directory grouping."""
        content = "# Documentation Index\n\nThis file contains links to all documentation in the repository.\n\n"

        # Group files by top-level directory
        sections = {}

        for file_path in files:
            relative_path = file_path.relative_to(self.repo_root)
            parts = relative_path.parts

            if len(parts) == 1:  # Root level file
                section_name = "Project Root"
            else:
                # Use first directory as section name
                section_name = parts[0].replace('-', ' ').replace('_', ' ').title()

            if section_name not in sections:
                sections[section_name] = []
            sections[section_name].append(file_path)

        # Sort sections (Project Root first, then alphabetically)
        sorted_sections = sorted(sections.keys(), key=lambda x: (x != "Project Root", x))

        # Generate content for each section
        for section_name in sorted_sections:
            content += f"\n## {section_name}\n"

            # Sort files within section by path
            section_files = sorted(sections[section_name], key=lambda x: str(x.relative_to(self.repo_root)))

            for file_path in section_files:
                relative_path = file_path.relative_to(self.repo_root)
                metadata = self.parse_metadata_from_file(file_path)

                status = metadata.get('Status', '🚧 Draft')
                date = metadata.get('Last Updated', '2025-01-01')

                content += f"- [{relative_path}]({relative_path}) – {status} – {date}\n"

            content += "\n"

        return content

    def _cleanup_index(self):
        """Remove entries for files that no longer exist or should be ignored."""
        if not self.index_file.exists():
            return

        try:
            content = self.index_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            cleaned_lines = []

            for line in lines:
                # Check if line contains a markdown link
                import re
                link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)

                if link_match:
                    file_path = link_match.group(2)

                    # Check if path should be ignored (simple string matching)
                    should_ignore = False

                    # Check for .vscode-test specifically
                    if '.vscode-test' in file_path:
                        should_ignore = True

                    # Check other patterns
                    if not should_ignore:
                        for pattern in self.ignore_patterns:
                            pattern_clean = pattern.rstrip('/')
                            if pattern_clean in file_path:
                                should_ignore = True
                                break

                    # Also check if file exists
                    full_path = self.repo_root / file_path
                    file_exists = full_path.exists()

                    # Keep line only if file exists AND is not ignored
                    if file_exists and not should_ignore:
                        cleaned_lines.append(line)
                    # Skip this line if file doesn't exist or should be ignored
                else:
                    # Keep non-link lines (headers, empty lines, etc.)
                    cleaned_lines.append(line)

            # Write cleaned content back
            cleaned_content = '\n'.join(cleaned_lines)
            self.index_file.write_text(cleaned_content, encoding='utf-8')

        except Exception as e:
            # If cleanup fails, continue without error
            print(f"Warning: Index cleanup failed: {e}")
            pass

    def _rebuild_index(self, ignore_patterns: List[str]):
        """Completely rebuild the index with only valid, non-ignored files."""
        try:
            # Find all markdown files in the repository using the same logic as CLI
            all_md_files = find_all_markdown_files(self.repo_root, ignore_patterns)

            # Generate new index content
            content = self._generate_index_content(all_md_files)

            # Write the new index
            self.index_file.write_text(content, encoding='utf-8')

        except Exception as e:
            print(f"Warning: Index rebuild failed: {e}")
            pass
