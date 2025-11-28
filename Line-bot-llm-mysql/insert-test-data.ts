import { databaseService } from './src/services/databaseService';

async function insertTestData() {
    try {
        console.log('📝 Inserting test data into dharma_books...\n');

        const testBooks = [
            {
                title: '佛說阿彌陀經',
                author: '鳩摩羅什 譯',
                cover_image_url: 'https://www.budaedu.org/budaedu/images/book_cover/amitabha_sutra.jpg',
                pdf_url: 'https://www.budaedu.org/budaedu/pdf/amitabha_sutra.pdf',
                url: 'https://www.budaedu.org/#/cht/book/detail/123',
                publish_date: '2024-11-01'
            },
            {
                title: '金剛般若波羅蜜經',
                author: '鳩摩羅什 譯',
                cover_image_url: 'https://www.budaedu.org/budaedu/images/book_cover/diamond_sutra.jpg',
                pdf_url: 'https://www.budaedu.org/budaedu/pdf/diamond_sutra.pdf',
                url: 'https://www.budaedu.org/#/cht/book/detail/124',
                publish_date: '2024-11-05'
            },
            {
                title: '普賢行願品',
                author: '般若 譯',
                cover_image_url: 'https://www.budaedu.org/budaedu/images/book_cover/samantabhadra.jpg',
                pdf_url: 'https://www.budaedu.org/budaedu/pdf/samantabhadra.pdf',
                url: 'https://www.budaedu.org/#/cht/book/detail/125',
                publish_date: '2024-11-10'
            },
            {
                title: '觀世音菩薩普門品',
                author: '鳩摩羅什 譯',
                cover_image_url: 'https://via.placeholder.com/300x400?text=No+Cover',
                pdf_url: 'https://www.budaedu.org/budaedu/pdf/guanyin.pdf',
                url: 'https://www.budaedu.org/#/cht/book/detail/126',
                publish_date: '2024-11-15'
            },
            {
                title: '地藏菩薩本願經',
                author: '實叉難陀 譯',
                cover_image_url: 'https://www.budaedu.org/budaedu/images/book_cover/ksitigarbha.jpg',
                pdf_url: 'https://www.budaedu.org/budaedu/pdf/ksitigarbha.pdf',
                url: 'https://www.budaedu.org/#/cht/book/detail/127',
                publish_date: '2024-11-20'
            }
        ];

        let inserted = 0;
        for (const book of testBooks) {
            try {
                await (databaseService as any).pool.execute(
                    `INSERT INTO dharma_books (title, author, cover_image_url, pdf_url, url, publish_date) 
           VALUES (?, ?, ?, ?, ?, ?)`,
                    [book.title, book.author, book.cover_image_url, book.pdf_url, book.url, book.publish_date]
                );
                console.log(`  ✓ ${book.title}`);
                inserted++;
            } catch (err: any) {
                if (err.code === 'ER_DUP_ENTRY') {
                    console.log(`  ⚠ ${book.title} (already exists)`);
                } else {
                    console.error(`  ✗ ${book.title}:`, err.message);
                }
            }
        }

        console.log(`\n✅ Inserted ${inserted} new books`);

        // Verify
        const [books] = await (databaseService as any).pool.execute(
            'SELECT id, title, author, pdf_url, publish_date FROM dharma_books ORDER BY publish_date DESC'
        );

        console.log('\n📊 Current books in database:');
        console.table(books);

        process.exit(0);
    } catch (error) {
        console.error('❌ Failed:', error);
        process.exit(1);
    }
}

insertTestData();
