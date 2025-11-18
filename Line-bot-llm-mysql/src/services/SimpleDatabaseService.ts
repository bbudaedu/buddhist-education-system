import mysql from 'mysql2/promise';
import { Book } from '../types/book';
import { config } from '../config';

/**
 * 簡化版資料庫服務，只處理書籍查詢功能
 * 不需要建立新表，適用於權限受限的環境
 */
export class SimpleDatabaseService {
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
    });
  }

  /**
   * 搜尋書籍，使用參數化查詢防止 SQL 注入
   * @param query 搜尋關鍵字，可以是書名、作者或相關主題
   * @param limit 最多回傳幾筆結果，預設 10
   * @returns Promise<Book[]> 符合條件的書籍陣列
   */
  async searchBooks(query: string, limit: number = 10): Promise<Book[]> {
    try {
      const sql = `
        SELECT 
          book_id, 
          title, 
          author,
          quantity_3f as quantity, 
          shelf_location_3f as shelf_location, 
          '3F' as library_branch 
        FROM books_3f 
        WHERE title LIKE ? OR author LIKE ?
        LIMIT ${limit}
      `;
      
      const searchPattern = `%${query}%`;
      const [rows] = await this.pool.execute(sql, [searchPattern, searchPattern]);

      return (rows as any[]).map(row => ({
        book_id: row.book_id,
        title: row.title,
        author: row.author,
        quantity: parseInt(row.quantity) || 0,
        shelf_location: row.shelf_location,
        library_branch: row.library_branch
      }));
    } catch (error) {
      console.error('Database search error:', error);
      throw new Error('Failed to search books in database');
    }
  }

  /**
   * 根據館藏地搜尋書籍，按庫存量排序
   * @param branch 館藏地名稱（如：3F、2F、5股）
   * @param limit 最多回傳幾筆結果，預設 10
   * @returns Promise<Book[]> 符合條件的書籍陣列，按庫存量降序排列
   */
  async searchBooksByBranch(branch: string, limit: number = 10): Promise<Book[]> {
    try {
      let sql = '';
      let params: any[] = [];

      if (branch === '3F' || branch === '3f') {
        sql = `
          SELECT 
            book_id, 
            title, 
            author,
            quantity_3f as quantity, 
            shelf_location_3f as shelf_location, 
            '3F' as library_branch 
          FROM books_3f 
          WHERE quantity_3f IS NOT NULL AND quantity_3f != '' 
          ORDER BY CAST(quantity_3f AS UNSIGNED) DESC 
          LIMIT ${limit}
        `;
      } else if (branch === '2F' || branch === '2f') {
        sql = `
          SELECT 
            book_id, 
            title, 
            author,
            inventory_count_2f as quantity, 
            shelf_location_2f as shelf_location, 
            '2F' as library_branch 
          FROM books_3f 
          WHERE inventory_count_2f IS NOT NULL AND inventory_count_2f != '' 
          ORDER BY CAST(inventory_count_2f AS UNSIGNED) DESC 
          LIMIT ${limit}
        `;
      } else if (branch === '5股' || branch === '5gu') {
        sql = `
          SELECT 
            book_id, 
            title, 
            author,
            inventory_count_5gu as quantity, 
            shelf_location_5gu as shelf_location, 
            '5股' as library_branch 
          FROM books_3f 
          WHERE inventory_count_5gu IS NOT NULL AND inventory_count_5gu != '' 
          ORDER BY CAST(inventory_count_5gu AS UNSIGNED) DESC 
          LIMIT ${limit}
        `;
      } else {
        // 搜尋所有館藏地
        sql = `
          SELECT 
            book_id, 
            title, 
            author,
            quantity_3f as quantity, 
            shelf_location_3f as shelf_location, 
            '3F' as library_branch 
          FROM books_3f 
          WHERE quantity_3f IS NOT NULL AND quantity_3f != '' 
          ORDER BY CAST(quantity_3f AS UNSIGNED) DESC 
          LIMIT ${limit}
        `;
      }

      const [rows] = await this.pool.execute(sql, params);

      return (rows as any[]).map(row => ({
        book_id: row.book_id,
        title: row.title,
        author: row.author,
        quantity: parseInt(row.quantity) || 0,
        shelf_location: row.shelf_location,
        library_branch: row.library_branch
      }));
    } catch (error) {
      console.error('Database searchBooksByBranch error:', error);
      throw new Error('Failed to search books by branch in database');
    }
  }

  /**
   * 根據書籍 ID 取得特定書籍資訊
   * @param bookId 書籍唯一識別碼
   * @returns Promise<Book | null> 書籍資訊或 null（如果找不到）
   */
  async getBookById(bookId: string): Promise<Book | null> {
    try {
      const [rows] = await this.pool.execute(
        `SELECT 
          book_id, 
          title, 
          author,
          quantity_3f as quantity, 
          shelf_location_3f as shelf_location, 
          '3F' as library_branch 
        FROM books_3f 
        WHERE book_id = ?`,
        [bookId]
      );

      const books = rows as any[];
      if (books.length === 0) return null;

      const book = books[0];
      return {
        book_id: book.book_id,
        title: book.title,
        author: book.author,
        quantity: parseInt(book.quantity) || 0,
        shelf_location: book.shelf_location,
        library_branch: book.library_branch
      };
    } catch (error) {
      console.error('Database getBookById error:', error);
      throw new Error('Failed to get book by ID from database');
    }
  }

  /**
   * 取得書籍統計資訊
   * @returns Promise<{total: number, available: number}> 書籍統計
   */
  async getBookStats(): Promise<{ total: number; available: number }> {
    try {
      const [rows] = await this.pool.execute(`
        SELECT 
          COUNT(*) as total,
          SUM(CASE WHEN quantity_3f IS NOT NULL AND quantity_3f != '' AND CAST(quantity_3f AS UNSIGNED) > 0 THEN 1 ELSE 0 END) as available
        FROM books_3f
      `);

      const stats = (rows as any[])[0];
      return {
        total: stats.total || 0,
        available: stats.available || 0
      };
    } catch (error) {
      console.error('Error getting book stats:', error);
      throw new Error('Failed to get book statistics');
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
      console.error('Database connection test failed:', error);
      return false;
    }
  }

  /**
   * 關閉資料庫連線池
   * @returns Promise<void>
   */
  async closeConnection(): Promise<void> {
    try {
      await this.pool.end();
      console.log('Database connection pool closed');
    } catch (error) {
      console.error('Error closing database connection:', error);
      throw new Error('Failed to close database connection');
    }
  }
}

// 建立單例實例
export const simpleDatabaseService = new SimpleDatabaseService();