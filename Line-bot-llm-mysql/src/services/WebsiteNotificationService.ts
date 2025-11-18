import { NewBookService } from './NewBookService';
// Import types for reference (currently unused but may be needed for future enhancements)
// import { CarouselContent, CourseCancellation, NewsAnnouncement, MediaContent } from '../types/WebsiteMonitoring';

// Interface for notification content items
interface NotificationContentItem {
  id?: string;
  content_type?: string;
  notification_text?: string;
  urgent?: boolean;
  timestamp?: string;
  [key: string]: any;
}

/**
 * Service for handling website monitoring notifications
 * Integrates with NewBookService for LINE message distribution
 */
export class WebsiteNotificationService {
  private newBookService: NewBookService;

  constructor() {
    this.newBookService = new NewBookService();
  }

  /**
   * Process website monitoring notification data and send LINE messages
   * @param notificationData Notification data from Python system
   * @returns Promise<boolean> Success status
   */
  async processWebsiteNotification(notificationData: {
    timestamp: string;
    priority: 'immediate' | 'high' | 'normal' | 'low';
    content_data: { [key: string]: NotificationContentItem[] };
  }): Promise<boolean> {
    try {
      console.log('Processing website monitoring notification:', {
        timestamp: notificationData.timestamp,
        priority: notificationData.priority,
        contentTypes: Object.keys(notificationData.content_data),
        totalItems: Object.values(notificationData.content_data).flat().length
      });

      // Send notification based on priority
      const success = await this.newBookService.sendNotificationByPriority(
        notificationData.content_data,
        notificationData.priority
      );

      if (success) {
        console.log('Website monitoring notification sent successfully');
        
        // Log notification details for audit
        await this.logNotificationActivity(notificationData);
      } else {
        console.error('Failed to send website monitoring notification');
      }

      return success;
    } catch (error) {
      console.error('Error processing website notification:', error);
      return false;
    }
  }

  /**
   * Send immediate alert for urgent content (e.g., course cancellations)
   * @param contentData Urgent content data
   * @returns Promise<boolean> Success status
   */
  async sendImmediateAlert(contentData: { [key: string]: NotificationContentItem[] }): Promise<boolean> {
    try {
      // Filter for immediate priority content only
      const immediateContent: { [key: string]: NotificationContentItem[] } = {};
      
      Object.entries(contentData).forEach(([type, items]) => {
        if (this.isImmediatePriority(type)) {
          immediateContent[type] = items;
        }
      });

      if (Object.keys(immediateContent).length === 0) {
        console.log('No immediate priority content to alert');
        return true;
      }

      return await this.newBookService.sendNotificationByPriority(immediateContent, 'immediate');
    } catch (error) {
      console.error('Error sending immediate alert:', error);
      return false;
    }
  }

  /**
   * Send daily summary notification for regular content
   * @param contentData Regular content data
   * @returns Promise<boolean> Success status
   */
  async sendDailySummary(contentData: { [key: string]: NotificationContentItem[] }): Promise<boolean> {
    try {
      // Filter for normal priority content only
      const regularContent: { [key: string]: NotificationContentItem[] } = {};
      
      Object.entries(contentData).forEach(([type, items]) => {
        if (!this.isImmediatePriority(type)) {
          regularContent[type] = items;
        }
      });

      if (Object.keys(regularContent).length === 0) {
        console.log('No regular content for daily summary');
        return true;
      }

      return await this.newBookService.sendNotificationByPriority(regularContent, 'normal');
    } catch (error) {
      console.error('Error sending daily summary:', error);
      return false;
    }
  }

  /**
   * Check if content type requires immediate priority
   * @private
   */
  private isImmediatePriority(contentType: string): boolean {
    const immediatePriorityTypes = ['cancellation'];
    return immediatePriorityTypes.includes(contentType);
  }

  /**
   * Log notification activity for audit purposes
   * @private
   */
  private async logNotificationActivity(notificationData: {
    timestamp: string;
    priority: string;
    content_data: { [key: string]: NotificationContentItem[] };
  }): Promise<void> {
    try {
      const logEntry = {
        timestamp: new Date().toISOString(),
        source_timestamp: notificationData.timestamp,
        priority: notificationData.priority,
        content_summary: Object.entries(notificationData.content_data).map(([type, items]) => ({
          type,
          count: items.length,
          items: items.map(item => ({
            id: item.id,
            notification_text: item.notification_text
          }))
        }))
      };

      console.log('Notification activity logged:', JSON.stringify(logEntry, null, 2));
      
      // Here you could save to database or file for audit trail
      // await this.saveNotificationLog(logEntry);
      
    } catch (error) {
      console.error('Error logging notification activity:', error);
    }
  }

  /**
   * Test notification functionality
   * @returns Promise<boolean> Test success status
   */
  async testNotification(): Promise<boolean> {
    try {
      const testData = {
        timestamp: new Date().toISOString(),
        priority: 'normal' as const,
        content_data: {
          test: [{
            id: 'test_001',
            content_type: 'test',
            notification_text: '系統測試通知 - LINE Bot 整合測試',
            urgent: false,
            timestamp: new Date().toISOString()
          }]
        }
      };

      return await this.processWebsiteNotification(testData);
    } catch (error) {
      console.error('Error testing notification:', error);
      return false;
    }
  }

  /**
   * Get notification statistics
   * @returns Promise<object> Notification statistics
   */
  async getNotificationStats(): Promise<{
    total_sent: number;
    by_priority: { [key: string]: number };
    by_content_type: { [key: string]: number };
    last_notification: string | null;
  }> {
    try {
      // This would typically query a database for actual statistics
      // For now, return mock data structure
      return {
        total_sent: 0,
        by_priority: {
          immediate: 0,
          high: 0,
          normal: 0,
          low: 0
        },
        by_content_type: {
          carousel: 0,
          cancellation: 0,
          news: 0,
          media: 0
        },
        last_notification: null
      };
    } catch (error) {
      console.error('Error getting notification stats:', error);
      throw new Error('Failed to get notification statistics');
    }
  }

  /**
   * Close service connections
   * @returns Promise<void>
   */
  async close(): Promise<void> {
    try {
      await this.newBookService.closeConnection();
      console.log('WebsiteNotificationService closed successfully');
    } catch (error) {
      console.error('Error closing WebsiteNotificationService:', error);
      throw error;
    }
  }
}

// CLI interface for Python integration
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('Usage: node WebsiteNotificationService.js <notification_data_file>');
    process.exit(1);
  }

  const notificationDataFile = args[0];
  
  (async () => {
    const service = new WebsiteNotificationService();
    
    try {
      // Read notification data from file
      const fs = require('fs').promises;
      const notificationDataRaw = await fs.readFile(notificationDataFile, 'utf-8');
      const notificationData = JSON.parse(notificationDataRaw);
      
      // Process notification
      const success = await service.processWebsiteNotification(notificationData);
      
      if (success) {
        console.log('Notification processed successfully');
        process.exit(0);
      } else {
        console.error('Failed to process notification');
        process.exit(1);
      }
    } catch (error) {
      console.error('Error:', error);
      process.exit(1);
    } finally {
      await service.close();
    }
  })();
}

// Export is handled by the class declaration above