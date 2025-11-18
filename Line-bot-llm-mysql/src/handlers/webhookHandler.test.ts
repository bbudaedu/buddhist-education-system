import express from 'express';
import * as line from '@line/bot-sdk';

// Mock the config first
jest.mock('../config/index', () => ({
  lineConfig: {
    channelSecret: 'test-channel-secret',
    channelAccessToken: 'test-access-token'
  }
}));

// Mock the services
jest.mock('../services/geminiService', () => ({
  geminiService: {
    processUserQuery: jest.fn().mockResolvedValue({
      text: '找到 1 本相關書籍：金剛經',
      books: [{
        book_id: 1,
        title: '金剛經',
        quantity: 5,
        shelf_location: 'A1-23',
        library_branch: '總館'
      }]
    })
  }
}));

jest.mock('../services/lineMessagingService', () => ({
  lineMessagingService: {
    sendBookQueryResponse: jest.fn().mockResolvedValue(undefined),
    sendErrorMessage: jest.fn().mockResolvedValue(undefined),
    sendWelcomeMessage: jest.fn().mockResolvedValue(undefined)
  }
}));

// Mock LINE SDK
jest.mock('@line/bot-sdk', () => ({
  validateSignature: jest.fn().mockReturnValue(true),
  middleware: jest.fn().mockReturnValue((_req: any, _res: any, next: any) => next())
}));

// Import after mocking
import { webhookHandler } from './webhookHandler';

describe('WebhookHandler', () => {
  let mockReq: Partial<express.Request>;
  let mockRes: Partial<express.Response>;

  beforeEach(() => {
    mockReq = {
      body: {
        events: [{
          type: 'message',
          message: {
            type: 'text',
            text: '有沒有金剛經相關的書？'
          },
          replyToken: 'test-reply-token'
        }]
      },
      get: jest.fn().mockReturnValue('test-signature')
    };

    mockRes = {
      status: jest.fn().mockReturnThis(),
      send: jest.fn().mockReturnThis()
    };

    jest.clearAllMocks();
  });

  describe('handleWebhook', () => {
    it('should handle webhook request successfully', async () => {
      await webhookHandler.handleWebhook(
        mockReq as express.Request,
        mockRes as express.Response
      );

      expect(mockRes.status).toHaveBeenCalledWith(200);
      expect(mockRes.send).toHaveBeenCalledWith('OK');
    });

    it('should reject invalid signature', async () => {
      (line.validateSignature as jest.Mock).mockReturnValue(false);

      await webhookHandler.handleWebhook(
        mockReq as express.Request,
        mockRes as express.Response
      );

      expect(mockRes.status).toHaveBeenCalledWith(401);
      expect(mockRes.send).toHaveBeenCalledWith('Unauthorized');
    });

    it('should handle missing signature', async () => {
      (mockReq.get as jest.Mock).mockReturnValue(undefined);

      await webhookHandler.handleWebhook(
        mockReq as express.Request,
        mockRes as express.Response
      );

      expect(mockRes.status).toHaveBeenCalledWith(401);
      expect(mockRes.send).toHaveBeenCalledWith('Unauthorized');
    });
  });

  describe('validateSignature', () => {
    it('should validate signature correctly', () => {
      (line.validateSignature as jest.Mock).mockReturnValue(true);
      
      const result = webhookHandler.validateSignature('test-body', 'test-signature');
      
      expect(line.validateSignature).toHaveBeenCalledWith(
        'test-body',
        expect.any(String),
        'test-signature'
      );
      expect(result).toBe(true);
    });

    it('should handle validation errors', () => {
      (line.validateSignature as jest.Mock).mockImplementation(() => {
        throw new Error('Validation failed');
      });

      const result = webhookHandler.validateSignature('test-body', 'test-signature');
      expect(result).toBe(false);
    });
  });

  describe('getMiddleware', () => {
    it('should return LINE middleware', () => {
      const middleware = webhookHandler.getMiddleware();
      
      expect(line.middleware).toHaveBeenCalledWith({
        channelSecret: expect.any(String)
      });
      expect(middleware).toBeDefined();
    });
  });
});