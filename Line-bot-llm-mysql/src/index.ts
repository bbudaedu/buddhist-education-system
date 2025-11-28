import express from 'express';
import cors from 'cors';
import { serverConfig, schedulerConfig } from './config/index';
import { webhookHandler } from './handlers/webhookHandler';
import { getSchedulerInstance } from './services/dailySchedulerService';
import { healthMonitoringService } from './services/healthMonitoringService';
import { adminDashboardService } from './services/adminDashboardService';

/**
 * LINE Book Query Bot - Express Server
 * 智能書庫查詢機器人主程式
 */

// 建立 Express 應用程式
const app = express();

// 設定 CORS middleware
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? ['https://liff.line.me'] // 生產環境只允許 LINE LIFF
    : true, // 開發環境允許所有來源
  credentials: true
}));

// 設定 JSON body parser middleware（但不應用於 webhook 路由）
app.use((req, res, next) => {
  if (req.path === '/webhook') {
    // webhook 路由使用 LINE SDK 的 middleware 處理 body parsing
    next();
  } else {
    // 其他路由使用標準的 JSON parser
    express.json()(req, res, next);
  }
});

// 基本健康檢查端點（快速檢查）
app.get('/health', async (_req, res) => {
  try {
    // 測試資料庫連線
    const { databaseService } = await import('./services/databaseService');
    const dbConnected = await databaseService.testConnection();
    
    res.json({
      status: dbConnected ? 'ok' : 'degraded',
      timestamp: new Date().toISOString(),
      service: 'LINE Book Query Bot',
      version: process.env.npm_package_version || '1.0.0',
      database: dbConnected ? 'connected' : 'disconnected'
    });
  } catch (error) {
    res.status(503).json({
      status: 'error',
      timestamp: new Date().toISOString(),
      service: 'LINE Book Query Bot',
      version: process.env.npm_package_version || '1.0.0',
      database: 'error',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 詳細系統健康檢查端點
app.get('/health/detailed', async (_req, res) => {
  try {
    const healthStatus = await healthMonitoringService.performHealthCheck();
    
    const httpStatus = healthStatus.status === 'healthy' ? 200 : 
                      healthStatus.status === 'degraded' ? 200 : 503;
    
    res.status(httpStatus).json(healthStatus);
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date(),
      error: error instanceof Error ? error.message : 'Health check failed',
      services: {},
      metrics: {
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage(),
        processingStats: {
          totalNotificationsSent: 0,
          totalSubscribers: 0,
          errorRate: 0
        }
      }
    });
  }
});

// 系統指標端點
app.get('/health/metrics', async (_req, res) => {
  try {
    const lastHealthCheck = healthMonitoringService.getLastHealthCheck();
    
    if (!lastHealthCheck) {
      // 如果沒有最近的健康檢查，執行一次
      const healthStatus = await healthMonitoringService.performHealthCheck();
      return res.json({
        metrics: healthStatus.metrics,
        timestamp: healthStatus.timestamp
      });
    }
    
    return res.json({
      metrics: lastHealthCheck.metrics,
      timestamp: lastHealthCheck.timestamp,
      cacheAge: Date.now() - lastHealthCheck.timestamp.getTime()
    });
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to get system metrics',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 根路徑端點
app.get('/', (_req, res) => {
  res.json({
    message: 'LINE Book Query Bot API',
    status: 'running',
    endpoints: {
      // Health endpoints
      health: '/health (GET)',
      healthDetailed: '/health/detailed (GET)',
      healthMetrics: '/health/metrics (GET)',
      
      // Core functionality
      webhook: '/webhook (POST)',
      
      // Scheduler management
      scheduler: '/admin/scheduler (GET)',
      manualTrigger: '/admin/scheduler/trigger (POST)',
      processFile: '/admin/scheduler/process-file (POST)',
      
      // Statistics and monitoring
      subscriptionStats: '/admin/stats/subscriptions (GET)',
      deliveryStats: '/admin/stats/deliveries (GET)',
      systemStatus: '/admin/status (GET)',
      performance: '/admin/performance (GET)',
      
      // Administrative actions
      manualNotificationTrigger: '/admin/notifications/trigger (POST)',
      auditLog: '/admin/audit (GET)',
      auditCleanup: '/admin/audit/cleanup (POST)',
      
      // Website monitoring notifications
      websiteMonitoringNotification: '/api/notifications/website-monitoring (POST)',
      testNotification: '/api/notifications/test (POST)',
      notificationHealth: '/api/notifications/health (GET)'
    },
    documentation: {
      healthCheck: 'Use /health for basic status, /health/detailed for comprehensive system health',
      administration: 'Admin endpoints require proper authentication in production',
      monitoring: 'Statistics endpoints provide real-time system metrics'
    }
  });
});

// 管理端點 - 排程器狀態
app.get('/admin/scheduler', (_req, res) => {
  try {
    if (!schedulerConfig.enabled) {
      return res.json({
        enabled: false,
        message: 'Scheduler is disabled'
      });
    }

    const scheduler = getSchedulerInstance();
    const status = scheduler.getStatus();
    
    return res.json({
      enabled: true,
      ...status,
      config: {
        dailyExecutionTime: schedulerConfig.dailyExecutionTime,
        timeZone: schedulerConfig.timeZone,
        maxRetries: schedulerConfig.maxRetries,
        retryDelayMinutes: schedulerConfig.retryDelayMinutes
      }
    });
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to get scheduler status',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 管理端點 - 手動觸發處理
app.post('/admin/scheduler/trigger', async (_req, res) => {
  try {
    if (!schedulerConfig.enabled) {
      return res.status(400).json({
        error: 'Scheduler is disabled',
        message: 'Cannot trigger processing when scheduler is disabled'
      });
    }

    const scheduler = getSchedulerInstance();
    const result = await scheduler.manualTrigger();
    
    return res.json({
      message: 'Manual trigger completed',
      result
    });
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to trigger manual processing',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 管理端點 - 手動處理指定檔案
app.post('/admin/scheduler/process-file', async (req, res) => {
  try {
    if (!schedulerConfig.enabled) {
      return res.status(400).json({
        error: 'Scheduler is disabled',
        message: 'Cannot process files when scheduler is disabled'
      });
    }

    const { filePath } = req.body;
    if (!filePath) {
      return res.status(400).json({
        error: 'Missing file path',
        message: 'Please provide a filePath in the request body'
      });
    }

    const scheduler = getSchedulerInstance();
    await scheduler.processOutputFileManually(filePath);
    
    return res.json({
      message: 'File processed successfully',
      filePath
    });
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to process file',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 管理端點 - 訂閱統計
app.get('/admin/stats/subscriptions', async (_req, res) => {
  try {
    const stats = await adminDashboardService.getSubscriptionStats();
    return res.json(stats);
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to get subscription statistics',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 管理端點 - 通知投遞統計
app.get('/admin/stats/deliveries', async (_req, res) => {
  try {
    const stats = await adminDashboardService.getDeliveryStats();
    return res.json(stats);
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to get delivery statistics',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 管理端點 - 系統狀態總覽
app.get('/admin/status', async (_req, res) => {
  try {
    const status = await adminDashboardService.getSystemStatusOverview();
    return res.json(status);
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to get system status',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 管理端點 - 效能摘要
app.get('/admin/performance', async (_req, res) => {
  try {
    const performance = await adminDashboardService.getPerformanceSummary();
    return res.json(performance);
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to get performance summary',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 管理端點 - 手動觸發通知（增強版）
app.post('/admin/notifications/trigger', async (req, res) => {
  try {
    const { triggeredBy = 'Admin API', testData } = req.body;
    const result = await adminDashboardService.triggerManualNotification(triggeredBy, testData);
    
    const httpStatus = result.success ? 200 : 500;
    return res.status(httpStatus).json(result);
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: error instanceof Error ? error.message : 'Unknown error',
      startTime: new Date()
    });
  }
});

// 管理端點 - 審計日誌
app.get('/admin/audit', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit as string) || 50;
    const auditLog = adminDashboardService.getAuditLog(limit);
    
    return res.json({
      entries: auditLog,
      total: auditLog.length,
      limit
    });
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to get audit log',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 管理端點 - 清理舊審計記錄
app.post('/admin/audit/cleanup', async (req, res) => {
  try {
    const { daysOld = 30 } = req.body;
    const removedCount = adminDashboardService.clearOldAuditEntries(daysOld);
    
    return res.json({
      message: 'Audit cleanup completed',
      removedEntries: removedCount,
      daysOld
    });
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to cleanup audit log',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// 網站監控通知 API 端點
import {
  handleWebsiteMonitoringNotification,
  handleTestNotification,
  handleHealthCheck as handleNotificationHealthCheck,
} from './handlers/notificationHandler';

// 接收來自 Python 的網站監控通知
app.post('/api/notifications/website-monitoring', handleWebsiteMonitoringNotification);

// 發送測試通知
app.post('/api/notifications/test', handleTestNotification);

// 通知服務健康檢查
app.get('/api/notifications/health', handleNotificationHealthCheck);

// 註冊 LINE Webhook 路由
// 注意：LINE middleware 必須在 webhook 路由之前應用
app.post('/webhook', 
  webhookHandler.getMiddleware(), // LINE SDK middleware 用於簽章驗證和 body parsing
  webhookHandler.handleWebhook.bind(webhookHandler) // Webhook 處理器
);

// 404 處理
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.originalUrl} not found`,
    availableRoutes: ['GET /', 'GET /health', 'POST /webhook']
  });
});

// 錯誤處理 middleware（必須有 4 個參數且放在最後）
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error('Express error handler:', err);

  // LINE SDK 特定錯誤處理
  if (err.name === 'SignatureValidationFailed') {
    return res.status(401).json({
      error: 'Signature validation failed',
      message: 'Invalid LINE signature'
    });
  }

  if (err.name === 'JSONParseError') {
    return res.status(400).json({
      error: 'Invalid JSON',
      message: 'Request body contains invalid JSON'
    });
  }

  // 一般錯誤處理
  const isDevelopment = serverConfig.nodeEnv === 'development';
  
  return res.status(500).json({
    error: 'Internal Server Error',
    message: isDevelopment ? err.message : 'Something went wrong',
    ...(isDevelopment && { stack: err.stack })
  });
});

// 啟動伺服器
const port = serverConfig.port;

app.listen(port, async () => {
  console.log(`🚀 LINE Book Query Bot server is running on port ${port}`);
  console.log(`📊 Health check: http://localhost:${port}/health`);
  console.log(`🤖 Webhook endpoint: http://localhost:${port}/webhook`);
  console.log(`🌍 Environment: ${serverConfig.nodeEnv}`);
  
  // 啟動健康監控
  try {
    healthMonitoringService.startMonitoring(60000); // 每分鐘檢查一次
    console.log(`💊 Health monitoring started (60s interval)`);
  } catch (error) {
    console.error('❌ Failed to start health monitoring:', error instanceof Error ? error.message : 'Unknown error');
  }
  
  // 啟動每日排程器（如果啟用）
  // 注意：網站監控由 Python 系統 (ebook/run_daily_monitoring.py) 負責
  // Python 系統會呼叫此 API 來推播通知給訂閱用戶
  if (schedulerConfig.enabled) {
    try {
      const scheduler = getSchedulerInstance();
      await scheduler.start();
      console.log(`📅 Daily scheduler started (${schedulerConfig.dailyExecutionTime} ${schedulerConfig.timeZone})`);
      console.log(`📰 Website monitoring: Handled by Python system (ebook/run_daily_monitoring.py)`);
    } catch (error) {
      console.error('❌ Failed to start daily scheduler:', error instanceof Error ? error.message : 'Unknown error');
    }
  } else {
    console.log('📅 Daily scheduler is disabled');
    console.log('📰 Website monitoring: Handled by Python system (ebook/run_daily_monitoring.py)');
  }
  
  if (serverConfig.nodeEnv === 'development') {
    console.log(`\n📝 Available endpoints:`);
    console.log(`   GET  /                              - API information`);
    console.log(`   GET  /health                        - Basic health check`);
    console.log(`   GET  /health/detailed               - Detailed system health`);
    console.log(`   GET  /health/metrics                - System performance metrics`);
    console.log(`   POST /webhook                       - LINE webhook`);
    console.log(`   GET  /admin/status                  - System status overview`);
    console.log(`   GET  /admin/performance             - Performance summary`);
    console.log(`   GET  /admin/stats/subscriptions     - Subscription statistics`);
    console.log(`   GET  /admin/stats/deliveries        - Delivery statistics`);
    console.log(`   POST /admin/notifications/trigger   - Manual notification trigger`);
    console.log(`   GET  /admin/audit                   - Audit log`);
  }
});

// 優雅關閉處理
process.on('SIGTERM', () => {
  console.log('📴 SIGTERM received, shutting down gracefully...');
  
  // 停止健康監控
  try {
    healthMonitoringService.stopMonitoring();
    console.log('💊 Health monitoring stopped');
  } catch (error) {
    console.error('❌ Error stopping health monitoring:', error instanceof Error ? error.message : 'Unknown error');
  }
  
  // 停止排程器
  if (schedulerConfig.enabled) {
    try {
      const scheduler = getSchedulerInstance();
      scheduler.stop();
      console.log('📅 Daily scheduler stopped');
    } catch (error) {
      console.error('❌ Error stopping scheduler:', error instanceof Error ? error.message : 'Unknown error');
    }
  }
  
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('📴 SIGINT received, shutting down gracefully...');
  
  // 停止健康監控
  try {
    healthMonitoringService.stopMonitoring();
    console.log('💊 Health monitoring stopped');
  } catch (error) {
    console.error('❌ Error stopping health monitoring:', error instanceof Error ? error.message : 'Unknown error');
  }
  
  // 停止排程器
  if (schedulerConfig.enabled) {
    try {
      const scheduler = getSchedulerInstance();
      scheduler.stop();
      console.log('📅 Daily scheduler stopped');
    } catch (error) {
      console.error('❌ Error stopping scheduler:', error instanceof Error ? error.message : 'Unknown error');
    }
  }
  
  process.exit(0);
});

// 未捕獲的異常處理
process.on('uncaughtException', (err) => {
  console.error('💥 Uncaught Exception:', err);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

export default app;