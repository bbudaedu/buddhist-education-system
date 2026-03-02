# New Book Notifier 獨立專案實作計畫

**Project Type**: BACKEND
**Overview**: 將現有附屬於 `Line-bot-llm-mysql` 專案中的 `ebook/` (Python) 網站偵測與新書簡介功能，獨立抽出為一個全新的 FastAPI 微服務專案 `new-book-notifier`。此服務將負責任務排程、網頁爬蟲、PDF 下載、Gemini AI 摘要生成，並在完成後透過 Webhook 推播及資料庫寫入通知 LINE Bot 端。

## 🎯 成功標準 (Success Criteria)
1. 成功建立 `new-book-notifier` 獨立專案，具備 `docker-compose.yml` 與 `.env` 配置。
2. 透過 FastAPI 提供 Webhook 接收與狀態查詢介面。
3. 系統能使用 `app-scheduler` 或自訂 Cron 邏輯獨立排程新書掃描任務。
4. 原 `Line-bot-llm-mysql` 不再負責啟動或管理 `ebook-processor` 容器。
5. 通過所有依賴套件與環境變數隔離測試。

---

## 🛠️ 技術棧 (Tech Stack)
- **語言**: Python 3.10+
- **框架**: FastAPI (用於 Webhook 與 API) + Uvicorn
- **核心庫**: Selenium (爬蟲), Google-genai (Gemini 摘要), PyPDF/PyMuPDF (文件解析)
- **排程管理**: APScheduler 或純 Python 排程迴圈
- **容器化**: Docker & Docker Compose
- **代碼品質**: Flake8 / Black (Linting & Formatting)

---

## 📂 預期檔案結構 (File Structure)

```text
/home/budaedu/projects/buddhist-education-system/new-book-notifier/
├── docs/                        # 專案文件
├── scripts/                     # 部署與驗證腳本
├── src/                         # 原始碼
│   ├── api/                     # FastAPI 路由 (Webhook, 狀態查詢)
│   ├── core/                    # 核心邏輯 (爬蟲, AI, 通知)
│   ├── models/                  # Pydantic 資料模型
│   ├── config.py                # Pydantic BaseSettings 環境變數載入
│   └── main.py                  # FastAPI 進入點與排程啟動
├── .env.example                 # 環境變數範本
├── .gitignore
├── requirements.txt             # Python 依賴
├── Dockerfile                   # 容器建置腳本
└── docker-compose.yml           # 容器編排
```

---

## 📋 任務拆解 (Task Breakdown)

### Task 1: 專案基礎建設與依賴遷移
- **Agent**: `backend-specialist`
- **Skill**: `app-builder`
- **輸入**: 原 `ebook/requirements.txt` 與目錄結構。
- **輸出**: 建立 `new-book-notifier` 資料夾，初始化 Git、`requirements.txt`、`.gitignore`、`Dockerfile` 與 `docker-compose.yml`。
- **驗證**: 執行 `docker compose build` 不報錯，且能進入容器環境。

### Task 2: 核心模組重構與 FastAPI 整合
- **Agent**: `backend-specialist`
- **Skill**: `clean-code`
- **輸入**: 原 `ebook/` 下的 Python 腳本 (如 `book_scraper.py`, `gemini_processor.py`, `main_processor.py`)。
- **輸出**: 將指令碼重構為模組化函數，並建立 FastAPI `main.py` 提供 `/health` 與手動觸發 `/trigger` 路由。引入 `pydantic` 的 `BaseSettings` 處理環境變數。
- **驗證**: 執行 `uvicorn src.main:app`，透過 `curl` 存取 `/health` 獲取 HTTP 200 回應。

### Task 3: 排程引擎實作
- **Agent**: `backend-specialist`
- **Skill**: `api-patterns`
- **輸入**: FastAPI 應用與原先在 Node.js 端的排程邏輯。
- **輸出**: 在 FastAPI 啟動事件 (Lifespan/Startup) 中整合 `APScheduler`，定期執行新書偵測任務。
- **驗證**: 啟動應用後，在 Console 觀察到 Scheduler 啟動日誌及定期任務觸發。

### Task 4: Webhook 通訊機制與資料庫清理
- **Agent**: `backend-specialist`
- **Skill**: `api-patterns`
- **輸入**: 原 `API_BASE_URL` 呼叫邏輯。
- **輸出**: 當新書摘要完成後，發送 HTTP POST Webhook 到 `Line-bot-llm-mysql`。若連線失敗，記錄 Error Log 並準備基本重試邏輯。移除 `Line-bot-llm-mysql` 中多餘的 Docker 服務定義 (`ebook-processor`)。
- **驗證**: 觸發掃描任務後，檢查 `Line-bot-llm-mysql` 伺服器是否正確收到 Webhook  payload。

### Task 5: 程式碼審查與清理 (Code Review Checklist)
- **Agent**: `security-auditor`
- **Skill**: `lint-and-validate`
- **輸入**: 完成的 `new-book-notifier` 專案。
- **輸出**: 移除非必要、寫死的 API Key 或帳號密碼，確保遵循 AI 防御 (Prompt Injection) 與 SQL 注入防護規範。
- **驗證**: 執行預先設定的 Linting 或安全掃描腳本 (Phase X)。

---

## 🛡️ 可行性與風險 (Risks & Mitigation)
- **LINE Bot 連線失敗**: 使用簡單的回退機制，失敗時記錄至特定 Log 檔供後續 PagerDuty 擷取或手動重發。
- **爬蟲依賴 ChromeDriver**: `Dockerfile` 需確保正確安裝 Chrome 與 ChromeDriver，建議使用 `selenium/standalone-chrome` 基底映像檔或正確指令避免版本不符問題。

---

## ✅ Phase X: Verification Plan (驗證計畫)

### 1. 自動化測試腳本
- **指令**: `python .agent/skills/lint-and-validate/scripts/lint_runner.py ./new-book-notifier`
- **指令**: `python .agent/skills/vulnerability-scanner/scripts/security_scan.py ./new-book-notifier`

### 2. 環境與容器測試
```bash
# 切換至專案目錄
cd /home/budaedu/projects/buddhist-education-system/new-book-notifier

# 測試構建
docker compose build

# 啟動服務 (背景)
docker compose up -d

# 檢查健康狀態 API
curl http://localhost:8000/health
# 預期輸出: {"status": "ok"}
```

### 3. Webhook 整合測試
- **指令**: 透過腳本或 Postman 對 `new-book-notifier` 發送 POST 到 `/trigger` 手動觸發新書檢查程序。
- **驗證**: 觀察 `Line-bot-llm-mysql` 容器是否成功接收來自 Webhook 的資料，並觸發 LINE 通知廣播。
