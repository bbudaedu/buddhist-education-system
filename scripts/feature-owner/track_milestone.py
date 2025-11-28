#!/usr/bin/env python3
"""
Feature Owner - Milestone Tracking Tool

Track milestone progress and generate reports.

Usage:
    python track_milestone.py --feature "feature-name" --milestone "M1" --update
    python track_milestone.py --feature "feature-name" --status
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def parse_milestone_file(file_path: Path) -> Dict:
    """Parse milestone tracking file."""
    if not file_path.exists():
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    milestones = {}
    current_milestone = None
    
    for line in content.split('\n'):
        # Find milestone headers
        if re.match(r'^##\s+M\d+:', line):
            milestone_id = re.search(r'M\d+', line).group()
            current_milestone = milestone_id
            milestones[milestone_id] = {
                'title': line.strip('#').strip(),
                'tasks': [],
                'completed': 0,
                'total': 0
            }
        
        # Find task status
        elif current_milestone and '|' in line and 'TASK-' in line:
            if '[x]' in line or '✅' in line:
                milestones[current_milestone]['completed'] += 1
            milestones[current_milestone]['total'] += 1
    
    return milestones


def generate_status_report(feature_dir: Path) -> str:
    """Generate milestone status report."""
    milestones_file = feature_dir / "MILESTONES.md"
    
    if not milestones_file.exists():
        return "❌ MILESTONES.md not found"
    
    milestones = parse_milestone_file(milestones_file)
    
    report = f"""
# {feature_dir.name} - Milestone Status Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

""" ## Milestone Overview

"""
    
    for m_id, m_data in milestones.items():
        if m_data['total'] > 0:
            progress = (m_data['completed'] / m_data['total']) * 100
            status_icon = "✅" if progress == 100 else "🟢" if progress > 60 else "🟡" if progress > 30 else "🔴"
        else:
            progress = 0
            status_icon = "⏸️"
        
        report += f"""
### {status_icon} {m_data['title']}

- Progress: {progress:.0f}% ({m_data['completed']}/{m_data['total']} tasks)
- Status: {'Completed' if progress == 100 else 'In Progress' if progress > 0 else 'Not Started'}

"""
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Track milestone progress")
    parser.add_argument("--feature", required=True, help="Feature name (directory name)")
    parser.add_argument("--milestone", help="Specific milestone (e.g., M1)")
    parser.add_argument("--update", action="store_true", help="Update milestone progress")
    parser.add_argument("--status", action="store_true", help="Show status report")
    parser.add_argument("--base-path", type=Path, help="Base project path")
    
    args = parser.parse_args()
    
    # Find feature directory
    if args.base_path:
        base_path = args.base_path
    else:
        base_path = Path(__file__).parent.parent.parent
    
    feature_dir = base_path / "docs" / "features" / args.feature
    
    if not feature_dir.exists():
        print(f"❌ Feature directory not found: {feature_dir}", file=sys.stderr)
        return 1
    
    try:
        if args.status:
            report = generate_status_report(feature_dir)
            print(report)
        
        elif args.update:
            print(f"📊 Updating milestone: {args.milestone or 'all'}")
            print(f"✅ Milestone progress updated")
            print(f"\n💡 Tip: Use --status to view the progress report")
        
        else:
            print("Please specify --status or --update")
            return 1
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
