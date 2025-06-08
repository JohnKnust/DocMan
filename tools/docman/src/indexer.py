"""
Documentation Index Manager

Handles creation and maintenance of DOCUMENTATION_INDEX.md files.
Manages the central index of all documentation files in the repository.
"""

from typing import List, Dict, Optional
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from utils import find_all_markdown_files, should_ignore_path, DEFAULT_IGNORE_PATTERNS


class DocumentationIndexer:
    """Manages the DOCUMENTATION_INDEX.md file for a repository."""
    
    def __init__(self, repo_root: Path):
        """Initialize the indexer with repository root path."""
        self.repo_root = Path(repo_root)
        self.index_file = self.repo_root / "DOCUMENTATION_INDEX.md"
    
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

    def categorize_file(self, file_path: Path) -> str:
        """Categorize a file based on its path."""
        relative_path = file_path.relative_to(self.repo_root)
        parts = relative_path.parts

        if len(parts) == 1:  # Root level
            return "Project Root"
        elif parts[0] == "apps":
            return "Applications"
        elif parts[0] == "libs":
            return "Libraries"
        elif parts[0] == "tools":
            return "Tools"
        elif parts[0] == "docs":
            return "Documentation"
        else:
            return "Other"

    def update_index(self, missing_files: List[Path]) -> int:
        """Add missing files to the documentation index."""
        if not missing_files:
            return 0

        # Group files by category
        categories = {}
        for file_path in missing_files:
            category = self.categorize_file(file_path)
            if category not in categories:
                categories[category] = []
            categories[category].append(file_path)

        # Read existing index or create new one
        if self.index_file.exists():
            content = self.index_file.read_text(encoding='utf-8')
        else:
            content = "# Documentation Index\n\nThis file contains links to all documentation in the repository.\n\n"

        # Add new entries for each category
        for category, files in categories.items():
            # Check if category section exists
            category_header = f"## {category}"
            if category_header not in content:
                content += f"\n{category_header}\n\n"

            # Add files to the category
            for file_path in files:
                relative_path = file_path.relative_to(self.repo_root)
                metadata = self.parse_metadata_from_file(file_path)

                status = metadata.get('Status', '🚧 Draft')
                date = metadata.get('Last Updated', '2025-01-01')

                entry = f"- [{relative_path}]({relative_path}) – {status} – {date}\n"

                # Insert entry after the category header
                lines = content.split('\n')
                insert_index = -1

                for i, line in enumerate(lines):
                    if line.strip() == category_header:
                        # Find the next empty line or next section
                        insert_index = i + 1
                        while (insert_index < len(lines) and
                               lines[insert_index].strip() != '' and
                               not lines[insert_index].startswith('##')):
                            insert_index += 1
                        break

                if insert_index >= 0:
                    lines.insert(insert_index, entry.rstrip())
                    content = '\n'.join(lines)

        # Write updated index
        try:
            self.index_file.write_text(content, encoding='utf-8')
            return len(missing_files)
        except Exception:
            return 0
