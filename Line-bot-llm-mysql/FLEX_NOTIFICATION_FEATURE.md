# Flex Message 通知系統

## 功能概述

全新的 Flex Carousel 通知系統，提供更豐富的視覺體驗和更好的用戶互動。

## 主要特性

### 1. Flex Carousel 呈現
- 📚 新書通知：卡片式展示，支援多個 PDF 閱讀連結
- 📰 新聞公告：精美排版，包含日期和內容預覽
- 🚫 停課通知：清晰的資訊結構，易於閱讀

### 2. PDF 閱讀連結
- 每本書下方顯示「閱讀 PDF」按鈕
- 支援多個 PDF 檔案（最多 3 個按鈕）
- 網址自動加上 `?openExternalBrowser=1` 參數
- 點擊後在外部瀏覽器開啟

### 3. 整合通知
- 用戶訂閱多種類型時，整合成一則訊息
- 第一張卡片顯示摘要資訊
- 向右滑動查看各類型詳細內容
- 根據用戶訂閱類型個性化過濾

## 技術實作

### 新增檔案
- `src/services/flexMessageService.ts` - Flex Message 創建服務
- `test-flex-notification.ts` - 測試腳本

### 修改檔案
- `src/services/websiteMonitoringNotificationService.ts` - 支援整合通知
- `ebook/unified_notification_service.py` - 發送結構化資料
- `ebook/line_notification_service.py` - 新增整合通知方法

## 使用方式

### Python 端發送
```python
# 準備結構化資料
structured_data = {
    'newBooks': [...],
    'news': [...],
    'cancellations': [...]
}

# 發送整合通知
line_service.send_integrated_notification(structured_data)
```

### TypeScript 端處理
```typescript
// 自動根據用戶訂閱類型創建個性化訊息
await handleIntegratedNotification(notification);
```

## 測試

```bash
# TypeScript 測試
cd Line-bot-llm-mysql
npx ts-node test-flex-notification.ts

# Python 測試
cd ebook
python test_new_book_notification.py
```

## 訊息範例

詳見測試腳本輸出的 JSON 格式。

## 日期
2025-11-18
