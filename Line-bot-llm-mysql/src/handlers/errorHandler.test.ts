import { ErrorHandler, ErrorType, ErrorContext } from './errorHandler';

describe('ErrorHandler', () => {
  // Mock console.error to avoid cluttering test output
  const originalConsoleError = console.error;
  beforeEach(() => {
    console.error = jest.fn();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  describe('classify', () => {
    it('should classify Gemini API errors correctly', () => {
      const error = new Error('Gemini API request failed');
      const errorType = ErrorHandler.classify(error);
      expect(errorType).toBe(ErrorType.GEMINI_API_ERROR);
    });

    it('should classify database errors correctly', () => {
      const error = new Error('MySQL connection failed');
      const errorType = ErrorHandler.classify(error);
      expect(errorType).toBe(ErrorType.DATABASE_ERROR);
    });

    it('should classify LINE API errors correctly', () => {
      const error = new Error('LINE messaging API error');
      const errorType = ErrorHandler.classify(error);
      expect(errorType).toBe(ErrorType.LINE_API_ERROR);
    });

    it('should classify validation errors correctly', () => {
      const error = new Error('Invalid request format');
      const errorType = ErrorHandler.classify(error);
      expect(errorType).toBe(ErrorType.VALIDATION_ERROR);
    });

    it('should classify unknown errors correctly', () => {
      const error = new Error('Some random error');
      const errorType = ErrorHandler.classify(error);
      expect(errorType).toBe(ErrorType.UNKNOWN_ERROR);
    });
  });

  describe('getFriendlyMessage', () => {
    it('should return correct friendly message for each error type', () => {
      expect(ErrorHandler.getFriendlyMessage(ErrorType.GEMINI_API_ERROR))
        .toBe('抱歉，AI 助理暫時無法回應，請稍後再試。');
      
      expect(ErrorHandler.getFriendlyMessage(ErrorType.DATABASE_ERROR))
        .toBe('書庫系統維護中，請稍後再試。');
      
      expect(ErrorHandler.getFriendlyMessage(ErrorType.LINE_API_ERROR))
        .toBe('訊息發送失敗，請重新傳送您的問題。');
      
      expect(ErrorHandler.getFriendlyMessage(ErrorType.VALIDATION_ERROR))
        .toBe('您的訊息格式有誤，請重新輸入。');
      
      expect(ErrorHandler.getFriendlyMessage(ErrorType.UNKNOWN_ERROR))
        .toBe('系統發生錯誤，我們正在處理中。');
    });
  });

  describe('handle', () => {
    it('should handle error and return friendly message', () => {
      const error = new Error('Gemini API timeout');
      const context: ErrorContext = {
        userId: 'user123',
        userMessage: '有沒有金剛經？',
        operation: 'processUserQuery'
      };

      const friendlyMessage = ErrorHandler.handle(error, context);
      
      expect(friendlyMessage).toBe('抱歉，AI 助理暫時無法回應，請稍後再試。');
      expect(console.error).toHaveBeenCalledWith(
        'Error occurred:',
        expect.stringContaining('"errorType": "GEMINI_API_ERROR"')
      );
    });

    it('should protect sensitive information in logs', () => {
      const error = new Error('Database connection failed');
      const context: ErrorContext = {
        userId: 'user123456789',
        userMessage: '我的密碼是 secret123',
        operation: 'databaseQuery'
      };

      ErrorHandler.handle(error, context);
      
      const logCall = (console.error as jest.Mock).mock.calls[0];
      const logString = logCall[1];
      
      // 檢查用戶ID被截斷
      expect(logString).toContain('"userId": "user1234..."');
      // 檢查不包含完整的用戶訊息，只有長度
      expect(logString).not.toContain('我的密碼是 secret123');
      expect(logString).toContain('"userMessageLength": 15');
    });
  });

  describe('log', () => {
    it('should log error without returning message', () => {
      const error = new Error('Test error');
      const context: ErrorContext = {
        operation: 'testOperation'
      };

      ErrorHandler.log(error, context);
      
      expect(console.error).toHaveBeenCalledWith(
        'Error occurred:',
        expect.stringContaining('"operation": "testOperation"')
      );
    });
  });
});