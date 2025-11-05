const axios = require('axios');
const fs = require('fs');
const path = require('path');

/**
 * 手動觸發單本書籍通知測試
 */
async function triggerSingleBookNotification() {
  try {
    console.log('🚀 開始手動觸發單本書籍通知測試...');
    
    // 讀取測試資料檔案
    const testDataPath = path.join(__dirname, '../ebook/test_single_book_notification.json');
    const testData = JSON.parse(fs.readFileSync(testDataPath, 'utf8'));
    
    console.log('📖 測試資料:');
    console.log('- 書籍標題:', testData.successfullyProcessed[0].title);
    console.log('- 作者:', testData.successfullyProcessed[0].author);
    console.log('- 摘要長度:', testData.successfullyProcessed[0].summary.length, '字元');
    
    // 調用 LINE Bot 的手動通知觸發 API
    console.log('\n📤 發送通知觸發請求...');
    const response = await axios.post('http://localhost:3001/admin/notifications/trigger', {
      testMode: true,
      testData: testData,
      reason: '手動測試單本書籍通知格式'
    }, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 30000 // 30秒超時
    });
    
    console.log('✅ 通知觸發成功!');
    console.log('回應狀態:', response.status);
    console.log('回應內容:', response.data);
    
    console.log('\n📱 請檢查您的 LINE 訊息，應該會收到包含以下內容的通知:');
    console.log('- 書籍標題和作者資訊');
    console.log('- AI 生成的內容摘要');
    console.log('- PDF 下載連結');
    console.log('- 處理統計資訊');
    
  } catch (error) {
    console.error('❌ 觸發通知失敗:');
    
    if (error.response) {
      console.error('HTTP 狀態:', error.response.status);
      console.error('錯誤訊息:', error.response.data);
    } else if (error.request) {
      console.error('請求失敗:', error.message);
      console.error('請確認 LINE Bot 服務是否正在運行 (http://localhost:3001)');
    } else {
      console.error('錯誤:', error.message);
    }
  }
}

// 執行測試
triggerSingleBookNotification();