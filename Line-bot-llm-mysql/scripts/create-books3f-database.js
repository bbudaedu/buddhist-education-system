/**
 * 建立 books_3f 資料庫
 * 這個腳本會檢查並建立 books_3f 資料庫，如果需要的話還會從舊資料庫複製 books 表
 */

const mysql = require('mysql2/promise');
require('dotenv').config();

async function createBooks3fDatabase() {
  console.log('🔍 檢查並建立 books_3f 資料庫...');
  
  const config = {
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT) || 3306,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD
    // 注意：這裡不指定 database，因為我們要建立它
  };

  console.log(`📊 連線配置:`);
  console.log(`   主機: ${config.host}:${config.port}`);
  console.log(`   用戶: ${config.user}`);

  let connection;
  
  try {
    // 建立連線（不指定資料庫）
    connection = await mysql.createConnection(config);
    console.log('✅ MySQL 伺服器連線成功！');

    // 檢查現有資料庫
    console.log('\n📋 檢查現有資料庫...');
    const [databases] = await connection.execute('SHOW DATABASES');
    const dbNames = databases.map(db => db.Database);
    
    console.log('現有資料庫:');
    dbNames.forEach(name => {
      console.log(`   - ${name}`);
    });

    // 檢查 books_3f 是否存在
    if (dbNames.includes('books_3f')) {
      console.log('\n✅ books_3f 資料庫已存在！');
    } else {
      console.log('\n🔨 建立 books_3f 資料庫...');
      await connection.execute('CREATE DATABASE books_3f CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci');
      console.log('✅ books_3f 資料庫建立成功！');
    }

    // 切換到 books_3f 資料庫
    await connection.execute('USE books_3f');
    console.log('\n📂 已切換到 books_3f 資料庫');

    // 檢查 books 表是否存在
    try {
      const [tables] = await connection.execute("SHOW TABLES LIKE 'books'");
      
      if (tables.length === 0) {
        console.log('\n⚠️  books 表不存在，需要建立或匯入');
        
        // 檢查是否有其他可能的資料庫包含 books 表
        const possibleDatabases = dbNames.filter(name => 
          name.includes('book') || name.includes('library') || name === 'budaedu'
        );
        
        if (possibleDatabases.length > 0) {
          console.log('\n🔍 發現可能包含 books 表的資料庫:');
          
          for (const dbName of possibleDatabases) {
            try {
              await connection.execute(`USE ${dbName}`);
              const [bookTables] = await connection.execute("SHOW TABLES LIKE 'books'");
              
              if (bookTables.length > 0) {
                const [bookCount] = await connection.execute('SELECT COUNT(*) as count FROM books');
                console.log(`   ✅ ${dbName} 包含 books 表 (${bookCount[0].count} 筆記錄)`);
                
                // 詢問是否要複製
                console.log(`\n📋 發現 ${dbName}.books 表，準備複製到 books_3f...`);
                
                // 複製表結構和資料
                await connection.execute('USE books_3f');
                await connection.execute(`CREATE TABLE books AS SELECT * FROM ${dbName}.books`);
                
                const [newCount] = await connection.execute('SELECT COUNT(*) as count FROM books');
                console.log(`✅ 成功複製 ${newCount[0].count} 筆書籍記錄到 books_3f.books`);
                break;
              } else {
                console.log(`   ❌ ${dbName} 不包含 books 表`);
              }
            } catch (error) {
              console.log(`   ❌ 無法檢查 ${dbName}: ${error.message}`);
            }
          }
        } else {
          console.log('\n⚠️  未找到包含 books 表的資料庫');
          console.log('💡 你可能需要：');
          console.log('   1. 手動匯入書籍資料');
          console.log('   2. 或者確認正確的來源資料庫名稱');
        }
      } else {
        const [bookCount] = await connection.execute('SELECT COUNT(*) as count FROM books');
        console.log(`✅ books 表已存在，包含 ${bookCount[0].count} 筆記錄`);
      }
    } catch (error) {
      console.log(`❌ 檢查 books 表時發生錯誤: ${error.message}`);
    }

    // 檢查表結構
    try {
      await connection.execute('USE books_3f');
      const [tables] = await connection.execute('SHOW TABLES');
      
      console.log('\n📋 books_3f 資料庫中的表:');
      tables.forEach(table => {
        const tableName = Object.values(table)[0];
        console.log(`   - ${tableName}`);
      });

      // 如果有 books 表，顯示結構
      const [bookTables] = await connection.execute("SHOW TABLES LIKE 'books'");
      if (bookTables.length > 0) {
        console.log('\n📊 books 表結構:');
        const [columns] = await connection.execute('DESCRIBE books');
        columns.forEach(col => {
          console.log(`   ${col.Field}: ${col.Type} ${col.Null === 'YES' ? '(可為空)' : '(不可為空)'}`);
        });
      }

    } catch (error) {
      console.log(`❌ 檢查表結構時發生錯誤: ${error.message}`);
    }

  } catch (error) {
    console.error('❌ 操作失敗:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      console.log('💡 建議檢查:');
      console.log('   1. MySQL 服務是否正在運行');
      console.log('   2. 主機和端口設定是否正確');
    } else if (error.code === 'ER_ACCESS_DENIED_ERROR') {
      console.log('💡 建議檢查:');
      console.log('   1. 用戶名和密碼是否正確');
      console.log('   2. 用戶是否有建立資料庫的權限');
    }
    
    process.exit(1);
  } finally {
    if (connection) {
      await connection.end();
      console.log('\n🔌 資料庫連線已關閉');
    }
  }
}

// 執行建立資料庫
createBooks3fDatabase()
  .then(() => {
    console.log('\n🎉 books_3f 資料庫設定完成！');
    console.log('\n📝 下一步:');
    console.log('   1. 執行 npm run test:db 測試連線');
    console.log('   2. 執行 npm run migrate 建立通知系統表');
    console.log('   3. 執行 npm run dev 啟動服務');
    process.exit(0);
  })
  .catch((error) => {
    console.error('💥 設定過程中發生錯誤:', error);
    process.exit(1);
  });