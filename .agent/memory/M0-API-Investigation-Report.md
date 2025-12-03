Context: Budaedu.org API Integration Specification (v5.3)
Role: You are a Backend Engineer building a data connector for the Budaedu (佛陀教育基金會) system. Constraint: DO NOT use web scraping (Selenium/BeautifulSoup). Use ONLY the verified HTTP API endpoints documented below. Tech Stack: Node.js (Axios) or Python (Requests/FastAPI).

1. Domain: Dharma Books (經書法寶)
1.1 Book List (Search & Index)
Endpoint: GET https://publish.budaedu.org/dharma/public/api/books/chinese

Purpose: Search books to get id and code.

Query Parameters:

per_page: 10 (Adjustable)

page: 1

order: latest_storage_date,desc

filter[name]: {keyword} (Optional: Search by book title)

filter[have_efile]: Y (Optional: Only show books with digital files)

Response Fields:

id: Book ID

code: Book code (e.g., "CH382-16", used for cover image)

chinese_name: Title

chinese_author: Author

chinese_intro: HTML string (Requires stripping)

latest_storage_date: Date string

1.2 PDF Download Link (Files)
Endpoint: GET https://publish.budaedu.org/dharma/public/api/books/{id}/efiles

Query Parameters: include=attached, order=name,asc

Target: data[0].url

1.3 Cover Image Logic (Computed)
Logic: Remove hyphens from code, append .jpg.

Base URL: https://www2.budaedu.org/dharma-data/book-front-cover/

Example: CH550-03 -> https://www2.budaedu.org/dharma-data/book-front-cover/CH55003.jpg

2. Domain: Courses & Live Streaming (課程直播)
2.1 Course Schedule (List View)
Endpoint: GET https://publish.budaedu.org/laravel/public/api/courses

Purpose: Get the weekly schedule, lecturer info, and live stream links.

Query Parameters:

filter[continued]: 1 (Status: Active/Continued courses)

filter[week]: {1-7} (Optional: 1=Mon, ..., 7=Sun)

include: places (CRITICAL: Retrieves live stream URL and location)

order: week,asc|spk_start_time,asc

Response Handling:

ID: id (String, e.g., "1012")

Title: title_name

Lecturer: lecturer.lecr_name

Intro: intro (Raw HTML, usually dirty, requires cleaning)

Time: week (Day), spk_start_time ~ spk_end_time

Live Stream: Iterate through places[].

Check pivot.live == "Y"

Get live_stream_url (HLS/m3u8) or mobile_live_url.

2.2 Single Course Detail (Lightweight / Optimization)
Endpoint: GET https://publish.budaedu.org/laravel/public/api/courses

Purpose: Fetch specific course details (e.g., Intro) without over-fetching data.

Optimization Strategy: Use Sparse Fieldsets to reduce payload size.

Query Parameters:

filter[id]: {id} (Target Course ID, e.g., "1012")

fields[courses]: id,title_name,intro (Only fetch these fields)

Why: The intro field contains heavy HTML. Fetching it only when user clicks "More Info" improves list performance.

Example Request:

GET .../courses?filter[id]=1012&fields[courses]=id,title_name,intro
2.3 Course Data Cleaning
Input: intro field (e.g., \u003Cp class=\"MsoNormal\"...)

Problem: Contains MS Word specific tags and raw HTML.

Solution: Reuse the stripHtmlTags function defined in Section 4.

3. Domain: Video Series (影音點播)
3.1 Ongoing Courses List
Endpoint: GET https://publish.budaedu.org/audiovisual/public/api/series/by-keyword-searched

Query Parameters: filter[ended]=N, order=latest_filedate,desc

Key Fields: title_no (Series ID), VL_nfiles (Count).

4. Implementation Logic & Utilities
Utility: HTML Cleaner (Universal)
Used for both Book Intro and Course Intro.

TypeScript

private stripHtmlTags(html: string): string {
  if (!html) return '';
  return html
    .replace(/<[^>]*>/g, '')        // Remove tags
    .replace(/&nbsp;/g, ' ')        // Decode spaces
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/mso-[^;]+;/g, '')     // Remove MS Office styles
    .replace(/\s+/g, ' ')           // Collapse whitespace
    .trim();
}
Logic: Get Course Detail (Optimized)
TypeScript

async function getCourseIntro(courseId: string): Promise<string> {
  try {
    // Request only the ID and Intro fields
    const response = await axios.get('https://publish.budaedu.org/laravel/public/api/courses', {
      params: {
        'filter[id]': courseId,
        'fields[courses]': 'id,intro' 
      }
    });

    const course = response.data.data[0];
    if (!course || !course.intro) return "暫無簡介";

    // Clean the HTML
    return stripHtmlTags(course.intro);

  } catch (error) {
    console.error(`Failed to fetch intro for course ${courseId}`, error);
    return "無法取得簡介";
  }
}
5. LINE Flex Message Integration
5.1 Book Card
Image: Computed Cover URL.

Action: Link to PDF if available.

5.2 Course Card
Header: week + spk_start_time (e.g., "週一 19:00").

Body: title_name + lecturer.lecr_name.

Footer Buttons:

直播: Open live_stream_url (If places[].pivot.live == 'Y').

簡介: Postback Action action=get_course_intro&id=1012. (Triggers logic in 2.2).

6. Performance Strategy
Caching Rules
Books: Cache for 5 minutes (TTL=300).

Course List: Cache for 10 minutes (TTL=600).

Course Intro: Cache for 24 hours (TTL=86400). Intros rarely change.

Error Handling
HTML Intro: If cleaning fails or returns empty, fallback to "詳細內容請點擊查看".

Live Links: If live_stream_url is missing but pivot.live is "Y", fallback to the generic live page URL.

Last Updated: 2025-12-03 Version: 5.3 (Added Course Sparse Fieldsets & ID Filtering)