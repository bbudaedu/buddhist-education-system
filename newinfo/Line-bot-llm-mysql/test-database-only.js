// 直接測試資料庫服務
const { DatabaseService } = require('./dist/services/databaseService');

async function testDatabaseService() {
  try {
    console.log('測試資料庫服務...');
    
    const databaseService = new DatabaseService();
    
    // 測試搜尋功能
    console.log('搜尋書籍: "金剛經"');
    const books = await databaseService.searchBooks('金剛經', 5);
    
    console.log('搜尋結果:');
    console.log('書籍數量:', books.length);
    
    if (books.length > 0) {
      books.forEach((book, index) => {
        console.log(`${index + 1}. ${book.title} (${book.library_branch})`);
      });
    } else {
      console.log('沒有找到相關書籍');
    }
    
    // 關閉連接
    await databaseService.closeConnection();
    console.log('✅ 資料庫測試完成');
    
  } catch (error) {
    console.error('❌ 資料庫測試失敗:', error.message);
  }
}

testDatabaseService();