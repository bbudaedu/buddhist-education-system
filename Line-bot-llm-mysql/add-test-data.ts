import { databaseService } from './src/services/databaseService';

async function addPdfUrlAndTestData() {
  try {
    console.log('🔄 Adding pdf_url column...');
    
    // Add pdf_url column
    await (databaseService as any).pool.execute(
      `ALTER TABLE dharma_books ADD COLUMN IF NOT EXISTS pdf_url VARCHAR(512) AFTER cover_image_url`
    );
    
    console.log('✅ Column added successfully!');
    
    // Insert test data
    console.log('📝 Inserting test data...');
    
    const testBooks = [
      {
        title: '佛說阿彌陀經',
        author: '鳩摩羅什 譯',
        cover_image_url: 'https://www.budaedu.org/budaedu/images/book_cover/amitabha_sutra.jpg',
        pdf_url: 'https://www.budaedu.org/budaedu/pdf/amitabha_sutra.pdf',
        url: 'https://www.budaedu.org/#/cht/book/detail/123',
        publish_date: '2024-01-15'
      },
      {
        title: '金剛般若波羅蜜經',
        author: '鳩摩羅什 譯',
        cover_image_url: 'https://www.budaedu.org/budaedu/images/book_cover/diamond_sutra.jpg',
        pdf_url: 'https://www.budaedu.org/budaedu/pdf/diamond_sutra.pdf',
        url: 'https://www.budaedu.org/#/cht/book/detail/124',
        publish_date: '2024-02-20'
      },
      {
        title: '普賢行願品',
        author: '般若 譯',
        cover_image_url: 'https://www.budaedu.org/budaedu/images/book_cover/samantabhadra.jpg',
        pdf_url: 'https://www.budaedu.org/budaedu/pdf/samantabhadra.pdf',
        url: 'https://www.budaedu.org/#/cht/book/detail/125',
        publish_date: '2024-03-10'
      },
      {
        title: '觀世音菩薩普門品',
        author: '鳩摩羅什 譯',
        cover_image_url: null,
        pdf_url: 'https://www.budaedu.org/budaedu/pdf/guanyin.pdf',
        url: 'https://www.budaedu.org/#/cht/book/detail/126',
        publish_date: '2024-04-05'
      },
      {
        title: '地藏菩薩本願經',
        author: '實叉難陀 譯',
        cover_image_url: 'https://www.budaedu.org/budaedu/images/book_cover/ksitigarbha.jpg',
        pdf_url: null,
        url: 'https://www.budaedu.org/#/cht/book/detail/127',
        publish_date: '2024-05-12'
      }
    ];
    
    for (const book of testBooks) {
      try {
        await (databaseService as any).pool.execute(
          `INSERT INTO dharma_books (title, author, cover_image_url, pdf_url, url, publish_date) 
           VALUES (?, ?, ?, ?, ?, ?)
           ON DUPLICATE KEY UPDATE 
           title = VALUES(title),
           author = VALUES(author),
           cover_image_url = VALUES(cover_image_url),
           pdf_url = VALUES(pdf_url),
           publish_date = VALUES(publish_date)`,
          [book.title, book.author, book.cover_image_url, book.pdf_url, book.url, book.publish_date]
        );
        console.log(`  ✓ ${book.title}`);
      } catch (err) {
        console.error(`  ✗ Failed to insert ${book.title}:`, err);
      }
    }
    
    console.log('\n✅ Test data inserted successfully!');
    
    // Verify
    const [books] = await (databaseService as any).pool.execute(
      'SELECT id, title, author, pdf_url FROM dharma_books ORDER BY publish_date DESC LIMIT 5'
    );
    
    console.log('\n📊 Current books in database:');
    console.table(books);
    
    process.exit(0);
  } catch (error) {
    console.error('❌ Operation failed:', error);
    process.exit(1);
  }
}

addPdfUrlAndTestData();
