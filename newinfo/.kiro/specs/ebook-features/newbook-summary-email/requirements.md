# Requirements Document

## Introduction

本系統為「新書摘要與郵件發送系統」，目的是自動化處理佛教教育網站的新書資訊。系統將自動訪問指定網頁、識別新書、下載 PDF 檔案、使用 Gemini Pro 2.5 生成摘要、將摘要整理到 Word 文件，最後透過電子郵件發送給指定收件人。

## Glossary

- **System**: 新書摘要與郵件發送系統
- **Gemini Pro 2.5**: Google 的生成式 AI 模型，用於生成書籍摘要
- **Context7**: 提供最新 API 使用範例的文件服務
- **Target Website**: 佛教教育網站 (https://www.budaedu.org)
- **PDF Document**: 新書的電子檔案格式
- **Summary**: 由 AI 生成的 300 字書籍摘要
- **Word Document**: Microsoft Word 格式的文件 (.docx)
- **Email Recipients**: jackyfang@budaedu.org 和 tyguo@budaedu.org
- **UI**: 使用者介面 (User Interface)
- **Log**: 系統執行過程的記錄訊息
- **Interrupt Function**: 允許使用者中斷正在執行的任務
- **Save Function**: 儲存處理進度和結果的功能
- **Check Function**: 驗證系統狀態和資料完整性的功能

## Requirements

### Requirement 1

**User Story:** 作為系統使用者，我希望能夠透過簡單的圖形介面操作系統，以便我不需要記憶複雜的命令列指令

#### Acceptance Criteria

1. THE System SHALL provide a graphical user interface with clearly labeled buttons and input fields
2. WHEN the user launches the application, THE System SHALL display all main functions on a single window
3. THE System SHALL use Traditional Chinese language for all UI elements and messages
4. THE System SHALL provide visual feedback for all button clicks within 500 milliseconds
5. THE System SHALL display status information for each operation in the UI

### Requirement 2

**User Story:** 作為系統使用者，我希望能夠查看詳細的執行日誌，以便我了解系統正在執行什麼操作以及是否有錯誤發生

#### Acceptance Criteria

1. THE System SHALL display real-time log messages in a scrollable text area within the UI
2. WHEN any operation executes, THE System SHALL write log entries with timestamp, log level, and message content
3. THE System SHALL save all log messages to a text file with filename format "log_YYYY-MM-DD_HH-MM-SS.txt"
4. THE System SHALL support log levels including INFO, WARNING, ERROR, and CRITICAL
5. THE System SHALL automatically scroll the log display to show the most recent messages

### Requirement 3

**User Story:** 作為系統使用者，我希望能夠隨時中斷正在執行的長時間任務，以便我在發現錯誤或需要修改設定時停止處理

#### Acceptance Criteria

1. THE System SHALL provide a visible "Stop" button that becomes enabled during task execution
2. WHEN the user clicks the Stop button, THE System SHALL terminate the current operation within 3 seconds
3. WHEN an operation is interrupted, THE System SHALL save the current progress to allow resumption
4. THE System SHALL log the interruption event with the current processing state
5. WHEN an operation completes or is interrupted, THE System SHALL re-enable all control buttons

### Requirement 4

**User Story:** 作為系統使用者，我希望系統能夠自動儲存處理進度，以便我在中斷後可以從上次停止的地方繼續執行

#### Acceptance Criteria

1. THE System SHALL create a progress cache file in JSON format for each processing session
2. WHEN processing is interrupted, THE System SHALL save the list of completed books to the cache file
3. WHEN the user restarts a processing task, THE System SHALL load the cache file and skip already processed books
4. THE System SHALL delete the cache file when all books are successfully processed
5. THE System SHALL store cache files in the same directory as the downloaded PDFs

### Requirement 5

**User Story:** 作為系統使用者，我希望系統能夠檢查必要的設定和檔案，以便在執行前確認所有條件都已滿足

#### Acceptance Criteria

1. THE System SHALL provide a "Check Configuration" button in the UI
2. WHEN the user clicks the Check Configuration button, THE System SHALL verify the Gemini API key is not empty
3. WHEN the user clicks the Check Configuration button, THE System SHALL verify the email SMTP settings are configured
4. WHEN the user clicks the Check Configuration button, THE System SHALL verify the ChromeDriver executable exists at the specified path
5. WHEN any check fails, THE System SHALL display a specific error message indicating which configuration item needs attention

### Requirement 6

**User Story:** 作為系統管理員，我希望系統能夠訪問指定的網頁並識別新書，以便自動取得最新出版的書籍資訊

#### Acceptance Criteria

1. THE System SHALL use Selenium WebDriver to navigate to the target website URL
2. WHEN the page loads, THE System SHALL wait up to 15 seconds for dynamic content to render
3. THE System SHALL locate all book card elements using CSS selector ".card-body"
4. THE System SHALL identify the baseline book by matching the configured book title substring
5. THE System SHALL extract all book cards appearing before the baseline book as new books

### Requirement 7

**User Story:** 作為系統管理員，我希望系統能夠自動下載新書的 PDF 檔案，以便後續進行內容分析

#### Acceptance Criteria

1. WHEN a new book is identified, THE System SHALL click the "電子檔下載" button within the book card
2. WHEN the download modal appears, THE System SHALL extract the first PDF download link
3. THE System SHALL download the PDF file using the extracted URL to the configured download directory
4. THE System SHALL save each PDF file with its original filename from the URL
5. THE System SHALL log the download status for each book including success or failure

### Requirement 8

**User Story:** 作為內容編輯，我希望系統能夠使用 Gemini Pro 2.5 生成每本新書的 300 字摘要，以便快速了解書籍內容

#### Acceptance Criteria

1. THE System SHALL configure the Gemini API client with the model name "gemini-2.5-pro"
2. WHEN a PDF is downloaded, THE System SHALL check the file size in bytes
3. IF the PDF file size exceeds 30 megabytes, THEN THE System SHALL use Google search method to obtain book information instead of PDF text extraction
4. IF the PDF file size is 30 megabytes or less, THEN THE System SHALL extract the full text content from the PDF and send it to Gemini API
5. THE System SHALL send a prompt to Gemini API requesting a 300-character Traditional Chinese summary
6. THE System SHALL set the API timeout to 120 seconds for each request
7. WHEN the API returns a response, THE System SHALL extract the summary text from the response

### Requirement 9

**User Story:** 作為內容編輯，我希望系統能夠將所有新書摘要整理到一個 Word 文件中，以便我可以方便地查看和編輯

#### Acceptance Criteria

1. THE System SHALL create a new Word document with filename format "新書簡介_YYYY-MM-DD.docx"
2. WHEN a book summary is generated, THE System SHALL add an entry to the Word document containing book title and summary
3. THE System SHALL format each book entry with the title in bold and 14-point font
4. THE System SHALL separate each book entry with a blank line
5. THE System SHALL save the Word document to the current working directory

### Requirement 10

**User Story:** 作為系統管理員，我希望系統能夠自動將包含新書摘要的 Word 文件發送給指定的收件人，以便相關人員及時收到更新

#### Acceptance Criteria

1. THE System SHALL send the Word document as an email attachment to jackyfang@budaedu.org and tyguo@budaedu.org
2. THE System SHALL use SMTP protocol to send the email
3. THE System SHALL set the email subject to "新書簡介 - YYYY年MM月DD日"
4. THE System SHALL include a brief message body explaining the attachment content
5. WHEN the email is sent successfully, THE System SHALL log a success message with the recipient addresses

### Requirement 11

**User Story:** 作為開發人員，我希望系統能夠參考 Context7 的最新範例，以便使用最新的 API 調用方式和最佳實踐

#### Acceptance Criteria

1. THE System SHALL retrieve Gemini API usage examples from Context7 documentation
2. THE System SHALL implement API calls following the patterns shown in Context7 examples
3. THE System SHALL use the same error handling patterns as demonstrated in Context7 examples
4. THE System SHALL implement retry logic for API failures as recommended by Context7
5. THE System SHALL configure API parameters (temperature, top_p, top_k) based on Context7 recommendations

### Requirement 12

**User Story:** 作為系統開發者，我希望系統能夠針對大型 PDF 檔案使用替代方案，以便避免消耗過多的 API token 成本

#### Acceptance Criteria

1. WHEN a PDF file size exceeds 30 megabytes, THE System SHALL construct a Google search query using the book title
2. WHEN using Google search method, THE System SHALL send the search query to Gemini API with instructions to search and summarize
3. THE System SHALL instruct Gemini to use its search capability to find book information online
4. THE System SHALL request Gemini to generate a 300-character Traditional Chinese summary based on search results
5. THE System SHALL log which method was used for each book (PDF extraction or Google search)

### Requirement 13

**User Story:** 作為系統使用者，我希望系統能夠處理錯誤情況並提供清晰的錯誤訊息，以便我知道如何解決問題

#### Acceptance Criteria

1. WHEN a network error occurs, THE System SHALL log the error and continue processing remaining books
2. WHEN the Gemini API returns an error, THE System SHALL retry the request up to 3 times with 10-second delays
3. WHEN a PDF download fails, THE System SHALL log the failure and continue with the next book
4. WHEN email sending fails, THE System SHALL display an error message with the SMTP error details
5. THE System SHALL not terminate the entire process due to a single book processing failure
