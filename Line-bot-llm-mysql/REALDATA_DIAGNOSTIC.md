# realdata 指令診斷指南

## 最新修復

### 修復內容
1. ✅ 過濾空資料（沒有標題或必要欄位的資料）
2. ✅ 限制 Carousel bubble 總數（最多 10 個）
3. ✅ 清理空陣列
4. ✅ 添加詳細日誌

### 重新編譯
```bash
cd Line-bot-llm-mysql
npm run build  # ✅ 編譯成功
```

## 測試步驟

### 1. 重啟伺服器
```bash
npm start
```

### 2. 在 LINE 中測試
```
輸入：realdata
```

### 3. 查看伺服器日誌

應該看到以下日誌：
```
Processing message from user: realdata
Fetching real data for test...
從 API 抓取停課公告...
成功抓取 X 則停課公告
從 API 抓取最新消息...
成功抓取 X 則最新消息
Creating integrated notification with data:
- Books: X
- News: X
- Cancellations: X
Message size: XXXX bytes
Total bubbles: X
✅ Sent real data test notification successfully
```

## 可能的錯誤情況

### 錯誤 1：400 Bad Request

**原因：**
- Flex Message JSON 結構無效
- 有空的必要欄位（如 text 為空字串）
- Bubble 數量超過 10 個

**診斷：**
查看日誌中的 `Total bubbles` 數量和 `Message size`

**解決：**
- 確保所有資料都經過過濾
- 限制每種類型的數量
- 檢查 JSON 結構

### 錯誤 2：沒有資料

**原因：**
- 資料庫中沒有資料
- 資料不完整被過濾掉

**診斷：**
查看日誌中的資料數量：
```
- Books: 0
- News: 0
- Cancellations: 0
```

**解決：**
執行爬蟲程式取得資料

### 錯誤 3：ReplyToken 已使用

**原因：**
- 同一個 replyToken 被使用兩次
- 錯誤處理中又嘗試發送訊息

**診斷：**
查看日誌中是否有重複的 reply 嘗試

**解決：**
- 確保錯誤處理不會重複使用 replyToken
- 使用 push message 代替 reply

## 資料完整性檢查

### 檢查書籍資料
```sql
SELECT book_id, title, author 
FROM books 
WHERE title IS NOT NULL AND title != ''
LIMIT 5;
```

### 檢查新聞資料
```sql
SELECT id, title, publication_date, url 
FROM bulletins 
WHERE type = 'news' 
AND title IS NOT NULL AND title != ''
LIMIT 5;
```

### 檢查停課資料
```sql
SELECT id, course_name, cancellation_date, instructor_name, location
FROM bulletins 
WHERE type = 'cancellation'
AND course_name IS NOT NULL AND course_name != ''
AND cancellation_date IS NOT NULL AND cancellation_date != ''
LIMIT 5;
```

## Flex Message 限制

### LINE 官方限制
- **最多 10 個 bubbles** 在一個 Carousel 中
- **最多 5 個 actions** 在一個 bubble 中
- **訊息大小限制**：建議不超過 50KB

### 我們的限制
- 摘要：1 個 bubble
- 新書：最多 3 個 bubbles
- 新聞：最多 3 個 bubbles
- 停課：最多 3 個 bubbles
- **總計：最多 10 個 bubbles**

## 當前狀態

### 已修復
- ✅ 過濾空資料
- ✅ 限制 bubble 數量
- ✅ 添加詳細日誌
- ✅ 編譯成功

### 待測試
- [ ] 重啟伺服器
- [ ] 測試 `realdata` 指令
- [ ] 驗證顯示正常

## 下一步

1. **重啟伺服器**
   ```bash
   npm start
   ```

2. **測試指令**
   ```
   在 LINE 中輸入：realdata
   ```

3. **查看日誌**
   - 檢查資料數量
   - 檢查 bubble 總數
   - 檢查是否有錯誤

4. **如果成功**
   - 驗證顯示效果
   - 檢查資料正確性
   - 測試按鈕功能

5. **如果失敗**
   - 複製完整的錯誤日誌
   - 檢查 JSON 結構
   - 使用 `flex4` 對比測試

## 備用方案

如果 `realdata` 仍然有問題，可以使用 `flex4` 測試預設資料，功能是一樣的，只是資料來源不同。

## 日期
2025-11-18
