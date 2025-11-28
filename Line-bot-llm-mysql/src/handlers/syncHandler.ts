import { Request, Response } from 'express';
import { databaseService } from '../services/databaseService';

/**
 * Sync API Handler for Python Scraper Integration
 * 接收 Python scraper 抓取的法寶資料並同步到資料庫
 */
export class SyncHandler {
    /**
     * Sync dharma books from Python scraper
     */
    async syncDharmaBooks(req: Request, res: Response): Promise<void> {
        try {
            const { books } = req.body;

            if (!books || !Array.isArray(books)) {
                res.status(400).json({
                    error: 'Invalid request',
                    message: 'Books array is required'
                });
                return;
            }

            console.log(`Received ${books.length} books from scraper`);

            // Transform data to match database schema
            const booksToSync = books.map((book: any) => ({
                title: book.title,
                author: book.author || null,
                coverImageUrl: book.cover_image_url || null,
                pdfUrl: book.pdf_url || null,
                publishDate: book.publish_date || null
            }));

            // Sync to database
            const result = await databaseService.syncDharmaBooks(booksToSync);

            res.status(200).json({
                success: true,
                message: `Successfully synced ${books.length} books`,
                details: {
                    inserted: result.inserted,
                    updated: result.updated
                }
            });
        } catch (error) {
            console.error('Sync dharma books error:', error);
            res.status(500).json({
                error: 'Sync failed',
                message: error instanceof Error ? error.message : 'Unknown error'
            });
        }
    }
}

export const syncHandler = new SyncHandler();
