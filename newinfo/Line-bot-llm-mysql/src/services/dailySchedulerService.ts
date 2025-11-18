import { CronJob } from 'cron';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import { schedulerConfig, SchedulerConfig as ConfigSchedulerConfig } from '../config/index';
import { EbookIntegrationService, defaultFileMonitorConfig, ProcessedBookData } from './ebookIntegrationService';
import { errorRecoveryService } from './errorRecoveryService';

/**
 * Daily Scheduler Service
 * 每日排程服務，負責觸發電子書處理和通知發送
 */

export interface SchedulerConfig extends ConfigSchedulerConfig {
  // 繼承配置介面，可以在這裡添加額外的運行時配置
}

export interface ProcessingResult {
  success: boolean;
  processingTime: number;
  booksProcessed: number;
  errorMessage?: string;
  outputFilePath?: string;
}

export class DailySchedulerService {
  private cronJob: CronJob | null = null;
  private retryCronJob: CronJob | null = null;
  private isProcessing = false;
  private retryCount = 0;
  private currentProcess: ChildProcess | null = null;
  private integrationService: EbookIntegrationService;

  constructor(private config: SchedulerConfig = schedulerConfig) {
    this.validateConfig();
    
    // 初始化整合服務
    const integrationConfig = {
      ...defaultFileMonitorConfig,
      watchDirectory: this.config.outputDataPath
    };
    
    this.integrationService = new EbookIntegrationService(integrationConfig);
    this.setupIntegrationEventHandlers();
  }

  /**
   * 驗證配置參數
   */
  private validateConfig(): void {
    if (!this.config.dailyExecutionTime.match(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/)) {
      throw new Error('Invalid dailyExecutionTime format. Expected HH:MM (24-hour format)');
    }

    if (this.config.maxRetries < 0 || this.config.maxRetries > 10) {
      throw new Error('maxRetries must be between 0 and 10');
    }

    if (this.config.retryDelayMinutes < 1 || this.config.retryDelayMinutes > 1440) {
      throw new Error('retryDelayMinutes must be between 1 and 1440 (24 hours)');
    }
  }

  /**
   * 設置整合服務事件處理器
   */
  private setupIntegrationEventHandlers(): void {
    this.integrationService.on('books-processed', async (data: ProcessedBookData, filePath: string) => {
      console.log(`📚 Received processed books from: ${path.basename(filePath)}`);
      console.log(`📊 Books processed: ${data.successfullyProcessed.length}`);
      
      try {
        await this.triggerNotifications(data);
        console.log('✅ Notifications triggered successfully');
      } catch (error) {
        console.error('❌ Failed to trigger notifications:', error instanceof Error ? error.message : 'Unknown error');
      }
    });

    this.integrationService.on('processing-failed', (filePath: string, error: string) => {
      console.error(`❌ Failed to process file: ${path.basename(filePath)} - ${error}`);
    });

    this.integrationService.on('error', (error: Error) => {
      console.error('❌ Integration service error:', error.message);
    });
  }

  /**
   * 啟動每日排程
   */
  public async start(): Promise<void> {
    if (this.cronJob) {
      console.log('📅 Daily scheduler is already running');
      return;
    }

    // 啟動檔案監控服務
    try {
      await this.integrationService.startMonitoring();
      console.log('📁 File monitoring service started');
    } catch (error) {
      console.error('❌ Failed to start file monitoring:', error instanceof Error ? error.message : 'Unknown error');
      throw error;
    }

    // 將時間轉換為 cron 表達式 (秒 分 時 日 月 週)
    const [hour, minute] = this.config.dailyExecutionTime.split(':');
    const cronExpression = `0 ${minute} ${hour} * * *`; // 每天指定時間執行

    console.log(`📅 Setting up daily scheduler for ${this.config.dailyExecutionTime} (${this.config.timeZone})`);
    console.log(`📅 Cron expression: ${cronExpression}`);

    this.cronJob = new CronJob(
      cronExpression,
      this.executeEbookWorkflow.bind(this),
      null, // onComplete callback
      true, // start immediately
      this.config.timeZone,
      null, // context
      false, // runOnInit
      undefined, // utcOffset
      false, // unrefTimeout
      true, // waitForCompletion - prevent overlapping executions
      (error: unknown) => this.handleCronError(error as Error), // errorHandler
      'DailyEbookProcessor' // job name
    );

    console.log(`✅ Daily scheduler started successfully`);
    console.log(`⏰ Next execution: ${this.cronJob.nextDate().toISO()}`);

    // 設置重試處理排程 - 每小時執行一次
    this.setupRetryScheduler();
  }

  /**
   * 設置重試處理排程
   */
  private setupRetryScheduler(): void {
    // 每小時的第 15 分鐘執行重試處理
    const retryCronExpression = '0 15 * * * *'; // 每小時 15 分執行

    console.log('🔄 Setting up retry scheduler (hourly at :15)');

    this.retryCronJob = new CronJob(
      retryCronExpression,
      this.processRetryAttempts.bind(this),
      null, // onComplete callback
      true, // start immediately
      this.config.timeZone,
      null, // context
      false, // runOnInit
      undefined, // utcOffset
      false, // unrefTimeout
      true, // waitForCompletion
      (error: unknown) => this.handleCronError(error as Error), // errorHandler
      'RetryProcessor' // job name
    );

    console.log(`✅ Retry scheduler started successfully`);
    console.log(`⏰ Next retry execution: ${this.retryCronJob.nextDate().toISO()}`);
  }

  /**
   * 停止每日排程
   */
  public stop(): void {
    if (this.cronJob) {
      this.cronJob.stop();
      this.cronJob = null;
      console.log('🛑 Daily scheduler stopped');
    }

    if (this.retryCronJob) {
      this.retryCronJob.stop();
      this.retryCronJob = null;
      console.log('🛑 Retry scheduler stopped');
    }

    // 停止檔案監控服務
    this.integrationService.stopMonitoring();
    console.log('🛑 File monitoring service stopped');

    // 如果有正在執行的處理程序，終止它
    if (this.currentProcess) {
      this.currentProcess.kill('SIGTERM');
      this.currentProcess = null;
      console.log('🛑 Current ebook processing terminated');
    }
  }

  /**
   * 執行電子書處理工作流程
   */
  private async executeEbookWorkflow(): Promise<void> {
    if (this.isProcessing) {
      console.log('⚠️ Ebook processing is already in progress, skipping this execution');
      return;
    }

    this.isProcessing = true;
    const startTime = Date.now();

    try {
      console.log('🚀 Starting daily ebook processing workflow...');
      
      const result = await this.triggerPythonEbookProcessor();
      
      if (result.success) {
        console.log(`✅ Ebook processing completed successfully in ${result.processingTime}ms`);
        console.log(`📚 Books processed: ${result.booksProcessed}`);
        
        // 重置重試計數器
        this.retryCount = 0;
        
        // 檔案監控服務會自動處理輸出檔案並觸發通知
        console.log('📁 Waiting for file monitoring service to detect output file...');
        
      } else {
        console.error(`❌ Ebook processing failed: ${result.errorMessage}`);
        await this.handleProcessingFailure(result.errorMessage || 'Unknown error');
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('💥 Unexpected error during ebook workflow:', errorMessage);
      await this.handleProcessingFailure(errorMessage);
      
    } finally {
      this.isProcessing = false;
      const totalTime = Date.now() - startTime;
      console.log(`⏱️ Total workflow execution time: ${totalTime}ms`);
    }
  }

  /**
   * 觸發 Python 電子書處理器
   */
  private async triggerPythonEbookProcessor(): Promise<ProcessingResult> {
    return new Promise((resolve) => {
      const startTime = Date.now();
      
      // 使用 UTF-8 批次檔案來執行通知處理器
      const batchFilePath = path.join(path.dirname(this.config.ebookProcessorPath), 'run_notification_processor_utf8.bat');
      
      console.log(`🐍 Executing Python notification processor: ${batchFilePath}`);
      
      // 執行批次檔案（Windows）或直接執行 Python（其他系統）
      const isWindows = process.platform === 'win32';
      
      if (isWindows) {
        // Windows: 使用批次檔案
        this.currentProcess = spawn('cmd', ['/c', batchFilePath], {
          cwd: path.dirname(this.config.ebookProcessorPath),
          stdio: ['pipe', 'pipe', 'pipe'],
          env: {
            ...process.env,
            PYTHONIOENCODING: 'utf-8',
            LC_ALL: 'zh_TW.UTF-8',
            LANG: 'zh_TW.UTF-8'
          }
        });
      } else {
        // 非 Windows: 直接執行 Python
        const notificationProcessorPath = path.join(path.dirname(this.config.ebookProcessorPath), 'notification_processor.py');
        this.currentProcess = spawn(this.config.pythonExecutable, [notificationProcessorPath], {
          cwd: path.dirname(this.config.ebookProcessorPath),
          stdio: ['pipe', 'pipe', 'pipe'],
          env: {
            ...process.env,
            PYTHONIOENCODING: 'utf-8',
            LC_ALL: 'zh_TW.UTF-8',
            LANG: 'zh_TW.UTF-8'
          }
        });
      }

      let stdout = '';
      let stderr = '';

      this.currentProcess.stdout?.on('data', (data) => {
        const output = data.toString();
        stdout += output;
        console.log(`📝 Python output: ${output.trim()}`);
      });

      this.currentProcess.stderr?.on('data', (data) => {
        const error = data.toString();
        stderr += error;
        console.error(`🚨 Python error: ${error.trim()}`);
      });

      this.currentProcess.on('close', async (code) => {
        this.currentProcess = null;
        const processingTime = Date.now() - startTime;
        
        if (code === 0) {
          // 處理成功，檔案監控服務會自動處理輸出
          resolve({
            success: true,
            processingTime,
            booksProcessed: 0, // 實際數量會由檔案監控服務報告
          });
        } else {
          resolve({
            success: false,
            processingTime,
            booksProcessed: 0,
            errorMessage: `Python process exited with code ${code}. stderr: ${stderr}`
          });
        }
      });

      this.currentProcess.on('error', (error) => {
        this.currentProcess = null;
        const processingTime = Date.now() - startTime;
        
        resolve({
          success: false,
          processingTime,
          booksProcessed: 0,
          errorMessage: `Failed to start Python process: ${error.message}`
        });
      });
    });
  }



  /**
   * 觸發通知發送
   */
  private async triggerNotifications(processedData: ProcessedBookData): Promise<void> {
    try {
      console.log('📢 Triggering notification delivery...');
      
      // 檢查是否有書籍需要通知
      if (!processedData.successfullyProcessed || processedData.successfullyProcessed.length === 0) {
        console.log('📢 No books to notify, skipping notification delivery');
        return;
      }
      
      // 動態導入 NotificationService 以避免循環依賴
      const { NotificationService } = await import('./notificationService');
      const notificationService = new NotificationService();
      
      // 發送通知 - 將 ProcessedBookData 轉換為 NotificationService 期望的格式
      await notificationService.processNewBooks(processedData as any);
      
      console.log('✅ Notification delivery completed');
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error(`❌ Failed to trigger notifications: ${errorMessage}`);
      // 不拋出錯誤，因為電子書處理已經成功
    }
  }

  /**
   * 處理重試嘗試（每小時執行）
   */
  private async processRetryAttempts(): Promise<void> {
    try {
      console.log('🔄 Starting scheduled retry processing...');
      
      const retryResult = await errorRecoveryService.processRetryableFailures();
      
      if (retryResult.processed > 0) {
        console.log(`🔄 Retry processing completed: ${retryResult.successful} successful, ${retryResult.failed} failed out of ${retryResult.processed} attempts`);
      } else {
        console.log('🔄 No retryable failures found');
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error(`❌ Error during retry processing: ${errorMessage}`);
      // 不拋出錯誤，讓排程器繼續運行
    }
  }

  /**
   * 處理處理失敗的情況
   */
  private async handleProcessingFailure(errorMessage: string): Promise<void> {
    this.retryCount++;
    
    if (this.retryCount <= this.config.maxRetries) {
      const delayMs = this.config.retryDelayMinutes * 60 * 1000 * Math.pow(2, this.retryCount - 1); // 指數退避
      const delayMinutes = Math.round(delayMs / 60000);
      
      console.log(`🔄 Scheduling retry ${this.retryCount}/${this.config.maxRetries} in ${delayMinutes} minutes...`);
      
      setTimeout(() => {
        if (!this.isProcessing) { // 確保沒有其他處理正在進行
          this.executeEbookWorkflow();
        }
      }, delayMs);
      
    } else {
      console.error(`💥 Maximum retries (${this.config.maxRetries}) exceeded. Giving up until next scheduled execution.`);
      this.retryCount = 0; // 重置重試計數器，等待下次排程執行
      
      // 可以在這裡添加錯誤通知邏輯，例如發送管理員通知
      await this.notifyAdministrators(errorMessage);
    }
  }

  /**
   * 通知管理員處理失敗
   */
  private async notifyAdministrators(errorMessage: string): Promise<void> {
    try {
      console.log('📧 Notifying administrators about processing failure...');
      
      // 這裡可以實作發送管理員通知的邏輯
      // 例如：發送 LINE 訊息給管理員、發送 email 等
      
      console.log(`📧 Administrator notification sent: ${errorMessage}`);
      
    } catch (error) {
      console.error('❌ Failed to notify administrators:', error instanceof Error ? error.message : 'Unknown error');
    }
  }

  /**
   * 處理 Cron 錯誤
   */
  private handleCronError(error: Error): void {
    console.error('💥 Cron job error:', error.message);
    
    // 記錄錯誤但不停止排程器
    // 可以在這裡添加錯誤監控邏輯
  }

  /**
   * 獲取排程器狀態
   */
  public getStatus(): {
    isRunning: boolean;
    isProcessing: boolean;
    nextExecution?: string;
    nextRetryExecution?: string;
    retryCount: number;
    retrySchedulerRunning: boolean;
  } {
    const nextExecution = this.cronJob?.nextDate().toISO();
    const nextRetryExecution = this.retryCronJob?.nextDate().toISO();
    
    const result: {
      isRunning: boolean;
      isProcessing: boolean;
      nextExecution?: string;
      nextRetryExecution?: string;
      retryCount: number;
      retrySchedulerRunning: boolean;
    } = {
      isRunning: this.cronJob !== null,
      isProcessing: this.isProcessing,
      retryCount: this.retryCount,
      retrySchedulerRunning: this.retryCronJob !== null
    };
    
    if (nextExecution) {
      result.nextExecution = nextExecution;
    }
    
    if (nextRetryExecution) {
      result.nextRetryExecution = nextRetryExecution;
    }
    
    return result;
  }

  /**
   * 手動觸發處理（用於測試或管理）
   */
  public async manualTrigger(): Promise<ProcessingResult> {
    if (this.isProcessing) {
      throw new Error('Processing is already in progress');
    }

    console.log('🔧 Manual trigger initiated...');
    
    this.isProcessing = true;
    try {
      const result = await this.triggerPythonEbookProcessor();
      
      // 檔案監控服務會自動處理輸出檔案
      if (result.success) {
        console.log('📁 Manual trigger completed, waiting for file monitoring to process output...');
      }
      
      return result;
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * 手動處理指定的輸出檔案
   */
  public async processOutputFileManually(filePath: string): Promise<void> {
    try {
      console.log('🔧 Manual file processing initiated...');
      const processedData = await this.integrationService.processFileManually(filePath);
      await this.triggerNotifications(processedData);
      console.log('✅ Manual file processing completed');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error(`❌ Manual file processing failed: ${errorMessage}`);
      throw error;
    }
  }

  /**
   * 手動觸發重試處理
   */
  public async manualRetryProcessing(): Promise<{
    processed: number;
    successful: number;
    failed: number;
  }> {
    try {
      console.log('🔧 Manual retry processing initiated...');
      const result = await errorRecoveryService.processRetryableFailures();
      console.log(`✅ Manual retry processing completed: ${result.successful}/${result.processed} successful`);
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error(`❌ Manual retry processing failed: ${errorMessage}`);
      throw error;
    }
  }

  /**
   * 獲取重試統計資料
   */
  public async getRetryStatistics(): Promise<any> {
    try {
      return await errorRecoveryService.getRetryStatistics();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error(`❌ Failed to get retry statistics: ${errorMessage}`);
      throw error;
    }
  }

  /**
   * 處理測試資料（用於手動測試通知格式）
   */
  public async processTestData(testData: any): Promise<ProcessingResult> {
    try {
      console.log('🧪 Processing test data for notification...');
      
      const startTime = Date.now();
      
      // 將測試資料轉換為 ProcessedBookData 格式
      const processedData: ProcessedBookData = {
        processingDate: testData.processingDate || new Date().toISOString().split('T')[0],
        totalBooksFound: testData.totalBooksFound || 1,
        successfullyProcessed: testData.successfullyProcessed || [],
        processingStats: testData.processingStats || {
          booksProcessed: 1,
          booksFailed: 0,
          pdfExtractions: 1,
          googleSearches: 0
        }
      };
      
      // 直接觸發通知，不經過檔案處理
      await this.triggerNotifications(processedData);
      
      const processingTime = Date.now() - startTime;
      
      console.log('✅ Test data processing completed');
      
      return {
        success: true,
        processingTime,
        booksProcessed: processedData.successfullyProcessed.length
      };
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error(`❌ Test data processing failed: ${errorMessage}`);
      
      return {
        success: false,
        processingTime: 0,
        booksProcessed: 0,
        errorMessage
      };
    }
  }
}

// 創建單例實例
let schedulerInstance: DailySchedulerService | null = null;

/**
 * 獲取排程器單例實例
 */
export function getSchedulerInstance(): DailySchedulerService {
  if (!schedulerInstance) {
    schedulerInstance = new DailySchedulerService();
  }
  return schedulerInstance;
}