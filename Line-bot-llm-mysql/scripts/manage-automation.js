const axios = require('axios');

/**
 * 自動化系統管理工具
 */
class AutomationManager {
  constructor() {
    this.baseUrl = 'http://localhost:3001';
  }

  /**
   * 顯示系統狀態
   */
  async showStatus() {
    try {
      console.log('🔍 檢查自動化系統狀態...\n');
      
      // 系統狀態
      const statusResponse = await axios.get(`${this.baseUrl}/admin/status`);
      const status = statusResponse.data;
      
      console.log('📊 系統狀態:');
      console.log(`   整體健康: ${status.overallHealth === 'healthy' ? '✅ 健康' : '❌ 異常'}`);
      console.log(`   運行時間: ${Math.round(status.uptime / 60)} 分鐘`);
      
      if (status.nextScheduledTime) {
        const nextTime = new Date(status.nextScheduledTime);
        console.log(`   下次執行: ${nextTime.toLocaleString('zh-TW')}`);
      }
      
      // 訂閱統計
      const subResponse = await axios.get(`${this.baseUrl}/admin/stats/subscriptions`);
      const subStats = subResponse.data;
      
      console.log('\n👥 訂閱統計:');
      console.log(`   總訂閱用戶: ${subStats.totalSubscribers}`);
      console.log(`   活躍訂閱: ${subStats.activeSubscribers}`);
      console.log(`   今日新增: ${subStats.newSubscribersToday}`);
      
      // 投遞統計
      const deliveryResponse = await axios.get(`${this.baseUrl}/admin/stats/deliveries`);
      const deliveryStats = deliveryResponse.data;
      
      console.log('\n📬 投遞統計:');
      console.log(`   總通知數: ${deliveryStats.totalNotificationsSent}`);
      console.log(`   成功投遞: ${deliveryStats.successfulDeliveries}`);
      console.log(`   失敗投遞: ${deliveryStats.failedDeliveries}`);
      console.log(`   成功率: ${deliveryStats.deliverySuccessRate.toFixed(1)}%`);
      
    } catch (error) {
      console.error('❌ 無法獲取系統狀態:', error.message);
    }
  }

  /**
   * 手動觸發新書檢查
   */
  async triggerManual() {
    try {
      console.log('🚀 手動觸發新書檢查...');
      
      const response = await axios.post(`${this.baseUrl}/admin/notifications/trigger`, {
        triggeredBy: 'Manual Management Tool',
        reason: '手動觸發新書檢查'
      });
      
      if (response.data.success) {
        console.log('✅ 觸發成功!');
        console.log(`   執行 ID: ${response.data.executionId}`);
        console.log(`   預估時間: ${response.data.estimatedDuration} 秒`);
      } else {
        console.log('❌ 觸發失敗:', response.data.message);
      }
      
    } catch (error) {
      console.error('❌ 觸發失敗:', error.message);
    }
  }

  /**
   * 顯示最近的審計日誌
   */
  async showAuditLog() {
    try {
      console.log('📋 最近的系統操作日誌:\n');
      
      const response = await axios.get(`${this.baseUrl}/admin/audit?limit=10`);
      const auditLog = response.data.entries;
      
      auditLog.forEach((entry, index) => {
        const time = new Date(entry.timestamp).toLocaleString('zh-TW');
        console.log(`${index + 1}. [${time}] ${entry.actor}`);
        console.log(`   操作: ${entry.action}`);
        console.log(`   詳情: ${entry.details}`);
        console.log('');
      });
      
    } catch (error) {
      console.error('❌ 無法獲取審計日誌:', error.message);
    }
  }

  /**
   * 顯示幫助資訊
   */
  showHelp() {
    console.log('🛠️  自動化系統管理工具\n');
    console.log('使用方式: node manage-automation.js [命令]\n');
    console.log('可用命令:');
    console.log('  status    - 顯示系統狀態');
    console.log('  trigger   - 手動觸發新書檢查');
    console.log('  audit     - 顯示操作日誌');
    console.log('  help      - 顯示此幫助資訊');
    console.log('\n範例:');
    console.log('  node manage-automation.js status');
    console.log('  node manage-automation.js trigger');
  }
}

// 主程式
async function main() {
  const manager = new AutomationManager();
  const command = process.argv[2];

  switch (command) {
    case 'status':
      await manager.showStatus();
      break;
    case 'trigger':
      await manager.triggerManual();
      break;
    case 'audit':
      await manager.showAuditLog();
      break;
    case 'help':
    case undefined:
      manager.showHelp();
      break;
    default:
      console.log(`❌ 未知命令: ${command}`);
      console.log('使用 "help" 查看可用命令');
  }
}

main().catch(console.error);