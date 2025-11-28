# LINE Dharma Media - API設計規範

**Version**: 1.0  
**Date**: 2025-11-21  
**Architect**: Backend Team

---

## 1. API Overview

### 1.1 API類型

本專案涉及三類API:

1. **Sync API** (Python → Node.js): 內部API,用於資料同步
2. **External API** (Node.js → budaedu.org): 外部API,獲取影音資料
3. **LINE Messaging API** (Node.js → LINE): 訊息推送API

---

## 2. Sync API設計

### 2.1 POST /api/sync/dharma-books

**用途**: 接收Python爬蟲同步的書籍資料

**Authentication**: Bearer Token

#### Request

```http
POST /api/sync/dharma-books HTTP/1.1
Host: localhost:3000
Content-Type: application/json
Authorization: Bearer {SYNC_API_KEY}

{
  "books": [
    {
      "title": "佛說阿彌陀經",
      "author": "姚秦 鳩摩羅什譯",
      "coverUrl": "https://www.budaedu.org/covers/amitabha.jpg",
      "pdfUrl": "https://www.budaedu.org/pdf/amitabha.pdf",
      "detailUrl": "https://www.budaedu.org/#/dharmas/001",
      "publishDate": "2025-11-20"
    }
  ],
  "syncedAt": "2025-11-21T10:00:00Z"
}
```

#### Response

**Success (200)**:
```json
{
  "success": true,
  "message": "Successfully synced 5 books",
  "data": {
    "insertedCount": 3,
    "updatedCount": 2,
    "totalProcessed": 5
  },
  "timestamp": "2025-11-21T10:00:01.234Z"
}
```

**Error Responses**:

| Code | Description | Example |
|------|-------------|---------|
| 400 | Invalid Request | `{ "error": "Validation failed", "details": [...] }` |
| 401 | Unauthorized | `{ "error": "Invalid or missing API key" }` |
| 429 | Rate Limit Exceeded | `{ "error": "Too many requests", "retryAfter": 60 }` |
| 500 | Server Error | `{ "error": "Database connection failed" }` |

#### Validation Rules

```typescript
interface SyncBooksRequest {
  books: Array<{
    title: string;           // Required, max 255 chars
    author?: string;         // Optional, max 255 chars
    coverUrl?: string;       // Optional, valid URL
    pdfUrl: string;          // Required, valid URL
    detailUrl: string;       // Required, valid URL
    publishDate?: string;    // Optional, ISO 8601 date
  }>;
  syncedAt: string;          // Required, ISO 8601 datetime
}
```

#### Rate Limiting

- **Window**: 1 minute
- **Max Requests**: 5
- **Response Header**: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## 3. External API Integration

### 3.1 GET /activity/public/api/events

**用途**: 獲取影音/直播資料

**Base URL**: `https://publish.budaedu.org/activity/public/api`

#### Request Parameters

```typescript
interface EventsQueryParams {
  filter?: {
    has_live_stream?: boolean;    // 過濾直播
    type?: 'video' | 'live';       // 類型過濾
  };
  include?: string;                // 'organizer,schedules.places'
  sort?: string;                   // '-start_date' (降序)
  per_page?: number;               // 每頁數量 (1-100)
  page?: number;                   // 頁碼
}
```

#### Request Example

```http
GET /activity/public/api/events?filter[has_live_stream]=true&include=organizer,schedules.places&sort=-start_date&per_page=5 HTTP/1.1
Host: publish.budaedu.org
Accept: application/json
```

#### Response

```json
{
  "data": [
    {
      "id": 123,
      "name": "佛學講座：心經導讀",
      "leader": "釋證嚴法師",
      "start_date": "2025-11-25",
      "cover_image": "https://publish.budaedu.org/covers/event123.jpg",
      "has_live_stream": true,
      "organizer": {
        "id": 1,
        "name": "佛陀教育基金會",
        "photo_url": "https://publish.budaedu.org/organizers/1.jpg"
      },
      "schedules": [
        {
          "id": 456,
          "start_time": "14:00:00",
          "end_time": "16:00:00",
          "places": [
            {
              "id": 789,
              "name": "線上會議室",
              "live_streaming_url": "https://youtube.com/watch?v=abc123"
            }
          ]
        }
      ]
    }
  ],
  "meta": {
    "current_page": 1,
    "last_page": 10,
    "per_page": 5,
    "total": 50
  }
}
```

#### Data Mapping

```typescript
// External API → Internal Model
function mapEventToStream(event: ExternalEvent): Stream {
  return {
    id: event.id.toString(),
    title: event.name,
    instructor: event.leader || event.organizer?.name || '未指定',
    instructorPhotoUrl: event.organizer?.photo_url,
    thumbnailUrl: event.cover_image,
    streamDate: new Date(event.start_date),
    streamUrl: event.schedules?.[0]?.places?.[0]?.live_streaming_url || '',
    type: event.has_live_stream ? 'live' : 'video'
  };
}
```

#### Error Handling

```typescript
try {
  const response = await axios.get('/events', {
    params: queryParams,
    timeout: 5000,  // 5秒超時
    httpsAgent: new https.Agent({ 
      rejectUnauthorized: process.env.NODE_ENV === 'production' 
    })
  });
  return response.data;
} catch (error) {
  if (error.code === 'ECONNABORTED') {
    throw new ServiceError('API請求超時', 'TIMEOUT');
  }
  if (error.response?.status === 429) {
    throw new ServiceError('API速率限制', 'RATE_LIMIT');
  }
  throw new ServiceError('無法連接Activity API', 'CONNECTION_ERROR');
}
```

---

## 4. LINE Messaging API Usage

### 4.1 Reply Message with Flex Carousel

```typescript
await client.replyMessage(replyToken, {
  type: 'flex',
  altText: '最新法寶',
  contents: {
    type: 'carousel',
    contents: flexBubbles  // Array<FlexBubble>
  },
  quickReply: {
    items: quickReplyItems
  }
});
```

### 4.2 Quick Reply Structure

```typescript
interface QuickReplyItems {
  items: Array<{
    type: 'action';
    action: {
      type: 'message';
      label: string;      // 按鈕文字
      text: string;       // 發送的訊息
    }
  }>;
}
```

---

## 5. API安全規範

### 5.1 Authentication

#### Sync API

```typescript
// 環境變數
SYNC_API_KEY=<generate_with: openssl rand -hex 32>

// 驗證Middleware
function verifySyncApiKey(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader?.replace('Bearer ', '');
  
  if (!token || token !== process.env.SYNC_API_KEY) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid or missing API key'
    });
  }
  
  next();
}
```

### 5.2 Input Sanitization

```typescript
import Joi from 'joi';
import DOMPurify from 'isomorphic-dompurify';

// Schema驗證
const schema = Joi.object({
  title: Joi.string().trim().max(255).required(),
  pdfUrl: Joi.string().uri().required()
});

// XSS防護
function sanitizeInput(input: string): string {
  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: []
  });
}
```

### 5.3 HTTPS Enforcement

```typescript
// 生產環境強制HTTPS
if (process.env.NODE_ENV === 'production') {
  app.use((req, res, next) => {
    if (req.header('x-forwarded-proto') !== 'https') {
      return res.redirect(301, `https://${req.header('host')}${req.url}`);
    }
    next();
  });
}
```

---

## 6. API Testing

### 6.1 Unit Tests

```typescript
describe('DharmaBookController', () => {
  it('should sync books successfully', async () => {
    const mockBooks = [
      {
        title: 'Test Book',
        author: 'Test Author',
        pdfUrl: 'https://example.com/test.pdf',
        detailUrl: 'https://example.com/detail'
      }
    ];
    
    const response = await request(app)
      .post('/api/sync/dharma-books')
      .set('Authorization', `Bearer ${SYNC_API_KEY}`)
      .send({ books: mockBooks, syncedAt: new Date().toISOString() })
      .expect(200);
    
    expect(response.body.success).toBe(true);
  });
  
  it('should reject invalid API key', async () => {
    await request(app)
      .post('/api/sync/dharma-books')
      .set('Authorization', 'Bearer invalid_key')
      .send({ books: [], syncedAt: new Date().toISOString() })
      .expect(401);
  });
});
```

### 6.2 Integration Tests

```typescript
describe('VideoStreamingService Integration', () => {
  it('should fetch events from Activity API', async () => {
    const service = new VideoStreamingService();
    const streams = await service.getLatestContent();
    
    expect(streams).toBeInstanceOf(Array);
    expect(streams.length).toBeGreaterThan(0);
    expect(streams[0]).toHaveProperty('title');
    expect(streams[0]).toHaveProperty('streamUrl');
  });
});
```

---

## 7. API Versioning

### 7.1 版本策略

**當前**: v1 (無版本前綴)

**未來**: 
- 破壞性變更時引入 `/api/v2/`
- 保持v1向後兼容6個月

### 7.2 棄用流程

1. 在Response Header加入 `X-API-Deprecated: true`
2. 更新文檔標註棄用日期
3. 提前3個月通知客戶端
4. 執行下線

---

## 8. API Documentation

### 8.1 OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: LINE Dharma Media API
  version: 1.0.0
paths:
  /api/sync/dharma-books:
    post:
      summary: Sync dharma books from scraper
      security:
        - BearerAuth: []
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SyncBooksRequest'
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SyncBooksResponse'
```

### 8.2 Interactive Documentation

使用 **Swagger UI** 提供互動式API文檔:

```bash
npm install swagger-ui-express
```

```typescript
import swaggerUi from 'swagger-ui-express';
import swaggerDocument from './openapi.json';

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
```

訪問: `http://localhost:3000/api-docs`

---

**API設計維護**: Backend Engineering Team  
**最後更新**: 2025-11-21
