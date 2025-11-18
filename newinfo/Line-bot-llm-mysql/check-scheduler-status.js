const axios = require('axios');

async function checkSchedulerStatus() {
  try {
    console.log('🔍 檢查排程器狀態...\n');
    
    // 檢查系統狀態
    const statusResponse = await axios.get('http://localhost:3001/admin/status');
    const status = statusResponse.data;
    
    console.log('📊 系統狀態總覽:');
    console.log('- 整體健康狀態:', status.overallHealth);
    console.log('- 運行時間:', Math.round(status.uptime / 60), '分鐘');
    console.log('- 下次排程執行:', status.nextScheduledTime ? new Date(status.nextScheduledTime).toLocaleString('zh-TW') : '未設定');
    console.log('- 活躍服務:', status.activeServices.join(', '));
    
    if (status.criticalIssues.length > 0) {
      console.log('❌ 嚴重問題:', status.criticalIssues);
    }
    
    if (status.warnings.length > 0) {
      console.log('⚠️ 警告:', status.warnings);
    }
    
    // 檢查詳細健康狀態
    console.log('\n🏥 詳細健康檢查:');
    const healthResponse = await axios.get('http://localhost:3001/health/detailed');
    const health = healthResponse.data;
    
    console.log('- 資料庫:', health.services.database.status);
    console.log('- 排程器:', health.services.scheduler.status);
    console.log('- 通知系統:', health.services.notification.status);
    console.log('- 檔案系統:', health.services.fileSystem.status);
    
    // 檢查訂閱統計
    console.log('\n📊 訂閱統計:');
    const subscriptionResponse = await axios.get('http://localhost:3001/admin/stats/subscriptions');
    const subscriptionStats = subscriptionResponse.data;
    
    console.log('- 總訂閱用戶:', subscriptionStats.totalSubscribers);
    console.log('- 活躍訂閱:', subscriptionStats.activeSubscribers);
    console.log('- 今日新訂閱:', subscriptionStats.newSubscribersToday);
    
    console.log('\n✅ 排程器狀態檢查完成');
    
  } catch (error) {
    console.error('❌ 檢查失敗:', error.message);
    if (error.response) {
      console.error('HTTP 狀態:', error.response.status);
      console.error('錯誤內容:', error.response.data);
    }
  }
}

checkSchedulerStatus();