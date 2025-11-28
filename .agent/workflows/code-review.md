---
description: Code Review & Auto PR Workflow
---

# Code Review & Auto PR Workflow

這是一個自動化的 Code Review 工作流程，旨在協助 "Code Reviewer" Agent 執行靜態分析、產生 Review 註解並自動建立 Pull Request。

## 觸發時機
- 當 Feature Owner 完成功能開發並準備合併時。
- 當 Engineer 完成 Bug Fix 並需要審查時。
- 手動觸發：`/code-review`

## 步驟 (Steps)

### Phase 1: 靜態分析 (Static Analysis)
1. **執行 Lint 與 Type Check**
   - 目標：確保代碼符合規範且無類型錯誤。
   - 工具：`npm run lint`, `tsc --noEmit`
   - 腳本：`python scripts/code_review/run_analysis.py`
   - 產出：`reports/static_analysis_report.json`

### Phase 2: AI 代碼審查 (AI Code Review)
2. **生成 Review 註解**
   - 目標：分析代碼邏輯、安全性與最佳實踐。
   - 行動：Agent 讀取 `src/` 代碼與 `reports/static_analysis_report.json`。
   - 產出：Review Comments (Markdown 格式)。

### Phase 3: 建立 Pull Request (Create PR)
3. **生成 PR 描述與建立 PR**
   - 目標：將變更包裝為 PR，並附上測試報告與 Review 結果。
   - 腳本：`python scripts/code_review/pr_generator.py`
   - 輸入：
     - 來源分支 (Source Branch)
     - 目標分支 (Target Branch, default: main)
     - Review 摘要
   - 產出：GitHub Pull Request URL

## 自動化指令
- `// turbo`: 可用於自動執行 `run_analysis.py`。
