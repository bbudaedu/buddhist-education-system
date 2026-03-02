# 網站選擇器配置
# 基於 Chrome DevTools MCP 實際檢測結果
# 檢測日期: 2025-11-10

## 書籍頁面 (https://www.budaedu.org/#/books/applicable/chinese)
- 書籍卡片: `.card.overflow-hidden` (10 個)
- 書籍標題: `h5`
- 作者資訊: `p`
- 書籍封面: `img.card-img-left`

## 首頁輪播 (https://www.budaedu.org/#/)
- 輪播項目: `.carousel-item` (4 個)
- 輪播圖片: `.carousel-item img`

## 首頁最新法寶
- 卡片容器: `.card` (13 個)
- 書籍標題: `h4`

## 等待頁面載入
- 等待選擇器: `.card.overflow-hidden, .card, .carousel-item`

## 重要提示
1. 這是一個 Vue.js SPA 應用，使用 Hash-based routing (#/)
2. 頁面需要額外的等待時間讓 JavaScript 渲染內容（建議 5-8 秒）
3. 書籍頁面和首頁使用不同的標題標籤（h5 vs h4）
4. 所有 URL 都需要包含 # 符號，例如: `/#/books/applicable/chinese`

## 測試結果
- ✓ 書籍卡片選擇器已驗證
- ✓ 輪播選擇器已驗證
- ✓ 頁面載入等待已驗證
