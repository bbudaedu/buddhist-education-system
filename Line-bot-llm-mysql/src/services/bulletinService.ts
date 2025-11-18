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
  
  // 建立 axios 實例，忽略 SSL 憑證驗證（僅用於開發/測試）
  private readonly axiosInstance = axios.create({
    httpsAgent: new https.Agent({
      rejectUnauthorized: false
    })
  });

  /**
   * 取得最新消息列表
   * @param limit 限制回傳數量，預設 10
   * @returns Promise<Bulletin[]> 最新消息列表
   */
  async getLatestBulletins(limit: number = 10): Promise<Bulletin[]> {
    try {
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
      
      return bulletins.slice(0, limit).map((item: any) => ({
        id: item.id,
        title: item.title,
        content: this.stripHtmlTags(item.content),
        publishStartDate: item.publish_start_date,
        publishEndDate: item.publish_end_date,
        url: `${this.WEBSITE_BASE_URL}/bulletins/${item.id}`
      }));
    } catch (error) {
      console.error('Error fetching bulletins:', error);
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
   * @returns Promise<any[]> 停課公告列表
   */
  async getCourseCancellations(limit: number = 3): Promise<any[]> {
    try {
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
      
      return records.slice(0, limit).map((item: any) => ({
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
    } catch (error) {
      console.error('Error fetching course cancellations:', error);
      return [];
    }
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
