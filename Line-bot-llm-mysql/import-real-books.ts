import { databaseService } from './src/services/databaseService';

const scrapedBooks = [
    { title: "菩提道次第廣論 CH550-03", author: "宗喀巴大師 著", publishDate: "2024-11-24" },
    { title: "成唯識論研習(內地流通版) CH549-13", author: "普行法師 編著", publishDate: "2024-11-23" },
    { title: "顯揚聖教論 CH541-10", author: "無著菩薩造 唐三藏法師玄奘奉詔譯", publishDate: "2024-11-22" },
    { title: "大佛頂首楞嚴經正脈疏-上、下冊（2013年10月修訂版） CH382-16", author: "明 交光真鑑 述", publishDate: "2024-11-21" },
    { title: "淨土要義 CH861-40", author: "懺雲老和尚開示", publishDate: "2024-11-20" },
    { title: "大手印五支道本尊修持 CH848-04", author: "森給滇真仁波切 講授/林生茂譯師 口譯", publishDate: "2024-11-19" },
    { title: "天台四教儀註彙補輔宏記 CH820-25", author: "未知作者", publishDate: "2024-11-18" },
    { title: "肇論新疏 CH820-14", author: "元沙門 文才 述", publishDate: "2024-11-17" },
    { title: "楞嚴經修學法要 CH382-23", author: "淨界法師 講述審閱妙法蓮心學院 編製", publishDate: "2024-11-16" },
    { title: "六百卷大般若經經脈指引 CH327-04", author: "楊宗翰 編著", publishDate: "2024-11-15" }
];

async function importScrapedBooks() {
    try {
        console.log('🗑️  Clearing old test data...\n');

        // 清空舊資料
        await (databaseService as any).pool.execute('DELETE FROM dharma_books');
        console.log('✅ Old data cleared\n');

        console.log('📝 Importing scraped books...\n');

        const booksToSync = scrapedBooks.map(book => ({
            title: book.title,
            author: book.author,
            publishDate: book.publishDate
        }));

        const result = await databaseService.syncDharmaBooks(booksToSync);

        console.log(`✅ Sync complete: ${result.inserted} inserted, ${result.updated} updated\n`);

        // Verify
        const [books] = await (databaseService as any).pool.execute(
            'SELECT id, title, author, publish_date FROM dharma_books ORDER BY publish_date DESC LIMIT 10'
        );

        console.log('📚 Latest books in database:');
        console.table(books);

        process.exit(0);
    } catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
}

importScrapedBooks();
