const axios = require('axios');
const fs = require('fs');
const path = require('path');

/**
 * 手動觸發真實的 8 本新書通知測試
 */
async function triggerRealBooksNotification() {
  try {
    console.log('🚀 開始手動觸發真實 8 本新書通知測試...');
    
    // 讀取真實的通知資料檔案
    const realDataPath = path.join(__dirname, '../ebook/generated_documents/notification_data_latest.json');
    const realData = JSON.parse(fs.readFileSync(realDataPath, 'utf8'));
    
    console.log('📖 真實資料統計:');
    console.log('- 處理日期:', realData.processingDate);
    console.log('- 總書籍數:', realData.totalBooksFound);
    console.log('- 成功處理:', realData.successfullyProcessed.length);
    console.log('- PDF 提取:', realData.processingStats.pdfExtractions);
    console.log('- Google 搜尋:', realData.processingStats.googleSearches);
    
    console.log('\n📚 書籍列表:');
    realData.successfullyProcessed.forEach((book, index) => {
      console.log(`${index + 1}. ${book.title}`);
      console.log(`   摘要長度: ${book.summary.length} 字元`);
      console.log(`   處理方式: ${book.processingMethod}`);
    });
    
    // 調用 LINE Bot 的手動通知觸發 API
    console.log('\n📤 發送通知觸發請求...');
    const response = await axios.post('http://localhost:3001/admin/notifications/trigger', {
      testMode: true,
      testData: realData,
      triggeredBy: 'Real Books Test',
      reason: '手動測試真實 8 本新書通知格式'
    }, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 60000 // 60秒超時（處理 8 本書可能需要更長時間）
    });
    
    console.log('✅ 通知觸發成功!');
    console.log('回應狀態:', response.status);
    console.log('回應內容:', response.data);
    
    console.log('\n📱 請檢查您的 LINE 訊息，應該會收到包含以下內容的通知:');
    console.log('- 8 本新書的標題和摘要資訊');
    console.log('- 每本書的 PDF 下載連結');
    console.log('- 處理統計資訊（6 本 PDF 提取，2 本 Google 搜尋）');
    console.log('- 根據書籍數量，可能會使用 Carousel 格式（3+ 本書）');
    
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
triggerRealBooksNotification();