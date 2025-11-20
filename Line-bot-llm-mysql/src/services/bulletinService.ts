import axios from 'axios';
import https from 'https';

/**
 * 最新消息資料結構
 */
export interface Bulletin {
  id: string;
  title: string;
  content: string;
  publishStartDate: string;
  publishEndDate: string;
  url: string;
}

/**
 * Bulletin Service
 * 負責從佛陀教育基金會網站抓取最新消息
 */
export class BulletinService {
  private readonly API_BASE_URL = 'https://publish.budaedu.org/laravel/public/api';
  private readonly WEBSITE_BASE_URL = 'https://www.budaedu.org/#';
  private readonly CACHE_TTL = 1 * 60 * 1000; // 快取 1 分鐘（更即時）
  
  // 快取
  private bulletinsCache: { data: Bulletin[]; timestamp: number } | null = null;
  private cancellationsCache: { data: any[]; timestamp: number } | null = null;
  
  // 建立 axios 實例，忽略 SSL 憑證驗證（僅用於開發/測試）
  private readonly axiosInstance = axios.create({
    httpsAgent: new https.Agent({
      rejectUnauthorized: false
    })
  });

  /**
   * 取得最新消息列表
   * @param limit 限制回傳數量，預設 10
   * @param forceRefresh 強制重新抓取，預設 false
   * @returns Promise<Bulletin[]> 最新消息列表
   */
  async getLatestBulletins(limit: number = 10, forceRefresh: boolean = false): Promise<Bulletin[]> {
    // 檢查快取是否有效
    const now = Date.now();
    if (!forceRefresh && this.bulletinsCache && (now - this.bulletinsCache.timestamp) < this.CACHE_TTL) {
      console.log('使用快取的最新消息資料');
      return this.bulletinsCache.data.slice(0, limit);
    }

    try {
      console.log('從 API 抓取最新消息...');
      const response = await this.axiosInstance.get(
        `${this.API_BASE_URL}/bulletins`,
        {
          params: {
            'filter[publishing]': '',
            'include': 'attachments',
            'order': 'publish_start_date,desc|updated_at,desc'
          },
          timeout: 10000
        }
      );

      const bulletins = response.data.data || [];
      
      const processedBulletins = bulletins.map((item: any) => ({
        id: item.id,
        title: item.title,
        content: this.stripHtmlTags(item.content),
        publishStartDate: item.publish_start_date,
        publishEndDate: item.publish_end_date,
        url: `${this.WEBSITE_BASE_URL}/bulletins/${item.id}`
      }));

      // 更新快取
      this.bulletinsCache = {
        data: processedBulletins,
        timestamp: now
      };

      console.log(`成功抓取 ${processedBulletins.length} 則最新消息`);
      return processedBulletins.slice(0, limit);
    } catch (error) {
      console.error('Error fetching bulletins:', error);
      
      // 如果有舊快取，回傳舊快取
      if (this.bulletinsCache) {
        console.log('API 失敗，使用舊快取資料');
        return this.bulletinsCache.data.slice(0, limit);
      }
      
      throw new Error('無法取得最新消息');
    }
  }

  /**
   * 取得單一最新消息詳情
   * @param bulletinId 最新消息 ID
   * @returns Promise<Bulletin | null> 最新消息詳情
   */
  async getBulletinById(bulletinId: string): Promise<Bulletin | null> {
    try {
      const response = await this.axiosInstance.get(
        `${this.API_BASE_URL}/bulletins/${bulletinId}`,
        {
          params: {
            'include': 'attachments'
          },
          timeout: 10000
        }
      );

      const item = response.data.data;
      
      if (!item) {
        return null;
      }

      return {
        id: item.id,
        title: item.title,
        content: this.stripHtmlTags(item.content),
        publishStartDate: item.publish_start_date,
        publishEndDate: item.publish_end_date,
        url: `${this.WEBSITE_BASE_URL}/bulletins/${item.id}`
      };
    } catch (error) {
      console.error(`Error fetching bulletin ${bulletinId}:`, error);
      return null;
    }
  }

  /**
   * 取得停課公告資料
   * @param limit 限制回傳數量，預設 3
   * @param forceRefresh 強制重新抓取，預設 false
   * @returns Promise<any[]> 停課公告列表
   */
  async getCourseCancellations(limit: number = 3, forceRefresh: boolean = false): Promise<any[]> {
    // 檢查快取是否有效
    const now = Date.now();
    if (!forceRefresh && this.cancellationsCache && (now - this.cancellationsCache.timestamp) < this.CACHE_TTL) {
      console.log('使用快取的停課公告資料');
      return this.cancellationsCache.data.slice(0, limit);
    }

    try {
      console.log('從 API 抓取停課公告...');
      const today = new Date().toISOString().split('T')[0];
      const response = await this.axiosInstance.get(
        `${this.API_BASE_URL}/course-cancel-records`,
        {
          params: {
            'include': 'course.lecturer',
            'filter[cancel_date][gte]': today,
            'order': 'cancel_date,asc'
          },
          timeout: 10000
        }
      );

      const records = response.data.data || [];
      
      const processedRecords = records.map((item: any) => ({
        id: item.id,
        cancelDate: item.cancel_date,
        courseTitle: item.course?.title_name || '課程',
        lecturerName: item.course?.lecturer?.lecr_name || '',
        weekDay: item.course?.week || '',
        time: item.course?.spk_start_time && item.course?.spk_end_time 
          ? `${item.course.spk_start_time} ~ ${item.course.spk_end_time}`
          : '',
        cause: item.cause || ''
      }));

      // 更新快取
      this.cancellationsCache = {
        data: processedRecords,
        timestamp: now
      };

      console.log(`成功抓取 ${processedRecords.length} 則停課公告`);
      return processedRecords.slice(0, limit);
    } catch (error) {
      console.error('Error fetching course cancellations:', error);
      
      // 如果有舊快取，回傳舊快取
      if (this.cancellationsCache) {
        console.log('API 失敗，使用舊快取資料');
        return this.cancellationsCache.data.slice(0, limit);
      }
      
      return [];
    }
  }

  /**
   * 清除快取（手動刷新用）
   */
  clearCache(): void {
    this.bulletinsCache = null;
    this.cancellationsCache = null;
    console.log('快取已清除');
  }

  /**
   * 移除 HTML 標籤，保留純文字
   * @param html HTML 字串
   * @returns 純文字字串
   */
  private stripHtmlTags(html: string): string {
    if (!html) return '';
    
    return html
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<\/p>/gi, '\n')
      .replace(/<[^>]+>/g, '')
      .replace(/&nbsp;/g, ' ')
      .replace(/\n\s*\n/g, '\n')
      .trim();
  }
}

// 建立單例實例
export const bulletinService = new BulletinService();
