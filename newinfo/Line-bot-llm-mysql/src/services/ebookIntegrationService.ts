import { promises as fs } from 'fs';
import { watch, FSWatcher } from 'fs';
import path from 'path';
import { EventEmitter } from 'events';

/**
 * Ebook Integration Service
 * 電子書處理系統整合服務，負責監控 Python 處理器輸出並處理結果
 */

export interface ProcessedBookData {
  processingDate: string;
  totalBooksFound: number;
  successfullyProcessed: BookSummary[];
  processingStats: {
    booksProcessed: number;
    booksFailed: number;
    pdfExtractions: number;
    googleSearches: number;
    networkFailures?: number;
    processingTimeSeconds?: number;
  };
}

export interface BookSummary {
  title: string;
  author?: string;
  summary: string;
  downloadUrl: string;
  processingMethod: 'pdf_extract' | 'google_search';
  processingSuccess: boolean;
  filename?: string;
  downloadPath?: string;
  errorMessage?: string;
}

export interface FileMonitorConfig {
  watchDirectory: string;
  filePattern: RegExp;
  processingTimeout: number; // 處理超時時間（毫秒）
  maxRetries: number;
  retryDelay: number;
}

export class EbookIntegrationService extends EventEmitter {
  private fileWatcher: FSWatcher | null = null;
  private isMonitoring = false;
  private processingTimeouts = new Map<string, NodeJS.Timeout>();
  private lastProcessedTime = new Map<string, number>(); // 追蹤文件最後處理時間
  private lastProcessedHash = new Map<string, string>(); // 追蹤文件內容哈希，避免重複處理相同內容

  constructor(private config: FileMonitorConfig) {
    super();
    this.validateConfig();
  }

  /**
   * 驗證配置參數
   */
  private validateConfig(): void {
    if (!this.config.watchDirectory) {
      throw new Error('Watch directory is required');
    }

    if (this.config.processingTimeout < 1000) {
      throw new Error('Processing timeout must be at least 1000ms');
    }

    if (this.config.maxRetries < 0 || this.config.maxRetries > 10) {
      throw new Error('Max retries must be between 0 and 10');
    }
  }

  /**
   * 開始監控檔案變化
   */
  public async startMonitoring(): Promise<void> {
    if (this.isMonitoring) {
      console.log('📁 File monitoring is already active');
      return;
    }

    try {
      // 確保監控目錄存在
      await this.ensureDirectoryExists(this.config.watchDirectory);

      console.log(`📁 Starting file monitoring: ${this.config.watchDirectory}`);
      console.log(`📁 File pattern: ${this.config.filePattern.source}`);

      this.fileWatcher = watch(this.config.watchDirectory, { persistent: true }, (eventType, filename) => {
        if (filename && eventType === 'change') {
          this.handleFileChange(filename);
        }
      });

      this.fileWatcher.on('error', (error) => {
        console.error('📁 File watcher error:', error);
        this.emit('error', error);
      });

      this.isMonitoring = true;
      console.log('✅ File monitoring started successfully');
      this.emit('monitoring-started');

    } catch (error) {
      console.error('❌ Failed to start file monitoring:', error);
      throw error;
    }
  }

  /**
   * 停止監控檔案變化
   */
  public stopMonitoring(): void {
    if (!this.isMonitoring) {
      return;
    }

    console.log('🛑 Stopping file monitoring...');

    if (this.fileWatcher) {
      this.fileWatcher.close();
      this.fileWatcher = null;
    }

    // 清除所有處理超時
    for (const timeout of this.processingTimeouts.values()) {
      clearTimeout(timeout);
    }
    this.processingTimeouts.clear();

    this.isMonitoring = false;
    console.log('✅ File monitoring stopped');
    this.emit('monitoring-stopped');
  }

  /**
   * 處理檔案變化事件
   */
  private handleFileChange(filename: string): void {
    // 檢查檔案是否符合模式
    if (!this.config.filePattern.test(filename)) {
      return;
    }

    // 只處理 latest 文件，完全忽略時間戳文件（避免重複通知）
    if (filename !== 'notification_data_latest.json') {
      console.log(`📄 Ignoring timestamped file (only processing latest): ${filename}`);
      return;
    }

    const filePath = path.join(this.config.watchDirectory, filename);
    const now = Date.now();
    
    // 檢查是否在短時間內重複處理同一文件（防止重複通知）
    const lastProcessed = this.lastProcessedTime.get(filePath);
    if (lastProcessed && (now - lastProcessed) < 60000) { // 60秒內不重複處理
      console.log(`📄 Skipping duplicate file change: ${filename} (processed ${Math.round((now - lastProcessed) / 1000)}s ago)`);
      return;
    }

    console.log(`📄 Detected file change: ${filename}`);

    // 清除之前的處理超時（如果存在）
    const existingTimeout = this.processingTimeouts.get(filePath);
    if (existingTimeout) {
      clearTimeout(existingTimeout);
      console.log(`📄 Cleared previous timeout for: ${filename}`);
    }

    // 設置新的處理超時，等待檔案寫入完成
    const timeout = setTimeout(() => {
      this.processFile(filePath);
      this.processingTimeouts.delete(filePath);
    }, 5000); // 等待 5 秒確保檔案寫入完成並合併多次變化

    this.processingTimeouts.set(filePath, timeout);
  }

  /**
   * 處理檔案內容
   */
  private async processFile(filePath: string): Promise<void> {
    let retryCount = 0;
    const maxRetries = this.config.maxRetries;

    while (retryCount <= maxRetries) {
      try {
        console.log(`📖 Processing file: ${path.basename(filePath)} (attempt ${retryCount + 1})`);

        // 檢查檔案是否存在且可讀取
        await fs.access(filePath, fs.constants.R_OK);

        // 讀取檔案內容
        const content = await fs.readFile(filePath, 'utf-8');

        if (!content.trim()) {
          throw new Error('File is empty');
        }

        // 計算內容哈希，避免處理相同內容
        const contentHash = this.calculateHash(content);
        const lastHash = this.lastProcessedHash.get(filePath);
        
        if (lastHash === contentHash) {
          console.log(`📄 Skipping file with identical content: ${path.basename(filePath)}`);
          return; // 內容相同，不重複處理
        }

        // 解析 JSON 內容
        const processedData = this.parseProcessedBookData(content);

        // 驗證資料格式
        this.validateProcessedData(processedData);

        console.log(`✅ Successfully processed file: ${path.basename(filePath)}`);
        console.log(`📚 Books processed: ${processedData.successfullyProcessed.length}`);

        // 記錄處理時間和內容哈希，防止重複處理
        this.lastProcessedTime.set(filePath, Date.now());
        this.lastProcessedHash.set(filePath, contentHash);

        // 發出處理完成事件
        this.emit('books-processed', processedData, filePath);

        return; // 成功處理，退出重試循環

      } catch (error) {
        retryCount++;
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        
        console.error(`❌ Failed to process file (attempt ${retryCount}/${maxRetries + 1}): ${errorMessage}`);

        if (retryCount <= maxRetries) {
          console.log(`🔄 Retrying in ${this.config.retryDelay}ms...`);
          await this.delay(this.config.retryDelay);
        } else {
          console.error(`💥 Max retries exceeded for file: ${path.basename(filePath)}`);
          this.emit('processing-failed', filePath, errorMessage);
        }
      }
    }
  }

  /**
   * 計算字符串的簡單哈希值
   */
  private calculateHash(content: string): string {
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return hash.toString(36);
  }

  /**
   * 解析處理過的書籍資料
   */
  private parseProcessedBookData(content: string): ProcessedBookData {
    // Check for empty content first
    if (!content.trim()) {
      throw new Error('File is empty');
    }

    try {
      const rawData = JSON.parse(content);

      // 轉換為標準格式
      const processedData: ProcessedBookData = {
        processingDate: rawData.processingDate || new Date().toISOString(),
        totalBooksFound: rawData.totalBooksFound || 0,
        successfullyProcessed: this.convertToBookSummaries(rawData.successfullyProcessed || []),
        processingStats: {
          booksProcessed: rawData.processingStats?.booksProcessed || 0,
          booksFailed: rawData.processingStats?.booksFailed || 0,
          pdfExtractions: rawData.processingStats?.pdfExtractions || 0,
          googleSearches: rawData.processingStats?.googleSearches || 0,
          networkFailures: rawData.processingStats?.networkFailures,
          processingTimeSeconds: rawData.processingStats?.processingTimeSeconds
        }
      };

      return processedData;

    } catch (error) {
      throw new Error(`Failed to parse JSON: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * 轉換為書籍摘要格式
   */
  private convertToBookSummaries(rawBooks: any[]): BookSummary[] {
    return rawBooks.map((book, index) => {
      try {
        // Validate required fields during conversion
        const title = book.title?.trim();
        if (!title) {
          throw new Error(`Book title is required for book at index ${index}`);
        }

        const bookSummary: BookSummary = {
          title: title,
          summary: book.summary || '',
          downloadUrl: book.pdf_url || book.downloadUrl || '',
          processingMethod: this.determineProcessingMethod(book),
          processingSuccess: book.processing_success !== false && !!book.summary
        };

        // 添加可選屬性
        if (book.author) {
          bookSummary.author = book.author;
        }
        if (book.filename) {
          bookSummary.filename = book.filename;
        }
        if (book.download_path || book.downloadPath) {
          bookSummary.downloadPath = book.download_path || book.downloadPath;
        }
        if (book.error_message || book.errorMessage) {
          bookSummary.errorMessage = book.error_message || book.errorMessage;
        }

        return bookSummary;
      } catch (error) {
        console.warn(`⚠️ Failed to convert book at index ${index}:`, error);
        return {
          title: `轉換失敗的書籍 ${index + 1}`,
          summary: '',
          downloadUrl: '',
          processingMethod: 'pdf_extract' as const,
          processingSuccess: false,
          errorMessage: `資料轉換失敗: ${error instanceof Error ? error.message : 'Unknown error'}`
        };
      }
    });
  }

  /**
   * 判斷處理方法
   */
  private determineProcessingMethod(book: any): 'pdf_extract' | 'google_search' {
    const method = book.processing_method || book.processingMethod;
    
    if (method === 'google_search' || method === 'google') {
      return 'google_search';
    }
    
    return 'pdf_extract';
  }

  /**
   * 驗證處理過的資料格式
   */
  private validateProcessedData(data: ProcessedBookData): void {
    if (!data.processingDate) {
      throw new Error('Missing processing date');
    }

    if (typeof data.totalBooksFound !== 'number' || data.totalBooksFound < 0) {
      throw new Error('Invalid total books found');
    }

    if (!Array.isArray(data.successfullyProcessed)) {
      throw new Error('Successfully processed books must be an array');
    }

    if (!data.processingStats || typeof data.processingStats !== 'object') {
      throw new Error('Missing or invalid processing stats');
    }

    // 驗證每本書的基本資料
    for (const book of data.successfullyProcessed) {
      if (!book.title) {
        throw new Error('Book title is required');
      }
      
      if (typeof book.processingSuccess !== 'boolean') {
        throw new Error('Book processing success flag is required');
      }
    }
  }

  /**
   * 確保目錄存在
   */
  private async ensureDirectoryExists(dirPath: string): Promise<void> {
    try {
      await fs.access(dirPath);
    } catch (error) {
      // 目錄不存在，嘗試創建
      try {
        await fs.mkdir(dirPath, { recursive: true });
        console.log(`📁 Created directory: ${dirPath}`);
      } catch (createError) {
        throw new Error(`Failed to create directory ${dirPath}: ${createError instanceof Error ? createError.message : 'Unknown error'}`);
      }
    }
  }

  /**
   * 延遲函數
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 手動處理指定檔案
   */
  public async processFileManually(filePath: string): Promise<ProcessedBookData> {
    console.log(`🔧 Manual file processing: ${filePath}`);
    
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      const processedData = this.parseProcessedBookData(content);
      this.validateProcessedData(processedData);
      
      console.log(`✅ Manual processing completed: ${path.basename(filePath)}`);
      return processedData;
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error(`❌ Manual processing failed: ${errorMessage}`);
      throw new Error(`Manual processing failed: ${errorMessage}`);
    }
  }

  /**
   * 尋找最新的處理結果檔案
   */
  public async findLatestProcessedFile(): Promise<string | null> {
    try {
      // 首先嘗試找到 latest 檔案
      const latestFilePath = path.join(this.config.watchDirectory, 'notification_data_latest.json');
      
      try {
        await fs.access(latestFilePath, fs.constants.R_OK);
        console.log(`📄 Found latest notification file: ${latestFilePath}`);
        return latestFilePath;
      } catch {
        console.log('📄 Latest notification file not found, searching for timestamped files...');
      }

      // 如果 latest 檔案不存在，尋找時間戳檔案
      const files = await fs.readdir(this.config.watchDirectory);
      
      const matchingFiles = files
        .filter(file => this.config.filePattern.test(file) && file !== 'notification_data_latest.json')
        .map(file => ({
          name: file,
          path: path.join(this.config.watchDirectory, file)
        }));

      if (matchingFiles.length === 0) {
        console.log('📄 No notification data files found');
        return null;
      }

      // 獲取檔案統計資訊並按修改時間排序
      const filesWithStats = await Promise.all(
        matchingFiles.map(async (file) => {
          try {
            const stat = await fs.stat(file.path);
            return { ...file, mtime: stat.mtime };
          } catch (error) {
            console.warn(`⚠️ Failed to get stats for file ${file.name}:`, error);
            return null;
          }
        })
      );

      const validFiles = filesWithStats.filter(file => file !== null);
      if (validFiles.length === 0) {
        return null;
      }

      validFiles.sort((a, b) => b!.mtime.getTime() - a!.mtime.getTime());
      
      const latestFile = validFiles[0];
      if (!latestFile) {
        return null;
      }
      
      console.log(`📄 Found latest timestamped file: ${latestFile.name}`);
      return latestFile.path;

    } catch (error) {
      console.error('❌ Failed to find latest processed file:', error);
      return null;
    }
  }

  /**
   * 檢查 Python 處理器是否正在運行
   */
  public async checkPythonProcessorStatus(): Promise<{
    isRunning: boolean;
    lastProcessingTime?: Date;
    hasRecentData: boolean;
  }> {
    try {
      const latestFile = await this.findLatestProcessedFile();
      
      if (!latestFile) {
        return {
          isRunning: false,
          hasRecentData: false
        };
      }

      const stat = await fs.stat(latestFile);
      const lastModified = stat.mtime;
      const now = new Date();
      const timeDiff = now.getTime() - lastModified.getTime();
      
      // 如果檔案在過去 24 小時內修改過，認為有最近的資料
      const hasRecentData = timeDiff < 24 * 60 * 60 * 1000;
      
      // 如果檔案在過去 1 小時內修改過，可能正在處理
      const isRunning = timeDiff < 60 * 60 * 1000;

      return {
        isRunning,
        lastProcessingTime: lastModified,
        hasRecentData
      };

    } catch (error) {
      console.error('❌ Failed to check Python processor status:', error);
      return {
        isRunning: false,
        hasRecentData: false
      };
    }
  }

  /**
   * 創建空的處理結果（當沒有新書時的回退機制）
   */
  public createEmptyProcessingResult(): ProcessedBookData {
    return {
      processingDate: new Date().toISOString(),
      totalBooksFound: 0,
      successfullyProcessed: [],
      processingStats: {
        booksProcessed: 0,
        booksFailed: 0,
        pdfExtractions: 0,
        googleSearches: 0,
        networkFailures: 0,
        processingTimeSeconds: 0
      }
    };
  }

  /**
   * 獲取處理結果，包含回退機制
   */
  public async getProcessingResultWithFallback(): Promise<{
    data: ProcessedBookData;
    source: 'file' | 'empty' | 'error';
    message?: string;
  }> {
    try {
      const latestFile = await this.findLatestProcessedFile();
      
      if (!latestFile) {
        console.log('📄 No processing files found, returning empty result');
        return {
          data: this.createEmptyProcessingResult(),
          source: 'empty',
          message: 'No processing files found'
        };
      }

      try {
        const data = await this.processFileManually(latestFile);
        return {
          data,
          source: 'file',
          message: `Loaded from ${path.basename(latestFile)}`
        };
      } catch (error) {
        console.error('❌ Failed to process latest file, returning empty result:', error);
        return {
          data: this.createEmptyProcessingResult(),
          source: 'error',
          message: `Failed to process file: ${error instanceof Error ? error.message : 'Unknown error'}`
        };
      }

    } catch (error) {
      console.error('❌ Failed to get processing result:', error);
      return {
        data: this.createEmptyProcessingResult(),
        source: 'error',
        message: `System error: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * 獲取監控狀態
   */
  public getStatus(): {
    isMonitoring: boolean;
    watchDirectory: string;
    filePattern: string;
    pendingProcessing: number;
  } {
    return {
      isMonitoring: this.isMonitoring,
      watchDirectory: this.config.watchDirectory,
      filePattern: this.config.filePattern.source,
      pendingProcessing: this.processingTimeouts.size
    };
  }
}

// 預設配置
export const defaultFileMonitorConfig: FileMonitorConfig = {
  watchDirectory: path.join(process.cwd(), '..', 'ebook', 'generated_documents'),
  filePattern: /^notification_data_(\d{8}_\d{6}|latest)\.json$/,
  processingTimeout: 30000, // 30 秒
  maxRetries: 3,
  retryDelay: 5000 // 5 秒
};