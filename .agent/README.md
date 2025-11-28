# .agent 目錄

此目錄包含專案的自動化工作流程定義。

## 目錄結構

```
.agent/
└── workflows/          # 工作流程定義文件
    ├── feature-owner-main.md           # Feature Owner主工作流程
    ├── task-planning.md                # 任務規劃工作流程
    ├── milestone-tracking.md           # 里程碑追蹤工作流程
    └── artifact-generation.md          # Artifact自動生成工作流程
```

## 工作流程說明

### Feature Owner 工作流程

專為功能負責人設計的完整功能開發生命週期管理工作流程套件。

#### 主要工作流程

1. **feature-owner-main** - 主工作流程
   - 完整的功能開發生命週期管理
   - 從PRD撰寫到交付驗收的全流程指引

2. **task-planning** - 任務規劃
   - 將PRD自動拆分為可執行的任務列表
   - 分階段規劃和資源分配

3. **milestone-tracking** - 里程碑追蹤
   - 管理功能開發進度
   - 生成狀態報告和風險預警

4. **artifact-generation** - Artifact生成
   - 在里程碑完成時自動生成文檔
   - 確保文檔更新與代碼同步

## 使用方式

工作流程文件遵循YAML frontmatter + markdown格式：

```markdown
---
description: 工作流程簡短描述
---

## 步驟說明

1. 第一步驟
2. 第二步驟
...
```

### 啟用自動執行 (Turbo Mode)

- 在步驟前加上 `// turbo` 可自動執行該步驟
- 在任意位置加上 `// turbo-all` 可自動執行所有步驟

詳細使用說明請參考：[docs/feature-owner/FEATURE_OWNER_GUIDE.md](../docs/feature-owner/FEATURE_OWNER_GUIDE.md)
