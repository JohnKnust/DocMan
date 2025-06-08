"""
Link and Date Integrity Validator

Validates that markdown links point to existing files and manages date consistency
between parent and child documentation files.
"""

import re
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils import find_all_markdown_files, should_ignore_path, DEFAULT_IGNORE_PATTERNS


class LinkValidator:
    """Validates link integrity and date consistency in markdown files."""
    
    def __init__(self, repo_root: Path, ignore_patterns: Set[str] = None):
        """Initialize validator with repository root and ignore patterns."""
        self.repo_root = Path(repo_root)
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS.copy()
    
    def extract_markdown_links(self, content: str) -> List[str]:
        """Extract markdown links from content."""
        # Pattern for markdown links: [text](path)
        pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        
        # Return only the link paths, filter out external URLs
        links = []
        for text, link in matches:
            # Skip external URLs (http, https, mailto, etc.)
            if not (link.startswith('http://') or link.startswith('https://') or 
                   link.startswith('mailto:') or link.startswith('ftp://')):
                links.append(link)
        
        return links
    
    def validate_links_in_file(self, file_path: Path) -> List[str]:
        """Validate all links in a single markdown file."""
        violations = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            violations.append(f"Could not read file: {e}")
            return violations
        
        links = self.extract_markdown_links(content)
        
        for link in links:
            # Resolve link relative to the file's directory
            link_path = (file_path.parent / link).resolve()
            
            # Check if the linked file exists
            if not link_path.exists():
                relative_file = file_path.relative_to(self.repo_root)
                violations.append(f"🚧 Broken link in {relative_file}: {link}")
        
        return violations
    
    def parse_last_updated_date(self, content: str) -> Optional[datetime]:
        """Parse the Last Updated date from README metadata."""
        # Look for **Last Updated**: YYYY-MM-DD pattern
        pattern = r'\*\*Last Updated\*\*:\s*(\d{4}-\d{2}-\d{2})'
        match = re.search(pattern, content)
        
        if match:
            try:
                date_str = match.group(1)
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                return None
        
        return None
    
    def update_last_updated_date(self, file_path: Path, new_date: str) -> bool:
        """Update the Last Updated date in a README file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Replace the Last Updated date
            pattern = r'(\*\*Last Updated\*\*:\s*)(\d{4}-\d{2}-\d{2})'
            new_content = re.sub(pattern, f'\\g<1>{new_date}', content)
            
            if new_content != content:
                file_path.write_text(new_content, encoding='utf-8')
                return True
            
        except Exception:
            pass
        
        return False
    
    def check_date_consistency(self) -> List[str]:
        """Check date consistency between parent and child READMEs and report outdated parents."""
        date_issues = []

        # Find all README files
        md_files = find_all_markdown_files(self.repo_root, self.ignore_patterns)
        readme_files = [f for f in md_files if f.name == 'README.md']

        # Build a directory hierarchy map
        dir_to_readme = {}
        for readme in readme_files:
            dir_path = readme.parent
            dir_to_readme[dir_path] = readme

        # Check each README against its parent
        for readme_path in readme_files:
            current_dir = readme_path.parent
            parent_dir = current_dir.parent

            # Skip if we're at the repo root or parent is ignored
            if parent_dir == self.repo_root.parent or should_ignore_path(parent_dir, self.ignore_patterns):
                continue

            # Find parent README
            parent_readme = dir_to_readme.get(parent_dir)
            if not parent_readme:
                continue

            # Parse dates from both files
            try:
                child_content = readme_path.read_text(encoding='utf-8')
                parent_content = parent_readme.read_text(encoding='utf-8')

                child_date = self.parse_last_updated_date(child_content)
                parent_date = self.parse_last_updated_date(parent_content)

                # If child is newer than parent, report the issue
                if child_date and parent_date and child_date > parent_date:
                    child_date_str = child_date.strftime('%Y-%m-%d')
                    parent_date_str = parent_date.strftime('%Y-%m-%d')
                    relative_parent = parent_readme.relative_to(self.repo_root)
                    relative_child = readme_path.relative_to(self.repo_root)
                    date_issues.append(f"🚧 Parent {relative_parent} ({parent_date_str}) is older than child {relative_child} ({child_date_str})")

            except Exception:
                continue

        return date_issues
    
    def validate_all_links(self) -> List[str]:
        """Validate links in all markdown files."""
        all_violations = []
        
        # Find all markdown files (not just READMEs)
        md_files = find_all_markdown_files(self.repo_root, self.ignore_patterns)
        
        for md_file in md_files:
            violations = self.validate_links_in_file(md_file)
            all_violations.extend(violations)
        
        return all_violations
    
    def validate(self) -> Tuple[List[str], List[str]]:
        """Run link validation and date consistency checks."""
        link_violations = self.validate_all_links()
        date_issues = self.check_date_consistency()

        return link_violations, date_issues
    
    def get_summary(self) -> str:
        """Get a summary of link validation results."""
        link_violations, date_issues = self.validate()
        link_count = len(link_violations)
        date_count = len(date_issues)

        if link_count == 0 and date_count == 0:
            return "✅ All links are valid and dates are consistent"
        else:
            return f"🚧 {link_count} broken links, {date_count} date inconsistencies found"
