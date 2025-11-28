# User Preferences (使用者偏好設定)

**最後更新**: 2025-11-26

## 1. 溝通與語言
- **主要語言**: 繁體中文 (Traditional Chinese)
- **溝通風格**: 專業、結構化、角色扮演 (Role-Playing)
- **回應格式**: 使用 Markdown，多用列表、表格和粗體強調關鍵字。

## 2. 工作流程偏好
- **Agent 協作模式**: 
  - 用戶會切換不同 Agent 角色 (PM, Feature Owner, Backend, Frontend, QA, DevOps)。
  - Agent 需根據當前角色執行特定任務，並更新共享文檔。
- **文檔驅動 (Document-Driven)**:
  - 任務來源：`TASKS.md`
  - 進度追蹤：`MILESTONES.md`
  - 核心需求：`PRD.md`
  - 協作產出：`artifacts/` 目錄下的報告
- **Artifact 管理**:
  - 關鍵流程需產出 Artifact 文件 (如 API 調查報告、UX 優化建議)。
  - 檔案路徑需嚴格遵守專案結構。

## 3. 技術偏好
- **前端**: Flex Message (LINE Bot), Vanilla CSS (若有 Web 頁面)
- **後端**: Node.js (TypeScript), Python (AI/Scraping)
- **資料庫**: MySQL 8.0
- **API**: 優先使用 RESTful API，並實作快取機制。
- **安全性**: HTTPS, SQL Injection 防護。

## 4. 特殊指令
- **Turbo Mode**: 允許對 `run_command` 使用 `// turbo` 標註以自動執行。
- **Task Boundary**: 任務邊界需清晰，對應 `task.md` 或 `TASKS.md`。