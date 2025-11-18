// 直接測試 Gemini Service，不涉及 LINE API
const { GeminiService } = require('./dist/services/geminiService');

async function testGeminiService() {
  try {
    console.log('測試 Gemini Service...');
    
    const geminiService = new GeminiService();
    
    // 測試用戶查詢
    const result = await geminiService.processUserQuery('推薦一些好書');
    
    console.log('Gemini 回應:');
    console.log('文字:', result.text);
    console.log('文字長度:', result.text.length);
    console.log('是否為空:', result.text === '');
    console.log('書籍數量:', result.books.length);
    
    if (result.text === '') {
      console.error('❌ 發現空字串回應！');
    } else {
      console.log('✅ 回應正常');
    }
    
  } catch (error) {
    console.error('測試失敗:', error.message);
  }
}

testGeminiService();