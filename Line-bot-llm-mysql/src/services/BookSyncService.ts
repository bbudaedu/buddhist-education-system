import { ExcelReaderService } from './ExcelReaderService';
import { NewBookService } from './NewBookService';
import { WebsiteMonitoringService } from './WebsiteMonitoringService';
import { 
  WebsiteMonitoringData, 
  ContentSyncResult, 
  BatchContentSyncResult,
  CarouselContent,
  CourseCancellation,
  NewsAnnouncement,
  MediaContent
} from '../types/WebsiteMonitoring';

/**
 * Service for synchronizing book data from Excel files to database
 */
export class BookSyncService {
  private excelReader: ExcelReaderService;
  private newBookService: NewBookService;
  private websiteMonitoringService: WebsiteMonitoringService;

  constructor() {
    this.excelReader = new ExcelReaderService();
    this.newBookService = new NewBookService();
    this.websiteMonitoringService = new WebsiteMonitoringService();
  }

  /**
   * 同步單個 Excel 檔案到資料庫
   * @param excelFilePath Excel 檔案路徑
   * @returns Promise<SyncResult> 同步結果
   */
  async syncExcelFileToDatabase(excelFilePath: string): Promise<SyncResult> {
    const startTime = Date.now();
    
    try {
      console.log(`Starting sync for Excel file: ${excelFilePath}`);
      
      // 讀取 Excel 檔案
      const books = await this.excelReader.readExcelFile(excelFilePath);
      
      if (books.length === 0) {
        return {
          success: true,
          filePath: excelFilePath,
          totalBooks: 0,
          successfulSyncs: 0,
          failedSyncs: 0,
          duration: Date.now() - startTime,
          errors: [],
          message: 'No books found in Excel file'
        };
      }
      
      // 驗證資料
      const validation = this.excelReader.validateExcelData(books);
      console.log(`Validation results: ${validation.valid}/${validation.total} valid books`);
      
      if (validation.issues.length > 0) {
        console.warn('Data validation issues:', validation.issues);
      }
      
      // 批量同步到資料庫
      const successfulSyncs = await this.newBookService.batchUpsertNewBooks(books);
      
      const result: SyncResult = {
        success: true,
        filePath: excelFilePath,
        totalBooks: books.length,
        successfulSyncs,
        failedSyncs: books.length - successfulSyncs,
        duration: Date.now() - startTime,
        errors: validation.issues,
        message: `Successfully synced ${successfulSyncs}/${books.length} books`
      };
      
      console.log(`Sync completed: ${result.message} in ${result.duration}ms`);
      return result;
      
    } catch (error) {
      console.error('Error during sync:', error);
      
      return {
        success: false,
        filePath: excelFilePath,
        totalBooks: 0,
        successfulSyncs: 0,
        failedSyncs: 0,
        duration: Date.now() - startTime,
        errors: [error instanceof Error ? error.message : String(error)],
        message: `Sync failed: ${error}`
      };
    }
  }

  /**
   * 同步指定目錄下的所有 Excel 檔案
   * @param directoryPath 目錄路徑
   * @param filePattern 檔案名稱模式（可選）
   * @returns Promise<BatchSyncResult> 批量同步結果
   */
  async syncDirectoryToDatabase(
    directoryPath: string, 
    filePattern?: RegExp
  ): Promise<BatchSyncResult> {
    const startTime = Date.now();
    
    try {
      console.log(`Starting batch sync for directory: ${directoryPath}`);
      
      // 尋找 Excel 檔案
      const excelFiles = await this.excelReader.findExcelFiles(directoryPath, filePattern);
      
      if (excelFiles.length === 0) {
        return {
          success: true,
          directoryPath,
          totalFiles: 0,
          processedFiles: 0,
          totalBooks: 0,
          successfulSyncs: 0,
          failedSyncs: 0,
          duration: Date.now() - startTime,
          fileResults: [],
          message: 'No Excel files found in directory'
        };
      }
      
      console.log(`Found ${excelFiles.length} Excel files to process`);
      
      // 處理每個檔案
      const fileResults: SyncResult[] = [];
      let totalBooks = 0;
      let totalSuccessfulSyncs = 0;
      let totalFailedSyncs = 0;
      
      for (const filePath of excelFiles) {
        const result = await this.syncExcelFileToDatabase(filePath);
        fileResults.push(result);
        
        totalBooks += result.totalBooks;
        totalSuccessfulSyncs += result.successfulSyncs;
        totalFailedSyncs += result.failedSyncs;
      }
      
      const batchResult: BatchSyncResult = {
        success: true,
        directoryPath,
        totalFiles: excelFiles.length,
        processedFiles: fileResults.length,
        totalBooks,
        successfulSyncs: totalSuccessfulSyncs,
        failedSyncs: totalFailedSyncs,
        duration: Date.now() - startTime,
        fileResults,
        message: `Batch sync completed: ${totalSuccessfulSyncs}/${totalBooks} books synced from ${fileResults.length} files`
      };
      
      console.log(`Batch sync completed: ${batchResult.message} in ${batchResult.duration}ms`);
      return batchResult;
      
    } catch (error) {
      console.error('Error during batch sync:', error);
      
      return {
        success: false,
        directoryPath,
        totalFiles: 0,
        processedFiles: 0,
        totalBooks: 0,
        successfulSyncs: 0,
        failedSyncs: 0,
        duration: Date.now() - startTime,
        fileResults: [],
        message: `Batch sync failed: ${error}`
      };
    }
  }

  /**
   * 監控指定目錄，自動同步新的 Excel 檔案
   * @param directoryPath 監控目錄路徑
   * @param intervalMs 檢查間隔（毫秒），預設 60000 (1分鐘)
   * @param filePattern 檔案名稱模式（可選）
   */
  async startDirectoryMonitoring(
    directoryPath: string,
    intervalMs: number = 60000,
    filePattern?: RegExp
  ): Promise<void> {
    console.log(`Starting directory monitoring: ${directoryPath} (interval: ${intervalMs}ms)`);
    
    const processedFiles = new Set<string>();
    
    // 初始掃描
    try {
      const initialFiles = await this.excelReader.findExcelFiles(directoryPath, filePattern);
      for (const file of initialFiles) {
        processedFiles.add(file);
      }
      console.log(`Initial scan found ${initialFiles.length} existing files`);
    } catch (error) {
      console.error('Error during initial directory scan:', error);
    }
    
    // 定期檢查新檔案
    const checkForNewFiles = async () => {
      try {
        const currentFiles = await this.excelReader.findExcelFiles(directoryPath, filePattern);
        const newFiles = currentFiles.filter(file => !processedFiles.has(file));
        
        if (newFiles.length > 0) {
          console.log(`Found ${newFiles.length} new Excel files to process`);
          
          for (const newFile of newFiles) {
            try {
              const result = await this.syncExcelFileToDatabase(newFile);
              console.log(`Auto-sync result for ${newFile}: ${result.message}`);
              processedFiles.add(newFile);
            } catch (error) {
              console.error(`Failed to auto-sync file ${newFile}:`, error);
            }
          }
        }
      } catch (error) {
        console.error('Error during directory monitoring check:', error);
      }
    };
    
    // 設定定期檢查
    setInterval(checkForNewFiles, intervalMs);
    console.log('Directory monitoring started successfully');
  }

  /**
   * 取得同步統計資料
   * @returns Promise<SyncStats> 同步統計
   */
  async getSyncStats(): Promise<SyncStats> {
    try {
      const stats = await this.newBookService.getNewBooksStats();
      
      return {
        totalBooksInDatabase: stats.total,
        notifiedBooks: stats.notified,
        unnotifiedBooks: stats.unnotified,
        recentBooks: stats.recentCount,
        lastSyncTime: new Date() // 這裡可以從資料庫或日誌中取得實際的最後同步時間
      };
    } catch (error) {
      console.error('Error getting sync stats:', error);
      throw new Error('Failed to get sync statistics');
    }
  }

  /**
   * 清理舊的同步資料
   * @param daysOld 保留天數，預設 30 天
   * @returns Promise<number> 清理的記錄數
   */
  async cleanupOldSyncData(daysOld: number = 30): Promise<number> {
    // 這裡可以實現清理邏輯，例如刪除舊的同步日誌或標記為已處理的舊資料
    console.log(`Cleanup old sync data older than ${daysOld} days`);
    // 實際實現會根據需求來決定
    return 0;
  }

  /**
   * 同步網站監控內容到資料庫
   * @param contentData 網站監控內容資料
   * @returns Promise<BatchContentSyncResult> 批量同步結果
   */
  async syncWebsiteMonitoringContent(contentData: WebsiteMonitoringData): Promise<BatchContentSyncResult> {
    const startTime = Date.now();
    
    try {
      console.log('Starting website monitoring content sync');
      
      const contentResults: ContentSyncResult[] = [];
      let totalItems = 0;
      let totalSuccessfulSyncs = 0;
      let totalFailedSyncs = 0;
      
      // 同步輪播內容
      if (contentData.carousel && contentData.carousel.length > 0) {
        const result = await this.syncCarouselContent(contentData.carousel);
        contentResults.push(result);
        totalItems += result.totalItems;
        totalSuccessfulSyncs += result.successfulSyncs;
        totalFailedSyncs += result.failedSyncs;
      }
      
      // 同步課程取消內容
      if (contentData.cancellation && contentData.cancellation.length > 0) {
        const result = await this.syncCancellationContent(contentData.cancellation);
        contentResults.push(result);
        totalItems += result.totalItems;
        totalSuccessfulSyncs += result.successfulSyncs;
        totalFailedSyncs += result.failedSyncs;
      }
      
      // 同步新聞內容
      if (contentData.news && contentData.news.length > 0) {
        const result = await this.syncNewsContent(contentData.news);
        contentResults.push(result);
        totalItems += result.totalItems;
        totalSuccessfulSyncs += result.successfulSyncs;
        totalFailedSyncs += result.failedSyncs;
      }
      
      // 同步媒體內容
      if (contentData.media && contentData.media.length > 0) {
        const result = await this.syncMediaContent(contentData.media);
        contentResults.push(result);
        totalItems += result.totalItems;
        totalSuccessfulSyncs += result.successfulSyncs;
        totalFailedSyncs += result.failedSyncs;
      }
      
      const batchResult: BatchContentSyncResult = {
        success: true,
        totalContentTypes: Object.keys(contentData).length,
        processedContentTypes: contentResults.length,
        totalItems,
        successfulSyncs: totalSuccessfulSyncs,
        failedSyncs: totalFailedSyncs,
        duration: Date.now() - startTime,
        contentResults,
        message: `Website monitoring sync completed: ${totalSuccessfulSyncs}/${totalItems} items synced across ${contentResults.length} content types`
      };
      
      console.log(`Website monitoring sync completed: ${batchResult.message} in ${batchResult.duration}ms`);
      return batchResult;
      
    } catch (error) {
      console.error('Error during website monitoring sync:', error);
      
      return {
        success: false,
        totalContentTypes: 0,
        processedContentTypes: 0,
        totalItems: 0,
        successfulSyncs: 0,
        failedSyncs: 0,
        duration: Date.now() - startTime,
        contentResults: [],
        message: `Website monitoring sync failed: ${error}`
      };
    }
  }

  /**
   * 同步輪播內容
   * @private
   */
  private async syncCarouselContent(carouselData: CarouselContent[]): Promise<ContentSyncResult> {
    const startTime = Date.now();
    
    try {
      console.log(`Syncing ${carouselData.length} carousel items`);
      
      const successfulSyncs = await this.websiteMonitoringService.batchUpsertCarouselContent(carouselData);
      
      return {
        success: true,
        contentType: 'carousel',
        totalItems: carouselData.length,
        successfulSyncs,
        failedSyncs: carouselData.length - successfulSyncs,
        duration: Date.now() - startTime,
        errors: [],
        message: `Successfully synced ${successfulSyncs}/${carouselData.length} carousel items`
      };
      
    } catch (error) {
      console.error('Error syncing carousel content:', error);
      
      return {
        success: false,
        contentType: 'carousel',
        totalItems: carouselData.length,
        successfulSyncs: 0,
        failedSyncs: carouselData.length,
        duration: Date.now() - startTime,
        errors: [error instanceof Error ? error.message : String(error)],
        message: `Carousel sync failed: ${error}`
      };
    }
  }

  /**
   * 同步課程取消內容
   * @private
   */
  private async syncCancellationContent(cancellationData: CourseCancellation[]): Promise<ContentSyncResult> {
    const startTime = Date.now();
    
    try {
      console.log(`Syncing ${cancellationData.length} cancellation items`);
      
      const successfulSyncs = await this.websiteMonitoringService.batchUpsertCancellationContent(cancellationData);
      
      return {
        success: true,
        contentType: 'cancellation',
        totalItems: cancellationData.length,
        successfulSyncs,
        failedSyncs: cancellationData.length - successfulSyncs,
        duration: Date.now() - startTime,
        errors: [],
        message: `Successfully synced ${successfulSyncs}/${cancellationData.length} cancellation items`
      };
      
    } catch (error) {
      console.error('Error syncing cancellation content:', error);
      
      return {
        success: false,
        contentType: 'cancellation',
        totalItems: cancellationData.length,
        successfulSyncs: 0,
        failedSyncs: cancellationData.length,
        duration: Date.now() - startTime,
        errors: [error instanceof Error ? error.message : String(error)],
        message: `Cancellation sync failed: ${error}`
      };
    }
  }

  /**
   * 同步新聞內容
   * @private
   */
  private async syncNewsContent(newsData: NewsAnnouncement[]): Promise<ContentSyncResult> {
    const startTime = Date.now();
    
    try {
      console.log(`Syncing ${newsData.length} news items`);
      
      const successfulSyncs = await this.websiteMonitoringService.batchUpsertNewsContent(newsData);
      
      return {
        success: true,
        contentType: 'news',
        totalItems: newsData.length,
        successfulSyncs,
        failedSyncs: newsData.length - successfulSyncs,
        duration: Date.now() - startTime,
        errors: [],
        message: `Successfully synced ${successfulSyncs}/${newsData.length} news items`
      };
      
    } catch (error) {
      console.error('Error syncing news content:', error);
      
      return {
        success: false,
        contentType: 'news',
        totalItems: newsData.length,
        successfulSyncs: 0,
        failedSyncs: newsData.length,
        duration: Date.now() - startTime,
        errors: [error instanceof Error ? error.message : String(error)],
        message: `News sync failed: ${error}`
      };
    }
  }

  /**
   * 同步媒體內容
   * @private
   */
  private async syncMediaContent(mediaData: MediaContent[]): Promise<ContentSyncResult> {
    const startTime = Date.now();
    
    try {
      console.log(`Syncing ${mediaData.length} media items`);
      
      const successfulSyncs = await this.websiteMonitoringService.batchUpsertMediaContent(mediaData);
      
      return {
        success: true,
        contentType: 'media',
        totalItems: mediaData.length,
        successfulSyncs,
        failedSyncs: mediaData.length - successfulSyncs,
        duration: Date.now() - startTime,
        errors: [],
        message: `Successfully synced ${successfulSyncs}/${mediaData.length} media items`
      };
      
    } catch (error) {
      console.error('Error syncing media content:', error);
      
      return {
        success: false,
        contentType: 'media',
        totalItems: mediaData.length,
        successfulSyncs: 0,
        failedSyncs: mediaData.length,
        duration: Date.now() - startTime,
        errors: [error instanceof Error ? error.message : String(error)],
        message: `Media sync failed: ${error}`
      };
    }
  }
}

/**
 * 單個檔案同步結果
 */
export interface SyncResult {
  success: boolean;
  filePath: string;
  totalBooks: number;
  successfulSyncs: number;
  failedSyncs: number;
  duration: number;
  errors: string[];
  message: string;
}

/**
 * 批量同步結果
 */
export interface BatchSyncResult {
  success: boolean;
  directoryPath: string;
  totalFiles: number;
  processedFiles: number;
  totalBooks: number;
  successfulSyncs: number;
  failedSyncs: number;
  duration: number;
  fileResults: SyncResult[];
  message: string;
}

/**
 * 同步統計資料
 */
export interface SyncStats {
  totalBooksInDatabase: number;
  notifiedBooks: number;
  unnotifiedBooks: number;
  recentBooks: number;
  lastSyncTime: Date;
}

// 建立單例實例
export const bookSyncService = new BookSyncService();