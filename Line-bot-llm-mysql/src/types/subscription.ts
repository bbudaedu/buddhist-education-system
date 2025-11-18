/**
 * User subscription and notification related type definitions
 */

/**
 * Notification types that users can subscribe to
 */
export type NotificationType = 'new_books' | 'news' | 'cancellation';

/**
 * User subscription preferences for daily book notifications
 */
export interface UserSubscription {
  id: number;
  lineUserId: string;
  displayName: string | undefined;
  isSubscribed: boolean;
  notificationTypes: NotificationType[]; // Types of notifications user subscribed to
  subscriptionDate: Date;
  lastNotificationSent: Date | undefined;
  notificationPreferences: NotificationPreferences;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Notification preferences for individual users
 */
export interface NotificationPreferences {
  enableSummary: boolean; // Include AI-generated summary
  enableDownloadLink: boolean; // Include PDF download link
  maxBooksPerNotification: number; // Limit books per message
}

/**
 * Daily notification processing log entry
 */
export interface NotificationLog {
  id: number;
  processingDate: Date;
  totalRecipients: number;
  successfulDeliveries: number;
  failedDeliveries: number;
  booksProcessed: number;
  processingDurationSeconds: number | undefined;
  createdAt: Date;
}

/**
 * Delivery failure tracking for debugging and retry logic
 */
export interface DeliveryFailure {
  id: number;
  notificationLogId: number | undefined;
  lineUserId: string;
  errorType: DeliveryErrorType;
  errorMessage: string;
  isRetryable: boolean;
  retryCount: number;
  createdAt: Date;
}

/**
 * Types of delivery errors that can occur
 */
export enum DeliveryErrorType {
  USER_BLOCKED = 'user_blocked',
  INVALID_USER = 'invalid_user',
  RATE_LIMIT = 'rate_limit',
  API_ERROR = 'api_error'
}

/**
 * Database row representation for user_subscriptions table
 */
export interface UserSubscriptionRow {
  id: number;
  line_user_id: string;
  display_name: string | null;
  is_subscribed: boolean;
  notification_types: string; // JSON array of notification types
  subscription_date: Date;
  last_notification_sent: Date | null;
  notification_preferences: string; // JSON string
  created_at: Date;
  updated_at: Date;
}

/**
 * Database row representation for notification_logs table
 */
export interface NotificationLogRow {
  id: number;
  processing_date: Date;
  total_recipients: number;
  successful_deliveries: number;
  failed_deliveries: number;
  books_processed: number;
  processing_duration_seconds: number | null;
  created_at: Date;
}

/**
 * Database row representation for delivery_failures table
 */
export interface DeliveryFailureRow {
  id: number;
  notification_log_id?: number;
  line_user_id: string;
  error_type: string;
  error_message: string;
  is_retryable: boolean;
  retry_count: number;
  created_at: Date;
}

/**
 * Comprehensive delivery metrics for monitoring and analysis
 */
export interface DeliveryMetrics {
  totalRecipients: number;
  successfulDeliveries: number;
  failedDeliveries: number;
  successRate: number; // Percentage
  averageProcessingTime: number; // Seconds
  totalNotifications: number;
  errorBreakdown: ErrorBreakdown[];
  dailyTrend: DailyTrendData[];
  recentDeliveries: NotificationLog[];
}

/**
 * Error breakdown by type for metrics analysis
 */
export interface ErrorBreakdown {
  errorType: string;
  count: number;
  retryableCount: number;
}

/**
 * Daily trend data for delivery metrics
 */
export interface DailyTrendData {
  date: Date;
  totalRecipients: number;
  successfulDeliveries: number;
  failedDeliveries: number;
}