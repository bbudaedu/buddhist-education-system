import * as line from '@line/bot-sdk';

/**
 * Subscription Carousel Template
 * 建立訂閱類型的輪播訊息模板
 */
export class SubscriptionCarouselTemplate {
    /**
     * 建立訂閱類型輪播
     */
    createSubscriptionCarousel(): line.FlexMessage {
        return {
            type: 'flex',
            altText: '訂閱管理 - 選擇您想訂閱的類型',
            contents: {
                type: 'carousel',
                contents: [
                    this.createNewsSubscriptionBubble(),
                    this.createBooksSubscriptionBubble(),
                    this.createVideosSubscriptionBubble(),
                    this.createCancellationSubscriptionBubble()
                ]
            }
        };
    }

    /**
     * 最新消息訂閱卡片
     */
    private createNewsSubscriptionBubble(): line.FlexBubble {
        return {
            type: 'bubble',
            size: 'micro',
            hero: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'text',
                        text: '📰',
                        size: '4xl',
                        align: 'center',
                        gravity: 'center'
                    }
                ],
                backgroundColor: '#EFF6FF',
                height: '100px'
            },
            body: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'text',
                        text: '最新消息',
                        weight: 'bold',
                        size: 'md',
                        align: 'center'
                    },
                    {
                        type: 'text',
                        text: '基金會公告與活動資訊',
                        size: 'xs',
                        color: '#6B7280',
                        align: 'center',
                        margin: 'sm',
                        wrap: true
                    },
                    {
                        type: 'box',
                        layout: 'vertical',
                        contents: [
                            {
                                type: 'text',
                                text: '範例：',
                                size: 'xxs',
                                color: '#9CA3AF',
                                margin: 'md'
                            },
                            {
                                type: 'text',
                                text: '「農曆新年休館公告」',
                                size: 'xxs',
                                color: '#4B5563',
                                margin: 'xs',
                                wrap: true
                            }
                        ],
                        backgroundColor: '#F9FAFB',
                        paddingAll: 'sm',
                        margin: 'md',
                        cornerRadius: 'md'
                    }
                ],
                paddingAll: 'lg'
            },
            footer: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'button',
                        action: {
                            type: 'message',
                            label: '訂閱',
                            text: '訂閱最新消息'
                        },
                        style: 'primary',
                        color: '#1E40AF',
                        height: 'sm'
                    }
                ],
                paddingAll: 'sm'
            }
        };
    }

    /**
     * 新書通知訂閱卡片
     */
    private createBooksSubscriptionBubble(): line.FlexBubble {
        return {
            type: 'bubble',
            size: 'micro',
            hero: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'text',
                        text: '📚',
                        size: '4xl',
                        align: 'center',
                        gravity: 'center'
                    }
                ],
                backgroundColor: '#F0FDF4',
                height: '100px'
            },
            body: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'text',
                        text: '新書通知',
                        weight: 'bold',
                        size: 'md',
                        align: 'center'
                    },
                    {
                        type: 'text',
                        text: '最新上架的法寶書籍',
                        size: 'xs',
                        color: '#6B7280',
                        align: 'center',
                        margin: 'sm',
                        wrap: true
                    },
                    {
                        type: 'box',
                        layout: 'vertical',
                        contents: [
                            {
                                type: 'text',
                                text: '範例：',
                                size: 'xxs',
                                color: '#9CA3AF',
                                margin: 'md'
                            },
                            {
                                type: 'text',
                                text: '「金剛經講記 已上架」',
                                size: 'xxs',
                                color: '#4B5563',
                                margin: 'xs',
                                wrap: true
                            }
                        ],
                        backgroundColor: '#F9FAFB',
                        paddingAll: 'sm',
                        margin: 'md',
                        cornerRadius: 'md'
                    }
                ],
                paddingAll: 'lg'
            },
            footer: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'button',
                        action: {
                            type: 'message',
                            label: '訂閱',
                            text: '訂閱新書'
                        },
                        style: 'primary',
                        color: '#16A34A',
                        height: 'sm'
                    }
                ],
                paddingAll: 'sm'
            }
        };
    }

    /**
     * 最新影音訂閱卡片
     */
    private createVideosSubscriptionBubble(): line.FlexBubble {
        return {
            type: 'bubble',
            size: 'micro',
            hero: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'text',
                        text: '🎥',
                        size: '4xl',
                        align: 'center',
                        gravity: 'center'
                    }
                ],
                backgroundColor: '#FEF3C7',
                height: '100px'
            },
            body: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'text',
                        text: '最新影音',
                        weight: 'bold',
                        size: 'md',
                        align: 'center'
                    },
                    {
                        type: 'text',
                        text: '直播與最新影音課程',
                        size: 'xs',
                        color: '#6B7280',
                        align: 'center',
                        margin: 'sm',
                        wrap: true
                    },
                    {
                        type: 'box',
                        layout: 'vertical',
                        contents: [
                            {
                                type: 'text',
                                text: '範例：',
                                size: 'xxs',
                                color: '#9CA3AF',
                                margin: 'md'
                            },
                            {
                                type: 'text',
                                text: '「今日直播：大乘起信論」',
                                size: 'xxs',
                                color: '#4B5563',
                                margin: 'xs',
                                wrap: true
                            }
                        ],
                        backgroundColor: '#F9FAFB',
                        paddingAll: 'sm',
                        margin: 'md',
                        cornerRadius: 'md'
                    }
                ],
                paddingAll: 'lg'
            },
            footer: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'button',
                        action: {
                            type: 'message',
                            label: '訂閱',
                            text: '訂閱最新影音'
                        },
                        style: 'primary',
                        color: '#D97706',
                        height: 'sm'
                    }
                ],
                paddingAll: 'sm'
            }
        };
    }

    /**
     * 停課通知訂閱卡片
     */
    private createCancellationSubscriptionBubble(): line.FlexBubble {
        return {
            type: 'bubble',
            size: 'micro',
            hero: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'text',
                        text: '⚠️',
                        size: '4xl',
                        align: 'center',
                        gravity: 'center'
                    }
                ],
                backgroundColor: '#FEE2E2',
                height: '100px'
            },
            body: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'text',
                        text: '停課通知',
                        weight: 'bold',
                        size: 'md',
                        align: 'center'
                    },
                    {
                        type: 'text',
                        text: '課程異動與停課資訊',
                        size: 'xs',
                        color: '#6B7280',
                        align: 'center',
                        margin: 'sm',
                        wrap: true
                    },
                    {
                        type: 'box',
                        layout: 'vertical',
                        contents: [
                            {
                                type: 'text',
                                text: '範例：',
                                size: 'xxs',
                                color: '#9CA3AF',
                                margin: 'md'
                            },
                            {
                                type: 'text',
                                text: '「週三佛學講座暫停一次」',
                                size: 'xxs',
                                color: '#4B5563',
                                margin: 'xs',
                                wrap: true
                            }
                        ],
                        backgroundColor: '#F9FAFB',
                        paddingAll: 'sm',
                        margin: 'md',
                        cornerRadius: 'md'
                    }
                ],
                paddingAll: 'lg'
            },
            footer: {
                type: 'box',
                layout: 'vertical',
                contents: [
                    {
                        type: 'button',
                        action: {
                            type: 'message',
                            label: '訂閱',
                            text: '訂閱停課通知'
                        },
                        style: 'primary',
                        color: '#DC2626',
                        height: 'sm'
                    }
                ],
                paddingAll: 'sm'
            }
        };
    }
}

export const subscriptionCarouselTemplate = new SubscriptionCarouselTemplate();
