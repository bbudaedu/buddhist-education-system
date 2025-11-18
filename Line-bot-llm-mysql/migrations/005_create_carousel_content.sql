-- Migration 005: Create carousel_content table
-- This table stores carousel banner information from website monitoring

CREATE TABLE IF NOT EXISTS carousel_content (
  id INT PRIMARY KEY AUTO_INCREMENT,
  carousel_id VARCHAR(255) NOT NULL COMMENT '輪播ID',
  banner_title VARCHAR(500) DEFAULT NULL COMMENT '橫幅標題',
  image_url TEXT DEFAULT NULL COMMENT '圖片網址',
  activity_link TEXT DEFAULT NULL COMMENT '活動連結',
  course_name VARCHAR(500) DEFAULT NULL COMMENT '課程名稱',
  location VARCHAR(255) DEFAULT NULL COMMENT '地點',
  instructor VARCHAR(255) DEFAULT NULL COMMENT '講師',
  description TEXT DEFAULT NULL COMMENT '描述',
  extraction_timestamp TIMESTAMP DEFAULT NULL COMMENT '擷取時間',
  sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '同步時間',
  is_notified BOOLEAN DEFAULT FALSE COMMENT '是否已通知',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  UNIQUE KEY unique_carousel_id (carousel_id),
  INDEX idx_banner_title (banner_title),
  INDEX idx_course_name (course_name),
  INDEX idx_instructor (instructor),
  INDEX idx_extraction_timestamp (extraction_timestamp),
  INDEX idx_sync_timestamp (sync_timestamp),
  INDEX idx_is_notified (is_notified)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='輪播內容資料表';