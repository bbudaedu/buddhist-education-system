# 最新消息功能整合文件

## 功能概述

整合佛陀教育基金會網站的最新消息功能到 LINE Bot，當用戶輸入「最新消息」時，會回覆一則 Flex Carousel（多卡片最新消息），並在同一則訊息掛上 Quick Reply 按鈕，讓使用者可以直接訂閱不同類型的通知。

## 功能特點

### 1. 最新消息顯示
- 使用 Flex Carousel 格式顯示最多 10 則最新消息
- 每則消息包含：
  - 📰 圖示
  - 標題（最多 60 字元）
  - 內容預覽（最多 100 字元）
  - 發布日期
  - 「查看完整內容」按鈕（連結到官網）

### 2. Quick Reply 訂閱選項
在最新消息下方提供 5 個快速回覆按鈕：
- 📰 訂閱最新消息
- ⚠️ 訂閱停課通知
- 📚 訂閱新書通知
- 📊 訂閱狀態查詢
- ❌ 取消訂閱

### 3. API 整合
- API 端點：`https://publish.budaedu.org/laravel/public/api/bulletins`
- 網址格式：`https://www.budaedu.org/#/bulletins/{id}`
- 支援過濾、排序和附件查詢

## 技術實作

### 新增檔案

#### 1. `src/services/bulletinService.ts`
負責從佛陀教育基金會 API 抓取最新消息資料。

**主要方法：**
- `getLatestBulletins(limit)`: 取得最新消息列表
- `getBulletinById(bulletinId)`: 取得單一消息詳情
- `stripHtmlTags(html)`: 移除 HTML 標籤

**資料結構：**
```typescript
interface Bulletin {
  id: string;
  title: string;
  content: string;
  publishStartDate: string;
  publishEndDate: string;
  url: string;
}
```

### 修改檔案

#### 1. `src/services/lineMessagingService.ts`
新增兩個方法：
- `sendBulletinsCarousel()`: 發送最新消息 Carousel 訊息（帶 Quick Reply）
- `createBulletinsCarouselFlexMessage()`: 建立 Flex Carousel 訊息格式

#### 2. `src/handlers/webhookHandler.ts`
- 新增 `handleBulletinsCommand()` 方法處理「最新消息」指令
- 在 `processMessage()` 中檢查「最新消息」關鍵字

#### 3. `package.json`
新增依賴套件：
- `axios`: ^1.6.0（用於 HTTP 請求）

## 使用方式

### 用戶操作流程

1. **查看最新消息**
   ```
   用戶輸入：最新消息
   Bot 回覆：Flex Carousel（顯示最多 10 則消息）+ Quick Reply 按鈕
   ```

2. **訂閱特定類型**
   - 點擊 Quick Reply 按鈕「📰 訂閱最新消息」
   - Bot 回覆訂閱成功訊息

3. **查看完整內容**
   - 點擊任一消息卡片的「查看完整內容」按鈕
   - 開啟瀏覽器顯示官網完整內容

### 指令列表

| 指令 | 功能 |
|------|------|
| `最新消息` | 顯示最新消息 Carousel |
| `訂閱最新消息` | 訂閱最新消息通知 |
| `訂閱停課通知` | 訂閱停課通知 |
| `訂閱新書通知` | 訂閱新書通知 |
| `訂閱狀態` | 查詢訂閱狀態 |
| `取消訂閱` | 取消所有訂閱 |

## 測試

### 測試檔案
`test-bulletin-service.ts` - 測試最新消息服務

### 執行測試
```bash
npx ts-node test-bulletin-service.ts
```

### 測試項目
1. ✅ 取得最新消息列表（前 5 則）
2. ✅ 取得單一消息詳情
3. ✅ HTML 標籤移除功能
4. ✅ API 連接穩定性

## API 規律

### 列表 API
```
GET https://publish.budaedu.org/laravel/public/api/bulletins
參數：
  - filter[publishing]: 過濾發布中的消息
  - include: attachments（包含附件）
  - order: publish_start_date,desc|updated_at,desc（排序）
```

### 單一消息 API
```
GET https://publish.budaedu.org/laravel/public/api/bulletins/{id}
參數：
  - include: attachments（包含附件）
```

### 網址格式
```
https://www.budaedu.org/#/bulletins/{id}
```

## 注意事項

### SSL 憑證處理
由於目標 API 的 SSL 憑證問題，在開發環境中使用了 `rejectUnauthorized: false` 設定。
**生產環境建議：**
- 聯繫 API 提供方修復憑證問題
- 或使用代理伺服器處理 SSL 驗證

### 錯誤處理
- API 連接失敗：回覆「無法取得最新消息，請稍後再試」
- 無消息資料：回覆「目前沒有最新消息」
- 超時設定：10 秒

### 效能考量
- Carousel 限制最多 10 則消息（LINE 平台限制）
- 標題限制 60 字元
- 內容預覽限制 100 字元
- API 請求超時 10 秒

## 未來擴展

### 可能的功能增強
1. **快取機制**：減少 API 請求次數
2. **分類過濾**：依消息類型過濾（課程、活動、公告等）
3. **關鍵字搜尋**：搜尋特定主題的消息
4. **定期推送**：自動推送最新消息給訂閱用戶
5. **多語言支援**：提供英文版消息

### 整合建議
- 與現有的訂閱系統整合
- 記錄用戶查看消息的行為
- 提供消息閱讀統計

## 相關文件

- [訂閱功能文件](./SUBSCRIPTION_FEATURE.md)
- [LINE Messaging API 文件](https://developers.line.biz/en/docs/messaging-api/)
- [Flex Message 設計指南](https://developers.line.biz/en/docs/messaging-api/using-flex-messages/)
