/**
 * Debug script to validate Flex Message structure
 */

import { flexMessageService } from './src/services/flexMessageService';

// 模擬真實資料
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
      content: '本會地下室教室(2) ，\n自 2025-12-09 起 ，\n每月第二週    星期(二)\n19:00 ~ 21:00 ，\n將由 賴金光居士 \n主講護法工作的經驗分享和傳承，\n歡迎各位蓮友同...'
    },
    {
      title: '學習坐禪（第13期）課程公告',
      date: '未知日期',
      url: 'https://www.budaedu.org/#/bulletins/1409',
      content: '本會十二樓佛堂 ，每週一晚上的「學習坐禪（第12期）」已經圓滿；\n 自 2025-12-05 起 ，改成每週\n    星期(五)\n19:00 ~ 21:00 ，\n將由 宗道法師 \n主講學習坐禪（...'
    },
    {
      title: '小菩薩的慈悲畫室－佛法讀經與護生繪畫班 課程公告',
      date: '未知日期',
      url: 'https://www.budaedu.org/#/bulletins/1408',
      content: '本會地下室教室(1) ，\n自 2025-12-07 起 ，\n每週\n    星期(日)\n14:30 ~ 16:00 ，\n將由 張貴瑛老師 \n主講小菩薩的慈悲畫室－佛法讀經與護生繪畫班...'
    }
  ]
};

console.log('Creating Flex Message...');
const message = flexMessageService.createIntegratedNotification(testData);

console.log('\n=== Flex Message Structure ===');
console.log(JSON.stringify(message, null, 2));

console.log('\n=== Validation ===');
console.log(`Type: ${message.type}`);
console.log(`Alt Text: ${message.altText}`);
console.log(`Contents Type: ${message.contents.type}`);

if (message.contents.type === 'carousel') {
  console.log(`Bubble Count: ${message.contents.contents.length}`);
  
  // 檢查每個 bubble
  message.contents.contents.forEach((bubble, index) => {
    console.log(`\nBubble ${index + 1}:`);
    console.log(`  - Type: ${bubble.type}`);
    console.log(`  - Size: ${bubble.size}`);
    console.log(`  - Has Hero: ${!!bubble.hero}`);
    console.log(`  - Has Body: ${!!bubble.body}`);
    console.log(`  - Has Footer: ${!!bubble.footer}`);
    
    // 檢查 body 內容
    if (bubble.body && bubble.body.type === 'box') {
      console.log(`  - Body Contents: ${bubble.body.contents.length} items`);
      bubble.body.contents.forEach((item: any, i: number) => {
        if (item.type === 'text') {
          const textPreview = item.text.substring(0, 50);
          console.log(`    ${i + 1}. Text: "${textPreview}${item.text.length > 50 ? '...' : ''}"`);
        }
      });
    }
  });
}

console.log('\n=== Message Size ===');
const messageJson = JSON.stringify(message);
console.log(`Total: ${messageJson.length} bytes`);
console.log(`Recommended: < 50000 bytes`);
console.log(`Status: ${messageJson.length < 50000 ? '✅ OK' : '❌ Too Large'}`);
