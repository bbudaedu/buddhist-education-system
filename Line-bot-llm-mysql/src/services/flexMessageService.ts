import { FlexMessage, FlexBubble, FlexCarousel } from '@line/bot-sdk';

/**
 * Flex Message Service
 * 用於創建 LINE Flex Message 格式的通知
 */

export interface BookNotification {
  title: string;
  author: string;
  pdfUrls?: string[];
}

export interface NewsNotification {
  title: string;
  date: string;
  url?: string;
  content?: string;
}

export interface CancellationNotification {
  courseName: string;
  date: string;
  instructor: string;
  location?: string;
}

export class FlexMessageService {
  /**
   * 創建新書通知 Flex Carousel
   */
  createNewBooksCarousel(books: BookNotification[]): FlexMessage {
    const bubbles: FlexBubble[] = books.map((book) => {
      const bubble: FlexBubble = {
        type: 'bubble',
        size: 'kilo',
        hero: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '📚',
              size: '4xl',
              align: 'center',
              color: '#ffffff'
            }
          ],
          backgroundColor: '#4A90E2',
          paddingAll: 'md'
        },
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: book.title,
              weight: 'bold',
              size: 'lg',
              wrap: true,
              maxLines: 3
            },
            {
              type: 'box',
              layout: 'baseline',
              margin: 'md',
              contents: [
                {
                  type: 'icon',
                  url: 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_sm.png',
                  size: 'sm'
                },
                {
                  type: 'text',
                  text: book.author,
                  size: 'sm',
                  color: '#999999',
                  margin: 'md',
                  flex: 0,
                  wrap: true
                }
              ]
            }
          ]
        }
      };

      // 只在有 PDF URLs 時添加 footer（使用 button 元件）
      if (book.pdfUrls && book.pdfUrls.length > 0) {
        const buttons = book.pdfUrls.slice(0, 3).map((pdfUrl, pdfIndex) => {
          const label = book.pdfUrls!.length > 1 
            ? `閱讀 PDF ${pdfIndex + 1}` 
            : '閱讀 PDF';
          
          return {
            type: 'button' as const,
            action: {
              type: 'uri' as const,
              label: label,
              uri: `${pdfUrl}?openExternalBrowser=1`
            },
            style: 'link' as const,
            height: 'sm' as const
          };
        });

        bubble.footer = {
          type: 'box',
          layout: 'vertical',
          spacing: 'sm',
          contents: buttons,
          flex: 0
        };
      }

      return bubble;
    });

    return {
      type: 'flex',
      altText: `📚 新書上架通知 (${books.length} 本)`,
      contents: {
        type: 'carousel',
        contents: bubbles
      }
    };
  }

  /**
   * 創建新聞公告 Flex Carousel
   */
  createNewsCarousel(newsItems: NewsNotification[]): FlexMessage {
    const bubbles: FlexBubble[] = newsItems.map((news) => {
      const bubble: FlexBubble = {
        type: 'bubble',
        size: 'kilo',
        hero: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '📰',
              size: '4xl',
              align: 'center',
              color: '#ffffff'
            }
          ],
          backgroundColor: '#E67E22',
          paddingAll: 'md'
        },
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: news.title,
              weight: 'bold',
              size: 'md',
              wrap: true,
              maxLines: 3
            },
            {
              type: 'box',
              layout: 'baseline',
              margin: 'md',
              contents: [
                {
                  type: 'icon',
                  url: 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_sm.png',
                  size: 'sm'
                },
                {
                  type: 'text',
                  text: news.date,
                  size: 'xs',
                  color: '#999999',
                  margin: 'md',
                  flex: 0
                }
              ]
            },
            ...(news.content ? [{
              type: 'text' as const,
              text: news.content.substring(0, 100) + (news.content.length > 100 ? '...' : ''),
              size: 'xs' as const,
              color: '#666666',
              margin: 'md' as const,
              wrap: true
            }] : [])
          ]
        }
      };

      // 只在有 URL 時添加 footer（使用 button 元件）
      if (news.url) {
        bubble.footer = {
          type: 'box',
          layout: 'vertical',
          spacing: 'sm',
          contents: [
            {
              type: 'button',
              action: {
                type: 'uri',
                label: '查看詳情',
                uri: `${news.url}?openExternalBrowser=1`
              },
              style: 'link',
              height: 'sm'
            }
          ],
          flex: 0
        };
      }

      return bubble;
    });

    return {
      type: 'flex',
      altText: `📰 新聞公告 (${newsItems.length} 則)`,
      contents: {
        type: 'carousel',
        contents: bubbles
      }
    };
  }

  /**
   * 創建停課通知 Flex Carousel
   */
  createCancellationCarousel(cancellations: CancellationNotification[]): FlexMessage {
    const bubbles: FlexBubble[] = cancellations.map((cancellation) => {
      return {
        type: 'bubble',
        size: 'kilo',
        hero: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '🚫',
              size: '4xl',
              align: 'center',
              color: '#ffffff'
            }
          ],
          backgroundColor: '#E74C3C',
          paddingAll: 'md'
        },
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: cancellation.courseName,
              weight: 'bold',
              size: 'md',
              wrap: true,
              maxLines: 2
            },
            {
              type: 'box',
              layout: 'vertical',
              margin: 'lg',
              spacing: 'sm',
              contents: [
                {
                  type: 'box',
                  layout: 'baseline',
                  spacing: 'sm',
                  contents: [
                    {
                      type: 'text',
                      text: '日期',
                      color: '#aaaaaa',
                      size: 'sm',
                      flex: 1
                    },
                    {
                      type: 'text',
                      text: cancellation.date,
                      wrap: true,
                      color: '#666666',
                      size: 'sm',
                      flex: 3
                    }
                  ]
                },
                {
                  type: 'box',
                  layout: 'baseline',
                  spacing: 'sm',
                  contents: [
                    {
                      type: 'text',
                      text: '講師',
                      color: '#aaaaaa',
                      size: 'sm',
                      flex: 1
                    },
                    {
                      type: 'text',
                      text: cancellation.instructor,
                      wrap: true,
                      color: '#666666',
                      size: 'sm',
                      flex: 3
                    }
                  ]
                },
                ...(cancellation.location ? [{
                  type: 'box' as const,
                  layout: 'baseline' as const,
                  spacing: 'sm' as const,
                  contents: [
                    {
                      type: 'text' as const,
                      text: '地點',
                      color: '#aaaaaa',
                      size: 'sm' as const,
                      flex: 1
                    },
                    {
                      type: 'text' as const,
                      text: cancellation.location,
                      wrap: true,
                      color: '#666666',
                      size: 'sm' as const,
                      flex: 3
                    }
                  ]
                }] : [])
              ]
            }
          ]
        }
      };
    });

    return {
      type: 'flex',
      altText: `🚫 停課通知 (${cancellations.length} 則)`,
      contents: {
        type: 'carousel',
        contents: bubbles
      }
    };
  }

  /**
   * 創建整合通知 Flex Message
   * 當用戶訂閱多種類型時，整合成一則訊息
   */
  createIntegratedNotification(data: {
    newBooks?: BookNotification[];
    news?: NewsNotification[];
    cancellations?: CancellationNotification[];
  }): FlexMessage {
    const bubbles: FlexBubble[] = [];

    // 1. 摘要 Bubble
    const summaryContents: any[] = [
      {
        type: 'text',
        text: '最新訊息',
        weight: 'bold',
        size: 'xl',
        color: '#ffffff'
      }
    ];

    const summaryItems: any[] = [];

    if (data.newBooks && data.newBooks.length > 0) {
      summaryItems.push({
        type: 'box',
        layout: 'baseline',
        spacing: 'sm',
        contents: [
          {
            type: 'text',
            text: '📚',
            size: 'lg',
            flex: 0
          },
          {
            type: 'text',
            text: `新書上架 ${data.newBooks.length} 本`,
            size: 'sm',
            color: '#ffffff',
            margin: 'md'
          }
        ]
      });
    }

    if (data.news && data.news.length > 0) {
      summaryItems.push({
        type: 'box',
        layout: 'baseline',
        spacing: 'sm',
        contents: [
          {
            type: 'text',
            text: '📰',
            size: 'lg',
            flex: 0
          },
          {
            type: 'text',
            text: `新聞公告 ${data.news.length} 則`,
            size: 'sm',
            color: '#ffffff',
            margin: 'md'
          }
        ]
      });
    }

    if (data.cancellations && data.cancellations.length > 0) {
      summaryItems.push({
        type: 'box',
        layout: 'baseline',
        spacing: 'sm',
        contents: [
          {
            type: 'text',
            text: '🚫',
            size: 'lg',
            flex: 0
          },
          {
            type: 'text',
            text: `停課通知 ${data.cancellations.length} 則`,
            size: 'sm',
            color: '#ffffff',
            margin: 'md'
          }
        ]
      });
    }

    const summaryBubble: FlexBubble = {
      type: 'bubble',
      size: 'kilo',
      hero: {
        type: 'box',
        layout: 'vertical',
        contents: [
          ...summaryContents,
          {
            type: 'box',
            layout: 'vertical',
            margin: 'lg',
            spacing: 'sm',
            contents: summaryItems
          }
        ],
        backgroundColor: '#27AE60',
        paddingAll: 'xl'
      },
      body: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'text',
            text: '向右滑動查看詳細內容 →',
            size: 'xs',
            color: '#999999',
            align: 'center'
          }
        ]
      }
    };

    bubbles.push(summaryBubble);

    // 2. 新書 Bubbles
    if (data.newBooks && data.newBooks.length > 0) {
      const newBooksBubbles = this.createNewBooksCarousel(data.newBooks).contents as FlexCarousel;
      bubbles.push(...newBooksBubbles.contents);
    }

    // 3. 新聞 Bubbles
    if (data.news && data.news.length > 0) {
      const newsBubbles = this.createNewsCarousel(data.news).contents as FlexCarousel;
      bubbles.push(...newsBubbles.contents);
    }

    // 4. 停課 Bubbles
    if (data.cancellations && data.cancellations.length > 0) {
      const cancellationBubbles = this.createCancellationCarousel(data.cancellations).contents as FlexCarousel;
      bubbles.push(...cancellationBubbles.contents);
    }

    return {
      type: 'flex',
      altText: '📢 佛教教育網站最新訊息',
      contents: {
        type: 'carousel',
        contents: bubbles
      }
    };
  }
}

export const flexMessageService = new FlexMessageService();
