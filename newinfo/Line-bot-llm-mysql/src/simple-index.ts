import express from 'express';
import cors from 'cors';
import { config } from './config';
import { simpleWebhookHandler } from './handlers/SimpleWebhookHandler';
import { simpleDatabaseService } from './services/SimpleDatabaseService';

/**
 * 簡化版 LINE Book Query Bot 主程式
 * 只包含基本的書籍查詢功能，不需要建立新的資料庫表
 */

const app = express();

// 中介軟體設定
app.use(cors());
app.use(express.json());

// 基本路由
app.get('/', (_req, res) => {
  res.json({
    name: 'LINE Book Query Bot (Simple)',
    version: '1.0.0',
    description: '佛教圖書館查詢機器人 - 簡化版',
    status: 'running',
    features: [
      '書籍搜尋',
      '館藏查詢',
      '庫存確認'
    ],
    endpoints: {
      'GET /': 'API 資訊',
      'GET /health': '健康檢查',
      'GET /stats': '書籍統計',
      'POST /webhook': 'LINE Webhook'
    }
  });
});

// 健康檢查端點
app.get('/health', async (_req, res) => {
  try {
    const dbConnected = await simpleDatabaseService.testConnection();
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      database: dbConnected ? 'connected' : 'disconnected',
      environment: config.server.nodeEnv
    });
  } catch (error) {
    res.status(500).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: 'Database connection failed'
    });
  }
});

// 書籍統計端點
app.get('/stats', async (_req, res) => {
  try {
    const stats = await simpleDatabaseService.getBookStats();
    
    res.json({
      timestamp: new Date().toISOString(),
      books: stats
    });
  } catch (error) {
    res.status(500).json({
      error: 'Failed to get book statistics'
    });
  }
});

// 書籍搜尋 API 端點（可選，用於測試）
app.get('/api/books/search', async (req, res) => {
  try {
    const query = req.query.q as string;
    const limit = parseInt(req.query.limit as string) || 10;
    
    if (!query) {
      res.status(400).json({ error: 'Query parameter "q" is required' });
      return;
    }
    
    const books = await simpleDatabaseService.searchBooks(query, limit);
    
    res.json({
      query,
      results: books.length,
      books
    });
  } catch (error) {
    res.status(500).json({
      error: 'Failed to search books'
    });
  }
});

// LINE Webhook 端點
app.post('/webhook', (req, res) => {
  simpleWebhookHandler.handleWebhook(req, res);
});

// 錯誤處理中介軟體
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error('❌ Unhandled error:', err);
  res.status(500).json({ 
    error: 'Internal server error',
    message: err.message 
  });
});

// 404 處理
app.use((req, res) => {
  res.status(404).json({ 
    error: 'Not found',
    path: req.path 
  });
});

// 啟動伺服器
const port = config.server.port;

async function startServer() {
  try {
    // 測試資料庫連線
    console.log('🔍 Testing database connection...');
    const dbConnected = await simpleDatabaseService.testConnection();
    
    if (!dbConnected) {
      console.error('❌ Database connection failed');
      process.exit(1);
    }
    
    console.log('✅ Database connection successful');
    
    // 啟動 HTTP 伺服器
    app.listen(port, () => {
      console.log(`🚀 LINE Book Query Bot (Simple) is running on port ${port}`);
      console.log(`📊 Health check: http://localhost:${port}/health`);
      console.log(`🤖 Webhook endpoint: http://localhost:${port}/webhook`);
      console.log(`📚 Book search API: http://localhost:${port}/api/books/search?q=佛`);
      console.log(`🌍 Environment: ${config.server.nodeEnv}`);
      console.log(`📁 Database: ${config.database.database}`);
      
      console.log('\n📝 Available endpoints:');
      console.log('GET  /                     - API information');
      console.log('GET  /health               - Health check');
      console.log('GET  /stats                - Book statistics');
      console.log('GET  /api/books/search     - Book search API');
      console.log('POST /webhook              - LINE webhook');
    });
    
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

// 優雅關閉處理
process.on('SIGTERM', async () => {
  console.log('📴 Received SIGTERM, shutting down gracefully...');
  await simpleDatabaseService.closeConnection();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('📴 Received SIGINT, shutting down gracefully...');
  await simpleDatabaseService.closeConnection();
  process.exit(0);
});

// 未捕獲的異常處理
process.on('uncaughtException', (error) => {
  console.error('💥 Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// 啟動應用程式
startServer();