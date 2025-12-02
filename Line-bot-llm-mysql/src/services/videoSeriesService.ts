import { VideoContent } from '../types/video';
import { budaeduConnector } from './budaeduConnector';

/**
 * Video Series Service
 * 負責從佛陀教育基金會影音系統 API 抓取系列課程資訊
 */
export class VideoSeriesService {
    private readonly SERIES_API_URL = 'https://publish.budaedu.org/audiovisual/public/api/series/by-keyword-searched';

    /**
     * 抓取近期系列課程
     * @param limit 限制回傳數量
     */
    async getLatestSeries(limit: number = 10): Promise<VideoContent[]> {
        try {
            const response = await budaeduConnector.get<any>(this.SERIES_API_URL, {
                params: {
                    'filter[ended]': 'N',
                    'filter[IsDirtyEntry]': 'N',
                    'order': 'latest_filedate,desc',
                    'per_page': limit
                },
                timeout: 5000
            });

            const series = response.data || [];
            return series.map((s: any) => ({
                id: `series_${s.title_no}`,
                title: s.title_name || s.name || '無標題',
                instructor: s.lecr_name || '佛陀教育基金會',
                startTime: s.latest_filedate,
                link: `https://www.budaedu.org/#/series/${s.title_no}`,
                seriesId: s.title_no,  // 保存課程編號以便獲取最新集數
                isLive: false,
                type: 'video',
                thumbnailUrl: 'https://www.budaedu.org/img/logo.png'
            } as VideoContent));
        } catch (error) {
            console.error('Fetch video series failed:', error);
            return [];
        }
    }

    /**
     * 獲取指定系列的最新一集播放連結
     * @param seriesId 課程編號 (如 T096M)
     * @returns 最新一集的播放連結，失敗返回 undefined
     */
    async getLatestEpisode(seriesId: string): Promise<string | undefined> {
        const EPISODES_API = `https://publish.budaedu.org/audiovisual/public/api/series/${seriesId}/episodes`;

        try {
            const response = await budaeduConnector.get<any>(EPISODES_API, {
                params: {
                    order: 'AV_fileorder,desc',  // 降序取得最新一集
                    per_page: 1
                },
                timeout: 5000
            });

            const episodes = response.data || [];
            if (episodes.length > 0) {
                const latestEpisode = episodes[0];
                // 嘗試多個可能的欄位名稱
                const playUrl = latestEpisode.video_url ||
                    latestEpisode.play_url ||
                    latestEpisode.url ||
                    latestEpisode.file_url;

                if (playUrl) {
                    console.log(`[VideoSeries] Latest episode for ${seriesId}: ${playUrl}`);
                    return playUrl;
                }

                // 如果找不到播放連結，嘗試構建官網播放頁面連結
                if (latestEpisode.id || latestEpisode.AV_id) {
                    const episodeId = latestEpisode.id || latestEpisode.AV_id;
                    return `https://www.budaedu.org/#/series/${seriesId}/episode/${episodeId}`;
                }
            }

            console.log(`[VideoSeries] No latest episode found for ${seriesId}`);
            return undefined;
        } catch (error) {
            console.error(`[VideoSeries] Failed to fetch latest episode for ${seriesId}:`, error);
            return undefined;
        }
    }
}

export const videoSeriesService = new VideoSeriesService();
