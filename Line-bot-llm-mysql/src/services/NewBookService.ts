import mysql from 'mysql2/promise';
import { NewBook, ExcelBookData } from '../types/NewBook';
import { config } from '../config';

/**
 * Service for managing new book data synchronized from the ebook system
 */
export class NewBookService {
  private pool: mysql.Pool;

  constructor() {
    // 建立 MySQL 連線池配置
    this.pool = mysql.createPool({
      host: config.database.host,
      port: config.database.port,
      user: config.database.user,
      password: config.database.password,
      database: config.database.database,
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0,
      charset: 'utf8mb4'
    });
  }

  /**
   * 插入新書資料，如果書號已存在則更新
   * @param bookData 新書資料
   * @returns Promise<number> 插入或更新的記錄 ID
   */
  async upsertNewBook(bookData: ExcelBookData): Promise<number> {
    const connection = await this.pool.getConnection();
    
    try {
      await connection.beginTransaction();

      const sql = `
        INSERT INTO new_books (
          book_code, title, author, pdf_filename, file_size_mb,
          processing_method, summary, download_url, processing_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE
          title = VALUES(title),
          author = VALUES(author),
          pdf_filename = VALUES(pdf_filename),
          file_size_mb = VALUES(file_size_mb),
          processing_method = VALUES(processing_method),
          summary = VALUES(summary),
          download_url = VALUES(download_url),
          processing_timestamp = VALUES(processing_timestamp),
          sync_timestamp = CURRENT_TIMESTAMP,
          updated_at = CURRENT_TIMESTAMP
      `;

      const processingTimestamp = bookData.processing_timestamp 
        ? new Date(bookData.processing_timestamp) 
        : null;

      const values = [
        bookData.book_code,
        bookData.title,
        bookData.author || null,
        bookData.pdf_filename || null,
        bookData.file_size_mb || null,
        bookData.processing_method || null,
        bookData.summary || null,
        bookData.download_url || null,
        processingTimestamp
      ];

      const [result] = await connection.execute(sql, values);
      await connection.commit();

      const insertResult = result as mysql.ResultSetHeader;
      return insertResult.insertId || insertResult.affectedRows;

    } catch (error) {
      await connection.rollback();
      console.error('Error upserting new book:', error);
      throw new Error(`Failed to upsert new book: ${error}`);
    } finally {
      connection.release();
    }
  }

  /**
   * 批量插入新書資料
   * @param booksData 新書資料陣列
   * @returns Promise<number> 成功處理的記錄數
   */
  async batchUpsertNewBooks(booksData: ExcelBookData[]): Promise<number> {
    if (!booksData || booksData.length === 0) {
      return 0;
    }

    const connection = await this.pool.getConnection();
    let successCount = 0;

    try {
      await connection.beginTransaction();

      for (const bookData of booksData) {
        try {
          await this.upsertNewBookWithConnection(connection, bookData);
          successCount++;
        } catch (error) {
          console.error(`Failed to process book ${bookData.book_code}:`, error);
          // 繼續處理其他書籍，不中斷整個批次
        }
      }

      await connection.commit();
      console.log(`Successfully processed ${successCount}/${booksData.length} books`);
      return successCount;

    } catch (error) {
      await connection.rollback();
      console.error('Batch upsert transaction failed:', error);
      throw new Error(`Batch upsert failed: ${error}`);
    } finally {
      connection.release();
    }
  }

  /**
   * 使用現有連線插入新書資料（內部方法）
   * @private
   */
  private async upsertNewBookWithConnection(
    connection: mysql.PoolConnection, 
    bookData: ExcelBookData
  ): Promise<void> {
    const sql = `
      INSERT INTO new_books (
        book_code, title, author, pdf_filename, file_size_mb,
        processing_method, summary, download_url, processing_timestamp
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE
        title = VALUES(title),
        author = VALUES(author),
        pdf_filename = VALUES(pdf_filename),
        file_size_mb = VALUES(file_size_mb),
        processing_method = VALUES(processing_method),
        summary = VALUES(summary),
        download_url = VALUES(download_url),
        processing_timestamp = VALUES(processing_timestamp),
        sync_timestamp = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    `;

    const processingTimestamp = bookData.processing_timestamp 
      ? new Date(bookData.processing_timestamp) 
      : null;

    const values = [
      bookData.book_code,
      bookData.title,
      bookData.author || null,
      bookData.pdf_filename || null,
      bookData.file_size_mb || null,
      bookData.processing_method || null,
      bookData.summary || null,
      bookData.download_url || null,
      processingTimestamp
    ];

    await connection.execute(sql, values);
  }

  /**
   * 取得所有新書資料
   * @param limit 限制回傳筆數，預設 50
   * @param offset 偏移量，預設 0
   * @returns Promise<NewBook[]> 新書資料陣列
   */
  async getAllNewBooks(limit: number = 50, offset: number = 0): Promise<NewBook[]> {
    try {
      const sql = `
        SELECT * FROM new_books 
        ORDER BY sync_timestamp DESC, processing_timestamp DESC 
        LIMIT ? OFFSET ?
      `;
      
      const [rows] = await this.pool.execute(sql, [limit, offset]);
      return rows as NewBook[];
    } catch (error) {
      console.error('Error getting all new books:', error);
      throw new Error('Failed to get new books from database');
    }
  }

  /**
   * 根據書號取得新書資料
   * @param bookCode 書號
   * @returns Promise<NewBook | null> 新書資料或 null
   */
  async getNewBookByCode(bookCode: string): Promise<NewBook | null> {
    try {
      const [rows] = await this.pool.execute(
        'SELECT * FROM new_books WHERE book_code = ?',
        [bookCode]
      );

      const books = rows as NewBook[];
      return books.length > 0 ? books[0]! : null;
    } catch (error) {
      console.error('Error getting new book by code:', error);
      throw new Error('Failed to get new book by code from database');
    }
  }

  /**
   * 搜尋新書資料
   * @param query 搜尋關鍵字（書名、作者）
   * @param limit 限制回傳筆數，預設 10
   * @returns Promise<NewBook[]> 符合條件的新書資料陣列
   */
  async searchNewBooks(query: string, limit: number = 10): Promise<NewBook[]> {
    try {
      const sql = `
        SELECT * FROM new_books 
        WHERE title LIKE ? OR author LIKE ? OR book_code LIKE ?
        ORDER BY sync_timestamp DESC, processing_timestamp DESC 
        LIMIT ?
      `;
      
      const searchPattern = `%${query}%`;
      const [rows] = await this.pool.execute(sql, [
        searchPattern, searchPattern, searchPattern, limit
      ]);

      return rows as NewBook[];
    } catch (error) {
      console.error('Error searching new books:', error);
      throw new Error('Failed to search new books in database');
    }
  }

  /**
   * 取得未通知的新書資料
   * @param limit 限制回傳筆數，預設 10
   * @returns Promise<NewBook[]> 未通知的新書資料陣列
   */
  async getUnnotifiedNewBooks(limit: number = 10): Promise<NewBook[]> {
    try {
      const sql = `
        SELECT * FROM new_books 
        WHERE is_notified = FALSE 
        ORDER BY processing_timestamp DESC, sync_timestamp DESC 
        LIMIT ?
      `;
      
      const [rows] = await this.pool.execute(sql, [limit]);
      return rows as NewBook[];
    } catch (error) {
      console.error('Error getting unnotified new books:', error);
      throw new Error('Failed to get unnotified new books from database');
    }
  }

  /**
   * 標記新書為已通知
   * @param bookCodes 書號陣列
   * @returns Promise<number> 更新的記錄數
   */
  async markBooksAsNotified(bookCodes: string[]): Promise<number> {
    if (!bookCodes || bookCodes.length === 0) {
      return 0;
    }

    try {
      const placeholders = bookCodes.map(() => '?').join(',');
      const sql = `
        UPDATE new_books 
        SET is_notified = TRUE, updated_at = CURRENT_TIMESTAMP 
        WHERE book_code IN (${placeholders})
      `;
      
      const [result] = await this.pool.execute(sql, bookCodes);
      const updateResult = result as mysql.ResultSetHeader;
      return updateResult.affectedRows;
    } catch (error) {
      console.error('Error marking books as notified:', error);
      throw new Error('Failed to mark books as notified');
    }
  }

  /**
   * 取得新書統計資料
   * @returns Promise<object> 統計資料
   */
  async getNewBooksStats(): Promise<{
    total: number;
    notified: number;
    unnotified: number;
    recentCount: number;
  }> {
    try {
      const [totalResult] = await this.pool.execute(
        'SELECT COUNT(*) as count FROM new_books'
      );
      
      const [notifiedResult] = await this.pool.execute(
        'SELECT COUNT(*) as count FROM new_books WHERE is_notified = TRUE'
      );
      
      const [unnotifiedResult] = await this.pool.execute(
        'SELECT COUNT(*) as count FROM new_books WHERE is_notified = FALSE'
      );
      
      const [recentResult] = await this.pool.execute(
        'SELECT COUNT(*) as count FROM new_books WHERE sync_timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)'
      );

      const total = (totalResult as any[])[0].count;
      const notified = (notifiedResult as any[])[0].count;
      const unnotified = (unnotifiedResult as any[])[0].count;
      const recentCount = (recentResult as any[])[0].count;

      return { total, notified, unnotified, recentCount };
    } catch (error) {
      console.error('Error getting new books stats:', error);
      throw new Error('Failed to get new books statistics');
    }
  }

  /**
   * 關閉資料庫連線池
   * @returns Promise<void>
   */
  async closeConnection(): Promise<void> {
    try {
      await this.pool.end();
      console.log('NewBookService database connection pool closed');
    } catch (error) {
      console.error('Error closing NewBookService database connection:', error);
      throw new Error('Failed to close database connection');
    }
  }

  /**
   * 測試資料庫連線
   * @returns Promise<boolean> 連線是否成功
   */
  async testConnection(): Promise<boolean> {
    try {
      const connection = await this.pool.getConnection();
      await connection.ping();
      connection.release();
      return true;
    } catch (error) {
      console.error('NewBookService database connection test failed:', error);
      return false;
    }
  }

  /**
   * 發送網站監控內容的 LINE 通知
   * @param contentData 網站監控內容資料
   * @returns Promise<boolean> 發送是否成功
   */
  async sendWebsiteMonitoringNotification(contentData: {
    [key: string]: Array<{
      id?: string;
      content_type?: string;
      notification_text?: string;
      urgent?: boolean;
      [key: string]: any;
    }>;
  }): Promise<boolean> {
    try {
      // 生成通知訊息
      const messages = this.generateWebsiteMonitoringMessages(contentData);
      
      if (messages.length === 0) {
        console.log('No website monitoring content to notify');
        return true;
      }

      // 這裡應該整合實際的 LINE Bot 發送邏輯
      // 目前先記錄訊息內容
      console.log('Website monitoring notifications to send:');
      messages.forEach((message, index) => {
        console.log(`Message ${index + 1}:`, message);
      });

      return true;
    } catch (error) {
      console.error('Error sending website monitoring notification:', error);
      return false;
    }
  }

  /**
   * 生成網站監控內容的 LINE 訊息
   * @private
   */
  private generateWebsiteMonitoringMessages(contentData: {
    [key: string]: Array<{
      id?: string;
      content_type?: string;
      notification_text?: string;
      urgent?: boolean;
      [key: string]: any;
    }>;
  }): string[] {
    const messages: string[] = [];

    try {
      // 處理緊急通知（課程取消）
      if (contentData.cancellation && contentData.cancellation.length > 0) {
        const urgentMessages = contentData.cancellation.map(item => 
          `🚨 緊急通知\n${item.notification_text || '課程取消通知'}`
        );
        messages.push(...urgentMessages);
      }

      // 處理其他內容類型的摘要通知
      const regularContent = Object.entries(contentData)
        .filter(([type]) => type !== 'cancellation')
        .filter(([, items]) => items && items.length > 0);

      if (regularContent.length > 0) {
        let summaryMessage = '📢 佛教教育網站更新通知\n\n';
        
        regularContent.forEach(([type, items]) => {
          const typeEmoji = this.getContentTypeEmoji(type);
          const typeName = this.getContentTypeName(type);
          
          summaryMessage += `${typeEmoji} ${typeName} (${items.length}項)\n`;
          
          // 顯示前3項內容
          items.slice(0, 3).forEach(item => {
            summaryMessage += `• ${item.notification_text || '新內容'}\n`;
          });
          
          if (items.length > 3) {
            summaryMessage += `... 還有 ${items.length - 3} 項\n`;
          }
          
          summaryMessage += '\n';
        });

        summaryMessage += `查看時間：${new Date().toLocaleString('zh-TW')}`;
        messages.push(summaryMessage);
      }

      return messages;
    } catch (error) {
      console.error('Error generating website monitoring messages:', error);
      return ['網站監控通知生成失敗，請聯繫系統管理員。'];
    }
  }

  /**
   * 取得內容類型的表情符號
   * @private
   */
  private getContentTypeEmoji(contentType: string): string {
    const emojiMap: { [key: string]: string } = {
      'carousel': '🎯',
      'news': '📢',
      'media': '🎥',
      'cancellation': '🚨'
    };
    return emojiMap[contentType] || '📄';
  }

  /**
   * 取得內容類型的中文名稱
   * @private
   */
  private getContentTypeName(contentType: string): string {
    const nameMap: { [key: string]: string } = {
      'carousel': '新活動',
      'news': '最新公告',
      'media': '媒體內容',
      'cancellation': '課程取消'
    };
    return nameMap[contentType] || '其他內容';
  }

  /**
   * 根據優先級發送通知
   * @param contentData 內容資料
   * @param priority 優先級 ('immediate', 'high', 'normal', 'low')
   * @returns Promise<boolean> 發送是否成功
   */
  async sendNotificationByPriority(
    contentData: { [key: string]: any[] },
    priority: 'immediate' | 'high' | 'normal' | 'low'
  ): Promise<boolean> {
    try {
      // 根據優先級過濾內容
      const filteredContent: { [key: string]: any[] } = {};
      
      Object.entries(contentData).forEach(([type, items]) => {
        const contentPriority = this.getContentPriority(type);
        if (this.shouldSendByPriority(contentPriority, priority)) {
          filteredContent[type] = items;
        }
      });

      if (Object.keys(filteredContent).length === 0) {
        console.log(`No content matches priority: ${priority}`);
        return true;
      }

      return await this.sendWebsiteMonitoringNotification(filteredContent);
    } catch (error) {
      console.error('Error sending notification by priority:', error);
      return false;
    }
  }

  /**
   * 取得內容類型的優先級
   * @private
   */
  private getContentPriority(contentType: string): 'immediate' | 'high' | 'normal' | 'low' {
    const priorityMap: { [key: string]: 'immediate' | 'high' | 'normal' | 'low' } = {
      'cancellation': 'immediate',
      'news': 'high',
      'carousel': 'normal',
      'media': 'normal'
    };
    return priorityMap[contentType] || 'normal';
  }

  /**
   * 判斷是否應該根據優先級發送通知
   * @private
   */
  private shouldSendByPriority(
    contentPriority: 'immediate' | 'high' | 'normal' | 'low',
    targetPriority: 'immediate' | 'high' | 'normal' | 'low'
  ): boolean {
    const priorityLevels = {
      'immediate': 4,
      'high': 3,
      'normal': 2,
      'low': 1
    };

    return priorityLevels[contentPriority] >= priorityLevels[targetPriority];
  }
}

// 建立單例實例
export const newBookService = new NewBookService();