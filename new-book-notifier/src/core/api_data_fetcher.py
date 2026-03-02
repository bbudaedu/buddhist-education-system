#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Budaedu API Data Fetcher
佛教教育基金會 API 資料抓取模組

取代原有爬蟲，透過官方 API 抓取資料：
- 書籍 (最新法寶)
- 佛卡 (歸類為書籍)
- 停課通知
- 最新消息
- 影音系列
"""

import logging
import requests
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from urllib3.exceptions import InsecureRequestWarning

# 忽略 SSL 警告 (開發環境)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class BudaeduAPIFetcher:
    """
    透過 API 抓取佛陀教育基金會資料
    
    取代 Selenium 爬蟲，提供更穩定的資料抓取方式
    """
    
    # API 基礎 URL
    DHARMA_BASE = "https://publish.budaedu.org/dharma/public/api"
    LARAVEL_BASE = "https://publish.budaedu.org/laravel/public/api"
    AUDIOVISUAL_BASE = "https://publish.budaedu.org/audiovisual/public/api"
    
    # 網站 URL (用於生成連結)
    WEBSITE_BASE = "https://www.budaedu.org/#"
    COVER_IMAGE_BASE = "https://www2.budaedu.org/dharma-data/book-front-cover"
    BUDDHA_CARD_IMAGE_BASE = "https://www2.budaedu.org/dharma-data/picture-downloadable-efile"
    
    # 請求設定
    DEFAULT_TIMEOUT = 10
    MAX_RETRIES = 3
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化 API 抓取器
        
        Args:
            logger: Logger 實例
        """
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        # 忽略 SSL 憑證驗證 (開發環境)
        self.session.verify = False
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        發送 API 請求，包含重試邏輯
        
        Args:
            url: API 端點 URL
            params: 查詢參數
            
        Returns:
            API 回應資料，失敗時返回 None
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.DEFAULT_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API 請求失敗 (第 {attempt + 1} 次): {url} - {e}")
                if attempt == self.MAX_RETRIES - 1:
                    self.logger.error(f"API 請求最終失敗: {url}")
                    return None
        return None
    
    def fetch_latest_books(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        抓取最新書籍 (法寶)
        
        API: GET /dharma/public/api/books/chinese
        
        Args:
            limit: 回傳數量限制
            
        Returns:
            書籍列表，每本包含 id, title, author, coverUrl, pdfUrl, publishDate, url
        """
        url = f"{self.DHARMA_BASE}/books/chinese"
        params = {
            'per_page': limit,
            'page': 1,
            # 與 LINE Bot「最新法寶」相同的排序方式
            'order': 'latest_storage_date,desc|order_by_language_category_count,asc|code,desc'
        }
        
        self.logger.info(f"正在抓取最新書籍 (limit={limit})...")
        data = self._make_request(url, params)
        
        if not data or 'data' not in data:
            self.logger.error("無法取得書籍資料")
            return []
        
        books = []
        for item in data['data'][:limit]:
            book_id = str(item.get('id', ''))
            code = item.get('code', '')
            
            # 生成封面圖 URL (移除 code 中的 - 符號)
            cover_url = self._generate_cover_url(code) if code else None
            
            # 取得 PDF 下載連結
            pdf_url = self._fetch_book_pdf_url(book_id) if book_id else None
            
            books.append({
                'id': book_id,
                'code': code,
                'title': item.get('chinese_name', item.get('name_zh', '未知書名')),
                'author': item.get('chinese_author', item.get('author_name', '未知作者')),
                'coverUrl': cover_url,
                'pdfUrl': pdf_url,
                'publishDate': item.get('latest_storage_date', item.get('storage_date', '')),
                'url': f"{self.WEBSITE_BASE}/books/{book_id}",
                'source': 'books'
            })
        
        self.logger.info(f"成功抓取 {len(books)} 本書籍")
        return books
    
    def _generate_cover_url(self, code: str) -> str:
        """
        生成書籍封面圖 URL
        
        規則：移除 code 中的 - 符號，加上 .jpg
        例：CH382-16 -> CH38216.jpg
        """
        if not code:
            return f"{self.WEBSITE_BASE}/img/logo.png"
        clean_code = code.replace('-', '')
        return f"{self.COVER_IMAGE_BASE}/{clean_code}.jpg"
    
    def _fetch_book_pdf_url(self, book_id: str) -> Optional[str]:
        """
        取得書籍 PDF 下載連結
        
        API: GET /dharma/public/api/books/{id}/efiles
        """
        url = f"{self.DHARMA_BASE}/books/{book_id}/efiles"
        params = {
            'include': 'attached',
            'order': 'name,asc'
        }
        
        data = self._make_request(url, params)
        if data and 'data' in data and len(data['data']) > 0:
            return data['data'][0].get('url')
        return None
    
    def fetch_buddha_cards(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        抓取最新佛卡
        
        API: GET /dharma/public/api/pictures
        
        Args:
            limit: 回傳數量限制
            
        Returns:
            佛卡列表，每張包含 id, code, title, imageUrl, url
        """
        url = f"{self.DHARMA_BASE}/pictures"
        params = {
            'filter[have_efile]': 1,
            'order': 'in_stock,asc|chinese_display_order,asc|latest_storage_date,desc|created_at,desc',
            'per_page': limit,
            'page': 1
        }
        
        self.logger.info(f"正在抓取最新佛卡 (limit={limit})...")
        data = self._make_request(url, params)
        
        if not data:
            self.logger.error("無法取得佛卡資料")
            return []
        
        # API 可能直接返回 array 或 { data: array }
        cards_data = data.get('data', data) if isinstance(data, dict) else data
        if not isinstance(cards_data, list):
            self.logger.error("佛卡 API 回傳格式不正確")
            return []
        
        cards = []
        for item in cards_data[:limit]:
            card_id = str(item.get('id', ''))
            code = item.get('code', '')
            
            cards.append({
                'id': card_id,
                'code': code,
                'title': item.get('chinese_name', item.get('name', '未知佛卡')),
                'imageUrl': f"{self.BUDDHA_CARD_IMAGE_BASE}/{code}.jpg" if code else None,
                'publishDate': item.get('updated_at', item.get('created_at', '')),
                'url': f"{self.WEBSITE_BASE}/pictures/{card_id}",
                'source': 'buddha_cards',
                'type': 'card'  # 標記類型以便歸類
            })
        
        self.logger.info(f"成功抓取 {len(cards)} 張佛卡")
        return cards
    
    def fetch_course_cancellations(self, days_ahead: int = 14) -> List[Dict[str, Any]]:
        """
        抓取停課通知
        
        API: GET /laravel/public/api/course-cancel-records
        
        Args:
            days_ahead: 抓取未來幾天的停課
            
        Returns:
            停課列表，每筆包含 id, courseName, cancelDate, instructor, cause, url
        """
        url = f"{self.LARAVEL_BASE}/course-cancel-records"
        today = date.today().isoformat()
        
        params = {
            'include': 'course.lecturer',
            'filter[cancel_date][gte]': today,
            'order': 'cancel_date,asc'
        }
        
        self.logger.info(f"正在抓取停課通知 (從 {today} 起)...")
        data = self._make_request(url, params)
        
        if not data or 'data' not in data:
            self.logger.error("無法取得停課資料")
            return []
        
        cancellations = []
        for item in data['data']:
            # 確保 course 和 lecturer 永遠是字典，即使 API 回傳 None
            course = item.get('course') or {}
            lecturer = course.get('lecturer') or {}
            
            cancel_date = item.get('cancel_date', '')
            # 格式化日期顯示
            formatted_date = self._format_date_display(cancel_date)
            
            cancellations.append({
                'id': str(item.get('id', '')),
                'courseName': course.get('title_name', '未知課程'),
                'cancelDate': cancel_date,
                'cancelDateDisplay': formatted_date,
                'instructor': lecturer.get('lecr_name', ''),
                'weekDay': course.get('week', ''),
                'time': self._format_course_time(course),
                'cause': item.get('cause', ''),
                'url': f"{self.WEBSITE_BASE}/bulletins/course-cancel",
                'source': 'cancellation'
            })
        
        self.logger.info(f"成功抓取 {len(cancellations)} 則停課通知")
        return cancellations
    
    def _format_course_time(self, course: Dict) -> str:
        """格式化課程時間"""
        start = course.get('spk_start_time', '')
        end = course.get('spk_end_time', '')
        if start and end:
            return f"{start} ~ {end}"
        return ''
    
    def _format_date_display(self, date_str: str) -> str:
        """格式化日期顯示 (YYYY-MM-DD -> MM/DD 週X)"""
        if not date_str:
            return ''
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            weekdays = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
            weekday = weekdays[dt.weekday()]
            return f"{dt.month}/{dt.day} ({weekday})"
        except ValueError:
            return date_str
    
    def fetch_latest_bulletins(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        抓取最新消息
        
        API: GET /laravel/public/api/bulletins
        
        Args:
            limit: 回傳數量限制
            
        Returns:
            消息列表，每則包含 id, title, content, publishDate, url
        """
        url = f"{self.LARAVEL_BASE}/bulletins"
        params = {
            'filter[publishing]': '',
            'include': 'attachments',
            'order': 'publish_start_date,desc|updated_at,desc'
        }
        
        self.logger.info(f"正在抓取最新消息 (limit={limit})...")
        data = self._make_request(url, params)
        
        if not data or 'data' not in data:
            self.logger.error("無法取得最新消息")
            return []
        
        bulletins = []
        for item in data['data'][:limit]:
            bulletin_id = str(item.get('id', ''))
            
            # 清理 HTML 內容
            content = self._strip_html_tags(item.get('content', ''))
            
            bulletins.append({
                'id': bulletin_id,
                'title': item.get('title', '未知標題'),
                'content': content[:100] + '...' if len(content) > 100 else content,
                'publishDate': item.get('publish_start_date', ''),
                'url': f"{self.WEBSITE_BASE}/bulletins/{bulletin_id}",
                'source': 'news'
            })
        
        self.logger.info(f"成功抓取 {len(bulletins)} 則最新消息")
        return bulletins
    
    def _strip_html_tags(self, html: str) -> str:
        """移除 HTML 標籤"""
        if not html:
            return ''
        import re
        # 移除 HTML 標籤
        text = re.sub(r'<[^>]+>', '', html)
        # 處理常見的 HTML 實體
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def fetch_latest_videos(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        抓取最新影音
        
        API: GET /audiovisual/public/api/series/by-keyword-searched
        
        Args:
            limit: 回傳數量限制
            
        Returns:
            影音列表，每個包含 id, title, instructor, latestDate, episodeCount, url
        """
        url = f"{self.AUDIOVISUAL_BASE}/series/by-keyword-searched"
        params = {
            'filter[ended]': 'N',
            'filter[IsDirtyEntry]': 'N',
            'order': 'latest_filedate,desc',
            'per_page': limit
        }
        
        self.logger.info(f"正在抓取最新影音 (limit={limit})...")
        data = self._make_request(url, params)
        
        if not data or 'data' not in data:
            self.logger.error("無法取得影音資料")
            return []
        
        videos = []
        for item in data['data'][:limit]:
            series_id = str(item.get('title_no', ''))
            
            videos.append({
                'id': series_id,
                'title': item.get('title_name', '未知標題'),
                'instructor': item.get('lecr_name', ''),
                'latestDate': item.get('latest_filedate', ''),
                'episodeCount': item.get('VL_nfiles', 0),
                'url': f"{self.WEBSITE_BASE}/series/{series_id}",
                'source': 'videos'
            })
        
        self.logger.info(f"成功抓取 {len(videos)} 個影音系列")
        return videos
    
    def fetch_all_sources(self, limits: Optional[Dict[str, int]] = None) -> Dict[str, List[Dict]]:
        """
        抓取所有來源的資料
        
        Args:
            limits: 各來源的數量限制，例如 {'books': 5, 'bulletins': 5}
            
        Returns:
            包含所有來源資料的字典
        """
        if limits is None:
            limits = {
                'books': 5,
                'cards': 5,  # 佛卡
                'cancellations': 10,  # 停課抓多一點
                'bulletins': 5,
                'videos': 5
            }
        
        self.logger.info("開始抓取所有資料來源...")
        
        # 抓取書籍和佛卡，合併為 new_books (歸類為書籍)
        books = self.fetch_latest_books(limits.get('books', 5))
        cards = self.fetch_buddha_cards(limits.get('cards', 5))
        
        result = {
            'new_books': books + cards,  # 佛卡歸類到書籍
            'cancellation': self.fetch_course_cancellations(),
            'news': self.fetch_latest_bulletins(limits.get('bulletins', 5)),
            'new_videos': self.fetch_latest_videos(limits.get('videos', 5)),
            'fetch_time': datetime.now().isoformat()
        }
        
        total = sum(len(v) for k, v in result.items() if isinstance(v, list))
        self.logger.info(f"資料抓取完成，共 {total} 筆")
        
        return result


# 測試用
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    fetcher = BudaeduAPIFetcher()
    
    print("=" * 60)
    print("測試 API 資料抓取")
    print("=" * 60)
    
    # 測試書籍
    print("\n📚 最新書籍:")
    books = fetcher.fetch_latest_books(3)
    for book in books:
        print(f"  - {book['title']} / {book['author']}")
    
    # 測試佛卡
    print("\n🙏 最新佛卡:")
    cards = fetcher.fetch_buddha_cards(3)
    for card in cards:
        print(f"  - {card['title']} ({card['code']})")
    
    # 測試停課
    print("\n⚠️ 停課通知:")
    cancellations = fetcher.fetch_course_cancellations()
    for cancel in cancellations[:3]:
        print(f"  - {cancel['courseName']} - {cancel['cancelDateDisplay']}")
    
    # 測試最新消息
    print("\n📰 最新消息:")
    bulletins = fetcher.fetch_latest_bulletins(3)
    for bulletin in bulletins:
        print(f"  - {bulletin['title']}")
    
    # 測試影音
    print("\n🎥 最新影音:")
    videos = fetcher.fetch_latest_videos(3)
    for video in videos:
        print(f"  - {video['title']} ({video['episodeCount']} 集)")
    
    print("\n" + "=" * 60)
    print("測試完成!")
