#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification State Manager
通知狀態管理模組

管理已發送通知的狀態，用於：
1. 辨識新內容 (避免重複通知)
2. 追蹤上次檢查時間
3. 持久化儲存已知 ID
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Set, Any, Optional
from pathlib import Path


class NotificationState:
    """
    通知狀態管理器
    
    基於日期 + ID 的混合辨識策略：
    - 書籍/影音：比較 publish_date > last_check AND id NOT IN known_ids
    - 停課：比較 cancel_date >= today (總是檢查近期停課)
    - 消息：比較 publish_date > last_check
    """
    
    DEFAULT_STATE_FILE = "notification_state.json"
    
    def __init__(
        self, 
        state_file: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化狀態管理器
        
        Args:
            state_file: 狀態檔案路徑，預設為 ebook/notification_state.json
            logger: Logger 實例
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 狀態檔案路徑
        if state_file:
            self.state_file = Path(state_file)
        else:
            # 預設在 ebook 目錄下
            self.state_file = Path(__file__).parent / self.DEFAULT_STATE_FILE
        
        # 初始化狀態
        self.state: Dict[str, Any] = {
            'last_check': None,
            'known_book_ids': [],
            'known_bulletin_ids': [],
            'known_video_ids': [],
            'last_cancellation_check': None
        }
        
        # 載入現有狀態
        self._load_state()
    
    def _load_state(self) -> None:
        """從檔案載入狀態"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.state.update(loaded)
                self.logger.info(f"已載入通知狀態: {self.state_file}")
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"無法載入狀態檔案，使用預設值: {e}")
        else:
            self.logger.info("狀態檔案不存在，將建立新檔案")
    
    def _save_state(self) -> None:
        """儲存狀態到檔案"""
        try:
            # 確保目錄存在
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"已儲存通知狀態: {self.state_file}")
        except IOError as e:
            self.logger.error(f"無法儲存狀態檔案: {e}")
    
    @property
    def last_check(self) -> Optional[datetime]:
        """上次檢查時間"""
        if self.state['last_check']:
            try:
                return datetime.fromisoformat(self.state['last_check'])
            except ValueError:
                return None
        return None
    
    @property
    def known_book_ids(self) -> Set[str]:
        """已知書籍 ID 集合"""
        return set(self.state.get('known_book_ids', []))
    
    @property
    def known_bulletin_ids(self) -> Set[str]:
        """已知消息 ID 集合"""
        return set(self.state.get('known_bulletin_ids', []))
    
    @property
    def known_video_ids(self) -> Set[str]:
        """已知影音 ID 集合"""
        return set(self.state.get('known_video_ids', []))
    
    def detect_new_items(
        self, 
        items: List[Dict[str, Any]], 
        source: str
    ) -> List[Dict[str, Any]]:
        """
        辨識新項目
        
        Args:
            items: 從 API 抓取的項目列表
            source: 來源類型 ('books', 'cancellation', 'news', 'videos')
            
        Returns:
            新項目列表 (尚未通知過的)
        """
        if not items:
            return []
        
        if source == 'cancellation':
            # 停課：只檢查日期 (未來的停課都要通知)
            return self._detect_new_cancellations(items)
        
        elif source == 'books' or source == 'new_books':
            return self._detect_new_by_id(items, self.known_book_ids)
        
        elif source == 'news':
            return self._detect_new_by_id(items, self.known_bulletin_ids)
        
        elif source == 'videos' or source == 'new_videos':
            return self._detect_new_by_id(items, self.known_video_ids)
        
        else:
            self.logger.warning(f"未知的來源類型: {source}")
            return items
    
    def _detect_new_by_id(
        self, 
        items: List[Dict], 
        known_ids: Set[str]
    ) -> List[Dict]:
        """基於 ID 辨識新項目"""
        new_items = []
        for item in items:
            item_id = str(item.get('id', ''))
            if item_id and item_id not in known_ids:
                new_items.append(item)
        
        self.logger.info(f"辨識到 {len(new_items)} 個新項目 (共 {len(items)} 個)")
        return new_items
    
    def _detect_new_cancellations(self, items: List[Dict]) -> List[Dict]:
        """
        辨識新停課通知
        
        停課的邏輯不同：
        - 只要是未來的停課日期，都應該通知
        - 不需要追蹤已發送的停課 (停課日期每天可能更新)
        """
        today = date.today()
        future_cancellations = []
        
        for item in items:
            cancel_date_str = item.get('cancelDate', item.get('cancel_date', ''))
            if cancel_date_str:
                try:
                    cancel_date = datetime.strptime(cancel_date_str, '%Y-%m-%d').date()
                    if cancel_date >= today:
                        future_cancellations.append(item)
                except ValueError:
                    # 日期格式錯誤，仍然包含
                    future_cancellations.append(item)
        
        self.logger.info(f"辨識到 {len(future_cancellations)} 則未來停課")
        return future_cancellations
    
    def mark_as_notified(
        self, 
        items: List[Dict[str, Any]], 
        source: str
    ) -> None:
        """
        標記項目為已通知
        
        Args:
            items: 已發送通知的項目列表
            source: 來源類型
        """
        if not items:
            return
        
        # 提取 ID
        item_ids = [str(item.get('id', '')) for item in items if item.get('id')]
        
        if source == 'books' or source == 'new_books':
            current_ids = set(self.state.get('known_book_ids', []))
            current_ids.update(item_ids)
            # 只保留最近 500 個 ID (避免檔案過大)
            self.state['known_book_ids'] = list(current_ids)[-500:]
            
        elif source == 'news':
            current_ids = set(self.state.get('known_bulletin_ids', []))
            current_ids.update(item_ids)
            self.state['known_bulletin_ids'] = list(current_ids)[-500:]
            
        elif source == 'videos' or source == 'new_videos':
            current_ids = set(self.state.get('known_video_ids', []))
            current_ids.update(item_ids)
            self.state['known_video_ids'] = list(current_ids)[-500:]
        
        # 更新檢查時間
        self.state['last_check'] = datetime.now().isoformat()
        
        # 儲存狀態
        self._save_state()
        self.logger.info(f"已標記 {len(item_ids)} 個 {source} 項目為已通知")
    
    def update_check_time(self) -> None:
        """更新上次檢查時間"""
        self.state['last_check'] = datetime.now().isoformat()
        self._save_state()
    
    def get_summary(self) -> Dict[str, Any]:
        """取得狀態摘要"""
        return {
            'last_check': self.state.get('last_check'),
            'known_book_count': len(self.state.get('known_book_ids', [])),
            'known_bulletin_count': len(self.state.get('known_bulletin_ids', [])),
            'known_video_count': len(self.state.get('known_video_ids', [])),
            'state_file': str(self.state_file)
        }
    
    def reset(self, source: Optional[str] = None) -> None:
        """
        重置狀態
        
        Args:
            source: 指定來源，None 表示重置全部
        """
        if source is None:
            self.state = {
                'last_check': None,
                'known_book_ids': [],
                'known_bulletin_ids': [],
                'known_video_ids': [],
                'last_cancellation_check': None
            }
            self.logger.info("已重置所有通知狀態")
        elif source == 'books':
            self.state['known_book_ids'] = []
            self.logger.info("已重置書籍通知狀態")
        elif source == 'news':
            self.state['known_bulletin_ids'] = []
            self.logger.info("已重置消息通知狀態")
        elif source == 'videos':
            self.state['known_video_ids'] = []
            self.logger.info("已重置影音通知狀態")
        
        self._save_state()


# 測試用
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 使用臨時檔案測試
    import tempfile
    temp_file = os.path.join(tempfile.gettempdir(), "test_notification_state.json")
    
    print("=" * 60)
    print("測試通知狀態管理")
    print("=" * 60)
    
    state = NotificationState(state_file=temp_file)
    
    # 模擬書籍資料
    mock_books = [
        {'id': '12345', 'title': '阿彌陀經講義'},
        {'id': '12346', 'title': '華嚴經疏'},
        {'id': '12347', 'title': '金剛經淺說'},
    ]
    
    print("\n📚 第一次檢查書籍:")
    new_books = state.detect_new_items(mock_books, 'books')
    print(f"  新書數量: {len(new_books)}")
    
    # 標記為已通知
    state.mark_as_notified(new_books, 'books')
    
    print("\n📚 第二次檢查書籍 (相同資料):")
    new_books = state.detect_new_items(mock_books, 'books')
    print(f"  新書數量: {len(new_books)}")
    
    # 新增一本書
    mock_books.append({'id': '12348', 'title': '法華經講記'})
    
    print("\n📚 第三次檢查書籍 (新增一本):")
    new_books = state.detect_new_items(mock_books, 'books')
    print(f"  新書數量: {len(new_books)}")
    for book in new_books:
        print(f"    - {book['title']}")
    
    # 顯示狀態摘要
    print("\n📊 狀態摘要:")
    summary = state.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # 清理測試檔案
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    print("\n" + "=" * 60)
    print("測試完成!")
