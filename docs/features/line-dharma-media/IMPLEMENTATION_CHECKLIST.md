# LINE Dharma Media - 實施檢查清單 (IMPLEMENTATION_CHECKLIST.md)

此清單用於開發與 Code Review 階段，確保技術實作符合品質標準。

---

## 🔹 後端開發 (Backend)

### API 串接
- [ ] **錯誤處理**: 當官網 API 回傳 404, 500 或 Timeout 時，是否有 Catch 並回傳預設空數據或友善訊息？
- [ ] **快取機制**:
  - [ ] 書籍列表是否設定了 5 分鐘快取？
  - [ ] 影音列表是否設定了 10 分鐘快取？
  - [ ] 直播列表是否設定了 1 分鐘快取？
- [ ] **數據解析**:
  - [ ] 是否正確過濾了 HTML 標籤 (如 `intro` 欄位)？
  - [ ] 是否正確處理了 Unicode 字符？

### 資料庫
- [ ] **Migration**: `subscribed_videos` 欄位是否正確添加？預設值是否為 `FALSE` (或 0)？
- [ ] **效能**: 訂閱查詢是否使用了索引？

---

## 🔹 前端/LINE 介面 (Frontend)

### Flex Message
- [ ] **圖片顯示**:
  - [ ] 是否實作了 Cover Mode (Aspect Ratio 2:3 或 16:9)？
  - [ ] 當圖片 URL 無效時，是否顯示 Fallback Image？
- [ ] **文字長度**: 標題過長時是否正確截斷 (Ellipsis)？
- [ ] **按鈕動作**:
  - [ ] 書籍下載按鈕是否包含 `?openExternalBrowser=1`？
  - [ ] 觀看按鈕連結是否為 HTTPS？

### 互動體驗
- [ ] **Quick Reply**: 是否包含所有 5 個選項？
- [ ] **回應速度**: Bot 是否能在 3 秒內回應？(若超過需優化或使用 Loading 動畫)

---

## 🔹 測試與發布 (QA & DevOps)

- [ ] **Android 測試**: 真機測試 PDF 下載功能是否正常喚起瀏覽器？
- [ ] **訂閱測試**: 點擊訂閱/取消訂閱後，資料庫狀態是否即時更新？
- [ ] **環境變數**: 生產環境的 API URL 是否配置正確？
