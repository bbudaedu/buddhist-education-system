/**
 * Validate Flex Message with LINE API
 * This script will attempt to validate the Flex Message structure using LINE's validation endpoint
 */

import axios from 'axios';
import { config } from './src/config';
import { flexMessageService } from './src/services/flexMessageService';

async function validateFlexMessage() {
  console.log('🔍 Validating Flex Message with LINE API...\n');

  // 準備測試資料
  const testData = {
    newBooks: [
      {
        title: '法苑珠林',
        author: '未知作者',
        pdfUrls: []
      },
      {
        title: '經律異相 (16K精裝)',
        author: '未知作者',
        pdfUrls: []
      },
      {
        title: '實用佛學辭典',
        author: '未知作者',
        pdfUrls: []
      }
    ],
    news: [
      {
        title: '護法工作的經驗分享和傳承課程公告',
        date: '未知日期',
        url: 'https://www.budaedu.org/#/bulletins/1410',
        content: '本會地下室教室(2) ，\n自 2025-12-09 起 ，\n   每月第二週    星期(二)\n19:00 ~ 21:00 ，\n將由 賴金光居士 \n主講護法工作的經驗分享和傳承，\n歡迎各位蓮友同修，蒞...'
      },
      {
        title: '學習坐禪（第13期）課程公告',
        date: '未知日期',
        url: 'https://www.budaedu.org/#/bulletins/1409',
        content: '本會十二樓佛堂 ，每週一晚上的「學習坐禪（第12期）」已經圓滿；\n 自 2025-12-05 起 ，改成每週\n    星期(五)\n19:30 ~ 21:00 ，\n將由 宗道法師 \n主講學習坐禪（第13...'
      },
      {
        title: '小菩薩的慈悲畫室－佛法讀經與護生繪畫班 課程公告',
        date: '未知日期',
        url: 'https://www.budaedu.org/#/bulletins/1408',
        content: '本會地下室教室(1) ，\n自 2025-12-07 起 ，\n      每週\n    星期(日)\n14:30 ~ 16:00 ，\n將由 張貴瑛老師 \n主講小菩薩的慈悲畫室－佛法讀經與護生繪畫班，\n歡迎...'
      }
    ]
  };

  // 創建 Flex Message
  const message = flexMessageService.createIntegratedNotification(testData);
  
  console.log('📋 Message structure:');
  console.log(`   Type: ${message.type}`);
  console.log(`   Alt Text: ${message.altText}`);
  console.log(`   Bubbles: ${message.contents.type === 'carousel' ? message.contents.contents.length : 1}`);
  console.log(`   Size: ${JSON.stringify(message).length} bytes\n`);

  // 嘗試使用 LINE Bot API 的 validate endpoint
  // 注意：LINE 沒有公開的 validate endpoint，所以我們用 push message 測試
  
  const testUserId = process.env.TEST_LINE_USER_ID;
  
  if (!testUserId) {
    console.log('❌ TEST_LINE_USER_ID not set in .env');
    console.log('   Please add your LINE User ID to test actual sending\n');
    console.log('💡 To get your LINE User ID:');
    console.log('   1. Send any message to your bot');
    console.log('   2. Check the server logs for "Processing message from user"');
    console.log('   3. The userId will be shown in the logs\n');
    return;
  }

  try {
    console.log(`📤 Attempting to send to user: ${testUserId}...\n`);
    
    const response = await axios.post(
      'https://api.line.me/v2/bot/message/push',
      {
        to: testUserId,
        messages: [message]
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${config.line.channelAccessToken}`
        }
      }
    );

    console.log('✅ Message sent successfully!');
    console.log(`   Status: ${response.status}`);
    console.log(`   Response:`, response.data);
    
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('❌ LINE API Error:');
      console.error(`   Status: ${error.response?.status}`);
      console.error(`   Status Text: ${error.response?.statusText}`);
      console.error(`   Error Data:`, JSON.stringify(error.response?.data, null, 2));
      
      // 如果是 400 錯誤，顯示詳細資訊
      if (error.response?.status === 400) {
        console.error('\n🔍 Possible issues:');
        console.error('   1. Invalid Flex Message structure');
        console.error('   2. Text content contains invalid characters');
        console.error('   3. URL format is incorrect');
        console.error('   4. Bubble count exceeds limit (max 10)');
        console.error('   5. Message size exceeds limit (max 50KB)');
      }
    } else {
      console.error('❌ Unexpected error:', error);
    }
    
    process.exit(1);
  }
}

validateFlexMessage()
  .then(() => {
    console.log('\n✅ Validation completed');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Validation failed:', error);
    process.exit(1);
  });
