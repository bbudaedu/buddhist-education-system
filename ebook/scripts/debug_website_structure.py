#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
網站結構診斷工具
用於檢查 budaedu.org 的實際 HTML 結構
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    """設定 Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service('./chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def diagnose_page(url, page_name):
    """診斷特定頁面的結構"""
    print(f"\n{'='*60}")
    print(f"診斷頁面: {page_name}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")
    
    driver = setup_driver()
    
    try:
        driver.get(url)
        print(f"✓ 頁面載入成功")
        
        # 等待頁面載入
        time.sleep(3)
        
        # 取得頁面標題
        print(f"頁面標題: {driver.title}")
        
        # 檢查常見的容器元素
        print("\n檢查常見容器元素:")
        containers = [
            ("div.container", "Container div"),
            ("div.content", "Content div"),
            ("main", "Main element"),
            ("div[class*='book']", "Book related divs"),
            ("div[class*='card']", "Card divs"),
            ("div[class*='item']", "Item divs"),
            ("article", "Article elements"),
        ]
        
        for selector, desc in containers:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  ✓ {desc}: 找到 {len(elements)} 個")
                    if len(elements) <= 5:
                        for i, elem in enumerate(elements[:3]):
                            classes = elem.get_attribute('class')
                            print(f"    [{i+1}] class='{classes}'")
            except Exception as e:
                print(f"  ✗ {desc}: {str(e)}")
        
        # 檢查圖片元素
        print("\n檢查圖片元素:")
        try:
            images = driver.find_elements(By.TAG_NAME, "img")
            print(f"  找到 {len(images)} 個圖片")
            for i, img in enumerate(images[:5]):
                src = img.get_attribute('src')
                alt = img.get_attribute('alt')
                print(f"    [{i+1}] src='{src[:50]}...' alt='{alt}'")
        except Exception as e:
            print(f"  ✗ 圖片檢查失敗: {str(e)}")
        
        # 檢查連結
        print("\n檢查連結元素:")
        try:
            links = driver.find_elements(By.TAG_NAME, "a")
            print(f"  找到 {len(links)} 個連結")
            for i, link in enumerate(links[:10]):
                href = link.get_attribute('href')
                text = link.text.strip()
                if text:
                    print(f"    [{i+1}] '{text[:30]}' -> {href}")
        except Exception as e:
            print(f"  ✗ 連結檢查失敗: {str(e)}")
        
        # 輸出頁面 HTML 結構（前 2000 字元）
        print("\n頁面 HTML 結構預覽:")
        print("-" * 60)
        html = driver.page_source[:2000]
        print(html)
        print("-" * 60)
        
        # 儲存完整 HTML
        filename = f"debug_{page_name.replace(' ', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"\n✓ 完整 HTML 已儲存至: {filename}")
        
    except Exception as e:
        print(f"✗ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

def main():
    """主程式"""
    print("="*60)
    print("佛教教育網站結構診斷工具")
    print("="*60)
    
    # 診斷各個頁面
    pages = [
        ("https://www.budaedu.org", "首頁"),
        ("https://www.budaedu.org/book/", "書籍頁面"),
        ("https://www.budaedu.org/news/", "最新消息"),
        ("https://www.budaedu.org/bulletin/", "公告事項"),
    ]
    
    for url, name in pages:
        try:
            diagnose_page(url, name)
        except Exception as e:
            print(f"\n✗ 診斷 {name} 時發生錯誤: {str(e)}")
        
        print("\n" + "="*60)
        time.sleep(2)  # 避免請求太頻繁
    
    print("\n診斷完成！請檢查生成的 debug_*.html 檔案")

if __name__ == "__main__":
    main()
