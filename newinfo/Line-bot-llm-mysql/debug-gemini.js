const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

async function debugGemini() {
  console.log('🔍 Debug Gemini Intent Recognition');
  console.log('==================================');

  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
  const model = genAI.getGenerativeModel({
    model: process.env.GEMINI_MODEL,
    generationConfig: {
      maxOutputTokens: 1024,
      temperature: 1,
    },
  });

  const systemInstruction = `你是一個友善且專業的書庫助理。當用戶詢問書籍相關問題時，請分析用戶的意圖：

1. 如果用戶想要搜尋書籍，請回覆 "SEARCH:" 後面跟著搜尋關鍵字
2. 如果用戶想要查詢特定館藏地的書籍，請回覆 "BRANCH:" 後面跟著館藏地名稱
3. 如果用戶只是打招呼或問其他問題，請直接友善回應

可用的館藏地點：五股、3F、2F

例如：
- 用戶問「有沒有金剛經相關的書？」→ 回覆「SEARCH:金剛經」
- 用戶問「五股有什麼書？」→ 回覆「BRANCH:五股」
- 用戶問「找五股庫存最多的書？」→ 回覆「BRANCH:五股」
- 用戶問「你好」→ 回覆「您好！我是書庫助理，可以幫您搜尋書籍資訊。」

保持回覆簡潔，不超過 200 字。`;

  const testQueries = [
    '找五股庫存最多的書？',
    '有沒有金剛經相關的書？',
    '你好',
    '推薦一些小說',
    '程式設計的書'
  ];

  for (const query of testQueries) {
    console.log(`\n📝 測試查詢: "${query}"`);
    console.log('-'.repeat(50));

    try {
      const result = await model.generateContent(systemInstruction + '\n\n用戶訊息：' + query);
      const response = result.response.text();
      
      console.log(`🤖 Gemini 回應: "${response}"`);
      
      // 檢查是否包含 SEARCH:
      if (response.startsWith('SEARCH:')) {
        const searchQuery = response.substring(7).trim();
        console.log(`🔍 提取的搜尋關鍵字: "${searchQuery}"`);
      } else {
        console.log('❌ 沒有識別為搜尋請求');
      }
      
    } catch (error) {
      console.error(`❌ 錯誤:`, error.message);
    }
  }
}

debugGemini();