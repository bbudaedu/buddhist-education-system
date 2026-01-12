# Docker 部署指南 (Deployment Guide)

本指南說明如何使用 Docker 容器化部署 LINE Bot 電子書摘要系統，包含 Node.js 服務與 Python 排程檢查器。

## 🐳 架構概觀

我們使用單一 Docker Image 同時運行 Node.js 與 Python 環境，以簡化部署複雜度：

1.  **line-bot-web**: Node.js Web 伺服器 (Express)，處理 LINE Webhook。
2.  **line-bot-scheduler**: Node.js 排程服務，負責觸發 Python 脚本進行新書檢查。
3.  **mysql**: 資料庫服務 (若使用外部資料庫則可停用)。

Python 腳本 (`run_newbook_scheduler.py`) 執行於 `line-bot-scheduler` 容器內，並已預裝 headless Chrome 與 Selenium。

## 📋 前置需求

- [Docker](https://www.docker.com/products/docker-desktop/) (Desktop 或 Engine)
- [Docker Compose](https://docs.docker.com/compose/install/)

## ⚙️ 配置設定

### 1. 環境變數 (.env)

確保 `Line-bot-llm-mysql/.env` 檔案存在並包含正確設定：

```env
# Database
# DB_HOST=mysql         # 如果使用 Docker 內建資料庫
DB_HOST=124.219.37.161  # 如果使用外部現有資料庫
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=line_bot_db
DB_ROOT_PASSWORD=your_root_password

# Line Bot
CHANNEL_ACCESS_TOKEN=your_token
CHANNEL_SECRET=your_secret

# Scheduler
SCHEDULER_ENABLED=true
NEWBOOK_SCHEDULER_ENABLED=true
NEWBOOK_CRON_EXPRESSION="0 9 * * *"  # 每天早上 9:00
```

### 2. Python 配置 (ebook/config.json)

確保 `ebook/config.json` 存在。
**注意**：在 Docker 環境中，以下路徑會自動由環境變數覆寫，您**不需要**手動修改 JSON 檔案中的這些路徑：

- `chromedriver_path` -> `/usr/bin/chromedriver`
- `download_dir` -> `/app/ebook/downloads`

## 🏭 正式環境建議 (Production Recommendations)

針對本專案的特性，我們**強烈建議**在正式環境繼續使用 **Docker** 進行部署，而非直接運作於 LXC 或實體機 OS。

### 為什麼選擇 Docker？

1.  **依賴版本鎖定 (關鍵)**：
    - 本專案依賴 **headless Chrome** 與 **Selenium**。
    - Chrome 與 ChromeDriver 的版本必須嚴格匹配（例如 Chrome 114 必須配 ChromeDriver 114）。
    - Docker Image 將這兩者鎖定在同一版本。若使用 LXC 或直接安裝於 Ubuntu，系統更新 (`apt upgrade`) 可能會單獨升級 Chrome，導致爬蟲功能失效。

2.  **環境一致性**：
    - 開發環境 (Windows/Docker) 與正式環境完全一致，減少「在我電腦上可以跑」的問題。

3.  **Host OS 選擇**：
    - 建議 Host OS 使用穩定的 Linux 發行版 (如 **Ubuntu 22.04 LTS** 或 **Debian 12**)。
    - 只需安裝 Docker Engine，保持 Host 純淨。

## 🚀 部署步驟

### 1. 建構並啟動容器

**注意：** 預設 `docker-compose.yml` 已設定為連線外部資料庫 (124.219.37.161)，並停用了 Docker 內部的 MySQL 容器以節省資源。

在專案根目錄 (`D:\AI Studio\newinfo\Line-bot-llm-mysql`) 執行：

```bash
# 建構 Docker Image (需時較長，因為要安裝 Python 和 Chrome)
docker-compose build

# 背景啟動所有服務
docker-compose up -d
```

### 2. 查看日誌

確認服務正常啟動：

```bash
# 查看排程器日誌 (確認 Python 環境與排程載入)
docker-compose logs -f line-bot-scheduler

# 查看 Web 服務日誌
docker-compose logs -f line-bot-web
```

### 3. 手動測試新書檢查

您可以進入容器手動觸發檢查，驗證環境是否正常：

```bash
docker exec -it line-bot-scheduler python3 /app/ebook/run_newbook_scheduler.py --check-only --verbose
```

若看到 `SUCCESS` 與 JSON 輸出，代表 Python、Selenium 與 Chrome 運作正常。

## 📁 檔案結構對應

| 主機路徑 (Host) | 容器路徑 (Container) | 說明 |
| :--- | :--- | :--- |
| `../ebook` | `/app/ebook` | 掛載 Python 程式碼與配置 |
| `../ebook/downloads` | `/app/ebook/downloads` | 下載的 PDF 與產生的摘要 |

**注意**：由於掛載了 `ebook` 目錄，容器內產生的 `downloads` 檔案會直接出現在您的主機 `ebook/downloads` 資料夾中。

## 🛠️ 常見問題排除

### 1. ChromeDriver 錯誤
若遇到 `Message: unknown error: Chrome failed to start`：
- 確認 Dockerfile 中已正確安裝 `chromium` 和 `chromium-chromedriver`。
- 確認 Python 腳本使用 `--headless` 和 `--no-sandbox` 參數 (程式碼中已預設啟用)。

### 2. 權限問題
若 Python 無法寫入 `config.json` 或 `downloads`：
- 確認 `docker-compose.yml` 中的 volume 掛載**沒有** `:ro` (唯讀) 標籤。
- 我們已設定 `DOWNLOAD_DIR=/app/ebook/downloads`，確保寫入路徑正確。
