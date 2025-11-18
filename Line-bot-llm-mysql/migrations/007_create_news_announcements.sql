-- Migration 007: Create news_announcements table
-- This table stores news announcement information from website monitoring

CREATE TABLE IF NOT EXISTS news_announcements (
  id INT PRIMARY KEY AUTO_INCREMENT,
  announcement_id VARCHAR(255) NOT NULL COMMENT '公告ID',
  title VARCHAR(500) DEFAULT NULL COMMENT '標題',
  publication_date DATE DEFAULT NULL COMMENT '發布日期',
  content TEXT DEFAULT NULL COMMENT '內容',
  extraction_timestamp TIMESTAMP DEFAULT NULL COMMENT '擷取時間',
  sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '同步時間',
  is_notified BOOLEAN DEFAULT FALSE COMMENT '是否已通知',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  UNIQUE KEY unique_announcement_id (announcement_id),
  INDEX idx_title (title),
  INDEX idx_publication_date (publication_date),
  INDEX idx_extraction_timestamp (extraction_timestamp),
  INDEX idx_sync_timestamp (sync_timestamp),
  INDEX idx_is_notified (is_notified)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='最新消息資料表';