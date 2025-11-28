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
   * 創建法寶圖書 Flex Carousel
   * @param books 法寶圖書列表
   * @returns FlexMessage
   */
  createDharmaBookCarousel(books: Array<{
    id?: string;
    code?: string;
    title: string;
    author?: string;
    description?: string;
    publishDate?: string | undefined;
    coverImageUrl?: string | undefined;
    pdfUrl?: string | undefined;
    fileSize?: string | undefined;
  }>): FlexMessage {
    const bubbles: FlexBubble[] = books.map(book => {
      const bubble: FlexBubble = {
        type: 'bubble',
        size: 'kilo',
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            // Top section: horizontal layout with image and basic info
            {
              type: 'box',
              layout: 'horizontal',
              contents: [
                // Left: Small cover image
                {
                  type: 'box',
                  layout: 'vertical',
                  contents: [
                    {
                      type: 'image',
                      url: book.coverImageUrl || 'https://www.budaedu.org/img/logo.png',
                      size: 'sm',
                      aspectRatio: '3:4',
                      aspectMode: 'cover',
                      backgroundColor: '#f0f0f0'
                    }
                  ],
                  flex: 0,
                  width: '80px'
                },
                // Right: Book basic info (title, author, code)
                {
                  type: 'box',
                  layout: 'vertical',
                  contents: [
                    {
                      type: 'text',
                      text: book.title,
                      weight: 'bold',
                      size: 'xl',
                      wrap: true,
                      maxLines: 2,
                      color: '#333333'
                    },
                    ...(book.code ? [{
                      type: 'text' as const,
                      text: `編號: ${book.code}`,
                      size: 'md' as const,
                      color: '#666666',
                      margin: 'sm' as const
                    }] : []),
                    {
                      type: 'text',
                      text: book.author || '佛陀教育基金會',
                      size: 'md',
                      color: '#666666',
                      margin: 'xs'
                    }
                  ],
                  flex: 1,
                  margin: 'md'
                }
              ]
            },
            // Bottom section: full-width description
            ...(book.description ? [{
              type: 'box' as const,
              layout: 'vertical' as const,
              contents: [
                {
                  type: 'text' as const,
                  text: book.description,
                  size: 'md' as const,
                  color: '#999999',
                  wrap: true,
                  maxLines: 5
                }
              ],
              margin: 'md' as const
            }] : [])
          ]
        },
        footer: {
          type: 'box',
          layout: 'vertical',
          spacing: 'sm',
          contents: [
            // First row: horizontal 2 buttons
            {
              type: 'box',
              layout: 'horizontal',
              spacing: 'sm',
              contents: [
                {
                  type: 'button',
                  action: {
                    type: 'uri',
                    label: '查看詳情',
                    uri: 'https://www.budaedu.org/#/books/applicable/chinese?openExternalBrowser=1'
                  },
                  style: 'primary',
                  height: 'sm',
                  flex: 1
                },
                {
                  type: 'button',
                  action: {
                    type: 'uri',
                    label: '書籍申請',
                    uri: 'https://www.budaedu.org/#/books/applicable/chinese?openExternalBrowser=1'
                  },
                  style: 'primary',
                  height: 'sm',
                  flex: 1
                }
              ]
            },
            // Second row: PDF button (if exists)
            ...(book.pdfUrl ? [{
              type: 'button' as const,
              action: {
                type: 'uri' as const,
                label: book.fileSize ? `📖 閱讀 PDF (${book.fileSize})` : '📖 閱讀 PDF',
                uri: (() => {
                  const encodedUrl = encodeURI(book.pdfUrl);
                  return encodedUrl.includes('openExternalBrowser=1')
                    ? encodedUrl
                    : `${encodedUrl}${encodedUrl.includes('?') ? '&' : '?'}openExternalBrowser=1`;
                })()
              },
              style: 'link' as const,
              height: 'sm' as const
            }] : []),
            // Third row: More button
            {
              type: 'button',
              action: {
                type: 'uri',
                label: '更多法寶',
                uri: 'https://www.budaedu.org/#/books/applicable/chinese?openExternalBrowser=1'
              },
              style: 'link',
              height: 'sm'
            }
          ]
        }
      };
      return bubble;
    });

    // Add "View All" bubble at the end
    const viewAllBubble: FlexBubble = {
      type: 'bubble',
      size: 'kilo',
      body: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'text',
            text: '📚',
            size: '5xl',
            align: 'center',
            color: '#4A90E2'
          },
          {
            type: 'text',
            text: '查看更多法寶',
            weight: 'bold',
            size: 'xl',
            align: 'center',
            margin: 'md',
            color: '#333333'
          },
          {
            type: 'text',
            text: '瀏覽完整法寶目錄',
            size: 'sm',
            align: 'center',
            margin: 'sm',
            color: '#999999'
          }
        ],
        justifyContent: 'center',
        height: '300px'
      },
      footer: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'button',
            style: 'primary',
            action: {
              type: 'uri',
              label: '前往網站',
              uri: 'https://www.budaedu.org/#/books/applicable/chinese?openExternalBrowser=1'
            }
          }
        ]
      }
    };

    bubbles.push(viewAllBubble);

    return {
      type: 'flex',
      altText: `${books.length} 本最新法寶`,
      contents: {
        type: 'carousel',
        contents: bubbles
      }
    };
  }
  /**
   * 創建影音/直播 Flex Carousel
   * @param streams 影音/直播列表
   * @returns FlexMessage
   */
  createVideoStreamingCarousel(streams: Array<{
    title: string;
    instructor?: string | undefined;
    startDate?: string | undefined;
    thumbnailUrl?: string | undefined;
    eventUrl?: string | undefined;
    isLive: boolean;
  }>): FlexMessage {
    const bubbles: FlexBubble[] = streams.map(stream => {
      const bubble: FlexBubble = {
        type: 'bubble',
        size: 'kilo',
        hero: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'image',
              url: stream.thumbnailUrl || stream.instructor
                ? `https://via.placeholder.com/300x200?text=${encodeURIComponent(stream.instructor || 'Instructor')}`
                : 'https://via.placeholder.com/300x200?text=Video',
              size: 'full',
              aspectRatio: '3:2',
              aspectMode: 'cover'
            },
            {
              type: 'box',
              layout: 'vertical',
              contents: [
                {
                  type: 'text',
                  text: stream.isLive ? '🔴 直播中' : '📹 錄影',
                  color: '#ffffff',
                  size: 'xs',
                  weight: 'bold'
                }
              ],
              position: 'absolute',
              offsetTop: '10px',
              offsetStart: '10px',
              paddingAll: '5px',
              backgroundColor: stream.isLive ? '#ff0000' : '#1e90ff',
              cornerRadius: '5px'
            }
          ]
        },
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: stream.title,
              weight: 'bold',
              size: 'lg',
              wrap: true,
              maxLines: 2
            },
            {
              type: 'box',
              layout: 'vertical',
              margin: 'md',
              spacing: 'sm',
              contents: [
                ...(stream.instructor ? [{
                  type: 'box' as const,
                  layout: 'baseline' as const,
                  contents: [
                    {
                      type: 'text' as const,
                      text: '講師:',
                      size: 'sm' as const,
                      color: '#aaaaaa',
                      flex: 0
                    },
                    {
                      type: 'text' as const,
                      text: stream.instructor,
                      size: 'sm' as const,
                      color: '#666666',
                      wrap: true,
                      flex: 1
                    }
                  ]
                }] : []),
                ...(stream.startDate ? [{
                  type: 'box' as const,
                  layout: 'baseline' as const,
                  contents: [
                    {
                      type: 'text' as const,
                      text: '時間:',
                      size: 'sm' as const,
                      color: '#aaaaaa',
                      flex: 0
                    },
                    {
                      type: 'text' as const,
                      text: stream.startDate,
                      size: 'sm' as const,
                      color: '#666666',
                      flex: 1
                    }
                  ]
                }] : [])
              ]
            }
          ]
        }
      };

      // Add footer only if eventUrl exists
      if (stream.eventUrl) {
        bubble.footer = {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'button',
              style: 'primary',
              action: {
                type: 'uri',
                label: stream.isLive ? '🎥 觀看直播' : '📺 觀看影片',
                uri: stream.eventUrl
              }
            }
          ]
        };
      }

      return bubble;
    });
    return {
      type: 'flex',
      altText: `${streams.length} 則最新影音`,
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
