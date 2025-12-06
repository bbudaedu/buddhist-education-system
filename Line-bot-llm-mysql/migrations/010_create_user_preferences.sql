-- Migration: Create user_preferences table
-- Date: 2025-12-06
-- Description: Store user preferences, interests, and interaction history

CREATE TABLE IF NOT EXISTS user_preferences (
  id INT PRIMARY KEY AUTO_INCREMENT,
  line_user_id VARCHAR(255) NOT NULL COMMENT 'LINE 用戶 ID',
  
  -- 興趣偏好（LIFF 會員中心設定）
  preferred_content_types JSON DEFAULT NULL COMMENT '偏好內容類型: ["books", "videos", "livestream"]',
  preferred_categories JSON DEFAULT NULL COMMENT '偏好分類: ["佛經", "修行", "講座"]',
  preferred_instructors JSON DEFAULT NULL COMMENT '偏好講師: ["淨空法師", "聖嚴法師"]',
  
  -- 通知偏好
  notification_channels JSON DEFAULT '["line"]' COMMENT '通知通道: ["line", "email", "webpush"]',
  notification_frequency ENUM('realtime', 'daily', 'weekly') DEFAULT 'realtime' COMMENT '通知頻率',
  quiet_hours_start TIME DEFAULT NULL COMMENT '靜音時段開始',
  quiet_hours_end TIME DEFAULT NULL COMMENT '靜音時段結束',
  
  -- 互動記錄（Bot 自動追蹤）
  recent_searches JSON DEFAULT NULL COMMENT '最近搜尋關鍵字（最多 20 筆）',
  recent_book_views JSON DEFAULT NULL COMMENT '最近查看的書籍（最多 20 筆）',
  recent_video_views JSON DEFAULT NULL COMMENT '最近查看的影音（最多 20 筆）',
  interaction_count INT DEFAULT 0 COMMENT '總互動次數',
  last_interaction_at TIMESTAMP NULL COMMENT '最後互動時間',
  
  -- 時間戳
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  -- 索引
  UNIQUE KEY uk_line_user_id (line_user_id),
  INDEX idx_notification_frequency (notification_frequency),
  INDEX idx_last_interaction (last_interaction_at),
  INDEX idx_interaction_count (interaction_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default preferences for existing subscribed users
INSERT INTO user_preferences (line_user_id, notification_channels, created_at)
SELECT line_user_id, '["line"]', NOW()
FROM user_subscriptions
WHERE is_subscribed = TRUE
ON DUPLICATE KEY UPDATE updated_at = NOW();
