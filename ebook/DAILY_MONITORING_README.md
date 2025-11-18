# 每日監控系統說明
# Daily Monitoring System Documentation

## 📋 概述 Overview

每日監控系統會自動執行所有網站爬蟲和處理器，包括：

1. **新書爬蟲** (Book Scraper) - 監控新書發布
2. **輪播橫幅爬蟲** (Carousel Scraper) - 監控首頁輪播內容
3. **停課公告爬蟲** (Bulletin Scraper) - 監控課程取消通知
4. **新聞爬蟲** (run_news_scraper_correct.py) - 處理最新公告
5. **多媒體處理器** (Media Processor) - 處理最新課程影音

## 🚀 執行方式

### 方式 1: 透過 Node.js 排程器（自動執行）

在 `.env` 檔案中設定：

```env
SCHEDULER_ENABLED=true
SCHEDULER_DAILY_TIME=02:00
```

然後執行：

```bash
cd Line-bot-llm-mysql
npm start
```

排程器會在每天 02:00 自動執行所有監控任務。

### 方式 2: 手動測試執行

在 `ebook` 目錄下執行：

```bash
# Windows
test_daily_monitoring.bat

# 或直接執行
run_daily_monitoring_utf8.bat manual
```

## 📁 輸出檔案

執行完成後會產生以下檔案：

### 1. 監控摘要 (JSON)
- 位置: `generated_documents/monitoring_summary_YYYYMMDD_HHMMSS.json`
- 內容: 執行統計、處理結果、執行時間
- **用途**: Node.js 會監控此檔案並觸發 LINE 通知

### 2. 執行日誌 (LOG)
- 位置: `logs/daily_monitoring_YYYYMMDD_HHMMSS.log`
- 內容: 詳細執行過程、錯誤訊息

### 3. 爬取資料 (Excel/JSON)
- 位置: `generated_documents/`
- 內容: 各種爬蟲的輸出資料

## 📢 通知機制

### LINE 通知 ✅
- **自動發送**：監控完成後自動發送
- **發送對象**：所有訂閱用戶（透過 LINE bot 訂閱）
- **發送方式**：Node.js NotificationService
- **內容**：新書資訊、課程更新、重要公告

### Email 通知 📧
- **需要設定**：在 `config.json` 中啟用
- **設定方式**：
  ```json
  {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "sender_email": "your-email@gmail.com",
      "sender_password": "your-app-password",
      "recipient_emails": ["recipient@example.com"]
    }
  }
  ```
- **內容**：每日監控執行報告

## 🔍 監控流程

```
開始執行
  ↓
初始化系統
  ↓
執行監控週期
  ├─ 輪播橫幅爬蟲 (CarouselScraper)
  ├─ 停課公告爬蟲 (BulletinScraper)
  ├─ 新聞處理器 (NewsProcessor)
  ├─ 多媒體處理器 (MediaProcessor)
  └─ 新書爬蟲 (BookScraper)
  ↓
資料同步
  ├─ 寫入 Excel
  └─ 寫入 MySQL
  ↓
發送通知
  ├─ LINE 通知 (透過 Node.js NotificationService)
  └─ Email 通知 (如果在 config.json 中啟用)
  ↓
完成

```

## ⚙️ 設定檔

### Node.js 環境變數 (.env)

```env
# 排程器設定
SCHEDULER_ENABLED=true
SCHEDULER_DAILY_TIME=02:00
SCHEDULER_TIMEZONE=Asia/Taipei
SCHEDULER_MAX_RETRIES=3

# Python 執行路徑
EBOOK_PROCESSOR_PATH=../ebook/main_processor.py
PYTHON_EXECUTABLE=python
EBOOK_OUTPUT_PATH=../ebook/generated_documents
```

### Python 設定檔 (config.json)

監控系統會自動讀取 `config.json` 中的設定，包括：
- ChromeDriver 路徑
- 下載目錄
- 資料庫連線
- 通知設定

## 🐛 除錯

### 檢查執行狀態

1. 查看最新的日誌檔案：
   ```
   logs/daily_monitoring_YYYYMMDD_HHMMSS.log
   ```

2. 查看監控摘要：
   ```
   generated_documents/monitoring_summary_YYYYMMDD_HHMMSS.json
   ```

3. 檢查 Node.js 排程器狀態：
   ```bash
   curl http://localhost:3000/admin/scheduler
   ```

### 常見問題

**Q: 排程器沒有執行？**
- 檢查 `SCHEDULER_ENABLED=true`
- 檢查 `SCHEDULER_DAILY_TIME` 格式是否正確 (HH:MM)
- 查看 Node.js 控制台輸出

**Q: Python 腳本執行失敗？**
- 檢查 `PYTHON_EXECUTABLE` 路徑是否正確
- 檢查 `EBOOK_PROCESSOR_PATH` 路徑是否正確
- 查看 Python 日誌檔案

**Q: 沒有產生輸出檔案？**
- 檢查 `generated_documents` 目錄權限
- 查看日誌檔案中的錯誤訊息
- 確認 ChromeDriver 版本與 Chrome 瀏覽器版本相容

## 📊 監控統計

執行完成後，可以透過以下方式查看統計：

### 1. 查看 JSON 摘要
```bash
cat generated_documents/monitoring_summary_*.json
```

### 2. 透過 API 查詢
```bash
curl http://localhost:3000/admin/status
curl http://localhost:3000/admin/performance
```

## 🔄 與舊系統的差異

### 舊系統 (notification_processor.py)
- ❌ 只執行通知處理
- ❌ 不執行任何爬蟲
- ❌ 只有測試範例

### 新系統 (run_daily_monitoring.py)
- ✅ 執行所有爬蟲和處理器
- ✅ 完整的監控週期
- ✅ 資料同步到 Excel 和 MySQL
- ✅ 自動發送通知
- ✅ 詳細的執行日誌和統計

## 📝 維護建議

1. **定期檢查日誌**：每週檢查一次執行日誌，確保沒有錯誤
2. **監控磁碟空間**：定期清理舊的日誌和輸出檔案
3. **更新 ChromeDriver**：當 Chrome 瀏覽器更新時，同步更新 ChromeDriver
4. **備份資料**：定期備份 `generated_documents` 目錄

## 🆘 支援

如有問題，請檢查：
1. 執行日誌：`logs/daily_monitoring_*.log`
2. 錯誤摘要：`generated_documents/monitoring_error_*.json`
3. Node.js 控制台輸出
