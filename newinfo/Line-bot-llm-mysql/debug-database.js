const mysql = require('mysql2/promise');
require('dotenv').config();

async function debugDatabase() {
  console.log('🔍 Debug Database Content');
  console.log('=========================');

  const connection = await mysql.createConnection({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
  });

  // 1. 檢查總書籍數量
  const [countResult] = await connection.execute('SELECT COUNT(*) as total FROM books');
  console.log(`📚 總書籍數量: ${countResult[0].total}`);

  // 2. 檢查是否有包含 "五股" 的書
  const [fiveStockResults] = await connection.execute(
    'SELECT title, library_branch, shelf_location, quantity FROM books WHERE title LIKE ? LIMIT 5',
    ['%五股%']
  );
  console.log(`\n🔍 包含 "五股" 的書籍 (${fiveStockResults.length} 本):`);
  fiveStockResults.forEach(book => {
    console.log(`  - ${book.title} (${book.library_branch}, 庫存: ${book.quantity})`);
  });

  // 3. 檢查庫存最多的書
  const [topStockResults] = await connection.execute(
    'SELECT title, library_branch, shelf_location, quantity FROM books ORDER BY quantity DESC LIMIT 10'
  );
  console.log(`\n📈 庫存最多的書籍 (前10本):`);
  topStockResults.forEach(book => {
    console.log(`  - ${book.title} (庫存: ${book.quantity} 本, ${book.library_branch})`);
  });

  // 4. 檢查館藏地點
  const [branchResults] = await connection.execute(
    'SELECT DISTINCT library_branch, COUNT(*) as count FROM books GROUP BY library_branch'
  );
  console.log(`\n🏢 館藏地點分布:`);
  branchResults.forEach(branch => {
    console.log(`  - ${branch.library_branch}: ${branch.count} 本書`);
  });

  // 5. 測試搜尋 "五股 庫存最多"
  const [searchResults] = await connection.execute(
    'SELECT title, library_branch, shelf_location, quantity FROM books WHERE title LIKE ? LIMIT 5',
    ['%五股 庫存最多%']
  );
  console.log(`\n🔍 搜尋 "五股 庫存最多" 結果 (${searchResults.length} 本):`);
  searchResults.forEach(book => {
    console.log(`  - ${book.title}`);
  });

  // 6. 隨機取樣一些書名
  const [sampleResults] = await connection.execute(
    'SELECT title FROM books LIMIT 10'
  );
  console.log(`\n📖 書名樣本:`);
  sampleResults.forEach(book => {
    console.log(`  - ${book.title}`);
  });

  await connection.end();
}

debugDatabase().catch(console.error);