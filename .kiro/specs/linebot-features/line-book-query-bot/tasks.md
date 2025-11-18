# 實作任務清單

## 核心功能實作

- [x] 1. 建立專案結構和基礎配置

















  - 初始化 Node.js + TypeScript 專案
  - 安裝必要依賴：express, @line/bot-sdk, @google/generative-ai, mysql2, dotenv
  - 建立 src 目錄結構：config/, services/, handlers/, types/
  - 設定 TypeScript 編譯配置 (tsconfig.json)
  - 建立 .env.example 檔案範本
  - _需求: 7.1, 7.2_

- [x] 2. 實作配置管理模組





  - 建立 src/config/index.ts 載入環境變數
  - 定義 Config, LineConfig, GeminiConfig, DatabaseConfig 介面
  - 實作環境變數驗證邏輯，確保必要變數存在
  - 匯出配置物件供其他模組使用
  - _需求: 7.1, 7.2, 7.3_

- [x] 3. 實作資料庫服務





  - 建立 src/types/book.ts 定義 Book 介面
  - 建立 src/services/databaseService.ts
  - 實作 MySQL 連線池配置
  - 實作 searchBooks(query: string, limit: number) 方法，使用參數化查詢防止 SQL 注入
  - 實作 getBookById(bookId: number) 方法
  - 實作 closeConnection() 方法
  - _需求: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. 實作 Gemini AI 服務





  - 建立 src/services/geminiService.ts
  - 定義 searchBooksInDatabase Function Calling 工具規格
  - 設定 System Instruction 為友善的書庫助理
  - 實作 processUserQuery(userMessage: string) 方法
  - 實作 handleFunctionCall() 邏輯，當 Gemini 回傳 functionCall 時執行資料庫查詢
  - 實作將資料庫結果回傳給 Gemini 並生成最終自然語言回覆
  - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.2, 4.3, 4.4_

- [x] 5. 實作 LINE 訊息服務





  - 建立 src/services/lineMessagingService.ts
  - 初始化 LINE Bot SDK Client
  - 實作 replyMessage(replyToken: string, messages: Message[]) 方法
  - 實作 sendTextMessage() 用於簡單文字回覆
  - 實作訊息格式判斷邏輯：1-2 本書用文字，3+ 本書用 Carousel
  - 實作 sendCarouselMessage() 建立書籍卡片輪播
  - _需求: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 6. 實作 Webhook 處理器





  - 建立 src/handlers/webhookHandler.ts
  - 實作 handleWebhook(req, res) Express 路由處理器
  - 使用 LINE SDK middleware 驗證請求簽章
  - 實作 processMessage(event) 處理文字訊息事件
  - 整合 Gemini Service 處理用戶查詢
  - 整合 LINE Messaging Service 發送回覆
  - 確保在 3 秒內回應 LINE 平台 HTTP 200
  - _需求: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 7. 建立 Express 伺服器主程式





  - 建立 src/index.ts 作為應用程式入口
  - 設定 Express app 和 middleware (body-parser, cors)
  - 註冊 POST /webhook 路由
  - 實作基本的錯誤處理 middleware
  - 實作 GET /health 健康檢查端點
  - 啟動伺服器監聽指定 PORT
  - _需求: 1.1, 7.4_

- [x] 8. 實作基礎錯誤處理





  - 建立 src/handlers/errorHandler.ts
  - 定義 ErrorType 列舉和 ErrorContext 介面
  - 實作 handleError(error, context) 方法
  - 建立錯誤類型與友善訊息的對應表
  - 實作 logError() 記錄錯誤資訊（不包含敏感資料）
  - 在 Webhook Handler 中整合錯誤處理，當發生錯誤時回覆友善訊息給用戶
  - _需求: 6.1, 6.2, 6.3, 6.4, 6.5, 7.3_

- [x] 9. 建立部署配置





  - 建立 Dockerfile 用於容器化應用程式
  - 建立 .dockerignore 排除不必要的檔案
  - 建立 package.json scripts: start, build, dev
  - 撰寫 README.md 說明環境變數設定和部署步驟
  - _需求: 7.1, 7.4_

- [ ]* 10. 撰寫核心功能測試
  - 使用 Jest 建立測試環境
  - 撰寫 databaseService.test.ts 測試 SQL 查詢邏輯（使用 mock）
  - 撰寫 geminiService.test.ts 測試 Function Calling 解析
  - 撰寫 webhookHandler.test.ts 測試完整流程（使用 supertest）
  - _需求: 所有核心需求_

## 進階功能與優化（可選）

- [ ]* 11. 實作進階錯誤處理與重試機制
  - 在 Gemini Service 中實作指數退避重試（最多 2 次）
  - 在 Database Service 中實作固定間隔重試（最多 3 次）
  - 在 LINE Messaging Service 中實作重試機制
  - 實作超時控制：Gemini 10 秒、Database 5 秒、LINE 5 秒
  - _需求: 6.1, 6.2, 6.3_

- [ ]* 12. 實作查詢快取機制
  - 安裝 node-cache 或使用 Redis
  - 在 Gemini Service 中實作查詢結果快取（5 分鐘 TTL）
  - 相同查詢直接回傳快取結果，減少 API 呼叫
  - _需求: 效能優化_

- [ ]* 13. 實作速率限制
  - 安裝 express-rate-limit
  - 設定每個用戶每分鐘最多 10 次請求
  - 超過限制時回覆友善的提示訊息
  - _需求: 7.5, 安全性_

- [ ]* 14. 實作日誌與監控
  - 安裝 winston 或 pino 日誌套件
  - 設定日誌層級：ERROR, WARN, INFO, DEBUG
  - 記錄關鍵操作：用戶查詢、API 呼叫、錯誤發生
  - 整合 Google Cloud Logging 或 Sentry
  - _需求: 6.4, 6.5, 監控與日誌_

- [ ]* 15. 建立 LIFF 前端應用程式
  - 使用 Vite + React + TypeScript 初始化專案
  - 安裝 @line/liff SDK
  - 建立頁面：Home (使用指南)、BookDetail (書籍詳情)、About
  - 實作 LIFF 初始化和登入邏輯
  - 實作 API Service 呼叫後端取得書籍詳情
  - 建立 BookCard 組件顯示書籍資訊
  - 部署到 Vercel 或 Netlify
  - _需求: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 16. 實作整合測試與端對端測試
  - 建立整合測試：測試 Webhook → Gemini → Database → LINE 完整流程
  - 使用 nock 模擬外部 API 回應
  - 建立端對端測試場景：模擬用戶在 LINE 中查詢書籍
  - 使用 Playwright 測試 LIFF 頁面
  - _需求: 測試策略_

- [ ]* 17. 優化資料庫查詢效能
  - 在 books 資料表的 title 欄位建立索引（如果尚未建立）
  - 實作全文搜尋（FULLTEXT INDEX）提升搜尋準確度
  - 實作查詢結果分頁（如果未來需要）
  - _需求: 3.3, 效能優化_

- [ ]* 18. 建立 CI/CD 流程
  - 建立 GitHub Actions workflow 或 Cloud Build 配置
  - 自動執行測試
  - 自動建置 Docker image
  - 自動部署到 Google Cloud Run
  - _需求: 部署架構_
