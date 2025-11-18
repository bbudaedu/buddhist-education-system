/**
 * Example usage of NotificationService for daily book notifications
 * This demonstrates how to process book data and send notifications
 */

import { NotificationService } from '../services/notificationService';
import { MessageTemplateService } from '../services/messageTemplateService';
import { ProcessedBookData } from '../types/notification';
import { UserSubscription } from '../types/subscription';

// Example processed book data (as would come from Python ebook system)
const exampleBookData: ProcessedBookData = {
  processingDate: new Date().toISOString(),
  totalBooksFound: 3,
  successfullyProcessed: [
    {
      title: '金剛般若波羅蜜經講記',
      author: '淨空法師',
      summary: '本書詳細解釋了金剛經的深奧義理，以現代語言闡述佛法智慧，適合初學者和進階修行者閱讀。書中包含了豐富的實修指導和生活應用。',
      downloadUrl: 'https://example.com/books/jingang-jing.pdf',
      processingMethod: 'pdf_extract',
      processingSuccess: true
    },
    {
      title: '心經的智慧',
      author: '聖嚴法師',
      summary: '透過心經的短短260字，揭示了佛法的核心智慧。本書以淺顯易懂的方式，解釋空性的真義和修行的要點。',
      downloadUrl: 'https://example.com/books/xin-jing.pdf',
      processingMethod: 'google_search',
      processingSuccess: true
    },
    {
      title: '佛教入門指南',
      author: '星雲大師',
      summary: '為初學者量身打造的佛教入門書籍，涵蓋佛教基本教義、修行方法和日常實踐，是學佛路上的良師益友。',
      downloadUrl: 'https://example.com/books/rujmen-zhinan.pdf',
      processingMethod: 'pdf_extract',
      processingSuccess: true
    }
  ],
  processingStats: {
    booksProcessed: 3,
    booksFailed: 0,
    pdfExtractions: 2,
    googleSearches: 1
  }
};

// Example user subscription
const exampleUser: UserSubscription = {
  id: 1,
  lineUserId: 'U1234567890abcdef',
  displayName: '測試用戶',
  isSubscribed: true,
  subscriptionDate: new Date('2024-01-01'),
  lastNotificationSent: undefined,
  notificationPreferences: {
    enableSummary: true,
    enableDownloadLink: true,
    maxBooksPerNotification: 3
  },
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date()
};

/**
 * Example function to demonstrate notification message creation
 */
function demonstrateMessageTemplates() {
  console.log('=== Notification Message Template Examples ===\n');
  
  const messageTemplateService = new MessageTemplateService();
  
  // Single book message
  console.log('1. Single Book Message:');
  const singleBookContent = messageTemplateService.createNotificationContent(
    [exampleBookData.successfullyProcessed[0]!], 
    exampleUser, 
    'single_book'
  );
  console.log('Fallback Text:', singleBookContent.text);
  console.log('Has Flex Message:', !!singleBookContent.flexMessage);
  console.log('Has Quick Reply:', !!singleBookContent.quickReply);
  console.log();
  
  // Multiple books message
  console.log('2. Multiple Books Message:');
  const multipleBooksContent = messageTemplateService.createNotificationContent(
    exampleBookData.successfullyProcessed.slice(0, 2), 
    exampleUser, 
    'multiple_books'
  );
  console.log('Fallback Text:', multipleBooksContent.text.substring(0, 200) + '...');
  console.log('Has Flex Message:', !!multipleBooksContent.flexMessage);
  console.log();
  
  // Daily summary message
  console.log('3. Daily Summary Message:');
  const summaryContent = messageTemplateService.createNotificationContent(
    exampleBookData.successfullyProcessed, 
    exampleUser, 
    'daily_summary'
  );
  console.log('Fallback Text:', summaryContent.text.substring(0, 200) + '...');
  console.log('Has Flex Message:', !!summaryContent.flexMessage);
  console.log();
}

/**
 * Example function to demonstrate notification processing workflow
 */
async function demonstrateNotificationWorkflow() {
  console.log('=== Notification Processing Workflow ===\n');
  
  try {
    // Create notification service instance
    const notificationService = new NotificationService({
      maxRecipientsPerBatch: 10,
      enableRichMessages: true,
      maxBooksPerMessage: 5
    });
    
    console.log('1. NotificationService created successfully');
    
    // Demonstrate book data validation
    const isValidData = (notificationService as any).validateBookData(exampleBookData);
    console.log('2. Book data validation:', isValidData ? 'PASSED' : 'FAILED');
    
    // Demonstrate message creation
    const messages = notificationService.createNotificationMessages(
      exampleBookData.successfullyProcessed,
      [exampleUser]
    );
    console.log('3. Created notification messages:', messages.length);
    
    if (messages.length > 0 && messages[0]) {
      console.log('   - Message ID:', messages[0].id);
      console.log('   - Message Type:', messages[0].messageType);
      console.log('   - Recipient:', messages[0].recipientUserId);
      console.log('   - Status:', messages[0].deliveryStatus);
    }
    
    // Demonstrate batch creation
    const batches = (notificationService as any).createBatches(messages, 2);
    console.log('4. Created batches:', batches.length);
    
    console.log('\n✅ Notification workflow demonstration completed successfully');
    
  } catch (error) {
    console.error('❌ Error in notification workflow:', error);
  }
}

/**
 * Main demonstration function
 */
async function runExamples() {
  console.log('📚 Daily Book Notification System - Examples\n');
  console.log('This demonstrates the notification service and message templates');
  console.log('created for the daily book notifications feature.\n');
  
  // Run message template examples
  demonstrateMessageTemplates();
  
  // Run notification workflow examples
  await demonstrateNotificationWorkflow();
  
  console.log('\n🎉 All examples completed!');
  console.log('\nNext steps:');
  console.log('- Implement daily scheduler service (Task 4)');
  console.log('- Create integration with Python ebook processor (Task 8)');
  console.log('- Set up database migrations (Task 6.2)');
}

// Export for use in other modules
export {
  exampleBookData,
  exampleUser,
  demonstrateMessageTemplates,
  demonstrateNotificationWorkflow,
  runExamples
};

// Run examples if this file is executed directly
if (require.main === module) {
  runExamples().catch(console.error);
}