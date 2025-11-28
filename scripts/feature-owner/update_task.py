#!/usr/bin/env python3
"""
Feature Owner - Task Status Update Tool

Update task status in TASKS.md.

Usage:
    python update_task.py --feature "feature-name" --task "TASK-001" --status completed
    python update_task.py --feature "feature-name" --task "TASK-001" --status in-progress
    python update_task.py --feature "feature-name" --task "TASK-001" --status blocked --note "等待API確認"
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


STATUS_MAP = {
    'todo': '[ ]',
    'in-progress': '[/]',
    'completed': '[x]',
    'blocked': '[!]'
}


def update_task_status(tasks_file: Path, task_id: str, new_status: str, note: str = None) -> bool:
    """Update task status in TASKS.md."""
    
    if not tasks_file.exists():
        print(f"❌ TASKS.md not found: {tasks_file}", file=sys.stderr)
        return False
    
    with open(tasks_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the task section
    task_pattern = rf'(###\s+{re.escape(task_id)}[^\n]*\n.*?- \*\*狀態\*\*：)(\[.\])'
    
    match = re.search(task_pattern, content, re.DOTALL)
    if not match:
        print(f"❌ Task {task_id} not found in TASKS.md", file=sys.stderr)
        return False
    
    # Replace status
    status_symbol = STATUS_MAP.get(new_status)
    if not status_symbol:
        print(f"❌ Invalid status: {new_status}", file=sys.stderr)
        print(f"Valid statuses: {', '.join(STATUS_MAP.keys())}", file=sys.stderr)
        return False
    
    new_content = re.sub(
        task_pattern,
        rf'\g<1>{status_symbol}',
        content,
        count=1,
        flags=re.DOTALL
    )
    
    # Add note if provided and task is blocked
    if note and new_status == 'blocked':
        # Find the task section and add note
        note_text = f"\n\n**阻塞原因**: {note}\n**阻塞時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        # Insert note after the acceptance criteria section
        new_content = re.sub(
            rf'(###\s+{re.escape(task_id)}.*?---)',
            rf'\g<1>{note_text}\n\n---',
            new_content,
            count=1,
            flags=re.DOTALL
        )
    
    # Write back
    with open(tasks_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def calculate_progress(tasks_file: Path) -> dict:
    """Calculate progress statistics."""
    
    with open(tasks_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count task statuses
    total = len(re.findall(r'- \*\*狀態\*\*：\[.\]', content))
    completed = len(re.findall(r'- \*\*狀態\*\*：\[x\]', content))
    in_progress = len(re.findall(r'- \*\*狀態\*\*：\[/\]', content))
    blocked = len(re.findall(r'- \*\*狀態\*\*：\[!\]', content))
    todo = total - completed - in_progress - blocked
    
    progress_pct = (completed / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'completed': completed,
        'in_progress': in_progress,
        'blocked': blocked,
        'todo': todo,
        'progress': progress_pct
    }


def update_progress_overview(tasks_file: Path, stats: dict):
    """Update the progress overview section in TASKS.md."""
    
    with open(tasks_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and update progress bar
    progress_bar = '█' * int(stats['progress'] / 10) + '░' * (10 - int(stats['progress'] / 10))
    
    # Update overview table
    overview_pattern = r'(\*\*完成情況\*\*：)([█░]+)\s+(\d+%)\s+\((\d+)/(\d+)\s+任務\)'
    new_overview = rf'\g<1>{progress_bar} {stats["progress"]:.0f}% ({stats["completed"]}/{stats["total"]} 任務)'
    
    content = re.sub(overview_pattern, new_overview, content)
    
    with open(tasks_file, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description="Update task status in TASKS.md")
    parser.add_argument("--feature", required=True, help="Feature name")
    parser.add_argument("--task", required=True, help="Task ID (e.g., TASK-001)")
    parser.add_argument("--status", required=True, 
                        choices=['todo', 'in-progress', 'completed', 'blocked'],
                        help="New status")
    parser.add_argument("--note", help="Note for blocked tasks")
    parser.add_argument("--base-path", type=Path, help="Base project path")
    
    args = parser.parse_args()
    
    # Find feature directory
    if args.base_path:
        base_path = args.base_path
    else:
        base_path = Path(__file__).parent.parent.parent
    
    feature_dir = base_path / "docs" / "features" / args.feature
    tasks_file = feature_dir / "TASKS.md"
    
    if not feature_dir.exists():
        print(f"❌ Feature directory not found: {feature_dir}", file=sys.stderr)
        return 1
    
    try:
        print(f"📝 Updating {args.task} status to: {args.status}")
        
        # Update task status
        success = update_task_status(tasks_file, args.task, args.status, args.note)
        
        if not success:
            return 1
        
        # Calculate and update progress
        stats = calculate_progress(tasks_file)
        update_progress_overview(tasks_file, stats)
        
        print(f"✅ Task {args.task} updated successfully!")
        print(f"\n📊 Overall Progress:")
        print(f"   Total: {stats['total']} tasks")
        print(f"   ✅ Completed: {stats['completed']}")
        print(f"   🚧 In Progress: {stats['in_progress']}")
        print(f"   ⛔ Blocked: {stats['blocked']}")
        print(f"   📋 To Do: {stats['todo']}")
        print(f"   Progress: {stats['progress']:.0f}%")
        
        if args.status == 'blocked' and args.note:
            print(f"\n⚠️  Task is blocked: {args.note}")
            print(f"💡 Tip: Resolve blocking issue and update status to 'in-progress'")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
