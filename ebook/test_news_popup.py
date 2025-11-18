#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新聞彈窗內容提取
"""

import os
import sys
import logging
import time
from datetime import datetime
from book_scraper import BookScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


def setup_logging():
    """設定日誌"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


def extract_popup_content(driver, logger):
    """提取彈窗內容 - 基於實際 DOM 結構"""
    try:
        logger.info("等待彈窗出現...")
        
        # 等待 modal-body 出現
        modal_body = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-body"))
        )
        logger.info("✓ 找到彈窗內容區域 (.modal-body)")
        
        # 等待內容完全載入
        time.sleep(2)
        
        # 提取標題
        title = ""
        try:
            title_element = modal_body.find_element(By.TAG_NAME, "h5")
            title = title_element.text.strip()
            logger.info(f"✓ 提取到標題: {title}")
        except Exception as e:
            logger.debug(f"提取標題失敗: {e}")
        
        # 提取內容
        content = ""
        try:
            # 提取所有 p 標籤的內容
            paragraphs = modal_body.find_elements(By.TAG_NAME, "p")
            if paragraphs:
                content_parts = []
                for p in paragraphs:
                    text = p.text.strip()
                    if text:
                        content_parts.append(text)
                content = '\n\n'.join(content_parts)
                logger.info(f"✓ 從 {len(paragraphs)} 個段落提取內容")
            
            # 如果沒有 p 標籤，獲取完整文字
            if not content:
                full_text = modal_body.text.strip()
                if title:
                    full_text = full_text.replace(title, "", 1)
                if "分享：" in full_text:
                    full_text = full_text.split("分享：")[0]
                content = full_text.strip()
            
            # 清理 "分享：" 及其後的內容
            if "分享：" in content:
                content = content.split("分享：")[0].strip()
            
            # 清理多餘的空白
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
            
            logger.info(f"✓ 清理後內容長度: {len(content)} 字元")
            
        except Exception as e:
            logger.warning(f"提取內容失敗: {e}")
        
        return {
            "title": title,
            "content": content,
            "success": len(content) > 0
        }
        
    except Exception as e:
        logger.error(f"提取彈窗內容失敗: {e}", exc_info=True)
        return None


def close_popup(driver, logger):
    """關閉彈窗"""
    try:
        close_button = driver.find_element(By.XPATH, "//button[contains(text(), '關閉')]")
        close_button.click()
        time.sleep(1)
        logger.info("✓ 彈窗已關閉")
        return True
    except:
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(1)
            logger.info("✓ 使用 ESC 關閉彈窗")
            return True
        except Exception as e:
            logger.warning(f"關閉彈窗失敗: {e}")
            return False


def main():
    """測試新聞彈窗提取"""
    print("=" * 80)
    print("測試新聞彈窗內容提取")
    print("=" * 80)
    print()
    
    logger = setup_logging()
    
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"
    news_url = "https://www.budaedu.org/#/bulletins/"
    
    scraper = None
    try:
        # 初始化
        logger.info("初始化 BookScraper...")
        scraper = BookScraper(chromedriver_path, download_dir, logger)
        scraper.setup_driver()
        
        # 導航
        logger.info(f"導航到: {news_url}")
        if not scraper.navigate_to_website(news_url):
            logger.error("無法訪問新聞頁面")
            return
        
        # 等待新聞頁面載入
        logger.info("等待新聞頁面載入...")
        try:
            WebDriverWait(scraper.driver, 15).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            WebDriverWait(scraper.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='javascript:void(0)']"))
            )
            logger.info("✓ 新聞頁面載入完成")
            time.sleep(3)
        except Exception as e:
            logger.error(f"等待新聞頁面載入失敗: {e}")
            return
        
        # 找到新聞連結
        news_links = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href='javascript:void(0)']")
        logger.info(f"✓ 找到 {len(news_links)} 個新聞項目")
        print()
        
        # 測試前 3 則新聞
        test_count = min(3, len(news_links))
        results = []
        
        for i in range(test_count):
            print(f"\n{'=' * 80}")
            print(f"測試新聞 {i + 1}/{test_count}")
            print('=' * 80)
            
            try:
                # 重新獲取連結
                news_links = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href='javascript:void(0)']")
                link = news_links[i]
                
                # 獲取預覽資訊
                preview_text = link.text.strip()
                lines = preview_text.split('\n')
                preview_title = lines[0] if len(lines) > 0 else "未知"
                preview_date = lines[1] if len(lines) > 1 else "未知"
                
                logger.info(f"預覽: {preview_title} ({preview_date})")
                
                # 滾動並點擊
                scraper.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                time.sleep(1)
                scraper.driver.execute_script("arguments[0].click();", link)
                logger.info("✓ 已點擊新聞項目")
                
                # 提取彈窗內容
                popup_data = extract_popup_content(scraper.driver, logger)
                
                if popup_data and popup_data.get('success'):
                    print(f"\n標題: {popup_data['title']}")
                    print(f"內容長度: {len(popup_data['content'])} 字元")
                    print(f"\n內容預覽:")
                    print("-" * 80)
                    print(popup_data['content'][:200] + "..." if len(popup_data['content']) > 200 else popup_data['content'])
                    print("-" * 80)
                    
                    results.append({
                        'index': i + 1,
                        'preview_title': preview_title,
                        'extracted_title': popup_data['title'],
                        'content_length': len(popup_data['content']),
                        'success': True
                    })
                    logger.info("✓ 提取成功")
                else:
                    logger.error("✗ 提取失敗")
                    results.append({
                        'index': i + 1,
                        'preview_title': preview_title,
                        'success': False
                    })
                
                # 關閉彈窗
                close_popup(scraper.driver, logger)
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"處理新聞 {i + 1} 時發生錯誤: {e}")
                close_popup(scraper.driver, logger)
                continue
        
        # 顯示測試結果摘要
        print(f"\n{'=' * 80}")
        print("測試結果摘要")
        print('=' * 80)
        
        success_count = sum(1 for r in results if r.get('success'))
        print(f"成功: {success_count}/{len(results)}")
        print()
        
        for result in results:
            status = "✓" if result.get('success') else "✗"
            print(f"{status} 新聞 {result['index']}: {result['preview_title']}")
            if result.get('success'):
                print(f"   標題: {result['extracted_title']}")
                print(f"   內容: {result['content_length']} 字元")
        
        print('=' * 80)
        
        if success_count == len(results):
            print("✓ 所有測試通過！")
        else:
            print(f"⚠ {len(results) - success_count} 個測試失敗")
        
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {e}", exc_info=True)
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()
