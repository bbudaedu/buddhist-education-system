const axios = require('axios');
const crypto = require('crypto');

// LINE Channel Secret
const CHANNEL_SECRET = 'a92288c46d7b1d9149b9d4dc65c2ff77';

// 生成正確的 LINE 簽名
function generateSignature(body, secret) {
  return crypto
    .createHmac('SHA256', secret)
    .update(body)
    .digest('base64');
}

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

  const body = JSON.stringify(webhookData);
  const signature = generateSignature(body, CHANNEL_SECRET);

  try {
    console.log('發送測試 webhook 請求...');
    console.log('訊息內容:', webhookData.events[0].message.text);
    
    const response = await axios.post('http://localhost:3001/webhook', webhookData, {
      headers: {
        'Content-Type': 'application/json',
        'X-Line-Signature': signature
      }
    });
    
    console.log('回應狀態:', response.status);
    console.log('回應內容:', response.data);
    
    // 等待一下讓後端處理完成
    setTimeout(() => {
      console.log('測試完成');
    }, 2000);
    
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