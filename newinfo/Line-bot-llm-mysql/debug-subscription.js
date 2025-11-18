const mysql = require('mysql2/promise');

async function debugSubscription() {
  const connection = await mysql.createConnection({
    host: '124.219.37.161',
    port: 3306,
    user: 'budaedu',
    password: '1Budaedu.org',
    database: 'library_db'
  });

  try {
    console.log('檢查訂閱資料...');
    
    // 查詢用戶訂閱資料
    const [rows] = await connection.execute(
      'SELECT * FROM user_subscriptions WHERE line_user_id = ?',
      ['U5a9fc549ab75277f70fb1ddb46cda7b6']
    );

    console.log('查詢結果:');
    console.log('記錄數量:', rows.length);
    
    if (rows.length > 0) {
      const row = rows[0];
      console.log('原始資料:');
      console.log('ID:', row.id);
      console.log('LINE User ID:', row.line_user_id);
      console.log('notification_preferences 類型:', typeof row.notification_preferences);
      console.log('notification_preferences 內容:', row.notification_preferences);
      console.log('notification_preferences 字串表示:', String(row.notification_preferences));
      
      // 嘗試解析
      try {
        const parsed = JSON.parse(row.notification_preferences);
        console.log('解析成功:', parsed);
      } catch (error) {
        console.error('解析失敗:', error.message);
      }
    }

  } catch (error) {
    console.error('查詢失敗:', error);
  } finally {
    await connection.end();
  }
}

debugSubscription();