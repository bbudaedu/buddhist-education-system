import express from 'express';
import * as line from '@line/bot-sdk';
import { lineConfig } from '../config/index';
import { geminiService } from '../services/geminiService';
import { lineMessagingService } from '../services/lineMessagingService';
import { subscriptionService } from '../services/subscriptionService';
import { bulletinService } from '../services/bulletinService';
import { adminService } from '../services/adminService';
import { flexMessageService } from '../services/flexMessageService';
import { dharmaMediaHandler } from './dharmaMediaHandler';
import { ErrorHandler, ErrorContext } from './errorHandler';
import { systemSettingsService } from '../services/systemSettingsService';
import { matchQuickCommand, getCommandDisplayName } from '../services/fuzzyCommandService';

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

      // 優先檢查管理員測試指令（在所有其他指令之前）
      if (userId && await adminService.isAdmin(userId)) {
        const isTestCommand = await this.handleAdminTestCommand(userMessage, replyToken);
        if (isTestCommand) {
          return; // 如果是管理員測試指令，直接返回
        }
      }

      // 優先檢查訂閱相關指令（在模糊匹配之前，避免「訂閱影音通知」被「影音」誤觸發）
      if (await this.handleSubscriptionCommand(userMessage, replyToken, userId)) {
        return; // 如果是訂閱指令，直接返回
      }

      // 檢查是否為快捷指令（支援模糊匹配）
      const quickCommand = matchQuickCommand(userMessage);
      if (quickCommand) {
        console.log(`Matched quick command: ${getCommandDisplayName(quickCommand)} (type: ${quickCommand})`);

        switch (quickCommand) {
          case 'bulletins':
            await this.handleBulletinsCommand(replyToken);
            return;
          case 'cancellations':
            await this.handleCancellationsCommand(replyToken);
            return;
          case 'latestBooks':
            await dharmaMediaHandler.handleLatestBooksCommand(replyToken);
            return;
          case 'latestVideos':
            await dharmaMediaHandler.handleLatestVideosCommand(replyToken);
            return;
        }
      }

      // 檢查 LLM 是否啟用，若關閉則靜默不回應
      const llmEnabled = await systemSettingsService.isLlmEnabled();
      if (!llmEnabled) {
        console.log('LLM is disabled, skipping Gemini query');
        return; // 靜默返回，不做任何回應
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

      // 取得停課公告（最多 8 則）
      const courseCancellations = await bulletinService.getCourseCancellations(8);

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
   * 處理停課通知指令
   * @param replyToken 回覆 token
   */
  private async handleCancellationsCommand(replyToken: string): Promise<void> {
    try {
      console.log('Fetching course cancellations...');

      // 取得停課公告（最多 10 則）
      const courseCancellations = await bulletinService.getCourseCancellations(10);

      // 建立停課內容
      let courseCancelContent = '🎉 目前沒有停課公告\n所有課程正常進行！';

      if (courseCancellations.length > 0) {
        courseCancelContent = courseCancellations.map((cancel: any) => {
          const date = new Date(cancel.cancelDate).toLocaleDateString('zh-TW', {
            month: '2-digit',
            day: '2-digit'
          });
          return `📅 ${date} ${cancel.courseTitle}`;
        }).join('\n');
      }

      // 建立簡化的停課通知 Flex Message（單一卡片）
      const flexMessage: line.FlexMessage = {
        type: 'flex',
        altText: `⚠️ 停課通知 (${courseCancellations.length} 則)`,
        contents: {
          type: 'bubble',
          hero: {
            type: 'box',
            layout: 'vertical',
            contents: [
              {
                type: 'text',
                text: '⚠️',
                size: '3xl',
                align: 'center'
              }
            ],
            backgroundColor: '#FFF3E0',
            paddingAll: 'md'
          },
          body: {
            type: 'box',
            layout: 'vertical',
            contents: [
              {
                type: 'text',
                text: '停課公告',
                weight: 'bold',
                size: 'xl',
                wrap: true
              },
              {
                type: 'separator',
                margin: 'md'
              },
              {
                type: 'text',
                text: courseCancelContent,
                size: 'lg',
                wrap: true,
                color: '#666666',
                margin: 'md'
              }
            ],
            spacing: 'sm'
          },
          footer: {
            type: 'box',
            layout: 'vertical',
            contents: [
              {
                type: 'button',
                action: {
                  type: 'uri',
                  label: '查看完整停課公告',
                  uri: 'https://www.budaedu.org/#/bulletins/course-cancel'
                },
                style: 'primary',
                color: '#FF9800'
              }
            ]
          }
        }
      };

      // 發送訊息
      await lineMessagingService.replyMessage(replyToken, [flexMessage]);

      console.log(`Successfully sent ${courseCancellations.length} course cancellations`);
    } catch (error) {
      console.error('Error handling cancellations command:', error);
      await lineMessagingService.sendErrorMessage(replyToken, '無法取得停課通知，請稍後再試');
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

    const message = userMessage.trim().toLowerCase();

    try {
      // 訂閱新書（支援模糊匹配）
      if (message.includes('訂閱') && (message.includes('新書') || message.includes('書籍'))) {
        await this.handleSubscribeToTypeCommand(replyToken, userId, 'new_books');
        return true;
      }

      // 訂閱影音/課程通知（支援模糊匹配）
      if (message.includes('訂閱') && (message.includes('影音') || message.includes('視訊') || message.includes('影片') || message.includes('課程') || message.includes('最新影音') || message.includes('最新課程'))) {
        await this.handleSubscribeToTypeCommand(replyToken, userId, 'videos');
        return true;
      }

      // 訂閱最新消息（支援模糊匹配）
      if (message.includes('訂閱') && (message.includes('最新消息') || message.includes('新聞') || message.includes('消息'))) {
        await this.handleSubscribeToTypeCommand(replyToken, userId, 'news');
        return true;
      }

      // 訂閱停課通知（支援模糊匹配）
      if (message.includes('訂閱') && (message.includes('停課') || message.includes('課程取消'))) {
        await this.handleSubscribeToTypeCommand(replyToken, userId, 'cancellation');
        return true;
      }

      // 全部訂閱（訂閱所有類型）
      if (message.includes('全部訂閱') || message.includes('訂閱全部') || message.includes('訂閱所有')) {
        await this.handleSubscribeAllCommand(replyToken, userId);
        return true;
      }

      // 單純的「訂閱」指令 - 顯示訂閱選項
      if (message === '訂閱') {
        await this.handleResubscribeCommand(replyToken);
        return true;
      }

      // 取消訂閱新書
      if (message.includes('取消') && message.includes('訂閱') && (message.includes('新書') || message.includes('書籍'))) {
        await this.handleUnsubscribeFromTypeCommand(replyToken, userId, 'new_books');
        return true;
      }

      // 取消訂閱最新消息
      if (message.includes('取消') && message.includes('訂閱') && (message.includes('最新消息') || message.includes('新聞') || message.includes('消息'))) {
        await this.handleUnsubscribeFromTypeCommand(replyToken, userId, 'news');
        return true;
      }

      // 取消訂閱停課通知
      if (message.includes('取消') && message.includes('訂閱') && (message.includes('停課') || message.includes('課程取消'))) {
        await this.handleUnsubscribeFromTypeCommand(replyToken, userId, 'cancellation');
        return true;
      }

      // 取消所有訂閱
      if (message.includes('取消') && message.includes('訂閱') && !message.includes('新書') && !message.includes('消息') && !message.includes('停課')) {
        await this.handleUnsubscribeCommand(replyToken, userId);
        return true;
      }

      // 查詢訂閱狀態
      if (message.includes('訂閱狀態') || message.includes('我的訂閱') || message === '訂閱查詢') {
        await this.handleSubscriptionStatusCommand(replyToken, userId);
        return true;
      }

      // 重新訂閱（顯示訂閱選項）
      if (message.includes('重新訂閱')) {
        await this.handleResubscribeCommand(replyToken);
        return true;
      }

      // 學員中心入口
      if (message === '學員中心' || message === '會員中心' || message === '個人設定' || message === '偏好設定') {
        await this.handleStudentCenterCommand(replyToken);
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
    notificationType: 'news' | 'cancellation' | 'new_books' | 'videos'
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
   * 處理全部訂閱指令
   * @param replyToken 回覆 token
   * @param userId 用戶 ID
   */
  private async handleSubscribeAllCommand(
    replyToken: string,
    userId: string
  ): Promise<void> {
    console.log(`User ${userId} requesting subscription to all types`);

    const allTypes: ('news' | 'cancellation' | 'new_books' | 'videos')[] = ['news', 'cancellation', 'new_books', 'videos'];

    try {
      // 訂閱所有類型
      for (const type of allTypes) {
        await subscriptionService.subscribeToType(userId, type);
      }

      const successText = `✅ 全部訂閱成功！

您已成功訂閱所有通知類型：
📰 最新消息
⚠️ 停課通知
📚 新書通知
🎬 最新課程

我們會在有新內容時立即通知您。`;

      const quickReply: line.QuickReply = {
        items: [
          {
            type: 'action',
            action: {
              type: 'message',
              label: '📊 查看訂閱狀態',
              text: '訂閱狀態'
            }
          },
          {
            type: 'action',
            action: {
              type: 'message',
              label: '❌ 取消訂閱',
              text: '取消訂閱'
            }
          }
        ]
      };

      const textMessage: line.TextMessage = {
        type: 'text',
        text: successText,
        quickReply
      };

      await lineMessagingService.replyMessage(replyToken, [textMessage]);
      console.log(`User ${userId} successfully subscribed to all types`);
    } catch (error) {
      await lineMessagingService.sendSubscriptionFailureMessage(replyToken);
      console.error(`Failed to subscribe user ${userId} to all types:`, error);
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
    notificationType: 'news' | 'cancellation' | 'new_books' | 'videos'
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
   * 處理學員中心指令
   * @param replyToken 回覆 token
   */
  private async handleStudentCenterCommand(replyToken: string): Promise<void> {
    console.log('User requesting student center');

    const LIFF_URL = 'https://liff.line.me/2008639772-ndVeDxwD';

    const flexMessage: line.FlexMessage = {
      type: 'flex',
      altText: '🎓 學員中心',
      contents: {
        type: 'bubble',
        hero: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '🎓',
              size: '3xl',
              align: 'center'
            }
          ],
          backgroundColor: '#06C755',
          paddingAll: 'lg'
        },
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '學員中心',
              weight: 'bold',
              size: 'xl',
              align: 'center'
            },
            {
              type: 'text',
              text: '設定您的通知偏好和 Email',
              size: 'sm',
              color: '#666666',
              align: 'center',
              margin: 'md'
            }
          ],
          spacing: 'sm'
        },
        footer: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'button',
              action: {
                type: 'uri',
                label: '開啟學員中心',
                uri: LIFF_URL
              },
              style: 'primary',
              color: '#06C755'
            }
          ]
        }
      }
    };

    await lineMessagingService.replyMessage(replyToken, [flexMessage]);
  }

  /**
   * 處理管理員測試指令
   * @param userMessage 用戶訊息
   * @param replyToken 回覆 token
   * @returns Promise<boolean> 是否為管理員測試指令
   */
  private async handleAdminTestCommand(
    userMessage: string,
    replyToken: string
  ): Promise<boolean> {
    const message = userMessage.trim().toLowerCase();

    try {
      // LLM ON - 開啟書庫助理 LLM 功能
      if (message === 'llm on') {
        await systemSettingsService.setLlmEnabled(true);
        await lineMessagingService.sendTextMessage(replyToken, '✅ 書庫助理 LLM 功能已開啟');
        console.log('Admin enabled LLM');
        return true;
      }

      // LLM OFF - 關閉書庫助理 LLM 功能
      if (message === 'llm off') {
        await systemSettingsService.setLlmEnabled(false);
        await lineMessagingService.sendTextMessage(replyToken, '⏸️ 書庫助理 LLM 功能已關閉');
        console.log('Admin disabled LLM');
        return true;
      }

      // LLM STATUS - 查詢 LLM 狀態
      if (message === 'llm status') {
        const isEnabled = await systemSettingsService.isLlmEnabled();
        const statusText = isEnabled ? '🟢 開啟中' : '🔴 關閉中';
        await lineMessagingService.sendTextMessage(replyToken, `📚 書庫助理 LLM 狀態: ${statusText}`);
        return true;
      }

      // flex1 - 新書通知測試
      if (message === 'flex1') {
        await this.sendTestNewBooksNotification(replyToken);
        return true;
      }

      // flex2 - 新聞公告測試
      if (message === 'flex2') {
        await this.sendTestNewsNotification(replyToken);
        return true;
      }

      // flex3 - 停課通知測試
      if (message === 'flex3') {
        await this.sendTestCancellationNotification(replyToken);
        return true;
      }

      // flex4 - 整合通知測試
      if (message === 'flex4') {
        await this.sendTestIntegratedNotification(replyToken);
        return true;
      }

      // realdata - 使用真實資料測試
      if (message === 'realdata') {
        await this.sendRealDataTest(replyToken);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Error handling admin test command:', error);
      // 錯誤已經在測試方法中處理，不要再次使用 replyToken
      return true;
    }
  }

  /**
   * 發送新書通知測試
   */
  private async sendTestNewBooksNotification(replyToken: string): Promise<void> {
    // 先用簡單的文字訊息測試管理員指令是否正常工作
    const testMessage = '📚 新書通知測試\n\n' +
      '1. 金剛經講記\n' +
      '   作者：淨空法師\n' +
      '   閱讀：https://www.budaedu.org/ebooks/book1.pdf\n\n' +
      '2. 楞嚴經淺釋\n' +
      '   作者：宣化上人\n' +
      '   閱讀：https://www.budaedu.org/ebooks/book2.pdf\n\n' +
      '3. 地藏菩薩本願經白話解釋\n' +
      '   作者：黃智海居士\n' +
      '   閱讀：https://www.budaedu.org/ebooks/book3.pdf\n\n' +
      '✅ 管理員測試指令正常運作！\n' +
      '（Flex Message 功能開發中）';

    await lineMessagingService.sendTextMessage(replyToken, testMessage);
    console.log('Sent test new books notification (text version)');
  }

  /**
   * 發送新聞公告測試
   */
  private async sendTestNewsNotification(replyToken: string): Promise<void> {
    const testMessage = '📰 新聞公告測試\n\n' +
      '1. 小菩薩的慈悲畫室－佛法讀經與護生繪畫班\n' +
      '   日期：2025-11-13\n' +
      '   連結：https://www.budaedu.org/#/course/123\n\n' +
      '2. 學佛基礎進階班－賢愚經課程公告\n' +
      '   日期：2025-11-11\n' +
      '   連結：https://www.budaedu.org/#/course/124\n\n' +
      '3. 佛學講座：心經的智慧\n' +
      '   日期：2025-11-10\n' +
      '   連結：https://www.budaedu.org/#/course/125\n\n' +
      '✅ 管理員測試指令正常運作！';

    await lineMessagingService.sendTextMessage(replyToken, testMessage);
    console.log('Sent test news notification (text version)');
  }

  /**
   * 發送停課通知測試
   */
  private async sendTestCancellationNotification(replyToken: string): Promise<void> {
    const testMessage = '🚫 停課通知測試\n\n' +
      '1. 華嚴經宗通\n' +
      '   日期：2025-11-20\n' +
      '   講師：某某法師\n' +
      '   地點：七樓教室\n\n' +
      '2. 楞嚴經研討\n' +
      '   日期：2025-11-22\n' +
      '   講師：某某居士\n' +
      '   地點：五樓教室\n\n' +
      '3. 禪修入門班\n' +
      '   日期：2025-11-25\n' +
      '   講師：禪師\n' +
      '   地點：禪堂\n\n' +
      '✅ 管理員測試指令正常運作！';

    await lineMessagingService.sendTextMessage(replyToken, testMessage);
    console.log('Sent test cancellation notification (text version)');
  }

  /**
   * 發送整合通知測試
   */
  private async sendTestIntegratedNotification(replyToken: string): Promise<void> {
    const testMessage = '📢 整合通知測試\n\n' +
      '=== 摘要 ===\n' +
      '📚 新書上架 2 本\n' +
      '📰 新聞公告 2 則\n' +
      '🚫 停課通知 1 則\n\n' +
      '=== 新書上架 ===\n' +
      '1. 金剛經講記 - 淨空法師\n' +
      '2. 楞嚴經淺釋 - 宣化上人\n\n' +
      '=== 新聞公告 ===\n' +
      '1. 小菩薩的慈悲畫室課程公告\n' +
      '2. 佛學講座：心經的智慧\n\n' +
      '=== 停課通知 ===\n' +
      '1. 華嚴經宗通 (2025-11-20)\n\n' +
      '✅ 管理員測試指令正常運作！\n' +
      '（這是整合通知的文字版本）';

    await lineMessagingService.sendTextMessage(replyToken, testMessage);
    console.log('Sent test integrated notification (text version)');
  }

  /**
   * 發送真實資料測試
   * 從資料庫取得真實的新書、新聞、停課資料
   */
  private async sendRealDataTest(replyToken: string): Promise<void> {
    try {
      console.log('Fetching real data for test...');

      // 1. 取得真實的停課公告（最多 3 則）
      const courseCancellations = await bulletinService.getCourseCancellations(3);

      // 2. 取得真實的新聞公告（最多 3 則）
      const bulletins = await bulletinService.getLatestBulletins(3);

      // 3. 取得真實的新書資料（從資料庫）
      const { databaseService } = await import('../services/databaseService');
      const recentBooks = await databaseService.searchBooks('', 3);

      // 準備資料
      const realData: {
        newBooks?: any[];
        news?: any[];
        cancellations?: any[];
      } = {};

      // 轉換新書資料
      if (recentBooks && recentBooks.length > 0) {
        realData.newBooks = recentBooks
          .filter((book: any) => book.title) // 過濾掉沒有標題的書籍
          .map((book: any) => ({
            title: book.title,
            author: book.author || '未知作者',
            pdfUrls: [] // Book 資料表沒有 PDF URL，使用空陣列
          }));
      }

      // 轉換新聞資料
      if (bulletins && bulletins.length > 0) {
        realData.news = bulletins
          .filter((bulletin: any) => bulletin.title) // 過濾掉沒有標題的新聞
          .map((bulletin: any) => {
            // 清理文字內容：統一換行符號、移除特殊字元
            const cleanText = (text: string): string => {
              if (!text) return '';
              return text
                .replace(/\r\n/g, '\n')  // 統一換行符號
                .replace(/\r/g, '\n')     // 移除單獨的 \r
                .replace(/\t/g, ' ')      // Tab 轉空格
                .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '') // 移除控制字元
                .trim();
            };

            return {
              title: cleanText(bulletin.title),
              date: cleanText(bulletin.publication_date || bulletin.created_at || '未知日期'),
              url: bulletin.url || '',
              content: cleanText(bulletin.content || '')
            };
          });
      }

      // 轉換停課資料
      if (courseCancellations && courseCancellations.length > 0) {
        realData.cancellations = courseCancellations
          .filter((cancellation: any) => cancellation.course_name && cancellation.cancellation_date) // 過濾掉空資料
          .map((cancellation: any) => ({
            courseName: cancellation.course_name,
            date: cancellation.cancellation_date,
            instructor: cancellation.instructor_name || '未知講師',
            location: cancellation.location || ''
          }));
      }

      // 清理空陣列
      if (realData.newBooks && realData.newBooks.length === 0) {
        delete realData.newBooks;
      }
      if (realData.news && realData.news.length === 0) {
        delete realData.news;
      }
      if (realData.cancellations && realData.cancellations.length === 0) {
        delete realData.cancellations;
      }

      // 檢查是否有資料
      const hasData = (realData.newBooks && realData.newBooks.length > 0) ||
        (realData.news && realData.news.length > 0) ||
        (realData.cancellations && realData.cancellations.length > 0);

      if (!hasData) {
        await lineMessagingService.sendTextMessage(
          replyToken,
          '⚠️ 目前資料庫中沒有足夠的真實資料\n\n請先執行：\n1. 新書爬蟲\n2. 新聞爬蟲\n3. 停課公告爬蟲\n\n或使用 flex1-4 查看測試資料'
        );
        return;
      }

      // 限制總 bubble 數量（LINE 限制最多 10 個）
      // 摘要 1 個 + 內容最多 9 個
      let totalBubbles = 1; // 摘要
      if (realData.newBooks) {
        const maxBooks = Math.min(realData.newBooks.length, 3);
        realData.newBooks = realData.newBooks.slice(0, maxBooks);
        totalBubbles += maxBooks;
      }
      if (realData.news && totalBubbles < 10) {
        const maxNews = Math.min(realData.news.length, 10 - totalBubbles);
        realData.news = realData.news.slice(0, maxNews);
        totalBubbles += maxNews;
      }
      if (realData.cancellations && totalBubbles < 10) {
        const maxCancellations = Math.min(realData.cancellations.length, 10 - totalBubbles);
        realData.cancellations = realData.cancellations.slice(0, maxCancellations);
      }

      // 創建整合通知
      console.log('Creating integrated notification with data:');
      console.log(`- Books: ${realData.newBooks?.length || 0}`);
      console.log(`- News: ${realData.news?.length || 0}`);
      console.log(`- Cancellations: ${realData.cancellations?.length || 0}`);

      const message = flexMessageService.createIntegratedNotification(realData);

      // 驗證訊息結構
      const messageJson = JSON.stringify(message);
      console.log(`Message size: ${messageJson.length} bytes`);

      // 檢查 Carousel bubble 數量
      if (message.contents.type === 'carousel') {
        const bubbleCount = message.contents.contents.length;
        console.log(`Total bubbles: ${bubbleCount}`);

        if (bubbleCount > 10) {
          throw new Error(`Too many bubbles: ${bubbleCount} (max 10)`);
        }
      }

      // 驗證 JSON 是否有效（檢查是否有無效字元）
      try {
        JSON.parse(messageJson);
      } catch (jsonError) {
        throw new Error(`Invalid JSON structure: ${jsonError}`);
      }

      // 發送訊息
      await lineMessagingService.replyMessage(replyToken, [message]);

      console.log('✅ Sent real data test notification successfully');
    } catch (error) {
      console.error('Error sending real data test:', error);

      // 嘗試發送錯誤訊息（可能會因為 replyToken 已使用而失敗）
      try {
        await lineMessagingService.sendErrorMessage(
          replyToken,
          '❌ 發送真實資料測試失敗\n\n請檢查伺服器日誌了解詳情'
        );
      } catch (replyError) {
        // replyToken 已被使用，無法發送錯誤訊息
        console.error('Cannot send error message: replyToken already used');
      }
    }
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