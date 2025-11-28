# LINE Dharma Media - 下一步行動 (NEXT_ACTIONS.md)

**最後更新**: 2025-11-25  
**當前階段**: M1 - 後端服務開發

---

## 🎯 立即執行 (Immediate Actions)

### 1. 啟動 M1 開發 (Backend Engineer)
請 Backend Engineer Agent 立即開始執行以下任務：

- **TASK-101**: 實作 `DharmaBookService`
  - 參考 PRD v1.7 的 FR-001 規格。
  - 確保處理 `cover_url` 的邏輯。

- **TASK-102**: 實作 `VideoStreamingService`
  - 參考 PRD v1.7 的 FR-004 規格。
  - 重點：解析直播的 HLS URL。

### 2. 資料庫變更 (Backend Engineer)
- **TASK-105**: 準備 `subscribers` 表的 Migration Script。

---

## 📋 執行指引

**如何開始？**
請輸入以下指令喚醒 Backend Engineer：
> "我是 Backend Engineer，請執行 line-dharma-media 的 TASK-101 和 TASK-102，實作書籍與直播的 API 串接服務。"

**完成後做什麼？**
1. 更新 `TASKS.md` 將對應任務標記為 `[x]`。
2. 產生 M1 結案報告，並觸發 UX 腦力激盪會議。

---

## 📊 當前狀態快照
- **PRD**: v1.7 (已確認 API 規格)
- **M0**: ✅ 完成
- **M1**: 🟡 準備開始
- **阻礙**: 無
