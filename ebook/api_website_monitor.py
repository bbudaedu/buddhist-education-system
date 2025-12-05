#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API-based Website Monitor
基於 API 的網站監控模組

取代 Selenium 爬蟲，使用官方 API 抓取資料：
- 更快速、更穩定
- 不需要 ChromeDriver
- 支援所有 4 種資料來源
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional

# 新增的 API 模組
from api_data_fetcher import BudaeduAPIFetcher
from notification_state import NotificationState

# 沿用現有的通知元件
from unified_notification_service import UnifiedNotificationService
from line_notification_service import LineNotificationService
from email_sender import EmailSender
from config_manager import ConfigManager


class APIWebsiteMonitor:
    """
    基於 API 的網站監控器
    
    相比 WebsiteMonitor (Selenium 爬蟲版本)：
    - 不需要 ChromeDriver
    - 更快速（約 5 秒 vs 30+ 秒）
    - 更穩定（不受 DOM 變化影響）
    """
    
    def __init__(
        self, 
        config_path: str = "config.json", 
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化 API 監控器
        
        Args:
            config_path: 設定檔路徑
            logger: Logger 實例
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 初始化設定管理器
        self.config_manager = ConfigManager(config_path, self.logger)
        self.config = self.config_manager.get_config()
        
        # 初始化 API 抓取器
        self.api_fetcher = BudaeduAPIFetcher(logger=self.logger)
        
        # 初始化通知狀態管理器
        self.notification_state = NotificationState(logger=self.logger)
        
        # 初始化通知元件（延遲初始化）
        self.notification_processor = None
        self.email_sender = None
        
        # 監控統計
        self.stats = {
            'cycles_completed': 0,
            'total_notifications_sent': 0,
            'last_cycle_time': None,
            'last_cycle_duration': 0
        }
        
        # LINE 推送頻率限制 (每天限制 1 次，會收費)
        self.push_limit_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'push_limit_state.json'
        )
        self.max_daily_pushes = 1  # 每天最多推送次數
        
        self.logger.info("APIWebsiteMonitor 初始化完成")
    
    def _can_push_today(self) -> bool:
        """
        檢查今天是否還可以推送
        
        LINE 推送會收費，每天限制 1 次
        
        Returns:
            bool: True 如果可以推送
        """
        try:
            if not os.path.exists(self.push_limit_file):
                return True
            
            with open(self.push_limit_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            last_push_date = state.get('last_push_date')
            today = date.today().isoformat()
            
            if last_push_date != today:
                # 新的一天，重置計數
                return True
            
            push_count = state.get('push_count', 0)
            return push_count < self.max_daily_pushes
            
        except Exception as e:
            self.logger.warning(f"讀取推送限制狀態失敗: {e}")
            return True
    
    def _record_push(self) -> None:
        """
        記錄推送
        """
        try:
            today = date.today().isoformat()
            state = {'last_push_date': today, 'push_count': 1}
            
            if os.path.exists(self.push_limit_file):
                with open(self.push_limit_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                
                if existing.get('last_push_date') == today:
                    state['push_count'] = existing.get('push_count', 0) + 1
            
            with open(self.push_limit_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"已記錄推送：今天第 {state['push_count']} 次")
            
        except Exception as e:
            self.logger.error(f"記錄推送失敗: {e}")
    
    def _get_remaining_pushes(self) -> int:
        """
        取得今天剩餘推送次數
        """
        try:
            if not os.path.exists(self.push_limit_file):
                return self.max_daily_pushes
            
            with open(self.push_limit_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            if state.get('last_push_date') != date.today().isoformat():
                return self.max_daily_pushes
            
            return max(0, self.max_daily_pushes - state.get('push_count', 0))
            
        except Exception:
            return self.max_daily_pushes
    
    def initialize_notification_components(self) -> bool:
        """
        初始化通知元件
        
        Returns:
            bool: True if successful
        """
        try:
            monitoring_config = self.config_manager.get_website_monitoring_config()
            
            # 初始化 Email 發送器
            if monitoring_config.get('notifications', {}).get('email_enabled', False):
                self.email_sender = EmailSender(
                    config=self.config,
                    logger=self.logger
                )
                self.logger.info("EmailSender 初始化完成")
            
            # 初始化 LINE 通知服務
            line_service = LineNotificationService(
                config=self.config,
                logger=self.logger
            )
            
            # 初始化統一通知服務
            self.notification_processor = UnifiedNotificationService(
                line_service=line_service,
                email_sender=self.email_sender,
                logger=self.logger
            )
            
            self.logger.info("通知元件初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化通知元件失敗: {e}")
            return False
    
    def run_monitoring_cycle(self, send_notification: bool = True) -> Dict[str, Any]:
        """
        執行一次監控循環
        
        Args:
            send_notification: 是否發送通知
            
        Returns:
            監控結果摘要
        """
        cycle_start = datetime.now()
        self.logger.info("=" * 60)
        self.logger.info("開始 API 監控循環")
        self.logger.info("=" * 60)
        
        try:
            # 1. 抓取所有資料來源
            all_content = self.api_fetcher.fetch_all_sources()
            
            # 2. 辨識新內容
            new_content = self._detect_new_content(all_content)
            
            # 3. 記錄結果
            result = {
                'success': True,
                'cycle_time': cycle_start.isoformat(),
                'fetched': {
                    'books': len(all_content.get('new_books', [])),
                    'cancellations': len(all_content.get('cancellation', [])),
                    'news': len(all_content.get('news', [])),
                    'videos': len(all_content.get('new_videos', []))
                },
                'new_items': {
                    'books': len(new_content.get('new_books', [])),
                    'cancellations': len(new_content.get('cancellation', [])),
                    'news': len(new_content.get('news', [])),
                    'videos': len(new_content.get('new_videos', []))
                }
            }
            
            # 4. 發送通知 (檢查每日限制)
            if send_notification and self._has_new_content(new_content):
                # 檢查推送限制
                if not self._can_push_today():
                    result['notification_sent'] = False
                    result['notification_reason'] = '已達今日推送上限 (1次/天)'
                    self.logger.warning("⚠️ 已達今日 LINE 推送上限，跳過通知")
                elif not self.notification_processor:
                    self.initialize_notification_components()
                    if self.notification_processor:
                        notification_sent = self.notification_processor.send_unified_notification(new_content)
                        result['notification_sent'] = notification_sent
                        
                        if notification_sent:
                            self._mark_content_as_notified(new_content)
                            self._record_push()
                            self.stats['total_notifications_sent'] += 1
                    else:
                        result['notification_sent'] = False
                        result['notification_error'] = '通知元件未初始化'
                else:
                    notification_sent = self.notification_processor.send_unified_notification(new_content)
                    result['notification_sent'] = notification_sent
                    
                    if notification_sent:
                        self._mark_content_as_notified(new_content)
                        self._record_push()
                        self.stats['total_notifications_sent'] += 1
            else:
                result['notification_sent'] = False
                result['notification_reason'] = '無新內容或通知已停用'
            
            # 5. 更新統計
            cycle_end = datetime.now()
            cycle_duration = (cycle_end - cycle_start).total_seconds()
            
            self.stats['cycles_completed'] += 1
            self.stats['last_cycle_time'] = cycle_end.isoformat()
            self.stats['last_cycle_duration'] = cycle_duration
            
            result['duration_seconds'] = cycle_duration
            
            self.logger.info(f"監控循環完成，耗時 {cycle_duration:.1f} 秒")
            self._log_summary(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"監控循環發生錯誤: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'cycle_time': cycle_start.isoformat()
            }
    
    def _detect_new_content(self, all_content: Dict[str, List]) -> Dict[str, List]:
        """
        辨識新內容
        """
        new_content = {}
        
        # 書籍
        books = all_content.get('new_books', [])
        new_books = self.notification_state.detect_new_items(books, 'books')
        if new_books:
            new_content['new_books'] = new_books
        
        # 停課 (總是檢查)
        cancellations = all_content.get('cancellation', [])
        new_cancellations = self.notification_state.detect_new_items(cancellations, 'cancellation')
        if new_cancellations:
            new_content['cancellation'] = new_cancellations
        
        # 消息
        news = all_content.get('news', [])
        new_news = self.notification_state.detect_new_items(news, 'news')
        if new_news:
            new_content['news'] = new_news
        
        # 影音
        videos = all_content.get('new_videos', [])
        new_videos = self.notification_state.detect_new_items(videos, 'videos')
        if new_videos:
            new_content['new_videos'] = new_videos
        
        return new_content
    
    def _has_new_content(self, new_content: Dict[str, List]) -> bool:
        """
        檢查是否有新內容
        """
        return any(len(items) > 0 for items in new_content.values())
    
    def _mark_content_as_notified(self, new_content: Dict[str, List]) -> None:
        """
        標記內容為已通知
        """
        source_mapping = {
            'new_books': 'books',
            'cancellation': 'cancellation',
            'news': 'news',
            'new_videos': 'videos'
        }
        
        for content_key, source in source_mapping.items():
            items = new_content.get(content_key, [])
            if items:
                self.notification_state.mark_as_notified(items, source)
    
    def _log_summary(self, result: Dict[str, Any]) -> None:
        """
        記錄摘要
        """
        self.logger.info("-" * 40)
        self.logger.info("📊 監控結果摘要")
        self.logger.info("-" * 40)
        
        fetched = result.get('fetched', {})
        new_items = result.get('new_items', {})
        
        self.logger.info(f"📚 書籍: 抓取 {fetched.get('books', 0)} 本, 新增 {new_items.get('books', 0)} 本")
        self.logger.info(f"⚠️ 停課: 抓取 {fetched.get('cancellations', 0)} 則, 新增 {new_items.get('cancellations', 0)} 則")
        self.logger.info(f"📰 消息: 抓取 {fetched.get('news', 0)} 則, 新增 {new_items.get('news', 0)} 則")
        self.logger.info(f"🎥 影音: 抓取 {fetched.get('videos', 0)} 個, 新增 {new_items.get('videos', 0)} 個")
        
        if result.get('notification_sent'):
            self.logger.info("✅ 通知已發送")
        elif result.get('notification_reason'):
            self.logger.info(f"ℹ️ {result['notification_reason']}")
        
        self.logger.info("-" * 40)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        取得監控統計
        """
        return {
            **self.stats,
            'state_summary': self.notification_state.get_summary(),
            'remaining_pushes_today': self._get_remaining_pushes(),
            'max_daily_pushes': self.max_daily_pushes
        }
    
    def reset_notification_state(self, source: Optional[str] = None) -> None:
        """
        重置通知狀態
        
        Args:
            source: 指定來源，None 表示重置全部
        """
        self.notification_state.reset(source)
        self.logger.info(f"通知狀態已重置: {source or '全部'}")


# 獨立測試
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("API 監控器測試")
    print("=" * 60)
    
    # 初始化監控器（不發送真正的通知）
    monitor = APIWebsiteMonitor()
    
    # 執行監控循環（不發送通知）
    result = monitor.run_monitoring_cycle(send_notification=False)
    
    print("\n📊 測試結果:")
    print(f"  成功: {result.get('success')}")
    print(f"  耗時: {result.get('duration_seconds', 0):.1f} 秒")
    
    print("\n📈 統計資料:")
    stats = monitor.get_stats()
    print(f"  已完成循環: {stats['cycles_completed']}")
    print(f"  已知書籍: {stats['state_summary']['known_book_count']}")
    print(f"  已知消息: {stats['state_summary']['known_bulletin_count']}")
    
    print("\n" + "=" * 60)
    print("測試完成!")
