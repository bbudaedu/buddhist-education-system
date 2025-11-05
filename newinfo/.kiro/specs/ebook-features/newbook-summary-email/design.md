# Design Document

## Overview

本系統為「新書摘要與郵件發送系統」，採用模組化設計，整合 Selenium WebDriver、Google Gemini Pro 2.5 API、PDF 處理、Word 文件生成和 SMTP 郵件發送功能。系統透過 Tkinter 提供圖形化使用者介面，支援即時日誌顯示、進度儲存、任務中斷等功能。

系統的核心流程為：

1. 使用 Selenium 訪問佛教教育網站並識別新書
2. 下載新書 PDF 檔案
3. 根據 PDF 大小選擇處理策略（直接提取或 Google 搜尋）
4. 使用 Gemini Pro 2.5 生成 300 字摘要
5. 將摘要整理到 Word 文件
6. 透過 SMTP 發送郵件給指定收件人

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     GUI Layer (Tkinter)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Config   │ │ Control  │ │ Log      │ │ Status   │       │
│  │ Panel    │ │ Buttons  │ │ Display  │ │ Display  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Controller                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Task Orchestrator (Threading + Progress Management) │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Web        │   │   AI         │   │   Document   │
│   Scraper    │   │   Processor  │   │   Generator  │
│              │   │              │   │              │
│ - Selenium   │   │ - Gemini API │   │ - Word Gen   │
│ - Download   │   │ - PDF Parse  │   │ - Email Send │
└──────────────┘   └──────────────┘   └──────────────┘

        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────────────────────────────────────────────┐
│              Utility Services                         │
│  - Logging Handler                                    │
│  - Config Manager (JSON)                              │
│  - Progress Cache (JSON)                              │
│  - File System Operations                             │
└──────────────────────────────────────────────────────┘
```

### Technology Stack

- **GUI Framework**: Tkinter (內建於 Python)
- **Web Automation**: Selenium WebDriver with Chrome
- **AI Service**: Google Gemini Pro 2.5 API (google-genai SDK)
- **PDF Processing**: pypdf library
- **Document Generation**: python-docx library
- **Email**: smtplib (內建於 Python)
- **Concurrency**: threading module
- **Data Persistence**: JSON files

## Components and Interfaces

### 1. GUI Layer (NewBookSummaryApp)

**Responsibility**: 提供使用者介面，處理使用者輸入，顯示執行狀態

**Key Methods**:

- `__init__(master)`: 初始化 UI 元件
- `create_widgets()`: 建立所有 UI 元件
- `setup_logging()`: 設定日誌處理器
- `load_config()`: 從 config.json 載入設定
- `save_config()`: 儲存設定到 config.json
- `start_processing()`: 啟動主要處理流程
- `stop_processing()`: 中斷執行中的任務
- `check_configuration()`: 檢查系統設定
- `disable_buttons()` / `enable_buttons()`: 控制按鈕狀態

**UI Components**:

```python
# Configuration Panel
- Gemini API Key (Entry, password masked)
- ChromeDriver Path (Entry + Browse Button)
- Target Website URL (Entry)
- Baseline Book Title (Entry)
- Download Directory (Entry + Browse Button)
- Email SMTP Settings (Server, Port, Username, Password)
- Email Recipients (Entry, comma-separated)

# Control Panel
- Start Processing (Button)
- Stop Processing (Button)
- Check Configuration (Button)

# Status Panel
- Log Display (ScrolledText, read-only)
- Progress Information (Label)
```

### 2. Web Scraper Module (BookScraper)

**Responsibility**: 使用 Selenium 訪問網站、識別新書、下載 PDF

**Key Methods**:

- `__init__(chromedriver_path, download_dir, logger)`: 初始化 WebDriver
- `setup_driver()`: 設定 Chrome options 和下載偏好
- `navigate_to_website(url)`: 訪問目標網站
- `wait_for_page_load(timeout=15)`: 等待頁面載入
- `find_new_books(baseline_title)`: 識別基準書籍之前的新書
- `extract_book_info(card_element)`: 從卡片元素提取書籍資訊
- `download_pdf(book_card)`: 點擊下載按鈕並取得 PDF 連結
- `close_modal()`: 關閉下載彈窗
- `cleanup()`: 關閉 WebDriver

**Data Structures**:

```python
BookInfo = {
    'title': str,           # 書籍標題
    'pdf_url': str,         # PDF 下載連結
    'filename': str,        # PDF 檔案名稱
    'download_path': str    # 本地儲存路徑
}
```

### 3. AI Processor Module (GeminiProcessor)

**Responsibility**: 使用 Gemini API 生成書籍摘要，支援 PDF 提取和 Google 搜尋兩種模式

**Key Methods**:

- `__init__(api_key, logger)`: 初始化 Gemini client
- `check_pdf_size(pdf_path)`: 檢查 PDF 檔案大小（單位：bytes）
- `extract_pdf_text(pdf_path)`: 從 PDF 提取文字內容
- `generate_summary_from_pdf(pdf_path, book_title)`: 從 PDF 生成摘要
- `generate_summary_from_search(book_title)`: 使用 Google 搜尋生成摘要
- `process_book(book_info)`: 主要處理邏輯，根據檔案大小選擇策略
- `retry_on_failure(func, max_retries=3, delay=10)`: 重試機制

**API Configuration** (基於 Context7 最新範例):

```python
from google import genai
from google.genai import types

# Initialize client
client = genai.Client(api_key=api_key)

# For PDF-based summary (file size <= 30MB)
response = client.models.generate_content(
    model='gemini-2.5-pro',
    contents=[
        types.Part.from_bytes(
            data=pdf_bytes,
            mime_type='application/pdf'
        ),
        '請用繁體中文為這本書生成 300 字的摘要，包含主要內容和重點。'
    ],
    config=types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=40,
    )
)

# For Google Search-based summary (file size > 30MB)
response = client.models.generate_content(
    model='gemini-2.5-pro',
    contents=f'請使用 Google 搜尋功能查找「{book_title}」這本書的資訊，並用繁體中文生成 300 字的摘要。',
    config=types.GenerateContentConfig(
        tools=[{"google_search": {}}],
        temperature=0.7,
    )
)
```

**Processing Logic**:

```python
def process_book(self, book_info):
    pdf_path = book_info['download_path']
    file_size = self.check_pdf_size(pdf_path)

    if file_size > 30 * 1024 * 1024:  # 30MB
        self.logger.info(f"PDF 大於 30MB，使用 Google 搜尋模式")
        summary = self.generate_summary_from_search(book_info['title'])
    else:
        self.logger.info(f"PDF 小於 30MB，使用 PDF 提取模式")
        summary = self.generate_summary_from_pdf(pdf_path, book_info['title'])

    return summary
```

### 4. Document Generator Module (DocumentGenerator)

**Responsibility**: 生成 Word 文件和 Excel 文件，整理書籍摘要和詳細資料

**Key Methods**:

- `__init__(logger)`: 初始化文件生成器
- `create_word_document()`: 建立新的 Word 文件
- `create_excel_document()`: 建立新的 Excel 文件
- `add_book_to_word(title, summary)`: 新增書籍條目到 Word
- `add_book_to_excel(book_data)`: 新增書籍詳細資料到 Excel
- `format_title(paragraph)`: 格式化標題樣式
- `save_documents(output_dir)`: 儲存所有文件

**Word Document Structure**:

```
新書簡介 - YYYY年MM月DD日
================================

【書名1】
摘要內容...

【書名2】
摘要內容...
```

**Excel Document Structure**:

```
| 序號 | 書名 | PDF檔名 | 檔案大小(MB) | 處理方式 | 摘要 | 下載連結 | 處理時間 |
|------|------|---------|--------------|----------|------|----------|----------|
| 1    | ... | ...     | ...          | ...      | ...  | ...      | ...      |
```

**Implementation** (使用 python-docx 和 openpyxl):

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

def create_word_document(self):
    doc = Document()
    # 標題
    title = doc.add_heading('新書簡介', level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # 日期
    date_para = doc.add_paragraph(datetime.now().strftime('%Y年%m月%d日'))
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return doc

def add_book_to_word(self, doc, title, summary):
    # 書名（粗體、14pt）
    title_para = doc.add_paragraph()
    title_run = title_para.add_run(f'【{title}】')
    title_run.bold = True
    title_run.font.size = Pt(14)
    # 摘要
    doc.add_paragraph(summary)
    # 空行
    doc.add_paragraph()

def create_excel_document(self):
    wb = Workbook()
    ws = wb.active
    ws.title = "新書詳細資料"

    # 設定標題列
    headers = ['序號', '書名', 'PDF檔名', '檔案大小(MB)',
               '處理方式', '摘要', '下載連結', '處理時間']
    ws.append(headers)

    # 格式化標題列
    for cell in ws[1]:
        cell.font = Font(bold=True, size=12)
        cell.fill = PatternFill(start_color='CCE5FF', end_color='CCE5FF', fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center')

    return wb

def add_book_to_excel(self, ws, index, book_data):
    row = [
        index,
        book_data['title'],
        book_data['filename'],
        round(book_data['file_size_bytes'] / (1024 * 1024), 2),
        'PDF提取' if book_data['processing_method'] == 'pdf_extract' else 'Google搜尋',
        book_data['summary'],
        book_data['pdf_url'],
        book_data['timestamp']
    ]
    ws.append(row)

    # 設定欄寬
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 50
    ws.column_dimensions['G'].width = 40
    ws.column_dimensions['H'].width = 20
```

### 5. Email Sender Module (EmailSender)

**Responsibility**: 透過 SMTP 發送郵件，支援多個附件

**Key Methods**:

- `__init__(smtp_server, smtp_port, username, password, logger)`: 初始化 SMTP 設定
- `send_email(recipients, subject, body, attachment_paths)`: 發送郵件（支援多個附件）
- `create_message(recipients, subject, body, attachment_paths)`: 建立郵件訊息
- `attach_file(message, file_path)`: 附加單個檔案

**Email Configuration**:

```python
SMTP_SERVER = 'smtp.gmail.com'  # 或其他 SMTP 伺服器
SMTP_PORT = 587
USE_TLS = True
```

**Implementation**:

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email(self, recipients, subject, body, attachment_paths):
    msg = MIMEMultipart()
    msg['From'] = self.username
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject

    # 郵件內容
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 附加多個檔案（Word 和 Excel）
    for attachment_path in attachment_paths:
        with open(attachment_path, 'rb') as f:
            # 根據副檔名決定 MIME subtype
            ext = os.path.splitext(attachment_path)[1].lower()
            if ext == '.docx':
                subtype = 'vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif ext == '.xlsx':
                subtype = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                subtype = 'octet-stream'

            attachment = MIMEApplication(f.read(), _subtype=subtype)
            attachment.add_header('Content-Disposition', 'attachment',
                                filename=os.path.basename(attachment_path))
            msg.attach(attachment)

    # 發送郵件
    with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
        server.starttls()
        server.login(self.username, self.password)
        server.send_message(msg)
```

### 6. Task Orchestrator (MainProcessor)

**Responsibility**: 協調各模組執行完整流程，管理進度和中斷

**Key Methods**:

- `__init__(config, logger)`: 初始化所有模組
- `run()`: 執行主要流程
- `load_progress()`: 載入進度快取
- `save_progress(processed_books)`: 儲存進度
- `should_stop()`: 檢查是否需要中斷
- `cleanup()`: 清理資源

**Main Processing Flow**:

```python
def run(self):
    try:
        # 1. 載入進度
        processed_books = self.load_progress()

        # 2. 網頁爬取
        scraper = BookScraper(...)
        new_books = scraper.find_new_books(baseline_title)

        # 3. 處理每本書
        summaries = []
        for book in new_books:
            if self.should_stop():
                break

            if book['title'] in processed_books:
                continue

            # 下載 PDF
            scraper.download_pdf(book)

            # 生成摘要
            ai_processor = GeminiProcessor(...)
            summary = ai_processor.process_book(book)

            summaries.append({'title': book['title'], 'summary': summary})
            processed_books.add(book['title'])
            self.save_progress(processed_books)

        # 4. 生成 Word 和 Excel 文件
        doc_gen = DocumentGenerator(...)
        word_path, excel_path = doc_gen.create_documents(summaries)

        # 5. 發送郵件（附加兩個檔案）
        email_sender = EmailSender(...)
        email_sender.send_email(recipients, subject, body, [word_path, excel_path])

    finally:
        self.cleanup()
```

## Data Models

### Configuration Model

```python
{
    "gemini_api_key": str,
    "chromedriver_path": str,
    "target_url": str,
    "baseline_book_title": str,
    "download_dir": str,
    "smtp_server": str,
    "smtp_port": int,
    "smtp_username": str,
    "smtp_password": str,
    "email_recipients": [str],
    "last_run_date": str  # ISO format
}
```

### Progress Cache Model

```python
{
    "session_id": str,  # UUID
    "start_time": str,  # ISO format
    "processed_books": [
        {
            "title": str,
            "pdf_filename": str,
            "processing_method": str,  # "pdf_extract" or "google_search"
            "summary_generated": bool,
            "timestamp": str
        }
    ]
}
```

### Book Information Model

```python
{
    "title": str,
    "pdf_url": str,
    "filename": str,
    "download_path": str,
    "file_size_bytes": int,
    "processing_method": str,  # "pdf_extract" or "google_search"
    "summary": str
}
```

## Error Handling

### Error Categories and Strategies

1. **Network Errors** (Selenium, PDF Download, API Calls)

   - Strategy: Log error, retry up to 3 times with exponential backoff
   - Fallback: Skip current book, continue with next

2. **API Errors** (Gemini API)

   - Rate Limit: Wait and retry with exponential backoff
   - Invalid Response: Log error, try alternative method if available
   - Timeout: Increase timeout, retry once

3. **File System Errors** (PDF Read/Write, Config)

   - Permission Denied: Log error, notify user
   - Disk Full: Stop processing, notify user
   - File Not Found: Log warning, skip item

4. **Email Errors** (SMTP)
   - Authentication Failed: Stop and notify user immediately
   - Connection Error: Retry up to 3 times
   - Attachment Too Large: Log error, notify user

### Error Handling Implementation

```python
class ErrorHandler:
    def __init__(self, logger):
        self.logger = logger

    def handle_with_retry(self, func, max_retries=3, delay=10):
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                self.logger.error(f"Attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay * (2 ** attempt))
                else:
                    raise

    def handle_gracefully(self, func, default_value=None):
        try:
            return func()
        except Exception as e:
            self.logger.error(f"Error occurred: {e}", exc_info=True)
            return default_value
```

## Testing Strategy

### Unit Testing

**Test Coverage Areas**:

1. Configuration loading and validation
2. PDF size checking logic
3. Text extraction from PDF
4. Word document generation
5. Excel document generation
6. Email message creation with multiple attachments
7. Progress cache save/load

**Example Test Cases**:

```python
# Test PDF size checking
def test_pdf_size_check():
    processor = GeminiProcessor(api_key, logger)
    # Test with small file
    assert processor.check_pdf_size('small.pdf') < 30 * 1024 * 1024
    # Test with large file
    assert processor.check_pdf_size('large.pdf') > 30 * 1024 * 1024

# Test configuration validation
def test_config_validation():
    config = ConfigManager()
    assert config.validate_api_key('valid_key') == True
    assert config.validate_api_key('') == False
```

### Integration Testing

**Test Scenarios**:

1. End-to-end flow with mock data
2. Selenium interaction with test website
3. Gemini API integration with sample PDFs
4. Email sending to test accounts
5. Progress save/resume functionality

### Manual Testing Checklist

- [ ] UI 所有按鈕可正常點擊
- [ ] 日誌訊息正確顯示
- [ ] 設定檢查功能正確驗證所有項目
- [ ] 中斷功能可正常停止執行
- [ ] 進度儲存和恢復功能正常
- [ ] 小於 30MB 的 PDF 使用提取模式
- [ ] 大於 30MB 的 PDF 使用搜尋模式
- [ ] Word 文件格式正確
- [ ] 郵件成功發送到指定收件人

## Performance Considerations

### Optimization Strategies

1. **Parallel Processing**

   - 考慮使用 ThreadPoolExecutor 並行處理多本書
   - 限制並行數量避免 API rate limit

2. **Caching**

   - 快取已處理的書籍資訊
   - 避免重複下載和處理

3. **Resource Management**

   - 及時關閉 WebDriver 釋放資源
   - 處理完 PDF 後刪除臨時檔案（可選）

4. **API Efficiency**
   - 使用適當的 timeout 設定
   - 實作 exponential backoff 避免過度重試

### Expected Performance

- 單本書處理時間：30-60 秒（取決於 PDF 大小和 API 回應時間）
- 10 本新書總處理時間：約 5-10 分鐘
- 記憶體使用：< 500MB（不含 Chrome）

## Security Considerations

1. **API Key Protection**

   - API Key 在 UI 中以密碼形式顯示
   - 儲存在 config.json 時使用明文（建議未來加密）

2. **Email Credentials**

   - SMTP 密碼在 UI 中以密碼形式顯示
   - 建議使用應用程式專用密碼而非主密碼

3. **File System Access**

   - 驗證所有檔案路徑避免路徑遍歷攻擊
   - 限制下載目錄在指定位置

4. **Network Security**
   - 使用 HTTPS 進行 API 呼叫
   - SMTP 使用 TLS 加密連線

## Deployment Notes

### Dependencies

```
selenium>=4.0.0
google-genai>=1.0.0
pypdf>=3.0.0
python-docx>=0.8.11
openpyxl>=3.0.0
urllib3>=1.26.0
```

### System Requirements

- Python 3.8+
- Chrome Browser (與 ChromeDriver 版本相容)
- 網路連線
- 至少 500MB 可用磁碟空間

### Configuration Steps

1. 安裝 Python 依賴套件
2. 下載對應版本的 ChromeDriver
3. 取得 Gemini API Key
4. 設定 SMTP 郵件伺服器資訊
5. 執行程式並填寫設定

## Future Enhancements

1. **多語言支援**: 支援英文等其他語言介面
2. **排程功能**: 定期自動執行檢查新書
3. **通知系統**: 完成後發送桌面通知
4. **進階過濾**: 支援按分類、作者等條件篩選新書
5. **摘要自訂**: 允許使用者自訂摘要長度和風格
6. **批次匯出**: 支援匯出為 PDF、HTML 等格式
7. **資料庫整合**: 使用資料庫儲存歷史記錄
8. **API Key 加密**: 加密儲存敏感資訊
