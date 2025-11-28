#!/usr/bin/env python3
"""
Feature Owner - Task Generation Tool

Generate task list from PRD document.

Usage:
    python generate_tasks.py --prd path/to/PRD.md --output path/to/TASKS.md
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


def parse_prd(prd_path: Path) -> dict:
    """Parse PRD and extract key information."""
    with open(prd_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract feature name from title
    title_match = re.search(r'^#\s+(.+?)\s+-\s+產品需求文檔', content, re.MULTILINE)
    feature_name = title_match.group(1) if title_match else "Unknown Feature"
    
    # Extract functional requirements
    # This is a simplified version - real implementation would be more sophisticated
    functional_reqs = []
    inreqs_section = False
    
    for line in content.split('\n'):
        if '## 3. 功能需求' in line:
            inreqs_section = True
        elif line.startswith('## ') and inreqs_section:
            break
        elif inreqs_section and line.startswith('###'):
            functional_reqs.append(line.strip('#').strip())
    
    return {
        'feature_name': feature_name,
        'functional_requirements': functional_reqs
    }


def generate_tasks(prd_info: dict, owner: str = "待分配") -> str:
    """Generate task list from PRD information."""
    today = datetime.now().strftime("%Y-%m-%d")
    feature_name = prd_info['feature_name']
    
    task_content = f"""# {feature_name} - 任務列表

**Feature Owner**：{owner}
**開始日期**：{today}
**狀態**：🟢 規劃中

---

## 任務狀態圖例

- `[ ]` 待辦
- `[/]` 進行中
- `[x]` 已完成
- `[!]` 被阻塞

## 優先級標記

- **P0**：必須有 (Must Have)
- **P1**：應該有 (Should Have)
- **P2**：可以有 (Nice to Have)

---

## 里程碑 M0：架構與設計

### TASK-001：系統架構設計
- **優先級**：P0
- **負責人**：待分配
- **預估工時**：2天
- **狀態**：[ ]

**描述**：設計整體系統架構

**驗收標準**：
- [ ] 架構圖完成並經過審查
- [ ] 技術棧選擇確定
- [ ] 服務邊界清晰定義

---

### TASK-002：數據庫Schema設計
- **優先級**：P0
- **負責人**：待分配
- **預估工時**：1.5天
- **狀態**：[ ]

**描述**：設計數據庫表結構、關係、索引

**驗收標準**：
- [ ] ER圖完成
- [ ] 所有表和欄位定義清晰
- [ ] 經過架構師審查

---

## 里程碑 M1：基礎設施與核心功能

"""
    
    # Add task基於功能需求
    task_id = 101
    for req in prd_info['functional_requirements']:
        task_content += f"""### TASK-{task_id:03d}：實現{req}
- **優先級**：P0
- **負責人**：待分配
- **預估工時**：待評估
- **狀態**：[ ]

**描述**：實現{req}功能

**驗收標準**：
- [ ] 功能按PRD要求實現
- [ ] 單元測試覆蓋率 ≥ 80%
- [ ] 代碼審查通過

---

"""
        task_id += 1
    
    task_content += f"""
## 備註

本任務列表基於PRD自動生成，需要團隊評審和細化。

**下一步**：
1. 團隊評審任務列表
2. 細化任務描述和驗收標準
3. 評估工時並分配負責人
4. 確定里程碑時間線

---

**最後更新**：{today}
**生成工具**：generate_tasks.py
"""
    
    return task_content


def main():
    parser = argparse.ArgumentParser(description="Generate task list from PRD")
    parser.add_argument("--prd", required=True, type=Path, help="Path to PRD.md")
    parser.add_argument("--output", required=True, type=Path, help="Output path for TASKS.md")
    parser.add_argument("--owner", default="待分配", help="Feature owner name")
    
    args = parser.parse_args()
    
    if not args.prd.exists():
        print(f"❌ PRD file not found: {args.prd}", file=sys.stderr)
        return 1
    
    try:
        print(f"📖 Reading PRD from: {args.prd}")
        prd_info = parse_prd(args.prd)
        
        print(f"✏️  Generating tasks for: {prd_info['feature_name']}")
        print(f"📋 Found {len(prd_info['functional_requirements'])} functional requirements")
        
        tasks = generate_tasks(prd_info, args.owner)
        
        # Create output directory if needed
        args.output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(tasks)
        
        print(f"✅ Task list generated: {args.output}")
        print(f"\n💡 Next step: Review and refine the generated tasks with your team")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
