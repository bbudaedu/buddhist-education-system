import { Request, Response } from 'express';
import {
  WebsiteMonitoringNotificationService,
  WebsiteMonitoringNotification,
} from '../services/websiteMonitoringNotificationService';

/**
 * Notification Handler
 * 處理來自外部系統（如 Python 網站監控）的通知請求
 */

const notificationService = new WebsiteMonitoringNotificationService();

/**
 * 處理網站監控通知
 */
export async function handleWebsiteMonitoringNotification(
  req: Request,
  res: Response
): Promise<void> {
  try {
    console.log('📥 Received website monitoring notification request');
    console.log('📦 Payload:', JSON.stringify(req.body, null, 2));

    // 驗證請求內容
    const notification = req.body as WebsiteMonitoringNotification;

    if (!notification.type || !notification.message) {
      res.status(400).json({
        success: false,
        error: 'Missing required fields: type and message',
      });
      return;
    }

    // 處理通知
    const result = await notificationService.handleNotification(notification);

    if (result.success) {
      res.status(200).json({
        success: true,
        messagesSent: result.messagesSent,
        message: 'Notification processed successfully',
      });
    } else {
      res.status(500).json({
        success: false,
        error: result.error || 'Failed to process notification',
      });
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('❌ Error in notification handler:', errorMessage);

    res.status(500).json({
      success: false,
      error: errorMessage,
    });
  }
}

/**
 * 發送測試通知
 */
export async function handleTestNotification(req: Request, res: Response): Promise<void> {
  try {
    const { userId } = req.body;

    if (!userId) {
      res.status(400).json({
        success: false,
        error: 'Missing required field: userId',
      });
      return;
    }

    const success = await notificationService.sendTestNotification(userId);

    if (success) {
      res.status(200).json({
        success: true,
        message: 'Test notification sent successfully',
      });
    } else {
      res.status(500).json({
        success: false,
        error: 'Failed to send test notification',
      });
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('❌ Error sending test notification:', errorMessage);

    res.status(500).json({
      success: false,
      error: errorMessage,
    });
  }
}

/**
 * 健康檢查
 */
export function handleHealthCheck(_req: Request, res: Response): void {
  res.status(200).json({
    success: true,
    service: 'LINE Bot Notification Service',
    status: 'healthy',
    timestamp: new Date().toISOString(),
  });
}
