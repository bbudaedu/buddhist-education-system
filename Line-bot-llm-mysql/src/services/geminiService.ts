import { GoogleGenerativeAI, GenerativeModel } from '@google/generative-ai';
import { geminiConfig } from '../config';
import { databaseService } from './databaseService';
import { Book } from '../types/book';

/**
 * Gemini AI Service for processing user queries with Function Calling
 */
export class GeminiService {
  private genAI: GoogleGenerativeAI;
  private model: GenerativeModel;
  private systemInstruction: string;

  constructor() {
    // 初始化 Gemini AI 客戶端
    this.genAI = new GoogleGenerativeAI(geminiConfig.apiKey);
    
    // 設定 System Instruction 為友善的書庫助理
    this.systemInstruction = `你是一個友善且專業的書庫助理。當用戶詢問書籍相關問題時，請分析用戶的意圖：

1. 如果用戶想要搜尋書籍，請回覆 "SEARCH:" 後面跟著搜尋關鍵字
2. 如果用戶想要查詢特定館藏地的書籍，請回覆 "BRANCH:" 後面跟著館藏地名稱
3. 如果用戶只是打招呼或問其他問題，請直接友善回應

可用的館藏地點：五股、3F、2F

例如：
- 用戶問「有沒有金剛經相關的書？」→ 回覆「SEARCH:金剛經」
- 用戶問「五股有什麼書？」→ 回覆「BRANCH:五股」
- 用戶問「找五股庫存最多的書？」→ 回覆「BRANCH:五股」
- 用戶問「你好」→ 回覆「您好！我是書庫助理，可以幫您搜尋書籍資訊。」

保持回覆簡潔，不超過 200 字。`;

    // 初始化模型
    this.model = this.genAI.getGenerativeModel({
      model: geminiConfig.model,
      generationConfig: {
        maxOutputTokens: geminiConfig.maxOutputTokens,
        temperature: geminiConfig.temperature,
      },
    });
  }

  /**
   * 解析 Gemini 回應，提取搜尋關鍵字或館藏地
   * @param response Gemini 的回應文字
   * @returns { type: 'search' | 'branch' | 'none', query: string }
   */
  private parseGeminiResponse(response: string): { type: 'search' | 'branch' | 'none', query: string } {
    if (response.startsWith('SEARCH:')) {
      return { type: 'search', query: response.substring(7).trim() };
    }
    if (response.startsWith('BRANCH:')) {
      return { type: 'branch', query: response.substring(7).trim() };
    }
    return { type: 'none', query: response };
  }

  /**
   * 處理用戶查詢的主要方法
   * @param userMessage 用戶輸入的訊息
   * @returns Promise<{ text: string; books: Book[] }> 回覆文字和相關書籍
   */
  async processUserQuery(userMessage: string): Promise<{ text: string; books: Book[] }> {
    try {
      // 第一步：讓 Gemini 分析用戶意圖
      const intentResult = await this.model.generateContent(
        this.systemInstruction + '\n\n用戶訊息：' + userMessage
      );
      
      const intentResponse = intentResult.response.text();
      
      // 確保意圖回應不為空
      if (!intentResponse || intentResponse.trim() === '') {
        console.warn('Gemini intent response is empty, using default response');
        return {
          text: '您好！我是書庫助理，可以幫您搜尋書籍資訊。請告訴我您想找什麼書？',
          books: []
        };
      }
      
      // 解析 Gemini 回應
      const parsed = this.parseGeminiResponse(intentResponse);
      
      if (parsed.type === 'search') {
        // 執行書名搜尋
        const books = await databaseService.searchBooks(parsed.query, 10);
        const finalResponse = await this.generateFinalResponse(userMessage, parsed.query, books);
        
        return {
          text: finalResponse,
          books: books
        };
      } else if (parsed.type === 'branch') {
        // 執行館藏地查詢
        const books = await databaseService.searchBooksByBranch(parsed.query, 10);
        const finalResponse = await this.generateFinalResponse(userMessage, `${parsed.query}館藏`, books);
        
        return {
          text: finalResponse,
          books: books
        };
      } else {
        // 沒有搜尋需求，直接回傳 Gemini 的回覆
        // 再次確保回應不為空
        const responseText = intentResponse.trim();
        return {
          text: responseText || '您好！我是書庫助理，有什麼可以幫您的嗎？',
          books: []
        };
      }
    } catch (error) {
      console.error('Gemini API error:', error);
      throw new Error('Failed to process user query with Gemini AI');
    }
  }

  /**
   * 根據資料庫查詢結果生成最終自然語言回覆
   * @param originalMessage 原始用戶訊息
   * @param searchQuery 搜尋關鍵字
   * @param books 查詢到的書籍
   * @returns Promise<string> 最終回覆文字
   */
  private async generateFinalResponse(
    originalMessage: string,
    searchQuery: string,
    books: Book[]
  ): Promise<string> {
    try {
      const booksInfo = books.map(book => 
        `書名：${book.title}，館藏地：${book.library_branch}，位置：${book.shelf_location}，庫存：${book.quantity}本`
      ).join('\n');

      const prompt = `用戶問：${originalMessage}
搜尋關鍵字：${searchQuery}
查詢結果：
${booksInfo || '沒有找到相關書籍'}

請以友善的書庫助理身份回覆用戶。如果找到書籍，請列出書名和館藏資訊。如果沒找到，請禮貌地告知並建議其他查詢方式。保持回覆簡潔，不超過200字。`;

      const result = await this.model.generateContent(prompt);
      const responseText = result.response.text();
      
      // 確保回應不為空字串
      if (!responseText || responseText.trim() === '') {
        console.warn('Gemini returned empty response, using fallback');
        return this.getFallbackResponse(books);
      }
      
      return responseText;
    } catch (error) {
      console.error('Error generating final response:', error);
      return this.getFallbackResponse(books);
    }
  }

  /**
   * 當 Gemini API 失敗或回傳空字串時的備用回應
   * @param books 查詢到的書籍
   * @returns string 備用回應文字
   */
  private getFallbackResponse(books: Book[]): string {
    if (books.length > 0) {
      return `找到 ${books.length} 本相關書籍：\n${books.map(book => 
        `• ${book.title} (${book.library_branch}, ${book.shelf_location})`
      ).join('\n')}`;
    } else {
      return '抱歉，沒有找到相關的書籍。您可以嘗試使用不同的關鍵字搜尋。';
    }
  }

  /**
   * 測試 Gemini API 連線
   * @returns Promise<boolean> 連線是否成功
   */
  async testConnection(): Promise<boolean> {
    try {
      const result = await this.model.generateContent('測試連線');
      return !!result.response.text();
    } catch (error) {
      console.error('Gemini connection test failed:', error);
      return false;
    }
  }
}

// 建立單例實例
export const geminiService = new GeminiService();