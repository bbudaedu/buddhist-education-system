# 快速測試設置指南

## 🚀 5 分鐘快速開始

### 步驟 1：設置管理員權限

在終端機執行：

```bash
cd Line-bot-llm-mysql
npx ts-node scripts/setup-admin-from-subscriptions.ts
```

這會自動將訂閱所有三種類型的用戶（你）設為管理員。

### 步驟 2：在 LINE Bot 中測試

打開 LINE，找到你的 Bot，輸入以下指令：

| 指令 | 功能 | 主題顏色 |
|------|------|----------|
| `flex1` | 新書通知 | 📚 藍色 |
| `flex2` | 新聞公告 | 📰 橙色 |
| `flex3` | 停課通知 | 🚫 紅色 |
| `flex4` | 整合通知 | 📢 綠色摘要 + 全部 |

### 步驟 3：驗證功能

測試 `flex1` 時檢查：
- ✅ 顯示 3 本書的卡片
- ✅ 每本書有「閱讀 PDF」按鈕
- ✅ 點擊按鈕在外部瀏覽器開啟
- ✅ 支援多個 PDF 的書籍顯示多個按鈕

測試 `flex4` 時檢查：
- ✅ 第一張卡片顯示摘要（綠色）
- ✅ 向右滑動查看新書、新聞、停課
- ✅ 所有內容整合在一則訊息中

## 💡 重要提示

- ✅ 測試指令使用 Reply API，**不消耗推播額度**
- ✅ 只有管理員可以使用這些指令
- ✅ 測試資料不會影響實際資料庫

## 🔧 如果遇到問題

### 問題：輸入指令沒反應
```bash
# 檢查是否為管理員
npx ts-node scripts/list-admins.ts
```

### 問題：不是管理員
```bash
# 手動添加（需要你的 LINE User ID）
npx ts-node scripts/add-admin.ts <你的LINE_USER_ID> "測試管理員"
```

### 如何取得 LINE User ID？
1. 在 Bot 中發送任何訊息
2. 查看伺服器日誌
3. 或輸入「訂閱狀態」查看

## 📚 詳細文檔

- `ADMIN_TEST_GUIDE.md` - 完整使用指南
- `FLEX_NOTIFICATION_FEATURE.md` - 功能說明
- `FLEX_MESSAGE_QUICK_REFERENCE.md` - API 參考

## 🎉 開始測試吧！

現在你可以盡情測試 Flex Message 功能，不用擔心推播額度！
