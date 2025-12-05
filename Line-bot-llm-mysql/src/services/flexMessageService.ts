import { FlexMessage, FlexBubble } from '@line/bot-sdk';

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
   * 創建單個書籍 Bubble
   */
  createBookBubble(book: {
    id?: string;
    code?: string;
    title: string;
    author?: string;
    description?: string;
    publishDate?: string | undefined;
    coverImageUrl?: string | undefined;
    pdfUrl?: string | undefined;
    fileSize?: string | undefined;
  }): FlexBubble {
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
                  uri: `https://www.budaedu.org/#/books/${book.id}?openExternalBrowser=1`
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
                  uri: `https://www.budaedu.org/#/books/${book.id}?openExternalBrowser=1`
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
                const encodedUrl = encodeURI(book.pdfUrl!);
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
          },
          // Fourth row: Share button
          {
            type: 'button',
            action: {
              type: 'uri',
              label: '📤 分享給朋友',
              uri: (() => {
                const shareText = `📚 ${book.title}\n作者：${book.author || '佛陀教育基金會'}\n\n查看詳情：https://www.budaedu.org/#/books/${book.id}`;
                return `https://line.me/R/share?text=${encodeURIComponent(shareText)}`;
              })()
            },
            style: 'link',
            height: 'sm',
            color: '#17c950'
          }
        ]
      }
    };
    return bubble;
  }

  /**
   * 創建佛卡 Bubble
   */
  createBuddhaCardBubble(card: {
    id: string;
    code: string;
    title: string;
    imageUrl: string;
    updatedAt: string;
  }): FlexBubble {
    return {
      type: 'bubble',
      size: 'kilo',
      body: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'image',
            url: card.imageUrl,
            size: 'full',
            aspectRatio: '1:1',
            aspectMode: 'cover',
            action: {
              type: 'uri',
              label: '查看圖片',
              uri: card.imageUrl
            }
          },
          {
            type: 'box',
            layout: 'vertical',
            contents: [
              {
                type: 'text',
                text: card.title,
                weight: 'bold',
                size: 'xl',
                wrap: true
              },
              {
                type: 'text',
                text: card.code,
                size: 'sm',
                color: '#666666',
                margin: 'sm'
              }
            ],
            paddingAll: 'lg'
          }
        ],
        paddingAll: '0px'
      },
      footer: {
        type: 'box',
        layout: 'vertical',
        spacing: 'sm',
        contents: [
          {
            type: 'button',
            style: 'primary',
            action: {
              type: 'uri',
              label: '下載圖片',
              uri: card.imageUrl
            }
          },
          {
            type: 'button',
            action: {
              type: 'uri',
              label: '更多佛卡',
              uri: 'https://www.budaedu.org/#/pictures/applicable?openExternalBrowser=1'
            },
            style: 'link',
            height: 'sm'
          },
          {
            type: 'button',
            style: 'link',
            action: {
              type: 'uri',
              label: '📤 分享給朋友',
              uri: `https://line.me/R/share?text=${encodeURIComponent(`🙏 ${card.title}\n${card.imageUrl}`)}`
            }
          }
        ]
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
    const bubbles: FlexBubble[] = books.map(book => this.createBookBubble(book));

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
    latestEpisodeUrl?: string | undefined;  // NEW: 最新一集連結
    intro?: string | undefined;  // NEW: 課程介紹
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
              aspectRatio: '2:1',
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
                      size: 'md' as const,
                      color: '#aaaaaa',
                      flex: 0
                    },
                    {
                      type: 'text' as const,
                      text: stream.instructor,
                      size: 'md' as const,
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
                      size: 'md' as const,
                      color: '#aaaaaa',
                      flex: 0
                    },
                    {
                      type: 'text' as const,
                      text: stream.startDate,
                      size: 'md' as const,
                      color: '#666666',
                      flex: 1
                    }
                  ]
                }] : [])
              ]
            },
            // 添加课程介绍显示区域
            ...(stream.intro ? [{
              type: 'box' as const,
              layout: 'vertical' as const,
              contents: [
                {
                  type: 'text' as const,
                  text: stream.intro,
                  size: 'md' as const,
                  color: '#999999',
                  wrap: true,
                  maxLines: 4
                }
              ],
              margin: 'md' as const
            }] : [])
          ]
        }
      };

      // Add footer only if eventUrl exists
      if (stream.eventUrl) {
        const footerButtons: any[] = [];

        if (stream.isLive) {
          // 直播：觀看直播 + 詳細資訊
          footerButtons.push({
            type: 'button',
            style: 'primary',
            action: {
              type: 'uri',
              label: '🎥 觀看直播',
              uri: stream.eventUrl
            }
          });
          footerButtons.push({
            type: 'button',
            style: 'link',
            action: {
              type: 'uri',
              label: 'ℹ️ 詳細資訊',
              uri: 'https://www.budaedu.org/#/series/live-streaming?openExternalBrowser=1'
            },
            height: 'sm'
          });
        } else {
          // 影片系列：簡介 + 最新一集 + 詳細資訊
          footerButtons.push({
            type: 'button',
            style: 'primary',
            action: {
              type: 'uri',
              label: '📖 簡介',  // 改名
              uri: stream.eventUrl  // 簡介頁連結
            }
          });

          // 最新一集按鈕（如果有 URL）
          if (stream.latestEpisodeUrl) {
            footerButtons.push({
              type: 'button',
              style: 'primary',
              action: {
                type: 'uri',
                label: '▶️ 最新一集',
                uri: `${stream.latestEpisodeUrl}?openExternalBrowser=1`
              }
            });
          }

          // 詳細資訊按鈕
          footerButtons.push({
            type: 'button',
            style: 'link',
            action: {
              type: 'uri',
              label: 'ℹ️ 詳細資訊',
              uri: 'https://www.budaedu.org/#/series/ongoing?openExternalBrowser=1'
            },
            height: 'sm'
          });
        }

        // 添加分享按鈕（適用於直播和影片系列）
        let shareText = '';
        if (stream.isLive) {
          shareText = `🎥 ${stream.title}\n${stream.instructor ? `講師：${stream.instructor}\n` : ''}${stream.startDate ? `時間：${stream.startDate}\n` : ''}${stream.eventUrl || ''}`;
        } else {
          // 影片系列：包含簡介和最新一集
          shareText = `📹 ${stream.title}\n${stream.instructor ? `講師：${stream.instructor}\n` : ''}`;
          if (stream.eventUrl) {
            shareText += `\n📖 簡介：${stream.eventUrl}`;
          }
          if (stream.latestEpisodeUrl) {
            shareText += `\n▶️ 最新一集：${stream.latestEpisodeUrl}`;
          }
        }

        footerButtons.push({
          type: 'button',
          style: 'link',
          action: {
            type: 'uri',
            label: '📤 分享',
            uri: `https://line.me/R/share?text=${encodeURIComponent(shareText)}`
          },
          height: 'sm'
        });


        bubble.footer = {
          type: 'box',
          layout: 'vertical',
          spacing: 'sm',
          contents: footerButtons
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
   * 創建簡化通知 Flex Message
   * 單一卡片，每個摘要行可點擊觸發查詢指令
   */
  createSimpleNotification(data: {
    newBooks?: number;      // 新書數量
    buddhaCards?: number;   // 佛卡數量
    cancellations?: number; // 停課數量
    news?: number;          // 消息數量
    videos?: number;        // 影音數量
  }): FlexMessage {
    const contents: any[] = [];

    // 標題
    contents.push({
      type: 'text',
      text: '📢 佛教教育網站有新內容',
      weight: 'bold',
      size: 'lg',
      color: '#1a1a1a'
    });

    contents.push({
      type: 'separator',
      margin: 'lg'
    });

    // 可點擊的摘要行（順序：停課 → 最新消息 → 新書 → 佛卡 → 影音）
    const items: Array<{ emoji: string; text: string; count: number; command: string; color: string }> = [];

    if (data.cancellations && data.cancellations > 0) {
      items.push({ emoji: '⚠️', text: '停課通知', count: data.cancellations, command: '停課通知', color: '#E74C3C' });
    }
    if (data.news && data.news > 0) {
      items.push({ emoji: '📰', text: '最新消息', count: data.news, command: '最新消息', color: '#3498DB' });
    }
    if (data.newBooks && data.newBooks > 0) {
      items.push({ emoji: '📚', text: '新書上架', count: data.newBooks, command: '最新法寶', color: '#27AE60' });
    }
    if (data.buddhaCards && data.buddhaCards > 0) {
      items.push({ emoji: '🖼️', text: '佛卡更新', count: data.buddhaCards, command: '佛卡', color: '#9B59B6' });
    }
    if (data.videos && data.videos > 0) {
      items.push({ emoji: '🎥', text: '影音更新', count: data.videos, command: '最新影音', color: '#8E44AD' });
    }

    // 建立可點擊的摘要行
    items.forEach(item => {
      contents.push({
        type: 'box',
        layout: 'horizontal',
        margin: 'lg',
        paddingAll: 'md',
        backgroundColor: '#f0f0f0',
        cornerRadius: 'lg',
        action: {
          type: 'message',
          text: item.command  // 點擊後自動輸入這個指令
        },
        contents: [
          {
            type: 'text',
            text: `${item.emoji} ${item.text} ${item.count} 項`,
            size: 'lg',
            color: item.color,
            weight: 'bold',
            flex: 1
          },
          {
            type: 'text',
            text: '👆點我',
            size: 'lg',
            color: '#1a73e8',
            align: 'end',
            gravity: 'center',
            weight: 'bold'
          }
        ]
      });
    });

    const bubble: FlexBubble = {
      type: 'bubble',
      size: 'mega',
      body: {
        type: 'box',
        layout: 'vertical',
        contents: contents,
        paddingAll: 'xl'
      }
    };

    // 返回包含 Flex Message 和 Quick Reply 的物件
    return {
      type: 'flex',
      altText: '📢 佛教教育網站有新內容',
      contents: bubble,
      quickReply: {
        items: [
          {
            type: 'action',
            action: { type: 'message', label: '⚠️停課通知', text: '停課通知' }
          },
          {
            type: 'action',
            action: { type: 'message', label: '📰最新消息', text: '最新消息' }
          },
          {
            type: 'action',
            action: { type: 'message', label: '📚最新法寶', text: '最新法寶' }
          },
          {
            type: 'action',
            action: { type: 'message', label: '🎥最新影音', text: '最新影音' }
          }
        ]
      }
    } as FlexMessage;
  }

  /**
   * 創建整合通知 Flex Message（整合卡片式佈局）
   * 每種類型一個卡片，最多 5-6 個 bubbles
   */
  createIntegratedNotification(data: {
    newBooks?: Array<{ title: string; author?: string; url?: string; source?: string; coverUrl?: string }>;
    news?: Array<{ title: string; date?: string; url?: string; content?: string }>;
    cancellations?: Array<{ courseName: string; cancelDate?: string; instructor?: string; time?: string; url?: string }>;
    videos?: Array<{ title: string; instructor?: string; episodeCount?: number | string; url?: string }>;
  }): FlexMessage {
    const bubbles: FlexBubble[] = [];

    // 官網連結
    const WEBSITE_LINKS = {
      books: 'https://www.budaedu.org/#/books',
      buddhaCards: 'https://www.budaedu.org/#/pictures',
      news: 'https://www.budaedu.org/#/bulletins',
      cancellations: 'https://www.budaedu.org/#/bulletins/course-cancel',
      videos: 'https://www.budaedu.org/#/series',
    };

    // 1. 📚 新書上架卡片
    if (data.newBooks && data.newBooks.length > 0) {
      const books = data.newBooks.filter(b => b.source !== 'buddha_cards');
      const cards = data.newBooks.filter(b => b.source === 'buddha_cards');

      if (books.length > 0) {
        const bookItems = books.slice(0, 5).map(book => ({
          type: 'box' as const,
          layout: 'horizontal' as const,
          contents: [
            { type: 'text' as const, text: '•', flex: 0, size: 'sm' as const, color: '#555555' },
            { type: 'text' as const, text: book.title.length > 18 ? book.title.substring(0, 18) + '...' : book.title, flex: 1, size: 'sm' as const, color: '#333333', margin: 'sm' as const, wrap: true }
          ],
          margin: 'sm' as const
        }));

        bubbles.push({
          type: 'bubble',
          size: 'kilo',
          header: {
            type: 'box',
            layout: 'vertical',
            contents: [
              { type: 'text', text: '📚 新書上架', weight: 'bold', size: 'lg', color: '#ffffff' },
              { type: 'text', text: `共 ${books.length} 本新書`, size: 'xs', color: '#ffffff', margin: 'sm' }
            ],
            backgroundColor: '#27AE60',
            paddingAll: 'lg'
          },
          body: { type: 'box', layout: 'vertical', contents: bookItems, paddingAll: 'lg' },
          footer: {
            type: 'box',
            layout: 'vertical',
            contents: [{ type: 'button', action: { type: 'uri', label: '查看更多 →', uri: WEBSITE_LINKS.books }, style: 'primary', color: '#27AE60', height: 'sm' }]
          }
        });
      }

      if (cards.length > 0) {
        const cardItems = cards.slice(0, 5).map(card => ({
          type: 'box' as const,
          layout: 'horizontal' as const,
          contents: [
            { type: 'text' as const, text: '•', flex: 0, size: 'sm' as const, color: '#555555' },
            { type: 'text' as const, text: card.title.length > 18 ? card.title.substring(0, 18) + '...' : card.title, flex: 1, size: 'sm' as const, color: '#333333', margin: 'sm' as const, wrap: true }
          ],
          margin: 'sm' as const
        }));

        bubbles.push({
          type: 'bubble',
          size: 'kilo',
          header: {
            type: 'box',
            layout: 'vertical',
            contents: [
              { type: 'text', text: '🖼️ 佛卡更新', weight: 'bold', size: 'lg', color: '#ffffff' },
              { type: 'text', text: `共 ${cards.length} 張佛卡`, size: 'xs', color: '#ffffff', margin: 'sm' }
            ],
            backgroundColor: '#9B59B6',
            paddingAll: 'lg'
          },
          body: { type: 'box', layout: 'vertical', contents: cardItems, paddingAll: 'lg' },
          footer: {
            type: 'box',
            layout: 'vertical',
            contents: [{ type: 'button', action: { type: 'uri', label: '查看更多 →', uri: WEBSITE_LINKS.buddhaCards }, style: 'primary', color: '#9B59B6', height: 'sm' }]
          }
        });
      }
    }

    // 2. ⚠️ 停課通知卡片
    if (data.cancellations && data.cancellations.length > 0) {
      const cancelItems = data.cancellations.slice(0, 5).map(item => ({
        type: 'box' as const,
        layout: 'vertical' as const,
        contents: [
          { type: 'text' as const, text: `📌 ${item.courseName}`, size: 'sm' as const, color: '#E74C3C', weight: 'bold' as const },
          { type: 'text' as const, text: `${(item.cancelDate || '').substring(0, 10)} ${item.time || ''} - ${item.instructor || ''}`.trim(), size: 'xs' as const, color: '#666666', margin: 'xs' as const }
        ],
        margin: 'md' as const
      }));

      bubbles.push({
        type: 'bubble',
        size: 'kilo',
        header: {
          type: 'box',
          layout: 'vertical',
          contents: [
            { type: 'text', text: '⚠️ 停課通知', weight: 'bold', size: 'lg', color: '#ffffff' },
            { type: 'text', text: `今日 ${data.cancellations.length} 堂課停課`, size: 'xs', color: '#ffffff', margin: 'sm' }
          ],
          backgroundColor: '#E74C3C',
          paddingAll: 'lg'
        },
        body: { type: 'box', layout: 'vertical', contents: cancelItems, paddingAll: 'lg' },
        footer: {
          type: 'box',
          layout: 'vertical',
          contents: [{ type: 'button', action: { type: 'uri', label: '查看詳情 →', uri: WEBSITE_LINKS.cancellations }, style: 'primary', color: '#E74C3C', height: 'sm' }]
        }
      });
    }

    // 3. 📰 最新消息卡片
    if (data.news && data.news.length > 0) {
      const newsItems = data.news.slice(0, 5).map(item => ({
        type: 'box' as const,
        layout: 'vertical' as const,
        contents: [
          { type: 'text' as const, text: item.title.length > 22 ? item.title.substring(0, 22) + '...' : item.title, size: 'sm' as const, color: '#333333', wrap: true },
          { type: 'text' as const, text: item.date || '', size: 'xs' as const, color: '#999999', margin: 'xs' as const }
        ],
        margin: 'md' as const
      }));

      bubbles.push({
        type: 'bubble',
        size: 'kilo',
        header: {
          type: 'box',
          layout: 'vertical',
          contents: [
            { type: 'text', text: '📰 最新消息', weight: 'bold', size: 'lg', color: '#ffffff' },
            { type: 'text', text: `共 ${data.news.length} 則公告`, size: 'xs', color: '#ffffff', margin: 'sm' }
          ],
          backgroundColor: '#3498DB',
          paddingAll: 'lg'
        },
        body: { type: 'box', layout: 'vertical', contents: newsItems, paddingAll: 'lg' },
        footer: {
          type: 'box',
          layout: 'vertical',
          contents: [{ type: 'button', action: { type: 'uri', label: '查看更多 →', uri: WEBSITE_LINKS.news }, style: 'primary', color: '#3498DB', height: 'sm' }]
        }
      });
    }

    // 4. 🎥 最新影音卡片
    if (data.videos && data.videos.length > 0) {
      const videoItems = data.videos.slice(0, 5).map(item => ({
        type: 'box' as const,
        layout: 'vertical' as const,
        contents: [
          { type: 'text' as const, text: item.title.length > 18 ? item.title.substring(0, 18) + '...' : item.title, size: 'sm' as const, color: '#333333', wrap: true },
          { type: 'text' as const, text: `${item.instructor || ''} ${item.episodeCount ? `| ${item.episodeCount} 集` : ''}`.trim(), size: 'xs' as const, color: '#666666', margin: 'xs' as const }
        ],
        margin: 'md' as const
      }));

      bubbles.push({
        type: 'bubble',
        size: 'kilo',
        header: {
          type: 'box',
          layout: 'vertical',
          contents: [
            { type: 'text', text: '🎥 最新影音', weight: 'bold', size: 'lg', color: '#ffffff' },
            { type: 'text', text: `共 ${data.videos.length} 個系列`, size: 'xs', color: '#ffffff', margin: 'sm' }
          ],
          backgroundColor: '#8E44AD',
          paddingAll: 'lg'
        },
        body: { type: 'box', layout: 'vertical', contents: videoItems, paddingAll: 'lg' },
        footer: {
          type: 'box',
          layout: 'vertical',
          contents: [{ type: 'button', action: { type: 'uri', label: '查看更多 →', uri: WEBSITE_LINKS.videos }, style: 'primary', color: '#8E44AD', height: 'sm' }]
        }
      });
    }

    if (bubbles.length === 0) {
      bubbles.push({
        type: 'bubble',
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            { type: 'text', text: '📢 佛教教育網站', weight: 'bold', size: 'lg' },
            { type: 'text', text: '目前沒有新的更新', size: 'sm', color: '#666666', margin: 'md' }
          ]
        }
      });
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
