import * as line from '@line/bot-sdk';
import { lineConfig } from '../config/index';
import { Book } from '../types/book';
import { UserSubscription } from '../types/subscription';
import { subscriptionCarouselTemplate } from './flexMessageTemplates/subscriptionCarouselTemplate';

export class LineMessagingService {
  private client: line.messagingApi.MessagingApiClient;

  constructor() {
    // 初始化 LINE Bot SDK Client
    this.client = new line.messagingApi.MessagingApiClient({
      channelAccessToken: lineConfig.channelAccessToken
    });
  }

  /**
   * 回覆訊息給用戶
   * @param replyToken - LINE 提供的回覆 token
   * @param messages - 要發送的訊息陣列
   */
  async replyMessage(replyToken: string, messages: line.Message[]): Promise<void> {
    try {
      await this.client.replyMessage({
        replyToken,
        messages
      });
    } catch (error: any) {
      console.error('Failed to reply message:', error);
      // 顯示 LINE API 的詳細錯誤訊息
      if (error.response && error.response.data) {
        console.error('LINE API Error Details:', JSON.stringify(error.response.data, null, 2));
      }
      throw new Error('LINE API 回覆失敗');
    }
  }

  /**
   * 主動發送訊息給用戶
   * @param userId - LINE 用戶 ID
   * @param messages - 要發送的訊息陣列
   */
  async pushMessage(userId: string, messages: line.Message[]): Promise<void> {
    try {
      await this.client.pushMessage({
        to: userId,
        messages
      });
    } catch (error: any) {
      console.error('Failed to push message:', error);
      if (error.response && error.response.data) {
        console.error('LINE API Error Details:', JSON.stringify(error.response.data, null, 2));
      }
      throw new Error('LINE API 推送失敗');
    }
  }

  /**
   * 發送簡單文字訊息
   * @param replyToken - LINE 提供的回覆 token
   * @param text - 要發送的文字內容
   */
  async sendTextMessage(replyToken: string, text: string): Promise<void> {
    // 確保文字內容不為空
    const messageText = text && text.trim() !== '' ? text : '抱歉，系統暫時無法處理您的請求，請稍後再試。';

    const textMessage: line.TextMessage = {
      type: 'text',
      text: messageText
    };

    await this.replyMessage(replyToken, [textMessage]);
  }

  /**
   * 根據書籍數量判斷訊息格式並發送適當的回覆
   * @param replyToken - LINE 提供的回覆 token
   * @param text - Gemini 生成的回覆文字
   * @param books - 查詢到的書籍陣列
   */
  async sendBookQueryResponse(replyToken: string, text: string, books: Book[]): Promise<void> {
    // 確保回覆文字不為空
    const responseText = text && text.trim() !== '' ? text : '抱歉，系統暫時無法處理您的請求，請稍後再試。';

    // 訊息格式判斷邏輯：1-2 本書用文字，3+ 本書用 Carousel
    if (books.length >= 3) {
      await this.sendCarouselMessage(replyToken, books, responseText);
    } else {
      await this.sendTextMessage(replyToken, responseText);
    }
  }

  /**
   * 發送書籍卡片輪播訊息
   * @param replyToken - LINE 提供的回覆 token
   * @param books - 書籍陣列
   * @param altText - 替代文字（用於不支援 rich message 的環境）
   */
  async sendCarouselMessage(replyToken: string, books: Book[], altText?: string): Promise<void> {
    // 限制最多 10 本書（LINE Carousel 限制）
    const limitedBooks = books.slice(0, 10);

    const carouselColumns = limitedBooks.map(book => ({
      // 標題限制 40 字元
      title: book.title.length > 40 ? book.title.substring(0, 37) + '...' : book.title,

      // 文字內容
      text: `館藏地：${book.library_branch}\n位置：${book.shelf_location}\n庫存：${book.quantity} 本`,

      // 動作按鈕
      actions: [
        {
          type: 'message' as const,
          label: '查看詳情',
          text: `請提供《${book.title}》的詳細資訊`
        },
        {
          type: 'message' as const,
          label: '借閱資訊',
          text: `我想借《${book.title}》這本書`
        }
      ]
    }));

    const carouselMessage: line.TemplateMessage = {
      type: 'template',
      altText: altText || '書籍查詢結果',
      template: {
        type: 'carousel',
        columns: carouselColumns
      }
    };

    await this.replyMessage(replyToken, [carouselMessage]);
  }

  /**
   * 發送錯誤訊息給用戶
   * @param replyToken - LINE 提供的回覆 token
   * @param errorMessage - 錯誤訊息
   */
  async sendErrorMessage(replyToken: string, errorMessage: string): Promise<void> {
    const defaultErrorMessage = '抱歉，系統暫時無法處理您的請求，請稍後再試。';
    await this.sendTextMessage(replyToken, errorMessage || defaultErrorMessage);
  }

  /**
   * 發送歡迎訊息
   * @param replyToken - LINE 提供的回覆 token
   */
  async sendWelcomeMessage(replyToken: string): Promise<void> {
    const welcomeText = `歡迎使用書庫查詢機器人！🤖📚

您可以用自然語言詢問書籍相關問題，例如：
• "有沒有金剛經相關的書？"
• "找一些關於程式設計的書"
• "推薦幾本小說"

我會幫您搜尋書庫並提供詳細資訊！`;

    await this.sendTextMessage(replyToken, welcomeText);
  }

  /**
   * 發送包含訂閱選項的歡迎訊息
   * @param replyToken - LINE 提供的回覆 token
   */
  async sendWelcomeMessageWithSubscription(replyToken: string): Promise<void> {
    const flexMessage = this.createWelcomeFlexMessage();
    await this.replyMessage(replyToken, [flexMessage]);
  }

  /**
   * 發送訂閱成功訊息
   * @param replyToken - LINE 提供的回覆 token
   */
  async sendSubscriptionSuccessMessage(replyToken: string): Promise<void> {
    const flexMessage = this.createSubscriptionSuccessFlexMessage();
    await this.replyMessage(replyToken, [flexMessage]);
  }

  /**
   * 發送已訂閱訊息
   * @param replyToken - LINE 提供的回覆 token
   */
  async sendSubscriptionAlreadyActiveMessage(replyToken: string): Promise<void> {
    const alreadyActiveText = `ℹ️ 您已經訂閱了每日新書通知服務！

目前訂閱狀態：✅ 已啟用

我們會在每天早上為您推送最新的書籍資訊。如需查看詳細訂閱資訊或取消訂閱，請使用下方選項。`;

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
      text: alreadyActiveText,
      quickReply
    };

    await this.replyMessage(replyToken, [textMessage]);
  }

  /**
   * 發送訂閱失敗訊息
   * @param replyToken - LINE 提供的回覆 token
   */
  async sendSubscriptionFailureMessage(replyToken: string): Promise<void> {
    const failureText = `❌ 訂閱失敗

很抱歉，系統暫時無法處理您的訂閱請求。請稍後再試，或聯繫管理員協助處理。

您仍然可以正常使用書籍查詢功能。`;

    const quickReply: line.QuickReply = {
      items: [
        {
          type: 'action',
          action: {
            type: 'message',
            label: '🔄 重新訂閱',
            text: '訂閱新書'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '🔍 搜尋書籍',
            text: '推薦一些好書'
          }
        }
      ]
    };

    const textMessage: line.TextMessage = {
      type: 'text',
      text: failureText,
      quickReply
    };

    await this.replyMessage(replyToken, [textMessage]);
  }

  /**
   * 發送取消訂閱成功訊息
   * @param replyToken - LINE 提供的回覆 token
   */
  async sendUnsubscriptionSuccessMessage(replyToken: string): Promise<void> {
    const flexMessage = this.createUnsubscriptionSuccessFlexMessage();

    // 添加 Quick Reply 讓用戶可以重新訂閱
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
    (flexMessage as any).quickReply = quickReply;

    await this.replyMessage(replyToken, [flexMessage]);
  }

  /**
   * 發送未訂閱訊息
   * @param replyToken - LINE 提供的回覆 token
   */
  async sendNotSubscribedMessage(replyToken: string): Promise<void> {
    const notSubscribedText = `ℹ️ 您目前尚未訂閱每日新書通知服務

如果您想要接收每日新書推送，請點選下方「訂閱新書通知」按鈕。

您仍然可以正常使用書籍查詢功能！`;

    const quickReply: line.QuickReply = {
      items: [
        {
          type: 'action',
          action: {
            type: 'message',
            label: '📚 訂閱新書通知',
            text: '訂閱新書'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '🔍 搜尋書籍',
            text: '推薦一些好書'
          }
        }
      ]
    };

    const textMessage: line.TextMessage = {
      type: 'text',
      text: notSubscribedText,
      quickReply
    };

    await this.replyMessage(replyToken, [textMessage]);
  }

  /**
   * 發送取消訂閱失敗訊息
   * @param replyToken - LINE 提供的回覆 token
   */
  async sendUnsubscriptionFailureMessage(replyToken: string): Promise<void> {
    const failureText = `❌ 取消訂閱失敗

很抱歉，系統暫時無法處理您的取消訂閱請求。請稍後再試，或聯繫管理員協助處理。`;

    const quickReply: line.QuickReply = {
      items: [
        {
          type: 'action',
          action: {
            type: 'message',
            label: '🔄 重新嘗試',
            text: '取消訂閱'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '📊 查看狀態',
            text: '訂閱狀態'
          }
        }
      ]
    };

    const textMessage: line.TextMessage = {
      type: 'text',
      text: failureText,
      quickReply
    };

    await this.replyMessage(replyToken, [textMessage]);
  }

  /**
   * 發送訂閱特定類型成功訊息
   * @param replyToken - LINE 提供的回覆 token
   * @param notificationType - 通知類型
   */
  async sendSubscriptionTypeSuccessMessage(
    replyToken: string,
    notificationType: 'news' | 'cancellation' | 'new_books' | 'videos'
  ): Promise<void> {
    const typeNames = {
      news: '最新消息',
      cancellation: '停課通知',
      new_books: '新書通知',
      videos: '最新課程'
    };

    const typeIcons = {
      news: '📰',
      cancellation: '⚠️',
      new_books: '📚',
      videos: '🎥'
    };

    const typeName = typeNames[notificationType];
    const typeIcon = typeIcons[notificationType];

    const successText = `✅ 訂閱成功！

您已成功訂閱 ${typeIcon} ${typeName}

我們會在有新的${typeName}時立即通知您。`;

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
            label: '📚 訂閱新書',
            text: '訂閱新書'
          }
        }
      ]
    };

    const textMessage: line.TextMessage = {
      type: 'text',
      text: successText,
      quickReply
    };

    await this.replyMessage(replyToken, [textMessage]);
  }

  /**
   * 發送已訂閱特定類型訊息
   * @param replyToken - LINE 提供的回覆 token
   * @param notificationType - 通知類型
   */
  async sendSubscriptionTypeAlreadyActiveMessage(
    replyToken: string,
    notificationType: 'news' | 'cancellation' | 'new_books' | 'videos'
  ): Promise<void> {
    const typeNames = {
      news: '最新消息',
      cancellation: '停課通知',
      new_books: '新書通知',
      videos: '最新課程'
    };

    const typeIcons = {
      news: '📰',
      cancellation: '⚠️',
      new_books: '📚',
      videos: '🎥'
    };

    const typeName = typeNames[notificationType];
    const typeIcon = typeIcons[notificationType];

    const alreadyActiveText = `ℹ️ 您已經訂閱了 ${typeIcon} ${typeName}

目前訂閱狀態：✅ 已啟用

如需查看詳細訂閱資訊或取消訂閱，請使用下方選項。`;

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
            text: `取消訂閱${typeName}`
          }
        }
      ]
    };

    const textMessage: line.TextMessage = {
      type: 'text',
      text: alreadyActiveText,
      quickReply
    };

    await this.replyMessage(replyToken, [textMessage]);
  }

  /**
   * 發送取消訂閱特定類型成功訊息
   * @param replyToken - LINE 提供的回覆 token
   * @param notificationType - 通知類型
   */
  async sendUnsubscriptionTypeSuccessMessage(
    replyToken: string,
    notificationType: 'news' | 'cancellation' | 'new_books' | 'videos'
  ): Promise<void> {
    const typeNames = {
      news: '最新消息',
      cancellation: '停課通知',
      new_books: '新書通知',
      videos: '最新課程'
    };

    const typeIcons = {
      news: '📰',
      cancellation: '⚠️',
      new_books: '📚',
      videos: '🎥'
    };

    const typeName = typeNames[notificationType];
    const typeIcon = typeIcons[notificationType];

    const successText = `✅ 取消訂閱成功

您已成功取消訂閱 ${typeIcon} ${typeName}

您仍然可以隨時重新訂閱此類型的通知。`;

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
            label: '🔄 重新訂閱',
            text: `訂閱${typeName}`
          }
        }
      ]
    };

    const textMessage: line.TextMessage = {
      type: 'text',
      text: successText,
      quickReply
    };

    await this.replyMessage(replyToken, [textMessage]);
  }

  /**
   * 發送未訂閱特定類型訊息
   * @param replyToken - LINE 提供的回覆 token
   * @param notificationType - 通知類型
   */
  async sendNotSubscribedToTypeMessage(
    replyToken: string,
    notificationType: 'news' | 'cancellation' | 'new_books' | 'videos'
  ): Promise<void> {
    const typeNames = {
      news: '最新消息',
      cancellation: '停課通知',
      new_books: '新書通知',
      videos: '最新課程'
    };

    const typeIcons = {
      news: '📰',
      cancellation: '⚠️',
      new_books: '📚',
      videos: '🎥'
    };

    const typeName = typeNames[notificationType];
    const typeIcon = typeIcons[notificationType];

    const notSubscribedText = `ℹ️ 您目前尚未訂閱 ${typeIcon} ${typeName}

如果您想要接收${typeName}，請點選下方「訂閱」按鈕。`;

    const quickReply: line.QuickReply = {
      items: [
        {
          type: 'action',
          action: {
            type: 'message',
            label: `${typeIcon} 訂閱${typeName}`,
            text: `訂閱${typeName}`
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '📊 查看訂閱狀態',
            text: '訂閱狀態'
          }
        }
      ]
    };

    const textMessage: line.TextMessage = {
      type: 'text',
      text: notSubscribedText,
      quickReply
    };

    await this.replyMessage(replyToken, [textMessage]);
  }

  /**
   * 發送訂閱狀態訊息
   * @param replyToken - LINE 提供的回覆 token
   * @param subscription - 用戶訂閱資訊
   */
  async sendSubscriptionStatusMessage(replyToken: string, subscription: UserSubscription | null): Promise<void> {
    if (!subscription) {
      await this.sendNotSubscribedMessage(replyToken);
      return;
    }

    const flexMessage = this.createSubscriptionStatusFlexMessage(subscription);

    // 總是添加 Quick Reply 讓用戶可以訂閱其他類型
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
    (flexMessage as any).quickReply = quickReply;

    await this.replyMessage(replyToken, [flexMessage]);
  }

  /**
   * 建立歡迎訊息的 Flex Message
   * @returns LINE Flex Message
   */
  private createWelcomeFlexMessage(): line.FlexMessage {
    return {
      type: 'flex',
      altText: '歡迎使用書庫查詢機器人！',
      contents: {
        type: 'bubble',
        header: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '🤖📚',
              size: '3xl',
              align: 'center'
            },
            {
              type: 'text',
              text: '書庫查詢機器人',
              weight: 'bold',
              size: 'xl',
              align: 'center',
              margin: 'sm'
            },
            {
              type: 'text',
              text: '歡迎使用！',
              size: 'md',
              align: 'center',
              color: '#666666'
            }
          ],
          backgroundColor: '#E3F2FD',
          paddingAll: 'lg'
        },
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '您可以用自然語言詢問書籍相關問題：',
              weight: 'bold',
              size: 'sm',
              wrap: true
            },
            {
              type: 'box',
              layout: 'vertical',
              contents: [
                {
                  type: 'text',
                  text: '💬 "有沒有金剛經相關的書？"',
                  size: 'sm',
                  wrap: true,
                  color: '#666666'
                },
                {
                  type: 'text',
                  text: '💬 "找一些關於程式設計的書"',
                  size: 'sm',
                  wrap: true,
                  color: '#666666',
                  margin: 'xs'
                },
                {
                  type: 'text',
                  text: '💬 "推薦幾本小說"',
                  size: 'sm',
                  wrap: true,
                  color: '#666666',
                  margin: 'xs'
                }
              ],
              margin: 'md'
            },
            {
              type: 'separator',
              margin: 'lg'
            },
            {
              type: 'box',
              layout: 'horizontal',
              contents: [
                {
                  type: 'text',
                  text: '💡',
                  size: 'lg',
                  flex: 0
                },
                {
                  type: 'text',
                  text: '您也可以訂閱每日新書通知，第一時間獲得最新書籍資訊！',
                  size: 'sm',
                  wrap: true,
                  margin: 'sm',
                  color: '#2196F3'
                }
              ],
              margin: 'lg'
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
                type: 'message',
                label: '📚 訂閱新書通知',
                text: '訂閱新書'
              },
              style: 'primary',
              color: '#2196F3'
            },
            {
              type: 'box',
              layout: 'horizontal',
              contents: [
                {
                  type: 'button',
                  action: {
                    type: 'message',
                    label: '查詢狀態',
                    text: '訂閱狀態'
                  },
                  style: 'secondary',
                  flex: 1
                },
                {
                  type: 'button',
                  action: {
                    type: 'message',
                    label: '搜尋書籍',
                    text: '推薦一些好書'
                  },
                  style: 'secondary',
                  flex: 1,
                  margin: 'sm'
                }
              ],
              margin: 'sm'
            }
          ],
          spacing: 'sm'
        }
      }
    };
  }

  /**
   * 建立訂閱成功的 Flex Message
   * @returns LINE Flex Message
   */
  private createSubscriptionSuccessFlexMessage(): line.FlexMessage {
    return {
      type: 'flex',
      altText: '訂閱成功通知',
      contents: {
        type: 'bubble',
        header: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '訂閱成功！',
              weight: 'bold',
              size: 'xl',
              color: '#27AE60',
              align: 'center'
            }
          ],
          backgroundColor: '#E8F5E8',
          paddingAll: 'lg'
        },
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '🎉 恭喜您成功訂閱每日新書通知！',
              weight: 'bold',
              size: 'md',
              wrap: true,
              margin: 'none'
            },
            {
              type: 'separator',
              margin: 'lg'
            },
            {
              type: 'box',
              layout: 'vertical',
              contents: [
                {
                  type: 'text',
                  text: '您將會收到：',
                  weight: 'bold',
                  size: 'sm',
                  color: '#666666',
                  margin: 'lg'
                },
                {
                  type: 'box',
                  layout: 'vertical',
                  contents: [
                    {
                      type: 'box',
                      layout: 'horizontal',
                      contents: [
                        {
                          type: 'text',
                          text: '📖',
                          size: 'sm',
                          flex: 0
                        },
                        {
                          type: 'text',
                          text: '新書標題和作者資訊',
                          size: 'sm',
                          wrap: true,
                          margin: 'sm'
                        }
                      ]
                    },
                    {
                      type: 'box',
                      layout: 'horizontal',
                      contents: [
                        {
                          type: 'text',
                          text: '📝',
                          size: 'sm',
                          flex: 0
                        },
                        {
                          type: 'text',
                          text: 'AI 生成的內容摘要',
                          size: 'sm',
                          wrap: true,
                          margin: 'sm'
                        }
                      ],
                      margin: 'sm'
                    },
                    {
                      type: 'box',
                      layout: 'horizontal',
                      contents: [
                        {
                          type: 'text',
                          text: '🔗',
                          size: 'sm',
                          flex: 0
                        },
                        {
                          type: 'text',
                          text: '書籍相關連結',
                          size: 'sm',
                          wrap: true,
                          margin: 'sm'
                        }
                      ],
                      margin: 'sm'
                    }
                  ],
                  margin: 'sm'
                }
              ]
            },
            {
              type: 'separator',
              margin: 'lg'
            },
            {
              type: 'text',
              text: '⏰ 通知時間：每天早上 8:00',
              size: 'sm',
              color: '#666666',
              margin: 'lg',
              align: 'center'
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
                type: 'message',
                label: '查看訂閱狀態',
                text: '訂閱狀態'
              },
              style: 'primary',
              color: '#27AE60'
            },
            {
              type: 'button',
              action: {
                type: 'message',
                label: '搜尋書籍',
                text: '推薦一些好書'
              },
              style: 'secondary',
              margin: 'sm'
            }
          ],
          spacing: 'sm'
        }
      }
    };
  }

  /**
   * 建立訂閱狀態的 Flex Message
   * @param subscription 用戶訂閱資訊
   * @returns LINE Flex Message
   */
  private createSubscriptionStatusFlexMessage(subscription: UserSubscription): line.FlexMessage {
    const statusColor = subscription.isSubscribed ? '#27AE60' : '#E74C3C';
    const statusText = subscription.isSubscribed ? '已啟用' : '已停用';
    const statusIcon = subscription.isSubscribed ? '✅' : '❌';

    const lastNotificationText = subscription.lastNotificationSent
      ? subscription.lastNotificationSent.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
      : '尚未發送';

    const subscriptionDate = subscription.subscriptionDate.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });

    // 訂閱類型顯示
    const typeIcons: Record<string, string> = {
      new_books: '📚',
      news: '📰',
      cancellation: '⚠️'
    };

    const typeNames: Record<string, string> = {
      new_books: '新書通知',
      news: '最新消息',
      cancellation: '停課通知'
    };

    const subscribedTypes = subscription.notificationTypes.map(type =>
      `${typeIcons[type] || '📌'} ${typeNames[type] || type}`
    );

    return {
      type: 'flex',
      altText: '訂閱狀態資訊',
      contents: {
        type: 'bubble',
        header: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '📊 訂閱狀態',
              weight: 'bold',
              size: 'xl',
              align: 'center'
            }
          ],
          backgroundColor: '#F8F9FA',
          paddingAll: 'lg'
        },
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'box',
              layout: 'horizontal',
              contents: [
                {
                  type: 'text',
                  text: statusIcon,
                  size: 'xl',
                  flex: 0
                },
                {
                  type: 'box',
                  layout: 'vertical',
                  contents: [
                    {
                      type: 'text',
                      text: '目前狀態',
                      size: 'sm',
                      color: '#666666'
                    },
                    {
                      type: 'text',
                      text: statusText,
                      weight: 'bold',
                      size: 'lg',
                      color: statusColor
                    }
                  ],
                  margin: 'sm'
                }
              ]
            },
            {
              type: 'separator',
              margin: 'lg'
            },
            {
              type: 'box',
              layout: 'vertical',
              contents: [
                {
                  type: 'box',
                  layout: 'horizontal',
                  contents: [
                    {
                      type: 'text',
                      text: '📅 訂閱日期',
                      size: 'sm',
                      color: '#666666',
                      flex: 2
                    },
                    {
                      type: 'text',
                      text: subscriptionDate,
                      size: 'sm',
                      align: 'end',
                      flex: 2
                    }
                  ]
                },
                {
                  type: 'box',
                  layout: 'horizontal',
                  contents: [
                    {
                      type: 'text',
                      text: '📬 上次通知',
                      size: 'sm',
                      color: '#666666',
                      flex: 2
                    },
                    {
                      type: 'text',
                      text: lastNotificationText,
                      size: 'sm',
                      align: 'end',
                      flex: 2
                    }
                  ],
                  margin: 'md'
                }
              ],
              margin: 'lg'
            },
            {
              type: 'separator',
              margin: 'lg'
            },
            {
              type: 'box',
              layout: 'vertical',
              contents: [
                {
                  type: 'text',
                  text: '📋 訂閱類型',
                  weight: 'bold',
                  size: 'sm',
                  color: '#666666'
                },
                {
                  type: 'box',
                  layout: 'vertical',
                  contents: subscribedTypes.length > 0 ? subscribedTypes.map((typeText, index) => ({
                    type: 'text' as const,
                    text: typeText,
                    size: 'sm' as const,
                    margin: index === 0 ? 'sm' as const : 'xs' as const
                  })) : [
                    {
                      type: 'text' as const,
                      text: '尚未訂閱任何類型',
                      size: 'sm' as const,
                      color: '#999999',
                      margin: 'sm' as const
                    }
                  ],
                  margin: 'sm'
                }
              ],
              margin: 'lg'
            },
            {
              type: 'separator',
              margin: 'lg'
            },
            {
              type: 'box',
              layout: 'vertical',
              contents: [
                {
                  type: 'text',
                  text: '⚙️ 通知設定',
                  weight: 'bold',
                  size: 'sm',
                  color: '#666666'
                },
                {
                  type: 'box',
                  layout: 'vertical',
                  contents: [
                    {
                      type: 'box',
                      layout: 'horizontal',
                      contents: [
                        {
                          type: 'text',
                          text: subscription.notificationPreferences.enableSummary ? '✅' : '❌',
                          size: 'sm',
                          flex: 0
                        },
                        {
                          type: 'text',
                          text: '包含內容摘要',
                          size: 'sm',
                          margin: 'sm'
                        }
                      ]
                    },
                    {
                      type: 'box',
                      layout: 'horizontal',
                      contents: [
                        {
                          type: 'text',
                          text: subscription.notificationPreferences.enableDownloadLink ? '✅' : '❌',
                          size: 'sm',
                          flex: 0
                        },
                        {
                          type: 'text',
                          text: '包含下載連結',
                          size: 'sm',
                          margin: 'sm'
                        }
                      ],
                      margin: 'sm'
                    },
                    {
                      type: 'box',
                      layout: 'horizontal',
                      contents: [
                        {
                          type: 'text',
                          text: '📚',
                          size: 'sm',
                          flex: 0
                        },
                        {
                          type: 'text',
                          text: `每次最多 ${subscription.notificationPreferences.maxBooksPerNotification} 本書`,
                          size: 'sm',
                          margin: 'sm'
                        }
                      ],
                      margin: 'sm'
                    }
                  ],
                  margin: 'sm'
                }
              ],
              margin: 'lg'
            }
          ],
          spacing: 'sm'
        },
        footer: {
          type: 'box',
          layout: 'vertical',
          contents: subscription.isSubscribed ? [
            {
              type: 'button',
              action: {
                type: 'message',
                label: '取消訂閱',
                text: '取消訂閱'
              },
              style: 'secondary',
              color: '#E74C3C'
            }
          ] : [
            {
              type: 'button',
              action: {
                type: 'message',
                label: '重新訂閱',
                text: '重新訂閱'
              },
              style: 'primary',
              color: '#27AE60'
            }
          ],
          spacing: 'sm'
        }
      }
    };
  }

  /**
   * 發送最新消息 Flex Carousel 訊息（帶 Quick Reply）
   * @param replyToken - LINE 提供的回覆 token
   * @param bulletins - 最新消息陣列
   * @param courseCancellations - 停課公告陣列
   */
  async sendBulletinsCarousel(replyToken: string, bulletins: any[], courseCancellations: any[] = []): Promise<void> {
    const flexMessage = this.createBulletinsCarouselFlexMessage(bulletins, courseCancellations);

    // 添加 Quick Reply 按鈕（使用全形字符放大）
    const quickReply: line.QuickReply = {
      items: [
        {
          type: 'action',
          action: {
            type: 'message',
            label: '📰　訂閱最新消息',  // 使用全形空格增加視覺效果
            text: '訂閱最新消息'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '⚠️　訂閱停課通知',
            text: '訂閱停課通知'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '📚　訂閱新書通知',
            text: '訂閱新書通知'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '✅　全部訂閱',
            text: '全部訂閱'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '📊　訂閱狀態查詢',
            text: '訂閱狀態'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '❌　取消訂閱',
            text: '取消訂閱'
          }
        }
      ]
    };

    // 將 Quick Reply 附加到 Flex Message
    (flexMessage as any).quickReply = quickReply;

    await this.replyMessage(replyToken, [flexMessage]);
  }

  /**
   * 建立最新消息 Carousel 的 Flex Message
   * @param bulletins 最新消息陣列
   * @param courseCancellations 停課公告陣列
   * @returns LINE Flex Message
   */
  private createBulletinsCarouselFlexMessage(bulletins: any[], courseCancellations: any[] = []): line.FlexMessage {
    // 建立停課公告卡片（第一張）
    let courseCancelContent = '目前沒有停課公告';

    if (courseCancellations.length > 0) {
      courseCancelContent = courseCancellations.map((cancel: any) => {
        const date = new Date(cancel.cancelDate).toLocaleDateString('zh-TW', {
          month: '2-digit',
          day: '2-digit'
        });
        return `${date} ${cancel.courseTitle}`;
      }).join('\n');

      // 限制長度
      if (courseCancelContent.length > 100) {
        courseCancelContent = courseCancelContent.substring(0, 97) + '...';
      }
    }

    const courseCancelBubble = {
      type: 'bubble' as const,
      hero: {
        type: 'box' as const,
        layout: 'vertical' as const,
        contents: [
          {
            type: 'text' as const,
            text: '⚠️',
            size: '3xl' as const,
            align: 'center' as const
          }
        ],
        backgroundColor: '#FFF3E0',
        paddingAll: 'md' as const
      },
      body: {
        type: 'box' as const,
        layout: 'vertical' as const,
        contents: [
          {
            type: 'text' as const,
            text: '停課公告',
            weight: 'bold' as const,
            size: 'xl' as const,
            wrap: true
          },
          {
            type: 'separator' as const,
            margin: 'md' as const
          },
          {
            type: 'text' as const,
            text: courseCancelContent,
            size: 'lg' as const,
            wrap: true,
            color: '#666666',
            margin: 'md' as const
          }
        ],
        spacing: 'sm' as const
      },
      footer: {
        type: 'box' as const,
        layout: 'vertical' as const,
        contents: [
          {
            type: 'button' as const,
            action: {
              type: 'uri' as const,
              label: '查看完整停課公告',
              uri: 'https://www.budaedu.org/#/bulletins/course-cancel'
            },
            style: 'primary' as const,
            color: '#FF9800'
          }
        ]
      }
    };

    // 限制最多 9 則消息（加上停課公告共 10 張，LINE Carousel 限制）
    const limitedBulletins = bulletins.slice(0, 9);

    const bulletinBubbles = limitedBulletins.map(bulletin => ({
      type: 'bubble' as const,
      hero: {
        type: 'box' as const,
        layout: 'vertical' as const,
        contents: [
          {
            type: 'text' as const,
            text: '📰',
            size: '3xl' as const,
            align: 'center' as const
          }
        ],
        backgroundColor: '#E3F2FD',
        paddingAll: 'md' as const
      },
      body: {
        type: 'box' as const,
        layout: 'vertical' as const,
        contents: [
          {
            type: 'text' as const,
            text: bulletin.title.length > 60 ? bulletin.title.substring(0, 57) + '...' : bulletin.title,
            weight: 'bold' as const,
            size: 'xl' as const,  // 加大 2 號（原 md → xl）
            wrap: true
          },
          {
            type: 'separator' as const,
            margin: 'md' as const
          },
          {
            type: 'text' as const,
            text: bulletin.content.length > 100 ? bulletin.content.substring(0, 97) + '...' : bulletin.content,
            size: 'lg' as const,  // 加大 2 號（原 sm → lg）
            wrap: true,
            color: '#666666',
            margin: 'md' as const
          },
          {
            type: 'box' as const,
            layout: 'vertical' as const,
            contents: [
              {
                type: 'text' as const,
                text: `📅 ${bulletin.publishStartDate}`,
                size: 'sm' as const,  // 加大 2 號（原 xs → sm）
                color: '#999999'
              }
            ],
            margin: 'md' as const
          }
        ],
        spacing: 'sm' as const
      },
      footer: {
        type: 'box' as const,
        layout: 'vertical' as const,
        contents: [
          {
            type: 'button' as const,
            action: {
              type: 'uri' as const,
              label: '查看完整內容',
              uri: bulletin.url
            },
            style: 'primary' as const,
            color: '#2196F3'
          }
        ]
      }
    }));

    // 將停課公告放在第一張
    const allBubbles = [courseCancelBubble, ...bulletinBubbles];

    return {
      type: 'flex',
      altText: '最新消息',
      contents: {
        type: 'carousel',
        contents: allBubbles
      }
    };
  }

  /**
   * 建立取消訂閱成功的 Flex Message
   * @returns LINE Flex Message
   */
  private createUnsubscriptionSuccessFlexMessage(): line.FlexMessage {
    return {
      type: 'flex',
      altText: '取消訂閱成功',
      contents: {
        type: 'bubble',
        header: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '取消訂閱成功',
              weight: 'bold',
              size: 'xl',
              color: '#E74C3C',
              align: 'center'
            }
          ],
          backgroundColor: '#FDEDEC',
          paddingAll: 'lg'
        },
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '✅ 您已成功取消每日新書通知服務',
              weight: 'bold',
              size: 'md',
              wrap: true,
              align: 'center'
            },
            {
              type: 'separator',
              margin: 'lg'
            },
            {
              type: 'box',
              layout: 'vertical',
              contents: [
                {
                  type: 'text',
                  text: '您仍然可以：',
                  weight: 'bold',
                  size: 'sm',
                  color: '#666666'
                },
                {
                  type: 'box',
                  layout: 'vertical',
                  contents: [
                    {
                      type: 'box',
                      layout: 'horizontal',
                      contents: [
                        {
                          type: 'text',
                          text: '🔍',
                          size: 'sm',
                          flex: 0
                        },
                        {
                          type: 'text',
                          text: '使用書籍查詢功能',
                          size: 'sm',
                          wrap: true,
                          margin: 'sm'
                        }
                      ]
                    },
                    {
                      type: 'box',
                      layout: 'horizontal',
                      contents: [
                        {
                          type: 'text',
                          text: '🔄',
                          size: 'sm',
                          flex: 0
                        },
                        {
                          type: 'text',
                          text: '隨時重新訂閱通知服務',
                          size: 'sm',
                          wrap: true,
                          margin: 'sm'
                        }
                      ],
                      margin: 'sm'
                    }
                  ],
                  margin: 'sm'
                }
              ],
              margin: 'lg'
            },
            {
              type: 'separator',
              margin: 'lg'
            },
            {
              type: 'text',
              text: '感謝您的使用！🙏',
              size: 'md',
              align: 'center',
              color: '#666666',
              margin: 'lg'
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
                type: 'message',
                label: '重新訂閱',
                text: '訂閱新書'
              },
              style: 'primary',
              color: '#27AE60'
            },
            {
              type: 'button',
              action: {
                type: 'message',
                label: '搜尋書籍',
                text: '推薦一些好書'
              },
              style: 'secondary',
              margin: 'sm'
            }
          ],
          spacing: 'sm'
        }
      }
    };
  }

  /**
   * 發送訂閱類型輪播訊息
   * @param replyToken - LINE 提供的回覆 token
   */
  async sendSubscriptionCarousel(replyToken: string): Promise<void> {
    const carouselMessage = subscriptionCarouselTemplate.createSubscriptionCarousel();
    await this.replyMessage(replyToken, [carouselMessage]);
  }
}

// 建立單例實例
export const lineMessagingService = new LineMessagingService();

// 預設匯出
export default lineMessagingService;