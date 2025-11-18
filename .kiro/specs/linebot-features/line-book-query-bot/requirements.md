# 需求文檔

## 簡介

本系統是一個整合 LINE Messaging API 與 Google Gemini 2.5 Pro 的智能書庫查詢機器人。用戶可以在 LINE 聊天室中使用自然語言提問，系統會透過 Gemini 的 Function Calling 功能理解用戶意圖，查詢 MySQL 書庫資料庫，並以友善的方式回覆查詢結果。

## 術語表

- **LINE Bot**: 在 LINE 平台上運行的聊天機器人應用程式
- **Webhook Server**: 接收 LINE 平台事件通知的後端伺服器
- **Gemini API**: Google 提供的生成式 AI 模型 API
- **Function Calling**: Gemini 模型將自然語言轉換為結構化函式呼叫的能力
- **Book Database**: 儲存書籍資訊的 MySQL 資料庫
- **LIFF App**: LINE Front-end Framework，在 LINE 中運行的網頁應用程式

## 需求

### 需求 1：用戶訊息接收與驗證

**用戶故事：** 作為系統管理員，我希望系統能安全地接收來自 LINE 平台的用戶訊息，以確保只處理合法的請求

#### 驗證標準

1. WHEN LINE 平台發送 Webhook 事件，THE Webhook Server SHALL 接收 HTTP POST 請求
2. WHEN Webhook Server 收到請求，THE Webhook Server SHALL 使用 Channel Secret 驗證請求簽章
3. IF 簽章驗證失敗，THEN THE Webhook Server SHALL 拒絕請求並回傳 HTTP 401 狀態碼
4. WHEN 簽章驗證成功，THE Webhook Server SHALL 解析訊息內容並提取用戶文字訊息
5. THE Webhook Server SHALL 在 3 秒內回應 LINE 平台 HTTP 200 狀態碼

### 需求 2：自然語言查詢理解

**用戶故事：** 作為用戶，我希望能用自然語言詢問書籍資訊，而不需要記住特定的查詢語法

#### 驗證標準

1. WHEN Webhook Server 接收到用戶文字訊息，THE Webhook Server SHALL 將訊息傳送給 Gemini 2.5 Pro 模型
2. THE Webhook Server SHALL 提供 searchBooksInDatabase 函式定義給 Gemini 模型
3. WHEN Gemini 模型判斷需要查詢書籍，THE Gemini API SHALL 回傳 functionCall 物件，包含函式名稱和查詢參數
4. THE Gemini API SHALL 在 10 秒內回應函式呼叫結果
5. IF Gemini 模型無法理解用戶意圖，THEN THE Gemini API SHALL 回傳澄清問題的文字回應

### 需求 3：書庫資料庫查詢

**用戶故事：** 作為用戶，我希望系統能從書庫資料庫中找到與我查詢相關的書籍

#### 驗證標準

1. WHEN Webhook Server 收到 Gemini 的 functionCall 請求，THE Webhook Server SHALL 執行對應的資料庫查詢函式
2. THE Webhook Server SHALL 連接到 MySQL Book Database 並執行 SQL 查詢
3. THE Webhook Server SHALL 使用 LIKE 或全文搜尋語法匹配書名、作者或關鍵字
4. THE Webhook Server SHALL 限制查詢結果最多回傳 10 筆記錄
5. WHEN 資料庫查詢完成，THE Webhook Server SHALL 將結果格式化為 JSON 字串並回傳給 Gemini 模型

### 需求 4：查詢結果回覆

**用戶故事：** 作為用戶，我希望收到清晰易讀的書籍查詢結果，而不是原始的資料格式

#### 驗證標準

1. WHEN Gemini 模型收到資料庫查詢結果，THE Gemini API SHALL 將結構化資料轉換為自然語言回覆
2. THE Gemini API SHALL 根據 systemInstruction 以友善的書庫助理口吻回應
3. WHEN 查詢結果包含多本書籍，THE Gemini API SHALL 列出書名、作者等關鍵資訊
4. WHEN 查詢無結果，THE Gemini API SHALL 回覆表示未找到相關書籍的訊息
5. THE Webhook Server SHALL 使用 LINE Messaging API 將 Gemini 的回覆傳送給用戶

### 需求 5：LINE 訊息發送

**用戶故事：** 作為用戶，我希望在 LINE 聊天室中快速收到機器人的回覆

#### 驗證標準

1. WHEN Webhook Server 準備好回覆內容，THE Webhook Server SHALL 使用 LINE Messaging API Reply Message 端點
2. THE Webhook Server SHALL 使用 Channel Access Token 進行 API 認證
3. THE Webhook Server SHALL 在收到用戶訊息後 30 秒內發送回覆
4. WHERE 查詢結果適合使用豐富訊息格式，THE Webhook Server SHALL 使用 Carousel Template 或 Button Template
5. IF LINE API 呼叫失敗，THEN THE Webhook Server SHALL 記錄錯誤並嘗試發送簡化的文字訊息

### 需求 6：錯誤處理與日誌

**用戶故事：** 作為系統管理員，我希望系統能妥善處理錯誤情況，並提供足夠的日誌資訊以便除錯

#### 驗證標準

1. WHEN 任何 API 呼叫失敗，THE Webhook Server SHALL 捕捉錯誤並記錄詳細資訊
2. IF Gemini API 呼叫超時或失敗，THEN THE Webhook Server SHALL 回覆用戶「系統暫時無法處理您的請求，請稍後再試」
3. IF Book Database 連線失敗，THEN THE Webhook Server SHALL 回覆用戶「書庫系統維護中，請稍後再試」
4. THE Webhook Server SHALL 記錄每次用戶查詢、Gemini 回應和資料庫查詢的日誌
5. THE Webhook Server SHALL 在發生錯誤時記錄完整的錯誤堆疊資訊

### 需求 7：環境配置與安全性

**用戶故事：** 作為系統管理員，我希望敏感資訊被安全地管理，不會暴露在程式碼或前端

#### 驗證標準

1. THE Webhook Server SHALL 從環境變數讀取 LINE Channel Secret、Channel Access Token 和 Gemini API Key
2. THE Webhook Server SHALL 從環境變數讀取 MySQL 連線資訊（主機、埠號、使用者名稱、密碼、資料庫名稱）
3. THE Webhook Server SHALL 確保所有敏感資訊不會出現在日誌輸出中
4. THE Webhook Server SHALL 使用 HTTPS 協定接收 Webhook 請求
5. THE Webhook Server SHALL 在回應中設定適當的 CORS 標頭，僅允許 LINE 平台存取

### 需求 8：LIFF 應用程式（可選）

**用戶故事：** 作為用戶，我希望能透過網頁介面查看更詳細的書籍資訊或使用指南

#### 驗證標準

1. WHERE LIFF App 功能啟用，THE LIFF App SHALL 在 LINE 應用程式內載入
2. WHEN LIFF App 初始化，THE LIFF App SHALL 使用 LIFF SDK 取得用戶的 LINE ID
3. WHERE 用戶點擊書籍詳情連結，THE LIFF App SHALL 顯示完整的書籍資訊頁面
4. THE LIFF App SHALL 提供使用指南頁面，說明如何與 LINE Bot 互動
5. THE LIFF App SHALL 確保所有 API 呼叫都透過後端伺服器，不直接暴露 API 金鑰
