import axios from 'axios';
import https from 'https';

/**
 * 活動資料結構
 */
export interface Activity {
    id: string;
    name: string;
    startDate: string;
    endDate: string;
    hasLiveStream: boolean;
    leader: string;
    contact: string;
    organizer?: {
        id: number;
        name: string;
    } | undefined;
    schedules?: ActivitySchedule[] | undefined;
}

/**
 * 活動時程資料結構
 */
export interface ActivitySchedule {
    id: number;
    name: string;
    scheduleDate: string;
    startTime: string;
    endTime: string;
    leader: string;
    overview: string;
    hasLiveStream: boolean;
    places?: {
        id: number;
        name: string;
        liveStreamingUrl: string;
        pivot: {
            offerLiveStreaming: string;
        };
    }[];
}

/**
 * Activity Service
 * 負責從佛陀教育基金會活動系統 API 抓取活動資訊
 */
export class ActivityService {
    private readonly API_BASE_URL = 'https://publish.budaedu.org/activity/public/api';
    // private readonly WEBSITE_BASE_URL = 'https://www.budaedu.org/#'; // Reserved for future use
    private readonly CACHE_TTL = 5 * 60 * 1000; // 快取 5 分鐘（活動資料更新較慢）

    // 快取
    private liveEventsCache: { data: Activity[]; timestamp: number } | null = null;
    private ongoingEventsCache: { data: Activity[]; timestamp: number } | null = null;

    // 建立 axios 實例，忽略 SSL 憑證驗證（僅用於開發/測試）
    private readonly axiosInstance = axios.create({
        httpsAgent: new https.Agent({
            rejectUnauthorized: false
        })
    });

    /**
     * 取得直播活動列表
     * @param limit 限制回傳數量，預設 5
     * @param forceRefresh 強制重新抓取，預設 false
     * @returns Promise<Activity[]> 直播活動列表
     */
    async getLiveEvents(limit: number = 5, forceRefresh: boolean = false): Promise<Activity[]> {
        // 檢查快取是否有效
        const now = Date.now();
        if (!forceRefresh && this.liveEventsCache && (now - this.liveEventsCache.timestamp) < this.CACHE_TTL) {
            console.log('使用快取的直播活動資料');
            return this.liveEventsCache.data.slice(0, limit);
        }

        try {
            console.log('從 API 抓取直播活動...');
            const response = await this.axiosInstance.get(
                `${this.API_BASE_URL}/events`,
                {
                    params: {
                        'filter[has_live_stream]': 'true',
                        'include': 'organizer,schedules.places',
                        'order': 'start_date,desc',
                        'per_page': limit
                    },
                    timeout: 10000
                }
            );

            const events = response.data.data || [];

            const processedEvents = events.map((item: any) => this.mapEventData(item));

            // 更新快取
            this.liveEventsCache = {
                data: processedEvents,
                timestamp: now
            };

            console.log(`成功抓取 ${processedEvents.length} 個直播活動`);
            return processedEvents.slice(0, limit);
        } catch (error) {
            console.error('Error fetching live events:', error);

            // 如果有舊快取，回傳舊快取
            if (this.liveEventsCache) {
                console.log('API 失敗，使用舊快取資料');
                return this.liveEventsCache.data.slice(0, limit);
            }

            throw new Error('無法取得直播活動');
        }
    }

    /**
     * 取得進行中的系列課程
     * @param limit 限制回傳數量，預設 5
     * @param forceRefresh 強制重新抓取，預設 false
     * @returns Promise<Activity[]> 系列課程列表
     */
    async getOngoingEvents(limit: number = 5, forceRefresh: boolean = false): Promise<Activity[]> {
        // 檢查快取是否有效
        const now = Date.now();
        if (!forceRefresh && this.ongoingEventsCache && (now - this.ongoingEventsCache.timestamp) < this.CACHE_TTL) {
            console.log('使用快取的系列課程資料');
            return this.ongoingEventsCache.data.slice(0, limit);
        }

        try {
            console.log('從 API 抓取系列課程...');
            const today = new Date().toISOString().split('T')[0];
            const response = await this.axiosInstance.get(
                `${this.API_BASE_URL}/events`,
                {
                    params: {
                        'include': 'organizer,schedules',
                        'filter[end_date][gte]': today,
                        'order': 'start_date,desc',
                        'per_page': limit
                    },
                    timeout: 10000
                }
            );

            const events = response.data.data || [];

            const processedEvents = events.map((item: any) => this.mapEventData(item));

            // 更新快取
            this.ongoingEventsCache = {
                data: processedEvents,
                timestamp: now
            };

            console.log(`成功抓取 ${processedEvents.length} 個系列課程`);
            return processedEvents.slice(0, limit);
        } catch (error) {
            console.error('Error fetching ongoing events:', error);

            // 如果有舊快取，回傳舊快取
            if (this.ongoingEventsCache) {
                console.log('API 失敗，使用舊快取資料');
                return this.ongoingEventsCache.data.slice(0, limit);
            }

            throw new Error('無法取得系列課程');
        }
    }

    /**
     * 取得單一活動詳情
     * @param eventId 活動 ID
     * @returns Promise<Activity | null> 活動詳情
     */
    async getEventById(eventId: string): Promise<Activity | null> {
        try {
            const response = await this.axiosInstance.get(
                `${this.API_BASE_URL}/events/${eventId}`,
                {
                    params: {
                        'include': 'organizer,detail,schedules.places'
                    },
                    timeout: 10000
                }
            );

            const item = response.data.data;

            if (!item) {
                return null;
            }

            return this.mapEventData(item);
        } catch (error) {
            console.error(`Error fetching event ${eventId}:`, error);
            return null;
        }
    }

    /**
     * 清除快取（手動刷新用）
     */
    clearCache(): void {
        this.liveEventsCache = null;
        this.ongoingEventsCache = null;
        console.log('快取已清除');
    }

    /**
     * 轉換 API 回應資料為統一格式
     * @param item API 回應的活動物件
     * @returns Activity 統一格式的活動物件
     */
    private mapEventData(item: any): Activity {
        return {
            id: item.id,
            name: item.name,
            startDate: item.start_date,
            endDate: item.end_date,
            hasLiveStream: item.has_live_stream || false,
            leader: item.leader || '',
            contact: item.contact || '',
            organizer: item.organizer ? {
                id: item.organizer.id,
                name: item.organizer.name
            } : undefined,
            schedules: item.schedules ? item.schedules.map((schedule: any) => ({
                id: schedule.id,
                name: schedule.name,
                scheduleDate: schedule.schedule_date,
                startTime: schedule.start_time,
                endTime: schedule.end_time,
                leader: schedule.leader || '',
                overview: schedule.overview || '',
                hasLiveStream: schedule.has_live_stream || false,
                places: schedule.places || []
            })) : undefined
        };
    }
}

// 建立單例實例
export const activityService = new ActivityService();
