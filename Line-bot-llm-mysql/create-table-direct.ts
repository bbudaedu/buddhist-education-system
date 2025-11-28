import { databaseService } from './src/services/databaseService';

async function createTableDirectly() {
    try {
        console.log('🔄 Creating dharma_books table directly...\n');

        const createTableSQL = `
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
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    `;

        await (databaseService as any).pool.execute(createTableSQL);
        console.log('✅ Table created successfully!');

        // Verify
        const [tables] = await (databaseService as any).pool.execute(
            "SHOW TABLES LIKE 'dharma_books'"
        );
        console.log('📊 Verification:', tables);

        // Insert test data
        console.log('\n📝 Inserting test data...');
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

        for (const book of testBooks) {
            await (databaseService as any).pool.execute(
                `INSERT INTO dharma_books (title, author, cover_image_url, pdf_url, url, publish_date) 
         VALUES (?, ?, ?, ?, ?, ?)`,
                [book.title, book.author, book.cover_image_url, book.pdf_url, book.url, book.publish_date]
            );
            console.log(`  ✓ ${book.title}`);
        }

        console.log('\n✅ All done!');

        // Show result
        const [books] = await (databaseService as any).pool.execute(
            'SELECT id, title, author, pdf_url FROM dharma_books ORDER BY publish_date DESC'
        );
        console.log('\n📚 Books in database:');
        console.table(books);

        process.exit(0);
    } catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
}

createTableDirectly();
