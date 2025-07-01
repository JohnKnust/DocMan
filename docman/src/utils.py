"""
Utility functions for DocMan

Common utilities used across the DocMan application.
"""

from typing import List, Set
from pathlib import Path


# Default ignore patterns for directory traversal
DEFAULT_IGNORE_PATTERNS = {
    '.git',
    'node_modules', 
    'venv',
    '__pycache__',
    'core',
    '.pytest_cache',
    '.mypy_cache',
    'dist',
    'build'
}


def should_ignore_path(path: Path, ignore_patterns: Set[str] = None) -> bool:
    """Check if a path should be ignored based on ignore patterns."""
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS
    
    # Check if any part of the path matches ignore patterns
    for part in path.parts:
        if part in ignore_patterns:
            return True
    return False


def find_all_directories(root: Path, ignore_patterns: Set[str] = None) -> List[Path]:
    """Recursively find all directories, respecting ignore patterns."""
    directories = []
    
    for path in root.rglob('*'):
        if path.is_dir() and not should_ignore_path(path, ignore_patterns):
            directories.append(path)
    
    return directories


def find_all_markdown_files(root: Path, ignore_patterns: Set[str] = None) -> List[Path]:
    """Recursively find all markdown files, respecting ignore patterns."""
    md_files = []
    
    for path in root.rglob('*.md'):
        if not should_ignore_path(path, ignore_patterns):
            md_files.append(path)
    
    return md_files
