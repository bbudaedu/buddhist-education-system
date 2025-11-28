---
description: Artifact自動生成工作流程 - 里程碑文檔自動化
---

# Artifact 自動生成工作流程

此工作流程確保在功能開發的關鍵節點自動生成必要的文檔和交付物（Artifacts），保持文檔與代碼同步。

## 什麼是 Artifact？

Artifact是功能開發過程中產出的重要文檔和交付物，包括：

- 📋 **技術文檔**：架構設計、API文檔、數據模型文檔
- 📊 **報告**：里程碑報告、進度報告、測試報告
- 📝 **決策記錄**：技術決策記錄（ADR）、變更日誌
- 🚀 **發布資料**：發布說明、部署指南、遷移指南
- 📚 **知識傳承**：經驗教訓、最佳實踐總結

## Artifact 生成時機

### 階段性Artifact

| 時機 | Artifact類型 | 目的 |
|------|-------------|------|
| M0完成 | 技術方案文檔、架構決策記錄 | 記錄設計決策和架構選擇 |
| 每個里程碑完成 | 里程碑報告、進度總結 | 記錄完成情況和經驗教訓 |
| 重大技術決策 | 技術決策記錄（ADR） | 記錄決策背景和理由 |
| 功能完成 | 發布說明、用戶指南 | 準備發布和用戶溝通 |
| 專案結束 | 完整交付報告、回顧總結 | 知識傳承和經驗總結 |

## 工作流程步驟

### 步驟 1：確定需要生成的Artifact

根據當前階段確定需要生成的文檔：

#### 里程碑完成時

```markdown
**必須生成**：
- [ ] 里程碑完成報告
- [ ] 功能演示材料
- [ ] 更新的技術文檔

**建議生成**：
- [ ] 測試報告
- [ ] 性能基準報告
- [ ] 經驗教訓記錄
```

#### 發布前

```markdown
**必須生成**：
- [ ] 發布說明（Release Notes）
- [ ] 部署指南
- [ ] 用戶文檔更新
- [ ] API變更文檔

**建議生成**：
- [ ] 遷移指南（如有破壞性變更）
- [ ] 故障排除指南
- [ ] 演示視頻或截圖
```

### 步驟 2：使用自動化工具生成Artifact

使用工具自動生成基礎文檔：

#### 生成里程碑報告

// turbo
```bash
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --milestone "M1" \
  --type "milestone-report" \
  --output "docs/features/[feature-name]/artifacts/M1-report.md"
```

工具會自動：
- 收集里程碑期間的所有任務
- 統計完成情況和關鍵指標
- 提取測試結果
- 匯總風險和問題
- 生成初始報告草稿

#### 生成發布說明

// turbo
```bash
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --type "release-notes" \
  --version "1.0.0" \
  --output "docs/features/[feature-name]/artifacts/RELEASE_NOTES_v1.0.0.md"
```

工具會自動：
- 從Git提交歷史提取變更
- 按類型分類（新功能、改進、修復）
- 識別破壞性變更
- 生成變更摘要

#### 生成技術決策記錄（ADR）

```bash
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --type "adr" \
  --decision-title "選擇使用PostgreSQL作為主數據庫" \
  --output "docs/features/[feature-name]/artifacts/adr/001-postgresql.md"
```

### 步驟 3：補充和完善自動生成的內容

自動生成的文檔是起點，需要人工補充：

#### 里程碑報告補充

```markdown
## [自動生成部分]
- ✅ 任務完成統計
- ✅ 關鍵指標
- ✅ 測試結果

## [需要手動補充]
- 💭 重要成就和亮點
- 💭 遇到的挑戰和解決方案
- 💭 對下階段的建議
- 💭 團隊協作的經驗
```

#### 發布說明補充

```markdown
## [自動生成部分]
- ✅ 功能變更清單
- ✅ Bug修復清單
- ✅ 技術變更

## [需要手動補充]
- 💭 重點功能的業務價值說明
- 💭 升級步驟和注意事項
- 💭 已知問題和限制
- 💭 未來計劃預告
```

### 步驟 4：審查和校對

確保Artifact質量：

#### 質量檢查清單

```markdown
### 內容完整性
- [ ] 所有必要章節都已包含
- [ ] 關鍵信息沒有遺漏
- [ ] 參考資料和鏈接完整

### 準確性
- [ ] 數據和指標準確
- [ ] 技術描述正確
- [ ] 時間線和日期正確

### 可讀性
- [ ] 語言清晰易懂
- [ ] 格式統一規範
- [ ] 圖表清晰有效
- [ ] 沒有拼寫和語法錯誤

### 目標受眾
- [ ] 內容符合讀者背景
- [ ] 技術深度適當
- [ ] 提供了必要的背景信息
```

### 步驟 5：分發和通知

將Artifact分享給相關人員：

#### 通知清單

```markdown
## 里程碑報告分發

**接收者**：
- ✉️ 開發團隊（必須）
- ✉️ 產品經理（必須）
- ✉️ 架構師（必須）
- ✉️ 測試團隊（建議）
- ✉️ 運維團隊（如涉及部署）

**通知方式**：
- Email摘要 + 文檔鏈接
- 團隊聊天頻道公告
- 專案管理工具更新

**通知內容應包含**：
- 里程碑名稱和日期
- 主要成就（3-5點）
- 需要關注的問題
- 下階段預告
- 文檔鏈接
```

### 步驟 6：歸檔和版本管理

組織和保存Artifact：

#### 目錄結構

```
docs/features/[feature-name]/
├── PRD.md
├── TASKS.md
├── MILESTONES.md
└── artifacts/
    ├── architecture/
    │   ├── system-design.md
    │   ├── data-model.md
    │   └── api-design.md
    ├── adr/
    │   ├── 001-database-choice.md
    │   ├── 002-authentication.md
    │   └── README.md
    ├── reports/
    │   ├── M0-design-review.md
    │   ├── M1-milestone-report.md
    │   ├── M2-milestone-report.md
    │   └── final-delivery-report.md
    ├── releases/
    │   ├── RELEASE_NOTES_v1.0.0.md
    │   ├── RELEASE_NOTES_v1.1.0.md
    │   └── MIGRATION_GUIDE.md
    └── lessons-learned/
        ├── technical-challenges.md
        └── process-improvements.md
```

#### 版本控制

確保所有Artifact納入版本控制：

```bash
# 添加新的Artifact
git add docs/features/[feature-name]/artifacts/

# 提交時使用清晰的消息
git commit -m "docs: Add M1 milestone report for [feature-name]"

# 標籤重要版本
git tag -a v1.0.0-docs -m "Documentation for v1.0.0 release"
```

## Artifact 模板和示例

### 1. 里程碑報告模板

```markdown
# [功能名稱] - [里程碑名稱] 完成報告

**日期**：2024-12-15
**里程碑**：M1 - 核心功能實現
**負責人**：張三

---

## 執行摘要

[2-3段簡要總結本里程碑的目標、完成情況和主要成就]

---

## 目標達成情況

### 原定目標
1. ✅ 實現核心業務邏輯
2. ✅ 完成基礎API
3. ⚠️ 前端基本頁面（90%完成）
4. ✅ 單元測試覆蓋率達80%

### 驗收標準檢查
- [x] 所有P0任務完成
- [x] API可以成功調用並返回正確結果
- [x] 單元測試通過率 100%
- [x] 代碼審查完成
- [/] 文檔完整性（待補充API範例）

---

## 關鍵指標

| 指標 | 目標 | 實際 | 狀態 |
|------|------|------|------|
| 任務完成率 | 100% | 95% | 🟡 |
| 測試覆蓋率 | ≥80% | 82% | 🟢 |
| 代碼審查通過率 | 100% | 100% | 🟢 |
| 缺陷修復率 | ≥90% | 95% | 🟢 |
| 文檔完整性 | 100% | 85% | 🟡 |

---

## 完成的主要工作

### 後端開發
- 實現用戶認證和授權系統
- 完成5個核心API端點
- 建立數據驗證和錯誤處理機制
- 集成第三方支付服務

### 前端開發
- 完成登錄和註冊頁面
- 實現用戶儀表板
- 建立組件庫基礎

### 測試
- 編寫67個單元測試用例
- 建立CI/CD測試流程
- 配置測試覆蓋率報告

---

## 遇到的挑戰與解決方案

### 🎯 挑戰1：第三方API整合延遲
**問題**：外部支付API文檔不完整，延遲開發3天

**解決方案**：
- 與外部團隊建立直接溝通渠道
- 先使用Mock API繼續開發
- 編寫適配層以便後續切換

**經驗**：早期識別外部依賴並建立應急方案

### 🎯 挑戰2：性能瓶頸
**問題**：某個查詢API響應時間超過2秒

**解決方案**：
- 添加數據庫索引
- 實現查詢結果緩存
- 優化SQL查詢邏輯

**經驗**：在開發階段就要關注性能

---

## 技術決策記錄

### 決策1：選擇Redis作為緩存
**背景**：需要提升API響應速度
**選項**：Redis vs Memcached
**決定**：使用Redis
**理由**：支持更豐富的數據結構，團隊有使用經驗
**文檔**：[ADR-003](./adr/003-redis-cache.md)

---

## 風險與問題

### 未解決的問題
1. **前端部署配置** (優先級: 高)
   - 需要DevOps協助配置CDN
   - 預計解決時間：本週五

2. **API文檔範例不完整** (優先級: 中)
   - 需要補充使用範例
   - 預計解決時間：下週二

### 新識別的風險
1. **測試環境穩定性**
   - 測試數據庫偶爾連接超時
   - 緩解措施：升級測試環境配置

---

## 團隊表現

### 🌟 突出貢獻
- 李四：快速解決了認證系統的安全問題
- 王五：建立了高效的測試框架
- 趙六：優秀的代碼審查反饋

### 團隊協作
- 每日站會效率高，問題解決及時
- 跨團隊溝通順暢
- 代碼審查文化良好

---

## 下階段計劃

### M2 目標
1. 完成所有前端頁面
2. 實現完整的業務流程
3. 集成測試覆蓋率達60%
4. 完成用戶文檔

### 準備工作
- 確認測試環境資源
- 安排UI/UX設計評審
- 準備演示環境

---

## 附錄

### 相關資源
- [測試報告](./test-report-M1.md)
- [API文檔](./api-docs-M1.md)
- [代碼倉庫](https://github.com/...)

### 指標詳細數據
[實際數據圖表或詳細表格]
```

### 2. 發布說明模板

使用模板：
```bash
cp templates/feature-owner/RELEASE_NOTES_TEMPLATE.md \
   docs/features/[feature-name]/artifacts/releases/RELEASE_NOTES_v1.0.0.md
```

### 3. 技術決策記錄（ADR）模板

```markdown
# ADR-001: [決策標題]

**狀態**：已接受 | 已拒絕 | 已棄用 | 已替代
**日期**：2024-12-15
**決策者**：張三、李四、架構師王五
**相關功能**：[功能名稱]

---

## 背景與問題

[描述需要做出決策的背景和要解決的問題]

**為什麼需要這個決策？**
- 原因1
- 原因2

**不做決策的後果？**
- 後果1
- 後果2

---

## 決策驅動因素

**必須滿足的要求**：
- 要求1
- 要求2

**希望滿足的要求**：
- 要求3
- 要求4

**約束條件**：
- 約束1（例如：預算、時間、技術棧）
- 約束2

---

## 考慮的方案

### 方案1：[方案名稱]

**描述**：[方案的簡要描述]

**優點**：
- ✅ 優點1
- ✅ 優點2

**缺點**：
- ❌ 缺點1
- ❌ 缺點2

**成本評估**：[開發成本、維護成本、學習成本]

### 方案2：[方案名稱]

[同上結構]

### 方案3：[方案名稱]

[同上結構]

---

## 決策結果

**選擇方案**：方案2 - [方案名稱]

**理由**：
1. 最符合長期技術戰略
2. 團隊有相關經驗，學習成本低
3. 社區支持活躍，生態系統完善
4. 性能和擴展性都能滿足需求

**權衡**：
- 接受的代價：[列出選擇此方案需要接受的代價]
- 緩解措施：[如何降低代價的影響]

---

## 實施計劃

**時間線**：
1. 第1週：技術調研和PoC
2. 第2-3週：核心實現
3. 第4週：測試和文檔

**所需資源**：
- 開發人員：2人
- 預計工時：80小時

**風險**：
- 風險1：[描述] → 緩解：[措施]
- 風險2：[描述] → 緩解：[措施]

---

## 後果

**正面影響**：
- 影響1
- 影響2

**負面影響**：
- 影響1（及緩解措施）
- 影響2（及緩解措施）

**需要注意的事項**：
- 注意事項1
- 注意事項2

---

## 參考資料

- [相關技術文檔](https://...)
- [競品分析](https://...)
- [團隊討論記錄](https://...)

---

## 變更歷史

| 日期 | 變更 | 變更人 |
|------|------|--------|
| 2024-12-15 | 創建初始版本 | 張三 |
```

## 自動化工具使用

### 可用命令

```bash
# 列出所有可生成的Artifact類型
python scripts/feature-owner/generate_artifact.py --list-types

# 生成里程碑報告
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --milestone "M1" \
  --type "milestone-report"

# 生成發布說明
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --type "release-notes" \
  --version "1.0.0"

# 生成完整交付報告
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --type "delivery-report"

# 生成ADR
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --type "adr" \
  --decision-title "選擇使用PostgreSQL"

# 生成測試報告
python scripts/feature-owner/generate_artifact.py \
  --feature "[feature-name]" \
  --type "test-report" \
  --milestone "M2"
```

## 最佳實踐

### ✅ 應該做的

1. **及時生成**：不要等到專案結束才寫文檔
2. **保持簡潔**：重點突出，避免冗長
3. **使用模板**：確保一致性和完整性
4. **包含上下文**：記錄"為什麼"而不僅僅是"是什麼"
5. **可視化**：使用圖表、截圖、圖示增強可讀性
6. **版本控制**：所有Artifact納入Git管理
7. **定期審查**：確保文檔保持更新

### ❌ 避免做的

1. **不要複製粘貼代碼**：鏈接到源碼而不是複製
2. **不要假設背景知識**：為未來的讀者提供足夠上下文
3. **不要忽視格式**：好的格式提升可讀性
4. **不要忘記受眾**：根據讀者調整技術深度
5. **不要孤立文檔**：在文檔間建立鏈接

## 檢查清單

Artifact生成完成後確認：

- ✅ 所有必要的Artifact都已生成
- ✅ 內容完整準確
- ✅ 格式統一規範
- ✅ 已經過審查和校對
- ✅ 已通知相關人員
- ✅ 已納入版本控制
- ✅ 文檔間鏈接正確
- ✅ 歸檔到正確位置

## 相關資源

- [Feature Owner主工作流程](./feature-owner-main.md)
- [所有模板](../../templates/feature-owner/)
- [示例文檔](../../docs/feature-owner/EXAMPLES.md)

---

**記住**：好的文檔是送給未來自己和團隊的禮物！
