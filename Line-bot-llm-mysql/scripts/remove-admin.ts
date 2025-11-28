/**
 * Remove Admin User Script
 * 移除管理員用戶腳本
 * 
 * 使用方式：
 * npx ts-node scripts/remove-admin.ts <LINE_USER_ID>
 */

import { adminService } from '../src/services/adminService';

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('❌ 錯誤：請提供 LINE User ID');
    console.log('\n使用方式：');
    console.log('  npx ts-node scripts/remove-admin.ts <LINE_USER_ID>');
    console.log('\n範例：');
    console.log('  npx ts-node scripts/remove-admin.ts U1234567890abcdef');
    process.exit(1);
  }

  const userId = args[0];

  console.log('='.repeat(60));
  console.log('移除管理員用戶');
  console.log('='.repeat(60));
  console.log(`LINE User ID: ${userId}`);
  console.log('');

  try {
    const success = await adminService.removeAdmin(userId);
    
    if (success) {
      console.log('✅ 成功移除管理員用戶');
    } else {
      console.error('❌ 移除管理員用戶失敗');
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
