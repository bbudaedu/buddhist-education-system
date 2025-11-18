# 快速參考指南
# Quick Reference Guide

## 🚀 快速開始

### 啟動自動排程
```bash
cd Line-bot-llm-mysql
npm start
```

### 手動測試執行
```bash
cd ebook
test_daily_monitoring.bat
```

### 檢查系統設定
```bash
cd ebook
python check_monitoring_setup.py
```

## 📋 會執行的爬蟲

| 爬蟲 | 功能 | 輸出 |
|------|------|------|
| 📚 BookScraper | 新書監控 | 新書資訊 |
| 🎯 CarouselScraper | 輪播橫幅 | 橫幅內容 |
| 📅 BulletinScraper | 停課公告 | 取消課程 |
| 📰 run_news_scraper_correct.py | 新聞處理 | 最新公告 |
| 🎬 MediaProcessor | 多媒體處理 | 課程影音 |

## 🔔 通知機制

### LINE 通知 ✅
- **自動發送**：是
- **發送對象**：所有訂閱用戶
- **觸發方式**：監控完成後自動
- **訊息格式**：Flex Message (豐富卡片)

### Email 通知 📧
- **自動發送**：需設定
- **發送對象**：config.json 中的收件人
- **內容**：每日執行報告
- **設定位置**：`config.json` → `email.enabled = true`

## 📁 重要檔案位置

```
ebook/
├── run_daily_monitoring.py          # 主執行腳本
├── run_daily_monitoring_utf8.bat    # Windows 批次檔
├── test_daily_monitoring.bat        # 測試腳本
├── config.json                      # 設定檔
├── logs/                            # 執行日誌
│   └── daily_monitoring_*.log
└── generated_documents/             # 輸出檔案
    └── monitoring_summary_*.json    # 監控摘要

Line-bot-llm-mysql/
├── .env                             # 環境變數
└── src/services/
    ├── dailySchedulerService.ts     # 排程器
    └── notificationService.ts       # LINE 通知
```

## ⚙️ 環境變數設定

```env
# .env 檔案 (Line-bot-llm-mysql/.env)

# 排程器設定
SCHEDULER_ENABLED=true
SCHEDULER_DAILY_TIME=02:00
SCHEDULER_TIMEZONE=Asia/Taipei

# Python 路徑
EBOOK_PROCESSOR_PATH=../ebook/main_processor.py
PYTHON_EXECUTABLE=python
EBOOK_OUTPUT_PATH=../ebook/generated_documents
```

## 🔍 常用指令

### 查看排程器狀態
```bash
curl http://localhost:3000/admin/scheduler
```

### 手動觸發監控
```bash
curl -X POST http://localhost:3000/admin/scheduler/trigger
```

### 查看訂閱統計
```bash
curl http://localhost:3000/admin/stats/subscriptions
```

### 查看發送統計
```bash
curl http://localhost:3000/admin/stats/deliveries
```

### 查看系統狀態
```bash
curl http://localhost:3000/admin/status
```

## 🐛 快速除錯

### 問題：排程器沒有執行
```bash
# 1. 檢查 Node.js 是否運行
curl http://localhost:3000/health

# 2. 檢查排程器設定
curl http://localhost:3000/admin/scheduler

# 3. 查看 .env 檔案
cat Line-bot-llm-mysql/.env | grep SCHEDULER
```

### 問題：Python 腳本執行失敗
```bash
# 1. 手動執行測試
cd ebook
test_daily_monitoring.bat

# 2. 查看最新日誌
ls -lt logs/daily_monitoring_*.log | head -1

# 3. 檢查 Python 環境
python --version
python -c "import selenium; print('Selenium OK')"
```

### 問題：沒有收到 LINE 通知
```bash
# 1. 檢查是否有訂閱用戶
curl http://localhost:3000/admin/stats/subscriptions

# 2. 檢查輸出檔案
ls -lt ebook/generated_documents/monitoring_summary_*.json | head -1

# 3. 查看 Node.js 日誌
# 檢查控制台輸出

# 4. 手動觸發通知
curl -X POST http://localhost:3000/admin/notifications/trigger
```

### 問題：沒有收到 Email
```bash
# 1. 檢查 Email 設定
cd ebook
python -c "
from config_manager import ConfigManager
config = ConfigManager().get_config()
print('Email enabled:', config.get('email', {}).get('enabled', False))
"

# 2. 測試 SMTP 連線
python -c "
from email_sender import EmailSender
from config_manager import ConfigManager
import logging
logging.basicConfig(level=logging.INFO)
email_sender = EmailSender(ConfigManager().get_config())
# 檢查日誌輸出
"
```

## 📊 監控指標

### 健康指標
- ✅ 排程器運行中
- ✅ 每日執行成功
- ✅ 通知發送成功率 > 95%
- ✅ 無重複錯誤

### 檢查頻率
- **每日**：查看執行日誌
- **每週**：檢查訂閱用戶數
- **每月**：清理舊檔案

## 🔗 相關文件

- 📖 [完整說明](DAILY_MONITORING_README.md)
- 🔔 [通知流程](NOTIFICATION_FLOW.md)
- 🛠️ [技術規格](../Line-bot-llm-mysql/README.md)

## 💡 提示

1. **首次使用**：先執行 `test_daily_monitoring.bat` 確認一切正常
2. **定期維護**：每週檢查一次日誌，確保沒有錯誤
3. **備份資料**：定期備份 `generated_documents` 目錄
4. **更新 ChromeDriver**：Chrome 更新時同步更新 ChromeDriver
5. **監控磁碟空間**：定期清理舊的日誌和輸出檔案

## 📞 支援

遇到問題時的檢查順序：
1. 查看執行日誌
2. 檢查系統狀態 API
3. 手動執行測試
4. 查看相關文件
5. 檢查環境設定
