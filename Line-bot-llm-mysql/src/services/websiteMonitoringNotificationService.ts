import { messagingApi } from '@line/bot-sdk';
import { config } from '../config';
import { subscriptionService } from './subscriptionService';
import { NotificationType } from '../types/subscription';
import {
  flexMessageService,
  BookNotification,
  NewsNotification,
  CancellationNotification
} from './flexMessageService';

/**
 * 影音通知介面
 */
export interface VideoNotification {
  title: string;
  instructor?: string;
  episodeCount?: number;
  url?: string;
}

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
  contentType?: string; // 'news', 'cancellation', 'new_books', 'videos'
  metadata?: {
    itemCount?: number;
    priority?: 'high' | 'medium' | 'low';
  };
  // 新增結構化資料支援 (包含影音)
  structuredData?: {
    newBooks?: BookNotification[];
    news?: NewsNotification[];
    cancellations?: CancellationNotification[];
    videos?: VideoNotification[];
  };
}

/**
 * Mapping from Python content types to our notification types
 */
export const NotificationTypeMapping: Record<string, NotificationType> = {
  'news': 'news',
  'cancellation': 'cancellation',
  'carousel': 'new_books', // 輪播圖通常是新書相關
  'media': 'news', // 媒體報導歸類為新聞
  'videos': 'videos', // 影音通知
  'new_videos': 'videos' // Python 端使用的 key
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
   * 支援整合通知：如果用戶訂閱多種類型，整合成一則 Flex Carousel 訊息
   */
  async handleNotification(notification: WebsiteMonitoringNotification): Promise<{
    success: boolean;
    messagesSent: number;
    error?: string;
  }> {
    try {
      console.log(`📢 Processing website monitoring notification (type: ${notification.type})`);

      // 如果有結構化資料，使用整合通知模式
      if (notification.structuredData) {
        return await this.handleIntegratedNotification(notification);
      }

      // 傳統模式：單一類型通知
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

      // 格式化訊息（文字模式）
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
   * 處理整合通知
   * 根據用戶訂閱的類型，智能整合訊息
   */
  private async handleIntegratedNotification(notification: WebsiteMonitoringNotification): Promise<{
    success: boolean;
    messagesSent: number;
    error?: string;
  }> {
    try {
      console.log('📢 Processing integrated notification with structured data');

      const { structuredData } = notification;
      if (!structuredData) {
        throw new Error('Structured data is required for integrated notification');
      }

      // 取得所有訂閱用戶
      const allUsers = await subscriptionService.getSubscribedUsers();

      if (allUsers.length === 0) {
        console.log('ℹ️ No subscribed users found');
        return {
          success: true,
          messagesSent: 0,
        };
      }

      let successCount = 0;
      let failCount = 0;

      // 為每個用戶根據其訂閱類型創建個性化訊息
      for (const user of allUsers) {
        try {
          const userNotificationTypes = user.notificationTypes;

          // 根據用戶訂閱類型過濾資料
          const filteredData: {
            newBooks?: BookNotification[];
            news?: NewsNotification[];
            cancellations?: CancellationNotification[];
            videos?: VideoNotification[];
          } = {};

          if (userNotificationTypes.includes('new_books') && structuredData.newBooks) {
            filteredData.newBooks = structuredData.newBooks;
          }
          if (userNotificationTypes.includes('news') && structuredData.news) {
            filteredData.news = structuredData.news;
          }
          if (userNotificationTypes.includes('cancellation') && structuredData.cancellations) {
            filteredData.cancellations = structuredData.cancellations;
          }
          if (userNotificationTypes.includes('videos') && structuredData.videos) {
            filteredData.videos = structuredData.videos;
          }

          // 如果用戶沒有訂閱任何有資料的類型，跳過
          const hasData = Object.keys(filteredData).length > 0;
          if (!hasData) {
            console.log(`ℹ️ User ${user.lineUserId} has no matching subscriptions, skipping`);
            continue;
          }

          // 創建訊息
          let message;
          const subscribedTypesCount = Object.keys(filteredData).length;

          if (subscribedTypesCount === 1) {
            // 單一類型：使用專用 Carousel
            if (filteredData.newBooks) {
              message = flexMessageService.createNewBooksCarousel(filteredData.newBooks);
            } else if (filteredData.news) {
              message = flexMessageService.createNewsCarousel(filteredData.news);
            } else if (filteredData.cancellations) {
              message = flexMessageService.createCancellationCarousel(filteredData.cancellations);
            } else if (filteredData.videos) {
              // 影音使用影音 Carousel
              const videoStreams = filteredData.videos.map(v => ({
                title: v.title,
                instructor: v.instructor,
                startDate: undefined,
                thumbnailUrl: undefined,
                eventUrl: v.url,
                isLive: false,
                intro: v.episodeCount ? `共 ${v.episodeCount} 集` : undefined
              }));
              message = flexMessageService.createVideoStreamingCarousel(videoStreams);
            }
          } else {
            // 多種類型：使用簡化通知模板（每個項目可點擊觸發查詢）
            const books = filteredData.newBooks?.filter(b => (b as any).source !== 'buddha_cards') || [];
            const cards = filteredData.newBooks?.filter(b => (b as any).source === 'buddha_cards') || [];

            message = flexMessageService.createSimpleNotification({
              newBooks: books.length,
              buddhaCards: cards.length,
              cancellations: filteredData.cancellations?.length || 0,
              news: filteredData.news?.length || 0,
              videos: filteredData.videos?.length || 0
            });
          }

          if (!message) {
            console.log(`⚠️ Failed to create message for user ${user.lineUserId}`);
            continue;
          }

          // 發送訊息
          await this.client.pushMessage({
            to: user.lineUserId,
            messages: [message],
          });

          successCount++;

          // 更新最後通知時間
          await subscriptionService.updateLastNotificationSent(user.lineUserId);

          console.log(`✅ Sent integrated notification to user ${user.lineUserId} (${subscribedTypesCount} types)`);
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          console.error(`❌ Failed to send to user ${user.lineUserId}:`, errorMessage);
          failCount++;
        }
      }

      console.log(`✅ Integrated notification sent: ${successCount} success, ${failCount} failed`);

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
      console.error('❌ Error handling integrated notification:', errorMessage);
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
