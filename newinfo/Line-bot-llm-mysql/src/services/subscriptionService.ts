import mysql from 'mysql2/promise';
import { config } from '../config';
import {
  UserSubscription,
  NotificationPreferences,
  UserSubscriptionRow,
  NotificationLog,
  NotificationLogRow,
  DeliveryFailure,
  DeliveryFailureRow,
  DeliveryErrorType,
  DeliveryMetrics
} from '../types/subscription';

/**
 * Service for managing user subscriptions and notification tracking
 */
export class SubscriptionService {
  private pool: mysql.Pool;

  constructor() {
    // 使用與 DatabaseService 相同的連線池配置
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
   * 訂閱用戶到每日書籍通知
   * @param lineUserId LINE 用戶 ID
   * @param displayName 用戶顯示名稱（可選）
   * @returns Promise<boolean> 訂閱是否成功
   */
  async subscribeUser(lineUserId: string, displayName?: string): Promise<boolean> {
    try {
      const defaultPreferences: NotificationPreferences = {
        enableSummary: true,
        enableDownloadLink: true,
        maxBooksPerNotification: 5
      };

      const sql = `
        INSERT INTO user_subscriptions 
        (line_user_id, display_name, is_subscribed, notification_preferences)
        VALUES (?, ?, TRUE, ?)
        ON DUPLICATE KEY UPDATE
        is_subscribed = TRUE,
        display_name = COALESCE(VALUES(display_name), display_name),
        updated_at = CURRENT_TIMESTAMP
      `;

      await this.pool.execute(sql, [
        lineUserId,
        displayName || null,
        JSON.stringify(defaultPreferences)
      ]);

      return true;
    } catch (error) {
      console.error('Error subscribing user:', error);
      return false;
    }
  }

  /**
   * 取消用戶訂閱
   * @param lineUserId LINE 用戶 ID
   * @returns Promise<boolean> 取消訂閱是否成功
   */
  async unsubscribeUser(lineUserId: string): Promise<boolean> {
    try {
      const sql = `
        UPDATE user_subscriptions 
        SET is_subscribed = FALSE, updated_at = CURRENT_TIMESTAMP
        WHERE line_user_id = ?
      `;

      const [result] = await this.pool.execute(sql, [lineUserId]);
      return (result as mysql.ResultSetHeader).affectedRows > 0;
    } catch (error) {
      console.error('Error unsubscribing user:', error);
      return false;
    }
  }

  /**
   * 檢查用戶是否已訂閱
   * @param lineUserId LINE 用戶 ID
   * @returns Promise<boolean> 用戶是否已訂閱
   */
  async isUserSubscribed(lineUserId: string): Promise<boolean> {
    try {
      const [rows] = await this.pool.execute(
        'SELECT is_subscribed FROM user_subscriptions WHERE line_user_id = ?',
        [lineUserId]
      );

      const subscriptions = rows as { is_subscribed: number | boolean }[];
      if (subscriptions.length === 0) {
        return false;
      }
      
      const isSubscribed = subscriptions[0]?.is_subscribed;
      // 處理 MySQL 的 TINYINT(1) 可能回傳 1/0 或 true/false
      return isSubscribed === true || isSubscribed === 1;
    } catch (error) {
      console.error('Error checking user subscription:', error);
      return false;
    }
  }

  /**
   * 取得所有已訂閱的用戶
   * @returns Promise<UserSubscription[]> 已訂閱用戶列表
   */
  async getSubscribedUsers(): Promise<UserSubscription[]> {
    try {
      const [rows] = await this.pool.execute(
        'SELECT * FROM user_subscriptions WHERE is_subscribed = TRUE ORDER BY subscription_date ASC'
      );

      return (rows as UserSubscriptionRow[]).map(this.mapRowToUserSubscription);
    } catch (error) {
      console.error('Error getting subscribed users:', error);
      throw new Error('Failed to get subscribed users');
    }
  }

  /**
   * 取得用戶訂閱資訊
   * @param lineUserId LINE 用戶 ID
   * @returns Promise<UserSubscription | null> 用戶訂閱資訊或 null
   */
  async getUserSubscription(lineUserId: string): Promise<UserSubscription | null> {
    try {
      const [rows] = await this.pool.execute(
        'SELECT * FROM user_subscriptions WHERE line_user_id = ?',
        [lineUserId]
      );

      const subscriptions = rows as UserSubscriptionRow[];
      return subscriptions.length > 0 && subscriptions[0] ? this.mapRowToUserSubscription(subscriptions[0]) : null;
    } catch (error) {
      console.error('Error getting user subscription:', error);
      return null;
    }
  }

  /**
   * 更新用戶最後通知發送時間
   * @param lineUserId LINE 用戶 ID
   * @returns Promise<void>
   */
  async updateLastNotificationSent(lineUserId: string): Promise<void> {
    try {
      await this.pool.execute(
        'UPDATE user_subscriptions SET last_notification_sent = CURRENT_TIMESTAMP WHERE line_user_id = ?',
        [lineUserId]
      );
    } catch (error) {
      console.error('Error updating last notification sent:', error);
      throw new Error('Failed to update last notification sent time');
    }
  }

  /**
   * 更新用戶通知偏好設定
   * @param lineUserId LINE 用戶 ID
   * @param preferences 通知偏好設定
   * @returns Promise<boolean> 更新是否成功
   */
  async updateNotificationPreferences(
    lineUserId: string, 
    preferences: NotificationPreferences
  ): Promise<boolean> {
    try {
      const sql = `
        UPDATE user_subscriptions 
        SET notification_preferences = ?, updated_at = CURRENT_TIMESTAMP
        WHERE line_user_id = ?
      `;

      const [result] = await this.pool.execute(sql, [
        JSON.stringify(preferences),
        lineUserId
      ]);

      return (result as mysql.ResultSetHeader).affectedRows > 0;
    } catch (error) {
      console.error('Error updating notification preferences:', error);
      return false;
    }
  }

  /**
   * 記錄通知處理日誌
   * @param logData 通知處理日誌資料
   * @returns Promise<number> 日誌記錄 ID
   */
  async createNotificationLog(logData: {
    processingDate: Date;
    totalRecipients: number;
    successfulDeliveries: number;
    failedDeliveries: number;
    booksProcessed: number;
    processingDurationSeconds?: number;
  }): Promise<number> {
    try {
      const sql = `
        INSERT INTO notification_logs 
        (processing_date, total_recipients, successful_deliveries, failed_deliveries, books_processed, processing_duration_seconds)
        VALUES (?, ?, ?, ?, ?, ?)
      `;

      const [result] = await this.pool.execute(sql, [
        logData.processingDate,
        logData.totalRecipients,
        logData.successfulDeliveries,
        logData.failedDeliveries,
        logData.booksProcessed,
        logData.processingDurationSeconds || null
      ]);

      return (result as mysql.ResultSetHeader).insertId;
    } catch (error) {
      console.error('Error creating notification log:', error);
      throw new Error('Failed to create notification log');
    }
  }

  /**
   * 記錄發送失敗
   * @param failureData 發送失敗資料
   * @returns Promise<void>
   */
  async recordDeliveryFailure(failureData: {
    notificationLogId?: number;
    lineUserId: string;
    errorType: DeliveryErrorType;
    errorMessage: string;
    isRetryable: boolean;
    retryCount?: number;
  }): Promise<void> {
    try {
      const sql = `
        INSERT INTO delivery_failures 
        (notification_log_id, line_user_id, error_type, error_message, is_retryable, retry_count)
        VALUES (?, ?, ?, ?, ?, ?)
      `;

      await this.pool.execute(sql, [
        failureData.notificationLogId || null,
        failureData.lineUserId,
        failureData.errorType,
        failureData.errorMessage,
        failureData.isRetryable,
        failureData.retryCount || 0
      ]);
    } catch (error) {
      console.error('Error recording delivery failure:', error);
      throw new Error('Failed to record delivery failure');
    }
  }

  /**
   * 取得通知處理統計
   * @param days 過去幾天的統計，預設 30 天
   * @returns Promise<NotificationLog[]> 通知處理日誌列表
   */
  async getNotificationStats(days: number = 30): Promise<NotificationLog[]> {
    try {
      const sql = `
        SELECT * FROM notification_logs 
        WHERE processing_date >= DATE_SUB(CURDATE(), INTERVAL ? DAY)
        ORDER BY processing_date DESC
      `;

      const [rows] = await this.pool.execute(sql, [days]);
      return (rows as NotificationLogRow[]).map(this.mapRowToNotificationLog);
    } catch (error) {
      console.error('Error getting notification stats:', error);
      throw new Error('Failed to get notification statistics');
    }
  }

  /**
   * 取得訂閱用戶統計
   * @returns Promise<{total: number, active: number}> 訂閱統計
   */
  async getSubscriptionStats(): Promise<{ total: number; active: number }> {
    try {
      const [rows] = await this.pool.execute(`
        SELECT 
          COUNT(*) as total,
          SUM(CASE WHEN is_subscribed = TRUE THEN 1 ELSE 0 END) as active
        FROM user_subscriptions
      `);

      const stats = (rows as any[])[0];
      return {
        total: stats.total || 0,
        active: stats.active || 0
      };
    } catch (error) {
      console.error('Error getting subscription stats:', error);
      throw new Error('Failed to get subscription statistics');
    }
  }



  /**
   * 取得需要重試的發送失敗記錄
   * @param maxRetryCount 最大重試次數，預設 3
   * @returns Promise<DeliveryFailure[]> 需要重試的失敗記錄
   */
  async getRetryableFailures(maxRetryCount: number = 3): Promise<DeliveryFailure[]> {
    try {
      const [rows] = await this.pool.execute(`
        SELECT df.*, nl.processing_date
        FROM delivery_failures df
        JOIN notification_logs nl ON df.notification_log_id = nl.id
        WHERE df.is_retryable = TRUE 
        AND df.retry_count < ?
        AND df.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        ORDER BY df.created_at ASC
      `, [maxRetryCount]);

      return (rows as DeliveryFailureRow[]).map(this.mapRowToDeliveryFailure);
    } catch (error) {
      console.error('Error getting retryable failures:', error);
      throw new Error('Failed to get retryable failures');
    }
  }

  /**
   * 更新發送失敗的重試次數
   * @param failureId 失敗記錄 ID
   * @returns Promise<void>
   */
  async incrementRetryCount(failureId: number): Promise<void> {
    try {
      await this.pool.execute(
        'UPDATE delivery_failures SET retry_count = retry_count + 1 WHERE id = ?',
        [failureId]
      );
    } catch (error) {
      console.error('Error incrementing retry count:', error);
      throw new Error('Failed to increment retry count');
    }
  }

  /**
   * 標記用戶為非活躍狀態（因為持續發送失敗）
   * @param lineUserId LINE 用戶 ID
   * @param reason 標記原因
   * @returns Promise<void>
   */
  async markUserInactive(lineUserId: string, reason: string): Promise<void> {
    try {
      // 取消用戶訂閱但保留記錄
      await this.pool.execute(`
        UPDATE user_subscriptions 
        SET is_subscribed = FALSE, 
            notification_preferences = JSON_SET(
              notification_preferences, 
              '$.inactiveReason', ?,
              '$.inactiveDate', NOW()
            ),
            updated_at = CURRENT_TIMESTAMP
        WHERE line_user_id = ?
      `, [reason, lineUserId]);

      console.log(`User ${lineUserId} marked as inactive: ${reason}`);
    } catch (error) {
      console.error('Error marking user inactive:', error);
      throw new Error('Failed to mark user as inactive');
    }
  }

  /**
   * 關閉資料庫連線池
   * @returns Promise<void>
   */
  async closeConnection(): Promise<void> {
    try {
      await this.pool.end();
      console.log('SubscriptionService database connection pool closed');
    } catch (error) {
      console.error('Error closing SubscriptionService database connection:', error);
      throw new Error('Failed to close SubscriptionService database connection');
    }
  }

  /**
   * 將資料庫行映射為 UserSubscription 物件
   * @private
   */
  private mapRowToUserSubscription(row: UserSubscriptionRow): UserSubscription {
    // 處理 notification_preferences 欄位
    let notificationPreferences;
    if (typeof row.notification_preferences === 'string') {
      try {
        notificationPreferences = JSON.parse(row.notification_preferences);
      } catch (error) {
        console.warn('Failed to parse notification_preferences, using default:', error instanceof Error ? error.message : String(error));
        notificationPreferences = {
          enableSummary: true,
          enableDownloadLink: true,
          maxBooksPerNotification: 5
        };
      }
    } else if (typeof row.notification_preferences === 'object' && row.notification_preferences !== null) {
      // 已經是物件，直接使用
      notificationPreferences = row.notification_preferences;
    } else {
      // 使用預設值
      notificationPreferences = {
        enableSummary: true,
        enableDownloadLink: true,
        maxBooksPerNotification: 5
      };
    }

    return {
      id: row.id,
      lineUserId: row.line_user_id,
      displayName: row.display_name ?? undefined,
      isSubscribed: row.is_subscribed,
      subscriptionDate: row.subscription_date,
      lastNotificationSent: row.last_notification_sent ?? undefined,
      notificationPreferences,
      createdAt: row.created_at,
      updatedAt: row.updated_at
    };
  }

  /**
   * 將資料庫行映射為 NotificationLog 物件
   * @private
   */
  private mapRowToNotificationLog(row: NotificationLogRow): NotificationLog {
    return {
      id: row.id,
      processingDate: row.processing_date,
      totalRecipients: row.total_recipients,
      successfulDeliveries: row.successful_deliveries,
      failedDeliveries: row.failed_deliveries,
      booksProcessed: row.books_processed,
      processingDurationSeconds: row.processing_duration_seconds ?? undefined,
      createdAt: row.created_at
    };
  }

  /**
   * 將資料庫行映射為 DeliveryFailure 物件
   * @private
   */
  private mapRowToDeliveryFailure(row: DeliveryFailureRow): DeliveryFailure {
    return {
      id: row.id,
      notificationLogId: row.notification_log_id,
      lineUserId: row.line_user_id,
      errorType: row.error_type as DeliveryErrorType,
      errorMessage: row.error_message,
      isRetryable: row.is_retryable,
      retryCount: row.retry_count,
      createdAt: row.created_at
    };
  }

  /**
   * 取得投遞統計指標
   * @returns Promise<DeliveryMetrics> 投遞統計資料
   */
  async getDeliveryMetrics(): Promise<DeliveryMetrics> {
    try {
      // 取得所有通知日誌
      const notificationLogs = await this.getAllNotificationLogs();
      
      // 計算統計資料
      const totalNotifications = notificationLogs.length;
      const totalRecipients = notificationLogs.reduce((sum: number, log: NotificationLog) => sum + log.totalRecipients, 0);
      const successfulDeliveries = notificationLogs.reduce((sum: number, log: NotificationLog) => sum + log.successfulDeliveries, 0);
      const failedDeliveries = notificationLogs.reduce((sum: number, log: NotificationLog) => sum + log.failedDeliveries, 0);
      
      const successRate = totalRecipients > 0 ? (successfulDeliveries / totalRecipients) * 100 : 0;
      
      // 計算平均處理時間
      const logsWithDuration = notificationLogs.filter((log: NotificationLog) => log.processingDurationSeconds !== undefined);
      const averageProcessingTime = logsWithDuration.length > 0 
        ? logsWithDuration.reduce((sum: number, log: NotificationLog) => sum + (log.processingDurationSeconds || 0), 0) / logsWithDuration.length
        : 0;

      // 取得最近的投遞記錄（最多 10 筆）
      const recentDeliveries = notificationLogs
        .sort((a: NotificationLog, b: NotificationLog) => b.processingDate.getTime() - a.processingDate.getTime())
        .slice(0, 10);

      return {
        totalRecipients,
        successfulDeliveries,
        failedDeliveries,
        successRate,
        averageProcessingTime,
        totalNotifications,
        errorBreakdown: [], // TODO: 實作錯誤分析
        dailyTrend: [], // TODO: 實作每日趨勢
        recentDeliveries
      };
    } catch (error) {
      console.error('Error getting delivery metrics:', error);
      
      // 回傳空的統計資料
      return {
        totalRecipients: 0,
        successfulDeliveries: 0,
        failedDeliveries: 0,
        successRate: 0,
        averageProcessingTime: 0,
        totalNotifications: 0,
        errorBreakdown: [],
        dailyTrend: [],
        recentDeliveries: []
      };
    }
  }

  /**
   * 取得所有通知日誌
   * @returns Promise<NotificationLog[]> 通知日誌列表
   */
  private async getAllNotificationLogs(): Promise<NotificationLog[]> {
    try {
      const [rows] = await this.pool.execute(
        'SELECT * FROM notification_logs ORDER BY processing_date DESC'
      );

      return (rows as NotificationLogRow[]).map(row => this.mapRowToNotificationLog(row));
    } catch (error) {
      console.error('Error getting notification logs:', error);
      return [];
    }
  }
}

// 建立單例實例
export const subscriptionService = new SubscriptionService();