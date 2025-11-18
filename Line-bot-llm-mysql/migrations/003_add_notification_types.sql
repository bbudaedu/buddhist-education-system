-- Migration: Add notification type subscriptions
-- Date: 2025-11-14
-- Description: Add support for different notification types (news, cancellation, new_books)

-- Add notification_types column to user_subscriptions table
ALTER TABLE user_subscriptions 
ADD COLUMN notification_types JSON DEFAULT '["new_books"]' COMMENT 'Subscribed notification types: new_books, news, cancellation'
AFTER notification_preferences;

-- Update existing users to subscribe to all types by default
UPDATE user_subscriptions 
SET notification_types = '["new_books", "news", "cancellation"]'
WHERE is_subscribed = TRUE;

-- Add index for better query performance
CREATE INDEX idx_notification_types ON user_subscriptions(line_user_id, is_subscribed);

-- Add notification_type column to notification_logs table
ALTER TABLE notification_logs
ADD COLUMN notification_type VARCHAR(50) DEFAULT 'new_books' COMMENT 'Type of notification: new_books, news, cancellation, daily_summary'
AFTER processing_date;

-- Add notification_type column to delivery_failures table  
ALTER TABLE delivery_failures
ADD COLUMN notification_type VARCHAR(50) DEFAULT 'new_books' COMMENT 'Type of notification that failed'
AFTER line_user_id;
