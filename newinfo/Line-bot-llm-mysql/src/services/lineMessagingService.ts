import * as line from '@line/bot-sdk';
import { lineConfig } from '../config/index';
import { Book } from '../types/book';
import { UserSubscription } from '../types/subscription';

/**
 * LINE Messaging Service
 * 負責透過 LINE Messaging API 發送訊息給用戶
 */
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
    } catch (error) {
      console.error('Failed to reply message:', error);
      throw new Error('LINE API 回覆失敗');
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
                          text: 'PDF 下載連結',
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
            },
            {
              type: 'button',
              action: {
                type: 'message',
                label: '搜尋書籍',
                text: '推薦一些好書'
              },
              style: 'primary',
              margin: 'sm'
            }
          ] : [
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
}

// 建立單例實例
export const lineMessagingService = new LineMessagingService();

// 預設匯出
export default lineMessagingService;