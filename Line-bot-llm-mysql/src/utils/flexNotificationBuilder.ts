/**
 * Flex Notification Builder
 * 濃縮通知版面建構器
 * 
 * 將多來源訂閱內容（停課、消息、法寶、影音）整合成一封簡潔的通知
 */

import { FlexMessage, FlexBubble, FlexBox, FlexComponent } from '@line/bot-sdk';

/**
 * 通知來源類型
 */
export interface NotificationSource {
  cancellations?: CancellationItem[];
  news?: NewsItem[];
  books?: BookItem[];
  videos?: VideoItem[];
}

export interface CancellationItem {
  id: string;
  courseName: string;
  cancelDate: string;
  cancelDateDisplay?: string;
  instructor?: string;
}

export interface NewsItem {
  id: string;
  title: string;
  publishDate?: string;
  url?: string;
}

export interface BookItem {
  id: string;
  title: string;
  author?: string;
  publishDate?: string;
}

export interface VideoItem {
  id: string;
  title: string;
  instructor?: string;
  episodeCount?: number;
}

/**
 * 官網連結配置
 */
const WEBSITE_URLS = {
  home: 'https://www.budaedu.org/#',
  cancellations: 'https://www.budaedu.org/#/bulletins/course-cancel',
  bulletins: 'https://www.budaedu.org/#/bulletins',
  books: 'https://www.budaedu.org/#/books/applicable/chinese',
  videos: 'https://www.budaedu.org/#/series/ongoing',
  subscription: 'https://www.budaedu.org/#/subscription'
};

/**
 * Flex Notification Builder
 */
export class FlexNotificationBuilder {

  /**
   * 建立多來源濃縮通知
   * 將所有來源整合成一個 Flex Bubble
   */
  createConsolidatedNotification(sources: NotificationSource): FlexMessage {
    const today = new Date();
    const dateStr = `${today.getMonth() + 1}/${today.getDate()}`;
    const timeStr = today.getHours() < 12 ? '上午' : '下午';

    // 建立各區塊內容
    const sections: FlexComponent[] = [];

    // 停課通知區塊 (紅色)
    if (sources.cancellations && sources.cancellations.length > 0) {
      sections.push(this.createSection(
        '⚠️ 停課通知',
        '#E74C3C',
        sources.cancellations.slice(0, 3).map(c => 
          `${c.courseName} - ${c.cancelDateDisplay || c.cancelDate}`
        ),
        WEBSITE_URLS.cancellations,
        sources.cancellations.length
      ));
    }

    // 最新消息區塊 (橙色)
    if (sources.news && sources.news.length > 0) {
      sections.push(this.createSection(
        '📰 最新消息',
        '#E67E22',
        sources.news.slice(0, 3).map(n => this.truncateText(n.title, 25)),
        WEBSITE_URLS.bulletins,
        sources.news.length
      ));
    }

    // 新書上架區塊 (綠色)
    if (sources.books && sources.books.length > 0) {
      sections.push(this.createSection(
        '📚 新書上架',
        '#27AE60',
        sources.books.slice(0, 3).map(b => this.truncateText(b.title, 25)),
        WEBSITE_URLS.books,
        sources.books.length
      ));
    }

    // 最新影音區塊 (紫色)
    if (sources.videos && sources.videos.length > 0) {
      sections.push(this.createSection(
        '🎥 最新影音',
        '#9B59B6',
        sources.videos.slice(0, 3).map(v => {
          const ep = v.episodeCount ? ` (${v.episodeCount}集)` : '';
          return this.truncateText(v.title, 22) + ep;
        }),
        WEBSITE_URLS.videos,
        sources.videos.length
      ));
    }

    // 如果沒有任何內容
    if (sections.length === 0) {
      return this.createEmptyNotification();
    }

    // 建立 Bubble
    const bubble: FlexBubble = {
      type: 'bubble',
      size: 'mega',
      header: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'box',
            layout: 'horizontal',
            contents: [
              {
                type: 'text',
                text: '🔔 每日更新通知',
                weight: 'bold',
                size: 'lg',
                color: '#ffffff',
                flex: 1
              },
              {
                type: 'text',
                text: `${dateStr} ${timeStr}`,
                size: 'sm',
                color: '#ffffff',
                align: 'end'
              }
            ]
          }
        ],
        backgroundColor: '#1E88E5',
        paddingAll: 'lg'
      },
      body: {
        type: 'box',
        layout: 'vertical',
        contents: sections as any[],
        spacing: 'md',
        paddingAll: 'lg'
      },
      footer: {
        type: 'box',
        layout: 'horizontal',
        contents: [
          {
            type: 'button',
            action: {
              type: 'uri',
              label: '🏠 官網首頁',
              uri: `${WEBSITE_URLS.home}?openExternalBrowser=1`
            },
            style: 'primary',
            height: 'sm',
            flex: 1
          },
          {
            type: 'button',
            action: {
              type: 'message',
              label: '⚙️ 訂閱管理',
              text: '訂閱狀態查詢'
            },
            style: 'secondary',
            height: 'sm',
            flex: 1,
            margin: 'sm'
          }
        ],
        spacing: 'sm'
      }
    };

    return {
      type: 'flex',
      altText: `🔔 每日更新通知 - ${this.getAltTextSummary(sources)}`,
      contents: bubble
    };
  }

  /**
   * 建立單一區塊
   */
  private createSection(
    title: string,
    tagColor: string,
    items: string[],
    moreUrl: string,
    totalCount: number
  ): FlexBox {
    const itemContents: FlexComponent[] = items.map(item => ({
      type: 'box',
      layout: 'horizontal',
      contents: [
        {
          type: 'text',
          text: '•',
          size: 'sm',
          color: '#666666',
          flex: 0
        },
        {
          type: 'text',
          text: item,
          size: 'sm',
          color: '#333333',
          wrap: true,
          margin: 'sm',
          flex: 1
        }
      ]
    } as FlexBox));

    return {
      type: 'box',
      layout: 'vertical',
      contents: [
        // 標題列
        {
          type: 'box',
          layout: 'horizontal',
          contents: [
            // 標籤
            {
              type: 'box',
              layout: 'vertical',
              contents: [
                {
                  type: 'text',
                  text: title,
                  size: 'sm',
                  color: '#ffffff',
                  weight: 'bold'
                }
              ],
              backgroundColor: tagColor,
              paddingAll: 'xs',
              cornerRadius: 'sm',
              flex: 0
            },
            // 數量
            {
              type: 'text',
              text: totalCount > 3 ? `(${totalCount}則)` : '',
              size: 'xs',
              color: '#999999',
              margin: 'sm',
              flex: 1
            },
            // 查看全部按鈕
            {
              type: 'text',
              text: '查看全部 →',
              size: 'xs',
              color: '#1E88E5',
              align: 'end',
              action: {
                type: 'uri',
                label: '查看全部',
                uri: `${moreUrl}?openExternalBrowser=1`
              }
            }
          ],
          alignItems: 'center'
        },
        // 項目列表
        {
          type: 'box',
          layout: 'vertical',
          contents: itemContents as any[],
          margin: 'sm',
          spacing: 'xs'
        }
      ],
      backgroundColor: '#F8F9FA',
      paddingAll: 'md',
      cornerRadius: 'md',
      margin: 'sm'
    };
  }

  /**
   * 建立空通知
   */
  private createEmptyNotification(): FlexMessage {
    return {
      type: 'flex',
      altText: '目前沒有新的通知',
      contents: {
        type: 'bubble',
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            {
              type: 'text',
              text: '✅',
              size: '3xl',
              align: 'center'
            },
            {
              type: 'text',
              text: '目前沒有新的通知',
              align: 'center',
              margin: 'md',
              color: '#666666'
            }
          ],
          justifyContent: 'center',
          paddingAll: 'xxl'
        }
      }
    };
  }

  /**
   * 截斷文字
   */
  private truncateText(text: string, maxLength: number): string {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  }

  /**
   * 生成 altText 摘要
   */
  private getAltTextSummary(sources: NotificationSource): string {
    const parts: string[] = [];
    
    if (sources.cancellations?.length) {
      parts.push(`${sources.cancellations.length}則停課`);
    }
    if (sources.news?.length) {
      parts.push(`${sources.news.length}則消息`);
    }
    if (sources.books?.length) {
      parts.push(`${sources.books.length}本新書`);
    }
    if (sources.videos?.length) {
      parts.push(`${sources.videos.length}則影音`);
    }
    
    return parts.join('、') || '無新通知';
  }
}

export const flexNotificationBuilder = new FlexNotificationBuilder();
