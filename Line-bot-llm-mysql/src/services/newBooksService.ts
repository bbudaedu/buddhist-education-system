import { databaseService } from './databaseService';

/**
 * New Books Database Service
 * 處理新書摘要的資料庫同步操作
 */

export interface NewBookSyncData {
    book_code: string;
    title: string;
    author?: string;
    pdf_filename?: string;
    file_size_mb?: number;
    processing_method?: string;
    summary: string;
    download_url?: string;
    processing_timestamp?: string;
}

class NewBooksService {
    /**
     * 同步新書摘要到資料庫
     * @param books 書籍資料陣列
     * @returns 同步結果
     */
    async syncNewBooks(books: NewBookSyncData[]): Promise<{
        success: boolean;
        synced: number;
        skipped: number;
        errors: string[];
    }> {
        const result = {
            success: true,
            synced: 0,
            skipped: 0,
            errors: [] as string[],
        };

        if (!books || books.length === 0) {
            return result;
        }

        const connection = await databaseService.getConnection();
        if (!connection) {
            throw new Error('無法取得資料庫連線');
        }

        try {
            for (const book of books) {
                try {
                    // 使用 INSERT ... ON DUPLICATE KEY UPDATE
                    const sql = `
            INSERT INTO new_books (
              book_code, title, author, pdf_filename, file_size_mb,
              processing_method, summary, download_url, processing_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
              title = VALUES(title),
              author = VALUES(author),
              pdf_filename = VALUES(pdf_filename),
              file_size_mb = VALUES(file_size_mb),
              processing_method = VALUES(processing_method),
              summary = VALUES(summary),
              download_url = VALUES(download_url),
              processing_timestamp = VALUES(processing_timestamp),
              sync_timestamp = CURRENT_TIMESTAMP
          `;

                    const processingTimestamp = book.processing_timestamp
                        ? new Date(book.processing_timestamp).toISOString().slice(0, 19).replace('T', ' ')
                        : new Date().toISOString().slice(0, 19).replace('T', ' ');

                    await connection.execute(sql, [
                        book.book_code,
                        book.title,
                        book.author || null,
                        book.pdf_filename || null,
                        book.file_size_mb || null,
                        book.processing_method || null,
                        book.summary,
                        book.download_url || null,
                        processingTimestamp,
                    ]);

                    result.synced++;
                    console.log(`📚 Synced book: ${book.title}`);
                } catch (bookError) {
                    const errorMsg = bookError instanceof Error ? bookError.message : 'Unknown error';
                    result.errors.push(`${book.title}: ${errorMsg}`);
                    result.skipped++;
                    console.error(`❌ Failed to sync book "${book.title}": ${errorMsg}`);
                }
            }
        } finally {
            connection.release();
        }

        result.success = result.errors.length === 0;
        return result;
    }

    /**
     * 取得未通知的新書
     * @param limit 限制數量
     */
    async getUnnotifiedBooks(limit: number = 10): Promise<NewBookSyncData[]> {
        const connection = await databaseService.getConnection();
        if (!connection) {
            throw new Error('無法取得資料庫連線');
        }

        try {
            const [rows] = await connection.execute(
                `SELECT book_code, title, author, summary, download_url, processing_timestamp
         FROM new_books
         WHERE is_notified = FALSE
         ORDER BY sync_timestamp DESC
         LIMIT ?`,
                [limit]
            );
            return rows as NewBookSyncData[];
        } finally {
            connection.release();
        }
    }

    /**
     * 標記書籍為已通知
     * @param bookCodes 書籍代碼陣列
     */
    async markAsNotified(bookCodes: string[]): Promise<number> {
        if (!bookCodes || bookCodes.length === 0) {
            return 0;
        }

        const connection = await databaseService.getConnection();
        if (!connection) {
            throw new Error('無法取得資料庫連線');
        }

        try {
            const placeholders = bookCodes.map(() => '?').join(', ');
            const [result] = await connection.execute(
                `UPDATE new_books SET is_notified = TRUE WHERE book_code IN (${placeholders})`,
                bookCodes
            );
            return (result as any).affectedRows || 0;
        } finally {
            connection.release();
        }
    }

    /**
     * 取得最近同步的新書
     * @param days 天數
     * @param limit 限制數量
     */
    async getRecentBooks(days: number = 7, limit: number = 20): Promise<NewBookSyncData[]> {
        const connection = await databaseService.getConnection();
        if (!connection) {
            throw new Error('無法取得資料庫連線');
        }

        try {
            const [rows] = await connection.execute(
                `SELECT book_code, title, author, summary, download_url, processing_timestamp, sync_timestamp
         FROM new_books
         WHERE sync_timestamp >= DATE_SUB(NOW(), INTERVAL ? DAY)
         ORDER BY sync_timestamp DESC
         LIMIT ?`,
                [days, limit]
            );
            return rows as NewBookSyncData[];
        } finally {
            connection.release();
        }
    }
}

export const newBooksService = new NewBooksService();
