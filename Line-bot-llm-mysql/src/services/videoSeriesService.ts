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
                isLive: false,
                type: 'video',
                thumbnailUrl: 'https://www.budaedu.org/img/logo.png'
            } as VideoContent));
        } catch (error) {
            console.error('Fetch video series failed:', error);
            return [];
        }
    }
}

export const videoSeriesService = new VideoSeriesService();
