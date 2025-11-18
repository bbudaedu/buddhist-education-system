---
inclusion: fileMatch
fileMatchPattern: 'Line-bot-llm-mysql/**'
---

# LINE Bot 最新技術範例參考

本文件包含從 Context7 獲取的最新官方範例，用於指導 LINE bot 專案實作。

## Express.js Webhook Server 設定

### 基本 Express 伺服器與錯誤處理

```typescript
import express from 'express';

const app = express();

// 中介軟體設定
app.use(express.json());

// 路由定義
app.post('/webhook', (req, res) => {
  // 處理 webhook 請求
  res.status(200).send('OK');
});

// 錯誤處理中介軟體（必須放在最後）
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err);
  res.status(500).json({ error: 'Sorry something bad happened!' });
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
```

## LINE Bot SDK 整合

### 完整的 Echo Bot 範例

```typescript
import * as line from '@line/bot-sdk';
import express from 'express';

// 建立 LINE SDK 配置
const config = {
  channelSecret: process.env.CHANNEL_SECRET,
};

// 建立 LINE SDK client
const client = new line.messagingApi.MessagingApiClient({
  channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN
});

// 建立 Express app
const app = express();

// 註冊 webhook 處理器與中介軟體
app.post('/webhook', line.middleware(config), (req, res) => {
  Promise
    .all(req.body.events.map(handleEvent))
    .then((result) => res.json(result))
    .catch((err) => {
      console.error(err);
      res.status(500).end();
    });
});

// 事件處理函式
function handleEvent(event: line.WebhookEvent) {
  if (event.type !== 'message' || event.message.type !== 'text') {
    return Promise.resolve(null);
  }

  // 建立回應訊息
  const echo = { type: 'text', text: event.message.text };

  // 使用 reply API
  return client.replyMessage({
    replyToken: event.replyToken,
    messages: [echo],
  });
}

// 啟動伺服器
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`listening on ${port}`);
});
```

### Carousel Template 訊息範例

```typescript
import { TemplateMessage } from '@line/bot-sdk';

const carouselMessage: TemplateMessage = {
  type: "template",
  altText: "書籍查詢結果",
  template: {
    type: "carousel",
    columns: [
      {
        title: "書名範例",
        text: "館藏地：總館\n位置：A1-23\n庫存：5 本",
        actions: [
          {
            type: "uri",
            label: "查看詳情",
            uri: "https://example.com/book/123"
          },
          {
            type: "message",
            label: "借閱",
            text: "我要借這本書"
          }
        ]
      }
    ]
  }
};
```

## Google Gemini AI Function Calling

### 基本 Function Calling 設定

```typescript
import { GoogleGenAI, FunctionDeclaration, Type, FunctionCallingConfigMode } from '@google/genai';

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

// 定義函式聲明
const searchBooksInDatabase: FunctionDeclaration = {
  name: 'searchBooksInDatabase',
  description: '在書庫資料庫中搜尋書籍，支援書名、作者、關鍵字查詢',
  parameters: {
    type: Type.OBJECT,
    properties: {
      query: {
        type: Type.STRING,
        description: '搜尋關鍵字，可以是書名、作者名或相關主題'
      },
      limit: {
        type: Type.NUMBER,
        description: '最多回傳幾筆結果，預設 10'
      }
    },
    required: ['query']
  }
};
```

## 重要注意事項

### LINE Middleware 順序
- LINE middleware 必須在其他 body parser **之前**應用
- 只應用於 webhook 路由，不要全域應用

### Gemini API 最佳實踐
- 使用 `ai.models.generateContent()` 而非舊版的 `model.generateContent()`
- Function Calling 使用 `FunctionCallingConfigMode.AUTO` 讓模型自動決定是否呼叫函式
- System Instruction 應該清楚說明 AI 的角色和回應風格

### 錯誤處理
- 錯誤處理 middleware 必須有 4 個參數：`(err, req, res, next)`
- 錯誤處理 middleware 必須放在所有其他 middleware 之後
- 特別處理 `SignatureValidationFailed` 和 `JSONParseError`