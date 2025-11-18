import { GeminiService } from './geminiService';
import { Book } from '../types/book';

// Mock the database service
jest.mock('./databaseService', () => ({
  databaseService: {
    searchBooks: jest.fn()
  }
}));

// Mock the config
jest.mock('../config', () => ({
  geminiConfig: {
    apiKey: 'test-api-key',
    model: 'gemini-2.5-pro',
    maxOutputTokens: 1024,
    temperature: 0.7
  }
}));

// Mock GoogleGenerativeAI
jest.mock('@google/generative-ai', () => ({
  GoogleGenerativeAI: jest.fn().mockImplementation(() => ({
    getGenerativeModel: jest.fn().mockReturnValue({
      generateContent: jest.fn()
    })
  }))
}));

describe('GeminiService', () => {
  let geminiService: GeminiService;

  beforeEach(() => {
    jest.clearAllMocks();
    geminiService = new GeminiService();
  });

  describe('extractSearchQuery', () => {
    it('should extract search query from SEARCH: prefix', () => {
      const service = geminiService as any;
      const result = service.extractSearchQuery('SEARCH:金剛經');
      expect(result).toBe('金剛經');
    });

    it('should return null for non-search responses', () => {
      const service = geminiService as any;
      const result = service.extractSearchQuery('您好！我是書庫助理');
      expect(result).toBeNull();
    });

    it('should handle SEARCH: with extra whitespace', () => {
      const service = geminiService as any;
      const result = service.extractSearchQuery('SEARCH:  金剛經  ');
      expect(result).toBe('金剛經');
    });
  });

  describe('generateFinalResponse', () => {
    it('should generate response with found books', async () => {
      const mockBooks: Book[] = [
        {
          book_id: 1,
          title: '金剛般若波羅蜜經',
          quantity: 3,
          shelf_location: 'A1-23',
          library_branch: '總館'
        }
      ];

      const service = geminiService as any;
      const mockModel = {
        generateContent: jest.fn().mockResolvedValue({
          response: {
            text: () => '找到了金剛經相關書籍：金剛般若波羅蜜經，位於總館A1-23，庫存3本。'
          }
        })
      };
      service.model = mockModel;

      const result = await service.generateFinalResponse('有沒有金剛經？', '金剛經', mockBooks);
      
      expect(result).toContain('金剛般若波羅蜜經');
      expect(mockModel.generateContent).toHaveBeenCalled();
    });

    it('should handle empty search results', async () => {
      const service = geminiService as any;
      const mockModel = {
        generateContent: jest.fn().mockResolvedValue({
          response: {
            text: () => '抱歉，沒有找到相關書籍。'
          }
        })
      };
      service.model = mockModel;

      const result = await service.generateFinalResponse('有沒有不存在的書？', '不存在的書', []);
      
      expect(result).toContain('沒有找到');
    });
  });

  describe('testConnection', () => {
    it('should return true when connection is successful', async () => {
      const service = geminiService as any;
      const mockModel = {
        generateContent: jest.fn().mockResolvedValue({
          response: {
            text: () => '測試成功'
          }
        })
      };
      service.model = mockModel;

      const result = await service.testConnection();
      expect(result).toBe(true);
    });

    it('should return false when connection fails', async () => {
      const service = geminiService as any;
      const mockModel = {
        generateContent: jest.fn().mockRejectedValue(new Error('Connection failed'))
      };
      service.model = mockModel;

      const result = await service.testConnection();
      expect(result).toBe(false);
    });
  });
});