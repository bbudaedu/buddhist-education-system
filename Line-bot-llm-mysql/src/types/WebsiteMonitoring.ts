/**
 * TypeScript interfaces for website monitoring content types
 */

export interface CarouselContent {
  id?: number;
  carousel_id: string;
  banner_title?: string;
  image_url?: string;
  activity_link?: string;
  course_name?: string;
  location?: string;
  instructor?: string;
  description?: string;
  extraction_timestamp?: string;
  sync_timestamp?: string;
  is_notified?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CourseCancellation {
  id?: number;
  cancellation_id: string;
  cancellation_date?: string;
  course_name?: string;
  instructor_name?: string;
  extraction_timestamp?: string;
  sync_timestamp?: string;
  is_notified?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface NewsAnnouncement {
  id?: number;
  announcement_id: string;
  title?: string;
  publication_date?: string;
  content?: string;
  extraction_timestamp?: string;
  sync_timestamp?: string;
  is_notified?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface MediaContent {
  id?: number;
  media_id: string;
  course_title?: string;
  speaker_name?: string;
  start_date?: string;
  redirect_url?: string;
  media_type?: string;
  extraction_timestamp?: string;
  sync_timestamp?: string;
  is_notified?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface WebsiteMonitoringData {
  carousel?: CarouselContent[];
  cancellation?: CourseCancellation[];
  news?: NewsAnnouncement[];
  media?: MediaContent[];
}

export interface ContentSyncResult {
  success: boolean;
  contentType: string;
  totalItems: number;
  successfulSyncs: number;
  failedSyncs: number;
  duration: number;
  errors: string[];
  message: string;
}

export interface BatchContentSyncResult {
  success: boolean;
  totalContentTypes: number;
  processedContentTypes: number;
  totalItems: number;
  successfulSyncs: number;
  failedSyncs: number;
  duration: number;
  contentResults: ContentSyncResult[];
  message: string;
}