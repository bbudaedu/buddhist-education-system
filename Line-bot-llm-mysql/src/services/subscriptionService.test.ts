import { SubscriptionService } from './subscriptionService';
import { DeliveryErrorType } from '../types/subscription';

// Mock mysql2/promise
jest.mock('mysql2/promise');

describe('SubscriptionService', () => {
  let subscriptionService: SubscriptionService;
  let mockPool: any;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock pool methods
    mockPool = {
      execute: jest.fn(),
      end: jest.fn()
    };

    // Mock mysql.createPool to return our mock pool
    const mysql = require('mysql2/promise');
    mysql.createPool = jest.fn().mockReturnValue(mockPool);

    subscriptionService = new SubscriptionService();
  });

  describe('subscribeUser', () => {
    it('should successfully subscribe a new user', async () => {
      // Mock successful database execution
      mockPool.execute.mockResolvedValue([{ affectedRows: 1 }]);

      const result = await subscriptionService.subscribeUser('test-user-id', 'Test User');

      expect(result).toBe(true);
      expect(mockPool.execute).toHaveBeenCalledWith(
        expect.stringContaining('INSERT INTO user_subscriptions'),
        expect.arrayContaining(['test-user-id', 'Test User', expect.any(String)])
      );
    });

    it('should handle database errors gracefully', async () => {
      // Mock database error
      mockPool.execute.mockRejectedValue(new Error('Database error'));

      const result = await subscriptionService.subscribeUser('test-user-id');

      expect(result).toBe(false);
    });
  });

  describe('isUserSubscribed', () => {
    it('should return true for subscribed user', async () => {
      // Mock user is subscribed
      mockPool.execute.mockResolvedValue([[{ is_subscribed: true }]]);

      const result = await subscriptionService.isUserSubscribed('test-user-id');

      expect(result).toBe(true);
      expect(mockPool.execute).toHaveBeenCalledWith(
        'SELECT is_subscribed FROM user_subscriptions WHERE line_user_id = ?',
        ['test-user-id']
      );
    });

    it('should return false for unsubscribed user', async () => {
      // Mock user is not subscribed
      mockPool.execute.mockResolvedValue([[{ is_subscribed: false }]]);

      const result = await subscriptionService.isUserSubscribed('test-user-id');

      expect(result).toBe(false);
    });

    it('should return false for non-existent user', async () => {
      // Mock no user found
      mockPool.execute.mockResolvedValue([[]]);

      const result = await subscriptionService.isUserSubscribed('test-user-id');

      expect(result).toBe(false);
    });
  });

  describe('unsubscribeUser', () => {
    it('should successfully unsubscribe a user', async () => {
      // Mock successful unsubscribe
      mockPool.execute.mockResolvedValue([{ affectedRows: 1 }]);

      const result = await subscriptionService.unsubscribeUser('test-user-id');

      expect(result).toBe(true);
      expect(mockPool.execute).toHaveBeenCalledWith(
        expect.stringContaining('UPDATE user_subscriptions'),
        ['test-user-id']
      );
    });

    it('should return false when user not found', async () => {
      // Mock no rows affected
      mockPool.execute.mockResolvedValue([{ affectedRows: 0 }]);

      const result = await subscriptionService.unsubscribeUser('test-user-id');

      expect(result).toBe(false);
    });
  });

  describe('recordDeliveryFailure', () => {
    it('should record delivery failure successfully', async () => {
      mockPool.execute.mockResolvedValue([{ insertId: 1 }]);

      await subscriptionService.recordDeliveryFailure({
        lineUserId: 'test-user-id',
        errorType: DeliveryErrorType.USER_BLOCKED,
        errorMessage: 'User blocked the bot',
        isRetryable: false
      });

      expect(mockPool.execute).toHaveBeenCalledWith(
        expect.stringContaining('INSERT INTO delivery_failures'),
        expect.arrayContaining([
          null, // notificationLogId
          'test-user-id',
          DeliveryErrorType.USER_BLOCKED,
          'User blocked the bot',
          false,
          0 // retryCount
        ])
      );
    });
  });
});