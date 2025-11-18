# Excel 新書簡介資料同步寫入資料庫功能指南

## 概述

本功能實現了將 Python ebook 系統生成的 Excel 新書簡介資料自動同步到 LINE Bot 的 MySQL 資料庫中，讓兩個系統能夠無縫整合，實現資料共享。

## 系統架構

```
Python Ebook System          LINE Bot System
┌─────────────────────┐      ┌─────────────────────┐
│ book_scraper.py     │      │ DatabaseService.ts  │
│ gemini_processor.py │      │ NewBookService.ts   │
│ document_generator.py│ ──→  │ BookSyncService.ts  │
│ database_sync.py    │      │ ExcelReaderService.ts│
└─────────────────────┘      └─────────────────────┘
         │                            │
         ▼                            ▼
┌─────────────────────┐      ┌─────────────────────┐
│ Excel Files         │      │ MySQL Database      │
│ 新書詳細資料_*.xlsx  │      │ new_books table     │
└─────────────────────┘      └─────────────────────┘
```

## 功能特點

### 1. 自動同步
- Excel 檔案生成後自動觸發同步
- 支援批量處理多個檔案
- 重複資料自動更新（upsert）

### 2. 資料驗證
- Excel 格式驗證
- 必要欄位檢查
- 重複書號檢測

### 3. 錯誤處理
- 完整的錯誤日誌記錄
- 失敗重試機制
- 部分失敗不影響其他資料

### 4. 監控功能
- 同步狀態查詢
- 統計資料報告
- 目錄監控模式

## 安裝與設定

### 1. 安裝依賴套件

在 LINE Bot 專案目錄下執行：

```bash
cd Line-bot-llm-mysql
npm install
```

新增的套件包括：
- `xlsx`: Excel 檔案處理
- `commander`: 命令行工具

### 2. 資料庫遷移

執行資料庫遷移來創建新書資料表：

```bash
npm run migrate
```

這會創建 `new_books` 資料表，包含以下欄位：
- `book_code`: 書號（主鍵）
- `title`: 書名
- `author`: 作者
- `pdf_filename`: PDF檔名
- `file_size_mb`: 檔案大小
- `processing_method`: 處理方式
- `summary`: 摘要
- `download_url`: 下載連結
- `processing_timestamp`: 處理時間
- `is_notified`: 是否已通知

### 3. Python 端設定

在 Python ebook 系統中，`database_sync.py` 模組會自動載入並在 Excel 生成後觸發同步。

## 使用方法

### 1. 命令行同步

#### 同步單個檔案
```bash
npm run sync:file -- "path/to/excel/file.xlsx"
```

#### 同步整個目錄
```bash
npm run sync:directory -- "path/to/excel/directory"
```

#### 監控目錄（自動同步新檔案）
```bash
npm run sync:monitor -- "path/to/excel/directory"
```

#### 查看同步統計
```bash
npm run sync:stats
```

### 2. Python 端自動同步

當 `document_generator.py` 生成 Excel 檔案後，會自動觸發同步：

```python
from database_sync import database_sync_manager

# 手動觸發同步
result = database_sync_manager.sync_excel_file("path/to/excel/file.xlsx")

# 同步最新檔案
results = database_sync_manager.sync_latest_excel_files(max_files=5)

# 查看同步狀態
status = database_sync_manager.get_sync_status()
```

### 3. 程式化使用

在 TypeScript/Node.js 中：

```typescript
import { BookSyncService } from './src/services/BookSyncService';
import { NewBookService } from './src/services/NewBookService';

const syncService = new BookSyncService();
const newBookService = new NewBookService();

// 同步檔案
const result = await syncService.syncExcelFileToDatabase('file.xlsx');

// 查詢新書
const books = await newBookService.searchNewBooks('佛教');

// 取得統計
const stats = await newBookService.getNewBooksStats();
```

## Excel 檔案格式

Excel 檔案必須包含以下欄位（標題行）：

| 欄位名稱 | 必要 | 說明 |
|---------|------|------|
| 書號 | ✓ | 書籍唯一識別碼 |
| 書名 | ✓ | 書籍標題 |
| 作者 | | 作者姓名 |
| PDF檔名 | | PDF 檔案名稱 |
| 檔案大小(MB) | | 檔案大小 |
| 處理方式 | | PDF提取/Google搜尋 |
| 摘要 | | 書籍摘要內容 |
| 下載連結 | | PDF 下載網址 |
| 處理時間 | | 處理時間戳記 |

## API 介面

### NewBookService 主要方法

```typescript
// 插入或更新新書
await newBookService.upsertNewBook(bookData);

// 批量處理
await newBookService.batchUpsertNewBooks(booksArray);

// 搜尋新書
await newBookService.searchNewBooks(query, limit);

// 取得未通知的新書
await newBookService.getUnnotifiedNewBooks(limit);

// 標記為已通知
await newBookService.markBooksAsNotified(bookCodes);

// 取得統計資料
await newBookService.getNewBooksStats();
```

### BookSyncService 主要方法

```typescript
// 同步單個檔案
await syncService.syncExcelFileToDatabase(filePath);

// 同步目錄
await syncService.syncDirectoryToDatabase(dirPath, pattern);

// 開始監控
await syncService.startDirectoryMonitoring(dirPath, interval);

// 取得同步統計
await syncService.getSyncStats();
```

## 測試

### 執行整合測試

```bash
node test-sync-integration.js
```

測試包括：
1. 資料庫連線測試
2. 遷移執行測試
3. Excel 檔案創建測試
4. 同步功能測試
5. 資料驗證測試
6. 查詢功能測試
7. 清理測試資料

### 手動測試步驟

1. 確保資料庫服務運行
2. 執行遷移：`npm run migrate`
3. 生成測試 Excel 檔案
4. 執行同步：`npm run sync:file -- "test.xlsx"`
5. 查看資料庫資料
6. 測試查詢功能

## 監控與維護

### 日誌記錄

所有同步操作都會記錄詳細日誌：
- 成功/失敗狀態
- 處理時間
- 錯誤訊息
- 統計資料

### 效能監控

- 同步處理時間
- 資料庫連線狀態
- 檔案處理統計
- 錯誤率監控

### 定期維護

建議定期執行：
```bash
# 查看同步統計
npm run sync:stats

# 清理舊資料（如需要）
# 可以在 BookSyncService 中實現清理邏輯
```

## 故障排除

### 常見問題

1. **資料庫連線失敗**
   - 檢查資料庫服務是否運行
   - 確認連線參數正確
   - 檢查防火牆設定

2. **Excel 檔案讀取失敗**
   - 確認檔案路徑正確
   - 檢查檔案權限
   - 驗證 Excel 格式

3. **同步部分失敗**
   - 查看詳細錯誤日誌
   - 檢查資料格式
   - 確認必要欄位完整

4. **重複資料問題**
   - 系統使用 upsert 機制自動處理
   - 以書號作為唯一鍵

### 除錯模式

啟用詳細日誌：
```bash
npm run sync:file -- --verbose "file.xlsx"
```

## 擴展功能

### 未來可能的擴展

1. **即時同步**
   - 檔案系統監控
   - WebSocket 通知

2. **增量同步**
   - 只同步變更的資料
   - 時間戳記比較

3. **多格式支援**
   - CSV 檔案支援
   - JSON 格式支援

4. **API 端點**
   - REST API 介面
   - 遠端同步觸發

## 安全考量

1. **資料驗證**
   - 輸入資料清理
   - SQL 注入防護

2. **存取控制**
   - 檔案權限檢查
   - 資料庫權限管理

3. **錯誤處理**
   - 敏感資訊過濾
   - 安全的錯誤訊息

## 結論

Excel 新書簡介資料同步功能提供了 Python ebook 系統與 LINE Bot 系統之間的無縫資料整合。透過自動化的同步機制，確保兩個系統的資料保持一致，提升整體系統的效率和可靠性。

如有任何問題或需要協助，請參考相關日誌檔案或聯繫系統管理員。