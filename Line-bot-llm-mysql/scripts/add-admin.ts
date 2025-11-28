/**
 * Add Admin User Script
 * 添加管理員用戶腳本
 * 
 * 使用方式：
 * npx ts-node scripts/add-admin.ts <LINE_USER_ID> [DISPLAY_NAME]
 */

import { adminService } from '../src/services/adminService';

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('❌ 錯誤：請提供 LINE User ID');
    console.log('\n使用方式：');
    console.log('  npx ts-node scripts/add-admin.ts <LINE_USER_ID> [DISPLAY_NAME]');
    console.log('\n範例：');
    console.log('  npx ts-node scripts/add-admin.ts U1234567890abcdef "管理員"');
    process.exit(1);
  }

  const userId = args[0];
  const displayName = args[1] || undefined;

  console.log('='.repeat(60));
  console.log('添加管理員用戶');
  console.log('='.repeat(60));
  console.log(`LINE User ID: ${userId}`);
  if (displayName) {
    console.log(`顯示名稱: ${displayName}`);
  }
  console.log('');

  try {
    const success = await adminService.addAdmin(userId, displayName);
    
    if (success) {
      console.log('✅ 成功添加管理員用戶');
      console.log('');
      console.log('該用戶現在可以使用以下測試指令：');
      console.log('  flex1 - 測試新書通知（藍色主題）');
      console.log('  flex2 - 測試新聞公告（橙色主題）');
      console.log('  flex3 - 測試停課通知（紅色主題）');
      console.log('  flex4 - 測試整合通知（包含所有類型）');
    } else {
      console.error('❌ 添加管理員用戶失敗');
      process.exit(1);
    }

    // 顯示當前所有管理員
    console.log('');
    console.log('='.repeat(60));
    console.log('當前所有管理員：');
    console.log('='.repeat(60));
    
    const admins = await adminService.getAllAdmins();
    if (admins.length === 0) {
      console.log('（無）');
    } else {
      admins.forEach((admin, index) => {
        console.log(`${index + 1}. ${admin.lineUserId}${admin.displayName ? ` (${admin.displayName})` : ''}`);
      });
    }

    await adminService.closeConnection();
    process.exit(0);
  } catch (error) {
    console.error('❌ 執行過程中發生錯誤：', error);
    await adminService.closeConnection();
    process.exit(1);
  }
}

main();
