# Requirements Document

## Introduction

This feature extends the existing Buddhist Education monitoring system to include real-time carousel monitoring, course information extraction, and multimedia content processing. The system will integrate with existing BookScraper, EmailSender, NewBookService, and notification infrastructure to provide comprehensive website monitoring capabilities.

## Glossary

- **Website_Monitor**: Extended monitoring system that adds carousel and course monitoring to existing book monitoring
- **Carousel_Scraper**: New component for extracting carousel banner information, extending existing BookScraper functionality
- **Course_Extractor**: New component that processes course information from popup dialogs
- **Media_Processor**: New component that handles multimedia content extraction
- **Data_Synchronizer**: Enhanced component that integrates with existing ExcelReaderService and BookSyncService to maintain dual storage in both Excel files and MySQL database
- **Notification_Sender**: Enhanced component that leverages existing EmailSender and NewBookService for notifications
- **Baseline_Manager**: Enhanced component that extends existing progress management for multiple content types
- **Chrome_DevTools**: Browser automation tool used for web scraping and testing, integrating with existing Selenium infrastructure
- **Bulletin_Scraper**: Component responsible for extracting course cancellation announcements from bulletin tables
- **News_Processor**: Component that processes latest news announcements and popup content

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to extend the existing monitoring system to include carousel banners, so that I can capture new promotional content and event information using the current infrastructure.

#### Acceptance Criteria

1. WHEN the Website_Monitor starts, THE Carousel_Scraper SHALL extend existing BookScraper functionality to extract carousel banner images from https://www.budaedu.org/#/
2. WHEN a carousel banner is detected, THE Carousel_Scraper SHALL capture the poster image and click to retrieve the activity introduction link using existing Selenium infrastructure
3. WHEN clicking on a banner image, THE Course_Extractor SHALL capture popup dialog information including course name, location, instructor, and course description
4. THE Website_Monitor SHALL store carousel information in structured format with fields for banner_title, image_url, activity_link, course_name, location, instructor, description, extraction_timestamp, and carousel_id
5. THE Carousel_Scraper SHALL format extracted data to be compatible with both Excel synchronization and MySQL database insertion
6. THE Baseline_Manager SHALL extend existing baseline management to handle carousel content reference points

### Requirement 2

**User Story:** As a content manager, I want to extract detailed course information from popup dialogs, so that I can maintain accurate course databases.

#### Acceptance Criteria

1. WHEN a course banner is clicked, THE Course_Extractor SHALL wait for the popup dialog to appear
2. WHEN the popup dialog is displayed, THE Course_Extractor SHALL extract the course name field
3. WHEN the popup dialog is displayed, THE Course_Extractor SHALL extract the class location field
4. WHEN the popup dialog is displayed, THE Course_Extractor SHALL extract the instructor name field
5. WHEN the popup dialog is displayed, THE Course_Extractor SHALL extract the course description field

### Requirement 3

**User Story:** As a multimedia content curator, I want to capture the latest video and audio information, so that I can keep track of educational media resources in structured format.

#### Acceptance Criteria

1. WHEN accessing multimedia content sections, THE Media_Processor SHALL locate lecture introduction links
2. WHEN a lecture introduction link is found, THE Media_Processor SHALL capture the redirect URL
3. WHEN processing multimedia content, THE Media_Processor SHALL extract the course title
4. WHEN processing multimedia content, THE Media_Processor SHALL extract the speaker information
5. WHEN processing multimedia content, THE Media_Processor SHALL extract the course start date
6. THE Media_Processor SHALL store extracted multimedia data in structured format with fields for course_title, speaker_name, start_date, redirect_url, media_type, extraction_timestamp, and media_id
7. THE Media_Processor SHALL format extracted data to be compatible with both Excel synchronization and MySQL database insertion

### Requirement 4

**User Story:** As a database administrator, I want all extracted information synchronized to both Excel files and MySQL database, so that I can maintain dual storage for backup and integration purposes.

#### Acceptance Criteria

1. WHEN course information is extracted, THE Data_Synchronizer SHALL create Excel entries using existing document_generator.py AND synchronize to MySQL database using existing BookSyncService
2. WHEN multimedia information is extracted, THE Data_Synchronizer SHALL create Excel entries for media content AND insert records into MySQL database tables
3. WHEN course cancellation data is extracted, THE Data_Synchronizer SHALL create Excel sheet with columns for date, course name, and instructor AND create corresponding MySQL table entries
4. WHEN news announcement data is extracted, THE Data_Synchronizer SHALL create Excel sheet with columns for title, publication date, and content AND store in MySQL database
5. WHEN carousel information is extracted, THE Data_Synchronizer SHALL create Excel entries for carousel data AND synchronize to MySQL database using existing infrastructure
6. THE Data_Synchronizer SHALL extend existing Excel generation functionality to create separate sheets for all content types AND maintain corresponding MySQL database tables
7. THE Data_Synchronizer SHALL use existing timestamp management from progress_manager.py for both Excel and MySQL database entries
8. THE Data_Synchronizer SHALL leverage existing ExcelReaderService and BookSyncService to ensure data consistency between Excel files and MySQL database

### Requirement 5

**User Story:** As a notification recipient, I want to receive automatic updates about new content, so that I can stay informed about website changes using existing notification infrastructure.

#### Acceptance Criteria

1. WHEN new content is detected and processed, THE Notification_Sender SHALL integrate with existing NewBookService to send LINE messages with content summaries
2. WHEN new content is detected and processed, THE Notification_Sender SHALL use existing EmailSender to send email notifications with detailed information
3. WHEN notifications are sent, THE Notification_Sender SHALL extend existing notification_processor.py to include relevant links and images
4. THE Notification_Sender SHALL leverage existing notification formatting from the current system for user-friendly presentation
5. THE Notification_Sender SHALL use existing error handling from EmailSender for notification delivery failures

### Requirement 6

**User Story:** As a system operator, I want automated baseline management, so that the system can detect new content efficiently using existing baseline infrastructure.

#### Acceptance Criteria

1. WHEN the monitoring cycle completes successfully, THE Baseline_Manager SHALL extend existing progress_manager.py to update reference points for carousel content
2. WHEN the monitoring cycle completes successfully, THE Baseline_Manager SHALL integrate with existing baseline management to update reference points for course information
3. WHEN the monitoring cycle completes successfully, THE Baseline_Manager SHALL use existing baseline tracking to update reference points for multimedia content
4. WHEN the monitoring cycle completes successfully, THE Baseline_Manager SHALL update reference points for course cancellation announcements
5. WHEN the monitoring cycle completes successfully, THE Baseline_Manager SHALL update reference points for latest news announcements
6. THE Baseline_Manager SHALL extend existing historical baseline functionality from progress_manager.py for comparison purposes across all content types
7. THE Baseline_Manager SHALL leverage existing configuration backup system for baseline restoration capabilities

### Requirement 7

**User Story:** As a developer, I want to use Chrome DevTools for web element extraction and testing, so that I can ensure reliable web scraping functionality while integrating with existing Selenium infrastructure.

#### Acceptance Criteria

1. WHEN performing web scraping operations, THE Website_Monitor SHALL integrate Chrome_DevTools with existing BookScraper Selenium automation
2. WHEN testing web element extraction, THE Chrome_DevTools SHALL extend existing ChromeDriver configuration for debugging capabilities
3. WHEN encountering dynamic content, THE Chrome_DevTools SHALL leverage existing wait_for_page_load functionality for JavaScript-rendered elements
4. THE Chrome_DevTools SHALL use existing headless Chrome configuration from BookScraper for production environments
5. THE Chrome_DevTools SHALL extend existing network error handling and retry logic from BookScraper for timeouts and page load failures

### Requirement 8

**User Story:** As a course administrator, I want to monitor course cancellation announcements automatically, so that I can stay informed about schedule changes and notify relevant parties.

#### Acceptance Criteria

1. WHEN the Website_Monitor accesses https://www.budaedu.org/#/bulletins/course-cancel, THE Bulletin_Scraper SHALL extract course cancellation table data
2. WHEN processing cancellation table, THE Bulletin_Scraper SHALL extract the date field from each table row
3. WHEN processing cancellation table, THE Bulletin_Scraper SHALL extract the course name field from each table row
4. WHEN processing cancellation table, THE Bulletin_Scraper SHALL extract the instructor name field from each table row
5. THE Bulletin_Scraper SHALL store extracted cancellation data in structured format with fields for cancellation_date, course_name, instructor_name, extraction_timestamp, and cancellation_id
6. THE Bulletin_Scraper SHALL format extracted data to be compatible with both Excel synchronization and MySQL database insertion
7. THE Bulletin_Scraper SHALL integrate with existing notification infrastructure to generate structured notification data for immediate alerts

### Requirement 9

**User Story:** As a news administrator, I want to monitor latest news announcements automatically, so that I can capture important announcements and their detailed content in structured format.

#### Acceptance Criteria

1. WHEN the Website_Monitor accesses https://www.budaedu.org/#/bulletins/, THE News_Processor SHALL identify all news announcement items
2. WHEN a news item is detected, THE News_Processor SHALL click on the item to trigger the popup dialog
3. WHEN the news popup dialog appears, THE News_Processor SHALL extract the complete announcement message content
4. WHEN processing news content, THE News_Processor SHALL capture the announcement title and publication date
5. THE News_Processor SHALL store extracted news data in structured format with fields for title, publication_date, content, extraction_timestamp, and announcement_id
6. THE News_Processor SHALL format extracted data to be compatible with both Excel synchronization and MySQL database insertion
7. THE News_Processor SHALL integrate with existing notification_processor.py to generate structured notification data for LINE and email distribution

### Requirement 10

**User Story:** As a system integrator, I want to reuse existing infrastructure components, so that I can minimize development effort and maintain consistency with current systems.

#### Acceptance Criteria

1. WHEN implementing carousel monitoring, THE Website_Monitor SHALL extend existing BookScraper class rather than creating new scraping infrastructure
2. WHEN processing extracted data, THE Website_Monitor SHALL reuse existing document_generator.py for Excel file creation
3. WHEN sending notifications, THE Website_Monitor SHALL integrate with existing notification_processor.py and EmailSender infrastructure
4. WHEN managing data synchronization, THE Website_Monitor SHALL leverage existing BookSyncService and ExcelReaderService from the LINE bot system
5. WHEN handling configuration, THE Website_Monitor SHALL extend existing config_manager.py rather than creating separate configuration management