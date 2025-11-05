// 測試完整流程，但不調用 LINE API
const { GeminiService } = require('./dist/services/geminiService');

async function testFullFlow() {
  try {
    console.log('測試完整處理流程...');
    
    const geminiService = new GeminiService();
    
    // 測試不同類型的用戶查詢
    const testQueries = [
      '推薦一些好書',
      '有沒有金剛經相關的書？',
      '五股有什麼書？',
      '你好',
      '', // 空字串測試
      '   ', // 只有空格的測試
    ];
    
    for (const query of testQueries) {
      console.log(`\n--- 測試查詢: "${query}" ---`);
      
      try {
        const result = await geminiService.processUserQuery(query);
        
        console.log('回應文字:', `"${result.text}"`);
        console.log('文字長度:', result.text.length);
        console.log('是否為空:', result.text === '');
        console.log('書籍數量:', result.books.length);
        
        if (result.text === '' || result.text.trim() === '') {
          console.error('❌ 發現空字串或純空格回應！');
        } else {
          console.log('✅ 回應正常');
        }
        
      } catch (error) {
        console.error('處理失敗:', error.message);
      }
    }
    
  } catch (error) {
    console.error('測試失敗:', error.message);
  }
}

testFullFlow();