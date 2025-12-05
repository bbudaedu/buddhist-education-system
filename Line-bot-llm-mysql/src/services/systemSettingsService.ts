import mysql from 'mysql2/promise';
import { config } from '../config';

/**
 * System Settings Service
 * 管理系統層級的設定（如 LLM 開關）
 */

export class SystemSettingsService {
    private pool: mysql.Pool;
    private initPromise: Promise<void>;
    private initialized: boolean = false;
    private settingsCache: Map<string, string> = new Map();

    constructor() {
        this.pool = mysql.createPool({
            host: config.database.host,
            port: config.database.port,
            user: config.database.user,
            password: config.database.password,
            database: config.database.database,
            waitForConnections: true,
            connectionLimit: 5,
            queueLimit: 0,
        });

        this.initPromise = this.initialize();
    }

    /**
     * 初始化服務，創建資料表
     */
    private async initialize(): Promise<void> {
        try {
            await this.createSettingsTable();
            await this.loadSettings();
            this.initialized = true;
            console.log('SystemSettingsService initialized');
        } catch (error) {
            console.error('Error initializing SystemSettingsService:', error);
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
     * 創建系統設定資料表
     */
    private async createSettingsTable(): Promise<void> {
        try {
            await this.pool.execute(`
        CREATE TABLE IF NOT EXISTS system_settings (
          setting_key VARCHAR(100) PRIMARY KEY,
          setting_value VARCHAR(500) NOT NULL,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
      `);
            console.log('System settings table created successfully');
        } catch (error) {
            console.error('Error creating system settings table:', error);
        }
    }

    /**
     * 載入所有設定到記憶體快取
     */
    private async loadSettings(): Promise<void> {
        try {
            const [rows] = await this.pool.execute(
                'SELECT setting_key, setting_value FROM system_settings'
            );

            const settings = rows as { setting_key: string; setting_value: string }[];
            this.settingsCache.clear();
            settings.forEach(s => this.settingsCache.set(s.setting_key, s.setting_value));

            console.log(`Loaded ${this.settingsCache.size} system settings`);
        } catch (error) {
            console.error('Error loading system settings:', error);
        }
    }

    /**
     * 取得設定值
     * @param key 設定鍵
     * @param defaultValue 預設值
     */
    async getSetting(key: string, defaultValue: string = ''): Promise<string> {
        await this.ensureInitialized();
        return this.settingsCache.get(key) ?? defaultValue;
    }

    /**
     * 設定值
     * @param key 設定鍵
     * @param value 設定值
     */
    async setSetting(key: string, value: string): Promise<boolean> {
        try {
            await this.ensureInitialized();
            await this.pool.execute(
                `INSERT INTO system_settings (setting_key, setting_value) 
         VALUES (?, ?) 
         ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)`,
                [key, value]
            );

            this.settingsCache.set(key, value);
            console.log(`Setting updated: ${key} = ${value}`);
            return true;
        } catch (error) {
            console.error('Error setting value:', error);
            return false;
        }
    }

    // ========== LLM 開關專用方法 ==========

    private static readonly LLM_ENABLED_KEY = 'llm_enabled';

    /**
     * 檢查 LLM 是否啟用（預設關閉）
     */
    async isLlmEnabled(): Promise<boolean> {
        const value = await this.getSetting(SystemSettingsService.LLM_ENABLED_KEY, 'false');
        return value === 'true';
    }

    /**
     * 設定 LLM 啟用狀態
     * @param enabled 是否啟用
     */
    async setLlmEnabled(enabled: boolean): Promise<boolean> {
        return this.setSetting(SystemSettingsService.LLM_ENABLED_KEY, enabled ? 'true' : 'false');
    }

    /**
     * 關閉資料庫連線池
     */
    async closeConnection(): Promise<void> {
        try {
            await this.pool.end();
            console.log('SystemSettingsService database connection pool closed');
        } catch (error) {
            console.error('Error closing SystemSettingsService database connection:', error);
        }
    }
}

export const systemSettingsService = new SystemSettingsService();
