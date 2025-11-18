-- Migration 006: Create course_cancellations table
-- This table stores course cancellation information from website monitoring

CREATE TABLE IF NOT EXISTS course_cancellations (
  id INT PRIMARY KEY AUTO_INCREMENT,
  cancellation_id VARCHAR(255) NOT NULL COMMENT '取消ID',
  cancellation_date DATE DEFAULT NULL COMMENT '取消日期',
  course_name VARCHAR(500) DEFAULT NULL COMMENT '課程名稱',
  instructor_name VARCHAR(255) DEFAULT NULL COMMENT '講師姓名',
  extraction_timestamp TIMESTAMP DEFAULT NULL COMMENT '擷取時間',
  sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '同步時間',
  is_notified BOOLEAN DEFAULT FALSE COMMENT '是否已通知',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  UNIQUE KEY unique_cancellation_id (cancellation_id),
  INDEX idx_cancellation_date (cancellation_date),
  INDEX idx_course_name (course_name),
  INDEX idx_instructor_name (instructor_name),
  INDEX idx_extraction_timestamp (extraction_timestamp),
  INDEX idx_sync_timestamp (sync_timestamp),
  INDEX idx_is_notified (is_notified)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='課程取消資料表';