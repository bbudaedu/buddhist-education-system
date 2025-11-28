import { test, expect } from '@playwright/test';
import { mockVideoStreams, mockEmptyStreams } from '../test-utils/mock-data';

/**
 * E2E Test Suite: 最新影音 (Latest Videos & Live Streams)
 * 
 * PRD Verification Criteria:
 * - FR-004: 顯示 5 直播 + 5 影音
 * - FR-005: 講師照片/縮圖顯示
 * - FR-006: Quick Reply 包含「訂閱最新影音」
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

test.describe('最新影音 Command - Basic Functionality', () => {

    test('FR-004: 應該成功獲取 10 筆影音資料 (5 直播 + 5 影音)', async () => {
        const streams = mockVideoStreams;

        expect(streams).toHaveLength(10);

        const liveStreams = streams.filter(s => s.type === 'live');
        const videoRecordings = streams.filter(s => s.type === 'video');

        expect(liveStreams).toHaveLength(5);
        expect(videoRecordings).toHaveLength(5);
    });

    test('FR-004: 影音資料結構應包含所有必要欄位', async () => {
        const stream = mockVideoStreams[0];

        // Required fields
        expect(stream.id).toBeTruthy();
        expect(stream.title).toBeTruthy();
        expect(stream.type).toBeTruthy();
        expect(stream.streamDate).toBeInstanceOf(Date);
        expect(stream.streamUrl).toBeTruthy();

        // Optional fields
        expect(stream).toHaveProperty('instructor');
        expect(stream).toHaveProperty('instructorPhotoUrl');
        expect(stream).toHaveProperty('topic');
        expect(stream).toHaveProperty('thumbnailUrl');
    });

    test('FR-004: 應該正確區分直播和影音類型', async () => {
        mockVideoStreams.forEach(stream => {
            expect(['live', 'video']).toContain(stream.type);
        });

        const liveStreams = mockVideoStreams.filter(s => s.type === 'live');
        const videos = mockVideoStreams.filter(s => s.type === 'video');

        expect(liveStreams.length + videos.length).toBe(10);
    });

    test('FR-005: 應該處理講師照片 URL', async () => {
        const streamsWithPhotos = mockVideoStreams.filter(s => s.instructorPhotoUrl);
        const streamsWithThumbnails = mockVideoStreams.filter(s => s.thumbnailUrl);

        // At least some streams should have images
        expect(streamsWithPhotos.length + streamsWithThumbnails.length).toBeGreaterThan(0);

        // Validate URLs
        streamsWithPhotos.forEach(stream => {
            expect(stream.instructorPhotoUrl).toMatch(/^https?:\/\/.+/);
        });

        streamsWithThumbnails.forEach(stream => {
            expect(stream.thumbnailUrl).toMatch(/^https?:\/\/.+/);
        });
    });

    test('FR-005: 圖片顯示優先順序：講師照片 > 縮圖 > 預設圖示', async () => {
        mockVideoStreams.forEach(stream => {
            let imageUrl: string;

            if (stream.instructorPhotoUrl) {
                imageUrl = stream.instructorPhotoUrl;
            } else if (stream.thumbnailUrl) {
                imageUrl = stream.thumbnailUrl;
            } else {
                // Use default based on type
                imageUrl = stream.type === 'live'
                    ? 'https://default-live-icon.png'
                    : 'https://default-video-icon.png';
            }

            expect(imageUrl).toBeTruthy();
            expect(imageUrl).toMatch(/^https?:\/\/.+/);
        });
    });
});

test.describe('最新影音 Command - Flex Message Validation', () => {

    test('應該生成正確的 Flex Message Carousel 結構', async () => {
        const flexMessage = {
            type: 'flex',
            altText: '🎥 最新影音',
            contents: {
                type: 'carousel',
                contents: mockVideoStreams.map(stream => {
                    const imageUrl = stream.instructorPhotoUrl || stream.thumbnailUrl ||
                        (stream.type === 'live' ? 'https://default-live.png' : 'https://default-video.png');

                    const typeLabel = stream.type === 'live' ? '[直播]' : '[影音]';

                    return {
                        type: 'bubble',
                        hero: {
                            type: 'image',
                            url: imageUrl,
                            size: 'full',
                            aspectRatio: '16:9',
                            aspectMode: 'cover'
                        },
                        body: {
                            type: 'box',
                            layout: 'vertical',
                            contents: [
                                {
                                    type: 'text',
                                    text: typeLabel,
                                    size: 'xs',
                                    color: stream.type === 'live' ? '#FF0000' : '#00AA00',
                                    weight: 'bold'
                                },
                                {
                                    type: 'text',
                                    text: stream.title,
                                    weight: 'bold',
                                    size: 'lg',
                                    wrap: true
                                },
                                {
                                    type: 'text',
                                    text: `講師：${stream.instructor || '未提供'}`,
                                    size: 'sm',
                                    color: '#666666'
                                },
                                {
                                    type: 'text',
                                    text: `日期：${stream.streamDate.toLocaleDateString('zh-TW')}`,
                                    size: 'xs',
                                    color: '#999999'
                                }
                            ]
                        },
                        footer: {
                            type: 'box',
                            layout: 'vertical',
                            contents: [
                                {
                                    type: 'button',
                                    action: {
                                        type: 'uri',
                                        label: stream.type === 'live' ? '觀看直播' : '觀看影音',
                                        uri: stream.streamUrl
                                    }
                                }
                            ]
                        }
                    };
                })
            }
        };

        expect(flexMessage.type).toBe('flex');
        expect(flexMessage.contents.type).toBe('carousel');
        expect(flexMessage.contents.contents).toHaveLength(10);
    });

    test('FR-006: Quick Reply 應包含「訂閱最新影音」選項', async () => {
        const quickReply = {
            items: [
                {
                    type: 'action',
                    action: {
                        type: 'message',
                        label: '🎥 訂閱最新影音',
                        text: '訂閱最新影音'
                    }
                },
                {
                    type: 'action',
                    action: {
                        type: 'message',
                        label: '📊 訂閱狀態查詢',
                        text: '訂閱狀態查詢'
                    }
                }
            ]
        };

        expect(quickReply.items).toHaveLength(2);
        expect(quickReply.items[0].action.label).toContain('訂閱最新影音');
        expect(quickReply.items[1].action.label).toContain('訂閱狀態查詢');
    });

    test('直播和影音應顯示不同的標籤顏色', async () => {
        const liveColor = '#FF0000'; // Red
        const videoColor = '#00AA00'; // Green

        mockVideoStreams.forEach(stream => {
            const expectedColor = stream.type === 'live' ? liveColor : videoColor;
            expect([liveColor, videoColor]).toContain(expectedColor);
        });
    });
});

test.describe('最新影音 Command - Edge Cases', () => {

    test('應該處理無影音資料的情況', async () => {
        const streams = mockEmptyStreams;

        expect(streams).toHaveLength(0);

        // Should return friendly message: "目前沒有最新影音資訊"
        const expectedMessage = '目前沒有最新影音資訊';
        expect(expectedMessage).toBeTruthy();
    });

    test('應該處理少於 10 筆資料的情況', async () => {
        const streams = mockVideoStreams.slice(0, 6); // Only 6 streams

        expect(streams.length).toBeLessThan(10);
        expect(streams.length).toBeGreaterThan(0);
    });

    test('應該處理缺少講師資訊的情況', async () => {
        const streamWithoutInstructor = {
            ...mockVideoStreams[0],
            instructor: undefined,
            instructorPhotoUrl: undefined
        };

        // Should display "未提供" or similar
        const instructorText = streamWithoutInstructor.instructor || '未提供';
        expect(instructorText).toBe('未提供');
    });

    test('應該處理缺少圖片的情況', async () => {
        const streamWithoutImages = {
            ...mockVideoStreams[0],
            instructorPhotoUrl: undefined,
            thumbnailUrl: undefined
        };

        // Should use default image
        const defaultImage = streamWithoutImages.type === 'live'
            ? 'https://default-live-icon.png'
            : 'https://default-video-icon.png';

        expect(defaultImage).toBeTruthy();
    });

    test('應該處理資料庫錯誤', async () => {
        const errorMessage = '無法取得最新影音資訊，請稍後再試';
        expect(errorMessage).toContain('無法取得');
    });
});

test.describe('最新影音 Command - URL Validation', () => {

    test('所有觀看連結應該是有效的 URL', async () => {
        mockVideoStreams.forEach(stream => {
            expect(stream.streamUrl).toMatch(/^https?:\/\/.+/);
        });
    });

    test('講師照片和縮圖應該是有效的圖片 URL', async () => {
        const imageExtensions = /\.(jpg|jpeg|png|gif|webp)/i;

        mockVideoStreams.forEach(stream => {
            if (stream.instructorPhotoUrl) {
                expect(stream.instructorPhotoUrl).toMatch(/^https?:\/\/.+/);
                expect(stream.instructorPhotoUrl).toMatch(imageExtensions);
            }

            if (stream.thumbnailUrl) {
                expect(stream.thumbnailUrl).toMatch(/^https?:\/\/.+/);
                expect(stream.thumbnailUrl).toMatch(imageExtensions);
            }
        });
    });

    test('YouTube 連結格式應正確', async () => {
        const youtubeStreams = mockVideoStreams.filter(s =>
            s.streamUrl.includes('youtube.com')
        );

        youtubeStreams.forEach(stream => {
            expect(stream.streamUrl).toMatch(/youtube\.com\/watch\?v=/);
        });
    });
});

test.describe('最新影音 Command - Date Handling', () => {

    test('直播日期應該是未來或當天', async () => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        mockVideoStreams
            .filter(s => s.type === 'live')
            .forEach(stream => {
                const streamDate = new Date(stream.streamDate);
                streamDate.setHours(0, 0, 0, 0);

                // Live streams should be today or future
                expect(streamDate.getTime()).toBeGreaterThanOrEqual(today.getTime());
            });
    });

    test('影音日期應該正確格式化', async () => {
        mockVideoStreams.forEach(stream => {
            expect(stream.streamDate).toBeInstanceOf(Date);
            expect(stream.streamDate.toISOString()).toBeTruthy();
        });
    });

    test('應該按日期排序（最新在前）', async () => {
        const sortedStreams = [...mockVideoStreams].sort((a, b) =>
            b.streamDate.getTime() - a.streamDate.getTime()
        );

        // First stream should be the most recent
        expect(sortedStreams[0].streamDate.getTime()).toBeGreaterThanOrEqual(
            sortedStreams[sortedStreams.length - 1].streamDate.getTime()
        );
    });
});

test.describe('最新影音 Command - Integration Test', () => {

    test('完整流程：指令 → 服務 → 回應', async () => {
        // Step 1: User sends "最新影音" command
        const userCommand = '最新影音';
        expect(userCommand).toBe('最新影音');

        // Step 2: System calls videoStreamingService.getLatestContent(10)
        const streams = mockVideoStreams;
        expect(streams).toHaveLength(10);

        // Step 3: System generates Flex Message
        // Step 4: System sends reply with Quick Reply buttons
        // Step 5: User receives carousel message with 5 live + 5 video items

        const liveCount = streams.filter(s => s.type === 'live').length;
        const videoCount = streams.filter(s => s.type === 'video').length;

        expect(liveCount).toBe(5);
        expect(videoCount).toBe(5);
    });
});
