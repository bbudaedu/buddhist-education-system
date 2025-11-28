# QA 交接文檔 - LINE Dharma Media

**交接日期**: 2025-11-24  
**PM-Lead**: Product Team  
**QA Team**: 請自行創建測試計劃

---

## 專案概況

### 功能摘要
- **最新法寶**: LINE Bot 指令，顯示最新佛教書籍（含封面圖）
- **最新影音**: LINE Bot 指令，顯示最新直播/影音（含講師照）

### 已完成里程碑
- ✅ **M0**: API 調查（確認混合式架構：Scraper + API）
- ✅ **M1**: 後端服務（Python Scraper 整合、Video API、DB 建立）
- ✅ **M2**: Webhook 整合（指令處理、Flex Message、Quick Reply）

### 當前狀態
- **M3**: 測試與優化（QA 負責）
- **目標日期**: 2025-11-29

---

## 關鍵文檔

### 必讀文檔
1. **PRD v1.6**: [`docs/features/line-dharma-media/PRD.md`](file:///d:/AIstudio/newinfo/docs/features/line-dharma-media/PRD.md)
   - 完整功能需求、使用者故事、驗收標準
2. **TASKS.md**: [`docs/features/line-dharma-media/TASKS.md`](file:///d:/AIstudio/newinfo/docs/features/line-dharma-media/TASKS.md)
   - M3 測試任務清單（TASK-301 ~ TASK-306）
3. **MILESTONES.md**: [`docs/features/line-dharma-media/MILESTONES.md`](file:///d:/AIstudio/newinfo/docs/features/line-dharma-media/MILESTONES.md)
   - 專案進度與驗收標準

### 技術參考
- **技術架構**: [`docs/features/line-dharma-media/artifacts/architecture/TECHNICAL_ARCHITECTURE.md`](file:///d:/AIstudio/newinfo/docs/features/line-dharma-media/artifacts/architecture/TECHNICAL_ARCHITECTURE.md)
- **實作檔案**:
  - `Line-bot-llm-mysql/src/handlers/dharmaMediaHandler.ts`
  - `Line-bot-llm-mysql/src/services/flexMessageService.ts`
  - `ebook/run_dharma_book_scraper.py`

---

## 測試範圍建議

### 核心功能
1. **指令處理**:
   - 輸入「最新法寶」→ 顯示書籍 Carousel
   - 輸入「最新影音」→ 顯示影音 Carousel
2. **資料正確性**:
   - 書籍顯示標題、作者、封面圖
   - 影音顯示講師、主題、照片
3. **Quick Reply**:
   - 訂閱按鈕功能正常

### 整合測試
- Python Scraper → `POST /api/sync/dharma-books` → MySQL → LINE Bot

### 非功能需求
- API 快取機制（1分鐘 TTL）
- 錯誤處理（無資料、API 失敗）

---

## QA 任務

### 請自行完成
1. **測試計劃**: 根據 PRD 制定詳細測試用例
2. **測試執行**: 涵蓋功能、整合、效能測試
3. **Bug 報告**: 使用專案 Issue Tracker
4. **測試報告**: 記錄於 `artifacts/M3-Test-Report.md`

### 交付物
- [ ] 測試計劃文檔
- [ ] 測試用例清單
- [ ] 測試執行報告
- [ ] Bug 清單（如有）

---

## PM-Lead 支援

如有問題或需要額外資源，請聯繫 PM-Lead。

**Good Luck! 🎯**
