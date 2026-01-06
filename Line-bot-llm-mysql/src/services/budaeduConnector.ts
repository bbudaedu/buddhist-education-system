import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import https from 'https';

/**
 * Budaedu Connector
 * 負責統一處理與佛陀教育基金會 API 的連線設定
 * 包含 SSL 憑證忽略、User-Agent 設定與錯誤處理
 */
export class BudaeduConnector {
    private axiosInstance: AxiosInstance;

    constructor() {
        this.axiosInstance = axios.create({
            httpsAgent: new https.Agent({
                rejectUnauthorized: false // 忽略 SSL 憑證驗證
            }),
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout: 10000 // 預設 10 秒超時
        });
    }

    /**
     * 發送 GET 請求
     * @param url 請求 URL
     * @param config Axios 設定 (可選)
     * @returns Promise<T> 回傳資料
     */
    async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
        try {
            const response = await this.axiosInstance.get<T>(url, config);
            return response.data;
        } catch (error: any) {
            console.error(`API Request Failed: ${url}`);
            if (error.response) {
                console.error(`Status: ${error.response.status}`);
                console.error(`Data: ${JSON.stringify(error.response.data)}`);
            } else {
                console.error(`Error: ${error.message}`);
            }
            throw error;
        }
    }

    /**
     * 發送 HEAD 請求（用於檢查 URL 是否有效）
     * @param url 請求 URL
     * @param config Axios 設定 (可選)
     * @returns Promise<AxiosResponse> 回傳完整 response
     */
    async head(url: string, config?: AxiosRequestConfig) {
        return this.axiosInstance.head(url, config);
    }
}

// 匯出單例
export const budaeduConnector = new BudaeduConnector();
