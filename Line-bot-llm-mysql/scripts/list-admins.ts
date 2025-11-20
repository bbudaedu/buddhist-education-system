/**
 * List Admin Users Script
 * 列出所有管理員用戶腳本
 * 
 * 使用方式：
 * npx ts-node scripts/list-admins.ts
 */

import { adminService } from '../src/services/adminService';

async function main() {
  console.log('='.repeat(60));
  console.log('管理員用戶列表');
  console.log('='.repeat(60));
  console.log('');

  try {
    const admins = await adminService.getAllAdmins();
    
    if (admins.length === 0) {
      console.log('目前沒有管理員用戶');
    } else {
      console.log(`共 ${admins.length} 位管理員：\n`);
      
      admins.forEach((admin, index) => {
        console.log(`${index + 1}. LINE User ID: ${admin.lineUserId}`);
        if (admin.displayName) {
          console.log(`   顯示名稱: ${admin.displayName}`);
        }
        console.log(`   創建時間: ${admin.createdAt.toLocaleString('zh-TW')}`);
        console.log('');
      });
    }

    console.log('='.repeat(60));
    console.log('管理員可用的測試指令：');
    console.log('='.repeat(60));
    console.log('  flex1 - 測試新書通知（藍色主題）');
    console.log('  flex2 - 測試新聞公告（橙色主題）');
    console.log('  flex3 - 測試停課通知（紅色主題）');
    console.log('  flex4 - 測試整合通知（包含所有類型）');
    console.log('');

    await adminService.closeConnection();
    process.exit(0);
  } catch (error) {
    console.error('❌ 執行過程中發生錯誤：', error);
    await adminService.closeConnection();
    process.exit(1);
  }
}

main();
