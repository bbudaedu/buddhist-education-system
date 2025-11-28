import * as line from '@line/bot-sdk';
import { lineMessagingService } from '../services/lineMessagingService';

/**
 * Welcome Handler
 * 處理新用戶加入好友時的歡迎訊息
 */
export class WelcomeHandler {
    /**
     * 發送歡迎訊息給新用戶
     * @param userId - LINE 用戶 ID
     */
    async sendWelcomeMessage(userId: string): Promise<void> {
        try {
            const welcomeMessage = this.createWelcomeFlexMessage();
            await lineMessagingService.pushMessage(userId, [welcomeMessage]);
            console.log(`Welcome message sent to user: ${userId}`);
        } catch (error) {
            console.error('Error sending welcome message:', error);
            throw error;
        }
    }

    /**
     * 建立歡迎Flex Message
     */
    private createWelcomeFlexMessage(): line.FlexMessage {
        return {
            type: 'flex',
            altText: '歡迎加入佛陀教育基金會 LINE Bot！',
            contents: {
                type: 'bubble',
                hero: {
                    type: 'image',
                    url: 'https://www.budaedu.org/img/logo.png',
                    size: 'full',
                    aspectRatio: '20:13',
                    aspectMode: 'cover'
                },
                body: {
                    type: 'box',
                    layout: 'vertical',
                    contents: [
                        {
                            type: 'text',
                            text: '🙏 歡迎您',
                            weight: 'bold',
                            size: 'xl',
                            color: '#1E3A8A'
                        },
                        {
                            type: 'text',
                            text: '感謝您加入佛陀教育基金會',
                            size: 'sm',
                            color: '#6B7280',
                            margin: 'md'
                        },
                        {
                            type: 'separator',
                            margin: 'xl'
                        },
                        {
                            type: 'box',
                            layout: 'vertical',
                            margin: 'lg',
                            spacing: 'sm',
                            contents: [
                                {
                                    type: 'text',
                                    text: '📚 本服務提供：',
                                    weight: 'bold',
                                    size: 'sm',
                                    color: '#374151'
                                },
                                {
                                    type: 'box',
                                    layout: 'baseline',
                                    spacing: 'sm',
                                    contents: [
                                        {
                                            type: 'text',
                                            text: '•',
                                            color: '#9CA3AF',
                                            size: 'sm',
                                            flex: 0
                                        },
                                        {
                                            type: 'text',
                                            text: '最新法寶書籍通知',
                                            color: '#4B5563',
                                            size: 'sm',
                                            flex: 1,
                                            wrap: true
                                        }
                                    ]
                                },
                                {
                                    type: 'box',
                                    layout: 'baseline',
                                    spacing: 'sm',
                                    contents: [
                                        {
                                            type: 'text',
                                            text: '•',
                                            color: '#9CA3AF',
                                            size: 'sm',
                                            flex: 0
                                        },
                                        {
                                            type: 'text',
                                            text: '最新影音課程資訊',
                                            color: '#4B5563',
                                            size: 'sm',
                                            flex: 1,
                                            wrap: true
                                        }
                                    ]
                                },
                                {
                                    type: 'box',
                                    layout: 'baseline',
                                    spacing: 'sm',
                                    contents: [
                                        {
                                            type: 'text',
                                            text: '•',
                                            color: '#9CA3AF',
                                            size: 'sm',
                                            flex: 0
                                        },
                                        {
                                            type: 'text',
                                            text: '課程停課通知',
                                            color: '#4B5563',
                                            size: 'sm',
                                            flex: 1,
                                            wrap: true
                                        }
                                    ]
                                },
                                {
                                    type: 'box',
                                    layout: 'baseline',
                                    spacing: 'sm',
                                    contents: [
                                        {
                                            type: 'text',
                                            text: '•',
                                            color: '#9CA3AF',
                                            size: 'sm',
                                            flex: 0
                                        },
                                        {
                                            type: 'text',
                                            text: '基金會最新消息',
                                            color: '#4B5563',
                                            size: 'sm',
                                            flex: 1,
                                            wrap: true
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                footer: {
                    type: 'box',
                    layout: 'vertical',
                    spacing: 'sm',
                    contents: [
                        {
                            type: 'button',
                            style: 'primary',
                            height: 'sm',
                            action: {
                                type: 'message',
                                label: '🔔 查看訂閱選項',
                                text: '訂閱'
                            },
                            color: '#1E40AF'
                        },
                        {
                            type: 'button',
                            style: 'link',
                            height: 'sm',
                            action: {
                                type: 'uri',
                                label: '🌐 訪問官網',
                                uri: 'https://www.budaedu.org'
                            }
                        },
                        {
                            type: 'box',
                            layout: 'vertical',
                            contents: [
                                {
                                    type: 'text',
                                    text: '💡 輸入「幫助」查看更多功能',
                                    color: '#9CA3AF',
                                    size: 'xxs',
                                    align: 'center',
                                    margin: 'md'
                                }
                            ]
                        }
                    ],
                    flex: 0
                }
            }
        };
    }
}

export const welcomeHandler = new WelcomeHandler();
