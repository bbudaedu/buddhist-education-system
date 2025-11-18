import { messagingApi } from '@line/bot-sdk';
import { config } from '../config';
import { subscriptionService } from './subscriptionService';
import { NotificationType } from '../types/subscription';

/**
 * Website Monitoring Notification Service
 * 網站監控通知服務
 * 
 * 接收來自 Python 網站監控系統的通知，並透過 LINE 發送給訂閱用戶
 */

export interface WebsiteMonitoringNotification {
  type: 'broadcast' | 'alert' | 'summary';
  message: string;
  timestamp: string;
  contentType?: string; // 'news', 'cancellation', 'new_books'
  metadata?: {
    itemCount?: number;
    priority?: 'high' | 'medium' | 'low';
  };
}

/**
 * Mapping from Python content types to our notification types
 */
export const NotificationTypeMapping: Record<string, NotificationType> = {
  'news': 'news',
  'cancellation': 'cancellation',
  'carousel': 'new_books', // 輪播圖通常是新書相關
  'media': 'news' // 媒體報導歸類為新聞
};

export class WebsiteMonitoringNotificationService {
  private client: messagingApi.MessagingApiClient;

  constructor() {
    this.client = new messagingApi.MessagingApiClient({
      channelAccessToken: config.line.channelAccessToken,
    });
  }

  /**
   * 處理來自 Python 的網站監控通知
   */
  async handleNotification(notification: WebsiteMonitoringNotification): Promise<{
    success: boolean;
    messagesSent: number;
    error?: string;
  }> {
    try {
      console.log(`📢 Processing website monitoring notification (type: ${notification.type})`);

      // 確定通知類型（支援兩種格式：直接在根層級或在 metadata 中，用於向後相容）
      const contentType = notification.contentType || 
                         (notification.metadata as any)?.contentType || 
                         'news';
      const notificationType = NotificationTypeMapping[contentType] || 'news';
      
      console.log(`📋 Content type: ${contentType}, Notification type: ${notificationType}`);

      // 取得訂閱該類型通知的用戶
      const subscribedUsers = await subscriptionService.getSubscribedUsers(notificationType);
      
      if (subscribedUsers.length === 0) {
        console.log(`ℹ️ No users subscribed to ${notificationType} notifications`);
        return {
          success: true,
          messagesSent: 0,
        };
      }

      console.log(`📤 Sending to ${subscribedUsers.length} subscribed users`);

      // 格式化訊息
      const formattedMessage = this.formatNotificationMessage(notification);

      // 發送給每個訂閱用戶
      let successCount = 0;
      let failCount = 0;

      for (const user of subscribedUsers) {
        try {
          await this.client.pushMessage({
            to: user.lineUserId,
            messages: [
              {
                type: 'text',
                text: formattedMessage,
              },
            ],
          });
          successCount++;
          
          // 更新最後通知時間
          await subscriptionService.updateLastNotificationSent(user.lineUserId);
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          console.error(`❌ Failed to send to user ${user.lineUserId}:`, errorMessage);
          failCount++;
        }
      }

      console.log(`✅ Notification sent: ${successCount} success, ${failCount} failed`);

      const result: { success: boolean; messagesSent: number; error?: string } = {
        success: failCount === 0,
        messagesSent: successCount,
      };

      if (failCount > 0) {
        result.error = `${failCount} messages failed to send`;
      }

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Error handling website monitoring notification:', errorMessage);
      return {
        success: false,
        messagesSent: 0,
        error: errorMessage,
      };
    }
  }

  /**
   * 格式化通知訊息
   */
  private formatNotificationMessage(notification: WebsiteMonitoringNotification): string {
    const { message } = notification;

    // 直接返回訊息內容，不添加額外的標題、時間戳或提示
    return message;
  }



  /**
   * 發送測試通知
   */
  async sendTestNotification(userId: string): Promise<boolean> {
    try {
      const testNotification: WebsiteMonitoringNotification = {
        type: 'broadcast',
        message: '這是一則測試通知\n\n網站監控系統運作正常 ✅',
        timestamp: new Date().toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' }),
        contentType: 'news',
        metadata: {
          itemCount: 1,
          priority: 'low',
        },
      };

      const formattedMessage = this.formatNotificationMessage(testNotification);

      await this.client.pushMessage({
        to: userId,
        messages: [
          {
            type: 'text',
            text: formattedMessage,
          },
        ],
      });

      console.log(`✅ Test notification sent to user ${userId}`);
      return true;
    } catch (error) {
      console.error('❌ Error sending test notification:', error);
      return false;
    }
  }

  /**
   * 訂閱/取消訂閱網站監控通知
   */
  async toggleSubscription(userId: string, subscribe: boolean): Promise<boolean> {
    try {
      // 這裡可以實作訂閱管理邏輯
      // 例如在資料庫中記錄用戶的訂閱偏好
      console.log(`${subscribe ? '訂閱' : '取消訂閱'} 網站監控通知: ${userId}`);
      return true;
    } catch (error) {
      console.error('❌ Error toggling subscription:', error);
      return false;
    }
  }
}
