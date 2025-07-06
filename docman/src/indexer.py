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

    def __init__(self, repo_root: Path, ignore_patterns: Set[str] = None, index_filename: str = "DOCUMENTATION_INDEX.md"):
        """Initialize the indexer with repository root path and configuration."""
        self.repo_root = Path(repo_root)
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS
        self.index_filename = index_filename
        # Only create index in the actual repository root
        self.index_file = self._find_repository_root() / self.index_filename

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
        """Generate complete index content with new 2-part structure: README hierarchy + Others section."""
        content = "# Documentation Index\n\nThis file contains links to all documentation in the repository.\n\n"

        # Separate README.md files from other markdown files
        readme_files = []
        other_files = []

        # Get index filename from config (default: DOCUMENTATION_INDEX.md)
        index_filename = getattr(self, 'index_filename', 'DOCUMENTATION_INDEX.md')

        for file_path in files:
            relative_path = file_path.relative_to(self.repo_root)
            filename = file_path.name

            # Skip the index file itself (only in repository root)
            if str(relative_path) == index_filename:
                continue

            if filename == 'README.md':
                readme_files.append(file_path)
            else:
                other_files.append(file_path)

        # Part 1: README.md Hierarchy (only directories with README.md)
        if readme_files:
            content += self._generate_readme_hierarchy(readme_files)

        # Part 2: Others Section (non-README markdown files)
        if other_files:
            content += self._generate_others_section(other_files)

        return content

    def _generate_readme_hierarchy(self, readme_files: List[Path]) -> str:
        """Generate hierarchical structure for README.md files only."""
        content = ""

        # Group README files by directory structure (max 2 levels: ## and ###)
        root_readmes = []
        level1_groups = {}  # top-level directory -> list of README files

        for file_path in readme_files:
            relative_path = file_path.relative_to(self.repo_root)
            parts = relative_path.parts

            if len(parts) == 1:  # Root level README.md
                root_readmes.append(file_path)
            else:
                # Group by top-level directory
                top_dir = parts[0]
                if top_dir not in level1_groups:
                    level1_groups[top_dir] = []
                level1_groups[top_dir].append(file_path)

        # Generate root level READMEs first
        if root_readmes:
            content += "## Project Root\n"
            for file_path in sorted(root_readmes, key=lambda x: str(x.relative_to(self.repo_root))):
                content += self._format_file_entry(file_path)
            content += "\n"

        # Generate level 1 directories (## headers)
        for top_dir in sorted(level1_groups.keys()):
            # Format directory name for display
            display_name = top_dir.replace('-', ' ').replace('_', ' ').title()
            content += f"## {display_name}\n"

            # Separate direct children from deeper nested files
            direct_children = []
            nested_groups = {}  # second-level dir -> list of files

            for file_path in level1_groups[top_dir]:
                relative_path = file_path.relative_to(self.repo_root)
                parts = relative_path.parts

                if len(parts) == 2:  # Direct child: top_dir/README.md
                    direct_children.append(file_path)
                else:
                    # Nested: group by second-level directory
                    second_dir = parts[1]
                    if second_dir not in nested_groups:
                        nested_groups[second_dir] = []
                    nested_groups[second_dir].append(file_path)

            # Add direct children first
            for file_path in sorted(direct_children, key=lambda x: str(x.relative_to(self.repo_root))):
                content += self._format_file_entry(file_path)

            # Add nested groups as ### subsections
            for second_dir in sorted(nested_groups.keys()):
                display_name = second_dir.replace('-', ' ').replace('_', ' ').title()
                content += f"\n### {display_name}\n"

                # Sort files within this subsection
                for file_path in sorted(nested_groups[second_dir], key=lambda x: str(x.relative_to(self.repo_root))):
                    content += self._format_file_entry(file_path)

            content += "\n"

        return content

    def _generate_others_section(self, other_files: List[Path]) -> str:
        """Generate Others section for non-README markdown files with 2-level hierarchy."""
        content = "## Others\n\n"

        # Group files by directory structure (max 2 levels)
        root_files = []
        level1_groups = {}  # top-level directory -> list of files

        for file_path in other_files:
            relative_path = file_path.relative_to(self.repo_root)
            parts = relative_path.parts

            if len(parts) == 1:  # Root level file
                root_files.append(file_path)
            else:
                # Group by top-level directory, but flatten deeper levels
                top_dir = parts[0]
                if top_dir not in level1_groups:
                    level1_groups[top_dir] = []
                level1_groups[top_dir].append(file_path)

        # Add root level files first (alphabetically sorted)
        if root_files:
            for file_path in sorted(root_files, key=lambda x: str(x.relative_to(self.repo_root))):
                content += self._format_file_entry(file_path)
            content += "\n"

        # Add grouped files by top-level directory
        for top_dir in sorted(level1_groups.keys()):
            # Format directory name for display
            display_name = top_dir.replace('-', ' ').replace('_', ' ').title()
            content += f"### {display_name}\n"

            # Sort files within this group alphabetically
            sorted_files = sorted(level1_groups[top_dir], key=lambda x: str(x.relative_to(self.repo_root)))
            for file_path in sorted_files:
                content += self._format_file_entry(file_path)

            content += "\n"

        return content

    def _format_file_entry(self, file_path: Path) -> str:
        """Format a single file entry with metadata."""
        relative_path = file_path.relative_to(self.repo_root)
        metadata = self.parse_metadata_from_file(file_path)

        status = metadata.get('Status', '🚧 Draft')
        date = metadata.get('Last Updated', '2025-01-01')

        return f"- [{relative_path}]({relative_path}) – {status} – {date}\n"

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
