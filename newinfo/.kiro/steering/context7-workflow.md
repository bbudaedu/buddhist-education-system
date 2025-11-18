# Context7 工作流程規則

## 任務開始前的 Context7 查詢

每當開始新的開發任務時，必須先執行以下步驟：

### 1. 識別相關技術棧
根據任務內容識別需要的技術：
- **LINE Bot 相關**: LINE Messaging API, @line/bot-sdk
- **AI 處理相關**: Google Gemini, @google/generative-ai
- **Web 框架**: Express.js, TypeScript
- **資料庫**: MySQL, mysql2
- **Python 相關**: Selenium, Tkinter, pypdf

### 2. 執行 Context7 查詢
使用 `mcp_Context7_resolve_library_id` 和 `mcp_Context7_get_library_docs` 工具：

```
1. 先解析 library ID: resolve_library_id(libraryName="相關技術名稱")
2. 獲取最新文件: get_library_docs(context7CompatibleLibraryID="解析到的ID", topic="相關主題")
```

### 3. 常用 Library ID 參考
- LINE Bot SDK: `/line/bot-sdk`
- Google Generative AI: `/google/generative-ai` 
- Express.js: `/expressjs/express`
- TypeScript: `/microsoft/typescript`
- MySQL: `/mysql/mysql`

### 4. 查詢主題建議
根據任務類型選擇適當的 topic 參數：
- **Webhook 處理**: "webhook", "middleware", "error-handling"
- **訊息回應**: "messaging", "templates", "carousel"
- **AI 整合**: "function-calling", "chat-completion", "system-instructions"
- **資料庫操作**: "connection", "queries", "transactions"

### 5. 整合最新範例
將 Context7 獲取的最新範例與現有 steering 規則結合：
- 更新 `linebot-examples.md` 中的程式碼範例
- 確保使用最新的 API 語法和最佳實踐
- 檢查是否有新的功能或改進的寫法

## 執行順序

每個新任務的標準流程：
1. **分析任務需求** - 確定涉及的技術棧
2. **Context7 查詢** - 獲取最新官方範例和文件
3. **更新 steering** - 將新資訊整合到相關 steering 檔案
4. **開始實作** - 使用最新範例作為參考基礎

## 自動化提醒

當遇到以下情況時，務必執行 Context7 查詢：
- 開始新的功能開發
- 遇到 API 相關錯誤
- 需要實作新的整合功能
- 更新現有程式碼到新版本

這確保我們始終使用最新、最正確的實作方式。