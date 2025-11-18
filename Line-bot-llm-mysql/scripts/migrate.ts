#!/usr/bin/env ts-node

import { databaseService } from '../src/services/databaseService';

/**
 * Database migration runner script
 * Usage: npm run migrate
 */
async function runMigrations() {
  console.log('🚀 Starting database migrations...');
  
  try {
    // 測試資料庫連線
    const isConnected = await databaseService.testConnection();
    if (!isConnected) {
      throw new Error('Database connection failed');
    }
    
    console.log('✅ Database connection successful');
    
    // 執行遷移
    await databaseService.runMigrations();
    
    console.log('🎉 All migrations completed successfully!');
    
  } catch (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  } finally {
    // 關閉資料庫連線
    await databaseService.closeConnection();
  }
}

// 執行遷移
runMigrations();