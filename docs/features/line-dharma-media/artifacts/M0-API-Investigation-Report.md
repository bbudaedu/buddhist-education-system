# Context: Budaedu.org API Integration Specification (v5.2)

**Role**: You are a Backend Engineer building a data connector for the Budaedu (佛陀教育基金會) system.
**Constraint**: DO NOT use web scraping (Selenium/BeautifulSoup). Use ONLY the verified HTTP API endpoints documented below.
**Tech Stack**: Node.js (Axios) or Python (Requests/FastAPI).

---

## 1. Domain: Dharma Books (經書法寶)

### 1.1 Book List (Search & Index)
* **Endpoint**: `GET https://publish.budaedu.org/dharma/public/api/books/chinese`
* **Purpose**: Search books to get `id` and `code`.
* **Query Parameters**:
    * `per_page`: `10` (Adjustable)
    * `page`: `1`
    * `order`: `latest_storage_date,desc`
    * `filter[name]`: `{keyword}` (Optional: Search by book title)
    * `filter[have_efile]`: `Y` (Optional: Only show books with digital files)
* **Response Fields**:
    * `id`: Book ID (用於後續 API 調用)
    * `code`: Book code (如 "CH382-16"，用於構建封面 URL)
    * `chinese_name`: 書名
    * `chinese_author`: 作者
    * `chinese_intro`: **HTML格式簡介**（需清理標籤後使用）
    * `latest_storage_date`: 上架日期

### 1.2 Book Details (Metadata & Intro)
* **Endpoint**: `GET https://publish.budaedu.org/dharma/public/api/books/{id}`
* **Purpose**: Get detailed metadata, HTML introduction, and author info without fetching file lists.
* **Response Handling**:
    * **Intro**: `data.chinese_intro` (HTML string, requires stripping)
    * **Spec**: `data.chinese_spec` (e.g., "25/精/書盒")
    * **Author**: `data.chinese_author`
    * **Stock**: `data.in_stock` ("Y"/"N")
* **⚠️ Note**: 此 API 目前有數據庫連線問題（500錯誤），建議直接使用 List API 的 `chinese_intro` 欄位。

### 1.3 PDF Download Link (Files)
* **Endpoint**: `GET https://publish.budaedu.org/dharma/public/api/books/{id}/efiles`
* **Purpose**: Get the direct PDF URL and file size.
* **Query Parameters**:
    * `include`: `attached` (**CRITICAL**: Required to link file back to book metadata)
    * `order`: `name,asc`
* **Response Handling**:
    * Target Path: `data[0].url` (The PDF link)
    * Target Size: `data[0].formatted_size`
* **Performance Consideration**: 
    * 需要對每本書進行額外 API 調用
    * 建議使用 `Promise.all()` 並行處理以優化性能
    * 設定合理的 timeout（如 5 秒）避免單個請求拖慢整體

### 1.4 Cover Image Logic (Computed Resource)
* **Pattern**: No API call required. Construct URL string using the Book Code.
* **Logic**:
    1.  Get `code` from Book List/Detail API (e.g., `CH550-03`).
    2.  Remove hyphens (`-`).
    3.  Append `.jpg`.
    4.  Prepend Base URL: `https://www2.budaedu.org/dharma-data/book-front-cover/`
* **Example**:
    * Code: `CH550-03` -> `CH55003`
    * URL: `https://www2.budaedu.org/dharma-data/book-front-cover/CH55003.jpg`
* **TypeScript Implementation**:
```typescript
private buildCoverImageUrl(code: string): string {
  if (!code) return 'https://www.budaedu.org/img/logo.png';
  const cleanCode = code.replace(/-/g, '');
  return `https://www2.budaedu.org/dharma-data/book-front-cover/${cleanCode}.jpg`;
}
```

### 1.5 HTML Intro Cleaning
* **Input**: `chinese_intro` (HTML格式，包含 `<p>`, `<span>` 等標籤)
* **Cleaning Steps**:
    1. 移除所有 HTML 標籤：`/<[^>]*>/g`
    2. 解碼 HTML entities（`&nbsp;`, `&lt;`, `&gt;`, etc.）
    3. 合併多餘空白：`/\s+/g` → 單一空格
    4. 截取前100字並加上省略號（如果超過）
* **TypeScript Implementation**:
```typescript
private stripHtmlTags(html: string): string {
  if (!html) return '';
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ')
    .trim();
}
```

---

## 2. Domain: Live Streaming (直播週表)

### 2.1 Daily Schedule
* **Endpoint**: `GET https://publish.budaedu.org/laravel/public/api/courses`
* **Purpose**: Get real-time schedule and HLS streaming links.
* **Query Parameters**:
    * `filter[week]`: `{1-7}` (1=Mon, 2=Tue, ..., 7=Sun)
    * `filter[have_live_stream]`: `true`
    * `filter[continued]`: `true` (Active courses)
    * `include`: `places` (**CRITICAL**: Contains the live URL)
    * `order`: `spk_start_time,asc|spk_end_time,asc`
* **Response Handling**:
    * Course Title: `title_name`
    * Lecturer: `lecturer.lecr_name`
    * Time: `spk_start_time` ~ `spk_end_time`
    * **Stream URL**: Find `live_stream_url` (Prefer `https` .m3u8 link). Avoid `pc_live_url` (MMS protocol).

---

## 3. Domain: Video Series (影音點播 / VOD)

### 3.1 Ongoing Courses List
* **Endpoint**: `GET https://publish.budaedu.org/audiovisual/public/api/series/by-keyword-searched`
* **Purpose**: Get a list of ongoing video lecture series.
* **Query Parameters**:
    * `filter[ended]`: `N` (Ongoing only)
    * `filter[IsDirtyEntry]`: `N`
    * `order`: `latest_filedate,desc` (Sort by recently updated)
    * `per_page`: `12`
* **Response Handling**:
    * Series ID: `title_no`
    * Video Count: `VL_nfiles`
    * Last Update: `latest_filedate`

---

## 4. Implementation Logic (Enhanced)

### Workflow: "Enhanced Book Display with Cover, Description, and PDF"
```typescript
async getLatestBooks(limit: number = 5): Promise<DharmaBook[]> {
  // Step 1: Fetch Book List
  const response = await budaeduConnector.get('/dharma/public/api/books/chinese', {
    params: { per_page: limit, order: 'latest_storage_date,desc' }
  });
  
  const rawBooks = response.data || [];
  
  // Step 2: Parallel fetch PDF URLs
  const booksWithFiles = await Promise.all(
    rawBooks.map(async (item: any) => {
      const pdfUrl = await this.getBookPdfUrl(item.id);
      return { ...item, pdfUrl };
    })
  );
  
  // Step 3: Transform data
  const books: DharmaBook[] = booksWithFiles.map((item: any) => {
    // Clean intro
    const cleanIntro = this.stripHtmlTags(item.chinese_intro || '');
    const description = cleanIntro.length > 100
      ? cleanIntro.substring(0, 100) + '...'
      : cleanIntro;
    
    return {
      id: String(item.id),
      title: item.chinese_name,
      author: item.chinese_author,
      description: description || '暫無簡介',
      coverImageUrl: this.buildCoverImageUrl(item.code),
      pdfUrl: item.pdfUrl || '',
      publishDate: item.latest_storage_date.split(' ')[0]
    };
  });
  
  return books;
}
```

---

## 5. LINE Flex Message Integration

### Enhanced Book Carousel Features
1. **封面圖**: 使用 `coverImageUrl`，失敗則 fallback 到 logo
2. **簡介**: 顯示清理後的 100 字描述
3. **雙按鈕佈局**:
   - **主要按鈕** (Primary): "📖 閱讀 PDF" (當 `pdfUrl` 存在)
   - **次要按鈕** (Link): "查看詳情" (連到完整目錄)
4. **查看更多卡片**: Carousel 最後一張卡片提供完整目錄連結

### Button Layout Example
```typescript
footer: {
  type: 'box',
  layout: 'vertical',
  spacing: 'sm',
  contents: book.pdfUrl ? [
    { type: 'button', style: 'primary', label: '📖 閱讀 PDF' },
    { type: 'button', style: 'link', label: '查看詳情' }
  ] : [
    { type: 'button', style: 'primary', label: '查看詳情' }
  ]
}
```

---

## 6. Performance Optimization

### Caching Strategy
- **Cache Key**: `dharma_books_enhanced_{limit}`
- **TTL**: 300 seconds (5 minutes)
- **Reason**: API 資料更新頻率低，快取可大幅減少 API 調用次數

### Parallel Processing
- 使用 `Promise.all()` 並行獲取 PDF URLs
- 設定 5 秒 timeout 避免單個請求拖慢整體
- Try-catch 包裹每個請求，確保單個失敗不影響其他書籍

---

**Last Updated**: 2025-11-27  
**Version**: 5.2 (Enhanced Book Display Implementation)