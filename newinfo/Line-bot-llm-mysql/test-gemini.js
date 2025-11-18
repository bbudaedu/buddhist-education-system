const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

async function testGemini() {
  try {
    console.log('🤖 Testing Gemini AI connection...');
    
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: process.env.GEMINI_MODEL });

    const result = await model.generateContent('請用中文回答：你好，請簡單介紹一下你自己。');
    const response = await result.response;
    const text = response.text();

    console.log('✅ Gemini AI connected successfully!');
    console.log('🤖 Gemini response:', text);
    
  } catch (error) {
    console.error('❌ Gemini AI test failed:', error.message);
    process.exit(1);
  }
}

testGemini();