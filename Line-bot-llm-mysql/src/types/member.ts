/**
 * Member Types
 * 會員相關型別定義
 */

/**
 * 會員資料
 */
export interface MemberProfile {
    lineUserId: string;
    displayName: string;
    pictureUrl: string | null;
    email: string | null;
    emailVerified: boolean;
    emailNotificationEnabled: boolean;
    createdAt: Date;
    updatedAt: Date;
}

/**
 * 用戶偏好設定
 */
export interface UserPreferences {
    lineUserId: string;
    preferredContentTypes: ContentType[];
    preferredCategories: string[];
    preferredInstructors: string[];
    notificationChannels: NotificationChannel[];
    notificationFrequency: NotificationFrequency;
    quietHoursStart: string | null;
    quietHoursEnd: string | null;
    quietHoursEnabled: boolean;
}

/**
 * 通知頻率
 */
export type NotificationFrequency = 'realtime' | 'daily' | 'weekly';

/**
 * 通知通道
 */
export type NotificationChannel = 'line' | 'email' | 'webpush';

/**
 * 內容類型
 */
export type ContentType = 'books' | 'videos' | 'livestream' | 'news';

/**
 * Email 驗證請求
 */
export interface SendVerificationRequest {
    email: string;
}

/**
 * Email 驗證確認請求
 */
export interface VerifyEmailRequest {
    email: string;
    code: string;
}

/**
 * 更新偏好請求
 */
export interface UpdatePreferencesRequest {
    notificationChannels?: NotificationChannel[];
    preferredContentTypes?: ContentType[];
    notificationFrequency?: NotificationFrequency;
    quietHoursStart?: string;
    quietHoursEnd?: string;
    quietHoursEnabled?: boolean;
}

/**
 * 用戶互動記錄
 */
export interface UserInteraction {
    lineUserId: string;
    type: 'search' | 'book_view' | 'video_view' | 'page_view';
    data: Record<string, unknown>;
    timestamp: Date;
}

/**
 * 資料庫行格式
 */
export interface UserPreferencesRow {
    id: number;
    line_user_id: string;
    preferred_content_types: string | null;
    preferred_categories: string | null;
    preferred_instructors: string | null;
    notification_channels: string | null;
    notification_frequency: NotificationFrequency;
    quiet_hours_start: string | null;
    quiet_hours_end: string | null;
    recent_searches: string | null;
    recent_book_views: string | null;
    recent_video_views: string | null;
    interaction_count: number;
    last_interaction_at: Date | null;
    created_at: Date;
    updated_at: Date;
}
