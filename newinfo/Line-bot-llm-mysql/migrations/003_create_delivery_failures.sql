-- Migration 003: Create delivery_failures table
-- This table tracks failed notification delivery attempts for debugging and retry logic

CREATE TABLE IF NOT EXISTS delivery_failures (
  id INT PRIMARY KEY AUTO_INCREMENT,
  notification_log_id INT,
  line_user_id VARCHAR(255) NOT NULL,
  error_type VARCHAR(50) NOT NULL,
  error_message TEXT,
  is_retryable BOOLEAN DEFAULT FALSE,
  retry_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (notification_log_id) REFERENCES notification_logs(id),
  INDEX idx_line_user_id (line_user_id),
  INDEX idx_error_type (error_type)
);