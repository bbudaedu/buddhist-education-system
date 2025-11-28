import NodeCache from 'node-cache';
import { budaeduConnector } from './budaeduConnector';

/**
 * 書籍資料介面
 */
export interface DharmaBook {
    id: string;
    code?: string; // Book code (e.g., CH550-03)
    title: string;
    author: string;
    description?: string;
    coverImageUrl?: string | undefined;
    pdfUrl?: string | undefined;
    fileSize?: string | undefined; // PDF file size (e.g., '5.2 MB')
    publishDate?: string | undefined;
}

/**
 * Dharma Book Service
 * 負責取得最新法寶（書籍）資料
 * 資料來源：直接呼叫 API (https://publish.budaedu.org/dharma/public/api/books/chinese)
 */
export class DharmaBookService {
    private readonly API_URL = 'https://publish.budaedu.org/dharma/public/api/books/chinese';
    private readonly EFILES_URL = 'https://publish.budaedu.org/dharma/public/api/books';
    private readonly COVER_BASE_URL = 'https://www2.budaedu.org/dharma-data/book-front-cover/';
    private cache: NodeCache;

    constructor() {
        // 快取 5 分鐘
        this.cache = new NodeCache({ stdTTL: 300 });
    }

    /**
     * 移除 HTML 標籤並清理文字
     */
    private stripHtmlTags(html: string): string {
        if (!html) return '';
        return html
            .replace(/<[^>]*>/g, '') // 移除 HTML 標籤
            .replace(/&nbsp;/g, ' ') // 解碼 &nbsp;
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&amp;/g, '&')
            .replace(/&quot;/g, '"')
            .replace(/&#039;/g, "'")
            .replace(/\s+/g, ' ') // 合併多餘空白
            .trim();
    }

    /**
     * 構建封面圖 URL
     * @param code 書籍代碼（如 "CH382-16"）
     * @returns 封面圖 URL
     */
    private buildCoverImageUrl(code: string): string {
        if (!code) return 'https://www.budaedu.org/img/logo.png';
        const cleanCode = code.replace(/-/g, ''); // 移除連字符
        return `${this.COVER_BASE_URL}${cleanCode}.jpg`;
    }

    /**
     * 取得指定書籍的 PDF URL
     * @param bookId 書籍 ID
     * @returns PDF URL 或空字串
     */
    private async getBookPdfUrl(bookId: string): Promise<{ url: string; size: string }> {
        try {
            const response = await budaeduConnector.get<any>(
                `${this.EFILES_URL}/${bookId}/efiles`,
                {
                    params: {
                        include: 'attached',
                        order: 'name,asc'
                    },
                    timeout: 5000 // 5秒超時
                }
            );

            const files = response.data || [];
            return {
                url: files[0]?.url || '',
                size: files[0]?.formatted_size || ''
            };
        } catch (error: any) {
            console.error(`Failed to fetch efiles for book ${bookId}:`, error.message);
            return { url: '', size: '' };
        }
    }

    /**
     * 取得最新法寶
     * @param limit 限制數量
     * @returns Promise<DharmaBook[]> 書籍列表
     */
    async getLatestBooks(limit: number = 5): Promise<DharmaBook[]> {
        try {
            // 檢查快取
            const cacheKey = `dharma_books_enhanced_${limit}`;
            const cached = this.cache.get<DharmaBook[]>(cacheKey);
            if (cached) {
                console.log('使用快取的書籍資料（增強版）');
                return cached;
            }

            console.log(`從 API 抓取書籍資料: ${this.API_URL}`);
            const response = await budaeduConnector.get<any>(this.API_URL, {
                params: {
                    'filter[have_efile]': 'Y',
                    'order': 'latest_storage_date,desc|order_by_language_category_count,asc|code,desc',
                    per_page: limit,
                    page: 1
                },
                timeout: 10000
            });

            // API 回傳格式通常是 { data: [...] } 或直接 [...]
            let rawBooks: any[] = [];
            if (response.data && Array.isArray(response.data)) {
                rawBooks = response.data;
            } else if (Array.isArray(response)) {
                rawBooks = response;
            }

            console.log(`API 回傳 ${rawBooks.length} 筆書籍，開始並行獲取 PDF 連結...`);

            // 並行獲取每本書的 PDF URL 和文件大小
            const booksWithFiles = await Promise.all(
                rawBooks.map(async (item: any) => {
                    const pdfInfo = await this.getBookPdfUrl(item.id);
                    return {
                        ...item,
                        pdfUrl: pdfInfo.url,
                        fileSize: pdfInfo.size
                    };
                })
            );

            // 轉換資料
            const books: DharmaBook[] = booksWithFiles.map((item: any) => {
                // 處理簡介
                const rawIntro = item.chinese_intro || '';
                const cleanIntro = this.stripHtmlTags(rawIntro);
                const description = cleanIntro.length > 100
                    ? cleanIntro.substring(0, 100) + '...'
                    : cleanIntro;

                return {
                    id: String(item.id || Math.random().toString(36).substr(2, 9)),
                    code: item.code || '',
                    title: item.chinese_name || item.name_zh || item.name || item.title || '無標題',
                    author: item.chinese_author || item.author_name || item.author || '佛陀教育基金會',
                    description: description || '暫無簡介',
                    coverImageUrl: this.buildCoverImageUrl(item.code),
                    pdfUrl: item.pdfUrl || '',
                    fileSize: item.fileSize || '',
                    publishDate: (item.latest_storage_date || item.storage_date || item.publish_date || item.created_at || new Date().toISOString().split('T')[0]).split(' ')[0]
                };
            });

            // 如果 API 回傳空陣列，使用備用資料
            if (books.length === 0) {
                console.log('API 回傳空資料，使用備用資料');
                return this.getFallbackBooks();
            }

            // 更新快取
            this.cache.set(cacheKey, books);

            console.log(`成功處理 ${books.length} 本書籍（包含封面、簡介、PDF連結）`);
            return books;
        } catch (error: any) {
            console.error('Error fetching dharma books from API:', error);
            console.error('Error details:', error.message);
            if (error.response) {
                console.error('API Response Status:', error.response.status);
                console.error('API Response Data:', JSON.stringify(error.response.data));
            }
            // 發生錯誤時回傳備用資料
            return this.getFallbackBooks();
        }
    }

    /**
     * 取得備用書籍資料（當 API 失敗時使用）
     */
    private getFallbackBooks(): DharmaBook[] {
        const today = new Date().toISOString().split('T')[0];
        return [
            {
                id: 'fallback_1',
                title: '佛說阿彌陀經',
                author: '姚秦三藏法師鳩摩羅什譯',
                description: '此經為淨土三經之一，闡述西方極樂世界的依正莊嚴，勸導眾生發願往生。經文簡明扼要，歷來為淨土宗行者日課必誦之經典。',
                coverImageUrl: 'https://www.budaedu.org/img/logo.png',
                pdfUrl: 'https://ftp.budaedu.org/publish/C1/CH11/CH111-06.pdf',
                publishDate: today
            },
            {
                id: 'fallback_2',
                title: '金剛般若波羅蜜經',
                author: '姚秦三藏法師鳩摩羅什譯',
                description: '本經為般若經典之精華，闡述空性般若之理，破除四相執著。經中「應無所住而生其心」一句，歷來為禪宗修行者所重視。',
                coverImageUrl: 'https://www.budaedu.org/img/logo.png',
                pdfUrl: 'https://ftp.budaedu.org/publish/C1/CH11/CH111-04.pdf',
                publishDate: today
            }
        ];
    }
}

export const dharmaBookService = new DharmaBookService();
