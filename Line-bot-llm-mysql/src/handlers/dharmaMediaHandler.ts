import * as line from '@line/bot-sdk';
import { lineMessagingService } from '../services/lineMessagingService';
import { dharmaBookService } from '../services/dharmaBookService';
import { videoStreamingService } from '../services/videoStreamingService';
import { videoSeriesService } from '../services/videoSeriesService';
import { flexMessageService } from '../services/flexMessageService';
import { buddhaCardService } from '../services/buddhaCardService';

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
      console.log('Fetching latest dharma books and buddha cards...');

      // 並行獲取書籍和佛卡
      const [books, cards] = await Promise.all([
        dharmaBookService.getLatestBooks(5),
        buddhaCardService.getLatestBuddhaCards(5)
      ]);

      if ((!books || books.length === 0) && (!cards || cards.length === 0)) {
        await lineMessagingService.sendTextMessage(replyToken, '目前沒有最新法寶資訊');
        return;
      }

      // 生成書籍 Bubbles
      const bookBubbles = (books || []).map(book => flexMessageService.createBookBubble(book));

      // 生成佛卡 Bubbles
      const cardBubbles = (cards || []).map(card => flexMessageService.createBuddhaCardBubble(card));

      // 合併 Bubbles (書籍在前，佛卡在後)
      const bubbles = [...bookBubbles, ...cardBubbles];

      // 生成 Flex Message Carousel
      const flexMessage: line.FlexMessage = {
        type: 'flex',
        altText: '最新法寶通知',
        contents: {
          type: 'carousel',
          contents: bubbles
        }
      };

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
              label: '✅ 全部訂閱',
              text: '全部訂閱'
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

      console.log(`Successfully sent ${books.length} books and ${cards.length} cards`);
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

      const streams = await videoStreamingService.getLatestContent(5);

      if (!streams || streams.length === 0) {
        await lineMessagingService.sendTextMessage(replyToken, '目前沒有最新影音資訊');
        return;
      }

      // 為每個影片系列並行獲取最新一集連結
      const streamsWithLatestEpisode = await Promise.all(
        streams.map(async (stream) => {
          if (!stream.isLive && stream.seriesId) {
            const latestEpisodeUrl = await videoSeriesService.getLatestEpisode(stream.seriesId);
            return {
              ...stream,
              latestEpisodeUrl
            };
          }
          return stream;
        })
      );

      // 生成 Flex Message Carousel
      const flexMessage = flexMessageService.createVideoStreamingCarousel(streamsWithLatestEpisode.map(stream => ({
        title: stream.title,
        instructor: stream.instructor,
        startDate: stream.startTime,
        thumbnailUrl: stream.thumbnailUrl,
        eventUrl: stream.link,
        isLive: stream.isLive,
        latestEpisodeUrl: stream.latestEpisodeUrl,  // NEW: 傳遞最新一集連結
        intro: stream.intro  // NEW: 傳遞課程介紹
      })));

      // 生成 Quick Reply
      const quickReply: line.QuickReply = {
        items: [
          {
            type: 'action',
            action: {
              type: 'message',
              label: '🎥 訂閱課程通知',
              text: '訂閱影音通知'
            }
          },
          {
            type: 'action',
            action: {
              type: 'message',
              label: '✅ 全部訂閱',
              text: '全部訂閱'
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