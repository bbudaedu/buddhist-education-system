/**
 * 測試 books_3f 資料庫連線
 * 這個腳本用於驗證新的資料庫配置是否正常工作
 */

const mysql = require('mysql2/promise');
require('dotenv').config();

async function testDatabaseConnection() {
  console.log('🔍 測試 books_3f 資料庫連線...');
  
  const config = {
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT) || 3306,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
  };

  console.log(`📊 連線配置:`);
  console.log(`   主機: ${config.host}:${config.port}`);
  console.log(`   用戶: ${config.user}`);
  console.log(`   資料庫: ${config.database}`);

  let connection;
  
  try {
    // 建立連線
    connection = await mysql.createConnection(config);
    console.log('✅ 資料庫連線成功！');

    // 測試基本查詢
    const [rows] = await connection.execute('SELECT DATABASE() as current_db, VERSION() as mysql_version');
    console.log(`📋 當前資料庫: ${rows[0].current_db}`);
    console.log(`🔧 MySQL 版本: ${rows[0].mysql_version}`);

    // 檢查 books_3f 表是否存在
    try {
      const [bookRows] = await connection.execute('SELECT COUNT(*) as book_count FROM books_3f LIMIT 1');
      console.log(`📚 books_3f 表存在，包含 ${bookRows[0].book_count} 筆記錄`);
    } catch (error) {
      console.log('⚠️  books_3f 表不存在或無法訪問');
    }

    // 檢查通知系統相關表
    const tables = ['user_subscriptions', 'notification_logs', 'delivery_failures'];
    
    for (const table of tables) {
      try {
        const [tableRows] = await connection.execute(`SELECT COUNT(*) as count FROM ${table}`);
        console.log(`✅ ${table} 表存在，包含 ${tableRows[0].count} 筆記錄`);
      } catch (error) {
        console.log(`❌ ${table} 表不存在，需要執行遷移`);
      }
    }

    // 測試書籍搜尋功能
    try {
      const [searchRows] = await connection.execute(
        'SELECT book_id, title, quantity_3f as quantity, shelf_location_3f as shelf_location FROM books_3f WHERE title LIKE ? LIMIT 3',
        ['%佛%']
      );
      console.log(`🔍 書籍搜尋測試: 找到 ${searchRows.length} 筆包含「佛」的書籍`);
      if (searchRows.length > 0) {
        console.log(`   範例: ${searchRows[0].title} (${searchRows[0].shelf_location})`);
      }
    } catch (error) {
      console.log('⚠️  書籍搜尋測試失敗:', error.message);
    }

  } catch (error) {
    console.error('❌ 資料庫連線失敗:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      console.log('💡 建議檢查:');
      console.log('   1. MySQL 服務是否正在運行');
      console.log('   2. 主機和端口設定是否正確');
      console.log('   3. 防火牆設定是否允許連線');
    } else if (error.code === 'ER_ACCESS_DENIED_ERROR') {
      console.log('💡 建議檢查:');
      console.log('   1. 用戶名和密碼是否正確');
      console.log('   2. 用戶是否有訪問該資料庫的權限');
    } else if (error.code === 'ER_BAD_DB_ERROR') {
      console.log('💡 建議檢查:');
      console.log('   1. 資料庫名稱是否正確');
      console.log('   2. 資料庫是否存在');
    }
    
    process.exit(1);
  } finally {
    if (connection) {
      await connection.end();
      console.log('🔌 資料庫連線已關閉');
    }
  }
}

// 執行測試
testDatabaseConnection()
  .then(() => {
    console.log('🎉 資料庫連線測試完成！');
    process.exit(0);
  })
  .catch((error) => {
    console.error('💥 測試過程中發生錯誤:', error);
    process.exit(1);
  });