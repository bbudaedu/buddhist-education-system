-- Migration 002: Create notification_logs table
-- This table tracks daily notification processing statistics

CREATE TABLE IF NOT EXISTS notification_logs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  processing_date DATE NOT NULL,
  total_recipients INT NOT NULL,
  successful_deliveries INT NOT NULL,
  failed_deliveries INT NOT NULL,
  books_processed INT NOT NULL,
  processing_duration_seconds INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_processing_date (processing_date)
);