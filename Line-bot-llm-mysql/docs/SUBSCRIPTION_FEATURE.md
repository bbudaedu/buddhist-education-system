# 訂閱功能使用指南

## 功能概述

LINE Bot 現在支援多種類型的通知訂閱，用戶可以選擇訂閱以下類型的通知：

- 📚 **新書通知** (`new_books`): 每日新書資訊推送
- 📰 **最新消息** (`news`): 網站最新消息和公告
- ⚠️ **停課通知** (`cancellation`): 課程停課資訊

## 用戶指令

### 訂閱指令

#### 訂閱所有類型
```
訂閱
訂閱新書
```

#### 訂閱特定類型
```
訂閱最新消息
訂閱新聞
訂閱停課通知
訂閱停課
```

### 取消訂閱指令

#### 取消所有訂閱
```
取消訂閱
```

#### 取消特定類型訂閱
```
取消訂閱最新消息
取消訂閱新聞
取消訂閱停課通知
取消訂閱停課
```

### 查詢訂閱狀態
```
訂閱狀態
我的訂閱
```

## 資料庫結構

### user_subscriptions 表格

新增欄位：
- `notification_types` (JSON): 用戶訂閱的通知類型陣列
  - 範例: `["new_books", "news", "cancellation"]`

### notification_logs 表格

新增欄位：
- `notification_type` (VARCHAR): 通知類型
  - 可能值: `new_books`, `news`, `cancellation`, `daily_summary`

### delivery_failures 表格

新增欄位：
- `notification_type` (VARCHAR): 失敗的通知類型

## API 使用

### 訂閱服務 API

```typescript
import { subscriptionService } from './services/subscriptionService';

// 訂閱所有類型
await subscriptionService.subscribeUser(userId);

// 訂閱特定類型
await subscriptionService.subscribeUser(userId, ['news', 'cancellation']);

// 訂閱單一類型
await subscriptionService.subscribeToType(userId, 'news');

// 取消訂閱特定類型
await subscriptionService.unsubscribeFromType(userId, 'news');

// 檢查用戶是否訂閱特定類型
const isSubscribed = await subscriptionService.isUserSubscribedToType(userId, 'news');

// 取得訂閱特定類型的所有用戶
const users = await subscriptionService.getSubscribedUsers('news');
```

### 網站監控通知 API

從 Python 發送通知時，需要在 metadata 中指定 contentType：

```python
import requests

notification_data = {
    "type": "broadcast",
    "message": "📰 最新消息\n\n...",
    "timestamp": "2025-11-14T10:00:00",
    "metadata": {
        "contentType": "news",  # 'news', 'cancellation', 'carousel', 'media'
        "itemCount": 5,
        "priority": "high"
    }
}

response = requests.post(
    "http://localhost:3000/api/notifications/website-monitoring",
    json=notification_data
)
```

### Content Type 對應

Python 的 contentType 會自動對應到訂閱類型：

| Python contentType | 訂閱類型 | 說明 |
|-------------------|---------|------|
| `news` | `news` | 最新消息 |
| `cancellation` | `cancellation` | 停課通知 |
| `carousel` | `new_books` | 輪播圖（通常是新書） |
| `media` | `news` | 媒體報導 |

## 資料庫遷移

執行以下 SQL 遷移檔案來更新資料庫結構：

```bash
# 在 MySQL 中執行
mysql -u username -p database_name < migrations/003_add_notification_types.sql
```

或使用應用程式內建的遷移功能：

```typescript
import { databaseService } from './services/databaseService';

await databaseService.runMigrations();
```

## 測試

### 測試訂閱功能

1. 在 LINE 中發送 `訂閱最新消息`
2. 確認收到訂閱成功訊息
3. 發送 `訂閱狀態` 查看訂閱資訊
4. 發送測試通知驗證接收

### 測試通知發送

使用測試端點發送通知：

```bash
curl -X POST http://localhost:3000/api/notifications/website-monitoring \
  -H "Content-Type: application/json" \
  -d '{
    "type": "broadcast",
    "message": "📰 測試最新消息\n\n這是一則測試通知",
    "timestamp": "2025-11-14T10:00:00",
    "metadata": {
      "contentType": "news",
      "itemCount": 1,
      "priority": "high"
    }
  }'
```

## 注意事項

1. **預設訂閱**: 新用戶訂閱時，預設訂閱所有類型
2. **通知過濾**: 只有訂閱相應類型的用戶才會收到通知
3. **訂閱狀態**: 用戶可以隨時查看和修改訂閱狀態
4. **資料遷移**: 現有用戶會自動訂閱所有類型（向後相容）

## 未來擴展

可以考慮添加的功能：

- 通知時間設定（靜音時段）
- 通知頻率控制
- 更細緻的通知類型分類
- 通知內容客製化
- 批次訂閱管理
