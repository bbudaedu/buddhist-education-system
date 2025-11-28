/**
 * Mock Data for E2E Testing
 * LINE Dharma Media Feature
 */

export interface MockDharmaBook {
    id: string;
    title: string;
    author: string;
    coverUrl?: string;
    publishDate: string;
    detailUrl: string;
    pdfUrl: string;
}

export interface MockVideoStream {
    id: string;
    title: string;
    type: 'live' | 'video';
    instructor?: string;
    instructorPhotoUrl?: string;
    topic?: string;
    streamDate: Date;
    streamUrl: string;
    thumbnailUrl?: string;
}

/**
 * Mock Dharma Books Data
 */
export const mockDharmaBooks: MockDharmaBook[] = [
    {
        id: 'book-001',
        title: '金剛般若波羅蜜經講記',
        author: '聖嚴法師',
        coverUrl: 'https://example.com/covers/book1.jpg',
        publishDate: '2025-11-20',
        detailUrl: 'https://publish.budaedu.org/book/001',
        pdfUrl: 'https://publish.budaedu.org/pdf/book001.pdf'
    },
    {
        id: 'book-002',
        title: '心經講義',
        author: '淨空法師',
        coverUrl: 'https://example.com/covers/book2.jpg',
        publishDate: '2025-11-19',
        detailUrl: 'https://publish.budaedu.org/book/002',
        pdfUrl: 'https://publish.budaedu.org/pdf/book002.pdf'
    },
    {
        id: 'book-003',
        title: '楞嚴經淺釋',
        author: '宣化上人',
        publishDate: '2025-11-18',
        detailUrl: 'https://publish.budaedu.org/book/003',
        pdfUrl: 'https://publish.budaedu.org/pdf/book003.pdf'
    },
    {
        id: 'book-004',
        title: '法華經玄義',
        author: '智者大師',
        coverUrl: 'https://example.com/covers/book4.jpg',
        publishDate: '2025-11-17',
        detailUrl: 'https://publish.budaedu.org/book/004',
        pdfUrl: 'https://publish.budaedu.org/pdf/book004.pdf'
    },
    {
        id: 'book-005',
        title: '阿彌陀經要解',
        author: '蕅益大師',
        coverUrl: 'https://example.com/covers/book5.jpg',
        publishDate: '2025-11-16',
        detailUrl: 'https://publish.budaedu.org/book/005',
        pdfUrl: 'https://publish.budaedu.org/pdf/book005.pdf'
    }
];

/**
 * Mock Video Streams Data (5 Live + 5 Videos)
 */
export const mockVideoStreams: MockVideoStream[] = [
    // Live Streams
    {
        id: 'live-001',
        title: '《楞嚴經》導讀',
        type: 'live',
        instructor: '慧律法師',
        instructorPhotoUrl: 'https://example.com/instructors/huilv.jpg',
        topic: '楞嚴經',
        streamDate: new Date('2025-11-24T19:00:00'),
        streamUrl: 'https://youtube.com/watch?v=live001',
        thumbnailUrl: 'https://example.com/thumbnails/live001.jpg'
    },
    {
        id: 'live-002',
        title: '禪修實踐課程',
        type: 'live',
        instructor: '果暉法師',
        instructorPhotoUrl: 'https://example.com/instructors/guohui.jpg',
        topic: '禪修',
        streamDate: new Date('2025-11-25T14:00:00'),
        streamUrl: 'https://youtube.com/watch?v=live002'
    },
    {
        id: 'live-003',
        title: '淨土法門講座',
        type: 'live',
        instructor: '淨空法師',
        topic: '淨土宗',
        streamDate: new Date('2025-11-26T09:00:00'),
        streamUrl: 'https://youtube.com/watch?v=live003',
        thumbnailUrl: 'https://example.com/thumbnails/live003.jpg'
    },
    {
        id: 'live-004',
        title: '《法華經》研討',
        type: 'live',
        instructor: '聖嚴法師',
        instructorPhotoUrl: 'https://example.com/instructors/shengyan.jpg',
        topic: '法華經',
        streamDate: new Date('2025-11-27T19:30:00'),
        streamUrl: 'https://youtube.com/watch?v=live004'
    },
    {
        id: 'live-005',
        title: '佛學入門講座',
        type: 'live',
        instructor: '證嚴法師',
        topic: '佛學基礎',
        streamDate: new Date('2025-11-28T10:00:00'),
        streamUrl: 'https://youtube.com/watch?v=live005',
        thumbnailUrl: 'https://example.com/thumbnails/live005.jpg'
    },
    // Video Recordings
    {
        id: 'video-001',
        title: '金剛經精華解析',
        type: 'video',
        instructor: '宣化上人',
        instructorPhotoUrl: 'https://example.com/instructors/xuanhua.jpg',
        topic: '金剛經',
        streamDate: new Date('2025-11-15T00:00:00'),
        streamUrl: 'https://youtube.com/watch?v=video001',
        thumbnailUrl: 'https://example.com/thumbnails/video001.jpg'
    },
    {
        id: 'video-002',
        title: '心經智慧',
        type: 'video',
        instructor: '星雲大師',
        topic: '心經',
        streamDate: new Date('2025-11-14T00:00:00'),
        streamUrl: 'https://youtube.com/watch?v=video002',
        thumbnailUrl: 'https://example.com/thumbnails/video002.jpg'
    },
    {
        id: 'video-003',
        title: '六祖壇經講座',
        type: 'video',
        instructor: '慈誠羅珠堪布',
        instructorPhotoUrl: 'https://example.com/instructors/cicheng.jpg',
        topic: '壇經',
        streamDate: new Date('2025-11-13T00:00:00'),
        streamUrl: 'https://youtube.com/watch?v=video003'
    },
    {
        id: 'video-004',
        title: '地藏經導讀',
        type: 'video',
        instructor: '夢參老和尚',
        topic: '地藏經',
        streamDate: new Date('2025-11-12T00:00:00'),
        streamUrl: 'https://youtube.com/watch?v=video004',
        thumbnailUrl: 'https://example.com/thumbnails/video004.jpg'
    },
    {
        id: 'video-005',
        title: '華嚴經概論',
        type: 'video',
        instructor: '海雲法師',
        instructorPhotoUrl: 'https://example.com/instructors/haiyun.jpg',
        topic: '華嚴經',
        streamDate: new Date('2025-11-11T00:00:00'),
        streamUrl: 'https://youtube.com/watch?v=video005',
        thumbnailUrl: 'https://example.com/thumbnails/video005.jpg'
    }
];

/**
 * Mock LINE Webhook Event
 */
export function createMockMessageEvent(userId: string, text: string) {
    return {
        type: 'message',
        replyToken: `mock-reply-token-${Date.now()}`,
        source: {
            userId: userId,
            type: 'user'
        },
        timestamp: Date.now(),
        message: {
            type: 'text',
            id: `mock-message-id-${Date.now()}`,
            text: text
        }
    };
}

/**
 * Mock Empty Response (No Data Scenario)
 */
export const mockEmptyBooks: MockDharmaBook[] = [];
export const mockEmptyStreams: MockVideoStream[] = [];
