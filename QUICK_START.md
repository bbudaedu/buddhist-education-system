# 🚀 快速啟動指南

## ⚠️ 重要：必須重啟 Node.js 伺服器

修改了 TypeScript 程式碼，**必須重啟伺服器**才能生效！

## 立即執行這 3 步

### 1️⃣ 重啟 Node.js 伺服器（必須！）
```bash
# 停止現有伺服器 (Ctrl+C)
cd Line-bot-llm-mysql
npm start
```

### 2️⃣ 執行完整測試
```bash
ebook\run_daily_monitoring_utf8.bat
```

### 3️⃣ 檢查結果
- ✅ 查看 Node.js 終端日誌
- ✅ 確認用戶收到 LINE 通知

---

## 預期看到的日誌

### Python 端
```
✅ Unified notification service initialized
✅ LINE 停課通知發送成功
✅ LINE 新聞公告發送成功
```

### Node.js 端
```
📥 Received website monitoring notification request
📋 Content type: cancellation
✅ Found 1 users subscribed to cancellation notifications
✅ Notification sent successfully
```

---

## 如果出問題

```bash
# 檢查訂閱狀態
node Line-bot-llm-mysql/quick-check-db.js

# 測試通知
python ebook/test_fixed_notification.py
```

---

## 完整文件
- `FINAL_SUMMARY.md` - 完整摘要
- `DEPLOYMENT_CHECKLIST.md` - 詳細檢查清單
- `NOTIFICATION_SYSTEM_FIXED.md` - 技術文件
