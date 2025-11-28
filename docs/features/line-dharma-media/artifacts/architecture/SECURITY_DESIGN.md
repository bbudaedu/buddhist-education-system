# LINE Dharma Media - 安全設計指南

**Version**: 1.0  
**Date**: 2025-11-21  
**Security Architect**: Tech Team

---

## 1. 概述

本文檔定義LINE Dharma Media功能的安全設計規範,涵蓋認證、授權、資料保護、API安全等面向。

---

## 2. 威脅模型

### 2.1 潛在威脅

| ID | 威脅 | 影響 | 可能性 | 風險等級 |
|----|------|------|--------|----------|
| T01 | 未授權API存取 | High | Medium | **High** |
| T02 | SQL注入攻擊 | High | Low | **Medium** |
| T03 | XSS攻擊 | Medium | Medium | **Medium** |
| T04 | 爬蟲資料污染 | Medium | Low | **Low** |
| T05 | DDoS攻擊 | Medium | Medium | **Medium** |
| T06 | 敏感資料洩露 | High | Low | **Medium** |

---

## 3. API安全

### 3.1 Sync API認證

#### 3.1.1 API Key管理

**生成**:
```bash
# 生成256-bit隨機密鑰
openssl rand -hex 32

# 輸出範例: 3f8a9c2d1e4b6f7a9c8e2d4b6f8a9c3e...
```

**儲存**:
```bash
# .env (NOT committed to git)
SYNC_API_KEY=3f8a9c2d1e4b6f7a9c8e2d4b6f8a9c3e...

# Python scraper.env
NODE_API_URL=https://your-domain.com/api/sync/dharma-books
NODE_API_KEY=3f8a9c2d1e4b6f7a9c8e2d4b6f8a9c3e...
```

**驗證**:
```typescript
// middleware/syncAuth.ts
import crypto from 'crypto';

export function verifySyncApiKey(req, res, next) {
  const authHeader = req.headers['authorization'];
  const providedKey = authHeader?.replace('Bearer ', '');
  const validKey = process.env.SYNC_API_KEY;
  
  // Timing-safe comparison to prevent timing attacks
  if (!providedKey || !crypto.timingSafeEqual(
    Buffer.from(providedKey),
    Buffer.from(validKey)
  )) {
    logger.warn('Unauthorized sync attempt', {
      ip: req.ip,
      userAgent: req.get('user-agent')
    });
    
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid or missing API key'
    });
  }
  
  next();
}
```

**輪換策略**:
- 定期輪換: 每90天
- 緊急輪換: 懷疑洩露時立即執行
- 輪換步驟:
  1. 生成新Key
  2. 更新Node.js環境變數
  3. 更新Python爬蟲配置
  4. 驗證新Key可用
  5. 移除舊Key

---

### 3.2 Rate Limiting

#### 3.2.1 實作

```typescript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import Redis from 'ioredis';

// Sync API限制
const syncLimiter = rateLimit({
  store: new RedisStore({
    client: new Redis(process.env.REDIS_URL)
  }),
  windowMs: 60 * 1000,        // 1分鐘
  max: 5,                      // 最多5次請求
  message: {
    error: 'Too many sync requests',
    retryAfter: 60
  },
  standardHeaders: true,       // 返回 RateLimit-* headers
  legacyHeaders: false,
  keyGenerator: (req) => {
    // 基於API Key限制 (而非IP)
    return req.headers['authorization'] || req.ip;
  }
});

app.post('/api/sync/dharma-books', syncLimiter, verifySyncApiKey, ...);
```

#### 3.2.2 LINE Bot使用者限流

```typescript
const userCommandLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10,                     // 每用戶每分鐘10次
  keyGenerator: (req) => {
    // 從LINE event取得userId
    return req.body.events[0]?.source?.userId || req.ip;
  },
  handler: (req, res) => {
    // 達到限制時,回傳友善訊息
    const userId = req.body.events[0]?.source?.userId;
    client.replyMessage(req.body.events[0].replyToken, {
      type: 'text',
      text: '請求過於頻繁,請稍後再試 🙏'
    });
  }
});
```

---

### 3.3 HTTPS強制

```typescript
// Production環境強制HTTPS
if (process.env.NODE_ENV === 'production') {
  app.use((req, res, next) => {
    if (req.header('x-forwarded-proto') !== 'https') {
      return res.redirect(301, `https://${req.header('host')}${req.url}`);
    }
    next();
  });
}

// HSTS Header
app.use((req, res, next) => {
  res.setHeader(
    'Strict-Transport-Security',
    'max-age=31536000; includeSubDomains; preload'
  );
  next();
});
```

---

## 4. 資料安全

### 4.1 SQL注入防護

#### 4.1.1 參數化查詢

```typescript
// ❌ 錯誤 - 易受SQL注入攻擊
const books = await db.query(`
  SELECT * FROM dharma_books WHERE title LIKE '%${userInput}%'
`);

// ✅ 正確 - 參數化查詢
const books = await db.query(`
  SELECT * FROM dharma_books WHERE title LIKE ?
`, [`%${userInput}%`]);
```

#### 4.1.2 ORM使用

```typescript
// 使用Query Builder避免手寫SQL
import { knex } from './db';

const books = await knex('dharma_books')
  .where('title', 'like', `%${userInput}%`)
  .orderBy('publish_date', 'desc')
  .limit(5);
```

---

### 4.2 輸入驗證

#### 4.2.1 Schema驗證

```typescript
import Joi from 'joi';

const syncBooksSchema = Joi.object({
  books: Joi.array().items(
    Joi.object({
      title: Joi.string().trim().max(255).required(),
      author: Joi.string().trim().max(255).allow('', null),
      coverUrl: Joi.string().uri().allow('', null),
      pdfUrl: Joi.string().uri().required(),
      detailUrl: Joi.string().uri().required(),
      publishDate: Joi.date().iso().max('now')
    })
  ).min(1).max(100).required(),
  syncedAt: Joi.date().iso().required()
});

// Middleware
function validateSyncBooks(req, res, next) {
  const { error, value } = syncBooksSchema.validate(req.body, {
    abortEarly: false,
    stripUnknown: true
  });
  
  if (error) {
    return res.status(400).json({
      error: 'Validation failed',
      details: error.details.map(d => ({
        field: d.path.join('.'),
        message: d.message
      }))
    });
  }
  
  req.validatedBody = value;
  next();
}
```

#### 4.2.2 XSS防護

```typescript
import DOMPurify from 'isomorphic-dompurify';

function sanitizeHtml(input: string): string {
  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS: [],        // 不允許任何HTML標籤
    ALLOWED_ATTR: []
  });
}

// 使用
const safeTitle = sanitizeHtml(book.title);
```

---

### 4.3 敏感資料保護

#### 4.3.1 環境變數加密

```typescript
// 生產環境使用Secrets Manager
import { SecretsManager } from '@aws-sdk/client-secrets-manager';

const secretsManager = new SecretsManager({ region: 'ap-northeast-1' });

async function getSecret(secretName: string): Promise<string> {
  const data = await secretsManager.getSecretValue({ SecretId: secretName });
  return data.SecretString;
}

// 使用
const apiKey = await getSecret('line-bot/sync-api-key');
```

#### 4.3.2 日誌脫敏

```typescript
import winston from 'winston';

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.printf(({ level, message, timestamp, ...meta }) => {
      // 移除敏感欄位
      const sanitized = JSON.stringify(meta, (key, value) => {
        if (['password', 'apiKey', 'token', 'authorization'].includes(key)) {
          return '***REDACTED***';
        }
        return value;
      });
      
      return `${timestamp} [${level}]: ${message} ${sanitized}`;
    })
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/app.log' })
  ]
});
```

---

## 5. 外部API安全

### 5.1 Activity API調用

```typescript
import https from 'https';
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://publish.budaedu.org/activity/public/api',
  timeout: 5000,
  
  // SSL憑證驗證
  httpsAgent: new https.Agent({
    rejectUnauthorized: process.env.NODE_ENV === 'production',
    minVersion: 'TLSv1.2'  // 強制最低TLS 1.2
  }),
  
  // 請求攔截器
  validateStatus: (status) => status >= 200 && status < 500,
  
  // 回應攔截器
  interceptors: {
    response: {
      use: (response) => {
        // 驗證Content-Type
        if (!response.headers['content-type']?.includes('application/json')) {
          throw new Error('Unexpected content type');
        }
        return response;
      },
      error: (error) => {
        logger.error('Activity API error', {
          url: error.config?.url,
          status: error.response?.status,
          message: error.message
        });
        throw error;
      }
    }
  }
});
```

### 5.2 Response驗證

```typescript
import Joi from 'joi';

const activityEventSchema = Joi.object({
  data: Joi.array().items(
    Joi.object({
      id: Joi.number().required(),
      name: Joi.string().required(),
      leader: Joi.string().allow('', null),
      start_date: Joi.string().isoDate().required(),
      // ... 其他欄位
    })
  ).required()
});

async function fetchEvents() {
  const response = await apiClient.get('/events');
  
  // 驗證回應格式
  const { error, value } = activityEventSchema.validate(response.data);
  if (error) {
    throw new ServiceError('Invalid API response format');
  }
  
  return value.data;
}
```

---

## 6. LINE Messaging API安全

### 6.1 Webhook簽名驗證

```typescript
import crypto from 'crypto';

function verifyLineSignature(req: Request): boolean {
  const channelSecret = process.env.LINE_CHANNEL_SECRET;
  const signature = req.headers['x-line-signature'] as string;
  const body = JSON.stringify(req.body);
  
  const hash = crypto
    .createHmac('SHA256', channelSecret)
    .update(body)
    .digest('base64');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(hash)
  );
}

// Middleware
app.post('/webhook', (req, res, next) => {
  if (!verifyLineSignature(req)) {
    logger.warn('Invalid LINE signature', { ip: req.ip });
    return res.status(401).send('Unauthorized');
  }
  next();
});
```

---

## 7. 爬蟲安全

### 7.1 防止資料污染

```typescript
// Python爬蟲端
import hashlib
import json

def generate_data_signature(books: list) -> str:
    """生成資料簽章"""
    data_str = json.dumps(books, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()

# 發送時附帶簽章
payload = {
    'books': books,
    'syncedAt': datetime.now().isoformat(),
    'signature': generate_data_signature(books)
}
```

```typescript
// Node.js接收端
function verifyDataSignature(books: any[], signature: string): boolean {
  const dataStr = JSON.stringify(books, Object.keys(books).sort());
  const hash = crypto.createHash('sha256').update(dataStr).digest('hex');
  return hash === signature;
}
```

### 7.2 爬蟲使用者代理

```python
# 避免被封鎖
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...',
]

import random
driver.execute_cdp_cmd('Network.setUserAgentOverride', {
    'userAgent': random.choice(USER_AGENTS)
})
```

---

## 8. 監控與稽核

### 8.1 安全事件日誌

```typescript
// 記錄所有安全相關事件
logger.security = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'dharma-media-security' },
  transports: [
    new winston.transports.File({ 
      filename: 'logs/security.log',
      maxsize: 10485760,  // 10MB
      maxFiles: 30
    })
  ]
});

// 記錄可疑活動
logger.security.warn('Failed authentication attempt', {
  ip: req.ip,
  userAgent: req.get('user-agent'),
  endpoint: req.path,
  timestamp: new Date().toISOString()
});
```

### 8.2 告警規則

```yaml
# Prometheus Alert Rules
groups:
  - name: dharma_media_security
    rules:
      - alert: HighFailedAuthRate
        expr: rate(failed_auth_attempts_total[5m]) > 10
        for: 5m
        annotations:
          summary: "High failed authentication rate"
          
      - alert: UnexpectedAPIUsage
        expr: rate(sync_api_calls_total[1h]) > 100
        annotations:
          summary: "Sync API called more than expected"
```

---

## 9. Compliance

### 9.1 資料保護法規

**GDPR適用性評估**:
- ❌ 不處理歐盟用戶個人資料
- ✅ LINE userId為匿名識別符
- ✅ 訂閱資料僅用於通知功能

**台灣個資法**:
- 僅收集LINE userId (非真實姓名)
- 用途明確 (訂閱通知)
- 提供取消訂閱機制

---

## 10. 安全檢查清單

### 部署前檢查

- [ ] 所有環境變數已加密儲存
- [ ] 生產環境開啟HTTPS
- [ ] API Key已生成並安全儲存
- [ ] Rate Limiting已配置
- [ ] SQL查詢全部參數化
- [ ] 輸入驗證已實作
- [ ] LINE Webhook簽名驗證已啟用
- [ ] 日誌不包含敏感資訊
- [ ] 安全告警已配置
- [ ] 備份策略已建立

### 定期審查

- [ ] API Key輪換 (每90天)
- [ ] 依賴套件更新 (`npm audit`)
- [ ] 安全日誌審查 (每週)
- [ ] 滲透測試 (每季)

---

**安全負責人**: Tech Lead  
**最後更新**: 2025-11-21  
**下次審查**: 2025-12-21
