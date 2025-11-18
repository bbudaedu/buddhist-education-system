// 測試實際的 GeminiService
const { GeminiService } = require('./dist/services/geminiService.js');
const { DatabaseService } = require('./dist/services/databaseService.js');

async function testRealService() {
  console.log('🧪 Testing Real GeminiService');
  console.log('==============================');

  try {
    // 先編譯 TypeScript
    console.log('📦 Building TypeScript...');
    const { execSync } = require('child_process');
    execSync('npm run build', { stdio: 'inherit' });

    // 測試服務
    const geminiService = new GeminiService();
    
    const testQueries = [
      '有沒有金剛經相關的書？',
      '找一些程式設計的書',
      '你好'
    ];

    for (const query of testQueries) {
      console.log(`\n📝 測試查詢: "${query}"`);
      console.log('-'.repeat(50));

      const result = await geminiService.processUserQuery(query);
      
      console.log(`📚 找到 ${result.books.length} 本書`);
      console.log(`🤖 AI 回應:\n${result.text}`);
      
      if (result.books.length > 0) {
        console.log('\n📖 書籍詳情:');
        result.books.slice(0, 3).forEach((book, index) => {
          console.log(`  ${index + 1}. ${book.title}`);
          console.log(`     位置: ${book.library_branch} - ${book.shelf_location}`);
          console.log(`     庫存: ${book.quantity} 本`);
        });
      }
    }

    console.log('\n✅ 測試完成！');
    
  } catch (error) {
    console.error('❌ 測試失敗:', error.message);
  }
}

testRealService();