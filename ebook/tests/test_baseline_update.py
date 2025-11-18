#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for baseline book title update functionality
測試基準書籍標題自動更新功能
"""

import os
import json
import logging
import tempfile
import shutil
from config_manager import ConfigManager


def setup_test_logging():
    """Set up logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def create_test_config(temp_dir):
    """Create a test configuration file"""
    test_config = {
        "gemini_api_key": "test-api-key",
        "chromedriver_path": "chromedriver-win64\\chromedriver.exe",
        "target_url": "https://www.budaedu.org/#/books/applicable/chinese",
        "baseline_book_title": "CH738-17",
        "download_dir": "downloads",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_username": "test@example.com",
        "smtp_password": "test-password",
        "email_recipients": "test1@example.com,test2@example.com",
        "last_run_date": ""
    }
    
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)
    
    return config_path


def test_config_manager_basic_operations():
    """Test basic ConfigManager operations"""
    logger = setup_test_logging()
    logger.info("=== 測試 ConfigManager 基本操作 ===")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test config file
        config_path = create_test_config(temp_dir)
        logger.info(f"測試配置檔案已建立: {config_path}")
        
        # Test ConfigManager initialization
        config_manager = ConfigManager(config_path, logger)
        
        # Test getting current baseline
        current_baseline = config_manager.get_baseline_book_title()
        logger.info(f"當前基準書籍標題: {current_baseline}")
        assert current_baseline == "CH738-17", f"Expected 'CH738-17', got '{current_baseline}'"
        
        # Test updating baseline
        new_baseline = "CH739-01"
        success = config_manager.update_baseline_book_title(new_baseline)
        assert success, "基準書籍標題更新失敗"
        
        # Verify update
        updated_baseline = config_manager.get_baseline_book_title()
        logger.info(f"更新後的基準書籍標題: {updated_baseline}")
        assert updated_baseline == new_baseline, f"Expected '{new_baseline}', got '{updated_baseline}'"
        
        # Test that last_run_date was updated
        last_run_date = config_manager.get_last_run_date()
        assert last_run_date is not None, "last_run_date 應該已更新"
        logger.info(f"最後執行時間: {last_run_date}")
        
        # Test configuration validation
        is_valid = config_manager.validate_config()
        assert is_valid, "配置驗證應該通過"
        
        logger.info("✓ ConfigManager 基本操作測試通過")


def test_config_manager_edge_cases():
    """Test ConfigManager edge cases"""
    logger = setup_test_logging()
    logger.info("=== 測試 ConfigManager 邊界情況 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config(temp_dir)
        config_manager = ConfigManager(config_path, logger)
        
        # Test empty baseline update
        success = config_manager.update_baseline_book_title("")
        assert not success, "空字串更新應該失敗"
        
        # Test whitespace-only baseline update
        success = config_manager.update_baseline_book_title("   ")
        assert not success, "純空白字串更新應該失敗"
        
        # Test None baseline update
        success = config_manager.update_baseline_book_title(None)
        assert not success, "None 更新應該失敗"
        
        # Test very long baseline title
        long_title = "A" * 1000
        success = config_manager.update_baseline_book_title(long_title)
        assert success, "長標題更新應該成功"
        
        updated_baseline = config_manager.get_baseline_book_title()
        assert updated_baseline == long_title, "長標題應該正確儲存"
        
        logger.info("✓ ConfigManager 邊界情況測試通過")


def test_config_backup_functionality():
    """Test configuration backup functionality"""
    logger = setup_test_logging()
    logger.info("=== 測試配置備份功能 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config(temp_dir)
        config_manager = ConfigManager(config_path, logger)
        
        # Update baseline to trigger backup
        success = config_manager.update_baseline_book_title("CH740-01")
        assert success, "基準書籍標題更新應該成功"
        
        # Check if backup file was created
        backup_files = [f for f in os.listdir(temp_dir) if f.startswith("config.json.backup_")]
        assert len(backup_files) > 0, "應該建立備份檔案"
        
        backup_path = os.path.join(temp_dir, backup_files[0])
        logger.info(f"備份檔案已建立: {backup_path}")
        
        # Verify backup contains original content
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_config = json.load(f)
        
        assert backup_config['baseline_book_title'] == "CH738-17", "備份應該包含原始基準標題"
        
        logger.info("✓ 配置備份功能測試通過")


def test_integration_with_main_processor():
    """Test integration scenario similar to MainProcessor usage"""
    logger = setup_test_logging()
    logger.info("=== 測試與 MainProcessor 整合情境 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config(temp_dir)
        config_manager = ConfigManager(config_path, logger)
        
        # Simulate processed books from MainProcessor
        processed_books = [
            {
                'title': 'CH739-01 新書標題一',
                'processing_success': True,
                'summary': '這是第一本書的摘要'
            },
            {
                'title': 'CH739-02 新書標題二',
                'processing_success': True,
                'summary': '這是第二本書的摘要'
            },
            {
                'title': 'CH739-03 新書標題三',
                'processing_success': False,  # This one failed
                'error_message': '處理失敗'
            }
        ]
        
        # Find first successful book (simulating MainProcessor logic)
        successful_books = [
            book for book in processed_books 
            if book.get('processing_success', False) and book.get('title')
        ]
        
        if successful_books:
            new_baseline_title = successful_books[0]['title']
            success = config_manager.update_baseline_book_title(new_baseline_title)
            assert success, "整合情境下的基準更新應該成功"
            
            # Verify the update
            updated_baseline = config_manager.get_baseline_book_title()
            assert updated_baseline == new_baseline_title, "基準標題應該正確更新"
            
            logger.info(f"整合測試成功，新基準: {updated_baseline}")
        
        logger.info("✓ MainProcessor 整合情境測試通過")


def test_config_file_error_handling():
    """Test error handling for config file operations"""
    logger = setup_test_logging()
    logger.info("=== 測試配置檔案錯誤處理 ===")
    
    # Test with non-existent config file
    try:
        config_manager = ConfigManager("non_existent_config.json", logger)
        assert False, "應該拋出 FileNotFoundError"
    except FileNotFoundError:
        logger.info("✓ 不存在的配置檔案正確拋出 FileNotFoundError")
    
    # Test with invalid JSON
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_config_path = os.path.join(temp_dir, "invalid_config.json")
        with open(invalid_config_path, 'w', encoding='utf-8') as f:
            f.write("{ invalid json content")
        
        try:
            config_manager = ConfigManager(invalid_config_path, logger)
            assert False, "應該拋出 JSONDecodeError"
        except json.JSONDecodeError:
            logger.info("✓ 無效 JSON 配置檔案正確拋出 JSONDecodeError")
    
    logger.info("✓ 配置檔案錯誤處理測試通過")


def run_all_tests():
    """Run all tests"""
    logger = setup_test_logging()
    logger.info("開始執行 baseline_book_title 自動更新功能測試")
    logger.info("=" * 60)
    
    try:
        test_config_manager_basic_operations()
        test_config_manager_edge_cases()
        test_config_backup_functionality()
        test_integration_with_main_processor()
        test_config_file_error_handling()
        
        logger.info("=" * 60)
        logger.info("🎉 所有測試通過！baseline_book_title 自動更新功能正常運作")
        return True
        
    except AssertionError as e:
        logger.error(f"❌ 測試失敗: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 測試執行錯誤: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)