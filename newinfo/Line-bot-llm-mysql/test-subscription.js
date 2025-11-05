// 測試訂閱功能
const { SubscriptionService } = require('./dist/services/subscriptionService');

async function testSubscription() {
  try {
    console.log('測試訂閱服務...');
    
    const subscriptionService = new SubscriptionService();
    const userId = 'U5a9fc549ab75277f70fb1ddb46cda7b6';
    
    // 測試取得用戶訂閱狀態
    console.log('取得用戶訂閱狀態...');
    const subscription = await subscriptionService.getUserSubscription(userId);
    
    if (subscription) {
      console.log('✅ 成功取得訂閱資訊:');
      console.log('用戶ID:', subscription.lineUserId);
      console.log('是否訂閱:', subscription.isSubscribed);
      console.log('訂閱日期:', subscription.subscriptionDate);
      console.log('通知偏好:', subscription.notificationPreferences);
    } else {
      console.log('❌ 沒有找到訂閱資訊');
    }
    
    // 測試檢查是否已訂閱
    console.log('\n檢查是否已訂閱...');
    const isSubscribed = await subscriptionService.isUserSubscribed(userId);
    console.log('是否已訂閱:', isSubscribed);
    
  } catch (error) {
    console.error('❌ 測試失敗:', error.message);
    console.error('錯誤堆疊:', error.stack);
  }
}

testSubscription();