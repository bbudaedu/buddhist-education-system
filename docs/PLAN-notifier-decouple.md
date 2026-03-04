# PLAN: 將 new-book-notifier 從 buddhist-education-system 獨立出去

**概述**：將目前位於 `buddhist-education-system/new-book-notifier/` 子目錄的微服務，提取為一個獨立的 GitHub Repository，使其擁有自己的版本控制、CI/CD 與部署流程。

---

## 📊 現況分析

| 項目 | 狀態 |
|------|------|
| 程式碼自含性 | ✅ 完全自含 — 所有 import 皆為 `src.*` 內部引用 |
| 與 ebook/ 共享程式碼 | ❌ 無 — 已完全解耦 |
| 與 Line-bot 共享程式碼 | ❌ 無 — 僅透過 HTTP Webhook 通訊 |
| 獨立 Dockerfile | ✅ 已具備 |
| 獨立 docker-compose | ✅ 已具備 |
| 獨立 .env | ✅ 已具備 |
| 獨立 requirements.txt | ✅ 已具備 |
| GitHub 獨立 Repo | ❌ 尚未建立 |

**結論**：程式碼層面已完全解耦，僅需處理 Git 歷史搬遷、GitHub Repo 建立、以及原 monorepo 的清理。

---

## 📋 執行計畫

### Phase 1: 建立獨立 GitHub Repository

1. 在 GitHub 上建立 `bbudaedu/new-book-notifier` 私有 Repo
2. 在本地初始化新 Repo：
   ```bash
   cd ~/projects
   cp -r buddhist-education-system/new-book-notifier ./new-book-notifier
   cd new-book-notifier
   git init
   git remote add origin git@github.com:bbudaedu/new-book-notifier.git
   ```
3. 建立適當的 `.gitignore`（Python + Docker，排除 `.env`、`__pycache__/`、`downloads/`、`logs/`）
4. 建立獨立的 `README.md`

### Phase 2: 補充獨立專案必要檔案

新增以下檔案讓專案完整：

| 檔案 | 用途 |
|------|------|
| `README.md` | 專案說明、啟動方式、環境變數列表 |
| `.gitignore` | Python/Docker 標準排除規則 |
| `.env.example` | 環境變數範本（不含真實密碼） |

### Phase 3: 首次推送

```bash
git add .
git commit -m "feat: initial commit - decouple from buddhist-education-system"
git push -u origin main
```

### Phase 4: 清理原 Monorepo

1. 刪除 `buddhist-education-system/new-book-notifier/` 目錄
2. 更新 `buddhist-education-system/README.md`，移除 new-book-notifier 相關段落
3. 在 `Line-bot-llm-mysql/docker-compose.yml` 中更新註解（指向新 Repo）
4. Commit 清理變更

### Phase 5: 部署切換

1. 在部署伺服器上 clone 新 Repo：
   ```bash
   cd ~/projects
   git clone git@github.com:bbudaedu/new-book-notifier.git
   ```
2. 將 `.env` 搬到新位置
3. 重新啟動容器：
   ```bash
   cd ~/projects/new-book-notifier
   docker compose up -d --build
   ```
4. 驗證服務正常（`curl http://localhost:8002/health`）

---

## ⚠️ 注意事項

> [!IMPORTANT]
> `.env` 包含 `GEMINI_API_KEY` 和 SMTP 密碼等敏感資訊，絕對不可推送到 Git。必須確認 `.gitignore` 正確排除 `.env`。

> [!WARNING]
> 搬遷後需更新部署伺服器的路徑。如果有 cron job 或監控指向舊路徑 `/home/budaedu/projects/buddhist-education-system/new-book-notifier/`，也必須一併更新。

---

## ✅ 驗證計畫

| 步驟 | 驗證方式 |
|------|---------|
| Repo 建立成功 | `gh repo view bbudaedu/new-book-notifier` |
| 程式碼完整 | 新 Repo `git log` 有初始 commit |
| `.env` 未推送 | GitHub 網頁確認無 `.env` 檔 |
| 容器正常啟動 | `docker compose up -d && curl localhost:8002/health` |
| 新書排程正常 | `curl -X POST localhost:8002/trigger` 回傳 accepted |
| 原 monorepo 清理 | `ls buddhist-education-system/` 無 `new-book-notifier/` |
