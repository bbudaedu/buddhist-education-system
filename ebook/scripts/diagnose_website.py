#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
網站結構診斷工具
用於檢查目標網站的實際 HTML 結構和元素
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def diagnose_website():
    """診斷網站結構"""
    
    # 設定 Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service('./chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("=" * 60)
        print("佛教教育網站結構診斷")
        print("=" * 60)
        
        # 測試新書頁面
        print("\n[1] 檢查新書頁面...")
        driver.get('https://www.budaedu.org/#/books/applicable/chinese')
        time.sleep(8)  # 等待 SPA 頁面載入
        
        print(f"頁面標題: {driver.title}")
        print(f"當前 URL: {driver.current_url}")
        
        # 嘗試各種可能的選擇器
        selectors = [
            ("CSS: .book-card", By.CSS_SELECTOR, ".book-card"),
            ("CSS: .card", By.CSS_SELECTOR, ".card"),
            ("CSS: [class*='book']", By.CSS_SELECTOR, "[class*='book']"),
            ("CSS: [class*='card']", By.CSS_SELECTOR, "[class*='card']"),
            ("CSS: .item", By.CSS_SELECTOR, ".item"),
            ("CSS: article", By.CSS_SELECTOR, "article"),
            ("XPATH: //div[contains(@class, 'book')]", By.XPATH, "//div[contains(@class, 'book')]"),
            ("XPATH: //a[contains(@href, 'book')]", By.XPATH, "//a[contains(@href, 'book')]"),
        ]
        
        print("\n嘗試各種選擇器:")
        for name, by, selector in selectors:
            try:
                elements = driver.find_elements(by, selector)
                print(f"  ✓ {name}: 找到 {len(elements)} 個元素")
                if elements and len(elements) > 0:
                    # 顯示第一個元素的 HTML
                    print(f"    第一個元素的 class: {elements[0].get_attribute('class')}")
                    print(f"    第一個元素的 tag: {elements[0].tag_name}")
            except Exception as e:
                print(f"  ✗ {name}: {str(e)}")
        
        # 取得頁面的主要結構
        print("\n頁面主要結構:")
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            print(f"  Body classes: {body.get_attribute('class')}")
            
            # 找出所有主要容器
            containers = driver.find_elements(By.CSS_SELECTOR, "div[class*='container'], div[class*='wrapper'], main, section")
            print(f"  找到 {len(containers)} 個主要容器")
            for i, container in enumerate(containers[:5]):  # 只顯示前5個
                print(f"    容器 {i+1}: {container.tag_name}.{container.get_attribute('class')}")
        except Exception as e:
            print(f"  錯誤: {e}")
        
        # 檢查是否為 SPA (Single Page Application)
        print("\n檢查頁面類型:")
        scripts = driver.find_elements(By.TAG_NAME, "script")
        has_react = any('react' in script.get_attribute('src') or '' for script in scripts if script.get_attribute('src'))
        has_vue = any('vue' in script.get_attribute('src') or '' for script in scripts if script.get_attribute('src'))
        has_angular = any('angular' in script.get_attribute('src') or '' for script in scripts if script.get_attribute('src'))
        
        print(f"  React: {'是' if has_react else '否'}")
        print(f"  Vue: {'是' if has_vue else '否'}")
        print(f"  Angular: {'是' if has_angular else '否'}")
        
        # 儲存頁面 HTML 供檢查
        with open('page_source_books.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"\n✓ 頁面 HTML 已儲存到: page_source_books.html")
        
        # 測試最新消息頁面
        print("\n" + "=" * 60)
        print("[2] 檢查最新消息頁面...")
        driver.get('https://www.budaedu.org/#/bulletins/')
        time.sleep(8)
        
        print(f"頁面標題: {driver.title}")
        
        news_selectors = [
            ("CSS: .news-item", By.CSS_SELECTOR, ".news-item"),
            ("CSS: .news", By.CSS_SELECTOR, ".news"),
            ("CSS: [class*='news']", By.CSS_SELECTOR, "[class*='news']"),
            ("CSS: article", By.CSS_SELECTOR, "article"),
        ]
        
        print("\n嘗試各種選擇器:")
        for name, by, selector in news_selectors:
            try:
                elements = driver.find_elements(by, selector)
                print(f"  ✓ {name}: 找到 {len(elements)} 個元素")
            except Exception as e:
                print(f"  ✗ {name}: {str(e)}")
        
        with open('page_source_news.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"\n✓ 頁面 HTML 已儲存到: page_source_news.html")
        
        print("\n" + "=" * 60)
        print("診斷完成！")
        print("請檢查生成的 HTML 檔案以了解實際的頁面結構")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    diagnose_website()
