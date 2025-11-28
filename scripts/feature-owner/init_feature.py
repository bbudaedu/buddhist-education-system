#!/usr/bin/env python3
"""
Feature Owner - Feature Initialization Tool

This script initializes a new feature with the standard Feature Owner directory
structure and template files.

Usage:
    python init_feature.py --name "Feature Name" --owner "John Doe"

"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


def create_directory_structure(feature_name: str, base_path: Path) -> Path:
    """Create the feature directory structure."""
    # Sanitize feature name for directory
    dir_name = feature_name.lower().replace(" ", "-").replace("_", "-")
    feature_dir = base_path / "docs" / "features" / dir_name
    
    directories = [
        feature_dir,
        feature_dir / "artifacts",
        feature_dir / "artifacts" / "architecture",
        feature_dir / "artifacts" / "adr",
        feature_dir / "artifacts" / "reports",
        feature_dir / "artifacts" / "releases",
        feature_dir / "artifacts" / "lessons-learned",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory.relative_to(base_path)}")
    
    return feature_dir


def copy_template(template_name: str, dest_path: Path, base_path: Path,
                  replacements: dict) -> None:
    """Copy and customize a template file."""
    template_dir = base_path / "templates" / "feature-owner"
    template_path = template_dir / template_name
    
    if not template_path.exists():
        print(f"⚠ Template not found: {template_name}")
        return
    
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply replacements
    for key, value in replacements.items():
        content = content.replace(key, value)
    
    # Write destination
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Created file: {dest_path.name}")


def initialize_feature(feature_name: str, owner_name: str, 
                       base_path: Path = None) -> None:
    """Initialize a new feature with all templates."""
    
    if base_path is None:
        # Assume script is in scripts/feature-owner/
        base_path = Path(__file__).parent.parent.parent
    
    print(f"\n🚀 Initializing feature: {feature_name}")
    print(f"👤 Feature Owner: {owner_name}")
    print(f"📁 Base path: {base_path}\n")
    
    # Create directory structure
    feature_dir = create_directory_structure(feature_name, base_path)
    
    # Prepare replacements
    today = datetime.now().strftime("%Y-%m-%d")
    replacements = {
        "[功能名稱]": feature_name,
        "[Feature Owner姓名]": owner_name,
        "[姓名]": owner_name,
        "YYYY-MM-DD": today,
    }
    
    # Copy templates
    templates = {
        "PRD_TEMPLATE.md": "PRD.md",
        "TASK_LIST_TEMPLATE.md": "TASKS.md",
        "MILESTONE_TEMPLATE.md": "MILESTONES.md",
        "IMPLEMENTATION_CHECKLIST_TEMPLATE.md": "IMPLEMENTATION_CHECKLIST.md",
    }
    
    print("\n📝 Creating template files:")
    for template_file, dest_file in templates.items():
        copy_template(
            template_file,
            feature_dir / dest_file,
            base_path,
            replacements
        )
    
    # Create README
    readme_content = f"""# {feature_name}

**Feature Owner**: {owner_name}
**Created**: {today}
**Status**: Planning

## 文檔

- [PRD](./PRD.md) - 產品需求文檔
- [任務列表](./TASKS.md) - 任務追蹤
- [里程碑](./MILESTONES.md) - 里程碑追蹤
- [實施檢查清單](./IMPLEMENTATION_CHECKLIST.md)

## Artifacts

- [架構設計](./artifacts/architecture/)
- [技術決策記錄](./artifacts/adr/)
- [進度報告](./artifacts/reports/)
- [發布資料](./artifacts/releases/)

## 下一步

1. 填寫PRD文檔
2. 與團隊審查PRD
3. 運行任務規劃工作流程: `/task-planning`
4. 開始開發！
"""
    
    with open(feature_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✓ Created file: README.md")
    
    # Success message
    print(f"\n✅ Feature initialized successfully!")
    print(f"\n📂 Feature directory: {feature_dir.relative_to(base_path)}")
    print(f"\n🎯 Next steps:")
    print(f"   1. cd {feature_dir.relative_to(base_path)}")
    print(f"   2. Edit PRD.md to define your feature requirements")
    print(f"   3. Run task planning workflow: /task-planning")
    print(f"\n💡 Tip: Refer to the Feature Owner Guide for best practices:")
    print(f"   docs/feature-owner/FEATURE_OWNER_GUIDE.md\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize a new feature with Feature Owner templates"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Feature name (e.g., 'User Authentication')"
    )
    parser.add_argument(
        "--owner",
        required=True,
        help="Feature owner name (e.g., 'John Doe')"
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        help="Base path of the project (default: auto-detect)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without creating files"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be created\n")
        print(f"Feature Name: {args.name}")
        print(f"Feature Owner: {args.owner}")
        print(f"This would create a new feature directory with all templates.")
        return 0
    
    try:
        initialize_feature(args.name, args.owner, args.base_path)
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
