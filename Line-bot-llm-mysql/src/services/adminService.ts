import mysql from 'mysql2/promise';
import { config } from '../config';

/**
 * Admin Service
 * 管理員權限管理服務
 */

export interface AdminUser {
  id: number;
  lineUserId: string;
  displayName?: string;
  createdAt: Date;
}

export class AdminService {
  private pool: mysql.Pool;
  private adminUserIds: Set<string> = new Set();
  private initPromise: Promise<void>;
  private initialized: boolean = false;

  constructor() {
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

    // 初始化時先創建資料表，再載入管理員列表
    this.initPromise = this.initialize();
  }

  /**
   * 初始化服務
   */
  private async initialize(): Promise<void> {
    try {
      // 先確保資料表存在
      await this.createAdminTable();
      // 再載入管理員列表
      await this.loadAdminUsers();
      this.initialized = true;
    } catch (error) {
      console.error('Error initializing AdminService:', error);
    }
  }

  /**
   * 確保服務已初始化
   */
  private async ensureInitialized(): Promise<void> {
    if (!this.initialized) {
      await this.initPromise;
    }
  }

  /**
   * 載入管理員列表到記憶體
   */
  private async loadAdminUsers(): Promise<void> {
    try {
      const [rows] = await this.pool.execute(
        'SELECT line_user_id FROM admin_users'
      );

      const admins = rows as { line_user_id: string }[];
      this.adminUserIds.clear();
      admins.forEach(admin => this.adminUserIds.add(admin.line_user_id));

      console.log(`Loaded ${this.adminUserIds.size} admin users`);
    } catch (error) {
      console.error('Error loading admin users:', error);
    }
  }

  /**
   * 創建管理員資料表
   */
  private async createAdminTable(): Promise<void> {
    try {
      await this.pool.execute(`
        CREATE TABLE IF NOT EXISTS admin_users (
          id INT AUTO_INCREMENT PRIMARY KEY,
          line_user_id VARCHAR(255) NOT NULL UNIQUE,
          display_name VARCHAR(255),
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          INDEX idx_line_user_id (line_user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      `);
      console.log('Admin users table created successfully');
    } catch (error) {
      console.error('Error creating admin users table:', error);
    }
  }

  /**
   * 檢查用戶是否為管理員
   */
  async isAdmin(userId: string): Promise<boolean> {
    await this.ensureInitialized();
    return this.adminUserIds.has(userId);
  }

  /**
   * 新增管理員
   */
  async addAdmin(userId: string, displayName?: string): Promise<boolean> {
    try {
      await this.ensureInitialized();
      await this.pool.execute(
        'INSERT INTO admin_users (line_user_id, display_name) VALUES (?, ?) ON DUPLICATE KEY UPDATE display_name = VALUES(display_name)',
        [userId, displayName || null]
      );

      this.adminUserIds.add(userId);
      console.log(`Added admin user: ${userId}`);
      return true;
    } catch (error) {
      console.error('Error adding admin user:', error);
      return false;
    }
  }

  /**
   * 移除管理員
   */
  async removeAdmin(userId: string): Promise<boolean> {
    try {
      await this.ensureInitialized();
      await this.pool.execute(
        'DELETE FROM admin_users WHERE line_user_id = ?',
        [userId]
      );

      this.adminUserIds.delete(userId);
      console.log(`Removed admin user: ${userId}`);
      return true;
    } catch (error) {
      console.error('Error removing admin user:', error);
      return false;
    }
  }

  /**
   * 取得所有管理員列表
   */
  async getAllAdmins(): Promise<AdminUser[]> {
    try {
      await this.ensureInitialized();
      const [rows] = await this.pool.execute(
        'SELECT * FROM admin_users ORDER BY created_at DESC'
      );

      return (rows as any[]).map(row => ({
        id: row.id,
        lineUserId: row.line_user_id,
        displayName: row.display_name,
        createdAt: row.created_at
      }));
    } catch (error) {
      console.error('Error getting admin users:', error);
      return [];
    }
  }

  /**
   * 關閉資料庫連線池
   */
  async closeConnection(): Promise<void> {
    try {
      await this.pool.end();
      console.log('AdminService database connection pool closed');
    } catch (error) {
      console.error('Error closing AdminService database connection:', error);
    }
  }
}

export const adminService = new AdminService();
