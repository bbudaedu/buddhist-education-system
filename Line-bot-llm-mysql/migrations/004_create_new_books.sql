-- Migration 004: Create new_books table
-- This table stores new book information synchronized from the ebook system

CREATE TABLE IF NOT EXISTS new_books (
  id INT PRIMARY KEY AUTO_INCREMENT,
  book_code VARCHAR(50) NOT NULL COMMENT '書號 (e.g., CH113-01)',
  title VARCHAR(500) NOT NULL COMMENT '書名',
  author VARCHAR(255) DEFAULT NULL COMMENT '作者',
  pdf_filename VARCHAR(255) DEFAULT NULL COMMENT 'PDF檔名',
  file_size_mb DECIMAL(10,2) DEFAULT NULL COMMENT '檔案大小(MB)',
  processing_method VARCHAR(50) DEFAULT NULL COMMENT '處理方式 (PDF提取/Google搜尋)',
  summary TEXT COMMENT '摘要',
  download_url VARCHAR(1000) DEFAULT NULL COMMENT '下載連結',
  processing_timestamp TIMESTAMP DEFAULT NULL COMMENT '處理時間',
  sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '同步時間',
  is_notified BOOLEAN DEFAULT FALSE COMMENT '是否已通知',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  UNIQUE KEY unique_book_code (book_code),
  INDEX idx_title (title),
  INDEX idx_author (author),
  INDEX idx_processing_timestamp (processing_timestamp),
  INDEX idx_sync_timestamp (sync_timestamp),
  INDEX idx_is_notified (is_notified)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='新書資料表';