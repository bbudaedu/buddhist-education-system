import mysql from 'mysql2/promise';
import { RowDataPacket, ResultSetHeader } from 'mysql2';
import { config } from '../config';
import { 
  CarouselContent, 
  CourseCancellation, 
  NewsAnnouncement, 
  MediaContent 
} from '../types/WebsiteMonitoring';

/**
 * Service for managing website monitoring content in the database
 */
export class WebsiteMonitoringService {
  private pool: mysql.Pool;

  constructor() {
    // 建立 MySQL 連線池配置
    this.pool = mysql.createPool({
      host: config.database.host,
      port: config.database.port,
      user: config.database.user,
      password: config.database.password,
      database: config.database.database,
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0,
    });
  }

  /**
   * 批量插入或更新輪播內容
   * @param carouselData 輪播內容陣列
   * @returns Promise<number> 成功處理的記錄數
   */
  async batchUpsertCarouselContent(carouselData: CarouselContent[]): Promise<number> {
    if (carouselData.length === 0) {
      return 0;
    }

    const connection = await this.pool.getConnection();
    
    try {
      await connection.beginTransaction();
      
      let successCount = 0;
      
      for (const item of carouselData) {
        try {
          const sql = `
            INSERT INTO carousel_content (
              carousel_id, banner_title, image_url, activity_link, 
              course_name, location, instructor, description, 
              extraction_timestamp, sync_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
            ON DUPLICATE KEY UPDATE
              banner_title = VALUES(banner_title),
              image_url = VALUES(image_url),
              activity_link = VALUES(activity_link),
              course_name = VALUES(course_name),
              location = VALUES(location),
              instructor = VALUES(instructor),
              description = VALUES(description),
              extraction_timestamp = VALUES(extraction_timestamp),
              sync_timestamp = NOW(),
              updated_at = NOW()
          `;
          
          const values = [
            item.carousel_id,
            item.banner_title || null,
            item.image_url || null,
            item.activity_link || null,
            item.course_name || null,
            item.location || null,
            item.instructor || null,
            item.description || null,
            item.extraction_timestamp || null
          ];
          
          await connection.execute(sql, values);
          successCount++;
          
        } catch (error) {
          console.error(`Failed to upsert carousel item ${item.carousel_id}:`, error);
        }
      }
      
      await connection.commit();
      console.log(`Successfully upserted ${successCount}/${carouselData.length} carousel items`);
      
      return successCount;
      
    } catch (error) {
      await connection.rollback();
      console.error('Error in batch carousel upsert:', error);
      throw error;
    } finally {
      connection.release();
    }
  }

  /**
   * 批量插入或更新課程取消內容
   * @param cancellationData 課程取消內容陣列
   * @returns Promise<number> 成功處理的記錄數
   */
  async batchUpsertCancellationContent(cancellationData: CourseCancellation[]): Promise<number> {
    if (cancellationData.length === 0) {
      return 0;
    }

    const connection = await this.pool.getConnection();
    
    try {
      await connection.beginTransaction();
      
      let successCount = 0;
      
      for (const item of cancellationData) {
        try {
          const sql = `
            INSERT INTO course_cancellations (
              cancellation_id, cancellation_date, course_name, 
              instructor_name, extraction_timestamp, sync_timestamp
            ) VALUES (?, ?, ?, ?, ?, NOW())
            ON DUPLICATE KEY UPDATE
              cancellation_date = VALUES(cancellation_date),
              course_name = VALUES(course_name),
              instructor_name = VALUES(instructor_name),
              extraction_timestamp = VALUES(extraction_timestamp),
              sync_timestamp = NOW(),
              updated_at = NOW()
          `;
          
          const values = [
            item.cancellation_id,
            item.cancellation_date || null,
            item.course_name || null,
            item.instructor_name || null,
            item.extraction_timestamp || null
          ];
          
          await connection.execute(sql, values);
          successCount++;
          
        } catch (error) {
          console.error(`Failed to upsert cancellation item ${item.cancellation_id}:`, error);
        }
      }
      
      await connection.commit();
      console.log(`Successfully upserted ${successCount}/${cancellationData.length} cancellation items`);
      
      return successCount;
      
    } catch (error) {
      await connection.rollback();
      console.error('Error in batch cancellation upsert:', error);
      throw error;
    } finally {
      connection.release();
    }
  }

  /**
   * 批量插入或更新新聞內容
   * @param newsData 新聞內容陣列
   * @returns Promise<number> 成功處理的記錄數
   */
  async batchUpsertNewsContent(newsData: NewsAnnouncement[]): Promise<number> {
    if (newsData.length === 0) {
      return 0;
    }

    const connection = await this.pool.getConnection();
    
    try {
      await connection.beginTransaction();
      
      let successCount = 0;
      
      for (const item of newsData) {
        try {
          const sql = `
            INSERT INTO news_announcements (
              announcement_id, title, publication_date, content, 
              extraction_timestamp, sync_timestamp
            ) VALUES (?, ?, ?, ?, ?, NOW())
            ON DUPLICATE KEY UPDATE
              title = VALUES(title),
              publication_date = VALUES(publication_date),
              content = VALUES(content),
              extraction_timestamp = VALUES(extraction_timestamp),
              sync_timestamp = NOW(),
              updated_at = NOW()
          `;
          
          const values = [
            item.announcement_id,
            item.title || null,
            item.publication_date || null,
            item.content || null,
            item.extraction_timestamp || null
          ];
          
          await connection.execute(sql, values);
          successCount++;
          
        } catch (error) {
          console.error(`Failed to upsert news item ${item.announcement_id}:`, error);
        }
      }
      
      await connection.commit();
      console.log(`Successfully upserted ${successCount}/${newsData.length} news items`);
      
      return successCount;
      
    } catch (error) {
      await connection.rollback();
      console.error('Error in batch news upsert:', error);
      throw error;
    } finally {
      connection.release();
    }
  }

  /**
   * 批量插入或更新媒體內容
   * @param mediaData 媒體內容陣列
   * @returns Promise<number> 成功處理的記錄數
   */
  async batchUpsertMediaContent(mediaData: MediaContent[]): Promise<number> {
    if (mediaData.length === 0) {
      return 0;
    }

    const connection = await this.pool.getConnection();
    
    try {
      await connection.beginTransaction();
      
      let successCount = 0;
      
      for (const item of mediaData) {
        try {
          const sql = `
            INSERT INTO media_content (
              media_id, course_title, speaker_name, start_date, 
              redirect_url, media_type, extraction_timestamp, sync_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
            ON DUPLICATE KEY UPDATE
              course_title = VALUES(course_title),
              speaker_name = VALUES(speaker_name),
              start_date = VALUES(start_date),
              redirect_url = VALUES(redirect_url),
              media_type = VALUES(media_type),
              extraction_timestamp = VALUES(extraction_timestamp),
              sync_timestamp = NOW(),
              updated_at = NOW()
          `;
          
          const values = [
            item.media_id,
            item.course_title || null,
            item.speaker_name || null,
            item.start_date || null,
            item.redirect_url || null,
            item.media_type || null,
            item.extraction_timestamp || null
          ];
          
          await connection.execute(sql, values);
          successCount++;
          
        } catch (error) {
          console.error(`Failed to upsert media item ${item.media_id}:`, error);
        }
      }
      
      await connection.commit();
      console.log(`Successfully upserted ${successCount}/${mediaData.length} media items`);
      
      return successCount;
      
    } catch (error) {
      await connection.rollback();
      console.error('Error in batch media upsert:', error);
      throw error;
    } finally {
      connection.release();
    }
  }

  /**
   * 取得未通知的輪播內容
   * @param limit 限制數量
   * @returns Promise<CarouselContent[]> 輪播內容陣列
   */
  async getUnnotifiedCarouselContent(limit: number = 50): Promise<CarouselContent[]> {
    const sql = `
      SELECT * FROM carousel_content 
      WHERE is_notified = FALSE 
      ORDER BY extraction_timestamp DESC 
      LIMIT ?
    `;
    
    const [rows] = await this.pool.execute<RowDataPacket[]>(sql, [limit]);
    return rows as CarouselContent[];
  }

  /**
   * 取得未通知的課程取消內容
   * @param limit 限制數量
   * @returns Promise<CourseCancellation[]> 課程取消內容陣列
   */
  async getUnnotifiedCancellationContent(limit: number = 50): Promise<CourseCancellation[]> {
    const sql = `
      SELECT * FROM course_cancellations 
      WHERE is_notified = FALSE 
      ORDER BY extraction_timestamp DESC 
      LIMIT ?
    `;
    
    const [rows] = await this.pool.execute<RowDataPacket[]>(sql, [limit]);
    return rows as CourseCancellation[];
  }

  /**
   * 取得未通知的新聞內容
   * @param limit 限制數量
   * @returns Promise<NewsAnnouncement[]> 新聞內容陣列
   */
  async getUnnotifiedNewsContent(limit: number = 50): Promise<NewsAnnouncement[]> {
    const sql = `
      SELECT * FROM news_announcements 
      WHERE is_notified = FALSE 
      ORDER BY extraction_timestamp DESC 
      LIMIT ?
    `;
    
    const [rows] = await this.pool.execute<RowDataPacket[]>(sql, [limit]);
    return rows as NewsAnnouncement[];
  }

  /**
   * 取得未通知的媒體內容
   * @param limit 限制數量
   * @returns Promise<MediaContent[]> 媒體內容陣列
   */
  async getUnnotifiedMediaContent(limit: number = 50): Promise<MediaContent[]> {
    const sql = `
      SELECT * FROM media_content 
      WHERE is_notified = FALSE 
      ORDER BY extraction_timestamp DESC 
      LIMIT ?
    `;
    
    const [rows] = await this.pool.execute<RowDataPacket[]>(sql, [limit]);
    return rows as MediaContent[];
  }

  /**
   * 標記內容為已通知
   * @param contentType 內容類型
   * @param ids ID陣列
   * @returns Promise<number> 更新的記錄數
   */
  async markContentAsNotified(contentType: string, ids: number[]): Promise<number> {
    if (ids.length === 0) {
      return 0;
    }

    const tableMap: { [key: string]: string } = {
      'carousel': 'carousel_content',
      'cancellation': 'course_cancellations',
      'news': 'news_announcements',
      'media': 'media_content'
    };

    const tableName = tableMap[contentType];
    if (!tableName) {
      throw new Error(`Unknown content type: ${contentType}`);
    }

    const placeholders = ids.map(() => '?').join(',');
    const sql = `
      UPDATE ${tableName} 
      SET is_notified = TRUE, updated_at = NOW() 
      WHERE id IN (${placeholders})
    `;

    const [result] = await this.pool.execute<ResultSetHeader>(sql, ids);
    return result.affectedRows;
  }

  /**
   * 取得網站監控內容統計
   * @returns Promise<object> 統計資料
   */
  async getWebsiteMonitoringStats(): Promise<{
    carousel: { total: number; notified: number; unnotified: number };
    cancellation: { total: number; notified: number; unnotified: number };
    news: { total: number; notified: number; unnotified: number };
    media: { total: number; notified: number; unnotified: number };
  }> {
    const stats = {
      carousel: { total: 0, notified: 0, unnotified: 0 },
      cancellation: { total: 0, notified: 0, unnotified: 0 },
      news: { total: 0, notified: 0, unnotified: 0 },
      media: { total: 0, notified: 0, unnotified: 0 }
    };

    const tables = [
      { key: 'carousel', table: 'carousel_content' },
      { key: 'cancellation', table: 'course_cancellations' },
      { key: 'news', table: 'news_announcements' },
      { key: 'media', table: 'media_content' }
    ];

    for (const { key, table } of tables) {
      try {
        const sql = `
          SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_notified = TRUE THEN 1 ELSE 0 END) as notified,
            SUM(CASE WHEN is_notified = FALSE THEN 1 ELSE 0 END) as unnotified
          FROM ${table}
        `;
        
        const [rows] = await this.pool.execute<RowDataPacket[]>(sql);
        const row = rows[0];
        
        if (row) {
          stats[key as keyof typeof stats] = {
            total: parseInt(row.total) || 0,
            notified: parseInt(row.notified) || 0,
            unnotified: parseInt(row.unnotified) || 0
          };
        }
      } catch (error) {
        console.error(`Error getting stats for ${table}:`, error);
      }
    }

    return stats;
  }
}

// 建立單例實例
export const websiteMonitoringService = new WebsiteMonitoringService();