---
description: Feature Owner主工作流程 - 完整功能開發生命週期管理
---

# Feature Owner 主工作流程

此工作流程定義了Feature Owner如何管理一個新功能從概念到交付的完整生命週期。

## 角色職責

作為Feature Owner，您負責：
- 📝 撰寫和維護PRD（產品需求文檔）
- 📊 將功能拆分為可執行的任務並分配優先級
- 🎯 定義和追蹤里程碑
- 🤝 與架構師、工程師和其他團隊成員協作
- 📈 監控進度並管理風險
- 📚 確保文檔及時更新

## 完整流程

### 階段一：需求定義與規劃

#### 1. 初始化新功能

```bash
# 使用初始化工具創建功能目錄結構
python scripts/feature-owner/init_feature.py --name "功能名稱" --owner "您的名字"
```

這會創建：
- `docs/features/[feature-name]/PRD.md` - PRD文檔
- `docs/features/[feature-name]/TASKS.md` - 任務列表
- `docs/features/[feature-name]/MILESTONES.md` - 里程碑追蹤
- `docs/features/[feature-name]/ARTIFACTS/` - Artifact存放目錄

#### 2. 撰寫PRD

使用PRD模板撰寫詳細的產品需求文檔：

```bash
# 複製PRD模板
cp templates/feature-owner/PRD_TEMPLATE.md docs/features/[feature-name]/PRD.md
```

PRD必須包含：
- ✅ 功能背景與目標
- ✅ 目標用戶和使用場景
- ✅ 功能需求（功能性和非功能性）
- ✅ 驗收標準
- ✅ 範圍界定（包含/不包含）
- ✅ 依賴和風險

#### 3. PRD審查與批准

- 與產品經理確認業務需求
- 與架構師討論技術可行性
- 與團隊成員收集反饋
- 根據反饋更新PRD
- 獲得關鍵利益相關者批准

### 階段二：任務規劃

#### 4. 生成任務列表

使用任務規劃工作流程將PRD拆分為任務：

```bash
# 自動生成任務列表
python scripts/feature-owner/generate_tasks.py \
  --prd "docs/features/[feature-name]/PRD.md" \
  --output "docs/features/[feature-name]/TASKS.md"
```

或手動執行工作流程：`/task-planning`

任務列表應包含：
- 📋 任務描述和驗收標準
- 👤 負責人分配
- ⏱️ 預估工時
- 🔗 任務依賴關係
- 🏷️ 優先級標記

#### 5. 定義里程碑

根據任務列表定義階段性里程碑：

```bash
# 複製里程碑模板
cp templates/feature-owner/MILESTONE_TEMPLATE.md docs/features/[feature-name]/MILESTONES.md
```

建議的里程碑結構：
- **M0: 架構設計** - 技術方案確定
- **M1: 核心功能** - 基本功能可用
- **M2: 完整功能** - 所有功能實現
- **M3: 優化與測試** - 性能優化和全面測試
- **M4: 發布準備** - 文檔完整、可部署

#### 6. 架構審查會議

與架構師協作進行技術審查：

```bash
# 創建架構審查文檔
cp templates/feature-owner/ARCHITECTURE_REVIEW_TEMPLATE.md \
   docs/features/[feature-name]/ARCHITECTURE_REVIEW.md
```

審查要點：
- 系統架構和設計模式
- 技術棧選擇
- 數據模型設計
- API設計
- 性能和擴展性考量
- 安全性評估

### 階段三：執行與追蹤

#### 7. 啟動開發

創建實施檢查清單：

```bash
# 創建實施檢查清單
cp templates/feature-owner/IMPLEMENTATION_CHECKLIST_TEMPLATE.md \
   docs/features/[feature-name]/IMPLEMENTATION_CHECKLIST.md
```

#### 8. 每日/每週進度追蹤

```bash
# 更新里程碑進度
python scripts/feature-owner/track_milestone.py \
  --feature "[feature-name]" \
  --milestone "M1" \
  --update
```

或使用工作流程：`/milestone-tracking`

關鍵活動：
- 📅 每日站會同步進度
- 📊 更新任務狀態
- 🚨 識別和處理阻塞問題
- 📝 記錄重要決策和變更

#### 9. 里程碑驗收

每個里程碑完成時：

1. 驗證所有任務完成
2. 執行驗收測試
3. 生成里程碑Artifact

```bash
# 生成里程碑報告
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --milestone "M1" \
  --type "milestone-report"
```

4. 通知團隊和利益相關者
5. 召開里程碑回顧會議

### 階段四：測試與驗證

#### 10. 功能測試

- 單元測試覆蓋率 ≥ 80%
- 集成測試通過
- E2E測試通過
- 性能測試滿足要求
- 安全性測試通過

#### 11. 用戶驗收測試 (UAT)

- 根據PRD中的驗收標準進行測試
- 收集用戶反饋
- 修復缺陷和改進體驗

### 階段五：發布與交付

#### 12. 準備發布

創建發布說明：

```bash
# 生成發布說明
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --type "release-notes"
```

發布前檢查清單：
- ✅ 所有測試通過
- ✅ 文檔更新完整
- ✅ 發布說明準備就緒
- ✅ 回滾計劃準備完成
- ✅ 監控和告警配置完成

#### 13. 發布

根據專案的部署流程執行發布：
- 部署到測試環境驗證
- 部署到生產環境
- 監控系統運行狀態
- 確認功能正常工作

#### 14. 發布後活動

```bash
# 生成完整功能交付報告
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --type "delivery-report"
```

- 📊 監控關鍵指標
- 📝 記錄經驗教訓
- 🎉 慶祝團隊成就
- 📚 歸檔文檔和資料

## 協作指南

### 與架構師協作

- 在設計階段早期介入
- 使用架構審查模板記錄技術決策
- 定期同步技術方案變更

### 與工程師協作

- 清晰定義任務和驗收標準
- 及時回應技術疑問
- 提供必要的業務背景
- 尊重技術實施細節的專業判斷

### 與產品經理協作

- 確保PRD與產品願景一致
- 及時同步進度和風險
- 在需求變更時評估影響

### 與測試團隊協作

- 提供清晰的測試場景
- 協助編寫驗收測試用例
- 參與缺陷優先級評估

## 文檔管理

### 必須維護的文檔

1. **PRD** - 隨需求變更持續更新
2. **TASKS.md** - 每日更新狀態
3. **MILESTONES.md** - 每週更新進度
4. **IMPLEMENTATION_CHECKLIST.md** - 根據執行情況更新

### Artifact生成時機

- 每個里程碑完成時
- 重大技術決策後
- 發布前和發布後
- 專案結束時

## 最佳實踐

### ✅ 應該做的

- 儘早並頻繁地與團隊溝通
- 保持文檔即時更新
- 主動識別和管理風險
- 慶祝小勝利和里程碑達成
- 記錄決策理由和上下文

### ❌ 避免做的

- 不要等到最後才寫文檔
- 不要跳過里程碑驗收
- 不要忽視團隊的反饋
- 不要過度承諾交付時間
- 不要在沒有評估影響的情況下接受需求變更

## 相關資源

- [任務規劃工作流程](./task-planning.md)
- [里程碑追蹤工作流程](./milestone-tracking.md)
- [Artifact生成工作流程](./artifact-generation.md)
- [Feature Owner指南](../../docs/feature-owner/FEATURE_OWNER_GUIDE.md)
- [最佳實踐](../../docs/feature-owner/BEST_PRACTICES.md)
- [示例文檔](../../docs/feature-owner/EXAMPLES.md)

## 故障排除

### 常見問題

**Q: PRD寫得太詳細還是太簡略？**
A: PRD應該詳細到工程師能夠理解需求，但不需要包含實施細節。重點是"做什麼"而不是"怎麼做"。

**Q: 任務拆分的粒度如何把握？**
A: 單個任務應該在1-3天內完成。如果超過3天，考慮進一步拆分。

**Q: 如何處理需求變更？**
A: 評估變更影響 → 更新PRD → 調整任務列表 → 重新評估里程碑 → 通知團隊。

**Q: 里程碑延期怎麼辦？**
A: 分析原因 → 調整計劃 → 與利益相關者溝通 → 考慮調整範圍或資源。

---

**記住**：作為Feature Owner，您是功能成功的關鍵！保持主動溝通、及時更新文檔、有效管理風險，確保團隊朝著共同目標前進。
