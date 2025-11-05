import { EbookIntegrationService, defaultFileMonitorConfig, ProcessedBookData } from './ebookIntegrationService';
import { promises as fs } from 'fs';
import path from 'path';

/**
 * Test suite for EbookIntegrationService
 * 電子書整合服務測試套件
 */

describe('EbookIntegrationService', () => {
  let service: EbookIntegrationService;
  let testDir: string;

  beforeEach(async () => {
    // 創建測試目錄
    testDir = path.join(__dirname, '../../test-data/ebook-integration');
    await fs.mkdir(testDir, { recursive: true });

    // 創建測試配置
    const testConfig = {
      ...defaultFileMonitorConfig,
      watchDirectory: testDir,
      processingTimeout: 5000,
      maxRetries: 2,
      retryDelay: 1000
    };

    service = new EbookIntegrationService(testConfig);
  });

  afterEach(async () => {
    // 停止監控
    service.stopMonitoring();

    // 清理測試目錄
    try {
      await fs.rm(testDir, { recursive: true, force: true });
    } catch (error) {
      console.warn('Failed to clean up test directory:', error);
    }
  });

  describe('File Processing', () => {
    test('should process valid notification data file', async () => {
      const testData: ProcessedBookData = {
        processingDate: '2025-10-31T10:00:00.000Z',
        totalBooksFound: 2,
        successfullyProcessed: [
          {
            title: '測試書籍1',
            author: '測試作者1',
            summary: '這是測試摘要1',
            downloadUrl: 'https://example.com/book1.pdf',
            processingMethod: 'pdf_extract',
            processingSuccess: true,
            filename: 'book1.pdf'
          },
          {
            title: '測試書籍2',
            summary: '這是測試摘要2',
            downloadUrl: 'https://example.com/book2.pdf',
            processingMethod: 'google_search',
            processingSuccess: true
          }
        ],
        processingStats: {
          booksProcessed: 2,
          booksFailed: 0,
          pdfExtractions: 1,
          googleSearches: 1,
          networkFailures: 0,
          processingTimeSeconds: 120.5
        }
      };

      // 寫入測試檔案
      const testFile = path.join(testDir, 'notification_data_latest.json');
      await fs.writeFile(testFile, JSON.stringify(testData, null, 2), 'utf-8');

      // 手動處理檔案
      const result = await service.processFileManually(testFile);

      expect(result.processingDate).toBe(testData.processingDate);
      expect(result.totalBooksFound).toBe(2);
      expect(result.successfullyProcessed).toHaveLength(2);
      expect(result.successfullyProcessed[0]?.title).toBe('測試書籍1');
      expect(result.successfullyProcessed[0]?.author).toBe('測試作者1');
      expect(result.successfullyProcessed[1]?.processingMethod).toBe('google_search');
    });

    test('should handle malformed JSON gracefully', async () => {
      const testFile = path.join(testDir, 'notification_data_latest.json');
      await fs.writeFile(testFile, '{ invalid json }', 'utf-8');

      await expect(service.processFileManually(testFile)).rejects.toThrow('Failed to parse JSON');
    });

    test('should handle empty file gracefully', async () => {
      const testFile = path.join(testDir, 'notification_data_latest.json');
      await fs.writeFile(testFile, '', 'utf-8');

      await expect(service.processFileManually(testFile)).rejects.toThrow('File is empty');
    });

    test('should handle missing required fields gracefully', async () => {
      const invalidData = {
        // Missing processingDate - but it will be provided as default
        totalBooksFound: 1,
        successfullyProcessed: [{
          title: '', // Empty title should be handled gracefully
          summary: 'test',
          downloadUrl: 'test',
          processingMethod: 'pdf_extract',
          processingSuccess: true
        }],
        processingStats: {}
      };

      const testFile = path.join(testDir, 'notification_data_latest.json');
      await fs.writeFile(testFile, JSON.stringify(invalidData), 'utf-8');

      const result = await service.processFileManually(testFile);
      
      // Should process successfully but mark the book as failed
      expect(result.totalBooksFound).toBe(1);
      expect(result.successfullyProcessed).toHaveLength(1);
      expect(result.successfullyProcessed[0]?.title).toContain('轉換失敗的書籍');
      expect(result.successfullyProcessed[0]?.processingSuccess).toBe(false);
      expect(result.successfullyProcessed[0]?.errorMessage).toContain('Book title is required');
    });
  });

  describe('File Discovery', () => {
    test('should find latest notification file', async () => {
      // 創建 latest 檔案
      const latestFile = path.join(testDir, 'notification_data_latest.json');
      const testData = { processingDate: '2025-10-31T10:00:00.000Z', totalBooksFound: 0, successfullyProcessed: [], processingStats: { booksProcessed: 0, booksFailed: 0, pdfExtractions: 0, googleSearches: 0 } };
      await fs.writeFile(latestFile, JSON.stringify(testData), 'utf-8');

      const foundFile = await service.findLatestProcessedFile();
      expect(foundFile).toBe(latestFile);
    });

    test('should find timestamped file when latest is missing', async () => {
      // 創建時間戳檔案
      const timestampedFile = path.join(testDir, 'notification_data_20251031_100000.json');
      const testData = { processingDate: '2025-10-31T10:00:00.000Z', totalBooksFound: 0, successfullyProcessed: [], processingStats: { booksProcessed: 0, booksFailed: 0, pdfExtractions: 0, googleSearches: 0 } };
      await fs.writeFile(timestampedFile, JSON.stringify(testData), 'utf-8');

      const foundFile = await service.findLatestProcessedFile();
      expect(foundFile).toBe(timestampedFile);
    });

    test('should return null when no files found', async () => {
      const foundFile = await service.findLatestProcessedFile();
      expect(foundFile).toBeNull();
    });
  });

  describe('Fallback Mechanisms', () => {
    test('should return empty result when no files exist', async () => {
      const result = await service.getProcessingResultWithFallback();

      expect(result.source).toBe('empty');
      expect(result.data.totalBooksFound).toBe(0);
      expect(result.data.successfullyProcessed).toHaveLength(0);
      expect(result.message).toContain('No processing files found');
    });

    test('should return error result when file is corrupted', async () => {
      // 創建損壞的檔案
      const corruptedFile = path.join(testDir, 'notification_data_latest.json');
      await fs.writeFile(corruptedFile, '{ corrupted json', 'utf-8');

      const result = await service.getProcessingResultWithFallback();

      expect(result.source).toBe('error');
      expect(result.data.totalBooksFound).toBe(0);
      expect(result.message).toContain('Failed to process file');
    });

    test('should create valid empty processing result', () => {
      const emptyResult = service.createEmptyProcessingResult();

      expect(emptyResult.totalBooksFound).toBe(0);
      expect(emptyResult.successfullyProcessed).toHaveLength(0);
      expect(emptyResult.processingStats.booksProcessed).toBe(0);
      expect(emptyResult.processingStats.booksFailed).toBe(0);
      expect(emptyResult.processingDate).toBeDefined();
    });
  });

  describe('Status Monitoring', () => {
    test('should check Python processor status correctly', async () => {
      // 創建最近的檔案
      const recentFile = path.join(testDir, 'notification_data_latest.json');
      const testData = { processingDate: new Date().toISOString(), totalBooksFound: 0, successfullyProcessed: [], processingStats: { booksProcessed: 0, booksFailed: 0, pdfExtractions: 0, googleSearches: 0 } };
      await fs.writeFile(recentFile, JSON.stringify(testData), 'utf-8');

      const status = await service.checkPythonProcessorStatus();

      expect(status.hasRecentData).toBe(true);
      expect(status.lastProcessingTime).toBeDefined();
    });

    test('should return correct status when no files exist', async () => {
      const status = await service.checkPythonProcessorStatus();

      expect(status.isRunning).toBe(false);
      expect(status.hasRecentData).toBe(false);
      expect(status.lastProcessingTime).toBeUndefined();
    });
  });

  describe('File Monitoring', () => {
    test('should start and stop monitoring successfully', async () => {
      await service.startMonitoring();
      
      const status = service.getStatus();
      expect(status.isMonitoring).toBe(true);
      expect(status.watchDirectory).toBe(testDir);

      service.stopMonitoring();
      
      const stoppedStatus = service.getStatus();
      expect(stoppedStatus.isMonitoring).toBe(false);
    });

    test('should emit events when files are processed', (done) => {
      const testData = {
        processingDate: new Date().toISOString(),
        totalBooksFound: 1,
        successfullyProcessed: [{
          title: '測試書籍',
          summary: '測試摘要',
          downloadUrl: 'https://example.com/test.pdf',
          processingMethod: 'pdf_extract' as const,
          processingSuccess: true
        }],
        processingStats: {
          booksProcessed: 1,
          booksFailed: 0,
          pdfExtractions: 1,
          googleSearches: 0
        }
      };

      service.on('books-processed', (data: ProcessedBookData, filePath: string) => {
        expect(data.totalBooksFound).toBe(1);
        expect(data.successfullyProcessed).toHaveLength(1);
        expect(filePath).toContain('notification_data_latest.json');
        done();
      });

      service.startMonitoring().then(async () => {
        // 寫入測試檔案觸發事件
        const testFile = path.join(testDir, 'notification_data_latest.json');
        await fs.writeFile(testFile, JSON.stringify(testData, null, 2), 'utf-8');
      });
    }, 10000); // 10 秒超時
  });
});