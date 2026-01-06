/**
 * Member Routes
 * 會員 API 路由
 */

import { Router, Request, Response } from 'express';
import { memberService } from '../services/memberService';
import { UpdatePreferencesRequest, SendVerificationRequest, VerifyEmailRequest } from '../types/member';
import { notificationChannelsConfig } from '../config/index';

const router = Router();

// LINE Profile 介面
interface LineProfile {
    userId: string;
    displayName?: string;
    pictureUrl?: string;
}

// 驗證 LINE Access Token
async function verifyLineToken(req: Request): Promise<string | null> {
    const authHeader = req.headers.authorization;
    if (!authHeader?.startsWith('Bearer ')) {
        return null;
    }

    const accessToken = authHeader.substring(7);

    try {
        const response = await fetch('https://api.line.me/v2/profile', {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        if (!response.ok) {
            return null;
        }

        const profile = await response.json() as LineProfile;
        return profile.userId;
    } catch (error) {
        console.error('Token verification failed:', error);
        return null;
    }
}

/**
 * GET /api/member/profile
 */
router.get('/profile', async (req: Request, res: Response): Promise<void> => {
    try {
        const lineUserId = await verifyLineToken(req);
        if (!lineUserId) {
            res.status(401).json({ error: '未授權' });
            return;
        }

        const profile = await memberService.getMemberProfile(lineUserId);
        if (!profile) {
            res.status(404).json({ error: '用戶不存在' });
            return;
        }

        res.json(profile);
    } catch (error) {
        console.error('Get profile error:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});

/**
 * PUT /api/member/profile
 */
router.put('/profile', async (req: Request, res: Response): Promise<void> => {
    try {
        const lineUserId = await verifyLineToken(req);
        if (!lineUserId) {
            res.status(401).json({ error: '未授權' });
            return;
        }

        const { displayName, pictureUrl, email } = req.body;
        const success = await memberService.updateMemberProfile(lineUserId, {
            displayName,
            pictureUrl,
            email
        });

        res.json({ success });
    } catch (error) {
        console.error('Update profile error:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});

/**
 * GET /api/member/preferences
 */
router.get('/preferences', async (req: Request, res: Response): Promise<void> => {
    try {
        const lineUserId = await verifyLineToken(req);
        if (!lineUserId) {
            res.status(401).json({ error: '未授權' });
            return;
        }

        const [preferences, profile] = await Promise.all([
            memberService.getUserPreferences(lineUserId),
            memberService.getMemberProfile(lineUserId)
        ]);

        res.json({
            ...preferences,
            email: profile?.email,
            emailVerified: profile?.emailVerified,
            emailNotificationEnabled: profile?.emailNotificationEnabled
        });
    } catch (error) {
        console.error('Get preferences error:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});

/**
 * PUT /api/member/preferences
 */
router.put('/preferences', async (req: Request, res: Response): Promise<void> => {
    try {
        const lineUserId = await verifyLineToken(req);
        if (!lineUserId) {
            res.status(401).json({ error: '未授權' });
            return;
        }

        const prefs: UpdatePreferencesRequest = req.body;
        const success = await memberService.upsertUserPreferences(lineUserId, {
            notificationChannels: prefs.notificationChannels ?? [],
            preferredContentTypes: prefs.preferredContentTypes ?? [],
            notificationFrequency: prefs.notificationFrequency ?? 'realtime',
            quietHoursStart: prefs.quietHoursStart ?? null,
            quietHoursEnd: prefs.quietHoursEnd ?? null
        });

        res.json({ success });
    } catch (error) {
        console.error('Update preferences error:', error);
        res.status(500).json({ error: '伺服器錯誤' });
    }
});

/**
 * POST /api/member/send-verification
 */
router.post('/send-verification', async (req: Request, res: Response): Promise<void> => {
    try {
        const lineUserId = await verifyLineToken(req);
        if (!lineUserId) {
            res.status(401).json({ error: '未授權' });
            return;
        }

        const { email }: SendVerificationRequest = req.body;
        if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            res.status(400).json({ error: '無效的 Email 地址' });
            return;
        }

        // 產生 6 位數驗證碼
        const token = Math.floor(100000 + Math.random() * 900000).toString();

        // 儲存驗證碼
        await memberService.setEmailVerificationToken(lineUserId, email, token);

        // 呼叫 Python email 服務發送驗證碼
        const { spawn } = await import('child_process');
        const path = await import('path');
        const ebookDir = path.resolve(process.cwd(), '..', 'ebook');

        const pythonScript = `
import sys
sys.path.insert(0, '.')
from email_notification_service import send_verification_email
result = send_verification_email('${email}', '${token}', 'LINE 用戶')
print('SUCCESS' if result else 'FAILED')
`;

        const python = spawn('python', ['-c', pythonScript], {
            cwd: ebookDir
        });

        let output = '';
        python.stdout.on('data', (data: Buffer) => { output += data.toString(); });
        python.stderr.on('data', (data: Buffer) => { console.error('Python error:', data.toString()); });

        python.on('close', (code: number) => {
            if (code === 0 && output.includes('SUCCESS')) {
                console.log(`[Email Verification] Sent to ${email}`);
            } else {
                console.error(`[Email Verification] Failed for ${email}`);
            }
        });

        res.json({ success: true, message: '驗證碼已發送' });
    } catch (error) {
        console.error('Send verification error:', error);
        res.status(500).json({ error: '發送失敗' });
    }
});

/**
 * POST /api/member/verify-email
 */
router.post('/verify-email', async (req: Request, res: Response): Promise<void> => {
    try {
        const lineUserId = await verifyLineToken(req);
        if (!lineUserId) {
            res.status(401).json({ error: '未授權' });
            return;
        }

        const { email, code }: VerifyEmailRequest = req.body;
        if (!email || !code) {
            res.status(400).json({ error: '缺少必要參數' });
            return;
        }

        const success = await memberService.verifyEmail(lineUserId, email, code);
        if (!success) {
            res.status(400).json({ error: '驗證碼錯誤或已過期' });
            return;
        }

        res.json({ success: true, message: 'Email 驗證成功' });
    } catch (error) {
        console.error('Verify email error:', error);
        res.status(500).json({ error: '驗證失敗' });
    }
});

/**
 * GET /api/member/notification-channels
 * 返回可用的通知管道列表（公開 API，不需認證）
 * 用於學員中心動態顯示/隱藏通知選項
 */
router.get('/notification-channels', (_req: Request, res: Response): void => {
    res.json({
        channels: {
            line: notificationChannelsConfig.lineEnabled,
            email: notificationChannelsConfig.emailEnabled,
            webpush: notificationChannelsConfig.webpushEnabled
        }
    });
});

export default router;
