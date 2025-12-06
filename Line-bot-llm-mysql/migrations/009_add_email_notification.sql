-- Migration: Add email notification fields to user_subscriptions
-- Date: 2025-12-06
-- Description: Add email and notification preference columns for multi-channel notifications

-- Add email related columns
ALTER TABLE user_subscriptions
ADD COLUMN email VARCHAR(255) NULL COMMENT '用戶 Email（來自 LINE Login 或手動輸入）' AFTER display_name,
ADD COLUMN email_verified BOOLEAN DEFAULT FALSE COMMENT 'Email 是否已驗證' AFTER email,
ADD COLUMN email_verification_token VARCHAR(6) NULL COMMENT '驗證碼' AFTER email_verified,
ADD COLUMN email_token_expires TIMESTAMP NULL COMMENT '驗證碼過期時間' AFTER email_verification_token,
ADD COLUMN email_notification_enabled BOOLEAN DEFAULT FALSE COMMENT '是否啟用 Email 通知' AFTER email_token_expires,
ADD COLUMN picture_url VARCHAR(500) NULL COMMENT '用戶頭像 URL' AFTER email_notification_enabled,
ADD COLUMN updated_via_liff TIMESTAMP NULL COMMENT '最後透過 LIFF 更新時間' AFTER picture_url;

-- Add indexes for email queries
CREATE INDEX idx_email ON user_subscriptions(email);
CREATE INDEX idx_email_verified ON user_subscriptions(email_verified);
CREATE INDEX idx_email_notification ON user_subscriptions(email_notification_enabled);

-- Update existing subscribed users to have default email notification disabled
UPDATE user_subscriptions 
SET email_notification_enabled = FALSE 
WHERE email_notification_enabled IS NULL;
