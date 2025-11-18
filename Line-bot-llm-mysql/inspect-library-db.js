/**
 * 詳細檢查 library_db 資料庫內容
 */

const mysql = require('mysql2/promise');
require('dotenv').config();

async function inspectLibraryDb() {
  console.log('🔍 詳細檢查 library_db 資料庫...');
  
  const config = {
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT) || 3306,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: 'library_db'
  };

  let connection;
  
  try {
    connection = await mysql.createConnection(config);
    console.log('✅ 連接到 library_db 成功！');

    // 顯示所有表
    const [tables] = await connection.query('SHOW TABLES');
    console.log('\n📋 library_db 中的表:');
    
    if (tables.length === 0) {
      console.log('   (無表)');
      return;
    }
    
    for (const tableRow of tables) {
      const tableName = Object.values(tableRow)[0];
      console.log(`\n📊 表: ${tableName}`);
      
      try {
        // 顯示表結構
        const [columns] = await connection.query(`DESCRIBE ${tableName}`);
        console.log('   欄位:');
        columns.forEach(col => {
          console.log(`     ${col.Field}: ${col.Type} ${col.Null === 'YES' ? '(可為空)' : '(不可為空)'}`);
        });
        
        // 顯示記錄數量
        const [count] = await connection.query(`SELECT COUNT(*) as count FROM ${tableName}`);
        console.log(`   記錄數: ${count[0].count}`);
        
        // 如果記錄數不多，顯示幾筆範例
        if (count[0].count > 0 && count[0].count <= 10) {
          const [samples] = await connection.query(`SELECT * FROM ${tableName} LIMIT 3`);
          console.log('   範例資料:');
          samples.forEach((row, index) => {
            console.log(`     ${index + 1}. ${JSON.stringify(row)}`);
          });
        } else if (count[0].count > 0) {
          const [samples] = await connection.query(`SELECT * FROM ${tableName} LIMIT 3`);
          console.log('   範例資料:');
          samples.forEach((row, index) => {
            const keys = Object.keys(row);
            const preview = keys.slice(0, 3).map(key => `${key}: ${row[key]}`).join(', ');
            console.log(`     ${index + 1}. ${preview}${keys.length > 3 ? '...' : ''}`);
          });
        }
        
      } catch (error) {
        console.log(`   ❌ 無法檢查表 ${tableName}: ${error.message}`);
      }
    }

  } catch (error) {
    console.error('❌ 操作失敗:', error.message);
    
    if (error.code === 'ER_BAD_DB_ERROR') {
      console.log('💡 library_db 資料庫不存在或無法訪問');
    }
    
    process.exit(1);
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}

inspectLibraryDb()
  .then(() => {
    console.log('\n🎉 檢查完成！');
  })
  .catch((error) => {
    console.error('💥 檢查過程中發生錯誤:', error);
  });