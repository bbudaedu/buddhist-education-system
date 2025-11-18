# Implementation Plan

- [x] 1. Set up project structure and dependencies

  - Create main application file `newbook_summary_app.py`
  - Create `requirements.txt` with all dependencies
  - Create configuration template file
  - _Requirements: 1.1, 2.3, 5.1_

-

- [x] 2. Implement configuration management module

  - [x] 2.1 Create ConfigManager class for loading and saving configuration

    - Implement JSON-based config file handling
    - Add validation methods for API key, paths, and email settings
    - _Requirements: 5.2, 5.3, 5.4, 5.5_

  - [x] 2.2 Create default configuration template

    - Define all required configuration fields
    - Set default values where applicable
    - _Requirements: 1.1_

-

- [x] 3. Implement logging system

  - [x] 3.1 Create TkinterLogHandler class

    - Implement custom logging handler for Tkinter ScrolledText widget
    - Add thread-safe log message insertion
    - _Requirements: 2.1, 2.2_

  - [x] 3.2 Set up file and UI logging

    - Configure logging to write to both file and UI
    - Implement log file naming with timestamp
    - Set up log levels (INFO, WARNING, ERROR, CRITICAL)
    - _Requirements: 2.3, 2.4, 2.5_

-

- [x] 4. Implement GUI layer with Tkinter

  - [x] 4.1 Create main application window and layout

    - Create NewBookSummaryApp class inheriting from tk.Frame
    - Set up window title, size, and basic layout
    - _Requirements: 1.1, 1.2_

  - [x] 4.2 Create configuration panel UI components

    - Add input fields for Gemini API key (masked)
    - Add input fields for ChromeDriver path with browse button
    - Add input fields for target URL and baseline book title
    - Add input fields for download directory with browse button
    - Add input fields for SMTP settings (server, port, username, password)
    - Add input field for email recipients
    - _Requirements: 1.3, 1.4_

  - [x] 4.3 Create control panel with action buttons

    - Add "Start Processing" button
    - Add "Stop Processing" button
    - Add "Check Configuration" button
    - Implement button enable/disable logic
    - _Requirements: 1.4, 3.1, 3.5, 5.1_

  - [x] 4.4 Create log display panel

    - Add ScrolledText widget for log display
    - Make log display read-only
    - Implement auto-scroll to latest messages
    - _Requirements: 2.1, 2.5_

  - [x] 4.5 Implement configuration check functionality

    - Validate Gemini API key is not empty
    - Verify ChromeDriver executable exists
    - Check SMTP settings are configured
    - Display specific error messages for failed checks
    - _Requirements: 5.2, 5.3, 5.4, 5.5_

- [x] 5. Implement web scraper module with Selenium

- [ ] 5. Implement web scraper module with Selenium

  - [x] 5.1 Create BookScraper class

    - Initialize WebDriver with Chrome options
    - Configure download preferences for PDF files
    - _Requirements: 6.1, 7.1_

  - [x] 5.2 Implement page navigation and waiting

    - Navigate to target website URL
    - Wait for dynamic content to load (up to 15 seconds)
    - _Requirements: 6.1, 6.2_

  - [x] 5.3 Implement new book identification logic

    - Locate all book card elements using CSS selector
    - Find baseline book by title matching
    - Extract books appearing before baseline
    - _Requirements: 6.3, 6.4, 6.5_

  - [x] 5.4 Implement book information extraction

    - Extract book title from card element
    - Click "電子檔下載" button
    - Extract PDF download link from modal
    - Close download modal
    - _Requirements: 7.1, 7.2_

  - [x] 5.5 Implement PDF download functionality

    - Download PDF using extracted URL
    - Save with original filename
    - Log download status
    - _Requirements: 7.3, 7.4, 7.5_

-

- [x] 6. Implement AI processor module with Gemini API

  - [x] 6.1 Create GeminiProcessor class

    - Initialize Gemini client using google-genai SDK
    - Configure with API key
    - _Requirements: 8.1, 11.2_

  - [x] 6.2 Implement PDF size checking

    - Check file size in bytes
    - Compare against 30MB threshold
    - _Requirements: 8.2, 8.3_

  - [x] 6.3 Implement PDF text extraction

    - Use pypdf to extract text from PDF
    - Handle extraction errors gracefully
    - _Requirements: 8.4_

  - [x] 6.4 Implement PDF-based summary generation

    - Upload PDF or send as bytes to Gemini API
    - Send prompt requesting 300-character Traditional Chinese summary
    - Configure API parameters (temperature, top_p, top_k)
    - Extract summary from API response
    - _Requirements: 8.4, 8.5, 8.6, 8.7, 11.2, 11.3_

  - [x] 6.5 Implement Google Search-based summary generation

    - Send search query to Gemini API with google_search tool
    - Request 300-character Traditional Chinese summary
    - Extract summary from search results
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 11.2_

  - [x] 6.6 Implement main book processing logic

    - Check PDF size and select processing method
    - Call appropriate summary generation method
    - Log which method was used
    - Return summary with metadata
    - _Requirements: 8.3, 12.5_

  - [x] 6.7 Implement retry mechanism for API calls

    - Retry up to 3 times on failure
    - Use 10-second delay between retries
    - _Requirements: 11.4, 13.2_

- [x] 7. Implement document generator module

  - [x] 7.1 Create DocumentGenerator class

    - Initialize with logger
    - _Requirements: 9.1_

  - [x] 7.2 Implement Word document generation

    - Create Word document with title and date
    - Add book entries with formatted titles (bold, 14pt)
    - Add summaries with proper spacing
    - Save document with filename format "新書簡介\_YYYY-MM-DD.docx"
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 7.3 Implement Excel document generation

    - Create Excel workbook with headers
    - Format header row (bold, colored background, centered)
    - Add book data rows with all fields (序號, 書名, PDF 檔名, 檔案大小, 處理方式, 摘要, 下載連結, 處理時間)
    - Set appropriate column widths
    - Save document with filename format "新書詳細資料\_YYYY-MM-DD.xlsx"
    - _Requirements: 9.1, 9.2, 9.5_

- [ ] 8. Implement email sender module

  - [x] 8.1 Create EmailSender class

    - Initialize with SMTP settings (server, port, username, password)

    - _Requirements: 10.2_

  - [ ] 8.2 Implement email message creation

    - Create MIME multipart message
    - Set sender, recipients, and subject
    - Add email body text

    - _Requirements: 10.3, 10.4_

  - [x] 8.3 Implement file attachment functionality

    - Support multiple attachments (Word and Excel)
    - Detect file type and set appropriate MIME type
    - Attach files to email message
    - _Requirements: 10.1_

  - [x] 8.4 Implement email sending

    - Connect to SMTP server with TLS
    - Authenticate with credentials

    - Send email message
    - Log success with recipient addresses
    - _Requirements: 10.2, 10.5_

- [x] 9. Implement progress management system

  - [ ] 9.1 Create progress cache structure

    - Define JSON format for progress data
    - Include session ID, timestamps, and processed books list

    - _Requirements: 4.1, 4.2_

  - [ ] 9.2 Implement progress save functionality

    - Save processed books to JSON cache file
    - Use atomic write with temporary file
    - _Requirements: 4.2_

  - [x] 9.3 Implement progress load functionality

    - Load cache file on startup
    - Parse processed books list
    - Skip already processed books
    - _Requirements: 4.3_

  - [ ] 9.4 Implement cache cleanup
    - Delete cache file when all books are processed
    - _Requirements: 4.4_

- [x] 10. Implement task orchestrator and main processing flow

  - [ ] 10.1 Create MainProcessor class

    - Initialize all modules (scraper, AI processor, document generator, email sender)
    - Set up stop flag for interruption
    - _Requirements: 3.2, 3.3_

  - [ ] 10.2 Implement main processing workflow

    - Load progress cache
    - Initialize web scraper and find new books
    - Process each book (download, generate summary)
    - Save progress after each book
    - Generate Word and Excel documents
    - Send email with attachments
    - Clean up resources
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ] 10.3 Implement interruption handling

    - Check stop flag between operations
    - Save progress before stopping
    - Log interruption event
    - _Requirements: 3.2, 3.3, 3.4_

  - [ ] 10.4 Implement threading for background execution
    - Run main processing in separate thread
    - Update UI from worker thread safely
    - _Requirements: 1.4, 3.5_

- [x] 11. Implement error handling and recovery

  - [x] 11.1 Add network error handling

    - Catch and log network errors
    - Continue processing remaining books
    - _Requirements: 13.1_

  - [x] 11.2 Add API error handling with retry

    - Implement retry logic for Gemini API failures
    - Use exponential backoff for rate limits
    - _Requirements: 13.2_

  - [x] 11.3 Add file system error handling

    - Handle PDF download failures gracefully
    - Log failures and continue with next book
    - _Requirements: 13.3_

  - [x] 11.4 Add email error handling

    - Display specific error messages for SMTP failures
    - _Requirements: 13.4_

  - [x] 11.5 Ensure process continues on single book failure

    - Wrap individual book processing in try-except
    - Log errors without terminating entire process
    - _Requirements: 13.5_

-

- [x] 12. Integration and final touches

  - [x] 12.1 Connect all modules in main application

    - Wire up GUI buttons to processing functions
    - Connect logging to all modules
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 12.2 Implement configuration persistence

    - Load config on startup
    - Save config on window close
    - _Requirements: 4.5_

  - [x] 12.3 Add user feedback and status updates

    - Update progress information in UI
    - Show processing status for each book
    - _Requirements: 1.5_

  - [x] 12.4 Create README with setup instructions

    - Document dependencies installation
    - Explain configuration steps
    - Provide usage examples
    - _Requirements: 1.1_
