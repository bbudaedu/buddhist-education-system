// 手動測試 Gemini + Database 整合
const { GoogleGenerativeAI } = require('@google/generative-ai');
const mysql = require('mysql2/promise');
require('dotenv').config();

async function manualTest() {
  console.log('🧪 Manual Integration Test');
  console.log('==========================');

  // 建立資料庫連線
  const db = await mysql.createConnection({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
  });

  // 建立 Gemini 客戶端
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
  const model = genAI.getGenerativeModel({ 
    model: process.env.GEMINI_MODEL,
    tools: [{
      functionDeclarations: [{
        name: 'searchBooksInDatabase',
        description: '在書庫資料庫中搜尋書籍',
        parameters: {
          type: 'object',
          properties: {
            query: { type: 'string', description: '搜尋關鍵字' },
            limit: { type: 'number', description: '最多回傳幾筆結果' }
          },
          required: ['query']
        }
      }]
    }]
  });

  // 測試查詢
  const testQueries = [
    '有沒有金剛經相關的書？',
    '找一些程式設計的書',
    '推薦幾本小說'
  ];

  for (const query of testQueries) {
    console.log(`\n📝 測試查詢: "${query}"`);
    console.log('-'.repeat(50));

    try {
      const result = await model.generateContent(`你是一個友善且專業的書庫助理。當用戶詢問書籍相關問題時，你會使用 searchBooksInDatabase 函式查詢資料庫。\n\n用戶問題：${query}`);

      const response = await result.response;
      
      if (response.functionCalls && response.functionCalls.length > 0) {
        const functionCall = response.functionCalls[0];
        console.log(`🔍 Function Call: ${functionCall.name}`);
        console.log(`📋 Parameters:`, functionCall.args);

        // 執行資料庫查詢
        const searchQuery = functionCall.args.query;
        const limit = functionCall.args.limit || 5;
        
        const [books] = await db.execute(
          'SELECT book_id, title, quantity, shelf_location, library_branch FROM books WHERE title LIKE ? LIMIT ?',
          [`%${searchQuery}%`, limit]
        );

        console.log(`📚 找到 ${books.length} 本書:`);
        books.forEach((book, index) => {
          console.log(`  ${index + 1}. ${book.title}`);
          console.log(`     位置: ${book.library_branch} - ${book.shelf_location}`);
          console.log(`     庫存: ${book.quantity} 本`);
        });

        // 生成最終回應
        const finalResult = await model.generateContent([
          { role: 'user', parts: [{ text: query }] },
          { role: 'model', parts: [{ functionCall: functionCall }] },
          { 
            role: 'function', 
            parts: [{ 
              functionResponse: { 
                name: functionCall.name, 
                response: { books: JSON.stringify(books) }
              }
            }]
          }
        ]);

        const finalResponse = await finalResult.response;
        console.log(`\n🤖 AI 回應:\n${finalResponse.text()}`);
        
      } else {
        console.log(`🤖 直接回應: ${response.text()}`);
      }

    } catch (error) {
      console.error(`❌ 測試失敗:`, error.message);
    }
  }

  await db.end();
  console.log('\n✅ 測試完成！');
}

manualTest().catch(console.error);