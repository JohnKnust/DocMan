"""
README Presence Validator

Validates that all directories contain README.md files according to documentation standards.
Recursively walks directories while respecting ignore patterns.
"""

from typing import List, Set
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils import find_all_directories, should_ignore_path, DEFAULT_IGNORE_PATTERNS


class ReadmeValidator:
    """Validates README.md presence in directories."""
    
    def __init__(self, repo_root: Path, ignore_patterns: Set[str] = None):
        """Initialize validator with repository root and ignore patterns."""
        self.repo_root = Path(repo_root)
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS.copy()
    
    def find_directories_without_readme(self) -> List[Path]:
        """Find all directories that are missing README.md files."""
        missing_readmes = []
        
        # Get all directories that should be checked
        directories = find_all_directories(self.repo_root, self.ignore_patterns)
        
        # Add the root directory to the check
        if not should_ignore_path(self.repo_root, self.ignore_patterns):
            directories.insert(0, self.repo_root)
        
        for directory in directories:
            readme_path = directory / "README.md"
            if not readme_path.exists():
                # Make path relative to repo root for reporting
                relative_path = directory.relative_to(self.repo_root)
                missing_readmes.append(relative_path)
        
        return missing_readmes
    
    def validate(self) -> List[str]:
        """Run README presence validation and return list of violations."""
        missing_dirs = self.find_directories_without_readme()
        
        violations = []
        for dir_path in missing_dirs:
            violations.append(f"🚧 Missing README: {dir_path}")
        
        return violations
    
    def get_summary(self) -> str:
        """Get a summary of README validation results."""
        violations = self.validate()
        count = len(violations)
        
        if count == 0:
            return "✅ All directories have README.md files"
        else:
            return f"🚧 {count} directories missing README.md files"
