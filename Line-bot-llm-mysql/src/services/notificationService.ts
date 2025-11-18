import * as fs from 'fs/promises';
import * as line from '@line/bot-sdk';
import { lineConfig } from '../config/index';
import { subscriptionService } from './subscriptionService';
import { messageTemplateService } from './messageTemplateService';
import { errorRecoveryService } from './errorRecoveryService';
import {
  ProcessedBookData,
  BookSummary,
  NotificationMessage,
  DeliveryResult,
  DeliveryFailureInfo,
  NotificationConfig
} from '../types/notification';
import { UserSubscription, DeliveryErrorType } from '../types/subscription';

/**
 * NotificationService handles processing and delivering daily book notifications
 * Integrates with Python ebook processor and LINE messaging system
 */
export class NotificationService {
  private client: line.messagingApi.MessagingApiClient;
  private config: NotificationConfig;

  constructor(config?: Partial<NotificationConfig>) {
    this.client = new line.messagingApi.MessagingApiClient({
      channelAccessToken: lineConfig.channelAccessToken
    });

    // Default configuration
    this.config = {
      maxRecipientsPerBatch: 50,
      deliveryTimeoutMs: 30000,
      maxBooksPerMessage: 5,
      enableRichMessages: true,
      retryAttempts: 3,
      retryDelayMs: 1000,
      ...config
    };
  }

  /**
   * Process new books from Python ebook system and deliver notifications
   * @param ebookDataPathOrData Path to the JSON file containing processed book data or ProcessedBookData object
   * @returns Promise<DeliveryResult> Delivery statistics and results
   */
  async processNewBooks(ebookDataPathOrData: string | ProcessedBookData): Promise<DeliveryResult> {
    const startTime = Date.now();
    
    try {
      let bookData: ProcessedBookData | null;
      
      // Handle both file path and direct data object
      if (typeof ebookDataPathOrData === 'string') {
        // Read processed book data from Python ebook system
        bookData = await this.readProcessedBookData(ebookDataPathOrData);
      } else {
        // Use provided data object directly
        bookData = ebookDataPathOrData;
        
        // Validate data structure
        if (!this.validateBookData(bookData)) {
          throw new Error('Invalid book data structure');
        }
        
        console.log(`Processing provided book data: ${bookData.successfullyProcessed.length} books`);
      }
      
      if (!bookData || bookData.successfullyProcessed.length === 0) {
        console.log('No new books to process for notifications');
        return {
          totalRecipients: 0,
          successfulDeliveries: 0,
          failedDeliveries: 0,
          deliveryFailures: [],
          processingTime: Date.now() - startTime
        };
      }

      // Get all subscribed users
      const subscribedUsers = await subscriptionService.getSubscribedUsers();
      
      if (subscribedUsers.length === 0) {
        console.log('No subscribed users found');
        return {
          totalRecipients: 0,
          successfulDeliveries: 0,
          failedDeliveries: 0,
          deliveryFailures: [],
          processingTime: Date.now() - startTime
        };
      }

      // Create notification messages for each user
      const notificationMessages = this.createNotificationMessages(
        bookData.successfullyProcessed,
        subscribedUsers
      );

      // Deliver notifications in batches
      const deliveryResult = await this.deliverNotifications(notificationMessages);

      // Log notification processing results
      await this.logNotificationResults(bookData, deliveryResult);

      return {
        ...deliveryResult,
        processingTime: Date.now() - startTime
      };

    } catch (error) {
      console.error('Error processing new books for notifications:', error);
      throw new Error(`Failed to process book notifications: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Read and parse processed book data from Python ebook system
   * @param filePath Path to the JSON file containing book data
   * @returns Promise<ProcessedBookData | null> Parsed book data or null if file doesn't exist
   */
  async readProcessedBookData(filePath: string): Promise<ProcessedBookData | null> {
    try {
      // Check if file exists
      await fs.access(filePath);
      
      // Read and parse JSON file
      const fileContent = await fs.readFile(filePath, 'utf-8');
      const bookData: ProcessedBookData = JSON.parse(fileContent);
      
      // Validate data structure
      if (!this.validateBookData(bookData)) {
        throw new Error('Invalid book data structure');
      }

      console.log(`Successfully read book data: ${bookData.successfullyProcessed.length} books processed`);
      return bookData;

    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        console.log(`Book data file not found: ${filePath}`);
        return null;
      }
      
      console.error('Error reading processed book data:', error);
      throw new Error(`Failed to read book data from ${filePath}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Create notification messages for users based on their preferences
   * @param books Array of processed book summaries
   * @param users Array of subscribed users
   * @returns NotificationMessage[] Array of notification messages to send
   */
  createNotificationMessages(books: BookSummary[], users: UserSubscription[]): NotificationMessage[] {
    const messages: NotificationMessage[] = [];

    for (const user of users) {
      try {
        // Filter books based on user preferences
        const userBooks = this.filterBooksForUser(books, user);
        
        if (userBooks.length === 0) {
          continue;
        }

        // Determine message type based on number of books
        const messageType = userBooks.length === 1 ? 'single_book' : 
                           userBooks.length <= this.config.maxBooksPerMessage ? 'multiple_books' : 
                           'daily_summary';

        // Create message content
        const content = this.createMessageContent(userBooks, user, messageType);

        const message: NotificationMessage = {
          id: `${Date.now()}-${user.lineUserId}`,
          recipientUserId: user.lineUserId,
          messageType,
          content,
          deliveryStatus: 'pending',
          createdAt: new Date()
        };

        messages.push(message);

      } catch (error) {
        console.error(`Error creating message for user ${user.lineUserId}:`, error);
      }
    }

    return messages;
  }

  /**
   * Deliver notifications to users with batching and rate limiting
   * @param messages Array of notification messages to deliver
   * @returns Promise<DeliveryResult> Delivery statistics and failures
   */
  async deliverNotifications(messages: NotificationMessage[]): Promise<DeliveryResult> {
    const deliveryFailures: DeliveryFailureInfo[] = [];
    let successfulDeliveries = 0;
    let failedDeliveries = 0;

    // Process messages in batches to avoid rate limits
    const batches = this.createBatches(messages, this.config.maxRecipientsPerBatch);

    for (let i = 0; i < batches.length; i++) {
      const batch = batches[i];
      if (!batch) continue;
      
      console.log(`Processing batch ${i + 1}/${batches.length} with ${batch.length} messages`);

      // Process batch with delay between batches
      const batchResults = await Promise.allSettled(
        batch.map(message => this.deliverSingleMessage(message))
      );

      // Process batch results
      for (let j = 0; j < batchResults.length; j++) {
        const result = batchResults[j];
        const message = batch[j];

        if (result && message) {
          if (result.status === 'fulfilled' && result.value.success) {
            successfulDeliveries++;
            message.deliveryStatus = 'sent';
            message.sentAt = new Date();
            
            // Update user's last notification sent time
            await subscriptionService.updateLastNotificationSent(message.recipientUserId);
            
          } else {
            failedDeliveries++;
            message.deliveryStatus = 'failed';
            
            const error = result.status === 'rejected' ? result.reason : 
                         (result.status === 'fulfilled' ? result.value.error : 'Unknown error');
            message.errorMessage = error instanceof Error ? error.message : String(error);

            // Categorize delivery failure
            const failureInfo = this.categorizeDeliveryFailure(message.recipientUserId, error);
            deliveryFailures.push(failureInfo);
          }
        }
      }

      // Add delay between batches to respect rate limits
      if (i < batches.length - 1) {
        await this.delay(1000); // 1 second delay between batches
      }
    }

    return {
      totalRecipients: messages.length,
      successfulDeliveries,
      failedDeliveries,
      deliveryFailures,
      processingTime: 0 // Will be set by caller
    };
  }

  /**
   * Deliver a single notification message to a user
   * @param message Notification message to deliver
   * @returns Promise<{success: boolean, error?: any}> Delivery result
   */
  private async deliverSingleMessage(message: NotificationMessage): Promise<{success: boolean, error?: any}> {
    try {
      const lineMessages: line.Message[] = [];

      // Add text message
      if (message.content.text) {
        const textMessage: line.TextMessage = {
          type: 'text',
          text: message.content.text
        };

        if (message.content.quickReply) {
          textMessage.quickReply = message.content.quickReply;
        }

        lineMessages.push(textMessage);
      }

      // Add flex message if available
      if (message.content.flexMessage && this.config.enableRichMessages) {
        lineMessages.push(message.content.flexMessage);
      }

      // Send message via LINE API
      await this.client.pushMessage({
        to: message.recipientUserId,
        messages: lineMessages
      });

      return { success: true };

    } catch (error) {
      console.error(`Failed to deliver message to ${message.recipientUserId}:`, error);
      return { success: false, error };
    }
  }

  /**
   * Filter books based on user preferences and limits
   * @param books Array of all processed books
   * @param user User subscription with preferences
   * @returns BookSummary[] Filtered books for the user
   */
  private filterBooksForUser(books: BookSummary[], user: UserSubscription): BookSummary[] {
    // Apply user's max books per notification limit
    const maxBooks = Math.min(
      user.notificationPreferences.maxBooksPerNotification,
      this.config.maxBooksPerMessage
    );

    // For now, return all successfully processed books up to the limit
    // Future enhancement: could add filtering by user interests, reading history, etc.
    return books
      .filter(book => book.processingSuccess)
      .slice(0, maxBooks);
  }

  /**
   * Create message content based on books and user preferences
   * @param books Array of books to include in message
   * @param user User subscription with preferences
   * @param messageType Type of message to create
   * @returns MessageContent Formatted message content
   */
  private createMessageContent(
    books: BookSummary[], 
    user: UserSubscription, 
    messageType: 'single_book' | 'multiple_books' | 'daily_summary'
  ): any {
    return messageTemplateService.createNotificationContent(books, user, messageType);
  }

  /**
   * Validate the structure of processed book data
   * @param data Parsed book data to validate
   * @returns boolean True if data structure is valid
   */
  private validateBookData(data: any): data is ProcessedBookData {
    return (
      data &&
      typeof data.processingDate === 'string' &&
      typeof data.totalBooksFound === 'number' &&
      Array.isArray(data.successfullyProcessed) &&
      data.processingStats &&
      typeof data.processingStats.booksProcessed === 'number'
    );
  }

  /**
   * Create batches of messages for rate-limited delivery
   * @param messages Array of messages to batch
   * @param batchSize Maximum size of each batch
   * @returns NotificationMessage[][] Array of message batches
   */
  private createBatches<T>(items: T[], batchSize: number): T[][] {
    const batches: T[][] = [];
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize));
    }
    return batches;
  }

  /**
   * Categorize delivery failure for proper error handling
   * @param userId LINE user ID that failed
   * @param error Error that occurred during delivery
   * @returns DeliveryFailureInfo Categorized failure information
   */
  private categorizeDeliveryFailure(userId: string, error: any): DeliveryFailureInfo {
    // Use the error recovery service for consistent error categorization
    return errorRecoveryService.categorizeDeliveryError(userId, error);
  }

  /**
   * Log notification processing results to database
   * @param bookData Original processed book data
   * @param deliveryResult Delivery statistics
   * @returns Promise<void>
   */
  private async logNotificationResults(
    bookData: ProcessedBookData, 
    deliveryResult: DeliveryResult
  ): Promise<void> {
    try {
      // Create notification log entry
      const logId = await subscriptionService.createNotificationLog({
        processingDate: new Date(bookData.processingDate),
        totalRecipients: deliveryResult.totalRecipients,
        successfulDeliveries: deliveryResult.successfulDeliveries,
        failedDeliveries: deliveryResult.failedDeliveries,
        booksProcessed: bookData.successfullyProcessed.length,
        processingDurationSeconds: Math.round(deliveryResult.processingTime / 1000)
      });

      // Record individual delivery failures
      for (const failure of deliveryResult.deliveryFailures) {
        await subscriptionService.recordDeliveryFailure({
          notificationLogId: logId,
          lineUserId: failure.userId,
          errorType: failure.errorType as DeliveryErrorType,
          errorMessage: failure.errorMessage,
          isRetryable: failure.retryable
        });
      }

      console.log(`Notification results logged with ID: ${logId}`);

    } catch (error) {
      console.error('Error logging notification results:', error);
      // Don't throw error here as notification delivery was successful
    }
  }

  /**
   * Process retry attempts for failed deliveries
   * @returns Promise<{processed: number, successful: number, failed: number}> Retry processing results
   */
  async processRetryAttempts(): Promise<{
    processed: number;
    successful: number;
    failed: number;
  }> {
    try {
      console.log('Starting retry processing for failed notification deliveries...');
      return await errorRecoveryService.processRetryableFailures();
    } catch (error) {
      console.error('Error processing retry attempts:', error);
      throw new Error(`Failed to process retry attempts: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get retry statistics for monitoring
   * @returns Promise<any> Retry statistics
   */
  async getRetryStatistics(): Promise<any> {
    try {
      return await errorRecoveryService.getRetryStatistics();
    } catch (error) {
      console.error('Error getting retry statistics:', error);
      throw new Error(`Failed to get retry statistics: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Utility function to add delay between operations
   * @param ms Milliseconds to delay
   * @returns Promise<void>
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Create singleton instance
export const notificationService = new NotificationService();