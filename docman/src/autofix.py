"""
Auto-fix functionality for DocMan

Provides automated fixes for common documentation issues with user confirmation.
"""

import sys
from pathlib import Path
from typing import List, Set
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from config import DocManConfig


class AutoFixer:
    """Handles automatic fixes for documentation issues."""
    
    def __init__(self, repo_root: Path, config: DocManConfig):
        """Initialize auto-fixer with repository root and configuration."""
        self.repo_root = Path(repo_root)
        self.config = config
    
    def create_missing_readme_template(self, directory: Path) -> str:
        """Create a README template with dynamic metadata based on configuration."""
        # Get directory name for title
        dir_name = directory.name if directory != self.repo_root else self.repo_root.name
        
        # Build metadata section dynamically based on config
        metadata_lines = []
        required_fields = getattr(self.config, 'required_metadata', ['Status', 'Version', 'Last Updated'])
        valid_statuses = getattr(self.config, 'valid_statuses', ['🚧 Draft'])
        
        for field in required_fields:
            if field == 'Status':
                # Use first valid status as default
                default_status = valid_statuses[0] if valid_statuses else '🚧 Draft'
                metadata_lines.append(f"**{field}**: {default_status}")
            elif field == 'Version':
                metadata_lines.append(f"**{field}**: 0.1.0")
            elif field == 'Last Updated':
                today = datetime.now().strftime('%Y-%m-%d')
                metadata_lines.append(f"**{field}**: {today}")
            else:
                # For any other custom fields, leave empty for user to fill
                metadata_lines.append(f"**{field}**: ")
        
        # Join metadata with proper spacing
        metadata_section = "  \n".join(metadata_lines)
        
        template = f"""# {dir_name}

{metadata_section}

## Description

Brief description of this component/module.

## Usage

How to use this component.

## Configuration

Any configuration options or requirements.

## Notes

Additional notes or considerations.
"""
        return template
    
    def fix_missing_readmes(self, missing_readme_dirs: List[Path], interactive: bool = True) -> int:
        """
        Create missing README files with user confirmation.
        
        Args:
            missing_readme_dirs: List of directories missing README files
            interactive: Whether to ask for user confirmation
            
        Returns:
            Number of README files created
        """
        if not missing_readme_dirs:
            print("✅ No missing README files to fix")
            return 0
        
        print(f"🔧 Found {len(missing_readme_dirs)} directories missing README files:")
        for i, dir_path in enumerate(missing_readme_dirs, 1):
            relative_path = dir_path.relative_to(self.repo_root) if dir_path != self.repo_root else Path(".")
            print(f"  {i}. {relative_path}")
        
        if interactive:
            print(f"\n📝 README files will be created with metadata based on your .docmanrc:")
            required_fields = getattr(self.config, 'required_metadata', ['Status', 'Version', 'Last Updated'])
            valid_statuses = getattr(self.config, 'valid_statuses', ['🚧 Draft'])
            print(f"   • Required fields: {', '.join(required_fields)}")
            print(f"   • Default status: {valid_statuses[0] if valid_statuses else '🚧 Draft'}")
            
            response = input(f"\n❓ Create {len(missing_readme_dirs)} README files? [y/N]: ").strip().lower()
            if response not in ['y', 'yes']:
                print("❌ Auto-fix cancelled by user")
                return 0
        
        created_count = 0
        for dir_path in missing_readme_dirs:
            try:
                readme_path = dir_path / "README.md"
                template_content = self.create_missing_readme_template(dir_path)
                
                # Create the README file
                readme_path.write_text(template_content, encoding='utf-8')
                
                relative_path = dir_path.relative_to(self.repo_root) if dir_path != self.repo_root else Path(".")
                print(f"✅ Created README.md in {relative_path}")
                created_count += 1
                
            except Exception as e:
                relative_path = dir_path.relative_to(self.repo_root) if dir_path != self.repo_root else Path(".")
                print(f"❌ Failed to create README.md in {relative_path}: {e}")
        
        if created_count > 0:
            print(f"\n🎉 Successfully created {created_count} README files!")
            print("💡 Review and customize the generated content as needed")
        
        return created_count
    
    def get_missing_readme_directories(self, missing_readme_violations: List[str]) -> List[Path]:
        """
        Extract directory paths from missing README violations.
        
        Args:
            missing_readme_violations: List of violation strings like "🚧 Missing README: path/to/dir"
            
        Returns:
            List of Path objects for directories missing README files
        """
        directories = []
        for violation in missing_readme_violations:
            # Extract path from violation string
            if "Missing README:" in violation:
                path_str = violation.split("Missing README:")[-1].strip()
                dir_path = self.repo_root / path_str
                if dir_path.exists() and dir_path.is_dir():
                    directories.append(dir_path)
        
        return directories
