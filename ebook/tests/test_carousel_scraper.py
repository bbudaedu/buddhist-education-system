#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for CarouselScraper with Chrome DevTools integration
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from carousel_scraper import CarouselScraper


def setup_logging():
    """Set up logging configuration for testing"""
    log_filename = f"test_carousel_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def test_carousel_scraper_basic():
    """Test basic CarouselScraper functionality"""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("測試 CarouselScraper 基本功能")
    logger.info("=" * 60)
    
    # Configuration
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"
    
    if not os.path.exists(chromedriver_path):
        logger.error(f"ChromeDriver 不存在: {chromedriver_path}")
        return False
    
    scraper = None
    try:
        # Test initialization
        logger.info("1. 測試初始化...")
        scraper = CarouselScraper(chromedriver_path, download_dir, logger, use_chrome_devtools=True)
        logger.info("✓ CarouselScraper 初始化成功")
        
        # Test driver setup
        logger.info("2. 測試 WebDriver 設定...")
        scraper.setup_driver()
        logger.info("✓ WebDriver 設定成功")
        
        # Test Chrome DevTools setup
        logger.info("3. 測試 Chrome DevTools 設定...")
        devtools_success = scraper.setup_chrome_devtools()
        if devtools_success:
            logger.info("✓ Chrome DevTools 設定成功")
        else:
            logger.warning("⚠ Chrome DevTools 設定失敗，將使用標準模式")
        
        # Test navigation
        logger.info("4. 測試網站導航...")
        nav_success = scraper.navigate_to_website(scraper.carousel_url)
        if nav_success:
            logger.info("✓ 網站導航成功")
        else:
            logger.error("✗ 網站導航失敗")
            return False
        
        # Test page loading
        logger.info("5. 測試頁面載入...")
        load_success = scraper.wait_for_page_load()
        if load_success:
            logger.info("✓ 頁面載入成功")
        else:
            logger.warning("⚠ 頁面載入可能不完整")
        
        # Test carousel extraction
        logger.info("6. 測試輪播橫幅提取...")
        banners = scraper.extract_carousel_banners()
        
        if banners:
            logger.info(f"✓ 成功提取 {len(banners)} 個輪播橫幅")
            
            # Display results
            for i, banner in enumerate(banners):
                logger.info(f"\n橫幅 {i + 1}:")
                logger.info(f"  ID: {banner['carousel_id']}")
                logger.info(f"  標題: {banner['banner_title']}")
                logger.info(f"  圖片 URL: {banner['image_url'][:80]}...")
                logger.info(f"  課程名稱: {banner['course_name']}")
                logger.info(f"  地點: {banner['location']}")
                logger.info(f"  講師: {banner['instructor']}")
                logger.info(f"  活動連結: {banner['activity_link']}")
                if banner['description']:
                    logger.info(f"  描述: {banner['description'][:100]}...")
        else:
            logger.warning("⚠ 未找到輪播橫幅")
        
        # Test baseline functionality
        logger.info("7. 測試基準線功能...")
        baseline = scraper.get_carousel_baseline()
        logger.info(f"✓ 基準線: {baseline}")
        
        # Test baseline update
        if banners:
            update_success = scraper.update_carousel_baseline(banners[0]['carousel_id'])
            if update_success:
                logger.info("✓ 基準線更新成功")
            else:
                logger.warning("⚠ 基準線更新失敗")
        
        logger.info("\n" + "=" * 60)
        logger.info("測試完成")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}", exc_info=True)
        return False
    finally:
        if scraper:
            scraper.cleanup()
            logger.info("WebDriver 已清理")


def test_devtools_vs_standard():
    """Compare DevTools vs standard Selenium performance"""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("測試 DevTools vs 標準 Selenium 效能比較")
    logger.info("=" * 60)
    
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"
    
    if not os.path.exists(chromedriver_path):
        logger.error(f"ChromeDriver 不存在: {chromedriver_path}")
        return False
    
    scraper = None
    try:
        scraper = CarouselScraper(chromedriver_path, download_dir, logger, use_chrome_devtools=True)
        scraper.setup_driver()
        
        # Test with DevTools
        logger.info("1. 使用 Chrome DevTools 模式...")
        start_time = datetime.now()
        scraper.use_chrome_devtools = True
        scraper.setup_chrome_devtools()
        devtools_banners = scraper.extract_carousel_banners()
        devtools_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"DevTools 模式: {len(devtools_banners)} 個橫幅，耗時 {devtools_time:.2f} 秒")
        
        # Test with standard Selenium
        logger.info("2. 使用標準 Selenium 模式...")
        start_time = datetime.now()
        scraper.use_chrome_devtools = False
        standard_banners = scraper.extract_carousel_banners()
        standard_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"標準模式: {len(standard_banners)} 個橫幅，耗時 {standard_time:.2f} 秒")
        
        # Compare results
        logger.info("\n效能比較:")
        logger.info(f"DevTools 模式: {len(devtools_banners)} 橫幅，{devtools_time:.2f} 秒")
        logger.info(f"標準模式: {len(standard_banners)} 橫幅，{standard_time:.2f} 秒")
        
        if devtools_time < standard_time:
            improvement = ((standard_time - devtools_time) / standard_time) * 100
            logger.info(f"DevTools 模式快 {improvement:.1f}%")
        else:
            degradation = ((devtools_time - standard_time) / standard_time) * 100
            logger.info(f"標準模式快 {degradation:.1f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"比較測試中發生錯誤: {e}", exc_info=True)
        return False
    finally:
        if scraper:
            scraper.cleanup()


def main():
    """Run all tests"""
    print("開始 CarouselScraper 測試...")
    
    # Test basic functionality
    basic_success = test_carousel_scraper_basic()
    
    if basic_success:
        print("\n基本功能測試通過，進行效能比較...")
        # Test performance comparison
        test_devtools_vs_standard()
    else:
        print("基本功能測試失敗")
    
    print("\n所有測試完成")


if __name__ == "__main__":
    main()