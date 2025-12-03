import { budaeduConnector } from './budaeduConnector';
import { BuddhaCard } from '../types/buddhaCard';

export class BuddhaCardService {
    private readonly API_URL = 'https://publish.budaedu.org/dharma/public/api/pictures';
    private readonly IMAGE_BASE_URL = 'https://www2.budaedu.org/dharma-data/picture-downloadable-efile';

    /**
     * 獲取最新佛卡
     * @param limit 數量限制，預設 5
     */
    async getLatestBuddhaCards(limit: number = 5): Promise<BuddhaCard[]> {
        try {
            // 1. 使用官方參數獲取佛卡列表
            // filter[have_efile]=1: 確保有電子檔 (即有縮圖)
            // order: 指定排序規則
            // per_page: 限制數量
            const response = await budaeduConnector.get<any>(this.API_URL, {
                params: {
                    'filter[have_efile]': 1,
                    'order': 'in_stock,asc|chinese_display_order,asc|latest_storage_date,desc|created_at,desc',
                    'per_page': limit,
                    'page': 1
                }
            });

            let cards: any[] = [];
            if (Array.isArray(response)) {
                cards = response;
            } else if (response && Array.isArray(response.data)) {
                cards = response.data;
            } else {
                console.error('BuddhaCard API response is not an array or {data: array}:', response);
                return [];
            }

            // 2. 轉換格式 (API 已排序，無需再次排序)
            return cards.map(card => ({
                id: card.id,
                code: card.code,
                title: card.chinese_name || card.name || '無標題',
                // 構造圖片 URL: https://www2.budaedu.org/dharma-data/picture-downloadable-efile/{code}.jpg
                // 注意：有些 code 可能已經包含副檔名，或者需要處理大小寫，這裡假設是 .jpg
                // 如果 API 返回的 code 是 "BP019"，則 URL 是 ".../BP019.jpg"
                imageUrl: `${this.IMAGE_BASE_URL}/${card.code}.jpg`,
                updatedAt: card.updated_at
            }));

        } catch (error) {
            console.error('Failed to fetch Buddha cards:', error);
            return [];
        }
    }
}

export const buddhaCardService = new BuddhaCardService();
