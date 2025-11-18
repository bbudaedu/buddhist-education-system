import * as line from '@line/bot-sdk';
import { BookSummary } from '../types/notification';
import { UserSubscription } from '../types/subscription';

/**
 * MessageTemplateService creates LINE message templates for book notifications
 * Handles both Flex Messages for rich content and fallback text messages
 */
export class MessageTemplateService {

  /**
   * Create notification message content based on books and message type
   * @param books Array of books to include in notification
   * @param user User subscription with preferences
   * @param messageType Type of message to create
   * @returns Object with text, quickReply, and flexMessage
   */
  createNotificationContent(
    books: BookSummary[], 
    user: UserSubscription, 
    messageType: 'single_book' | 'multiple_books' | 'daily_summary'
  ): { text: string; quickReply?: line.QuickReply; flexMessage?: line.FlexMessage } {
    
    switch (messageType) {
      case 'single_book':
        if (books.length === 0) {
          return this.createFallbackMessage(books);
        }
        return this.createSingleBookMessage(books[0]!, user);
      
      case 'multiple_books':
        return this.createMultipleBooksMessage(books, user);
      
      case 'daily_summary':
        return this.createDailySummaryMessage(books, user);
      
      default:
        return this.createFallbackMessage(books);
    }
  }

  /**
   * Create message for a single book notification
   * @param book Single book to feature
   * @param user User subscription with preferences
   * @returns Message content with Flex Message
   */
  private createSingleBookMessage(
    book: BookSummary, 
    user: UserSubscription
  ): { text: string; quickReply?: line.QuickReply; flexMessage?: line.FlexMessage } {
    
    // Create fallback text message
    const fallbackText = this.createSingleBookFallbackText(book, user);
    
    // Create Flex Message for rich display
    const flexMessage = this.createSingleBookFlexMessage(book, user);
    
    // Create quick reply options
    const quickReply = this.createBookNotificationQuickReply();

    return {
      text: fallbackText,
      quickReply,
      flexMessage
    };
  }

  /**
   * Create message for multiple books notification
   * @param books Array of books (2-5 books typically)
   * @param user User subscription with preferences
   * @returns Message content with Carousel or Flex Message
   */
  private createMultipleBooksMessage(
    books: BookSummary[], 
    user: UserSubscription
  ): { text: string; quickReply?: line.QuickReply; flexMessage?: line.FlexMessage } {
    
    // Create fallback text message
    const fallbackText = this.createMultipleBooksFallbackText(books, user);
    
    // Create Flex Message (Carousel for multiple books)
    const flexMessage = this.createMultipleBooksFlexMessage(books, user);
    
    // Create quick reply options
    const quickReply = this.createBookNotificationQuickReply();

    return {
      text: fallbackText,
      quickReply,
      flexMessage
    };
  }

  /**
   * Create daily summary message for many books
   * @param books Array of all books processed today
   * @param user User subscription with preferences
   * @returns Message content with summary format
   */
  private createDailySummaryMessage(
    books: BookSummary[], 
    user: UserSubscription
  ): { text: string; quickReply?: line.QuickReply; flexMessage?: line.FlexMessage } {
    
    // Create fallback text message
    const fallbackText = this.createDailySummaryFallbackText(books, user);
    
    // Create Flex Message for summary display
    const flexMessage = this.createDailySummaryFlexMessage(books, user);
    
    // Create quick reply options
    const quickReply = this.createBookNotificationQuickReply();

    return {
      text: fallbackText,
      quickReply,
      flexMessage
    };
  }

  /**
   * Create fallback text message for single book
   * @param book Book to feature
   * @param user User preferences
   * @returns Formatted text message
   */
  private createSingleBookFallbackText(book: BookSummary, user: UserSubscription): string {
    let text = `📚 今日新書通知\n\n`;
    text += `📖 ${this.truncateText(book.title, 50)}\n`;
    
    if (book.author) {
      text += `👤 作者：${this.truncateText(book.author, 30)}\n`;
    }
    
    if (user.notificationPreferences.enableSummary && book.summary) {
      text += `\n📝 內容摘要：\n${this.truncateText(book.summary, 200)}\n`;
    }
    
    if (user.notificationPreferences.enableDownloadLink && book.downloadUrl) {
      text += `\n🔗 閱讀連結：${book.downloadUrl}\n`;
    }
    
    return text;
  }

  /**
   * Create fallback text message for multiple books
   * @param books Array of books
   * @param user User preferences
   * @returns Formatted text message
   */
  private createMultipleBooksFallbackText(books: BookSummary[], user: UserSubscription): string {
    let text = `📚 今日新書通知\n\n發現 ${books.length} 本新書：\n\n`;
    
    books.forEach((book, index) => {
      text += `${index + 1}. ${this.truncateText(book.title, 40)}`;
      if (book.author) {
        text += ` - ${this.truncateText(book.author, 20)}`;
      }
      text += '\n';
      
      if (user.notificationPreferences.enableSummary && book.summary) {
        text += `   📝 ${this.truncateText(book.summary, 100)}\n`;
      }
      
      if (user.notificationPreferences.enableDownloadLink && book.downloadUrl) {
        text += `   🔗 ${book.downloadUrl}\n`;
      }
      
      text += '\n';
    });
    
    return text.trim();
  }

  /**
   * Create fallback text message for daily summary
   * @param books Array of all books
   * @param user User preferences
   * @returns Formatted text message
   */
  private createDailySummaryFallbackText(books: BookSummary[], user: UserSubscription): string {
    const displayBooks = books.slice(0, user.notificationPreferences.maxBooksPerNotification);
    const remainingCount = books.length - displayBooks.length;
    
    let text = `📚 今日新書摘要\n\n共發現 ${books.length} 本新書`;
    
    if (remainingCount > 0) {
      text += `，顯示前 ${displayBooks.length} 本：\n\n`;
    } else {
      text += `：\n\n`;
    }
    
    displayBooks.forEach((book, index) => {
      text += `${index + 1}. ${this.truncateText(book.title, 35)}\n`;
      if (book.author) {
        text += `   作者：${this.truncateText(book.author, 25)}\n`;
      }
    });
    
    if (remainingCount > 0) {
      text += `\n...還有 ${remainingCount} 本書，請查看詳細訊息。`;
    }
    
    return text;
  }

  /**
   * Create Flex Message for single book display
   * @param book Book to display
   * @param user User preferences
   * @returns LINE Flex Message
   */
  private createSingleBookFlexMessage(book: BookSummary, user: UserSubscription): line.FlexMessage {
    const contents: any = {
      type: 'bubble',
      header: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'text',
            text: '📚 今日新書',
            weight: 'bold',
            size: 'lg',
            color: '#2196F3',
            align: 'center'
          }
        ],
        backgroundColor: '#E3F2FD',
        paddingAll: 'md'
      },
      body: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'text',
            text: this.truncateText(book.title, 60),
            weight: 'bold',
            size: 'md',
            wrap: true,
            color: '#333333'
          }
        ],
        spacing: 'sm'
      }
    };

    // Add author if available
    if (book.author) {
      contents.body.contents.push({
        type: 'box',
        layout: 'horizontal',
        contents: [
          {
            type: 'text',
            text: '👤',
            size: 'sm',
            flex: 0
          },
          {
            type: 'text',
            text: this.truncateText(book.author, 40),
            size: 'sm',
            wrap: true,
            margin: 'sm',
            color: '#666666'
          }
        ],
        margin: 'md'
      });
    }

    // Add summary if enabled
    if (user.notificationPreferences.enableSummary && book.summary) {
      contents.body.contents.push(
        {
          type: 'separator',
          margin: 'lg'
        },
        {
          type: 'text',
          text: '📝 內容摘要',
          weight: 'bold',
          size: 'sm',
          color: '#666666',
          margin: 'lg'
        },
        {
          type: 'text',
          text: this.truncateText(book.summary, 300),
          size: 'sm',
          wrap: true,
          margin: 'sm',
          color: '#333333'
        }
      );
    }



    // Add footer with download button if enabled
    if (user.notificationPreferences.enableDownloadLink && book.downloadUrl) {
      contents.footer = {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'button',
            action: {
              type: 'uri',
              label: '📖 閱讀全文',
              uri: book.downloadUrl
            },
            style: 'primary',
            color: '#2196F3'
          }
        ],
        spacing: 'sm'
      };
    }

    return {
      type: 'flex',
      altText: `新書通知：${book.title}`,
      contents
    };
  }

  /**
   * Create Flex Message carousel for multiple books
   * @param books Array of books to display
   * @param user User preferences
   * @returns LINE Flex Message (Carousel)
   */
  private createMultipleBooksFlexMessage(books: BookSummary[], user: UserSubscription): line.FlexMessage {
    const bubbles = books.map(book => this.createBookBubble(book, user));

    return {
      type: 'flex',
      altText: `今日新書通知：${books.length} 本新書`,
      contents: {
        type: 'carousel',
        contents: bubbles
      }
    };
  }

  /**
   * Create Flex Message for daily summary
   * @param books Array of all books
   * @param user User preferences
   * @returns LINE Flex Message
   */
  private createDailySummaryFlexMessage(books: BookSummary[], user: UserSubscription): line.FlexMessage {
    const displayBooks = books.slice(0, user.notificationPreferences.maxBooksPerNotification);
    const remainingCount = books.length - displayBooks.length;

    const contents: any = {
      type: 'bubble',
      header: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'text',
            text: '📚 今日新書摘要',
            weight: 'bold',
            size: 'lg',
            color: '#2196F3',
            align: 'center'
          },
          {
            type: 'text',
            text: `共發現 ${books.length} 本新書`,
            size: 'sm',
            color: '#666666',
            align: 'center',
            margin: 'sm'
          }
        ],
        backgroundColor: '#E3F2FD',
        paddingAll: 'md'
      },
      body: {
        type: 'box',
        layout: 'vertical',
        contents: [],
        spacing: 'sm'
      }
    };

    // Add book list
    displayBooks.forEach((book, index) => {
      contents.body.contents.push({
        type: 'box',
        layout: 'horizontal',
        contents: [
          {
            type: 'text',
            text: `${index + 1}.`,
            size: 'sm',
            flex: 0,
            color: '#666666'
          },
          {
            type: 'box',
            layout: 'vertical',
            contents: [
              {
                type: 'text',
                text: this.truncateText(book.title, 45),
                size: 'sm',
                wrap: true,
                weight: 'bold'
              },
              ...(book.author ? [{
                type: 'text',
                text: this.truncateText(book.author, 30),
                size: 'xs',
                color: '#666666',
                margin: 'xs'
              }] : [])
            ],
            margin: 'sm'
          }
        ],
        margin: index > 0 ? 'md' : 'none'
      });
    });

    // Add remaining count if applicable
    if (remainingCount > 0) {
      contents.body.contents.push(
        {
          type: 'separator',
          margin: 'lg'
        },
        {
          type: 'text',
          text: `...還有 ${remainingCount} 本書`,
          size: 'sm',
          color: '#666666',
          align: 'center',
          margin: 'md'
        }
      );
    }

    return {
      type: 'flex',
      altText: `今日新書摘要：${books.length} 本新書`,
      contents
    };
  }

  /**
   * Create individual book bubble for carousel
   * @param book Book to display
   * @param user User preferences
   * @returns Bubble content for carousel
   */
  private createBookBubble(book: BookSummary, user: UserSubscription): any {
    const bubble: any = {
      type: 'bubble',
      body: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'text',
            text: this.truncateText(book.title, 50),
            weight: 'bold',
            size: 'md',
            wrap: true
          }
        ],
        spacing: 'sm'
      }
    };

    // Add author
    if (book.author) {
      bubble.body.contents.push({
        type: 'text',
        text: `👤 ${this.truncateText(book.author, 30)}`,
        size: 'sm',
        color: '#666666',
        margin: 'sm'
      });
    }

    // Add summary if enabled and available
    if (user.notificationPreferences.enableSummary && book.summary) {
      bubble.body.contents.push({
        type: 'text',
        text: this.truncateText(book.summary, 150),
        size: 'xs',
        wrap: true,
        margin: 'md',
        color: '#333333'
      });
    }

    // Add footer with download button if enabled
    if (user.notificationPreferences.enableDownloadLink && book.downloadUrl) {
      bubble.footer = {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'button',
            action: {
              type: 'uri',
              label: '📖 閱讀',
              uri: book.downloadUrl
            },
            style: 'primary',
            color: '#2196F3',
            height: 'sm'
          }
        ]
      };
    }

    return bubble;
  }

  /**
   * Create quick reply options for book notifications
   * @returns LINE QuickReply object
   */
  private createBookNotificationQuickReply(): line.QuickReply {
    return {
      items: [
        {
          type: 'action',
          action: {
            type: 'message',
            label: '📊 訂閱狀態',
            text: '訂閱狀態'
          }
        },
        {
          type: 'action',
          action: {
            type: 'message',
            label: '🔍 搜尋書籍',
            text: '推薦一些好書'
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
  }

  /**
   * Create fallback message when no specific template matches
   * @param books Array of books
   * @returns Basic message content
   */
  private createFallbackMessage(books: BookSummary[]): { text: string } {
    const bookTitles = books.map(book => book.title).join('、');
    return {
      text: `📚 今日新書通知\n\n發現 ${books.length} 本新書：${bookTitles}\n\n請查看詳細資訊。`
    };
  }

  /**
   * Truncate text to specified length with ellipsis
   * @param text Text to truncate
   * @param maxLength Maximum length
   * @returns Truncated text
   */
  private truncateText(text: string, maxLength: number): string {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
  }
}

// Create singleton instance
export const messageTemplateService = new MessageTemplateService();