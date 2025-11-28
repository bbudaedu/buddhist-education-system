#!/usr/bin/env python3
"""
Feature Owner - Artifact Generation Tool

Generate artifact documents for milestones and releases.

Usage:
    python generate_artifact.py --feature "feature-name" --type milestone-report --milestone M1
    python generate_artifact.py --feature "feature-name" --type release-notes --version 1.0.0
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


ARTIFACT_TYPES = [
    "milestone-report",
    "release-notes",
    "delivery-report",
    "adr",
    "test-report"
]


def generate_milestone_report(feature_name: str, milestone: str, owner: str) -> str:
    """Generate milestone completion report."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    return f"""# {feature_name} - {milestone} 完成報告

**日期**：{today}
**里程碑**：{milestone}
**負責人**：{owner}

---

## 執行摘要

[簡要總結本里程碑的目標、完成情況和主要成就]

---

## 目標達成情況

### 原定目標
1. ✅ [目標1]
2. ✅ [目標2]
3. ⚠️ [目標3]（90%完成）

### 驗收標準檢查
- [x] [標準1]
- [x] [標準2]
- [/] [標準3]（進行中）

---

## 關鍵指標

| 指標 | 目標 | 實際 | 狀態 |
|------|------|------|------|
| 任務完成率 | 100% | 95% | 🟡 |
| 測試覆蓋率 | ≥80% | 82% | 🟢 |

---

## 完成的主要工作

- [主要工作1]
- [主要工作2]

---

## 遇到的挑戰與解決方案

### 挑戰1：[描述]
**解決方案**：[描述]
**經驗**：[學到什麼]

---

## 下階段計劃

[下個里程碑的準備工作]

---

**報告生成時間**：{today}
**生成工具**：generate_artifact.py
"""


def generate_release_notes(feature_name: str, version: str, owner: str) -> str:
    """Generate release notes."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    return f"""# Release Notes - {feature_name} v{version}

**發布日期**：{today}
**版本**：v{version}
**Feature Owner**：{owner}

---

## 📋 概述

[簡要描述本次發布的核心價值和主要功能]

---

## ✨ 新功能

### [功能1]
[描述功能和用戶價值]

---

## 🔧 改進

- [改進1]
- [改進2]

---

## 🐛 Bug修復

- [修復1]
- [修復2]

---

## ⚠️ 破壞性變更

[列出不向後兼容的變更，如無則說明無破壞性變更]

---

## 📦 升級指南

### 升級步驟

1. [步驟1]
2. [步驟2]

---

## 📚 文檔

- [用戶指南鏈接]
- [API文檔鏈接]

---

**發布團隊**：{owner}
**生成時間**：{today}
"""


def main():
    parser = argparse.ArgumentParser(description="Generate artifact documents")
    parser.add_argument("--feature", required=True, help="Feature name")
    parser.add_argument("--type", required=True, choices=ARTIFACT_TYPES, help="Artifact type")
    parser.add_argument("--milestone", help="Milestone (for milestone-report)")
    parser.add_argument("--version", help="Version (for release-notes)")
    parser.add_argument("--owner", default="Feature Owner", help="Feature owner name")
    parser.add_argument("--output", type=Path, help="Output file path")
    parser.add_argument("--base-path", type=Path, help="Base project path")
    parser.add_argument("--list-types", action="store_true", help="List available artifact types")
    
    args = parser.parse_args()
    
    if args.list_types:
        print("Available artifact types:")
        for t in ARTIFACT_TYPES:
            print(f"  - {t}")
        return 0
    
    # Determine base path
    if args.base_path:
        base_path = args.base_path
    else:
        base_path = Path(__file__).parent.parent.parent
    
    feature_dir = base_path / "docs" / "features" / args.feature
    
    try:
        # Generate artifact based on type
        if args.type == "milestone-report":
            if not args.milestone:
                print("❌ --milestone required for milestone-report", file=sys.stderr)
                return 1
            content = generate_milestone_report(args.feature, args.milestone, args.owner)
            default_output = feature_dir / "artifacts" / "reports" / f"{args.milestone}-report.md"
        
        elif args.type == "release-notes":
            if not args.version:
                print("❌ --version required for release-notes", file=sys.stderr)
                return 1
            content = generate_release_notes(args.feature, args.version, args.owner)
            default_output = feature_dir / "artifacts" / "releases" / f"RELEASE_NOTES_v{args.version}.md"
        
        else:
            print(f"⚠️  Artifact type '{args.type}' template not yet implemented")
            print(f"💡 Please use the manual templates in templates/feature-owner/")
            return 1
        
        # Determine output path
        output_path = args.output or default_output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write artifact
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Artifact generated: {output_path}")
        print(f"\n💡 Next step: Review and customize the generated artifact")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
