/**
 * 影音內容介面
 */
export interface VideoContent {
    id: string;
    title: string;
    instructor?: string;
    startTime?: string;
    link: string;
    thumbnailUrl?: string; // 預留欄位，目前 API 可能未提供
    isLive: boolean;
    type: 'live' | 'video';
    seriesId?: string;           // 課程編號 (如 T096M)，用於獲取最新集數
    latestEpisodeUrl?: string;   // 最新一集的播放連結
}
