const axios = require('axios');

// 模擬 LINE webhook 請求
const testWebhook = async () => {
  const webhookData = {
    events: [
      {
        type: 'message',
        replyToken: 'test-reply-token-123',
        source: {
          userId: 'test-user-123',
          type: 'user'
        },
        message: {
          type: 'text',
          text: '推薦一些好書'
        }
      }
    ]
  };

  try {
    console.log('發送測試 webhook 請求...');
    const response = await axios.post('http://localhost:3001/webhook', webhookData, {
      headers: {
        'Content-Type': 'application/json',
        'X-Line-Signature': 'test-signature' // 這會失敗，但可以測試錯誤處理
      }
    });
    
    console.log('回應狀態:', response.status);
    console.log('回應內容:', response.data);
  } catch (error) {
    if (error.response) {
      console.log('錯誤狀態:', error.response.status);
      console.log('錯誤內容:', error.response.data);
    } else {
      console.error('請求錯誤:', error.message);
    }
  }
};

testWebhook();