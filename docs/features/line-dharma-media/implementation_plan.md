# Implementation Plan - M2 Refactor: Real-time API Integration

## Goal Description
Refactor the "Latest Dharma Books" and "Latest Videos" features to use the specific API endpoints identified in the M0 Investigation Report (v3.0). This ensures the LINE Bot displays real-time, accurate data directly from the source systems without scraping.

## User Review Required
> [!IMPORTANT]
> **API Endpoints Change**:
> - Books: Switching to `/dharma/public/api/books/chinese`
> - Video Series: Switching to `/audiovisual/public/api/series/by-keyword-searched`
> - Live: Refining logic to use Weekday filter for "Today's Schedule".

## Proposed Changes

### Service Layer

#### [MODIFY] [src/services/dharmaBookService.ts](file:///d:/AIstudio/newinfo/Line-bot-llm-mysql/src/services/dharmaBookService.ts)
- **Endpoint**: Update to `https://publish.budaedu.org/dharma/public/api/books/chinese`
- **Parameters**: Add `per_page=5`, `page=1`, `order=latest_storage_date,desc`
- **Interface**: Update `DharmaBook` to match API response.
- **Mapping**:
    - `title` <- `name_zh`
    - `publishDate` <- `storage_date`
    - `pdfUrl` <- Parse from `downloads` (or `url`)
    - `coverImageUrl` <- Construct from `code` or use default if not provided.

#### [MODIFY] [src/services/videoStreamingService.ts](file:///d:/AIstudio/newinfo/Line-bot-llm-mysql/src/services/videoStreamingService.ts)
- **Refactor**: Split `getLatestContent` into distinct strategies for "Live" and "VOD".
- **Live Strategy (`fetchLiveEvents`)**:
    - Endpoint: `https://publish.budaedu.org/laravel/public/api/courses`
    - Logic: Filter by `week={current_weekday}` and `have_live_stream=true`.
    - Mapping: `title_name`, `lecturer.lecr_name`, `live_stream_url`.
- **VOD Strategy (`fetchVideoSeries`)**:
    - Endpoint: `https://publish.budaedu.org/audiovisual/public/api/series/by-keyword-searched`
    - Params: `filter[ended]=N`, `order=latest_filedate,desc`, `per_page=10`
    - Mapping:
        - `title` <- `title_name`
        - `instructor` <- `lecr_name`
        - `link` <- Construct series URL `https://www.budaedu.org/#/series/{title_no}`

### Handler Layer

#### [MODIFY] [src/handlers/dharmaMediaHandler.ts](file:///d:/AIstudio/newinfo/Line-bot-llm-mysql/src/handlers/dharmaMediaHandler.ts)
- Ensure handler correctly processes the updated data models from services.
- No major logic change expected, just data flow verification.

## Verification Plan

### Automated Tests
- **Unit Tests**: Update `test_book_api.js` (or create new `test_services.ts`) to verify:
    1. Book API returns valid JSON with `name_zh`.
    2. Video Series API returns valid JSON with `title_name`.
    3. Live API returns data for the current weekday (or empty if no live).

### Manual Verification
- **LINE Bot**:
    - Command `最新法寶`: Check if the carousel shows the latest Chinese books.
    - Command `最新影音`: Check if it shows "Live" (if any) and "Latest Series".
