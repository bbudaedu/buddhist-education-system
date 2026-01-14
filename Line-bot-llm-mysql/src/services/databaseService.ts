import mysql from 'mysql2/promise';
import { promises as fs } from 'fs';
import { join } from 'path';
import { Book } from '../types/book';
import { config } from '../config';

/**
 * Database service for managing book queries and database connections
 */
export class DatabaseService {
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
      // 使用字符串拼接的方式來避免 LIMIT 參數問題
      const sql = 'SELECT book_id, title, quantity_3f as quantity, shelf_location_3f as shelf_location, "3F" as library_branch FROM books_3f WHERE title LIKE ? LIMIT ' + limit;
      const [rows] = await this.pool.execute(sql, [`%${query}%`]);

      return rows as Book[];
    } catch (error) {
      console.error('Database search error:', error);
      throw new Error('Failed to search books in database');
    }
  }

  /**
   * 根據館藏地搜尋書籍，按庫存量排序
   * @param branch 館藏地名稱（如：五股、3F、2F）
   * @param limit 最多回傳幾筆結果，預設 10
   * @returns Promise<Book[]> 符合條件的書籍陣列，按庫存量降序排列
   */
  async searchBooksByBranch(branch: string, limit: number = 10): Promise<Book[]> {
    try {
      const sql = 'SELECT book_id, title, quantity_3f as quantity, shelf_location_3f as shelf_location, "3F" as library_branch FROM books_3f WHERE ? IN (shelf_location_3f, shelf_location_2f, shelf_location_5gu) ORDER BY CAST(quantity_3f AS UNSIGNED) DESC LIMIT ' + limit;
      const [rows] = await this.pool.execute(sql, [branch]);

      return rows as Book[];
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
  async getBookById(bookId: number): Promise<Book | null> {
    try {
      const [rows] = await this.pool.execute(
        'SELECT book_id, title, quantity_3f as quantity, shelf_location_3f as shelf_location, "3F" as library_branch FROM books_3f WHERE book_id = ?',
        [bookId]
      );

      const books = rows as Book[];
      return books.length > 0 ? books[0] || null : null;
    } catch (error) {
      console.error('Database getBookById error:', error);
      throw new Error('Failed to get book by ID from database');
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
   * 取得資料庫連線
   * @returns Promise<mysql.PoolConnection> 資料庫連線
   */
  async getConnection(): Promise<mysql.PoolConnection> {
    return await this.pool.getConnection();
  }

  /**
   * 同步法寶資料到資料庫
   * @param books 書籍資料陣列
   * @returns Promise<{ inserted: number, updated: number }> 同步結果
   */
  async syncDharmaBooks(books: any[]): Promise<{ inserted: number, updated: number }> {
    let inserted = 0;
    let updated = 0;

    try {
      const connection = await this.pool.getConnection();

      try {
        await connection.beginTransaction();

        for (const book of books) {
          // 檢查書籍是否存在 (根據 URL)
          const [existing] = await connection.execute(
            'SELECT id FROM dharma_books WHERE url = ?',
            [book.pdfUrl || '']
          );

          if ((existing as any[]).length > 0) {
            // 更新現有書籍
            await connection.execute(
              `UPDATE dharma_books 
               SET title = ?, author = ?, cover_image_url = ?, publish_date = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE url = ?`,
              [book.title, book.author, book.coverImageUrl, book.publishDate, book.pdfUrl]
            );
            updated++;
          } else {
            // 新增書籍
            await connection.execute(
              `INSERT INTO dharma_books (title, author, cover_image_url, pdf_url, url, publish_date) 
               VALUES (?, ?, ?, ?, ?, ?)`,
              [book.title, book.author, book.coverImageUrl, book.pdfUrl, book.pdfUrl, book.publishDate]
            );
            inserted++;
          }
        }

        await connection.commit();
        return { inserted, updated };
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        connection.release();
      }
    } catch (error) {
      console.error('Sync dharma books error:', error);
      throw new Error('Failed to sync dharma books');
    }
  }

  /**
   * 執行資料庫遷移
   * @returns Promise<void>
   */
  async runMigrations(): Promise<void> {
    try {
      // 建立 migrations 表格來追蹤已執行的遷移
      await this.createMigrationsTable();

      // 取得已執行的遷移
      const executedMigrations = await this.getExecutedMigrations();

      // 讀取遷移檔案
      const migrationsDir = join(process.cwd(), 'migrations');
      const migrationFiles = await fs.readdir(migrationsDir);

      // 過濾並排序 SQL 檔案
      const sqlFiles = migrationFiles
        .filter(file => file.endsWith('.sql'))
        .sort();

      console.log(`Found ${sqlFiles.length} migration files`);

      // 執行未執行的遷移
      for (const file of sqlFiles) {
        if (!executedMigrations.includes(file)) {
          console.log(`Executing migration: ${file}`);
          await this.executeMigration(file);
          await this.recordMigration(file);
          console.log(`Migration completed: ${file}`);
        } else {
          console.log(`Migration already executed: ${file}`);
        }
      }

      console.log('All migrations completed successfully');
    } catch (error) {
      console.error('Migration error:', error);
      throw new Error('Failed to run database migrations');
    }
  }

  /**
   * 建立 migrations 表格
   * @private
   */
  private async createMigrationsTable(): Promise<void> {
    const sql = `
      CREATE TABLE IF NOT EXISTS migrations (
        id INT PRIMARY KEY AUTO_INCREMENT,
        filename VARCHAR(255) UNIQUE NOT NULL,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `;
    await this.pool.execute(sql);
  }

  /**
   * 取得已執行的遷移列表
   * @private
   * @returns Promise<string[]>
   */
  private async getExecutedMigrations(): Promise<string[]> {
    try {
      const [rows] = await this.pool.execute('SELECT filename FROM migrations');
      return (rows as any[]).map(row => row.filename);
    } catch (error) {
      // 如果 migrations 表格不存在，回傳空陣列
      return [];
    }
  }

  /**
   * 執行單一遷移檔案
   * @private
   * @param filename 遷移檔案名稱
   */
  private async executeMigration(filename: string): Promise<void> {
    const migrationsDir = join(process.cwd(), 'migrations');
    const filePath = join(migrationsDir, filename);
    const sql = await fs.readFile(filePath, 'utf-8');

    // 移除註解並分割 SQL 語句
    const statements = sql
      .split('\n')
      .filter(line => !line.trim().startsWith('--') && line.trim() !== '')
      .join('\n')
      .split(';')
      .filter(statement => statement.trim() !== '');

    // 執行每個 SQL 語句
    for (const statement of statements) {
      if (statement.trim()) {
        await this.pool.execute(statement.trim());
      }
    }
  }

  /**
   * 記錄已執行的遷移
   * @private
   * @param filename 遷移檔案名稱
   */
  private async recordMigration(filename: string): Promise<void> {
    await this.pool.execute(
      'INSERT INTO migrations (filename) VALUES (?)',
      [filename]
    );
  }
}

// 建立單例實例
export const databaseService = new DatabaseService();