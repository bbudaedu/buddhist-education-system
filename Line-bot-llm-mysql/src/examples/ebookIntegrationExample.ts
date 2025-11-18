#!/usr/bin/env node
/**
 * Example demonstrating ebook integration service usage
 * 電子書整合服務使用範例
 */

import { EbookIntegrationService, defaultFileMonitorConfig } from '../services/ebookIntegrationService';
import path from 'path';

async function demonstrateEbookIntegration() {
  console.log('🚀 Starting Ebook Integration Service Demo');
  console.log('==========================================');

  // Create service instance with custom config
  const config = {
    ...defaultFileMonitorConfig,
    watchDirectory: path.join(process.cwd(), '..', 'ebook', 'generated_documents'),
    processingTimeout: 10000,
    maxRetries: 2,
    retryDelay: 3000
  };

  const service = new EbookIntegrationService(config);

  // Set up event listeners
  service.on('monitoring-started', () => {
    console.log('✅ File monitoring started');
  });

  service.on('books-processed', (data, filePath) => {
    console.log('📚 New books processed!');
    console.log(`📄 File: ${path.basename(filePath)}`);
    console.log(`📊 Total books found: ${data.totalBooksFound}`);
    console.log(`✅ Successfully processed: ${data.successfullyProcessed.length}`);
    console.log(`📈 Processing stats:`, data.processingStats);
    
    if (data.successfullyProcessed.length > 0) {
      console.log('📖 Books:');
      data.successfullyProcessed.forEach((book: any, index: number) => {
        console.log(`  ${index + 1}. ${book.title} (${book.processingMethod})`);
        if (book.author) {
          console.log(`     Author: ${book.author}`);
        }
        console.log(`     Summary: ${book.summary.substring(0, 100)}...`);
      });
    }
  });

  service.on('processing-failed', (filePath, error) => {
    console.error(`❌ Failed to process file: ${path.basename(filePath)}`);
    console.error(`   Error: ${error}`);
  });

  service.on('error', (error) => {
    console.error('💥 Service error:', error);
  });

  try {
    // Check current status
    console.log('\n🔍 Checking Python processor status...');
    const status = await service.checkPythonProcessorStatus();
    console.log(`   Is running: ${status.isRunning}`);
    console.log(`   Has recent data: ${status.hasRecentData}`);
    if (status.lastProcessingTime) {
      console.log(`   Last processing: ${status.lastProcessingTime.toLocaleString()}`);
    }

    // Try to find existing files
    console.log('\n📁 Looking for existing notification files...');
    const latestFile = await service.findLatestProcessedFile();
    if (latestFile) {
      console.log(`📄 Found: ${path.basename(latestFile)}`);
      
      // Process the existing file
      console.log('\n🔧 Processing existing file...');
      try {
        const data = await service.processFileManually(latestFile);
        console.log(`✅ Successfully processed existing file`);
        console.log(`📊 Books found: ${data.totalBooksFound}`);
        console.log(`✅ Successfully processed: ${data.successfullyProcessed.length}`);
      } catch (error) {
        console.error(`❌ Failed to process existing file: ${error}`);
      }
    } else {
      console.log('📄 No existing files found');
    }

    // Demonstrate fallback mechanism
    console.log('\n🔄 Testing fallback mechanism...');
    const fallbackResult = await service.getProcessingResultWithFallback();
    console.log(`📊 Fallback result source: ${fallbackResult.source}`);
    console.log(`📊 Books in result: ${fallbackResult.data.successfullyProcessed.length}`);
    if (fallbackResult.message) {
      console.log(`💬 Message: ${fallbackResult.message}`);
    }

    // Start monitoring
    console.log('\n👀 Starting file monitoring...');
    await service.startMonitoring();
    
    const monitoringStatus = service.getStatus();
    console.log(`📁 Monitoring directory: ${monitoringStatus.watchDirectory}`);
    console.log(`🔍 File pattern: ${monitoringStatus.filePattern}`);
    console.log(`⚡ Is monitoring: ${monitoringStatus.isMonitoring}`);

    // Keep the demo running for a while to show monitoring
    console.log('\n⏰ Monitoring for 30 seconds...');
    console.log('   (You can run the Python ebook processor now to see live updates)');
    
    await new Promise(resolve => setTimeout(resolve, 30000));

    // Stop monitoring
    console.log('\n🛑 Stopping monitoring...');
    service.stopMonitoring();

    console.log('\n✅ Demo completed successfully!');

  } catch (error) {
    console.error('💥 Demo failed:', error);
  }
}

// Run the demo if this file is executed directly
if (require.main === module) {
  demonstrateEbookIntegration()
    .then(() => {
      console.log('\n👋 Demo finished');
      process.exit(0);
    })
    .catch((error) => {
      console.error('💥 Demo error:', error);
      process.exit(1);
    });
}

export { demonstrateEbookIntegration };