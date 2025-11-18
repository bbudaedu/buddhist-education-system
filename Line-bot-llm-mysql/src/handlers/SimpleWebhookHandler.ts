import express from 'express';
import * as line from '@line/bot-sdk';
import { lineConfig } from '../config/index';

import { lineMessagingService } from '../services/lineMessagingService';
import { simpleDatabaseService } from '../services/SimpleDatabaseService';

/**
 * 簡化版 Webhook Handler for LINE Bot
 * 只處理基本的書籍查詢功能，不包含訂閱系統
 */
export class SimpleWebhookHandler {
  constructor() {
    console.log('📱 Simple Webhook Handler initialized');
  }

  /**
   * Express 路由處理器，接收 POST /webhook 請求
   */
  async handleWebhook(req: express.Request, res: express.Response): Promise<void> {
    try {
      // 驗證請求簽章
      const signature = req.get('X-Line-Signature');
      if (!signature || !this.validateSignature(JSON.stringify(req.body), signature)) {
        console.error('❌ Invalid signature');
        res.status(401).send('Unauthorized');
        return;
      }

      // 確保在 3 秒內回應 LINE 平台 HTTP 200
      res.status(200).send('OK');

      // 非同步處理事件
      setImmediate(async () => {
        try {
          const events: line.WebhookEvent[] = req.body.events || [];
          
          // 處理每個事件
          await Promise.all(
            events.map(event => this.processEvent(event))
          );
        } catch (error) {
          console.error('❌ Error processing webhook events:', error);
        }
      });

    } catch (error) {
      console.error('❌ Webhook handler error:', error);
      res.status(500).send('Internal Server Error');
    }
  }

  /**
   * 處理單一 LINE 事件
   */
  private async processEvent(event: line.WebhookEvent): Promise<void> {
    try {
      console.log(`📨 Processing event: ${event.type}`);

      switch (event.type) {
        case 'message':
          await this.handleMessage(event);
          break;
        case 'follow':
          await this.handleFollow(event);
          break;
        case 'unfollow':
          await this.handleUnfollow(event);
          break;
        default:
          console.log(`ℹ️  Unhandled event type: ${event.type}`);
      }
    } catch (error) {
      console.error('❌ Error processing event:', error);
    }
  }

  /**
   * 處理訊息事件
   */
  private async handleMessage(event: line.MessageEvent): Promise<void> {
    if (event.message.type !== 'text') {
      console.log('ℹ️  Non-text message received');
      return;
    }

    const userMessage = event.message.text.trim();
    const userId = event.source.userId;

    if (!userId) {
      console.error('❌ No user ID in message event');
      return;
    }

    console.log(`💬 User ${userId}: ${userMessage}`);

    try {
      // 處理特殊指令
      if (userMessage === '幫助' || userMessage === 'help' || userMessage === '說明') {
        await this.sendHelpMessage(userId);
        return;
      }

      if (userMessage === '統計' || userMessage === 'stats') {
        await this.sendBookStats(userId);
        return;
      }

      // 處理書籍查詢
      await this.handleBookQuery(userId, userMessage);

    } catch (error) {
      console.error('❌ Error handling message:', error);
      await lineMessagingService.sendTextMessage(
        userId,
        '抱歉，處理您的訊息時發生錯誤，請稍後再試。'
      );
    }
  }

  /**
   * 處理書籍查詢
   */
  private async handleBookQuery(userId: string, query: string): Promise<void> {
    try {
      // 發送處理中訊息
      await lineMessagingService.sendTextMessage(userId, '🔍 正在搜尋書籍...');

      // 搜尋書籍
      const books = await simpleDatabaseService.searchBooks(query, 5);

      if (books.length === 0) {
        await lineMessagingService.sendTextMessage(
          userId,
          `找不到包含「${query}」的書籍。\n\n💡 搜尋建議：\n• 嘗試使用書名的部分關鍵字\n• 嘗試使用作者姓名\n• 檢查是否有錯字`
        );
        return;
      }

      // 格式化搜尋結果
      let resultMessage = `📚 找到 ${books.length} 本相關書籍：\n\n`;
      
      books.forEach((book, index) => {
        resultMessage += `${index + 1}. 📖 ${book.title}\n`;
        if (book.author) {
          resultMessage += `   👤 作者：${book.author}\n`;
        }
        resultMessage += `   📍 位置：${book.shelf_location} (${book.library_branch})\n`;
        resultMessage += `   📊 庫存：${book.quantity} 本\n`;
        resultMessage += `   🆔 書號：${book.book_id}\n\n`;
      });

      resultMessage += '💡 輸入「幫助」查看更多功能';

      await lineMessagingService.sendTextMessage(userId, resultMessage);

    } catch (error) {
      console.error('❌ Error in book query:', error);
      await lineMessagingService.sendTextMessage(
        userId,
        '搜尋書籍時發生錯誤，請稍後再試。'
      );
    }
  }

  /**
   * 發送幫助訊息
   */
  private async sendHelpMessage(userId: string): Promise<void> {
    const helpMessage = `📚 佛教圖書館查詢機器人\n\n🔍 功能說明：\n• 直接輸入書名或作者名稱搜尋書籍\n• 輸入「統計」查看館藏統計\n• 輸入「幫助」查看此說明\n\n📖 使用範例：\n• 「金剛經」\n• 「聖嚴法師」\n• 「禪修」\n\n📍 館藏位置說明：\n• 3F：三樓書庫\n• 2F：二樓書庫\n• 5股：五股分館\n\n如有問題請聯繫圖書館管理員。`;

    await lineMessagingService.sendTextMessage(userId, helpMessage);
  }

  /**
   * 發送書籍統計訊息
   */
  private async sendBookStats(userId: string): Promise<void> {
    try {
      const stats = await simpleDatabaseService.getBookStats();
      
      const statsMessage = `📊 館藏統計\n\n📚 總書籍數：${stats.total} 本\n📖 可借閱：${stats.available} 本\n\n💡 輸入書名或作者名稱即可搜尋書籍`;

      await lineMessagingService.sendTextMessage(userId, statsMessage);
    } catch (error) {
      console.error('❌ Error getting book stats:', error);
      await lineMessagingService.sendTextMessage(
        userId,
        '取得統計資料時發生錯誤，請稍後再試。'
      );
    }
  }

  /**
   * 處理用戶加入好友事件
   */
  private async handleFollow(event: line.FollowEvent): Promise<void> {
    const userId = event.source.userId;
    if (!userId) return;

    console.log(`👋 New follower: ${userId}`);

    const welcomeMessage = `🙏 歡迎使用佛教圖書館查詢機器人！\n\n📚 我可以幫您：\n• 搜尋書籍資訊\n• 查看館藏位置\n• 確認庫存數量\n\n💡 直接輸入書名或作者名稱開始搜尋\n輸入「幫助」查看詳細說明`;

    await lineMessagingService.sendTextMessage(userId, welcomeMessage);
  }

  /**
   * 處理用戶取消好友事件
   */
  private async handleUnfollow(event: line.UnfollowEvent): Promise<void> {
    const userId = event.source.userId;
    console.log(`👋 User unfollowed: ${userId}`);
  }

  /**
   * 驗證 LINE 請求簽章
   */
  private validateSignature(body: string, signature: string): boolean {
    try {
      const crypto = require('crypto');
      const hash = crypto
        .createHmac('sha256', lineConfig.channelSecret)
        .update(body)
        .digest('base64');
      
      return hash === signature;
    } catch (error) {
      console.error('❌ Signature validation error:', error);
      return false;
    }
  }
}

// 建立單例實例
export const simpleWebhookHandler = new SimpleWebhookHandler();