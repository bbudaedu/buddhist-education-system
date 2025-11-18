-- Migration 008: Create media_content table
-- This table stores multimedia content information from website monitoring

CREATE TABLE IF NOT EXISTS media_content (
  id INT PRIMARY KEY AUTO_INCREMENT,
  media_id VARCHAR(255) NOT NULL COMMENT '媒體ID',
  course_title VARCHAR(500) DEFAULT NULL COMMENT '課程標題',
  speaker_name VARCHAR(255) DEFAULT NULL COMMENT '講師姓名',
  start_date DATE DEFAULT NULL COMMENT '開始日期',
  redirect_url TEXT DEFAULT NULL COMMENT '重定向網址',
  media_type VARCHAR(100) DEFAULT NULL COMMENT '媒體類型',
  extraction_timestamp TIMESTAMP DEFAULT NULL COMMENT '擷取時間',
  sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '同步時間',
  is_notified BOOLEAN DEFAULT FALSE COMMENT '是否已通知',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  UNIQUE KEY unique_media_id (media_id),
  INDEX idx_course_title (course_title),
  INDEX idx_speaker_name (speaker_name),
  INDEX idx_start_date (start_date),
  INDEX idx_media_type (media_type),
  INDEX idx_extraction_timestamp (extraction_timestamp),
  INDEX idx_sync_timestamp (sync_timestamp),
  INDEX idx_is_notified (is_notified)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='多媒體內容資料表';