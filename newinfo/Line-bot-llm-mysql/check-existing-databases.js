/**
 * 檢查現有資料庫中的 books 表
 */

const mysql = require('mysql2/promise');
require('dotenv').config();

async function checkExistingDatabases() {
  console.log('🔍 檢查現有資料庫中的 books 表...');
  
  const config = {
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT) || 3306,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD
  };

  let connection;
  
  try {
    connection = await mysql.createConnection(config);
    console.log('✅ MySQL 伺服器連線成功！');

    // 檢查現有資料庫
    const [databases] = await connection.execute('SHOW DATABASES');
    const dbNames = databases.map(db => db.Database).filter(name => 
      !['information_schema', 'mysql', 'performance_schema', 'sys'].includes(name)
    );
    
    console.log('\n📋 用戶資料庫:');
    dbNames.forEach(name => {
      console.log(`   - ${name}`);
    });

    // 檢查每個資料庫是否包含 books 表
    for (const dbName of dbNames) {
      try {
        const [tables] = await connection.query(`SHOW TABLES FROM ${dbName} LIKE 'books'`);
        
        if (tables.length > 0) {
          const [bookCount] = await connection.query(`SELECT COUNT(*) as count FROM ${dbName}.books`);
          console.log(`\n✅ 發現 ${dbName}.books 表 (${bookCount[0].count} 筆記錄)`);
          
          // 顯示表結構
          const [columns] = await connection.query(`DESCRIBE ${dbName}.books`);
          console.log('   表結構:');
          columns.forEach(col => {
            console.log(`     ${col.Field}: ${col.Type}`);
          });
          
          // 顯示幾筆範例資料
          const [samples] = await connection.query(`SELECT * FROM ${dbName}.books LIMIT 3`);
          console.log('   範例資料:');
          samples.forEach((book, index) => {
            console.log(`     ${index + 1}. ${book.title || book.book_title || '未知標題'}`);
          });
        } else {
          console.log(`   ❌ ${dbName} 不包含 books 表`);
        }
      } catch (error) {
        console.log(`   ❌ 無法檢查 ${dbName}: ${error.message}`);
      }
    }

  } catch (error) {
    console.error('❌ 操作失敗:', error.message);
    process.exit(1);
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}

checkExistingDatabases()
  .then(() => {
    console.log('\n🎉 檢查完成！');
  })
  .catch((error) => {
    console.error('💥 檢查過程中發生錯誤:', error);
  });