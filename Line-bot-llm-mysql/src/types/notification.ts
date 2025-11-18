/**
 * Notification system type definitions for daily book notifications
 */

/**
 * Processed book data from Python ebook system
 */
export interface ProcessedBookData {
  processingDate: string;
  totalBooksFound: number;
  successfullyProcessed: BookSummary[];
  processingStats: {
    booksProcessed: number;
    booksFailed: number;
    pdfExtractions: number;
    googleSearches: number;
  };
}

/**
 * Individual book summary from ebook processor
 */
export interface BookSummary {
  title: string;
  author?: string;
  summary: string;
  downloadUrl: string;
  processingMethod: 'pdf_extract' | 'google_search';
  processingSuccess: boolean;
}

/**
 * Notification message content for LINE delivery
 */
export interface NotificationMessage {
  id: string;
  recipientUserId: string;
  messageType: 'single_book' | 'multiple_books' | 'daily_summary';
  content: MessageContent;
  deliveryStatus: 'pending' | 'sent' | 'failed';
  createdAt: Date;
  sentAt?: Date;
  errorMessage?: string;
}

/**
 * Message content structure for LINE messages
 */
export interface MessageContent {
  text: string;
  quickReply?: any; // LINE QuickReply type
  flexMessage?: any; // LINE FlexMessage type
}

/**
 * Delivery result summary
 */
export interface DeliveryResult {
  totalRecipients: number;
  successfulDeliveries: number;
  failedDeliveries: number;
  deliveryFailures: DeliveryFailureInfo[];
  processingTime: number;
}

/**
 * Delivery failure information
 */
export interface DeliveryFailureInfo {
  userId: string;
  errorType: 'user_blocked' | 'invalid_user' | 'rate_limit' | 'api_error';
  errorMessage: string;
  retryable: boolean;
}

/**
 * Notification processing configuration
 */
export interface NotificationConfig {
  maxRecipientsPerBatch: number;
  deliveryTimeoutMs: number;
  maxBooksPerMessage: number;
  enableRichMessages: boolean;
  retryAttempts: number;
  retryDelayMs: number;
}