# Templates 目錄

此目錄包含Feature Owner工作流程使用的標準化文檔模板。

## 目錄結構

```
templates/
└── feature-owner/
    ├── PRD_TEMPLATE.md                        # PRD模板
    ├── TASK_LIST_TEMPLATE.md                  # 任務列表模板
    ├── MILESTONE_TEMPLATE.md                  # 里程碑追蹤模板
    ├── ARCHITECTURE_REVIEW_TEMPLATE.md        # 架構審查模板
    ├── IMPLEMENTATION_CHECKLIST_TEMPLATE.md   # 實施檢查清單模板
    └── RELEASE_NOTES_TEMPLATE.md              # 發布說明模板
```

## 模板使用指南

### 如何使用模板

1. **複製模板到功能目錄**
   ```bash
   cp templates/feature-owner/PRD_TEMPLATE.md docs/features/[your-feature]/PRD.md
   ```

2. **填寫模板內容**
   - 保留章節結構
   - 填充實際內容
   - 刪除不適用的章節（標註為可選的）

3. **定期更新**
   - PRD：需求變更時更新
   - 任務列表：每日更新狀態
   - 里程碑：每週更新進度

### 模板說明

#### PRD_TEMPLATE.md
**目的**：標準化產品需求文檔格式
**使用時機**：功能規劃開始時
**維護頻率**：需求變更時更新

#### TASK_LIST_TEMPLATE.md  
**目的**：結構化任務管理
**使用時機**：PRD確定後
**維護頻率**：每日更新

#### MILESTONE_TEMPLATE.md
**目的**：追蹤階段性目標
**使用時機**：任務規劃完成後
**維護頻率**：每週更新

#### ARCHITECTURE_REVIEW_TEMPLATE.md
**目的**：記錄技術審查
**使用時機**：設計階段
**維護頻率**：重大技術決策時更新

#### IMPLEMENTATION_CHECKLIST_TEMPLATE.md
**目的**：確保開發過程完整性
**使用時機**：開發開始前
**維護頻率**：根據執行進度更新

#### RELEASE_NOTES_TEMPLATE.md
**目的**：標準化發布說明
**使用時機**：準備發布時
**維護頻率**：每個版本發布前

## 自定義模板

如果項目有特殊需求，可以：

1. 複製現有模板
2. 根據需要修改
3. 保存為項目特定模板
4. 更新此README記錄自定義模板

## 相關資源

- [Feature Owner主工作流程](../.agent/workflows/feature-owner-main.md)
- [使用示例](../docs/feature-owner/EXAMPLES.md)
- [最佳實踐](../docs/feature-owner/BEST_PRACTICES.md)

## 貢獻

如果發現模板可以改進：

1. 提出改進建議
2. 說明改進理由
3. 提供示例（如適用）
4. 討論並達成共識後更新

---

**提示**：好的模板可以節省時間並提高一致性，但不要讓模板成為負擔。根據實際需求靈活調整！
