#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版新聞爬蟲測試 - 直接輸出到 downloads
"""

import os
import json
import logging
from datetime import datetime
from book_scraper import BookScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def setup_logging():
    """設定日誌"""
    os.makedirs("downloads", exist_ok=True)
    log_file = os.path.join("downloads", f"news_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__), log_file


def extract_news_from_popup(driver, logger):
    """從彈窗提取新聞內容"""
    try:
        # 等待彈窗出現
        time.sleep(3)
        
        # 嘗試找到彈窗
        popup_selectors = [
            ".modal-content",
            ".modal-dialog",
            ".modal",
            "[role='dialog']"
        ]
        
        popup = None
        for selector in popup_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # 找到可見的彈窗
                    for elem in elements:
                        if elem.is_displayed():
                            popup = elem
                            logger.info(f"找到可見彈窗: {selector}")
                            break
                if popup:
                    break
            except:
                continue
        
        if not popup:
            logger.warning("未找到彈窗")
            return None
        
        # 提取標題 - 找所有 h5 元素
        title = ""
        try:
            h5_elements = popup.find_elements(By.TAG_NAME, "h5")
            for h5 in h5_elements:
                text = h5.text.strip()
                # 跳過 "最新消息" 這個標題
                if text and text != "最新消息" and len(text) > 3:
                    title = text
                    logger.info(f"提取到標題: {title}")
                    break
        except Exception as e:
            logger.warning(f"提取標題失敗: {e}")
        
        # 提取內容 - 獲取整個彈窗的文字
        content = ""
        try:
            full_text = popup.text.strip()
            logger.debug(f"彈窗完整文字: {full_text[:100]}...")
            
            # 移除不需要的文字
            content = full_text
            content = content.replace("最新消息", "")
            content = content.replace("關閉", "")
            content = content.replace(title, "", 1)  # 只移除第一次出現的標題
            content = content.strip()
            
            logger.info(f"提取到內容長度: {len(content)} 字元")
            
        except Exception as e:
            logger.warning(f"提取內容失敗: {e}")
        
        return {
            "title": title,
            "content": content,
            "extraction_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        logger.error(f"提取彈窗內容時發生錯誤: {e}")
        return None


def close_popup(driver, logger):
    """關閉彈窗"""
    try:
        # 嘗試多種關閉方式
        close_selectors = [
            "button.close",
            ".close",
            "button:contains('關閉')",
            ".modal-footer button"
        ]
        
        for selector in close_selectors:
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, selector)
                close_btn.click()
                logger.info(f"使用 {selector} 關閉彈窗")
                time.sleep(1)
                return True
            except:
                continue
        
        # 如果找不到關閉按鈕，按 ESC
        from selenium.webdriver.common.keys import Keys
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        logger.info("使用 ESC 鍵關閉彈窗")
        time.sleep(1)
        return True
        
    except Exception as e:
        logger.warning(f"關閉彈窗時發生錯誤: {e}")
        return False


def main():
    """主程式"""
    print("=" * 80)
    print("新聞公告爬蟲 - 簡化測試版")
    print("=" * 80)
    print()
    
    logger, log_file = setup_logging()
    
    # 配置
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"
    news_url = "https://www.budaedu.org/#/bulletins/"
    
    logger.info("配置資訊:")
    logger.info(f"  目標網址: {news_url}")
    logger.info(f"  輸出目錄: {download_dir}")
    logger.info("")
    
    scraper = None
    try:
        # 初始化爬蟲
        logger.info("初始化 BookScraper...")
        scraper = BookScraper(chromedriver_path, download_dir, logger)
        
        # 設定瀏覽器
        scraper.setup_driver()
        
        # 導航到新聞頁面
        if not scraper.navigate_to_website(news_url):
            logger.error("無法訪問新聞頁面")
            return
        
        # 等待頁面載入
        if not scraper.wait_for_page_load():
            logger.error("頁面載入失敗")
            return
        
        # 找到所有新聞連結
        logger.info("尋找新聞項目...")
        news_links = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href='javascript:void(0)']")
        
        if not news_links:
            logger.warning("未找到新聞項目")
            return
        
        logger.info(f"找到 {len(news_links)} 個新聞項目")
        logger.info("")
        
        # 處理每個新聞項目
        news_items = []
        for i, link in enumerate(news_links[:5], 1):  # 只處理前5個
            try:
                logger.info(f"處理新聞 {i}/{min(5, len(news_links))}")
                
                # 獲取預覽資訊
                preview_text = link.text.strip()
                logger.info(f"預覽: {preview_text[:50]}...")
                
                # 滾動到元素
                scraper.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                time.sleep(1)
                
                # 點擊新聞項目
                scraper.driver.execute_script("arguments[0].click();", link)
                logger.info("已點擊新聞項目")
                time.sleep(2)
                
                # 提取彈窗內容
                news_data = extract_news_from_popup(scraper.driver, logger)
                if news_data:
                    news_data['preview'] = preview_text
                    news_items.append(news_data)
                    logger.info(f"✓ 成功提取: {news_data['title']}")
                else:
                    logger.warning("✗ 提取失敗")
                
                # 關閉彈窗
                close_popup(scraper.driver, logger)
                time.sleep(1)
                
                logger.info("")
                
            except Exception as e:
                logger.error(f"處理新聞 {i} 時發生錯誤: {e}")
                close_popup(scraper.driver, logger)
                continue
        
        # 儲存結果
        if news_items:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 儲存 JSON
            json_file = os.path.join(download_dir, f"news_{timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, ensure_ascii=False, indent=2)
            
            # 儲存文字檔
            txt_file = os.path.join(download_dir, f"news_{timestamp}.txt")
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("佛陀教育基金會 - 最新消息\n")
                f.write(f"擷取時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, news in enumerate(news_items, 1):
                    f.write(f"【新聞 {i}】\n")
                    f.write(f"標題: {news['title']}\n")
                    f.write(f"擷取時間: {news['extraction_time']}\n")
                    f.write(f"\n內容:\n")
                    f.write("-" * 80 + "\n")
                    f.write(news['content'] + "\n")
                    f.write("-" * 80 + "\n\n")
            
            logger.info("=" * 80)
            logger.info("執行摘要")
            logger.info("=" * 80)
            logger.info(f"成功提取: {len(news_items)} 則新聞")
            logger.info("")
            logger.info("檔案已儲存:")
            logger.info(f"  JSON: {json_file}")
            logger.info(f"  文字: {txt_file}")
            logger.info(f"  日誌: {log_file}")
            logger.info("=" * 80)
        else:
            logger.info("未成功提取任何新聞")
        
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {e}", exc_info=True)
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()
