-- Add dharma_books table and subscribed_videos column

-- Create dharma_books table for scraped data
CREATE TABLE IF NOT EXISTS dharma_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    cover_image_url VARCHAR(512),
    pdf_url VARCHAR(512),
    url VARCHAR(512),
    publish_date DATE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_book_url (url)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add subscribed_videos column to subscribers table
-- Check if column exists first (MySQL 8.0+ support IF NOT EXISTS in ADD COLUMN, but for safety we use a procedure or just ignore error if it fails in simple script)
-- For simplicity in this environment, we'll assume it doesn't exist or use a safe approach.
-- However, standard SQL doesn't support IF NOT EXISTS for columns easily.
-- We will just run the ALTER TABLE. If it fails, it might be because it exists.
-- But since this is a controlled environment, we can try.

ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS subscribed_videos BOOLEAN DEFAULT FALSE;
