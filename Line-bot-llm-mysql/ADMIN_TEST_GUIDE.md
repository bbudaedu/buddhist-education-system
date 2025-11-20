# 管理員測試指令使用指南

## 功能說明

為了測試 Flex Message 通知功能而不消耗 LINE 免費推播額度，我們建立了管理員測試系統。管理員可以使用特殊指令來測試各種通知樣式。

## 快速設置

### 方法 1：自動設置（推薦）

如果你已經訂閱了所有三種類型（新書、新聞、停課），執行以下指令自動成為管理員：

```bash
cd Line-bot-llm-mysql
npx ts-node scripts/setup-admin-from-subscriptions.ts
```

### 方法 2：手動添加管理員

```bash
cd Line-bot-llm-mysql
npx ts-node scripts/add-admin.ts <你的LINE_USER_ID> "管理員"
```

**如何取得 LINE User ID？**
1. 在 LINE Bot 中發送任何訊息
2. 查看伺服器日誌，會顯示你的 User ID
3. 或使用 LINE Developers Console 的 Messaging API 測試工具

## 測試指令

管理員在 LINE Bot 中輸入以下指令即可測試：

### flex1 - 新書通知測試
- 📚 藍色主題卡片
- 顯示 3 本測試書籍
- 每本書有「閱讀 PDF」按鈕
- 支援多個 PDF 檔案
- 網址自動加上 `?openExternalBrowser=1`

**測試內容：**
- 金剛經講記（2 個 PDF）
- 楞嚴經淺釋（1 個 PDF）
- 地藏菩薩本願經白話解釋（1 個 PDF）

### flex2 - 新聞公告測試
- 📰 橙色主題卡片
- 顯示 3 則測試新聞
- 包含標題、日期、內容預覽
- 有「查看詳情」按鈕連結到網站

**測試內容：**
- 小菩薩的慈悲畫室課程公告
- 學佛基礎進階班課程公告
- 佛學講座：心經的智慧

### flex3 - 停課通知測試
- 🚫 紅色主題卡片
- 顯示 3 則測試停課通知
- 包含課程名稱、日期、講師、地點
- 清晰的資訊結構

**測試內容：**
- 華嚴經宗通停課
- 楞嚴經研討停課
- 禪修入門班停課

### flex4 - 整合通知測試
- 📢 整合所有類型的通知
- 第一張卡片：綠色摘要卡片
  - 顯示各類型數量
  - 提示向右滑動查看詳情
- 後續卡片：各類型詳細內容
  - 2 本新書
  - 2 則新聞
  - 1 則停課通知

## 管理指令

### 列出所有管理員
```bash
npx ts-node scripts/list-admins.ts
```

### 添加管理員
```bash
npx ts-node scripts/add-admin.ts <LINE_USER_ID> [顯示名稱]
```

### 移除管理員
```bash
npx ts-node scripts/remove-admin.ts <LINE_USER_ID>
```

## 使用流程

1. **設置管理員權限**
   ```bash
   cd Line-bot-llm-mysql
   npx ts-node scripts/setup-admin-from-subscriptions.ts
   ```

2. **在 LINE Bot 中測試**
   - 打開 LINE 與 Bot 的對話
   - 輸入 `flex1` 測試新書通知
   - 輸入 `flex2` 測試新聞公告
   - 輸入 `flex3` 測試停課通知
   - 輸入 `flex4` 測試整合通知

3. **驗證功能**
   - ✅ 檢查卡片樣式是否正確
   - ✅ 檢查顏色主題是否符合
   - ✅ 點擊「閱讀 PDF」按鈕，確認在外部瀏覽器開啟
   - ✅ 檢查整合通知的摘要卡片
   - ✅ 向右滑動查看所有內容

## 注意事項

1. **權限限制**
   - 只有管理員可以使用 flex 測試指令
   - 一般用戶輸入這些指令會被當作書籍查詢處理

2. **不消耗推播額度**
   - 測試指令使用 Reply API，不消耗推播額度
   - 只有實際的通知推送才會消耗額度

3. **測試資料**
   - 所有測試資料都是預設的範例
   - PDF 連結指向測試網址
   - 不會影響實際的資料庫

4. **管理員資料表**
   - 首次執行會自動創建 `admin_users` 資料表
   - 管理員資訊儲存在 MySQL 資料庫中

## 疑難排解

### 問題：輸入 flex1 沒有反應
**解決方法：**
1. 確認你已被設為管理員：`npx ts-node scripts/list-admins.ts`
2. 確認 Bot 伺服器正在運行
3. 檢查伺服器日誌是否有錯誤訊息

### 問題：無法添加管理員
**解決方法：**
1. 確認 MySQL 資料庫連線正常
2. 確認 LINE User ID 格式正確（通常以 U 開頭）
3. 檢查資料庫權限

### 問題：測試訊息顯示異常
**解決方法：**
1. 確認 flexMessageService 已正確編譯
2. 重新啟動 Bot 伺服器
3. 檢查 TypeScript 編譯錯誤

## 相關文檔

- `FLEX_NOTIFICATION_FEATURE.md` - Flex Message 功能說明
- `FLEX_MESSAGE_QUICK_REFERENCE.md` - 快速參考指南
- `FLEX_NOTIFICATION_COMPLETE.md` - 完整實作文檔

## 技術細節

### 資料表結構
```sql
CREATE TABLE admin_users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  line_user_id VARCHAR(255) NOT NULL UNIQUE,
  display_name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_line_user_id (line_user_id)
);
```

### 權限檢查流程
```
用戶發送訊息
    ↓
Webhook Handler
    ↓
檢查是否為管理員 (adminService.isAdmin)
    ↓ (是)
處理測試指令 (handleAdminTestCommand)
    ↓
發送 Flex Message
```

## 日期
2025-11-18
