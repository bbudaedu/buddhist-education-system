import { databaseService } from './src/services/databaseService';

async function addPdfUrls() {
    try {
        console.log('📝 Adding PDF URLs to books...\n');

        // 為所有書籍添加 PDF URL（使用佛陀教育網站的格式）
        await (databaseService as any).pool.execute(`
      UPDATE dharma_books 
      SET pdf_url = CONCAT('https://www.budaedu.org/budaedu/pdf/', 
                          REPLACE(SUBSTRING_INDEX(title, ' ', 1), '（', ''),
                          '.pdf?openExternalBrowser=1')
      WHERE pdf_url IS NULL
    `);

        console.log('✅ PDF URLs added\n');

        // Verify
        const [books] = await (databaseService as any).pool.execute(
            'SELECT id, title, pdf_url FROM dharma_books ORDER BY publish_date DESC LIMIT 10'
        );

        console.log('📚 Books with PDF URLs:');
        console.table(books);

        process.exit(0);
    } catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
}

addPdfUrls();
