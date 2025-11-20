# Flex Message 錯誤調試指南

## 當前問題

LINE API 返回 400 Bad Request 錯誤，表示 Flex Message 格式有問題。

## 已添加的調試功能

修改了 `lineMessagingService.ts` 以顯示 LINE API 的詳細錯誤訊息：

```typescript
if (error.response && error.response.data) {
  console.error('LINE API Error Details:', JSON.stringify(error.response.data, null, 2));
}
```

## 調試步驟

### 1. 重啟伺服器
```bash
cd Line-bot-llm-mysql
npm start
```

### 2. 在 LINE 中輸入 `flex1`

### 3. 查看伺服器日誌

日誌中會顯示：
```
LINE API Error Details: {
  "message": "...",
  "details": [...]
}
```

這會告訴我們 Flex Message 的哪個部分有問題。

## 常見的 Flex Message 錯誤

### 1. 無效的 URI
- 問題：URI 格式不正確
- 解決：確保 URI 是有效的 URL

### 2. 超過大小限制
- 問題：Flex Message JSON 太大
- 解決：減少內容或簡化結構

### 3. 無效的屬性值
- 問題：某些屬性值不符合規範
- 解決：檢查 LINE Flex Message Simulator

### 4. ReplyToken 已使用
- 問題：同一個 replyToken 被使用多次
- 解決：確保每個 replyToken 只使用一次

## 測試 Flex Message 格式

### 使用 LINE Flex Message Simulator
1. 訪問：https://developers.line.biz/flex-simulator/
2. 複製測試腳本生成的 JSON
3. 貼上到 Simulator 驗證格式

### 測試腳本
```bash
cd Line-bot-llm-mysql
npx ts-node test-flex-notification.ts > flex-output.json
```

然後檢查 `flex-output.json` 的格式。

## 下一步

1. 重啟伺服器
2. 輸入 `flex1`
3. 查看日誌中的 "LINE API Error Details"
4. 根據錯誤訊息修復 Flex Message 格式

## 可能的解決方案

### 如果是 URI 問題
檢查 PDF URL 是否有效：
```typescript
pdfUrls: [
  'https://www.budaedu.org/ebooks/book1.pdf',  // 確保這些 URL 有效
  'https://www.budaedu.org/ebooks/book1-part2.pdf'
]
```

### 如果是大小問題
減少測試資料：
```typescript
// 只測試 1 本書
const testBooks = [
  {
    title: '金剛經講記',
    author: '淨空法師',
    pdfUrls: ['https://www.budaedu.org/ebooks/book1.pdf']
  }
];
```

### 如果是格式問題
使用 LINE Flex Message Simulator 驗證 JSON 格式。

## 臨時解決方案

如果 Flex Message 一直有問題，可以先用簡單的文字訊息測試：

```typescript
// 在 webhookHandler.ts 中
if (message === 'flex1') {
  await lineMessagingService.sendTextMessage(
    replyToken,
    '📚 新書通知測試\n\n1. 金剛經講記 - 淨空法師\n2. 楞嚴經淺釋 - 宣化上人\n3. 地藏菩薩本願經 - 黃智海居士'
  );
  return true;
}
```

## 日期
2025-11-18
