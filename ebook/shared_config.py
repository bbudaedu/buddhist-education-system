#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared Configuration Module - 共享配置模組
統一管理 Python 與 Node.js 共用的配置變數

優先級: 環境變數 > JSON 配置檔 > 預設值

支援從 Line-bot-llm-mysql/.env 自動載入環境變數
"""

import os
import logging
from typing import Any, Optional
from pathlib import Path

# 嘗試載入 python-dotenv（可選）
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)


def _load_env_file():
    """嘗試從 .env 檔案載入環境變數"""
    if not DOTENV_AVAILABLE:
        return
    
    # 嘗試多個可能的 .env 位置
    possible_paths = [
        Path(__file__).parent.parent / 'Line-bot-llm-mysql' / '.env',
        Path(__file__).parent / '.env',
        Path.cwd() / '.env',
        Path.cwd() / 'Line-bot-llm-mysql' / '.env',
    ]
    
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"已從 {env_path} 載入環境變數")
            return
    
    logger.debug("未找到 .env 檔案，使用系統環境變數")


# 初始化時自動載入 .env
_load_env_file()


def get_env(key: str, default: Any = None, cast_type: type = str) -> Any:
    """
    從環境變數獲取配置值
    
    Args:
        key: 環境變數名稱
        default: 預設值
        cast_type: 類型轉換 (str, int, bool, float)
    
    Returns:
        配置值
    """
    value = os.environ.get(key)
    
    if value is None:
        return default
    
    # 類型轉換
    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == int:
        try:
            return int(value)
        except ValueError:
            return default
    elif cast_type == float:
        try:
            return float(value)
        except ValueError:
            return default
    
    return value


def get_with_fallback(
    env_key: str,
    json_value: Any,
    default: Any = None,
    cast_type: type = str
) -> Any:
    """
    優先從環境變數獲取，fallback 到 JSON 配置值
    
    優先級: 環境變數 > JSON 配置 > 預設值
    
    Args:
        env_key: 環境變數名稱
        json_value: JSON 配置中的值
        default: 預設值
        cast_type: 類型轉換
    
    Returns:
        配置值
    """
    # 先嘗試環境變數
    env_value = os.environ.get(env_key)
    
    if env_value is not None:
        # 環境變數存在，進行類型轉換
        if cast_type == bool:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        elif cast_type == int:
            try:
                return int(env_value)
            except ValueError:
                pass
        elif cast_type == float:
            try:
                return float(env_value)
            except ValueError:
                pass
        else:
            return env_value
    
    # 環境變數不存在，使用 JSON 配置
    if json_value is not None:
        return json_value
    
    # 最後使用預設值
    return default


# ========== 共享配置項目 ==========

class SharedConfig:
    """共享配置類別 - 提供統一的配置存取介面"""
    
    def __init__(self, json_config: dict = None):
        """
        初始化共享配置
        
        Args:
            json_config: 可選的 JSON 配置字典
        """
        self._json_config = json_config or {}
    
    @property
    def gemini_api_key(self) -> str:
        """Gemini API 金鑰"""
        return get_with_fallback(
            'GEMINI_API_KEY',
            self._json_config.get('gemini_api_key'),
            ''
        )
    
    @property
    def smtp_server(self) -> str:
        """SMTP 伺服器"""
        return get_with_fallback(
            'SMTP_SERVER',
            self._json_config.get('smtp_server'),
            'smtp.gmail.com'
        )
    
    @property
    def smtp_port(self) -> int:
        """SMTP 埠號"""
        return get_with_fallback(
            'SMTP_PORT',
            self._json_config.get('smtp_port'),
            587,
            cast_type=int
        )
    
    @property
    def smtp_username(self) -> str:
        """SMTP 使用者名稱"""
        return get_with_fallback(
            'SMTP_USERNAME',
            self._json_config.get('smtp_username'),
            ''
        )
    
    @property
    def smtp_password(self) -> str:
        """SMTP 密碼"""
        return get_with_fallback(
            'SMTP_PASSWORD',
            self._json_config.get('smtp_password'),
            ''
        )
    
    @property
    def email_recipients(self) -> str:
        """Email 收件人 (逗號分隔)"""
        return get_with_fallback(
            'EMAIL_RECIPIENTS',
            self._json_config.get('email_recipients'),
            ''
        )
    
    @property
    def chromedriver_path(self) -> str:
        """ChromeDriver 路徑"""
        return get_with_fallback(
            'CHROMEDRIVER_PATH',
            self._json_config.get('chromedriver_path'),
            'chromedriver-win64/chromedriver.exe'
        )
    
    @property
    def download_dir(self) -> str:
        """下載目錄"""
        return get_with_fallback(
            'DOWNLOAD_DIR',
            self._json_config.get('download_dir'),
            'downloads'
        )
    
    @property
    def target_url(self) -> str:
        """目標網站 URL"""
        return get_with_fallback(
            'TARGET_URL',
            self._json_config.get('target_url'),
            'https://www.budaedu.org'
        )
    
    @property
    def baseline_book_title(self) -> str:
        """基準書籍標題"""
        return get_with_fallback(
            'BASELINE_BOOK_TITLE',
            self._json_config.get('baseline_book_title'),
            ''
        )
    
    @property
    def line_push_enabled(self) -> bool:
        """LINE 推播開關 (成本控制)"""
        # 從 monitoring_config 讀取
        notifications = self._json_config.get('website_monitoring', {}).get('notifications', {})
        return get_with_fallback(
            'LINE_PUSH_ENABLED',
            notifications.get('line_push_enabled'),
            False,
            cast_type=bool
        )
    
    @property
    def line_enabled(self) -> bool:
        """LINE 通知開關"""
        notifications = self._json_config.get('website_monitoring', {}).get('notifications', {})
        return get_with_fallback(
            'NOTIFICATION_LINE_ENABLED',
            notifications.get('line_enabled'),
            False,
            cast_type=bool
        )
    
    @property
    def email_enabled(self) -> bool:
        """Email 通知開關"""
        notifications = self._json_config.get('website_monitoring', {}).get('notifications', {})
        return get_with_fallback(
            'NOTIFICATION_EMAIL_ENABLED',
            notifications.get('email_enabled'),
            True,
            cast_type=bool
        )
    
    def to_dict(self) -> dict:
        """匯出為字典格式"""
        return {
            'gemini_api_key': self.gemini_api_key,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'smtp_username': self.smtp_username,
            'smtp_password': self.smtp_password,
            'email_recipients': self.email_recipients,
            'chromedriver_path': self.chromedriver_path,
            'download_dir': self.download_dir,
            'target_url': self.target_url,
            'baseline_book_title': self.baseline_book_title,
            'line_push_enabled': self.line_push_enabled,
            'line_enabled': self.line_enabled,
            'email_enabled': self.email_enabled,
        }


# 全域共享配置實例 (延遲初始化)
_shared_config: Optional[SharedConfig] = None


def get_shared_config(json_config: dict = None) -> SharedConfig:
    """
    獲取共享配置實例
    
    Args:
        json_config: 可選的 JSON 配置字典
    
    Returns:
        SharedConfig 實例
    """
    global _shared_config
    
    if _shared_config is None or json_config is not None:
        _shared_config = SharedConfig(json_config)
    
    return _shared_config
