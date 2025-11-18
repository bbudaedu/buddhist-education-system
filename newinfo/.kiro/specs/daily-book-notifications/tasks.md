# Implementation Plan

- [x] 1. Set up database schema and subscription management





  - Create database migration scripts for user subscriptions, notification logs, and delivery failures tables
  - Implement SubscriptionService class with CRUD operations for user subscription management
  - Add database connection and migration support to existing DatabaseService
  - _Requirements: 1.1, 1.3, 4.1, 4.4_

- [x] 2. Extend LINE bot webhook handler for subscription commands




  - [x] 2.1 Add subscription command handlers to WebhookHandler


    - Implement handlers for "訂閱新書", "取消訂閱", and "訂閱狀態" commands
    - Add subscription menu options to existing quick reply system
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 2.2 Create subscription management UI components


    - Design LINE Flex Messages for subscription confirmation and status display
    - Implement user-friendly subscription flow with confirmation messages
    - _Requirements: 1.4, 1.5_
-

- [x] 3. Implement notification service and message formatting



  - [x] 3.1 Create NotificationService class for processing and delivering notifications


    - Implement methods to read processed book data from Python ebook system
    - Create notification message formatting logic for single and multiple books
    - Add delivery batching and rate limiting to handle large subscriber lists
    - _Requirements: 3.1, 3.2, 3.4_



  - [x] 3.2 Design notification message templates


    - Create LINE Flex Message templates for book notifications with title, author, summary, and download link
    - Implement mobile-optimized message formatting with proper text truncation



    - Add fallback text messages for users with older LINE clients


    - _Requirements: 3.2, 3.4_

- [x] 4. Create daily scheduler service












  - [x] 4.1 Implement DailyScheduler class with cron job functionality


    - Set up daily execution at configured time using node-cron or similar library

    - Implement retry logic with exponential backoff for failed processing attempts
    - Add logging and monitoring for scheduled executions


    - _Requirements: 2.1, 2.4, 2.5_

  - [x] 4.2 Create integration bridge with Python ebook processor


    - Implement file-based communication to trigger Python ebook processing


    - Add monitoring for ebook processing completion and result file generation
    - Handle processing failures and timeout scenarios gracefully
    - _Requirements: 2.1, 2.2, 5.1, 5.2_







- [ ] 5. Implement delivery tracking and error handling

  - [x] 5.1 Create delivery result tracking and logging


    - Implement NotificationLog model and database operations for tracking delivery statistics
    - Add DeliveryFailure tracking for failed notification attempts with error categorization
    - Create metrics collection for successful and failed deliveries
    - _Requirements: 3.5, 4.2, 4.3, 4.4_

  - [ ] 5.2 Add comprehensive error handling and recovery
    - Implement retry mechanisms for transient delivery failures (rate limits, temporary API issues)
    - Add user status management for handling blocked or inactive LINE accounts
    - Create error categorization and logging for debugging and monitoring
    - _Requirements: 3.5, 4.4_

- [ ] 6. Add configuration and environment setup

  - [ ] 6.1 Extend configuration system for notification features
    - Add notification-specific configuration options to existing config system
    - Implement environment variables for scheduler timing, batch sizes, and retry settings
    - Create configuration validation for notification system settings
    - _Requirements: 2.1, 2.4, 5.3, 5.4_

  - [ ] 6.2 Create deployment scripts and database migrations
    - Write database migration scripts for new tables and indexes


    - Add npm scripts for running migrations and starting scheduler service


    - Create Docker configuration updates for notification system deployment
    - _Requirements: 5.1, 5.2, 5.3_

- [x]* 7. Add comprehensive testing suite


  - [ ]* 7.1 Write unit tests for subscription service
    - Test user subscription/unsubscription workflows and edge cases
    - Test database operations and data integrity for subscription management






    - Test notification preferences and user status management
    - _Requirements: 1.1, 1.3, 1.5_

  - [x]* 7.2 Write integration tests for notification delivery


    - Test end-to-end notification workflow from ebook processing to delivery
    - Test LINE API integration with mock and real API calls
    - Test error handling and retry mechanisms for delivery failures
    - _Requirements: 3.1, 3.2, 3.5_

  - [ ]* 7.3 Write tests for scheduler and Python integration
    - Test daily scheduler execution and retry logic
    - Test file-based communication with Python ebook processor
    - Test system behavior during processing failures and recovery
    - _Requirements: 2.1, 2.4, 2.5, 5.1_

- [ ] 8. Integrate with existing ebook processing system

  - [ ] 8.1 Modify Python ebook processor to output notification data
    - Update main_processor.py to generate JSON output file with processed book summaries
    - Add notification-specific data fields (title, author, summary, download URL) to output format
    - Ensure backward compatibility with existing email functionality
    - _Requirements: 2.2, 3.1, 5.1, 5.2_

  - [ ] 8.2 Create data exchange interface between Python and TypeScript systems
    - Implement file monitoring in TypeScript service to detect new ebook processing results
    - Add data validation and error handling for malformed or incomplete ebook processor output
    - Create fallback mechanisms when ebook processing fails or produces no results
    - _Requirements: 2.2, 5.1, 5.2, 5.4_

- [ ] 9. Add monitoring and metrics collection

  - [ ] 9.1 Implement system health monitoring
    - Add health check endpoints for scheduler service and notification system status
    - Implement database connectivity monitoring and connection pool health checks
    - Create logging for system performance metrics and processing statistics
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 9.2 Create administrative dashboard endpoints
    - Add REST endpoints for viewing subscription statistics and delivery metrics
    - Implement endpoints for manual notification triggering and system status monitoring
    - Create logging and audit trail for administrative actions
    - _Requirements: 4.1, 4.2, 4.3, 4.4_