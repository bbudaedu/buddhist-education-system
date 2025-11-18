-- Migration 001: Create user_subscriptions table
-- This table stores user subscription preferences for daily book notifications

CREATE TABLE IF NOT EXISTS user_subscriptions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  line_user_id VARCHAR(255) UNIQUE NOT NULL,
  display_name VARCHAR(255),
  is_subscribed BOOLEAN DEFAULT FALSE,
  subscription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_notification_sent TIMESTAMP NULL,
  notification_preferences JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_line_user_id (line_user_id),
  INDEX idx_is_subscribed (is_subscribed)
);