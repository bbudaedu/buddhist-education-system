# 每日書籍通知系統 - 手動驗收測試指南

## 測試環境準備

### 1. 系統環境檢查
```bash
# 檢查 Node.js 版本
node --version  # 應該 >= 18.0.0

# 檢查 Python 版本
python --version  # 應該 >= 3.8

# 檢查 MySQL 連線
mysql -u root -p -e "SELECT VERSION();"
```

### 2. 服務啟動檢查
```bash
# 啟動 LINE Bot 服務
cd Line-bot-llm-mysql
npm run dev

# 檢查服務健康狀態
curl http://localhost:3000/health
```

### 3. 測試資料準備
- 準備測試用的 LINE 用戶 ID
- 確保 `books_3f` 資料庫中有測試資料
- 準備測試用的書籍資料檔案
- 確認資料庫連線設定正確指向 `books_3f`

## 核心功能測試

### A. 訂閱管理功能測試

#### A1. 用戶訂閱流程
**測試步驟：**
1. 在 LINE 中發送訊息：`訂閱新書`
2. 檢查是否收到訂閱確認訊息
3. 驗證資料庫中是否正確記錄訂閱狀態

**預期結果：**
- 收到友善的訂閱確認訊息
- 資料庫 `user_subscriptions` 表中新增記錄
- `is_subscribed` 欄位為 `true`

**驗證 SQL：**
```sql
-- 連接到 books_3f 資料庫
USE books_3f;
SELECT * FROM user_subscriptions WHERE line_user_id = 'YOUR_TEST_USER_ID';
```

#### A2. 訂閱狀態查詢
**測試步驟：**
1. 發送訊息：`訂閱狀態`
2. 檢查回應訊息內容

**預期結果：**
- 顯示目前訂閱狀態
- 包含訂閱日期資訊
- 提供相關操作選項

#### A3. 取消訂閱流程
**測試步驟：**
1. 發送訊息：`取消訂閱`
2. 檢查確認訊息
3. 驗證資料庫狀態更新

**預期結果：**
- 收到取消訂閱確認
- 資料庫中 `is_subscribed` 更新為 `false`
- 保留歷史訂閱記錄

### B. 通知訊息功能測試

#### B1. 單本書籍通知格式
**測試步驟：**
1. 準備測試書籍資料檔案：
```json
{
  "processingDate": "2025-10-31",
  "totalBooksFound": 1,
  "successfullyProcessed": [
    {
      "title": "測試書籍標題",
      "author": "測試作者",
      "summary": "這是一本測試書籍的摘要內容...",
      "downloadUrl": "https://example.com/test-book.pdf",
      "processingMethod": "pdf_extract",
      "processingSuccess": true
    }
  ],
  "processingStats": {
    "booksProcessed": 1,
    "booksFailed": 0,
    "pdfExtractions": 1,
    "googleSearches": 0
  }
}
```

2. 手動觸發通知處理
3. 檢查收到的 LINE 訊息格式

**預期結果：**
- 訊息包含書籍標題、作者、摘要
- 包含下載連結
- 格式美觀易讀
- 支援 Flex Message 格式

#### B2. 多本書籍通知格式
**測試步驟：**
1. 準備包含多本書籍的測試資料
2. 觸發通知處理
3. 檢查訊息是否正確分組或分批發送

**預期結果：**
- 多本書籍合理分組顯示
- 不超過 LINE 訊息長度限制
- 保持良好的可讀性

#### B3. 無新書籍情況
**測試步驟：**
1. 準備空的處理結果檔案
2. 觸發通知處理
3. 檢查是否發送適當的訊息

**預期結果：**
- 發送「今日無新書籍」類型訊息
- 或者不發送訊息（根據設計決定）

### C. 排程服務測試

#### C1. 手動觸發排程任務
**測試步驟：**
1. 使用管理介面或 API 手動觸發
```bash
# 如果有提供管理端點
curl -X POST http://localhost:3000/admin/trigger-daily-processing
```

2. 監控日誌輸出
3. 檢查處理結果

**預期結果：**
- Python ebook 處理器被正確調用
- 處理結果檔案生成
- 通知成功發送給訂閱用戶

#### C2. 錯誤處理和重試機制
**測試步驟：**
1. 故意造成處理失敗（如移除必要檔案）
2. 觀察重試行為
3. 檢查錯誤日誌

**預期結果：**
- 系統按設定進行重試
- 錯誤被正確記錄
- 不會無限重試

### D. 資料庫整合測試

#### D1. 訂閱資料完整性
**驗證 SQL：**
```sql
-- 連接到 books_3f 資料庫
USE books_3f;

-- 檢查訂閱用戶數量
SELECT COUNT(*) as total_subscribers 
FROM user_subscriptions 
WHERE is_subscribed = true;

-- 檢查最近的訂閱活動
SELECT line_user_id, subscription_date, last_notification_sent 
FROM user_subscriptions 
ORDER BY subscription_date DESC 
LIMIT 10;
```

#### D2. 通知記錄完整性
**驗證 SQL：**
```sql
-- 連接到 books_3f 資料庫
USE books_3f;

-- 檢查通知發送記錄
SELECT * FROM notification_logs 
ORDER BY processing_date DESC 
LIMIT 5;

-- 檢查失敗記錄
SELECT nf.*, us.display_name 
FROM delivery_failures nf
LEFT JOIN user_subscriptions us ON nf.line_user_id = us.line_user_id
WHERE nf.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

### E. 系統整合測試

#### E1. Python-TypeScript 資料交換
**測試步驟：**
1. 手動執行 Python ebook 處理器
```bash
cd ebook
python main_processor.py
```

2. 檢查輸出檔案是否生成
3. 驗證 TypeScript 服務是否正確讀取

**預期結果：**
- JSON 輸出檔案格式正確
- TypeScript 服務成功解析資料
- 資料完整性保持

#### E2. LINE API 整合
**測試步驟：**
1. 發送各種類型的測試訊息
2. 檢查 webhook 處理
3. 驗證回應訊息

**預期結果：**
- Webhook 正確接收和處理訊息
- 回應訊息格式正確
- 無 API 錯誤

## 效能測試

### F1. 大量用戶通知測試
**測試步驟：**
1. 在 books_3f 資料庫中建立多個測試訂閱用戶
```sql
-- 連接到 books_3f 資料庫
USE books_3f;

INSERT INTO user_subscriptions (line_user_id, display_name, is_subscribed) 
VALUES 
('test_user_1', 'Test User 1', true),
('test_user_2', 'Test User 2', true),
-- ... 更多測試用戶
('test_user_100', 'Test User 100', true);
```

2. 觸發通知發送
3. 監控處理時間和成功率

**預期結果：**
- 所有用戶都收到通知
- 處理時間在合理範圍內
- 無記憶體洩漏或效能問題

### F2. 錯誤恢復測試
**測試步驟：**
1. 在處理過程中故意中斷服務
2. 重啟服務
3. 檢查是否能正確恢復

**預期結果：**
- 服務能夠正常重啟
- 未完成的任務能夠恢復或重新處理
- 資料一致性保持

## 用戶體驗測試

### G1. 訊息內容品質
**檢查項目：**
- [ ] 訊息文字清晰易懂
- [ ] 書籍摘要長度適中
- [ ] 下載連結可正常使用
- [ ] 訊息格式在手機上顯示良好

### G2. 互動流程順暢性
**檢查項目：**
- [ ] 訂閱流程簡單直觀
- [ ] 快速回覆按鈕功能正常
- [ ] 錯誤訊息友善且有幫助
- [ ] 回應時間在可接受範圍內

## 安全性測試

### H1. 輸入驗證
**測試步驟：**
1. 發送異常格式的訊息
2. 嘗試 SQL 注入攻擊
3. 發送超長訊息

**預期結果：**
- 系統正確處理異常輸入
- 無安全漏洞
- 適當的錯誤處理

### H2. 資料保護
**檢查項目：**
- [ ] 用戶資料加密存儲
- [ ] API 金鑰安全管理
- [ ] 日誌中無敏感資訊洩露

## 測試記錄表

### 測試執行記錄
| 測試項目 | 執行日期 | 測試結果 | 問題描述 | 解決狀態 |
|---------|---------|---------|---------|---------|
| A1. 用戶訂閱流程 | | ✅/❌ | | |
| A2. 訂閱狀態查詢 | | ✅/❌ | | |
| A3. 取消訂閱流程 | | ✅/❌ | | |
| B1. 單本書籍通知 | | ✅/❌ | | |
| B2. 多本書籍通知 | | ✅/❌ | | |
| B3. 無新書籍情況 | | ✅/❌ | | |
| C1. 手動觸發排程 | | ✅/❌ | | |
| C2. 錯誤處理重試 | | ✅/❌ | | |
| D1. 訂閱資料完整性 | | ✅/❌ | | |
| D2. 通知記錄完整性 | | ✅/❌ | | |
| E1. 資料交換整合 | | ✅/❌ | | |
| E2. LINE API 整合 | | ✅/❌ | | |
| F1. 大量用戶測試 | | ✅/❌ | | |
| F2. 錯誤恢復測試 | | ✅/❌ | | |

### 問題追蹤
| 問題 ID | 發現日期 | 問題描述 | 嚴重程度 | 負責人 | 解決日期 | 解決方案 |
|---------|---------|---------|---------|--------|---------|---------|
| | | | 高/中/低 | | | |

## 驗收標準

### 必須通過的測試項目
- [ ] 所有訂閱管理功能正常運作
- [ ] 通知訊息格式正確且美觀
- [ ] 排程服務穩定執行
- [ ] 資料庫操作無錯誤
- [ ] 系統整合無問題
- [ ] 基本效能要求達標

### 建議通過的測試項目
- [ ] 大量用戶測試通過
- [ ] 錯誤恢復機制完善
- [ ] 用戶體驗良好
- [ ] 安全性測試通過

## 測試工具和腳本

### 快速測試腳本
```bash
#!/bin/bash
# quick_test.sh - 快速功能測試腳本

echo "開始快速功能測試..."

# 檢查服務狀態
curl -f http://localhost:3000/health || echo "❌ 服務未啟動"

# 檢查資料庫連線
mysql -u root -p -e "SELECT 1" || echo "❌ 資料庫連線失敗"

# 檢查必要檔案
[ -f "ebook/main_processor.py" ] || echo "❌ Python 處理器檔案不存在"

echo "快速測試完成"
```

### 資料庫測試查詢
```sql
-- test_queries.sql
-- 檢查系統狀態的 SQL 查詢集合

-- 連接到 books_3f 資料庫
USE books_3f;

-- 1. 檢查訂閱用戶統計
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN is_subscribed = true THEN 1 ELSE 0 END) as subscribed_users,
    SUM(CASE WHEN is_subscribed = false THEN 1 ELSE 0 END) as unsubscribed_users
FROM user_subscriptions;

-- 2. 檢查最近的通知記錄
SELECT 
    processing_date,
    total_recipients,
    successful_deliveries,
    failed_deliveries,
    (successful_deliveries / total_recipients * 100) as success_rate
FROM notification_logs 
ORDER BY processing_date DESC 
LIMIT 7;

-- 3. 檢查錯誤統計
SELECT 
    error_type,
    COUNT(*) as error_count,
    COUNT(DISTINCT line_user_id) as affected_users
FROM delivery_failures 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY error_type;
```

這個測試指南涵蓋了系統的所有主要功能和整合點，你可以按照這個流程進行系統性的驗收測試。