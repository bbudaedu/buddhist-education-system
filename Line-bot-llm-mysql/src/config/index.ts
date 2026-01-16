import dotenv from 'dotenv';

// 載入環境變數
dotenv.config();

// LINE 配置介面
export interface LineConfig {
  channelSecret: string;
  channelAccessToken: string;
}

// Gemini AI 配置介面
export interface GeminiConfig {
  apiKey: string;
  model: string;
  maxOutputTokens: number;
  temperature: number;
}

// 資料庫配置介面
export interface DatabaseConfig {
  host: string;
  port: number;
  user: string;
  password: string;
  database: string;
}

// 伺服器配置介面
export interface ServerConfig {
  port: number;
  nodeEnv: string;
}

// LIFF 配置介面（可選）
export interface LiffConfig {
  liffId: string;
  liffUrl?: string;
}

// 通知管道可用性配置介面
export interface NotificationChannelsConfig {
  lineEnabled: boolean;      // LINE 推播是否可用
  emailEnabled: boolean;     // Email 通知是否可用
  webpushEnabled: boolean;   // 桌面通知是否可用
}

// 通知系統配置介面
export interface NotificationConfig {
  maxRecipientsPerBatch: number;
  deliveryTimeoutMs: number;
  maxBooksPerMessage: number;
  enableRichMessages: boolean;
  retryFailedDeliveries: boolean;
  maxDeliveryRetries: number;
  deliveryRetryDelayMinutes: number;
}

// 排程器配置介面
export interface SchedulerConfig {
  dailyExecutionTime: string;
  maxRetries: number;
  retryDelayMinutes: number;
  timeZone: string;
  ebookProcessorPath: string;
  pythonExecutable: string;
  outputDataPath: string;
  enabled: boolean;
}

// 新書排程器配置介面
export interface NewBookSchedulerConfig {
  enabled: boolean;
  cronExpression: string;       // cron 表達式，例如 '0 9 * * *' (每天 09:00)
  scriptPath: string;           // Python 腳本路徑
  checkOnly: boolean;           // 是否僅檢查不處理
  timeoutMs: number;            // 執行超時時間 (毫秒)
  runOnInit: boolean;           // 是否在啟動時立即執行
}

// 主配置介面
export interface Config {
  line: LineConfig;
  gemini: GeminiConfig;
  database: DatabaseConfig;
  server: ServerConfig;
  scheduler: SchedulerConfig;
  newBookScheduler: NewBookSchedulerConfig;
  notifications: NotificationConfig;
  notificationChannels: NotificationChannelsConfig;
  liff?: LiffConfig;
}

// 環境變數驗證函式
function validateRequiredEnvVars(): void {
  const requiredVars = [
    'LINE_CHANNEL_SECRET',
    'LINE_CHANNEL_ACCESS_TOKEN',
    'GEMINI_API_KEY',
    'DB_HOST',
    'DB_USER',
    'DB_PASSWORD',
    'DB_NAME'
  ];

  const missingVars = requiredVars.filter(varName => !process.env[varName]);

  if (missingVars.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missingVars.join(', ')}\n` +
      'Please check your .env file and ensure all required variables are set.'
    );
  }
}

// 通知系統配置驗證函式
function validateNotificationConfig(config: NotificationConfig): void {
  const errors: string[] = [];

  if (config.maxRecipientsPerBatch <= 0) {
    errors.push('NOTIFICATION_MAX_RECIPIENTS_PER_BATCH must be greater than 0');
  }

  if (config.deliveryTimeoutMs <= 0) {
    errors.push('NOTIFICATION_DELIVERY_TIMEOUT_MS must be greater than 0');
  }

  if (config.maxBooksPerMessage <= 0) {
    errors.push('NOTIFICATION_MAX_BOOKS_PER_MESSAGE must be greater than 0');
  }

  if (config.maxDeliveryRetries < 0) {
    errors.push('NOTIFICATION_MAX_DELIVERY_RETRIES must be 0 or greater');
  }

  if (config.deliveryRetryDelayMinutes <= 0) {
    errors.push('NOTIFICATION_DELIVERY_RETRY_DELAY_MINUTES must be greater than 0');
  }

  if (errors.length > 0) {
    throw new Error(
      `Invalid notification configuration:\n${errors.join('\n')}`
    );
  }
}

// 排程器配置驗證函式
function validateSchedulerConfig(config: SchedulerConfig): void {
  const errors: string[] = [];

  // 驗證時間格式 (HH:MM)
  const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
  if (!timeRegex.test(config.dailyExecutionTime)) {
    errors.push('SCHEDULER_DAILY_TIME must be in HH:MM format (e.g., 02:00)');
  }

  if (config.maxRetries < 0) {
    errors.push('SCHEDULER_MAX_RETRIES must be 0 or greater');
  }

  if (config.retryDelayMinutes <= 0) {
    errors.push('SCHEDULER_RETRY_DELAY_MINUTES must be greater than 0');
  }

  if (!config.ebookProcessorPath) {
    errors.push('EBOOK_PROCESSOR_PATH cannot be empty');
  }

  if (!config.pythonExecutable) {
    errors.push('PYTHON_EXECUTABLE cannot be empty');
  }

  if (!config.outputDataPath) {
    errors.push('EBOOK_OUTPUT_PATH cannot be empty');
  }

  if (errors.length > 0) {
    throw new Error(
      `Invalid scheduler configuration:\n${errors.join('\n')}`
    );
  }
}

// 數值環境變數解析輔助函式
function parseIntEnv(value: string | undefined, defaultValue: number): number {
  if (!value) return defaultValue;
  const parsed = parseInt(value, 10);
  return isNaN(parsed) ? defaultValue : parsed;
}

function parseFloatEnv(value: string | undefined, defaultValue: number): number {
  if (!value) return defaultValue;
  const parsed = parseFloat(value);
  return isNaN(parsed) ? defaultValue : parsed;
}

// 配置物件建立函式
function createConfig(): Config {
  // 驗證必要環境變數
  validateRequiredEnvVars();

  const config: Config = {
    line: {
      channelSecret: process.env.LINE_CHANNEL_SECRET!,
      channelAccessToken: process.env.LINE_CHANNEL_ACCESS_TOKEN!
    },
    gemini: {
      apiKey: process.env.GEMINI_API_KEY!,
      model: process.env.GEMINI_MODEL || 'gemini-2.5-pro',
      maxOutputTokens: parseIntEnv(process.env.GEMINI_MAX_OUTPUT_TOKENS, 1024),
      temperature: parseFloatEnv(process.env.GEMINI_TEMPERATURE, 0.7)
    },
    database: {
      host: process.env.DB_HOST!,
      port: parseIntEnv(process.env.DB_PORT, 3306),
      user: process.env.DB_USER!,
      password: process.env.DB_PASSWORD!,
      database: process.env.DB_NAME!
    },
    server: {
      port: parseIntEnv(process.env.PORT, 3000),
      nodeEnv: process.env.NODE_ENV || 'development'
    },
    scheduler: {
      dailyExecutionTime: process.env.SCHEDULER_DAILY_TIME || '02:00',
      maxRetries: parseIntEnv(process.env.SCHEDULER_MAX_RETRIES, 3),
      retryDelayMinutes: parseIntEnv(process.env.SCHEDULER_RETRY_DELAY_MINUTES, 30),
      timeZone: process.env.SCHEDULER_TIMEZONE || 'Asia/Taipei',
      ebookProcessorPath: process.env.EBOOK_PROCESSOR_PATH || '../ebook/main_processor.py',
      pythonExecutable: process.env.PYTHON_EXECUTABLE || 'python',
      outputDataPath: process.env.EBOOK_OUTPUT_PATH || '../ebook/generated_documents',
      enabled: process.env.SCHEDULER_ENABLED !== 'false' // 預設啟用，除非明確設為 false
    },
    // 新書排程器配置
    newBookScheduler: {
      enabled: process.env.NEWBOOK_SCHEDULER_ENABLED !== 'false',  // 預設啟用
      cronExpression: process.env.NEWBOOK_CRON_EXPRESSION || '0 9 * * *', // 每天 09:00
      scriptPath: process.env.NEWBOOK_SCRIPT_PATH || '../ebook/run_newbook_scheduler.py',
      checkOnly: process.env.NEWBOOK_CHECK_ONLY === 'true',  // 預設執行完整處理
      timeoutMs: parseIntEnv(process.env.NEWBOOK_TIMEOUT_MS, 300000),  // 5 分鐘超時
      runOnInit: process.env.NEWBOOK_RUN_ON_INIT === 'true'   // 是否在啟動時立即執行
    },
    notifications: {
      maxRecipientsPerBatch: parseIntEnv(process.env.NOTIFICATION_MAX_RECIPIENTS_PER_BATCH, 100),
      deliveryTimeoutMs: parseIntEnv(process.env.NOTIFICATION_DELIVERY_TIMEOUT_MS, 30000),
      maxBooksPerMessage: parseIntEnv(process.env.NOTIFICATION_MAX_BOOKS_PER_MESSAGE, 5),
      enableRichMessages: process.env.NOTIFICATION_ENABLE_RICH_MESSAGES !== 'false',
      retryFailedDeliveries: process.env.NOTIFICATION_RETRY_FAILED_DELIVERIES !== 'false',
      maxDeliveryRetries: parseIntEnv(process.env.NOTIFICATION_MAX_DELIVERY_RETRIES, 3),
      deliveryRetryDelayMinutes: parseIntEnv(process.env.NOTIFICATION_DELIVERY_RETRY_DELAY_MINUTES, 15)
    },
    // 通知管道可用性配置（控制學員中心顯示哪些選項）
    notificationChannels: {
      lineEnabled: process.env.NOTIFICATION_LINE_ENABLED === 'true',       // LINE 推播，預設關閉
      emailEnabled: process.env.NOTIFICATION_EMAIL_ENABLED !== 'false',    // Email 通知，預設開啟
      webpushEnabled: process.env.NOTIFICATION_WEBPUSH_ENABLED === 'true'  // 桌面通知，預設關閉
    }
  };

  // 可選的 LIFF 配置
  if (process.env.LIFF_ID) {
    config.liff = {
      liffId: process.env.LIFF_ID,
      ...(process.env.LIFF_URL && { liffUrl: process.env.LIFF_URL })
    };
  }

  // 驗證配置
  validateSchedulerConfig(config.scheduler);
  validateNotificationConfig(config.notifications);

  return config;
}

// 匯出配置物件
export const config = createConfig();

// 匯出個別配置區塊以便使用
export const lineConfig = config.line;
export const geminiConfig = config.gemini;
export const databaseConfig = config.database;
export const serverConfig = config.server;
export const schedulerConfig = config.scheduler;
export const newBookSchedulerConfig = config.newBookScheduler;
export const notificationConfig = config.notifications;
export const notificationChannelsConfig = config.notificationChannels;
export const liffConfig = config.liff;

// 預設匯出
export default config;