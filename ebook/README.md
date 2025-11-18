# 新書摘要與郵件發送系統

Buddhist Education New Book Summary and Email Distribution System

## 系統概述

本系統為佛教教育網站的新書監控與摘要生成系統，能夠自動化處理以下任務：

1. **網頁監控**: 使用 Selenium 監控 https://www.budaedu.org 網站的新書發布
2. **PDF 下載**: 自動下載新書的 PDF 檔案
3. **AI 摘要**: 使用 Google Gemini Pro 2.5 生成 300 字繁體中文摘要
4. **文件生成**: 建立 Word 和 Excel 格式的摘要文件
5. **郵件發送**: 自動發送摘要文件給指定收件人

## 系統需求

### 軟體需求

- **作業系統**: Windows 10/11
- **Python**: 3.8 或更高版本
- **Chrome 瀏覽器**: 最新版本
- **網路連線**: 穩定的網際網路連線

### 硬體需求

- **記憶體**: 至少 4GB RAM (建議 8GB)
- **磁碟空間**: 至少 500MB 可用空間
- **處理器**: 支援多執行緒的現代處理器

## 安裝步驟

### 1. 安裝 Python 依賴套件

首先確保已安裝 Python 3.8+，然後安裝所需的套件：

```bash
pip install -r requirements.txt
```

如果 `requirements.txt` 不存在，請手動安裝以下套件：

```bash
pip install selenium>=4.0.0
pip install google-genai>=1.0.0
pip install pypdf>=3.0.0
pip install python-docx>=0.8.11
pip install openpyxl>=3.0.0
pip install urllib3>=1.26.0
```

### 2. 下載 ChromeDriver

1. 檢查您的 Chrome 瀏覽器版本：
   - 開啟 Chrome
   - 點選右上角三點選單 → 說明 → 關於 Google Chrome
   - 記下版本號碼

2. 下載對應版本的 ChromeDriver：
   - 訪問 https://chromedriver.chromium.org/
   - 下載與您的 Chrome 版本相符的 ChromeDriver
   - 解壓縮到專案目錄的 `chromedriver-win64` 資料夾中

### 3. 取得 Gemini API Key

1. 訪問 Google AI Studio: https://aistudio.google.com/
2. 登入您的 Google 帳戶
3. 建立新的 API Key
4. 複製 API Key 備用

### 4. 設定 SMTP 郵件伺服器

準備以下郵件伺服器資訊：

- **Gmail 範例**:
  - SMTP 伺服器: `smtp.gmail.com`
  - 連接埠: `587`
  - 使用者名稱: 您的 Gmail 地址
  - 密碼: 應用程式專用密碼 (不是您的 Gmail 密碼)

**重要**: 如果使用 Gmail，需要：
1. 啟用兩步驟驗證
2. 產生應用程式專用密碼
3. 使用應用程式專用密碼而非一般密碼

## 使用方法

### 1. 啟動應用程式

```bash
python newbook_summary_app.py
```

### 2. 設定系統參數

在應用程式介面中填入以下資訊：

#### 基本設定
- **Gemini API Key**: 您的 Google Gemini API 金鑰
- **ChromeDriver 路徑**: ChromeDriver 執行檔的完整路徑
- **目標網站 URL**: `https://www.budaedu.org`
- **基準書籍標題**: 用於識別新書的基準書籍標題 (例如: `CH754-02`)
- **下載目錄**: PDF 檔案下載位置

#### 郵件設定
- **SMTP 伺服器**: 郵件伺服器地址
- **連接埠**: SMTP 連接埠 (通常是 587)
- **SMTP 使用者名稱**: 您的郵件帳戶
- **SMTP 密碼**: 郵件帳戶密碼或應用程式專用密碼
- **收件人**: 以逗號分隔的收件人清單

### 3. 檢查設定

點選「檢查設定」按鈕驗證所有設定是否正確。

### 4. 開始處理

點選「開始處理」按鈕啟動自動化流程。

### 5. 監控進度

- 查看即時日誌了解處理進度
- 觀察狀態列顯示的當前狀態
- 如需中斷，點選「停止處理」按鈕

## 設定檔案

系統會自動建立 `config.json` 檔案儲存您的設定：

```json
{
  "gemini_api_key": "您的API金鑰",
  "chromedriver_path": "chromedriver-win64\\chromedriver.exe",
  "target_url": "https://www.budaedu.org",
  "baseline_book_title": "CH754-02",
  "download_dir": "downloads",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your-email@gmail.com",
  "smtp_password": "your-app-password",
  "email_recipients": "recipient1@example.com,recipient2@example.com"
}
```

## 輸出檔案

系統會產生以下檔案：

### 文件檔案
- **Word 文件**: `新書簡介_YYYY-MM-DD.docx` - 包含書籍摘要
- **Excel 文件**: `新書詳細資料_YYYY-MM-DD.xlsx` - 包含詳細資料表

### 日誌檔案
- **執行日誌**: `log_YYYY-MM-DD_HH-MM-SS.txt` - 詳細執行記錄

### 快取檔案
- **進度快取**: `.newbook_summary_email_progress_cache.json` - 處理進度 (自動管理)

## 故障排除

### 常見問題

#### 1. ChromeDriver 錯誤
**錯誤**: `ChromeDriver executable not found`
**解決方法**: 
- 確認 ChromeDriver 路徑正確
- 確認 ChromeDriver 版本與 Chrome 瀏覽器版本相符
- 檢查檔案權限

#### 2. Gemini API 錯誤
**錯誤**: `API key invalid` 或 `Rate limit exceeded`
**解決方法**:
- 檢查 API Key 是否正確
- 確認 API Key 有足夠的配額
- 等待一段時間後重試

#### 3. 郵件發送失敗
**錯誤**: `SMTP authentication failed`
**解決方法**:
- 檢查郵件帳戶和密碼
- 如使用 Gmail，確認已啟用兩步驟驗證並使用應用程式專用密碼
- 檢查 SMTP 伺服器設定

#### 4. 網路連線問題
**錯誤**: `Connection timeout` 或 `Network error`
**解決方法**:
- 檢查網路連線
- 確認防火牆設定
- 嘗試使用 VPN (如果網站被封鎖)

### 日誌分析

查看日誌檔案了解詳細錯誤資訊：

```
2024-01-01 10:00:00 [INFO] 開始新書摘要處理流程
2024-01-01 10:00:05 [INFO] 找到 3 本新書
2024-01-01 10:00:10 [INFO] 處理書籍 1/3...
2024-01-01 10:00:15 [ERROR] PDF 下載失敗: 網路連線超時
```

## 進階設定

### 自訂處理邏輯

系統支援兩種摘要生成模式：

1. **PDF 提取模式** (檔案 ≤ 30MB): 直接分析 PDF 內容
2. **Google 搜尋模式** (檔案 > 30MB): 使用 Google 搜尋取得書籍資訊

### 批次處理

系統支援中斷恢復功能：
- 處理過程中可隨時中斷
- 重新啟動時會自動跳過已處理的書籍
- 進度資訊儲存在快取檔案中

### 錯誤處理

系統具備強健的錯誤處理機制：
- 單一書籍處理失敗不會影響整體流程
- 網路錯誤會自動重試
- API 呼叫失敗會使用指數退避重試

## 系統架構

```
新書摘要系統
├── GUI 層 (Tkinter)
│   ├── 設定面板
│   ├── 控制按鈕
│   └── 日誌顯示
├── 應用程式控制器
│   └── 任務協調器 (多執行緒 + 進度管理)
├── 核心模組
│   ├── 網頁爬蟲 (Selenium)
│   ├── AI 處理器 (Gemini API)
│   ├── 文件生成器 (Word/Excel)
│   └── 郵件發送器 (SMTP)
└── 工具服務
    ├── 日誌處理器
    ├── 設定管理器
    ├── 進度快取
    └── 檔案系統操作
```

## 授權條款

本專案僅供內部使用，請勿用於商業用途。

## 技術支援

如遇到問題，請：

1. 檢查日誌檔案了解詳細錯誤資訊
2. 參考故障排除章節
3. 確認所有依賴套件已正確安裝
4. 驗證網路連線和 API 配額

## 更新記錄

### v1.0.0 (2024-01-01)
- 初始版本發布
- 支援新書監控和摘要生成
- 整合 Gemini Pro 2.5 API
- 支援 Word 和 Excel 文件生成
- 實作郵件自動發送功能