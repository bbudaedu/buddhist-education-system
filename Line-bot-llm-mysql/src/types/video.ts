/**
 * 影音內容介面
 */
export interface VideoContent {
    id: string;
    title: string;
    instructor: string;
    startTime: string;
    endTime?: string;
    link: string;
    thumbnailUrl?: string; // 預留欄位，目前 API 可能未提供
    isLive: boolean;
    type: 'live' | 'video';
}
