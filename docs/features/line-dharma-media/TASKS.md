# LINE Dharma Media - 任務列表 (TASKS.md)

**Feature Owner**：Product Team  
**PRD版本**：v1.7 (2025-11-25)  
**狀態**：🟢 On Track  
**最後更新**：2025-11-28  

---

## 任務狀態圖例
- `[ ]` 待辦 (To Do)
- `[/]` 進行中 (In Progress)
- `[x]` 已完成 (Done)
- `[!]` 被阻塞 (Blocked)

---

## 總體進度概覽
**完成情況**：████████░░ 40% (15/38 任務)

---

## 里程碑 M0: API調查與架構確認 (已完成)
**目標**：確認所有外部數據源的可行性與規格。

### API 調查
- [x] **TASK-001**: 調查書籍/法寶 API 端點 (Backend Engineer)
  - *產出*: `artifacts/M0-API-Investigation-Report.md`
- [x] **TASK-002**: 調查影音/直播 API 端點 (Backend Engineer)
- [x] **TASK-003**: 建立 API 測試腳本 (Backend Engineer)
- [x] **TASK-004**: 確認圖片資源 (封面圖/講師照) 可用性 (Backend Engineer)

### 架構設計
- [x] **TASK-005**: 更新 PRD v1.7 技術規格 (Feature Owner)
- [x] **TASK-006**: 定義 M1 服務介面規格 (Backend Engineer)

---

## 里程碑 M1: 後端服務開發 (Backend Services)
**目標**：實作核心數據獲取服務，確保能正確從官網 API 取得並解析數據。

### 核心服務實作
- [x] **TASK-101**: 實作 `DharmaBookService` (Backend Engineer)
  - *需求*: 串接 `/dharma/public/api/books/chinese`
  - *功能*: 取得最新5本書籍，處理 `cover_url`
  - *完成日期*: 2025-11-26
- [x] **TASK-102**: 實作 `VideoStreamingService` (Backend Engineer)
  - *需求*: 串接 `/laravel/public/api/courses`
  - *功能*: 取得當日直播資訊，解析 HLS URL
  - *完成日期*: 2025-11-26
- [ ] **TASK-103**: 實作 `VideoSeriesService` (Backend Engineer)
  - *需求*: 串接 `/audiovisual/public/api/series/by-keyword-searched`
  - *功能*: 取得最新影音課程
- [ ] **TASK-104**: 實作 `BudaeduConnector` 統一介面 (Backend Engineer)
  - *需求*: 封裝上述三個服務，提供統一調用入口
  - *功能*: 實作快取機制 (Books: 5m, Videos: 10m, Live: 1m)

### 資料庫變更
- [ ] **TASK-105**: 更新 `subscribers` 表 Schema (Backend Engineer)
  - *需求*: 新增 `subscribed_videos` 欄位 (Boolean)
  - *產出*: Migration SQL script

### 協作與產出
- [ ] **TASK-106**: **M1 階段性驗收與 UX 腦力激盪** (All Agents)
  - *活動*: 檢視 API 回傳數據，討論如何優化 Flex Message 呈現
  - *產出*: `artifacts/M1-Completion-Report.md` (含 UX 建議)

---

## 里程碑 M2: LINE 介面整合 (Frontend/Interaction)
**目標**：將後端數據轉化為精美的 Flex Message，並處理用戶互動。

### Flex Message 設計與實作
- [x] **TASK-201**: 設計「最新法寶」Flex Carousel 模板 (Frontend Engineer)
  - *需求*: 顯示封面圖、標題、作者、下載按鈕(外部瀏覽器)
  - *完成日期*: 2025-11-26
- [x] **TASK-202**: 設計「最新影音」Flex Carousel 模板 (Frontend Engineer)
  - *需求*: 顯示講師照/縮圖、類型標籤、觀看按鈕
  - *完成日期*: 2025-11-26
- [x] **TASK-203**: 實作 Flex Message 生成邏輯 (Backend Engineer)
  - *需求*: 將 Service 數據填充至模板，處理缺圖 Fallback
  - *完成日期*: 2025-11-26

### 互動邏輯
- [x] **TASK-204**: 實作 Webhook 指令處理 (Backend Engineer)
  - *指令*: 「最新法寶」、「最新影音」
  - *完成日期*: 2025-11-26
- [x] **TASK-205**: 更新 Quick Reply 選單 (Frontend Engineer)
  - *需求*: 新增「訂閱最新影音」按鈕
  - *完成日期*: 2025-11-26
- [x] **TASK-206**: 實作訂閱影音通知路由邏輯 (Backend Engineer)
  - *需求*: 在 `webhookHandler.ts` 添加影音訂閱指令識別
  - *完成日期*: 2025-11-28
  - *實作內容*: 
    - 識別「訂閱影音通知」、「訂閱視訊」、「訂閱影片」等指令
    - 提供臨時回應訊息，防止指令被轉發到 LLM
    - 位置：`webhookHandler.ts:249-254`
- [ ] **TASK-206-B**: 實作完整訂閱/取消訂閱邏輯 (Backend Engineer)
  - *需求*: 實作 `videos` 訂閱類型到 `subscriptionService`
  - *狀態*: 待規劃

### 協作與產出
- [ ] **TASK-207**: **M2 階段性驗收與 UX 腦力激盪** (All Agents)
  - *活動*: 實際測試 LINE Bot 回應，優化卡片視覺與互動流暢度
  - *產出*: `artifacts/M2-UX-Optimization-Report.md`

---

## 里程碑 M3: 測試與優化 (Testing & Optimization)
**目標**：確保功能穩定、效能達標，並進行最終 UX 微調。

### 測試執行
- [ ] **TASK-301**: 單元測試 - Services (Backend Engineer)
- [ ] **TASK-302**: 整合測試 - Webhook to API (QA Engineer)
- [ ] **TASK-303**: 真機測試 - Android PDF 下載體驗 (QA Engineer)
  - *重點*: 驗證 `?openExternalBrowser=1` 是否生效

### 效能與優化
- [ ] **TASK-304**: 壓力測試與快取驗證 (QA Engineer)
  - *目標*: 回應時間 < 3秒
- [ ] **TASK-305**: 執行 M1/M2 提出的 UX 優化建議 (Frontend/Backend)

### 協作與產出
- [ ] **TASK-306**: **M3 階段性驗收與發布評審** (All Agents)
  - *活動*: 確認所有 Bug 修復，批准上線
  - *產出*: `artifacts/M3-Test-Summary.md`

---

## 里程碑 M4: 部署與發布 (Deployment)
**目標**：安全上線並通知用戶。

### 部署
- [ ] **TASK-401**: 資料庫 Migration (DevOps)
- [ ] **TASK-402**: 部署程式碼至生產環境 (DevOps)
- [ ] **TASK-403**: 線上功能驗證 (QA Engineer)

### 發布與監控
- [ ] **TASK-404**: 發布新功能公告 (Product Team)
- [ ] **TASK-405**: 設定監控儀表板 (DevOps)
  - *指標*: API 錯誤率、回應時間

### 協作與產出
- [ ] **TASK-406**: **專案結案會議** (All Agents)
  - *產出*: `artifacts/Project-Closure-Report.md`
