import express from 'express';
import * as line from '@line/bot-sdk';
import { lineConfig } from '../config/index';
import { geminiService } from '../services/geminiService';
import { lineMessagingService } from '../services/lineMessagingService';
import { subscriptionService } from '../services/subscriptionService';
import { bulletinService } from '../services/bulletinService';
import { ErrorHandler, ErrorContext } from './errorHandler';

/**
 * Webhook Handler for LINE Bot
 * 負責接收並處理來自 LINE 平台的 Webhook 事件
 */
export class WebhookHandler {
  constructor() {
    // Webhook handler 初始化完成
  }

  /**
   * Express 路由處理器，接收 POST /webhook 請求
   * @param req Express Request 物件
   * @param res Express Response 物件
   */
  async handleWebhook(req: express.Request, res: express.Response): Promise<void> {
    try {
      // 驗證請求簽章
      const signature = req.get('X-Line-Signature');
      if (!signature || !this.validateSignature(JSON.stringify(req.body), signature)) {
        const errorContext: ErrorContext = {
          operation: 'validateSignature'
        };
        ErrorHandler.log(new Error('Invalid signature'), errorContext);
        res.status(401).send('Unauthorized');
        return;
      }

      // 確保在 3 秒內回應 LINE 平台 HTTP 200
      res.status(200).send('OK');

      // 非同步處理事件，避免阻塞回應
      setImmediate(async () => {
        try {
          const events: line.WebhookEvent[] = req.body.events || [];
          
          // 處理每個事件
          await Promise.all(
            events.map(event => this.processEvent(event))
          );
        } catch (error) {
          const errorContext: ErrorContext = {
            operation: 'processWebhookEvents'
          };
          ErrorHandler.log(error as Error, errorContext);
        }
      });

    } catch (error) {
      const errorContext: ErrorContext = {
        operation: 'handleWebhook'
      };
      ErrorHandler.log(error as Error, errorContext);
      res.status(500).send('Internal Server Error');
    }
  }

  /**
   * 使用 Channel Secret 驗證 X-Line-Signature 標頭
   * @param body 請求主體的 JSON 字串
   * @param signature X-Line-Signature 標頭值
   * @returns 驗證是否成功
   */
  validateSignature(body: string, signature: string): boolean {
    try {
      return line.validateSignature(body, lineConfig.channelSecret, signature);
    } catch (error) {
      console.error('Signature validation error:', error);
      return false;
    }
  }

  /**
   * 處理單個 Webhook 事件
   * @param event LINE Webhook 事件
   */
  private async processEvent(event: line.WebhookEvent): Promise<void> {
    try {
      // 只處理訊息事件
      if (event.type === 'message') {
        await this.processMessage(event);
      } else if (event.type === 'follow') {
        // 處理用戶加入好友事件
        await this.processFollowEvent(event);
      } else {
        console.log(`Unhandled event type: ${event.type}`);
      }
    } catch (error) {
      // 建立錯誤上下文
      const errorContext: ErrorContext = {
        userId: 'source' in event ? event.source?.userId : undefined,
        operation: `processEvent_${event.type}`
      };
      
      // 使用統一錯誤處理
      const friendlyMessage = ErrorHandler.handle(error as Error, errorContext);
      
      // 嘗試發送錯誤訊息給用戶（如果有 replyToken）
      if ('replyToken' in event && event.replyToken) {
        try {
          await lineMessagingService.sendErrorMessage(
            event.replyToken,
            friendlyMessage
          );
        } catch (replyError) {
          const replyErrorContext: ErrorContext = {
            userId: errorContext.userId,
            operation: 'sendErrorMessage'
          };
          ErrorHandler.log(replyError as Error, replyErrorContext);
        }
      }
    }
  }

  /**
   * 處理文字訊息事件
   * @param event LINE 訊息事件
   */
  async processMessage(event: line.MessageEvent): Promise<void> {
    // 只處理文字訊息
    if (event.message.type !== 'text') {
      console.log(`Unhandled message type: ${event.message.type}`);
      return;
    }

    const userMessage = event.message.text;
    const replyToken = event.replyToken;
    const userId = event.source?.userId;

    try {
      console.log(`Processing message from user: ${userMessage}`);

      // 檢查是否為「最新消息」指令
      if (userMessage.trim() === '最新消息') {
        await this.handleBulletinsCommand(replyToken);
        return;
      }

      // 檢查是否為訂閱相關指令
      if (await this.handleSubscriptionCommand(userMessage, replyToken, userId)) {
        return; // 如果是訂閱指令，直接返回
      }

      // 使用 Gemini Service 處理用戶查詢
      const { text, books } = await geminiService.processUserQuery(userMessage);

      // 使用 LINE Messaging Service 發送回覆
      await lineMessagingService.sendBookQueryResponse(replyToken, text, books);

      console.log(`Successfully replied to user with ${books.length} books found`);

    } catch (error) {
      // 建立錯誤上下文
      const errorContext: ErrorContext = {
        userId,
        userMessage,
        operation: 'processMessage'
      };
      
      // 使用統一錯誤處理
      const friendlyMessage = ErrorHandler.handle(error as Error, errorContext);
      
      // 發送友善的錯誤訊息
      try {
        await lineMessagingService.sendErrorMessage(replyToken, friendlyMessage);
      } catch (replyError) {
        const replyErrorContext: ErrorContext = {
          userId,
          operation: 'sendErrorMessage_processMessage'
        };
        ErrorHandler.log(replyError as Error, replyErrorContext);
      }
    }
  }

  /**
   * 處理最新消息指令
   * @param replyToken 回覆 token
   */
  private async handleBulletinsCommand(replyToken: string): Promise<void> {
    try {
      console.log('Fetching latest bulletins...');
      
      // 取得停課公告（最多 3 則）
      const courseCancellations = await bulletinService.getCourseCancellations(3);
      
      // 取得最新消息（最多 9 則，因為第一張要放停課公告）
      const bulletins = await bulletinService.getLatestBulletins(9);
      
      if (bulletins.length === 0 && courseCancellations.length === 0) {
        await lineMessagingService.sendTextMessage(replyToken, '目前沒有最新消息');
        return;
      }

      // 發送 Carousel 訊息（帶 Quick Reply，第一張為停課公告）
      await lineMessagingService.sendBulletinsCarousel(replyToken, bulletins, courseCancellations);
      
      console.log(`Successfully sent ${bulletins.length} bulletins with ${courseCancellations.length} course cancellations`);
    } catch (error) {
      console.error('Error handling bulletins command:', error);
      await lineMessagingService.sendErrorMessage(replyToken, '無法取得最新消息，請稍後再試');
    }
  }

  /**
   * 處理訂閱相關指令
   * @param userMessage 用戶訊息
   * @param replyToken 回覆 token
   * @param userId 用戶 ID
   * @returns Promise<boolean> 是否為訂閱指令
   */
  private async handleSubscriptionCommand(
    userMessage: string, 
    replyToken: string, 
    userId?: string
  ): Promise<boolean> {
    if (!userId) {
      return false; // 無法處理沒有用戶 ID 的訂閱指令
    }

    const message = userMessage.trim();

    try {
      // 訂閱特定類型（每個指令只訂閱對應的單一類型）
      if (message === '訂閱新書' || message === '訂閱') {
        await this.handleSubscribeToTypeCommand(replyToken, userId, 'new_books');
        return true;
      }

      if (message === '訂閱最新消息' || message === '訂閱新聞') {
        await this.handleSubscribeToTypeCommand(replyToken, userId, 'news');
        return true;
      }

      if (message === '訂閱停課通知' || message === '訂閱停課') {
        await this.handleSubscribeToTypeCommand(replyToken, userId, 'cancellation');
        return true;
      }

      // 取消訂閱
      if (message === '取消訂閱') {
        await this.handleUnsubscribeCommand(replyToken, userId);
        return true;
      }

      // 取消訂閱特定類型
      if (message === '取消訂閱新書') {
        await this.handleUnsubscribeFromTypeCommand(replyToken, userId, 'new_books');
        return true;
      }

      if (message === '取消訂閱最新消息' || message === '取消訂閱新聞') {
        await this.handleUnsubscribeFromTypeCommand(replyToken, userId, 'news');
        return true;
      }

      if (message === '取消訂閱停課通知' || message === '取消訂閱停課') {
        await this.handleUnsubscribeFromTypeCommand(replyToken, userId, 'cancellation');
        return true;
      }

      // 查詢訂閱狀態
      if (message === '訂閱狀態' || message === '我的訂閱') {
        await this.handleSubscriptionStatusCommand(replyToken, userId);
        return true;
      }

      // 重新訂閱（顯示訂閱選項）
      if (message === '重新訂閱') {
        await this.handleResubscribeCommand(replyToken);
        return true;
      }

      return false; // 不是訂閱指令
    } catch (error) {
      const errorContext: ErrorContext = {
        userId,
        userMessage,
        operation: 'handleSubscriptionCommand'
      };
      
      const friendlyMessage = ErrorHandler.handle(error as Error, errorContext);
      
      try {
        await lineMessagingService.sendErrorMessage(replyToken, friendlyMessage);
      } catch (replyError) {
        ErrorHandler.log(replyError as Error, { ...errorContext, operation: 'sendErrorMessage_subscription' });
      }
      
      return true; // 即使出錯也算是處理了訂閱指令
    }
  }



  /**
   * 處理訂閱特定類型的指令
   * @param replyToken 回覆 token
   * @param userId 用戶 ID
   * @param notificationType 通知類型
   */
  private async handleSubscribeToTypeCommand(
    replyToken: string, 
    userId: string, 
    notificationType: 'news' | 'cancellation' | 'new_books'
  ): Promise<void> {
    console.log(`User ${userId} requesting subscription to ${notificationType}`);

    // 檢查用戶是否已經訂閱該類型
    const isAlreadySubscribed = await subscriptionService.isUserSubscribedToType(userId, notificationType);
    
    if (isAlreadySubscribed) {
      await lineMessagingService.sendSubscriptionTypeAlreadyActiveMessage(replyToken, notificationType);
      return;
    }

    // 訂閱特定類型
    const success = await subscriptionService.subscribeToType(userId, notificationType);
    
    if (success) {
      await lineMessagingService.sendSubscriptionTypeSuccessMessage(replyToken, notificationType);
      console.log(`User ${userId} successfully subscribed to ${notificationType}`);
    } else {
      await lineMessagingService.sendSubscriptionFailureMessage(replyToken);
      console.error(`Failed to subscribe user ${userId} to ${notificationType}`);
    }
  }

  /**
   * 處理取消訂閱特定類型的指令
   * @param replyToken 回覆 token
   * @param userId 用戶 ID
   * @param notificationType 通知類型
   */
  private async handleUnsubscribeFromTypeCommand(
    replyToken: string, 
    userId: string, 
    notificationType: 'news' | 'cancellation' | 'new_books'
  ): Promise<void> {
    console.log(`User ${userId} requesting unsubscription from ${notificationType}`);

    // 檢查用戶是否訂閱該類型
    const isSubscribed = await subscriptionService.isUserSubscribedToType(userId, notificationType);
    
    if (!isSubscribed) {
      await lineMessagingService.sendNotSubscribedToTypeMessage(replyToken, notificationType);
      return;
    }

    // 取消訂閱特定類型
    const success = await subscriptionService.unsubscribeFromType(userId, notificationType);
    
    if (success) {
      await lineMessagingService.sendUnsubscriptionTypeSuccessMessage(replyToken, notificationType);
      console.log(`User ${userId} successfully unsubscribed from ${notificationType}`);
    } else {
      await lineMessagingService.sendUnsubscriptionFailureMessage(replyToken);
      console.error(`Failed to unsubscribe user ${userId} from ${notificationType}`);
    }
  }

  /**
   * 處理取消訂閱指令
   * @param replyToken 回覆 token
   * @param userId 用戶 ID
   */
  private async handleUnsubscribeCommand(replyToken: string, userId: string): Promise<void> {
    console.log(`User ${userId} requesting unsubscription`);

    // 檢查用戶是否已經訂閱
    const isSubscribed = await subscriptionService.isUserSubscribed(userId);
    
    if (!isSubscribed) {
      await lineMessagingService.sendNotSubscribedMessage(replyToken);
      return;
    }

    // 取消訂閱
    const success = await subscriptionService.unsubscribeUser(userId);
    
    if (success) {
      await lineMessagingService.sendUnsubscriptionSuccessMessage(replyToken);
      console.log(`User ${userId} successfully unsubscribed from daily notifications`);
    } else {
      await lineMessagingService.sendUnsubscriptionFailureMessage(replyToken);
      console.error(`Failed to unsubscribe user ${userId}`);
    }
  }

  /**
   * 處理訂閱狀態查詢指令
   * @param replyToken 回覆 token
   * @param userId 用戶 ID
   */
  private async handleSubscriptionStatusCommand(replyToken: string, userId: string): Promise<void> {
    console.log(`User ${userId} requesting subscription status`);

    // 取得用戶訂閱資訊
    const subscription = await subscriptionService.getUserSubscription(userId);
    
    await lineMessagingService.sendSubscriptionStatusMessage(replyToken, subscription);
  }

  /**
   * 處理重新訂閱指令（顯示訂閱選項）
   * @param replyToken 回覆 token
   */
  private async handleResubscribeCommand(replyToken: string): Promise<void> {
    console.log('User requesting resubscribe options');

    const resubscribeText = `請選擇您想要訂閱的通知類型：`;

    const quickReply: line.QuickReply = {
      items: [
        {
          type: 'action',
          action: {
            type: 'message',
            label: '📰 訂閱最新消息',
            text: '訂閱最新消息'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '⚠️ 訂閱停課通知',
            text: '訂閱停課通知'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '📚 訂閱新書通知',
            text: '訂閱新書通知'
          }
        }
      ]
    };

    const textMessage: line.TextMessage = {
      type: 'text',
      text: resubscribeText,
      quickReply
    };

    await lineMessagingService.replyMessage(replyToken, [textMessage]);
  }

  /**
   * 處理用戶加入好友事件
   * @param event LINE Follow 事件
   */
  private async processFollowEvent(event: line.FollowEvent): Promise<void> {
    try {
      console.log('New user followed the bot');
      
      // 發送歡迎訊息（包含訂閱選項）
      await lineMessagingService.sendWelcomeMessageWithSubscription(event.replyToken);
      
    } catch (error) {
      // 建立錯誤上下文
      const errorContext: ErrorContext = {
        userId: event.source?.userId,
        operation: 'processFollowEvent'
      };
      
      // 記錄錯誤但不發送錯誤訊息給用戶（歡迎訊息失敗不需要通知）
      ErrorHandler.log(error as Error, errorContext);
    }
  }

  /**
   * 取得 LINE SDK middleware 用於 Express 路由
   * @returns LINE SDK middleware 函式
   */
  getMiddleware(): express.RequestHandler {
    return line.middleware({
      channelSecret: lineConfig.channelSecret
    });
  }
}

// 建立單例實例
export const webhookHandler = new WebhookHandler();

// 預設匯出
export default webhookHandler;