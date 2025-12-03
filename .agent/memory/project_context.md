# Project Context (專案上下文)

**最後更新**: 2025-12-03
**專案名稱**: Buddhist Education System (佛教教育系統)

## 1. 系統架構概覽
本系統由兩個主要部分組成：
1.  **Ebook Summary System (Python)**:
    - 負責網站監控、PDF 下載、AI 摘要生成 (Google Gemini)。
    - 自動化內容處理與通知分發。
2.  **LINE Book Query Bot (Node.js/TypeScript)**:
    - 提供 LINE 介面供用戶查詢書籍、接收通知。
    - 整合 MySQL 資料庫儲存用戶與書籍資料。

## 2. 當前焦點功能: LINE Dharma Media (最新法寶 & 最新影音)
- **目標**: 新增「最新法寶」與「最新影音」查詢功能，並支援訂閱。
- **文件位置**: `docs/features/line-dharma-media/`
- **PRD 版本**: v1.7 (已確認 API 規格)
- **當前階段**: **M4+ - 後續優化與修正**

### 關鍵狀態
- **M0 (API 調查)**: ✅ 已完成。確認了書籍、直播、影音的 API 端點。
- **M1 (後端開發)**: ✅ 已完成。已實作 `DharmaBookService` 和 `VideoStreamingService`。
- **M2 (介面整合)**: ✅ 已完成。Flex Message、Webhook 與 Quick Reply 已實作並通過測試。
- **M2 後續優化 (2025-11-28)**: ✅ 已完成。
  - 影音訂閱路由功能實作 (`webhookHandler.ts:249-254`)
  - 直播串流顯示優化（時間格式、講師稱謂、時間篩選）
- **M3 (測試優化)**: ✅ 已完成。E2E 測試執行完成，通過率 95.65%，所有 PRD 驗收標準通過。
- **M4 (部署發布)**: 🟢 準備就緒。已獲 QA 批准，可進入部署階段。
- **M4+ 後續優化 (2025-12-02 ~ 2025-12-03)**: ✅ 已完成。
  - 書籍分享功能（LINE 分享 API）
  - 直播 URL 修正（使用實際 `live_stream_url`）
  - 影片系列按鈕優化（簡介 + 最新一集 + 詳細資訊）
  - API 超時問題修正（統一使用 10 秒超時）


## 3. 專案結構地圖
- `.agent/`: Agent 協作相關 (記憶、工作流程、模板)
- `docs/`: 專案文檔
  - `features/`: 功能特性文檔 (Feature Owner 結構)
- `src/`: Node.js 原始碼 (LINE Bot)
- `ebook/`: Python 原始碼 (Ebook System)
- `scripts/`: 自動化腳本 (Feature Owner 工具)

## 4. 關鍵依賴
- **外部 API**: `budaedu.org` (書籍、影音、直播數據)
- **AI 模型**: Google Gemini Pro (摘要與查詢)
- **Messaging**: LINE Messaging API, LINE Notify

## 5. 團隊協作 (AI Agents)
- **Feature Owner**: 負責規劃與進度 (TASKS.md, MILESTONES.md)。
- **Backend Engineer**: 負責 API 串接與 DB 變更。
- **Frontend Engineer**: 負責 Flex Message 設計。
- **QA Engineer**: 負責測試與驗收。
- **DevOps**: 負責部署與監控。
