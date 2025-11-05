const mysql = require('mysql2/promise');
require('dotenv').config();

async function testDatabase() {
  try {
    console.log('🔍 Testing database connection...');
    
    const connection = await mysql.createConnection({
      host: process.env.DB_HOST,
      port: process.env.DB_PORT,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME
    });

    console.log('✅ Database connected successfully!');

    // 測試查詢書籍表
    const [rows] = await connection.execute('SELECT COUNT(*) as count FROM books');
    console.log(`📚 Total books in database: ${rows[0].count}`);

    // 測試搜尋功能
    const [searchResults] = await connection.execute(
      'SELECT book_id, title, quantity, shelf_location, library_branch FROM books WHERE title LIKE ? LIMIT 3',
      ['%金剛%']
    );
    
    console.log('🔍 Sample search results for "金剛":');
    searchResults.forEach(book => {
      console.log(`  - ${book.title} (${book.library_branch}, ${book.shelf_location})`);
    });

    await connection.end();
    console.log('✅ Database test completed successfully!');
    
  } catch (error) {
    console.error('❌ Database test failed:', error.message);
    process.exit(1);
  }
}

testDatabase();