import { databaseService } from './src/services/databaseService';

async function checkDatabase() {
    try {
        console.log('🔍 Checking dharma_books table...\n');

        // 1. Check if table exists
        console.log('1️⃣ Checking table structure...');
        const [columns] = await (databaseService as any).pool.execute(
            `DESCRIBE dharma_books`
        );
        console.log('\n📋 Table Structure:');
        console.table(columns);

        // 2. Check row count
        const [countResult] = await (databaseService as any).pool.execute(
            `SELECT COUNT(*) as total FROM dharma_books`
        );
        const total = (countResult as any)[0].total;
        console.log(`\n📊 Total rows: ${total}`);

        // 3. Show sample data
        if (total > 0) {
            console.log('\n3️⃣ Sample data (latest 5 books):');
            const [books] = await (databaseService as any).pool.execute(
                `SELECT 
          id, 
          title, 
          author, 
          SUBSTRING(cover_image_url, 1, 50) as cover_url,
          SUBSTRING(pdf_url, 1, 50) as pdf,
          publish_date,
          created_at
         FROM dharma_books 
         ORDER BY publish_date DESC 
         LIMIT 5`
            );
            console.table(books);
        } else {
            console.log('\n⚠️  No data found in dharma_books table');
            console.log('💡 You may need to run the Python scraper or insert test data');
        }

        process.exit(0);
    } catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
}

checkDatabase();
