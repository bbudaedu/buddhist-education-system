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
                }
            });

            const series = response.data || [];
            return series.map((s: any) => ({
                id: `series_${s.title_no}`,
                title: s.title_name || s.name || '無標題',
                instructor: s.lecr_name || '佛陀教育基金會',
                startTime: s.latest_filedate,
                link: `https://www.budaedu.org/#/series/${s.title_no}`,
                seriesId: s.title_no,
                isLive: false,
                type: 'video',
                thumbnailUrl: 'https://www.budaedu.org/img/logo.png',
                intro: s.title_abstract || `${s.lecr_name || '法師'}講授${s.title_name || '佛法課程'}` // 添加简单介绍
            } as VideoContent));
        } catch (error) {
            console.error('Fetch video series failed:', error);
            return [];
        }
    }

    /**
     * 獲取指定系列的最新一集播放連結
     * 優先級：視頻 MP4 > 音頻 MP3 > FTP 視頻 > FTP 音頻
     * @param seriesId 課程編號 (如 T096M)
     * @returns 最新一集的播放連結，失敗返回 undefined
     */
    async getLatestEpisode(seriesId: string): Promise<string | undefined> {
        const EPISODES_API = `https://publish.budaedu.org/audiovisual/public/api/series/${seriesId}/episodes`;

        try {
            const response = await budaeduConnector.get<any>(EPISODES_API, {
                params: {
                    order: 'AV_fileorder,desc',
                    per_page: 1
                },
                timeout: 20000 // 增加超時時間到 20 秒
            });

            const episodes = response.data || [];

            if (episodes.length > 0) {
                const latestEpisode = episodes[0];
                let playUrl: string | undefined;
                let mediaType = '';

                // 使用實際的 API 欄位：VL_streaming_url (視頻) 和 AL_streaming_url (音頻)
                if (latestEpisode.VL_streaming_url) {
                    playUrl = latestEpisode.VL_streaming_url;
                    mediaType = '視頻MP4';
                } else if (latestEpisode.AL_streaming_url) {
                    playUrl = latestEpisode.AL_streaming_url;
                    mediaType = '音頻MP3';
                } else if (latestEpisode.VL_ftp_url) {
                    playUrl = latestEpisode.VL_ftp_url;
                    mediaType = 'FTP視頻';
                } else if (latestEpisode.AL_ftp_url) {
                    playUrl = latestEpisode.AL_ftp_url;
                    mediaType = 'FTP音頻';
                }

                if (playUrl) {
                    console.log(`[VideoSeries] ✓ ${seriesId} - 找到${mediaType}: 第${latestEpisode.AV_fileorder || '?'}集`);
                    return playUrl;
                }

                // 降級：使用官網播放頁面連結
                if (latestEpisode.AV_fileindex) {
                    const constructedUrl = `https://www.budaedu.org/#/series/${seriesId}/episode/${latestEpisode.AV_fileindex}`;
                    console.log(`[VideoSeries] ✓ ${seriesId} - 使用官網頁面`);
                    return constructedUrl;
                }
            }

            console.log(`[VideoSeries] ✗ ${seriesId} - 無可用集數`);
            return undefined;
        } catch (error) {
            console.error(`[VideoSeries] ✗ ${seriesId} - API失敗:`, error);
            return undefined;
        }
    }
}

export const videoSeriesService = new VideoSeriesService();
