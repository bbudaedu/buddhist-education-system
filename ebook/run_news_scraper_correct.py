#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正確的新聞爬蟲 - 基於實際 DOM 結構
輸出到 downloads 目錄
"""

import os
import json
import logging
import time
from datetime import datetime
from book_scraper import BookScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def setup_logging():
    """設定日誌"""
    os.makedirs("downloads", exist_ok=True)
    log_file = os.path.join("downloads", f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__), log_file


def extract_popup_content(driver, logger):
    """提取彈窗內容 - 基於實際 DOM 結構"""
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        logger.info("等待彈窗出現...")
        
        # 等待 modal-body 出現（這是內容的主要容器）
        modal_body = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-body"))
        )
        logger.info("找到彈窗內容區域 (.modal-body)")
        
        # 等待內容完全載入
        time.sleep(2)
        
        # 提取標題 - 從 modal-body 內的 h5 元素
        title = ""
        try:
            title_element = modal_body.find_element(By.TAG_NAME, "h5")
            title = title_element.text.strip()
            logger.info(f"提取到標題: {title}")
        except Exception as e:
            logger.debug(f"提取標題失敗: {e}")
        
        # 提取連結 - 從 modal-body 內的 a 標籤
        url = ""
        try:
            # 尋找「課程介紹」或其他連結
            links = modal_body.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and href.startswith("http"):
                    url = href
                    logger.info(f"提取到連結: {url}")
                    break
        except Exception as e:
            logger.debug(f"提取連結失敗: {e}")
        
        # 提取內容 - 從 modal-body 內的 p 元素
        content = ""
        try:
            # 方法1: 提取所有 p 標籤的內容
            paragraphs = modal_body.find_elements(By.TAG_NAME, "p")
            if paragraphs:
                content_parts = []
                for p in paragraphs:
                    text = p.text.strip()
                    if text:
                        content_parts.append(text)
                content = '\n\n'.join(content_parts)
                logger.debug(f"從 p 標籤提取內容長度: {len(content)} 字元")
            
            # 方法2: 如果沒有 p 標籤，獲取 modal-body 的完整文字
            if not content:
                full_text = modal_body.text.strip()
                logger.debug(f"modal-body 完整文字長度: {len(full_text)} 字元")
                
                # 移除標題
                if title:
                    full_text = full_text.replace(title, "", 1)
                
                # 移除 "分享：" 及其後的內容
                if "分享：" in full_text:
                    full_text = full_text.split("分享：")[0]
                
                content = full_text.strip()
            
            # 清理內容 - 移除 "分享：" 及其後的內容
            if "分享：" in content:
                content = content.split("分享：")[0].strip()
            
            # 清理多餘的空白
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
            
            logger.debug(f"清理後內容長度: {len(content)} 字元")
            
        except Exception as e:
            logger.warning(f"提取內容失敗: {e}")
        
        # 如果內容仍然為空，記錄警告
        if not content:
            logger.warning("⚠ 內容為空，可能是頁面結構變更")
        
        logger.info(f"✓ 提取完成 - 標題: {title if title else '(無)'}, 內容: {len(content)} 字元")
        
        return {
            "title": title,
            "content": content,
            "url": url
        }
        
    except Exception as e:
        logger.error(f"提取彈窗內容失敗: {e}", exc_info=True)
        return None


def close_popup(driver, logger):
    """關閉彈窗"""
    try:
        # 找到關閉按鈕
        close_button = driver.find_element(By.XPATH, "//button[contains(text(), '關閉')]")
        close_button.click()
        time.sleep(1)
        logger.info("彈窗已關閉")
        return True
    except:
        # 備用方案：按 ESC
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(1)
            logger.info("使用 ESC 關閉彈窗")
            return True
        except Exception as e:
            logger.warning(f"關閉彈窗失敗: {e}")
            return False


def main():
    """主程式"""
    print("=" * 80)
    print("佛陀教育基金會 - 新聞公告爬蟲")
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
        # 初始化
        logger.info("初始化 BookScraper...")
        scraper = BookScraper(chromedriver_path, download_dir, logger)
        scraper.setup_driver()
        
        # 導航
        if not scraper.navigate_to_website(news_url):
            logger.error("無法訪問新聞頁面")
            return
        
        # 等待新聞頁面載入（不使用 wait_for_page_load，因為它會尋找書籍元素）
        logger.info("等待新聞頁面載入...")
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        try:
            # 等待文檔載入完成
            WebDriverWait(scraper.driver, 15).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # 等待新聞連結出現
            WebDriverWait(scraper.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='javascript:void(0)']"))
            )
            logger.info("新聞頁面載入完成")
            time.sleep(3)  # 額外等待確保內容完全載入
            
        except Exception as e:
            logger.error(f"等待新聞頁面載入失敗: {e}")
            return
        
        # 找到所有新聞連結 (href="javascript:void(0)")
        logger.info("尋找新聞項目...")
        news_links = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href='javascript:void(0)']")
        
        if not news_links:
            logger.warning("未找到新聞項目")
            return
        
        logger.info(f"找到 {len(news_links)} 個新聞項目")
        logger.info("")
        
        # 處理每個新聞
        news_items = []
        max_news = min(10, len(news_links))  # 最多處理 10 則
        
        for i in range(max_news):
            try:
                # 重新獲取連結（避免 stale element）
                news_links = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href='javascript:void(0)']")
                link = news_links[i]
                
                logger.info(f"處理新聞 {i + 1}/{max_news}")
                
                # 獲取預覽資訊
                preview_text = link.text.strip()
                lines = preview_text.split('\n')
                preview_title = lines[0] if len(lines) > 0 else "未知"
                preview_date = lines[1] if len(lines) > 1 else "未知"
                
                logger.info(f"預覽: {preview_title} ({preview_date})")
                
                # 滾動到元素
                scraper.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                time.sleep(1)
                
                # 點擊新聞
                scraper.driver.execute_script("arguments[0].click();", link)
                logger.info("已點擊新聞項目")
                
                # 提取彈窗內容
                popup_data = extract_popup_content(scraper.driver, logger)
                
                if popup_data:
                    news_item = {
                        "id": i + 1,
                        "content_type": "news",
                        "title": popup_data["title"] or preview_title,
                        "publication_date": preview_date,
                        "date": preview_date,
                        "content": popup_data["content"],
                        "url": popup_data.get("url", ""),
                        "extraction_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    news_items.append(news_item)
                    logger.info(f"✓ 成功提取")
                else:
                    logger.warning(f"✗ 提取失敗")
                
                # 關閉彈窗
                close_popup(scraper.driver, logger)
                time.sleep(1)
                
                logger.info("")
                
            except Exception as e:
                logger.error(f"處理新聞 {i + 1} 時發生錯誤: {e}")
                close_popup(scraper.driver, logger)
                continue
        
        # 儲存結果
        if news_items:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # JSON
            json_file = os.path.join(download_dir, f"news_{timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, ensure_ascii=False, indent=2)
            
            # 文字檔
            txt_file = os.path.join(download_dir, f"news_{timestamp}.txt")
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("佛陀教育基金會 - 最新消息\n")
                f.write(f"擷取時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for news in news_items:
                    f.write(f"【新聞 {news['id']}】\n")
                    f.write(f"標題: {news['title']}\n")
                    f.write(f"日期: {news['date']}\n")
                    f.write(f"擷取時間: {news['extraction_time']}\n")
                    f.write(f"\n內容:\n")
                    f.write("-" * 80 + "\n")
                    f.write(news['content'] + "\n")
                    f.write("-" * 80 + "\n\n")
            
            # 顯示摘要
            logger.info("=" * 80)
            logger.info("執行摘要")
            logger.info("=" * 80)
            logger.info(f"成功提取: {len(news_items)} 則新聞")
            logger.info("")
            
            for news in news_items:
                logger.info(f"  {news['id']}. {news['title']} ({news['date']})")
            
            logger.info("")
            logger.info("檔案已儲存:")
            logger.info(f"  JSON: {json_file}")
            logger.info(f"  文字: {txt_file}")
            logger.info(f"  日誌: {log_file}")
            logger.info("=" * 80)
            logger.info("執行完成！")
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
