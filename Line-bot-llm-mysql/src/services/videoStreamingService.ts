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
     * 从课程详情 API 获取介绍
     * @param courseId 课程 ID
     * @returns Promise<string | undefined> 清理后的介绍文字
     */
    private async getCourseIntro(courseId: string): Promise<string | undefined> {
        try {
            const response = await budaeduConnector.get<any>(this.LIVE_API_URL + `/${courseId}`, {
                params: {
                    'fields[courses]': 'intro'
                }
            });

            const course = response.data;
            if (!course || !course.intro) return undefined;

            // 清理 HTML 标签并限制长度
            const rawIntro = course.intro;
            const cleanIntro = rawIntro
                .replace(/<[^>]*>/g, '')  // 移除所有 HTML 标签
                .replace(/&nbsp;/g, ' ')  // 替换 HTML 实体
                .replace(/&lt;/g, '<')
                .replace(/&gt;/g, '>')
                .replace(/&amp;/g, '&')
                .replace(/mso-[^;]+;/g, '')  // 移除 MS Office 样式
                .replace(/\\u[0-9a-fA-F]{4}/g, (match: string) => String.fromCharCode(parseInt(match.substr(2), 16)))  // 解码 Unicode
                .replace(/\s+/g, ' ')  // 合并多余空白
                .trim();

            // 限制长度为 200 字符
            return cleanIntro.length > 200
                ? cleanIntro.substring(0, 200) + '...'
                : cleanIntro || undefined;

        } catch (error) {
            console.error(`Failed to fetch intro for course ${courseId}:`, error);
            return undefined;
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
                }
            });

            const courses = response.data || [];

            // 獲取今天的日期（僅日期部分）
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            // 過濾：1) 尚未結束的直播 2) 已經開始的課程（開課日 <= 今天）
            const currentTimeInMinutes = now.getHours() * 60 + now.getMinutes();
            const ongoingCourses = courses.filter((c: any) => {
                // Check 1: 必須有結束時間且尚未結束
                if (!c.spk_end_time) return false;
                const [endHour, endMinute] = c.spk_end_time.split(':').map(Number);
                const endTimeInMinutes = endHour * 60 + endMinute;
                if (endTimeInMinutes <= currentTimeInMinutes) return false;

                // Check 2: 開課日期必須 <= 今天（排除尚未開始的課程）
                if (c.spkdate) {
                    const courseStartDate = new Date(c.spkdate);
                    courseStartDate.setHours(0, 0, 0, 0);
                    if (courseStartDate > today) {
                        console.log(`[FILTER] Excluding "${c.title_name}" - Not started yet (${c.spkdate})`);
                        return false;
                    }
                }

                return true;
            });

            console.log(`Found ${courses.length} total courses for ${weekdayName}, ${ongoingCourses.length} still ongoing`);

            // 並行獲取所有課程的 intro
            const coursesWithIntro = await Promise.all(
                ongoingCourses.map(async (c: any) => {
                    // 尋找直播連結
                    // Priority 1: Check  course.live_stream_url (top-level field)
                    let liveUrl = c.live_stream_url || '';

                    // Priority 2: Check course.places[].live_url (direct array)
                    if (!liveUrl && c.places && c.places.length > 0) {
                        const place = c.places.find((p: any) => p.live_url);
                        if (place) liveUrl = place.live_url || '';
                    }

                    // Priority 3: Fallback - check schedules.places
                    if (!liveUrl && c.schedules && c.schedules.length > 0) {
                        for (const schedule of c.schedules) {
                            if (schedule.places) {
                                const place = schedule.places.find((p: any) => p.live_stream_url || p.live_url);
                                if (place) {
                                    liveUrl = place.live_url || place.live_stream_url || '';
                                    break;
                                }
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

                    // 使用新的 API 获取课程介绍
                    const intro = await this.getCourseIntro(c.id);

                    return {
                        id: `live_${c.id}`,
                        title: c.title_name || c.name || '直播課程',
                        instructor: instructorName,
                        startTime: timeDisplay,
                        link: liveUrl || 'https://www.budaedu.org/#/series/live-streaming',
                        isLive: true,
                        type: 'live',
                        thumbnailUrl: 'https://www.budaedu.org/img/logo.png',
                        intro  // 使用新 API 获取的 intro
                    } as VideoContent;
                })
            );

            return coursesWithIntro;
        } catch (error) {
            console.error('Fetch live events failed:', error);
            return [];
        }
    }
}

export const videoStreamingService = new VideoStreamingService();
