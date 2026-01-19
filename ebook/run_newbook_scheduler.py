#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
New Book Scheduler - Headless Execution Script
新書排程檢查腳本 (無 GUI)

This script is designed to be called by schedulers (Node.js cron, Windows Task Scheduler)
to check for new books and automatically trigger processing if new books are found.

Usage:
    python run_newbook_scheduler.py                 # Check and process new books
    python run_newbook_scheduler.py --check-only    # Only check, don't process
    python run_newbook_scheduler.py --verbose       # Enable verbose logging
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ensure the ebook directory is in the path
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

from api_data_fetcher import BudaeduAPIFetcher
from config_manager import ConfigManager
from main_processor import MainProcessor

# Configuration file path
CONFIG_FILE = SCRIPT_DIR / "config.json"


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging for scheduler execution"""
    log_dir = SCRIPT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"newbook_scheduler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def load_config(logger: logging.Logger) -> Dict[str, Any]:
    """
    Load configuration from config.json or environment variables
    
    Priority: config.json > environment variables > defaults
    If config.json doesn't exist, uses pure environment variable mode via SharedConfig
    """
    # Try to load from config.json first
    if CONFIG_FILE.exists():
        config_manager = ConfigManager(str(CONFIG_FILE), logger)
        config = config_manager.load_config()
        config['config_path'] = str(CONFIG_FILE)  # Store path for later use
        logger.info(f"配置已從 config.json 載入: {CONFIG_FILE}")
        return config
    
    # Fallback to environment variables via SharedConfig
    logger.info("config.json 不存在，使用環境變數模式")
    
    try:
        from shared_config import SharedConfig
        shared = SharedConfig()
        
        # Build config dict from environment variables
        config = {
            'gemini_api_key': shared.gemini_api_key,
            'chromedriver_path': shared.chromedriver_path,
            'target_url': shared.target_url,
            'download_dir': shared.download_dir,
            'baseline_book_title': shared.baseline_book_title,
            'smtp_server': shared.smtp_server,
            'smtp_port': shared.smtp_port,
            'smtp_username': shared.smtp_username,
            'smtp_password': shared.smtp_password,
            'email_recipients': shared.email_recipients,
            'website_monitoring': {
                'notifications': {
                    'line_enabled': shared.line_enabled,
                    'email_enabled': shared.email_enabled,
                    'line_push_enabled': shared.line_push_enabled,
                }
            }
        }
        
        # Validate required fields
        if not config.get('gemini_api_key'):
            logger.warning("⚠️ GEMINI_API_KEY 環境變數未設定")
        
        logger.info("✅ 環境變數配置載入成功")
        return config
        
    except Exception as e:
        logger.error(f"載入環境變數配置失敗: {e}")
        raise


def check_for_new_books(
    fetcher: BudaeduAPIFetcher,
    baseline_title: str,
    logger: logging.Logger,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Check if there are new books compared to baseline
    
    Args:
        fetcher: API fetcher instance
        baseline_title: The baseline book title to compare against
        logger: Logger instance
        limit: Number of books to fetch
        
    Returns:
        Dict containing:
            - has_new_books: bool
            - new_books: list of new book dicts
            - latest_title: the newest book title
    """
    logger.info(f"正在檢查新書 (基準書籍: {baseline_title or '無'})...")
    
    # Fetch latest books
    books = fetcher.fetch_latest_books(limit=limit)
    
    if not books:
        logger.warning("無法取得書籍列表")
        return {
            'has_new_books': False,
            'new_books': [],
            'latest_title': None,
            'error': '無法取得書籍列表'
        }
    
    logger.info(f"成功取得 {len(books)} 本書籍")
    
    # If no baseline set, all books are considered "new" but we just set the baseline
    if not baseline_title:
        logger.info("未設定基準書籍，將以第一本書作為基準")
        return {
            'has_new_books': False,
            'new_books': [],
            'latest_title': books[0]['title'] if books else None,
            'is_first_run': True
        }
    
    # Find new books (books newer than baseline)
    new_books = []
    for book in books:
        current_title = book['title']
        current_code = book.get('code', '')
        
        # Construct composite title (Title + Code) to match legacy scraper format
        composite_title = f"{current_title} {current_code}".strip()
        
        # Match using multiple strategies
        is_match = False
        
        # 1. Exact title match
        if current_title == baseline_title:
            is_match = True
        
        # 2. Composite title match (Title + Code) - this is likely what matched the baseline
        elif composite_title == baseline_title:
            is_match = True
            
        # 3. Baseline starts with current title (handle potential extra spaces or suffixes)
        elif baseline_title.startswith(current_title) and (not current_code or current_code in baseline_title):
            is_match = True
            
        if is_match:
            # Found the baseline, all previous books are new
            logger.info(f"找到基準書籍: {current_title} (原始基準: {baseline_title})")
            break
            
        new_books.append(book)
    
    has_new_books = len(new_books) > 0
    latest_title = books[0]['title'] if books else None
    
    if has_new_books:
        logger.info(f"🎉 發現 {len(new_books)} 本新書！")
        for i, book in enumerate(new_books, 1):
            logger.info(f"  {i}. {book['title']} / {book.get('author', '未知作者')}")
    else:
        logger.info("✓ 沒有新書")
    
    return {
        'has_new_books': has_new_books,
        'new_books': new_books,
        'latest_title': latest_title
    }


def process_new_books(config: Dict[str, Any], api_books: List[Dict[str, Any]], logger: logging.Logger) -> Dict[str, Any]:
    """
    Execute the full new book processing workflow using MainProcessor with API data
    
    API-first approach: Uses book data from API directly instead of web scraping
    
    Args:
        config: Configuration dictionary
        api_books: List of book dicts from API (contains pdfUrl, title, author, etc.)
        logger: Logger instance
        
    Returns:
        Dict containing processing results
    """
    logger.info("=" * 60)
    logger.info("開始執行 API 模式新書處理流程")
    logger.info(f"待處理書籍: {len(api_books)} 本")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    try:
        # Initialize MainProcessor
        processor = MainProcessor(config, logger)
        
        # Run the API-based processing workflow
        success = processor.run_with_api_data(api_books)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        result = {
            'success': success,
            'execution_time_seconds': execution_time,
            'timestamp': datetime.now().isoformat(),
            'message': '處理完成' if success else '處理失敗',
            'mode': 'api_first'
        }
        
        if success:
            logger.info(f"✅ 處理完成，耗時 {execution_time:.2f} 秒")
        else:
            logger.error(f"❌ 處理失敗，耗時 {execution_time:.2f} 秒")
        
        return result
        
    except Exception as e:
        logger.error(f"處理過程發生錯誤: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def write_output(result: Dict[str, Any], logger: logging.Logger) -> str:
    """Write output JSON for Node.js integration"""
    output_dir = SCRIPT_DIR / "generated_documents"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"newbook_scheduler_result_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    logger.info(f"結果已寫入: {output_file}")
    return str(output_file)


def main():
    """Main entry point for the new book scheduler"""
    parser = argparse.ArgumentParser(
        description='新書排程檢查與處理腳本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python run_newbook_scheduler.py                 # 檢查並處理新書
  python run_newbook_scheduler.py --check-only    # 僅檢查不處理
  python run_newbook_scheduler.py --verbose       # 詳細日誌
        """
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='僅檢查新書，不執行處理'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='啟用詳細日誌輸出'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='檢查書籍數量上限 (預設: 10)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    logger.info("=" * 80)
    logger.info("新書排程檢查開始")
    logger.info(f"啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"模式: {'僅檢查' if args.check_only else '檢查並處理'}")
    logger.info("=" * 80)
    
    try:
        # Load configuration
        config = load_config(logger)
        baseline_title = config.get('baseline_book_title', '')
        
        # Initialize API fetcher
        fetcher = BudaeduAPIFetcher(logger=logger)
        
        # Check for new books
        check_result = check_for_new_books(
            fetcher=fetcher,
            baseline_title=baseline_title,
            logger=logger,
            limit=args.limit
        )
        
        # Prepare final result
        final_result = {
            'check_time': datetime.now().isoformat(),
            'baseline_title': baseline_title,
            'latest_title': check_result.get('latest_title'),
            'has_new_books': check_result.get('has_new_books', False),
            'new_books_count': len(check_result.get('new_books', [])),
            'new_books': check_result.get('new_books', []),
            'mode': 'check_only' if args.check_only else 'full_process'
        }
        
        # If check-only mode, just output results
        if args.check_only:
            final_result['action'] = 'check_only'
            final_result['success'] = True
            output_path = write_output(final_result, logger)
            
            # Print JSON to stdout for easy parsing
            print("\n--- JSON OUTPUT ---")
            print(json.dumps(final_result, ensure_ascii=False, indent=2))
            
            logger.info("=" * 80)
            logger.info("檢查完成")
            logger.info("=" * 80)
            
            return 0
        
        # If new books found and not check-only, process them using API data
        if check_result.get('has_new_books'):
            api_books = check_result.get('new_books', [])
            process_result = process_new_books(config, api_books, logger)
            final_result['processing'] = process_result
            final_result['action'] = 'processed'
            final_result['success'] = process_result.get('success', False)
        else:
            final_result['action'] = 'no_action_needed'
            final_result['success'] = True
            logger.info("沒有新書需要處理")
        
        # Handle first run (no baseline set)
        if check_result.get('is_first_run'):
            final_result['action'] = 'baseline_initialized'
            final_result['message'] = '首次執行，已設定基準書籍'
            
            # Update baseline in config
            if check_result.get('latest_title'):
                config_manager = ConfigManager(str(CONFIG_FILE), logger)
                config_manager.update_baseline_book_title(check_result['latest_title'])
                logger.info(f"已更新基準書籍: {check_result['latest_title']}")
        
        # Write output
        output_path = write_output(final_result, logger)
        final_result['output_file'] = output_path
        
        # Print JSON to stdout
        print("\n--- JSON OUTPUT ---")
        print(json.dumps(final_result, ensure_ascii=False, indent=2))
        
        logger.info("=" * 80)
        logger.info("排程執行完成")
        logger.info("=" * 80)
        
        return 0 if final_result.get('success') else 1
        
    except Exception as e:
        logger.error(f"💥 排程執行發生錯誤: {e}", exc_info=True)
        
        error_result = {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        write_output(error_result, logger)
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
