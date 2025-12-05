from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# chromedriver.exe 路徑（請依你的電腦實際調整）
CHROMEDRIVER_PATH = r"D:\ebook\chromedriver-win64\chromedriver.exe"
DOWNLOAD_DIR = os.path.abspath("downloads")    # PDF下載儲存目錄

TARGET_URL = "https://www.budaedu.org/#/books/applicable/chinese"
BASE_BOOK_TITLE = "CH754-02"   # 可用 "CH754-02" 更容易比對！例如只用 "CH754-02"

def main():
    # 建立下載目錄（如果不存在）
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"已建立下載目錄: {DOWNLOAD_DIR}")
    
    # 建立 Chrome options
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,  # 禁用下載提示
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1  # 允許多個下載
    }
    options.add_experimental_option("prefs", prefs)
    print(f"下載目錄設定為: {DOWNLOAD_DIR}")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(TARGET_URL)

    # 等待SPA網頁載入完成 - 使用顯式等待
    print("等待頁面載入...")
    
    # 等待頁面載入
    time.sleep(10)
    
    # 找所有書本卡片（使用 card-body）
    items = driver.find_elements(By.CSS_SELECTOR, ".card-body")
    print(f"共找到 {len(items)} 本書條目")
    # debug: 列印所有條目內容
    for idx, item in enumerate(items):
        print(f'條目{idx}:', repr(item.text))

    # 用模糊比對尋找基準書名
    base_index = -1
    for i, item in enumerate(items):
        if BASE_BOOK_TITLE in item.text:
            base_index = i
            print('基準書名命中:', repr(item.text))
            break
    if base_index == -1:
        print(f"找不到包含基準書名 {BASE_BOOK_TITLE}")
        driver.quit()
        return

    # 取基準書上方的新書
    new_books = items[:base_index]
    print(f"新書數：{len(new_books)}")

    # 記錄要下載的書籍數量
    total_new_books = len(new_books)
    
    for idx in range(total_new_books):
        # 每次重新獲取元素，避免 stale element 問題
        time.sleep(3)
        
        # 滾動到頁面頂部
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        items = driver.find_elements(By.CSS_SELECTOR, ".card-body")
        
        # 確保有足夠的元素
        if idx >= len(items):
            print(f"索引 {idx} 超出範圍，停止")
            break
            
        book_card = items[idx]
        
        # 滾動到書籍卡片位置
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book_card)
        time.sleep(1)
        
        # 從 card-body 中提取書名（在 h5 標籤中）
        try:
            book_title_elem = book_card.find_element(By.TAG_NAME, "h5")
            book_title = book_title_elem.text
            print(f"\n下載新書 {idx+1}/{total_new_books}：{book_title}")
        except:
            print(f"無法取得書名，跳過")
            continue

        # 在卡片內找「電子檔下載」按鈕並點擊
        try:
            # 找到卡片內的所有按鈕
            buttons = book_card.find_elements(By.TAG_NAME, "button")
            download_btn = None
            for btn in buttons:
                if "電子檔下載" in btn.text:
                    download_btn = btn
                    break
            
            if download_btn:
                # 使用 JavaScript 點擊，避免元素遮擋問題
                driver.execute_script("arguments[0].click();", download_btn)
                print("已點擊電子檔下載按鈕")
                time.sleep(3)
                
                # 彈窗PDF連結 - 只下載第一個
                # 嘗試多種選擇器
                pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href,'.pdf') or contains(@href,'.PDF')]")
                
                if len(pdf_links) == 0:
                    # 嘗試找包含 PDF 文字的連結
                    pdf_links = driver.find_elements(By.XPATH, "//a[contains(text(),'PDF') or contains(text(),'pdf')]")
                
                if len(pdf_links) == 0:
                    # 嘗試找彈窗內的所有連結
                    modal = driver.find_elements(By.CSS_SELECTOR, ".modal")
                    if modal:
                        pdf_links = modal[0].find_elements(By.TAG_NAME, "a")
                
                print(f"找到 {len(pdf_links)} 個 PDF 連結")
                if len(pdf_links) > 0:
                    href = pdf_links[0].get_attribute('href')
                    filename = href.split('/')[-1]
                    
                    print(f"  PDF 連結: {href}")
                    
                    # 記錄到下載清單
                    if not hasattr(main, 'download_list'):
                        main.download_list = []
                    main.download_list.append({
                        'title': book_title,
                        'url': href,
                        'filename': filename
                    })
                else:
                    print("  沒有找到 PDF 連結")
                
                # 關閉彈窗 - 嘗試多種方法
                time.sleep(2)
                try: 
                    # 方法1: 找關閉按鈕
                    close_btns = driver.find_elements(By.CSS_SELECTOR, "button.close")
                    if close_btns:
                        close_btns[0].click()
                        print("已關閉彈窗（方法1）")
                        time.sleep(2)  # 等待彈窗完全關閉
                    else:
                        # 方法2: 按 ESC 鍵
                        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        print("已關閉彈窗（方法2 - ESC）")
                        time.sleep(2)
                except Exception as e:
                    print(f"關閉彈窗時出錯: {e}")
            else:
                print("找不到電子檔下載按鈕")
                
        except Exception as e:
            print(f"電子檔下載失敗！{e}")

    driver.quit()
    
    # 產生下載清單和下載腳本
    if hasattr(main, 'download_list') and len(main.download_list) > 0:
        print(f"\n\n=== 找到 {len(main.download_list)} 個 PDF 檔案 ===\n")
        
        # 產生下載連結清單文字檔
        with open("download_links.txt", "w", encoding="utf-8") as f:
            for item in main.download_list:
                f.write(f"{item['url']}\n")
        print("✓ 已產生下載連結清單: download_links.txt")
        
        # 產生 PowerShell 下載腳本
        ps_script = f"""# PDF 下載腳本
$downloadDir = "{DOWNLOAD_DIR}"

# 建立下載目錄
if (!(Test-Path $downloadDir)) {{
    New-Item -ItemType Directory -Path $downloadDir | Out-Null
    Write-Host "已建立下載目錄: $downloadDir"
}}

# 下載清單
$downloads = @(
"""
        for item in main.download_list:
            ps_script += f'    @{{url="{item["url"]}"; filename="{item["filename"]}"; title="{item["title"]}"}},\n'
        
        ps_script += """)

# 開始下載
$count = 0
foreach ($item in $downloads) {
    $count++
    $filepath = Join-Path $downloadDir $item.filename
    Write-Host "[$count/$($downloads.Count)] 下載: $($item.title)"
    Write-Host "  檔案: $($item.filename)"
    
    try {
        # 使用 Invoke-WebRequest 下載
        Invoke-WebRequest -Uri $item.url -OutFile $filepath -UseBasicParsing
        Write-Host "  ✓ 下載成功" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ 下載失敗: $_" -ForegroundColor Red
    }
}

Write-Host "`n下載完成！檔案儲存在: $downloadDir"
"""
        
        with open("download_pdfs.ps1", "w", encoding="utf-8") as f:
            f.write(ps_script)
        print("✓ 已產生 PowerShell 下載腳本: download_pdfs.ps1")
        
        # 產生批次檔
        bat_script = f"""@echo off
chcp 65001 >nul
echo 開始下載 PDF 檔案...
echo.
powershell -ExecutionPolicy Bypass -File download_pdfs.ps1
echo.
pause
"""
        with open("download_pdfs.bat", "w", encoding="utf-8") as f:
            f.write(bat_script)
        print("✓ 已產生批次檔: download_pdfs.bat")
        
        print("\n=== 下載方式 ===")
        print("方式 1: 執行批次檔")
        print("  雙擊 download_pdfs.bat")
        print("\n方式 2: 執行 PowerShell 腳本")
        print("  powershell -ExecutionPolicy Bypass -File download_pdfs.ps1")
        print("\n方式 3: 使用其他下載工具")
        print("  使用 download_links.txt 中的連結")
    else:
        print("\n沒有找到任何 PDF 連結")

if __name__ == "__main__":
    main()
