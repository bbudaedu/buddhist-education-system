/**
 * NewBook interface representing the structure of new book records in the database
 * This corresponds to the new_books table created by migration 004
 */
export interface NewBook {
  /** 資料庫主鍵 */
  id?: number;
  
  /** 書號 (e.g., CH113-01) */
  book_code: string;
  
  /** 書名 */
  title: string;
  
  /** 作者 */
  author?: string;
  
  /** PDF檔名 */
  pdf_filename?: string;
  
  /** 檔案大小(MB) */
  file_size_mb?: number;
  
  /** 處理方式 (PDF提取/Google搜尋) */
  processing_method?: string;
  
  /** 摘要 */
  summary?: string;
  
  /** 下載連結 */
  download_url?: string;
  
  /** 處理時間 */
  processing_timestamp?: Date;
  
  /** 同步時間 */
  sync_timestamp?: Date;
  
  /** 是否已通知 */
  is_notified?: boolean;
  
  /** 建立時間 */
  created_at?: Date;
  
  /** 更新時間 */
  updated_at?: Date;
}

/**
 * Interface for Excel data import
 * Matches the structure from Python ebook system's Excel output
 */
export interface ExcelBookData {
  /** 書號 */
  book_code: string;
  
  /** 書名 */
  title: string;
  
  /** 作者 */
  author?: string;
  
  /** PDF檔名 */
  pdf_filename?: string;
  
  /** 檔案大小(MB) */
  file_size_mb?: number;
  
  /** 處理方式 */
  processing_method?: string;
  
  /** 摘要 */
  summary?: string;
  
  /** 下載連結 */
  download_url?: string;
  
  /** 處理時間 */
  processing_timestamp?: string;
}