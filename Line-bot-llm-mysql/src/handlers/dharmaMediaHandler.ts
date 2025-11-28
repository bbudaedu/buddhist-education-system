import * as line from '@line/bot-sdk';
import { lineMessagingService } from '../services/lineMessagingService';
import { dharmaBookService } from '../services/dharmaBookService';
import { videoStreamingService } from '../services/videoStreamingService';
import { flexMessageService } from '../services/flexMessageService';

/**
 * Dharma Media Command Handlers
 * 處理「最新法寶」和「最新影音」指令
 */
export class DharmaMediaHandler {
  /**
   * 處理「最新法寶」指令
   * @param replyToken 回覆 token
   */
  async handleLatestBooksCommand(replyToken: string): Promise<void> {
    try {
      console.log('Fetching latest dharma books...');

      const books = await dharmaBookService.getLatestBooks(5);

      if (!books || books.length === 0) {
        await lineMessagingService.sendTextMessage(replyToken, '目前沒有最新法寶資訊');
        return;
      }

      // 生成 Flex Message Carousel
      const flexMessage = flexMessageService.createDharmaBookCarousel(books);

      // 生成 Quick Reply
      const quickReply: line.QuickReply = {
        items: [
          {
            type: 'action',
            action: {
              type: 'message',
              label: '📚 訂閱新書通知',
              text: '訂閱新書通知'
            }
          },
          {
            type: 'action',
            action: {
              type: 'message',
              label: '📊 訂閱狀態查詢',
              text: '訂閱狀態查詢'
            }
          },
          {
            type: 'action',
            action: {
              type: 'message',
              label: '🚫 取消訂閱',
              text: '取消訂閱'
            }
          }
        ]
      };

      await lineMessagingService.replyMessage(replyToken, [{
        ...flexMessage,
        quickReply
      }]);

      console.log(`Successfully sent ${books.length} dharma books`);
    } catch (error) {
      console.error('Error handling latest books command:', error);
      await lineMessagingService.sendErrorMessage(replyToken, '無法取得最新法寶資訊，請稍後再試');
    }
  }

  /**
   * 處理「最新影音」指令
   * @param replyToken 回覆 token
   */
  async handleLatestVideosCommand(replyToken: string): Promise<void> {
    try {
      console.log('Fetching latest videos and live streams...');

      const streams = await videoStreamingService.getLatestContent(10);

      if (!streams || streams.length === 0) {
        await lineMessagingService.sendTextMessage(replyToken, '目前沒有最新影音資訊');
        return;
      }

      // 生成 Flex Message Carousel
      const flexMessage = flexMessageService.createVideoStreamingCarousel(streams.map(stream => ({
        title: stream.title,
        instructor: stream.instructor,
        startDate: stream.startTime,
        thumbnailUrl: stream.thumbnailUrl,
        eventUrl: stream.link,
        isLive: stream.isLive
      })));

      // 生成 Quick Reply
      const quickReply: line.QuickReply = {
        items: [
          {
            type: 'action',
            action: {
              type: 'message',
              label: '🎥 訂閱影音通知',
              text: '訂閱影音通知'
            }
          },
          {
            type: 'action',
            action: {
              type: 'message',
              label: '📊 訂閱狀態查詢',
              text: '訂閱狀態查詢'
            }
          },
          {
            type: 'action',
            action: {
              type: 'message',
              label: '🚫 取消訂閱',
              text: '取消訂閱'
            }
          }
        ]
      };

      await lineMessagingService.replyMessage(replyToken, [{
        ...flexMessage,
        quickReply
      }]);

      console.log(`Successfully sent ${streams.length} streams`);
    } catch (error) {
      console.error('Error handling latest videos command:', error);
      await lineMessagingService.sendErrorMessage(replyToken, '無法取得最新影音資訊，請稍後再試');
    }
  }
}

export const dharmaMediaHandler = new DharmaMediaHandler();