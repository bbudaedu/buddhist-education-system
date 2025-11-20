# 真實資料測試指令

## 新增指令：realdata

### 功能說明

`realdata` 指令會從資料庫取得真實的資料來測試 Flex Message 通知：
- 📚 最新 3 本書籍（從 books 資料表）
- 📰 最新 3 則新聞公告（從 bulletins 資料表）
- 🚫 最新 3 則停課通知（從 bulletins 資料表）

### 使用方式

在 LINE Bot 中輸入：
```
realdata
```

### 與測試指令的差異

| 指令 | 資料來源 | 用途 |
|------|----------|------|
| `flex1-4` | 預設測試資料 | 測試 UI 樣式和功能 |
| `realdata` | 資料庫真實資料 | 測試實際資料顯示效果 |

### 預期結果

#### 有資料時
顯示整合通知 Flex Carousel：
1. 第一張：綠色摘要卡片
   - 顯示實際的資料數量
2. 後續卡片：真實的內容
   - 真實的書名、作者
   - 真實的新聞標題、日期
   - 真實的停課資訊

#### 沒有資料時
顯示提示訊息：
```
⚠️ 目前資料庫中沒有足夠的真實資料

請先執行：
1. 新書爬蟲
2. 新聞爬蟲
3. 停課公告爬蟲

或使用 flex1-4 查看測試資料
```

## 準備真實資料

### 方法 1：執行爬蟲（推薦）

```bash
# 1. 執行新書爬蟲
cd ebook
python book_scraper.py

# 2. 執行新聞爬蟲
python run_news_scraper_correct.py

# 3. 執行停課公告爬蟲
python bulletin_scraper.py
```

### 方法 2：手動新增測試資料

使用 MySQL 客戶端新增資料：

```sql
-- 新增測試書籍
INSERT INTO books (title, author, pdf_url) VALUES
('測試書籍1', '測試作者1', 'https://www.budaedu.org/test1.pdf'),
('測試書籍2', '測試作者2', 'https://www.budaedu.org/test2.pdf'),
('測試書籍3', '測試作者3', 'https://www.budaedu.org/test3.pdf');

-- 新增測試新聞
INSERT INTO bulletins (title, content, date, url, type) VALUES
('測試新聞1', '測試內容1', CURDATE(), 'https://www.budaedu.org/news1', 'news'),
('測試新聞2', '測試內容2', CURDATE(), 'https://www.budaedu.org/news2', 'news'),
('測試新聞3', '測試內容3', CURDATE(), 'https://www.budaedu.org/news3', 'news');

-- 新增測試停課
INSERT INTO bulletins (course_name, cancellation_date, instructor_name, location, type) VALUES
('測試課程1', CURDATE(), '測試講師1', '測試地點1', 'cancellation'),
('測試課程2', CURDATE(), '測試講師2', '測試地點2', 'cancellation'),
('測試課程3', CURDATE(), '測試講師3', '測試地點3', 'cancellation');
```

## 測試流程

### 1. 確認有真實資料
```bash
# 檢查書籍數量
mysql -u root -p library_db -e "SELECT COUNT(*) FROM books;"

# 檢查新聞數量
mysql -u root -p library_db -e "SELECT COUNT(*) FROM bulletins WHERE type='news';"

# 檢查停課數量
mysql -u root -p library_db -e "SELECT COUNT(*) FROM bulletins WHERE type='cancellation';"
```

### 2. 重新編譯並啟動
```bash
cd Line-bot-llm-mysql
npm run build
npm start
```

### 3. 在 LINE 中測試
```
輸入：realdata
```

### 4. 驗證結果
- [ ] 顯示整合通知 Flex Carousel
- [ ] 摘要卡片顯示正確的數量
- [ ] 書籍資訊正確（真實的書名和作者）
- [ ] 新聞資訊正確（真實的標題和日期）
- [ ] 停課資訊正確（真實的課程和講師）
- [ ] PDF 連結可以點擊
- [ ] 在外部瀏覽器開啟

## 資料來源

### 新書資料
- **資料表**: `books`
- **欄位**: `title`, `author`, `pdf_url`
- **數量**: 最新 3 本

### 新聞資料
- **資料表**: `bulletins`
- **條件**: `type = 'news'`
- **欄位**: `title`, `date`, `url`, `content`
- **數量**: 最新 3 則

### 停課資料
- **資料表**: `bulletins`
- **條件**: `type = 'cancellation'`
- **欄位**: `course_name`, `cancellation_date`, `instructor_name`, `location`
- **數量**: 最新 3 則

## 疑難排解

### 問題：顯示「沒有足夠的真實資料」

**原因**：資料庫中沒有資料或資料不足

**解決方法**：
1. 執行爬蟲程式取得真實資料
2. 或手動新增測試資料到資料庫
3. 確認資料表結構正確

### 問題：顯示錯誤訊息

**原因**：資料庫連線或查詢錯誤

**解決方法**：
1. 檢查資料庫連線設定
2. 確認資料表已建立
3. 查看伺服器日誌的詳細錯誤訊息

### 問題：資料顯示不完整

**原因**：某些欄位為 NULL 或空值

**解決方法**：
1. 檢查資料庫中的資料完整性
2. 確認必要欄位有值
3. 更新不完整的資料

## 管理員指令總覽

| 指令 | 資料來源 | 說明 |
|------|----------|------|
| `flex1` | 測試資料 | 新書通知樣式測試 |
| `flex2` | 測試資料 | 新聞公告樣式測試 |
| `flex3` | 測試資料 | 停課通知樣式測試 |
| `flex4` | 測試資料 | 整合通知樣式測試 |
| `realdata` | 真實資料 | 使用資料庫真實資料測試 |

## 注意事項

1. **權限要求**
   - 只有管理員可以使用此指令
   - 非管理員輸入會被當作書籍查詢

2. **資料要求**
   - 至少需要一種類型的資料（新書、新聞或停課）
   - 建議每種類型至少有 3 筆資料

3. **推播額度**
   - 使用 Reply API，不消耗推播額度
   - 可以無限次測試

4. **資料更新**
   - 每次執行都會取得最新的資料
   - 反映資料庫的即時狀態

## 相關文檔

- `ADMIN_TEST_GUIDE.md` - 管理員測試系統完整指南
- `FLEX_NOTIFICATION_FEATURE.md` - Flex Message 功能說明
- `TEST_CHECKLIST.md` - 測試檢查清單

## 日期
2025-11-18
