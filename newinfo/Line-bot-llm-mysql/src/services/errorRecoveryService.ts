import { subscriptionService } from './subscriptionService';
import { DeliveryFailure, DeliveryErrorType } from '../types/subscription';
import { NotificationMessage, DeliveryFailureInfo } from '../types/notification';

/**
 * Service for handling error recovery and retry mechanisms for notification delivery
 */
export class ErrorRecoveryService {
  private readonly maxRetryAttempts: number;
  private readonly baseRetryDelayMs: number;
  private readonly maxRetryDelayMs: number;
  private readonly retryMultiplier: number;

  constructor(config?: {
    maxRetryAttempts?: number;
    baseRetryDelayMs?: number;
    maxRetryDelayMs?: number;
    retryMultiplier?: number;
  }) {
    this.maxRetryAttempts = config?.maxRetryAttempts ?? 3;
    this.baseRetryDelayMs = config?.baseRetryDelayMs ?? 1000; // 1 second
    this.maxRetryDelayMs = config?.maxRetryDelayMs ?? 300000; // 5 minutes
    this.retryMultiplier = config?.retryMultiplier ?? 2;
  }

  /**
   * Process all retryable delivery failures with exponential backoff
   * @returns Promise<{processed: number, successful: number, failed: number}> Retry processing results
   */
  async processRetryableFailures(): Promise<{
    processed: number;
    successful: number;
    failed: number;
  }> {
    try {
      console.log('Starting retry processing for failed deliveries...');
      
      // Get all retryable failures
      const retryableFailures = await subscriptionService.getRetryableFailures(this.maxRetryAttempts);
      
      if (retryableFailures.length === 0) {
        console.log('No retryable failures found');
        return { processed: 0, successful: 0, failed: 0 };
      }

      console.log(`Found ${retryableFailures.length} retryable failures to process`);

      let successful = 0;
      let failed = 0;

      // Process each failure with appropriate retry logic
      for (const failure of retryableFailures) {
        try {
          const retryResult = await this.retryDeliveryFailure(failure);
          
          if (retryResult.success) {
            successful++;
            console.log(`Successfully retried delivery for user ${failure.lineUserId}`);
          } else {
            failed++;
            await this.handleRetryFailure(failure, retryResult.error);
          }

          // Add delay between retries to avoid overwhelming the API
          await this.delay(500);

        } catch (error) {
          failed++;
          console.error(`Error processing retry for failure ${failure.id}:`, error);
          await this.handleRetryFailure(failure, error);
        }
      }

      console.log(`Retry processing completed: ${successful} successful, ${failed} failed`);
      return {
        processed: retryableFailures.length,
        successful,
        failed
      };

    } catch (error) {
      console.error('Error in processRetryableFailures:', error);
      throw new Error(`Failed to process retryable failures: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Retry a specific delivery failure with exponential backoff
   * @param failure The delivery failure to retry
   * @returns Promise<{success: boolean, error?: any}> Retry result
   */
  async retryDeliveryFailure(failure: DeliveryFailure): Promise<{
    success: boolean;
    error?: any;
  }> {
    try {
      // Calculate retry delay with exponential backoff
      const retryDelay = this.calculateRetryDelay(failure.retryCount);
      
      console.log(`Retrying delivery for user ${failure.lineUserId} (attempt ${failure.retryCount + 1}/${this.maxRetryAttempts}) after ${retryDelay}ms delay`);
      
      // Wait for the calculated delay
      await this.delay(retryDelay);

      // Check if user is still subscribed before retrying
      const isSubscribed = await subscriptionService.isUserSubscribed(failure.lineUserId);
      if (!isSubscribed) {
        console.log(`User ${failure.lineUserId} is no longer subscribed, skipping retry`);
        return { success: false, error: 'User no longer subscribed' };
      }

      // Create a simple notification message for retry
      const retryMessage = await this.createRetryMessage(failure);
      
      // Attempt to deliver the message
      const deliveryResult = await this.attemptMessageDelivery(retryMessage);
      
      if (deliveryResult.success) {
        // Update user's last notification sent time
        await subscriptionService.updateLastNotificationSent(failure.lineUserId);
        return { success: true };
      } else {
        return { success: false, error: deliveryResult.error };
      }

    } catch (error) {
      console.error(`Error retrying delivery failure ${failure.id}:`, error);
      return { success: false, error };
    }
  }

  /**
   * Handle a failed retry attempt
   * @param failure The original delivery failure
   * @param retryError The error that occurred during retry
   * @returns Promise<void>
   */
  async handleRetryFailure(failure: DeliveryFailure, retryError: any): Promise<void> {
    try {
      // Increment retry count
      await subscriptionService.incrementRetryCount(failure.id);

      // Check if we've exceeded max retry attempts
      if (failure.retryCount + 1 >= this.maxRetryAttempts) {
        console.log(`Max retry attempts reached for user ${failure.lineUserId}, marking as inactive`);
        
        // Determine if user should be marked as inactive
        const shouldMarkInactive = this.shouldMarkUserInactive(failure.errorType, retryError);
        
        if (shouldMarkInactive) {
          const reason = this.getInactiveReason(failure.errorType, retryError);
          await subscriptionService.markUserInactive(failure.lineUserId, reason);
        }
      }

      // Log the retry failure for monitoring
      console.error(`Retry failed for user ${failure.lineUserId} (attempt ${failure.retryCount + 1}):`, retryError);

    } catch (error) {
      console.error('Error handling retry failure:', error);
    }
  }

  /**
   * Determine if a user should be marked as inactive based on error type
   * @param errorType The type of delivery error
   * @param error The specific error that occurred
   * @returns boolean Whether the user should be marked inactive
   */
  private shouldMarkUserInactive(errorType: DeliveryErrorType, error: any): boolean {
    switch (errorType) {
      case DeliveryErrorType.USER_BLOCKED:
      case DeliveryErrorType.INVALID_USER:
        return true; // These are permanent failures
      
      case DeliveryErrorType.RATE_LIMIT:
        return false; // Rate limits are temporary
      
      case DeliveryErrorType.API_ERROR:
        // Check if it's a permanent API error
        if (error && typeof error === 'object') {
          const errorMessage = error.message || error.toString();
          return errorMessage.includes('user not found') || 
                 errorMessage.includes('invalid user') ||
                 errorMessage.includes('blocked');
        }
        return false;
      
      default:
        return false;
    }
  }

  /**
   * Get the reason for marking a user as inactive
   * @param errorType The type of delivery error
   * @param error The specific error that occurred
   * @returns string Reason for marking user inactive
   */
  private getInactiveReason(errorType: DeliveryErrorType, error: any): string {
    switch (errorType) {
      case DeliveryErrorType.USER_BLOCKED:
        return 'User has blocked the bot';
      
      case DeliveryErrorType.INVALID_USER:
        return 'Invalid or deleted LINE user account';
      
      case DeliveryErrorType.API_ERROR:
        if (error && typeof error === 'object') {
          const errorMessage = error.message || error.toString();
          if (errorMessage.includes('user not found')) {
            return 'LINE user account not found';
          }
          if (errorMessage.includes('blocked')) {
            return 'User has blocked the bot';
          }
        }
        return 'Persistent API error after multiple retries';
      
      default:
        return 'Multiple delivery failures after retry attempts';
    }
  }

  /**
   * Calculate retry delay with exponential backoff
   * @param retryCount Current retry count (0-based)
   * @returns number Delay in milliseconds
   */
  private calculateRetryDelay(retryCount: number): number {
    const delay = this.baseRetryDelayMs * Math.pow(this.retryMultiplier, retryCount);
    return Math.min(delay, this.maxRetryDelayMs);
  }

  /**
   * Create a simple retry message for failed delivery
   * @param failure The delivery failure to create a retry message for
   * @returns Promise<NotificationMessage> Retry notification message
   */
  private async createRetryMessage(failure: DeliveryFailure): Promise<NotificationMessage> {
    // Create a simple text message for retry attempts
    const retryMessage: NotificationMessage = {
      id: `retry-${failure.id}-${Date.now()}`,
      recipientUserId: failure.lineUserId,
      messageType: 'daily_summary',
      content: {
        text: '📚 您好！我們有新的佛教教育書籍資訊要與您分享。\n\n由於之前的發送遇到問題，我們重新為您發送通知。如果您不希望收到這些通知，請回覆「取消訂閱」。'
      },
      deliveryStatus: 'pending',
      createdAt: new Date()
    };

    return retryMessage;
  }

  /**
   * Attempt to deliver a single message with error handling
   * @param message The message to deliver
   * @returns Promise<{success: boolean, error?: any}> Delivery result
   */
  private async attemptMessageDelivery(message: NotificationMessage): Promise<{
    success: boolean;
    error?: any;
  }> {
    try {
      // Create a simple delivery using LINE client directly
      const line = require('@line/bot-sdk');
      const { lineConfig } = require('../config/index');
      
      const client = new line.messagingApi.MessagingApiClient({
        channelAccessToken: lineConfig.channelAccessToken
      });

      const lineMessages: any[] = [{
        type: 'text',
        text: message.content.text
      }];

      await client.pushMessage({
        to: message.recipientUserId,
        messages: lineMessages
      });

      return { success: true };

    } catch (error) {
      console.error(`Failed to deliver retry message to ${message.recipientUserId}:`, error);
      return { success: false, error };
    }
  }

  /**
   * Categorize a delivery error for proper handling
   * @param error The error that occurred during delivery
   * @returns DeliveryFailureInfo Categorized error information
   */
  categorizeDeliveryError(userId: string, error: any): DeliveryFailureInfo {
    let errorType: 'user_blocked' | 'invalid_user' | 'rate_limit' | 'api_error' = 'api_error';
    let retryable = true;

    if (error && typeof error === 'object') {
      const errorMessage = error.message || error.toString();
      
      if (errorMessage.includes('user not found') || errorMessage.includes('invalid user')) {
        errorType = 'invalid_user';
        retryable = false;
      } else if (errorMessage.includes('blocked') || errorMessage.includes('user has blocked')) {
        errorType = 'user_blocked';
        retryable = false;
      } else if (errorMessage.includes('rate limit') || errorMessage.includes('too many requests')) {
        errorType = 'rate_limit';
        retryable = true;
      } else if (errorMessage.includes('400') || errorMessage.includes('401') || errorMessage.includes('403')) {
        // Client errors are usually not retryable
        retryable = false;
      } else if (errorMessage.includes('500') || errorMessage.includes('502') || errorMessage.includes('503')) {
        // Server errors are usually retryable
        retryable = true;
      }
    }

    return {
      userId,
      errorType,
      errorMessage: error instanceof Error ? error.message : String(error),
      retryable
    };
  }

  /**
   * Utility function to add delay between operations
   * @param ms Milliseconds to delay
   * @returns Promise<void>
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get retry statistics for monitoring
   * @returns Promise<RetryStatistics> Current retry statistics
   */
  async getRetryStatistics(): Promise<RetryStatistics> {
    try {
      const retryableFailures = await subscriptionService.getRetryableFailures(this.maxRetryAttempts);
      const deliveryMetrics = await subscriptionService.getDeliveryMetrics();

      return {
        pendingRetries: retryableFailures.length,
        totalFailures: deliveryMetrics.failedDeliveries,
        retrySuccessRate: this.calculateRetrySuccessRate(deliveryMetrics),
        errorBreakdown: deliveryMetrics.errorBreakdown
      };
    } catch (error) {
      console.error('Error getting retry statistics:', error);
      throw new Error('Failed to get retry statistics');
    }
  }

  /**
   * Calculate retry success rate from delivery metrics
   * @param metrics Delivery metrics
   * @returns number Retry success rate as percentage
   */
  private calculateRetrySuccessRate(metrics: any): number {
    const totalRetryableErrors = metrics.errorBreakdown
      .filter((error: any) => error.retryableCount > 0)
      .reduce((sum: number, error: any) => sum + error.retryableCount, 0);

    if (totalRetryableErrors === 0) return 100;

    // This is a simplified calculation - in a real implementation,
    // you'd track actual retry success rates
    return Math.max(0, 100 - (totalRetryableErrors / metrics.totalRecipients) * 100);
  }
}

/**
 * Retry statistics for monitoring and analysis
 */
export interface RetryStatistics {
  pendingRetries: number;
  totalFailures: number;
  retrySuccessRate: number;
  errorBreakdown: any[];
}

// Create singleton instance
export const errorRecoveryService = new ErrorRecoveryService();