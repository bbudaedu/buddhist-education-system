#!/usr/bin/env ts-node

import { getSchedulerInstance } from '../src/services/dailySchedulerService';
import { config } from '../src/config';

/**
 * Daily scheduler service runner script
 * Usage: npm run scheduler
 */
async function startScheduler() {
  console.log('🚀 Starting daily scheduler service...');
  
  try {
    // 檢查排程器是否啟用
    if (!config.scheduler.enabled) {
      console.log('⚠️  Scheduler is disabled in configuration');
      process.exit(0);
    }
    
    console.log(`📅 Scheduler configured for daily execution at ${config.scheduler.dailyExecutionTime} (${config.scheduler.timeZone})`);
    console.log(`🔄 Max retries: ${config.scheduler.maxRetries}`);
    console.log(`⏱️  Retry delay: ${config.scheduler.retryDelayMinutes} minutes`);
    
    // 啟動排程器
    const schedulerService = getSchedulerInstance();
    await schedulerService.start();
    
    console.log('✅ Daily scheduler service started successfully!');
    console.log('Press Ctrl+C to stop the scheduler');
    
    // 處理優雅關閉
    process.on('SIGINT', async () => {
      console.log('\n🛑 Received SIGINT, shutting down gracefully...');
      schedulerService.stop();
      console.log('👋 Scheduler stopped');
      process.exit(0);
    });
    
    process.on('SIGTERM', async () => {
      console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
      schedulerService.stop();
      console.log('👋 Scheduler stopped');
      process.exit(0);
    });
    
  } catch (error) {
    console.error('❌ Failed to start scheduler:', error);
    process.exit(1);
  }
}

// 啟動排程器
startScheduler();