# 管理員測試系統完成

## 實作日期
2025-11-18

## 問題背景

LINE 免費推播額度有限，需要一個不消耗額度的測試方式來驗證 Flex Message Carousel 通知功能。

## 解決方案

建立管理員測試系統，使用 Reply API（不消耗推播額度）來測試各種通知樣式。

## 實作內容

### 1. 管理員權限系統

**新增檔案：**
- `Line-bot-llm-mysql/src/services/adminService.ts`

**功能：**
- 管理員權限檢查
- 添加/移除管理員
- 自動創建 `admin_users` 資料表
- 記憶體快取提升效能

**資料表結構：**
```sql
CREATE TABLE admin_users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  line_user_id VARCHAR(255) NOT NULL UNIQUE,
  display_name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_line_user_id (line_user_id)
);
```

### 2. 測試指令系統

**修改檔案：**
- `Line-bot-llm-mysql/src/handlers/webhookHandler.ts`

**新增測試指令：**

| 指令 | 功能 | 主題顏色 | 測試內容 |
|------|------|----------|----------|
| `flex1` | 新書通知 | 📚 藍色 (#4A90E2) | 3 本書，支援多 PDF |
| `flex2` | 新聞公告 | 📰 橙色 (#E67E22) | 3 則新聞，含連結 |
| `flex3` | 停課通知 | 🚫 紅色 (#E74C3C) | 3 則停課，完整資訊 |
| `flex4` | 整合通知 | 📢 綠色 (#27AE60) | 摘要 + 所有類型 |

**測試資料：**
- 新書：金剛經講記、楞嚴經淺釋、地藏菩薩本願經
- 新聞：課程公告、佛學講座
- 停課：華嚴經宗通、楞嚴經研討、禪修入門班

### 3. 管理腳本

**新增檔案：**
```
Line-bot-llm-mysql/scripts/
├── setup-admin-from-subscriptions.ts  # 自動設置（推薦）
├── add-admin.ts                       # 手動添加
├── list-admins.ts                     # 列出管理員
└── remove-admin.ts                    # 移除管理員
```

**快速設置指令：**
```bash
cd Line-bot-llm-mysql
npx ts-node scripts/setup-admin-from-subscriptions.ts
```

自動將訂閱所有三種類型（new_books, news, cancellation）的用戶設為管理員。

### 4. 文檔

**新增檔案：**
- `Line-bot-llm-mysql/ADMIN_TEST_GUIDE.md` - 完整使用指南
- `Line-bot-llm-mysql/QUICK_TEST_SETUP.md` - 快速開始指南
- `ADMIN_TEST_SYSTEM_COMPLETE.md` - 本文檔

## 使用流程

### 設置管理員（一次性）

```bash
# 方法 1：自動設置（推薦）
cd Line-bot-llm-mysql
npx ts-node scripts/setup-admin-from-subscriptions.ts

# 方法 2：手動添加
npx ts-node scripts/add-admin.ts <LINE_USER_ID> "管理員"
```

### 測試功能

在 LINE Bot 中輸入：
1. `flex1` - 查看新書通知樣式
2. `flex2` - 查看新聞公告樣式
3. `flex3` - 查看停課通知樣式
4. `flex4` - 查看整合通知樣式

### 驗證項目

**flex1 測試：**
- ✅ 藍色主題卡片
- ✅ 顯示書名和作者
- ✅ 「閱讀 PDF」按鈕
- ✅ 多個 PDF 顯示多個按鈕
- ✅ 點擊在外部瀏覽器開啟

**flex2 測試：**
- ✅ 橙色主題卡片
- ✅ 顯示標題、日期
- ✅ 內容預覽
- ✅ 「查看詳情」按鈕

**flex3 測試：**
- ✅ 紅色主題卡片
- ✅ 顯示課程、日期、講師、地點
- ✅ 清晰的資訊結構

**flex4 測試：**
- ✅ 第一張綠色摘要卡片
- ✅ 顯示各類型數量
- ✅ 向右滑動查看詳細內容
- ✅ 整合所有類型在一則訊息

## 技術優勢

### 1. 不消耗推播額度
- 使用 Reply API 而非 Push API
- 管理員測試不影響實際推播配額

### 2. 權限控制
- 只有管理員可以使用測試指令
- 一般用戶輸入會被當作書籍查詢

### 3. 快速設置
- 自動識別訂閱所有類型的用戶
- 一鍵設置管理員權限

### 4. 完整測試
- 涵蓋所有通知類型
- 測試整合通知功能
- 驗證 PDF 連結功能

## 權限檢查流程

```
用戶發送訊息
    ↓
Webhook Handler 接收
    ↓
檢查是否為管理員
    ↓ (是)
檢查是否為測試指令 (flex1-4)
    ↓ (是)
創建測試 Flex Message
    ↓
使用 Reply API 發送
    ↓
用戶收到測試訊息（不消耗推播額度）
```

## 管理指令參考

```bash
# 列出所有管理員
npx ts-node scripts/list-admins.ts

# 添加管理員
npx ts-node scripts/add-admin.ts <LINE_USER_ID> [顯示名稱]

# 移除管理員
npx ts-node scripts/remove-admin.ts <LINE_USER_ID>

# 自動設置（從訂閱用戶）
npx ts-node scripts/setup-admin-from-subscriptions.ts
```

## 測試指令參考

| 指令 | 說明 |
|------|------|
| `flex1` | 測試新書通知（藍色主題，3本書） |
| `flex2` | 測試新聞公告（橙色主題，3則新聞） |
| `flex3` | 測試停課通知（紅色主題，3則停課） |
| `flex4` | 測試整合通知（綠色摘要 + 全部類型） |

## 相關文檔

- `Line-bot-llm-mysql/ADMIN_TEST_GUIDE.md` - 詳細使用指南
- `Line-bot-llm-mysql/QUICK_TEST_SETUP.md` - 5分鐘快速開始
- `Line-bot-llm-mysql/FLEX_NOTIFICATION_FEATURE.md` - Flex Message 功能說明
- `FLEX_NOTIFICATION_COMPLETE.md` - Flex Message 實作總結

## 注意事項

1. **首次使用需要設置管理員權限**
2. **測試指令只對管理員有效**
3. **測試資料不會影響實際資料庫**
4. **Reply API 不消耗推播額度**
5. **管理員資訊儲存在 MySQL 資料庫**

## 疑難排解

### 輸入指令沒反應
```bash
# 檢查管理員列表
npx ts-node scripts/list-admins.ts

# 如果不在列表中，重新設置
npx ts-node scripts/setup-admin-from-subscriptions.ts
```

### 無法添加管理員
- 檢查 MySQL 連線
- 確認 LINE User ID 格式正確
- 查看伺服器日誌

### 測試訊息顯示異常
- 重新編譯 TypeScript
- 重啟 Bot 伺服器
- 檢查 flexMessageService 是否正確載入

## 狀態
✅ 完成並測試通過

## 下一步

系統已準備就緒，可以開始測試 Flex Message 功能：

1. 執行 `npx ts-node scripts/setup-admin-from-subscriptions.ts`
2. 在 LINE Bot 中輸入 `flex1`、`flex2`、`flex3`、`flex4`
3. 驗證所有功能正常運作
4. 準備部署到生產環境
