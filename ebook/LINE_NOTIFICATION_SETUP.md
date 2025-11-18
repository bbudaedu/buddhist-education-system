# LINE 通知整合設定指南

## 概述

本系統整合了 Python 網站監控系統與 TypeScript LINE bot，實現自動通知功能。

## 架構

```
Python 網站監控系統 (ebook/)
    ↓ HTTP POST
TypeScript LINE Bot API (Line-bot-llm-mysql/)
    ↓ LINE Messaging API
LINE 用戶
```

## 設定步驟

### 1. Python 端配置 (ebook/config.json)

在 `config.json` 中添加 LINE bot 配置：

```json
{
  "line_bot": {
    "enabled": true,
    "api_url": "http://localhost:3000/api/notifications/website-monitoring",
    "api_key": ""
  },
  "website_monitoring": {
    "notifications": {
      "line_enabled": true,
      "email_enabled": true
    }
  }
}
```

### 2. TypeScript 端啟動

確保 LINE bot 服務正在運行：

```bash
cd Line-bot-llm-mysql
npm install
npm run dev
```

服務將在 `http://localhost:3000` 啟動。

### 3. 測試整合

執行測試腳本：

```bash
cd ebook
python test_line_notification.py
```

## API 端點

### 接收網站監控通知

**POST** `/api/notifications/website-monitoring`

請求格式：
```json
{
  "type": "broadcast|alert|summary",
  "message": "通知訊息內容",
  "timestamp": "2025-11-13T10:00:00",
  "metadata": {
    "contentType": "news|carousel|cancellation|media",
    "itemCount": 5,
    "priority": "high|medium|low"
  }
}
```

回應格式：
```json
{
  "success": true,
  "messagesSent": 10,
  "message": "Notification processed successfully"
}
```

### 發送測試通知

**POST** `/api/notifications/test`

請求格式：
```json
{
  "userId": "U1234567890abcdef"
}
```

### 健康檢查

**GET** `/api/notifications/health`

回應格式：
```json
{
  "success": true,
  "service": "LINE Bot Notification Service",
  "status": "healthy",
  "timestamp": "2025-11-13T10:00:00.000Z"
}
```

## 通知類型

### 1. 緊急通知 (Immediate Alert)

用於需要立即關注的內容，如課程取消。

```python
alert_items = [
    {
        'content_type': 'cancellation',
        'course_name': '課程名稱',
        'cancellation_date': '2025-11-13',
        'instructor_name': '講師名稱'
    }
]
service.send_immediate_alert(alert_items)
```

### 2. 每日摘要 (Daily Summary)

用於定期彙總的內容更新。

```python
summary_items = [
    {
        'content_type': 'news',
        'title': '新聞標題',
        'publication_date': '2025-11-13'
    },
    {
        'content_type': 'carousel',
        'banner_title': '橫幅標題',
        'course_name': '課程名稱'
    }
]
service.send_daily_summary(summary_items)
```

### 3. 廣播訊息 (Broadcast)

用於發送自訂格式的訊息。

```python
message = "📢 通知內容\n\n詳細資訊..."
service.send_broadcast_message(message)
```

## 訊息格式範例

### 緊急通知

```
🚨 緊急通知
━━━━━━━━━━━━━━━

📅 課程取消
課程：華嚴經宗通
日期：2025-11-13
講師：某某法師

📰 重要公告
標題：【重要】圖書館閉館通知
日期：2025-11-13

⏰ 2025-11-13 10:00

💡 輸入「查詢書籍」可搜尋館藏
```

### 每日摘要

```
📊 每日監控摘要
━━━━━━━━━━━━━━━

📰 新聞公告：5 項
  • 【公告】圖書館開放時間調整
  • 【活動】佛學講座報名開始
  • 【通知】新書到館通知
  ... 還有 2 項

🎯 輪播橫幅：3 項
  • 2025年度課程總覽
  • 線上課程報名中
  • 圖書館服務指南

⏰ 2025-11-13 10:00

💡 輸入「查詢書籍」可搜尋館藏
```

## 重要提醒

### LINE Broadcast 限制

LINE broadcast API 只會發送訊息給：
1. **已加入 bot 為好友的用戶**
2. **曾經與 bot 互動過的用戶**

如果你沒有收到通知，請確認：
- 已經在 LINE 中加入此 bot 為好友
- 至少發送過一次訊息給 bot（例如：「查詢書籍」）

### 測試步驟

1. 在 LINE 中搜尋並加入你的 bot
2. 發送任意訊息給 bot（例如：「測試」）
3. 執行測試腳本：`python test_line_notification.py`
4. 檢查 LINE 是否收到通知

## 故障排除

### 1. 通知未發送

檢查項目：
- LINE bot 服務是否運行 (`http://localhost:3000/health`)
- `config.json` 中 `line_bot.enabled` 是否為 `true`
- `website_monitoring.notifications.line_enabled` 是否為 `true`
- API URL 是否正確
- **是否已加入 bot 為好友並互動過**

### 2. 連線錯誤

```
Error: Connection refused
```

解決方法：
- 確認 LINE bot 服務正在運行
- 檢查防火牆設定
- 確認端口 3000 未被占用

### 3. 認證錯誤

如果設定了 `api_key`，確保 Python 端和 TypeScript 端的 key 一致。

## 日誌查看

### Python 端

日誌位置：`ebook/logs/daily_monitoring_*.log`

關鍵訊息：
```
LINE notification service initialized
Sending LINE broadcast message...
LINE broadcast message sent successfully
```

### TypeScript 端

控制台輸出：
```
📢 Processing website monitoring notification (type: broadcast)
✅ Website monitoring notification sent: 10 success, 0 failed
```

## 生產環境部署

### 1. 修改 API URL

將 `config.json` 中的 `api_url` 改為生產環境地址：

```json
{
  "line_bot": {
    "api_url": "https://your-domain.com/api/notifications/website-monitoring"
  }
}
```

### 2. 添加 API Key

為安全起見，在生產環境中設定 API key：

```json
{
  "line_bot": {
    "api_key": "your-secret-api-key"
  }
}
```

### 3. HTTPS 支援

確保 LINE bot 服務使用 HTTPS。

## 進階功能

### 用戶訂閱管理

目前系統向所有用戶廣播通知。未來可以實作：

1. 用戶訂閱/取消訂閱功能
2. 通知偏好設定（只接收特定類型）
3. 通知時間設定（靜音時段）

### 通知統計

可以在 TypeScript 端添加統計功能：

- 通知發送成功率
- 用戶互動率
- 通知類型分布

## 相關檔案

### Python 端
- `line_notification_service.py` - LINE 通知服務
- `notification_processor.py` - 通知處理器
- `test_line_notification.py` - 測試腳本

### TypeScript 端
- `src/services/websiteMonitoringNotificationService.ts` - 通知服務
- `src/handlers/notificationHandler.ts` - API 處理器
- `src/index.ts` - 主程式（包含 API routes）

## 支援

如有問題，請檢查：
1. 日誌檔案
2. API 健康檢查端點
3. 網路連線狀態
