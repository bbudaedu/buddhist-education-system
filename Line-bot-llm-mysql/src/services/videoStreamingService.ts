import { VideoContent } from '../types/video';
import { videoSeriesService } from './videoSeriesService';
import { budaeduConnector } from './budaeduConnector';

/**
 * Video Streaming Service
 * 負責從佛陀教育基金會活動系統 API 抓取直播與影音資訊
 */
export class VideoStreamingService {
    private readonly LIVE_API_URL = 'https://publish.budaedu.org/laravel/public/api/courses';
    private readonly CACHE_TTL = 60 * 1000; // 快取 1 分鐘

    // 快取
    private cache: { data: VideoContent[]; timestamp: number } | null = null;

    /**
     * 取得最新影音內容（直播 + 系列課程）
     * @param limit 限制回傳數量
     * @returns Promise<VideoContent[]> 影音內容列表
     */
    async getLatestContent(limit: number = 10): Promise<VideoContent[]> {
        // 檢查快取
        const now = Date.now();
        if (this.cache && (now - this.cache.timestamp) < this.CACHE_TTL) {
            console.log('使用快取的影音資料');
            return this.cache.data.slice(0, limit);
        }

        try {
            console.log('從 API 抓取影音資料...');

            // 平行請求：直播活動 + 近期課程
            const [liveResponse, seriesResponse] = await Promise.all([
                this.fetchLiveEvents(),
                videoSeriesService.getLatestSeries(limit)
            ]);

            // 合併並排序（優先顯示直播，再來是近期課程）
            const allContent = [...liveResponse, ...seriesResponse];

            // 去除重複 (以 ID 判斷)
            const uniqueContent = Array.from(
                new Map(allContent.map(item => [item.id, item])).values()
            );

            // 更新快取
            this.cache = {
                data: uniqueContent,
                timestamp: now
            };

            return uniqueContent.slice(0, limit);
        } catch (error) {
            console.error('Error fetching video content:', error);
            if (this.cache) return this.cache.data.slice(0, limit);
            return [];
        }
    }

    /**
     * 抓取直播活動 (使用 Laravel API)
     */
    private async fetchLiveEvents(): Promise<VideoContent[]> {
        try {
            // 取得今日星期幾 (1-7, 1=週一, 7=週日)
            const now = new Date();
            const day = now.getDay();
            const weekday = day === 0 ? 7 : day;

            const weekdayNames = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
            const weekdayName = weekdayNames[day];

            console.log(`Today is ${weekdayName} (weekday ${weekday}), current time: ${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`);

            const response = await budaeduConnector.get<any>(this.LIVE_API_URL, {
                params: {
                    'filter[week]': weekday,
                    'filter[have_live_stream]': 'true',
                    'filter[continued]': 'true',
                    'include': 'places,lecturer',
                    'order': 'spk_start_time,asc|spk_end_time,asc'
                },
                timeout: 5000
            });

            const courses = response.data || [];

            // 過濾：只保留尚未結束的直播
            const currentTimeInMinutes = now.getHours() * 60 + now.getMinutes();
            const ongoingCourses = courses.filter((c: any) => {
                if (!c.spk_end_time) return false;
                const [endHour, endMinute] = c.spk_end_time.split(':').map(Number);
                const endTimeInMinutes = endHour * 60 + endMinute;
                return endTimeInMinutes > currentTimeInMinutes;
            });

            console.log(`Found ${courses.length} total courses for ${weekdayName}, ${ongoingCourses.length} still ongoing`);

            return ongoingCourses.map((c: any) => {
                // 尋找直播連結
                let liveUrl = '';
                if (c.schedules && c.schedules.length > 0) {
                    for (const schedule of c.schedules) {
                        if (schedule.places) {
                            const place = schedule.places.find((p: any) => p.live_stream_url);
                            if (place) liveUrl = place.live_stream_url;
                        }
                    }
                }

                // 格式化時間顯示：星期四 14:30 ~ 16:30
                const timeDisplay = `${weekdayName} ${c.spk_start_time} ~ ${c.spk_end_time}`;

                // 講師名稱（包含稱謂）
                const instructorName = c.lecturer?.lecr_full_name ||
                    (c.lecturer?.lecr_name && c.lecturer?.lecr_title
                        ? `${c.lecturer.lecr_name}${c.lecturer.lecr_title}`
                        : '') ||
                    c.leader ||
                    '佛陀教育基金會';

                return {
                    id: `live_${c.id}`,
                    title: c.title_name || c.name || '直播課程',
                    instructor: instructorName,
                    startTime: timeDisplay,
                    link: liveUrl || 'https://www.budaedu.org/#/series/live-streaming',
                    isLive: true,
                    type: 'live',
                    thumbnailUrl: 'https://www.budaedu.org/img/logo.png'
                } as VideoContent;
            });
        } catch (error) {
            console.error('Fetch live events failed:', error);
            return [];
        }
    }
}

export const videoStreamingService = new VideoStreamingService();
