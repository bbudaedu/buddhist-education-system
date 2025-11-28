# LINE Bot Dharma & Media Features - 產品需求文檔 (PRD)

**版本**：1.7  
**日期**：2025-11-25  
**負責人**：Product Team  
**狀態**：已批准 (M0 Complete, Ready for M1)

---

## 文檔變更歷史

| 版本 | 日期 | 變更內容 | 變更人 |
|------|------|----------|--------|
| 1.0 | 2025-11-21 | 初始版本 | Product Team |
| 1.1 | 2025-11-21 | 變更資料來源：從MySQL改為即時API抓取 | Product Team |
| 1.2 | 2025-11-21 | 修正FR-008：僅PDF連結需openExternalBrowser參數 | Product Team |
| 1.3 | 2025-11-21 | 更新FR-007 & FR-011：Quick Reply複用與新增影音訂閱 | Product Team |
| 1.4 | 2025-11-21 | 術語更正：統一為「直播」與「影音」 | Product Team |
| 1.5 | 2025-11-21 | 增強UX：FR-002新增書籍封面圖顯示需求 | Product Team |
| 1.6 | 2025-11-21 | 新增圖片資源需求：講師照片和縮圖URL | Product Team |
| 1.7 | 2025-11-25 | **技術規格更新**：根據 M0 報告確認最終 API 端點與資料結構 | Feature Owner |

---

## 1. 執行摘要

本專案旨在為LINE Bot新增「最新法寶」與「最新影音」兩大功能，透過即時串接官網API，讓用戶能快速獲取並訂閱最新的佛教書籍與影音資源。這將顯著提升用戶黏著度，並透過視覺化優化（封面圖、講師照）提供更優質的瀏覽體驗。

**關鍵要點**：
- 🎯 **目標**：提供即時、視覺化的法寶與影音資訊查詢及訂閱服務
- 👥 **用戶**：所有關注佛陀教育基金會資源的LINE Bot用戶
- 📊 **成功指標**：日查詢量 > 100次，訂閱轉換率 > 15%
- 📅 **計劃時間線**：2025-11-21 至 2025-12-05

---

## 2. 功能需求 (Functional Requirements)

### FR-001: 最新法寶查詢 (Latest Dharma Books)
- **觸發指令**：用戶輸入「最新法寶」或點擊選單對應按鈕。
- **資料來源**：即時呼叫官網API（已確認）。
  - **Endpoint**: `https://publish.budaedu.org/dharma/public/api/books/chinese`
  - **Method**: `GET`
  - **Params**: `per_page=5`, `page=1`, `order=latest_storage_date,desc`
- **顯示內容**：
  - 顯示最新 **5本** 書籍。
  - 格式：Flex Message Carousel。
  - **卡片內容**：
    - **封面圖** (Cover Image)：優先顯示API提供的封面圖；若無則顯示預設圖示。
    - **標題** (Title)：書籍名稱 (`name_zh`)。
    - **作者** (Author)：作者/譯者/講者。
    - **發布日期** (Date)：出版/上架日期 (`storage_date`)。
    - **詳情按鈕**：開啟官網書籍詳情頁。
    - **下載按鈕**：直接開啟PDF檔案（需加上 `?openExternalBrowser=1`）。

### FR-002: 書籍封面圖顯示 (Book Cover Display)
- **優先級**：P0
- **邏輯**：
  1. 檢查API回傳資料是否有 `cover_url`。
  2. 若有且有效，顯示該圖片（Aspect Ratio: 2:3, Mode: Cover）。
  3. 若無，顯示系統預設的書籍圖示（藍色背景）。

### FR-003: PDF外部瀏覽器開啟 (External Browser for PDF)
- **修正 (v1.2)**：
  - **僅** PDF下載連結需附加 `?openExternalBrowser=1` 參數。
  - 原因：Android版LINE內建瀏覽器無法直接下載PDF，需引導至外部瀏覽器。
  - 一般網頁連結（如詳情頁）**不** 需要此參數。

### FR-004: 最新影音查詢 (Latest Videos & Live Streams)
- **觸發指令**：用戶輸入「最新影音」。
- **資料來源**：即時呼叫官網API（已確認）。
  - **直播 (Live)**:
    - **Endpoint**: `https://publish.budaedu.org/laravel/public/api/courses`
    - **Params**: `filter[week]=X` (current weekday), `filter[have_live_stream]=true`, `include=places`
  - **影音 (Series)**:
    - **Endpoint**: `https://publish.budaedu.org/audiovisual/public/api/series/by-keyword-searched`
    - **Params**: `filter[ended]=N`, `filter[IsDirtyEntry]=N`, `order=latest_filedate,desc`, `per_page=12`
- **顯示內容**：
  - 顯示 **5個直播** (Live) + **5個影音** (Video)，共10張卡片。
  - 格式：Flex Message Carousel。
  - **卡片內容**：
    - **圖片**：優先顯示講師照片或影片縮圖；若無則顯示預設圖示。
    - **標題**：課程/影片主題 (`title_name`)。
    - **講師**：講師姓名 (`lecr_name`)。
    - **類型標籤**：[直播] 或 [影音]。
    - **日期**：直播日期或發布日期 (`latest_filedate`)。
    - **觀看按鈕**：連結至YouTube或官網播放頁。

### FR-005: 影音圖片顯示 (Video/Instructor Image)
- **優先級**：P0 (v1.6新增)
- **邏輯**：
  1. 優先使用 `instructor_photo_url` (講師照片)。
  2. 次之使用 `thumbnail_url` (影片縮圖)。
  3. 若皆無，使用預設圖示（直播：紅色背景🎥；影音：綠色背景📹）。

### FR-006: Quick Reply 按鈕 (Quick Replies)
- **複用現有實作 (v1.3)**：
  - 直接使用 `bulletinService` 的 Quick Reply 結構。
  - 按鈕列表：
    1. 📰 訂閱最新消息
    2. 📚 訂閱新書通知
    3. 🎥 訂閱最新影音 (新功能)
    4. 📊 訂閱狀態查詢
    5. ❌ 取消訂閱

### FR-007: 訂閱最新影音 (Subscribe to Videos)
- **功能**：允許用戶訂閱影音更新通知。
- **資料庫變更**：
  - 表：`subscribers`
  - 欄位：新增 `subscribed_videos` (BOOLEAN, default FALSE)
- **互動流程**：
  - 用戶點擊「訂閱最新影音」Quick Reply。
  - 系統更新資料庫。
  - 回覆確認訊息：「✅ 已成功訂閱最新影音通知！」

---

## 3. 非功能需求 (Non-Functional Requirements)

### NFR-001: 效能要求
- **API回應時間**：LINE Bot 回應需在 **3秒** 內完成（避免 Timeout）。
- **快取策略**：
  - 書籍列表：5分鐘 (TTL)
  - 影音列表：10分鐘 (TTL)
  - 直播列表：1分鐘 (TTL, 確保即時性)

### NFR-002: 可靠性
- **API 錯誤處理**：若官網 API 失敗，需回傳友善錯誤訊息（例如：「目前無法取得最新資訊，請稍後再試」），不可讓 Bot 無回應。
- **圖片載入失敗**：需有預設圖片 (Fallback Image) 機制。

### NFR-003: 安全性
- **HTTPS**：所有外部連結必須使用 HTTPS。
- **SQL Injection**：用戶輸入需經過過濾（雖然此功能主要透過按鈕觸發）。

---

## 4. 數據追蹤 (Analytics)

需追蹤以下事件以評估功能成效：
- `feature_usage`: `dharma_books` (最新法寶查詢次數)
- `feature_usage`: `latest_videos` (最新影音查詢次數)
- `subscription_change`: `subscribe_videos` (影音訂閱人數)
- `click_event`: `book_detail`, `book_download`, `video_watch` (點擊轉化率)

---

## 5. 附錄：API 規格摘要 (M0 結果)

| 資源 | Endpoint | 關鍵參數 | 備註 |
|------|----------|----------|------|
| **書籍** | `/dharma/public/api/books/chinese` | `per_page=5`, `order=latest_storage_date,desc` | 需處理 `cover_url` |
| **直播** | `/laravel/public/api/courses` | `filter[week]=X`, `filter[have_live_stream]=true` | 需過濾當日直播 |
| **影音** | `/audiovisual/public/api/series/by-keyword-searched` | `filter[ended]=N`, `order=latest_filedate,desc` | 取前5筆 |
  - 新增欄位：`subscribed_videos` (BOOLEAN, default 0)
- **互動**：點擊Quick Reply後，更新資料庫並回覆確認訊息。

---

## 3. 技術規格 (Technical Specifications)

### 3.1 API 整合 (Confirmed v1.7)

**Base Domain**: `publish.budaedu.org`

#### 書籍 API (Books)
- **Endpoint**: `/dharma/public/api/books/chinese`
- **Method**: GET
- **Parameters**: `per_page=5`, `page=1`, `order=latest_storage_date,desc`
- **Response Fields**: `code` (ID), `name_zh` (Title), `author_name` (Author), `storage_date` (Date), `downloads` (PDF), `cover_url` (Cover)

#### 直播 API (Live Streams)
- **Endpoint**: `/laravel/public/api/courses`
- **Method**: GET
- **Parameters**: `filter[week]={current_weekday}`, `filter[have_live_stream]=true`, `include=places`
- **Response Fields**: `title_name`, `lecturer.lecr_name`, `schedules[].places[].live_stream_url`

#### 影音 API (Video Series)
- **Endpoint**: `/audiovisual/public/api/series/by-keyword-searched`
- **Method**: GET
- **Parameters**: `filter[ended]=N`, `order=latest_filedate,desc`, `per_page=10`
- **Response Fields**: `title_no` (ID), `title_name`, `lecr_name` (Instructor), `latest_filedate` (Date)

### 3.2 資料結構 (TypeScript Interfaces)

```typescript
interface DharmaBook {
  id: string;
  title: string;
  author: string;
  coverImageUrl?: string;
  publishDate?: string;
  pdfUrl?: string;
}

interface VideoContent {
  id: string;
  title: string;
  instructor: string;
  startTime?: string; // For Live
  link: string;
  isLive: boolean;
  type: 'live' | 'video';
  thumbnailUrl?: string;
}
```

### 3.3 快取策略 (Caching)
- **TTL**: 60秒 (1分鐘)
- **機制**: 記憶體快取 (Memory Cache)
- **目的**: 避免頻繁呼叫API，同時確保資料相對即時。

---

## 4. 非功能需求 (Non-Functional Requirements)

1. **效能**：API回應處理需在 3秒內完成。
2. **容錯**：若API失敗，需回傳友善錯誤訊息，不可讓Bot崩潰。
3. **相容性**：Flex Message需在 iOS/Android/Desktop LINE 正常顯示。
4. **安全性**：API呼叫需處理SSL憑證問題 (目前開發環境可能需 `rejectUnauthorized: false`)。

---

## 5. 驗收標準 (Verification Criteria)

### 功能驗收
- [ ] 輸入「最新法寶」能顯示5張書籍卡片。
- [ ] 書籍卡片顯示封面圖（若有）。
- [ ] 點擊書籍PDF下載能開啟瀏覽器（Android測試）。
- [ ] 輸入「最新影音」能顯示5直播+5影音。
- [ ] 影音卡片顯示講師照片或縮圖。
- [ ] Quick Reply 包含「訂閱最新影音」選項。
- [ ] 點擊訂閱能成功更新資料庫狀態。

### 技術驗收
- [ ] API 呼叫成功且資料解析正確。
- [ ] 快取機制生效（1分鐘內重複請求不打API）。
- [ ] 錯誤處理機制能捕捉API異常。

---

## 6. 實作計劃 (Implementation Plan)

詳見 [MILESTONES.md](./MILESTONES.md) 與 [TASKS.md](./TASKS.md)。

- **M0**: API端點調查與驗證 (Critical)
- **M1**: 後端服務開發 (Service Layer)
- **M2**: Webhook整合與指令處理
- **M3**: 測試與優化
- **M4**: 部署與發布

---

## 7. 附錄：資料庫 Schema 變更

```sql
ALTER TABLE subscribers 
ADD COLUMN subscribed_videos TINYINT(1) DEFAULT 0 
AFTER subscribed_new_books;
```

---

**文檔維護**：Product Team  
**最後更新**：2025-11-21 (v1.6)
