/**
 * Setup Admin from Subscriptions Script
 * 從訂閱用戶中設置管理員腳本
 * 
 * 自動將訂閱所有三種類型（new_books, news, cancellation）的用戶設為管理員
 * 
 * 使用方式：
 * npx ts-node scripts/setup-admin-from-subscriptions.ts
 */

import { adminService } from '../src/services/adminService';
import { subscriptionService } from '../src/services/subscriptionService';

async function main() {
  console.log('='.repeat(60));
  console.log('從訂閱用戶中設置管理員');
  console.log('='.repeat(60));
  console.log('');
  console.log('正在查找訂閱所有三種類型的用戶...');
  console.log('');

  try {
    // 取得所有訂閱用戶
    const allUsers = await subscriptionService.getSubscribedUsers();
    
    if (allUsers.length === 0) {
      console.log('❌ 沒有找到任何訂閱用戶');
      await adminService.closeConnection();
      await subscriptionService.closeConnection();
      process.exit(0);
    }

    console.log(`找到 ${allUsers.length} 位訂閱用戶`);
    console.log('');

    // 篩選訂閱所有三種類型的用戶
    const fullSubscribers = allUsers.filter(user => {
      const types = user.notificationTypes;
      return types.includes('new_books') && 
             types.includes('news') && 
             types.includes('cancellation');
    });

    if (fullSubscribers.length === 0) {
      console.log('❌ 沒有找到訂閱所有三種類型的用戶');
      console.log('');
      console.log('提示：請確保用戶已訂閱以下所有類型：');
      console.log('  - 新書通知 (new_books)');
      console.log('  - 新聞公告 (news)');
      console.log('  - 停課通知 (cancellation)');
      await adminService.closeConnection();
      await subscriptionService.closeConnection();
      process.exit(0);
    }

    console.log(`找到 ${fullSubscribers.length} 位訂閱所有類型的用戶：`);
    console.log('');

    // 將這些用戶設為管理員
    let successCount = 0;
    for (const user of fullSubscribers) {
      console.log(`處理用戶: ${user.lineUserId}${user.displayName ? ` (${user.displayName})` : ''}`);
      
      const success = await adminService.addAdmin(user.lineUserId, user.displayName);
      if (success) {
        console.log('  ✅ 已設為管理員');
        successCount++;
      } else {
        console.log('  ❌ 設置失敗');
      }
    }

    console.log('');
    console.log('='.repeat(60));
    console.log(`完成！成功設置 ${successCount} 位管理員`);
    console.log('='.repeat(60));
    console.log('');
    console.log('這些用戶現在可以使用以下測試指令：');
    console.log('  flex1 - 測試新書通知（藍色主題）');
    console.log('  flex2 - 測試新聞公告（橙色主題）');
    console.log('  flex3 - 測試停課通知（紅色主題）');
    console.log('  flex4 - 測試整合通知（包含所有類型）');
    console.log('');

    await adminService.closeConnection();
    await subscriptionService.closeConnection();
    process.exit(0);
  } catch (error) {
    console.error('❌ 執行過程中發生錯誤：', error);
    await adminService.closeConnection();
    await subscriptionService.closeConnection();
    process.exit(1);
  }
}

main();
