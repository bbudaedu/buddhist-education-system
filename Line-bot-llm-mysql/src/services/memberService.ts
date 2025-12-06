/**
 * Member Service
 * 會員服務 - 處理會員資料和偏好設定
 */

import mysql from 'mysql2/promise';
import { config } from '../config';
import {
    MemberProfile,
    UserPreferences,
    UserPreferencesRow,
    NotificationChannel,
    ContentType
} from '../types/member';

export class MemberService {
    private pool: mysql.Pool;

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
    }

    /**
     * 取得會員資料
     */
    async getMemberProfile(lineUserId: string): Promise<MemberProfile | null> {
        const [rows] = await this.pool.query<mysql.RowDataPacket[]>(
            `SELECT 
                line_user_id, display_name, picture_url, 
                email, email_verified, email_notification_enabled,
                created_at, updated_at
            FROM user_subscriptions 
            WHERE line_user_id = ?`,
            [lineUserId]
        );

        if (rows.length === 0) return null;

        const row = rows[0];
        if (!row) return null;

        return {
            lineUserId: row.line_user_id,
            displayName: row.display_name,
            pictureUrl: row.picture_url,
            email: row.email,
            emailVerified: Boolean(row.email_verified),
            emailNotificationEnabled: Boolean(row.email_notification_enabled),
            createdAt: row.created_at,
            updatedAt: row.updated_at
        };
    }

    /**
     * 更新會員基本資料（從 LIFF 登入）
     */
    async updateMemberProfile(
        lineUserId: string,
        data: { displayName?: string; pictureUrl?: string; email?: string }
    ): Promise<boolean> {
        const updates: string[] = [];
        const values: (string | null)[] = [];

        if (data.displayName !== undefined) {
            updates.push('display_name = ?');
            values.push(data.displayName);
        }
        if (data.pictureUrl !== undefined) {
            updates.push('picture_url = ?');
            values.push(data.pictureUrl);
        }
        if (data.email !== undefined) {
            updates.push('email = ?');
            values.push(data.email);
        }

        if (updates.length === 0) return false;

        updates.push('updated_via_liff = NOW()');
        values.push(lineUserId);

        const [result] = await this.pool.query<mysql.ResultSetHeader>(
            `UPDATE user_subscriptions 
            SET ${updates.join(', ')} 
            WHERE line_user_id = ?`,
            values
        );

        return result.affectedRows > 0;
    }

    /**
     * 設定 Email 驗證碼
     */
    async setEmailVerificationToken(lineUserId: string, email: string, token: string): Promise<boolean> {
        const expiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

        console.log(`[Email] Setting token: ${token} for ${email}, expires: ${expiresAt.toISOString()}`);

        // 使用 INSERT ... ON DUPLICATE KEY UPDATE 確保用戶記錄存在
        const [result] = await this.pool.query<mysql.ResultSetHeader>(
            `INSERT INTO user_subscriptions (line_user_id, email, email_verification_token, email_token_expires, email_verified, is_subscribed)
            VALUES (?, ?, ?, ?, FALSE, TRUE)
            ON DUPLICATE KEY UPDATE 
                email = VALUES(email),
                email_verification_token = VALUES(email_verification_token),
                email_token_expires = VALUES(email_token_expires),
                email_verified = FALSE`,
            [lineUserId, email, token, expiresAt]
        );

        console.log(`[Email] Token set result: affectedRows=${result.affectedRows}`);
        return result.affectedRows > 0;
    }

    /**
     * 驗證 Email
     */
    async verifyEmail(lineUserId: string, email: string, token: string): Promise<boolean> {
        // 先查詢當前資料
        const [rows] = await this.pool.query<mysql.RowDataPacket[]>(
            `SELECT email_verification_token, email_token_expires FROM user_subscriptions WHERE line_user_id = ?`,
            [lineUserId]
        );

        if (rows.length > 0 && rows[0]) {
            console.log(`[Email] Verifying: stored_token=${rows[0].email_verification_token}, input_token=${token}`);
            console.log(`[Email] Expires: ${rows[0].email_token_expires}, NOW: ${new Date().toISOString()}`);
        }

        const [result] = await this.pool.query<mysql.ResultSetHeader>(
            `UPDATE user_subscriptions 
            SET email_verified = TRUE,
                email_verification_token = NULL,
                email_token_expires = NULL
            WHERE line_user_id = ? 
                AND email = ?
                AND email_verification_token = ?
                AND email_token_expires > NOW()`,
            [lineUserId, email, token]
        );

        console.log(`[Email] Verify result: affectedRows=${result.affectedRows}`);
        return result.affectedRows > 0;
    }

    /**
     * 取得用戶偏好設定
     */
    async getUserPreferences(lineUserId: string): Promise<UserPreferences | null> {
        const [rows] = await this.pool.query<mysql.RowDataPacket[]>(
            `SELECT * FROM user_preferences WHERE line_user_id = ?`,
            [lineUserId]
        );

        if (rows.length === 0) return null;

        const row = rows[0] as UserPreferencesRow;
        return this.parsePreferencesRow(row);
    }

    /**
     * 建立或更新用戶偏好
     */
    async upsertUserPreferences(lineUserId: string, prefs: Partial<UserPreferences>): Promise<boolean> {
        const contentTypes = JSON.stringify(prefs.preferredContentTypes || []);
        const channels = JSON.stringify(prefs.notificationChannels || ['line']);
        const frequency = prefs.notificationFrequency || 'realtime';

        const [result] = await this.pool.query<mysql.ResultSetHeader>(
            `INSERT INTO user_preferences (
                line_user_id, 
                preferred_content_types, 
                notification_channels, 
                notification_frequency,
                quiet_hours_start,
                quiet_hours_end
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                preferred_content_types = VALUES(preferred_content_types),
                notification_channels = VALUES(notification_channels),
                notification_frequency = VALUES(notification_frequency),
                quiet_hours_start = VALUES(quiet_hours_start),
                quiet_hours_end = VALUES(quiet_hours_end),
                updated_at = NOW()`,
            [
                lineUserId,
                contentTypes,
                channels,
                frequency,
                prefs.quietHoursStart || null,
                prefs.quietHoursEnd || null
            ]
        );

        return result.affectedRows > 0;
    }

    /**
     * 記錄用戶互動（搜尋、查看等）
     */
    async recordInteraction(
        lineUserId: string,
        type: 'search' | 'book_view' | 'video_view',
        data: string
    ): Promise<void> {
        const column = type === 'search'
            ? 'recent_searches'
            : type === 'book_view'
                ? 'recent_book_views'
                : 'recent_video_views';

        // 取得現有記錄
        const [rows] = await this.pool.query<mysql.RowDataPacket[]>(
            `SELECT ${column} FROM user_preferences WHERE line_user_id = ?`,
            [lineUserId]
        );

        let recentItems: string[] = [];
        const firstRow = rows[0];
        if (rows.length > 0 && firstRow && firstRow[column]) {
            try {
                recentItems = JSON.parse(firstRow[column] as string);
            } catch {
                recentItems = [];
            }
        }

        // 新增並限制數量
        recentItems.unshift(data);
        recentItems = recentItems.slice(0, 20);

        // 更新
        await this.pool.query(
            `INSERT INTO user_preferences (line_user_id, ${column}, interaction_count, last_interaction_at)
            VALUES (?, ?, 1, NOW())
            ON DUPLICATE KEY UPDATE
                ${column} = VALUES(${column}),
                interaction_count = interaction_count + 1,
                last_interaction_at = NOW()`,
            [lineUserId, JSON.stringify(recentItems)]
        );
    }

    /**
     * 取得啟用 Email 通知的用戶
     */
    async getEmailEnabledUsers(): Promise<{ lineUserId: string; email: string; displayName: string }[]> {
        const [rows] = await this.pool.query<mysql.RowDataPacket[]>(
            `SELECT line_user_id, email, display_name
            FROM user_subscriptions
            WHERE is_subscribed = TRUE 
                AND email IS NOT NULL 
                AND email_verified = TRUE
                AND email_notification_enabled = TRUE`
        );

        return rows.map(row => ({
            lineUserId: row.line_user_id,
            email: row.email,
            displayName: row.display_name
        }));
    }

    /**
     * 解析偏好設定資料庫行
     */
    private parsePreferencesRow(row: UserPreferencesRow): UserPreferences {
        return {
            lineUserId: row.line_user_id,
            preferredContentTypes: this.parseJsonArray<ContentType>(row.preferred_content_types),
            preferredCategories: this.parseJsonArray<string>(row.preferred_categories),
            preferredInstructors: this.parseJsonArray<string>(row.preferred_instructors),
            notificationChannels: this.parseJsonArray<NotificationChannel>(row.notification_channels) || ['line'],
            notificationFrequency: row.notification_frequency,
            quietHoursStart: row.quiet_hours_start,
            quietHoursEnd: row.quiet_hours_end,
            quietHoursEnabled: Boolean(row.quiet_hours_start && row.quiet_hours_end)
        };
    }

    private parseJsonArray<T>(json: string | null): T[] {
        if (!json) return [];
        try {
            return JSON.parse(json);
        } catch {
            return [];
        }
    }
}

export const memberService = new MemberService();
