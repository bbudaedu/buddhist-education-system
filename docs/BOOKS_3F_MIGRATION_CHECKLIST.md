# books_3f 資料庫遷移檢查清單

## ✅ 已完成的配置更新

### 1. 環境變數配置
- [x] `.env` 檔案中 `DB_NAME=books_3f` ✅
- [x] `.env.example` 檔案已更新為 `books_3f` ✅

### 2. 應用程式配置
- [x] `src/config/index.ts` 使用環境變數 `DB_NAME` ✅
- [x] `DatabaseService.ts` 使用統一配置 ✅
- [x] `SubscriptionService.ts` 使用統一配置 ✅

### 3. 測試工具
- [x] 建立 `test-books3f-connection.js` 連線測試腳本 ✅
- [x] 更新 `package.json` 加入 `test:db` 腳本 ✅
- [x] 更新手動測試指南 `MANUAL_TESTING_GUIDE.md` ✅

## ✅ 已完成的手動步驟

### 1. 資料庫連線測試 ✅
```bash
cd Line-bot-llm-mysql
npm run test:db
```

**實際結果：**
- ✅ 資料庫連線成功
- ✅ 確認當前資料庫為 `library_db`
- ✅ 檢查 `books_3f` 表存在且包含 1334 筆記錄
- ✅ 書籍搜尋功能正常運作

### 發現的重要資訊：
- 實際的資料庫名稱是 `library_db`，不是 `books_3f`
- 書籍資料存放在 `library_db.books_3f` 表中
- 用戶 `budaedu` 沒有建立新表的權限

### 2. 資料庫遷移狀態 ⚠️
```bash
cd Line-bot-llm-mysql
npm run migrate
```

**實際結果：**
- ❌ 用戶沒有 CREATE TABLE 權限
- ⚠️  無法建立通知系統相關表
- ✅ 建立了簡化版服務，暫時不使用通知功能

### 3. 驗證服務啟動 ✅
```bash
cd Line-bot-llm-mysql
npm run dev:simple
```

**實際結果：**
- ✅ 簡化版服務在 port 3001 啟動成功
- ✅ 資料庫連線池建立成功
- ✅ 無連線錯誤
- ✅ 所有基本功能正常運作

### 4. 測試基本功能 ✅
```bash
# 測試健康檢查端點
curl http://localhost:3001/health

# 測試書籍搜尋
curl "http://localhost:3001/api/books/search?q=佛"
```

**實際結果：**
- ✅ 健康檢查端點正常回應
- ✅ 書籍搜尋 API 正常運作
- ✅ 找到 10 筆包含「佛」的書籍記錄
- ✅ 資料格式正確，包含書名、作者、位置等資訊

## 🔍 驗證檢查項目

### 資料庫層面檢查
```sql
-- 連接到 MySQL 並執行以下查詢
USE books_3f;

-- 1. 檢查資料庫是否存在且可訪問
SELECT DATABASE() as current_database;

-- 2. 檢查 books 表
SHOW TABLES LIKE 'books';
SELECT COUNT(*) as book_count FROM books;

-- 3. 檢查通知系統表（遷移後）
SHOW TABLES LIKE 'user_subscriptions';
SHOW TABLES LIKE 'notification_logs';
SHOW TABLES LIKE 'delivery_failures';

-- 4. 測試書籍搜尋功能
SELECT book_id, title, library_branch 
FROM books 
WHERE title LIKE '%佛%' 
LIMIT 5;
```

### 應用程式層面檢查
- [ ] LINE Bot webhook 正常接收訊息
- [ ] 書籍查詢功能正常運作
- [ ] 訂閱管理功能正常運作
- [ ] 日誌輸出無資料庫錯誤

## 🚨 常見問題排除

### 問題 1: 資料庫連線失敗
**症狀：** `ECONNREFUSED` 或 `ER_ACCESS_DENIED_ERROR`

**解決方案：**
1. 檢查 MySQL 服務是否運行
2. 確認 `.env` 檔案中的連線資訊正確
3. 測試用戶權限：
```sql
-- 檢查用戶權限
SHOW GRANTS FOR 'budaedu'@'%';

-- 如果需要，授予權限
GRANT ALL PRIVILEGES ON books_3f.* TO 'budaedu'@'%';
FLUSH PRIVILEGES;
```

### 問題 2: books 表不存在
**症狀：** `Table 'books_3f.books' doesn't exist`

**解決方案：**
1. 確認 `books_3f` 資料庫中是否有 `books` 表
2. 如果沒有，可能需要從舊資料庫匯入：
```sql
-- 從舊資料庫匯出
mysqldump -u budaedu -p old_database_name books > books_backup.sql

-- 匯入到新資料庫
mysql -u budaedu -p books_3f < books_backup.sql
```

### 問題 3: 通知系統表不存在
**症狀：** 遷移相關的表不存在

**解決方案：**
```bash
# 重新執行遷移
cd Line-bot-llm-mysql
npm run migrate
```

## 📋 測試場景

### 基本功能測試
1. **資料庫連線測試**
   ```bash
   npm run test:db
   ```

2. **書籍搜尋測試**
   - 在 LINE 中發送書名查詢
   - 檢查是否返回正確結果

3. **訂閱功能測試**
   - 發送「訂閱新書」
   - 檢查資料庫中是否新增記錄
   - 發送「訂閱狀態」確認

### 整合測試
1. **完整通知流程測試**
   - 手動觸發每日處理
   - 檢查通知是否正確發送
   - 驗證資料庫記錄

2. **錯誤處理測試**
   - 故意造成資料庫連線中斷
   - 檢查應用程式是否正確處理錯誤
   - 驗證重連機制

## 🎯 完成標準

當以下所有項目都 ✅ 時，表示遷移成功：

- [ ] `npm run test:db` 執行成功
- [ ] `npm run dev` 啟動無錯誤
- [ ] LINE Bot 基本功能正常
- [ ] 書籍搜尋返回正確結果
- [ ] 訂閱管理功能正常
- [ ] 資料庫遷移表建立成功
- [ ] 日誌中無資料庫相關錯誤

## 📞 支援資訊

如果遇到問題，請檢查：
1. **日誌檔案** - 查看詳細錯誤訊息
2. **環境變數** - 確認所有必要變數都已設定
3. **網路連線** - 確認可以連接到資料庫主機
4. **權限設定** - 確認資料庫用戶有足夠權限

---

**最後更新：** 2025-10-31
**適用版本：** books_3f 資料庫遷移