# Requirements Document

## Introduction

A daily notification push system that allows LINE official account users to subscribe to receive automated notifications about new Buddhist education books. The system integrates the existing ebook processing workflow with the LINE bot to deliver daily summaries of new book releases including titles, authors, summaries, and download links to subscribed users.

## Glossary

- **LINE_Bot_Server**: The TypeScript/Node.js application that handles LINE messaging API interactions
- **Ebook_Processor**: The Python application that monitors budaedu.org and generates book summaries
- **Subscription_Service**: The component that manages user subscription preferences for notifications
- **Daily_Scheduler**: The automated process that triggers daily ebook processing and notification delivery
- **Notification_Message**: A formatted message containing book information sent to subscribed users
- **User_Subscriber**: A LINE user who has opted in to receive daily book notifications

## Requirements

### Requirement 1

**User Story:** As a LINE user, I want to subscribe to daily book notifications, so that I can automatically receive information about new Buddhist education books without manually checking the website.

#### Acceptance Criteria

1. WHEN a User_Subscriber sends a subscription command, THE LINE_Bot_Server SHALL store the user's subscription preference in the database
2. THE LINE_Bot_Server SHALL provide a subscription button or menu option for users to easily subscribe
3. WHEN a User_Subscriber requests to unsubscribe, THE LINE_Bot_Server SHALL remove their subscription preference from the database
4. THE LINE_Bot_Server SHALL confirm subscription and unsubscription actions with a confirmation message
5. WHERE a user is already subscribed, THE LINE_Bot_Server SHALL inform them of their current subscription status

### Requirement 2

**User Story:** As a system administrator, I want the ebook processing to run automatically on a daily schedule, so that new book information is consistently gathered and processed without manual intervention.

#### Acceptance Criteria

1. THE Daily_Scheduler SHALL execute the Ebook_Processor workflow once per day at a configured time
2. WHEN the Daily_Scheduler triggers processing, THE Ebook_Processor SHALL check for new books on budaedu.org
3. IF new books are found, THEN THE Ebook_Processor SHALL generate summaries using Google Gemini Pro 2.5
4. THE Daily_Scheduler SHALL log all processing activities with timestamps and status information
5. IF the daily processing fails, THEN THE Daily_Scheduler SHALL retry the process up to three times with exponential backoff

### Requirement 3

**User Story:** As a subscribed user, I want to receive formatted notifications about new books, so that I can quickly understand the book content and access download links.

#### Acceptance Criteria

1. WHEN new books are processed successfully, THE LINE_Bot_Server SHALL create Notification_Messages for each new book
2. THE Notification_Message SHALL include the book title, author name, AI-generated summary, and download link
3. THE LINE_Bot_Server SHALL send Notification_Messages to all active User_Subscribers
4. THE Notification_Message SHALL be formatted for optimal readability on mobile devices
5. IF a User_Subscriber's LINE account is inactive, THEN THE LINE_Bot_Server SHALL handle delivery failures gracefully and log the error

### Requirement 4

**User Story:** As a system administrator, I want to monitor notification delivery and subscription metrics, so that I can ensure the system is functioning properly and understand user engagement.

#### Acceptance Criteria

1. THE LINE_Bot_Server SHALL track the number of active User_Subscribers
2. THE LINE_Bot_Server SHALL log successful and failed notification deliveries with timestamps
3. THE LINE_Bot_Server SHALL provide metrics on daily notification volume and delivery success rates
4. WHEN notification delivery fails for a User_Subscriber, THE LINE_Bot_Server SHALL record the failure reason
5. THE LINE_Bot_Server SHALL maintain a history of sent notifications for audit purposes

### Requirement 5

**User Story:** As a system integrator, I want the notification system to integrate seamlessly with existing ebook and LINE bot infrastructure, so that minimal changes are required to current systems.

#### Acceptance Criteria

1. THE Daily_Scheduler SHALL integrate with the existing Ebook_Processor Python application without modifying its core functionality
2. THE LINE_Bot_Server SHALL extend the existing LINE bot codebase to include subscription management
3. THE Subscription_Service SHALL use the existing MySQL database infrastructure
4. THE notification system SHALL reuse existing Google Gemini AI processing capabilities
5. THE integration SHALL maintain backward compatibility with existing LINE bot features