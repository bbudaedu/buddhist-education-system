# Project Context (專案上下文)

**最後更新**: 2025-12-06
**專案名稱**: Buddhist Education System (佛教教育系統)

## 1. 系統架構概覽
本系統由兩個主要部分組成：
1.  **Ebook Summary System (Python)**:
    - 負責網站監控、PDF 下載、AI 摘要生成 (Google Gemini)。
    - 自動化內容處理與通知分發。
    - **新增**: Email 通知服務 (`email_notification_service.py`)。
2.  **LINE Book Query Bot (Node.js/TypeScript)**:
    - 提供 LINE 介面供用戶查詢書籍、接收通知。
    - 整合 MySQL 資料庫儲存用戶與書籍資料。
    - **新增**: LIFF 學員中心、會員 API、Email 驗證。

## 2. 當前焦點功能: LIFF 學員中心 ✅
- **目標**: 建立 LIFF 會員中心，支援 Email 驗證與多管道通知設定。
- **當前階段**: **已完成並測試通過**

### 關鍵狀態
- **LIFF 學員中心**: ✅ 已完成。HTML/CSS/JS 前端 + Node.js API。
- **Email 驗證**: ✅ 已完成。SMTP 透過 Python 服務發送驗證碼。
- **LINE Bot 入口**: ✅ 已完成。「學員中心」指令觸發 Flex Message。
- **Cloudflare Tunnel**: ✅ 已設定。`liff.budaedu.dpdns.org` 穩定 HTTPS。

### 本次開發成果 (2025-12-06)
1.  **LIFF 學員中心** (`static/liff/member-center.*`):
    - 通知偏好設定、Email 驗證、興趣追蹤。
    - 佛陀教育基金會官方 Logo。
2.  **會員 API** (`src/routes/memberRoutes.ts`, `src/services/memberService.ts`):
    - /api/member/profile, /api/member/preferences
    - /api/member/send-verification, /api/member/verify-email
3.  **資料庫擴展** (`migrations/009_*.sql`, `migrations/010_*.sql`):
    - `user_subscriptions` 新增 Email 相關欄位。
    - `user_preferences` 用戶偏好追蹤表。
4.  **Email 通知服務** (`ebook/email_notification_service.py`):
    - 從 `config.json` 讀取 SMTP 設定。
    - 驗證碼發送與訂閱通知功能。

## 3. 專案結構地圖
- `.agent/`: Agent 協作相關 (記憶、工作流程、模板)
- `docs/`: 專案文檔
- `Line-bot-llm-mysql/src/`: Node.js 原始碼 (LINE Bot)
- `Line-bot-llm-mysql/static/liff/`: LIFF 學員中心前端
- `ebook/`: Python 原始碼 (Ebook System + Email 服務)

## 4. 關鍵依賴
- **外部 API**: `budaedu.org` (書籍、影音、直播、停課數據)
- **AI 模型**: Google Gemini Pro (摘要與查詢)
- **Messaging**: LINE Messaging API, LINE LIFF SDK
- **Email**: SMTP (config.json 設定)
- **Tunnel**: Cloudflare Tunnel (liff.budaedu.dpdns.org)

## 5. 團隊協作 (AI Agents)
- **Feature Owner**: 負責規劃與進度
- **Backend Engineer**: 負責 API 串接與 DB 變更
- **Frontend Engineer**: 負責 LIFF/Flex Message 設計
- **QA Engineer**: 負責測試與驗收

## 6. Git 分支管理
- **主分支**: `master`
- **待推送**: 學員中心功能 (2025-12-06)

