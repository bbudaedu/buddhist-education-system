import asyncio
import json

# 從 crawl4ai 引入非同步爬蟲類別 AsyncWebCrawler
from crawl4ai import AsyncWebCrawler

async def main():
    """
    主執行函數，包含了爬蟲的所有邏輯。
    """
    target_url = "https://www.budaedu.org/#/"
    book_catalog_selector = "div.tab-pane.active .card-deck"

    print(f"--- 開始爬取 (非同步模式): {target_url} ---")
    print(f"--- 目標區塊 (Selector): {book_catalog_selector} ---")

    # 【最終修正點】
    # 建立爬蟲時，指定 page_load_state="networkidle"。
    # 這會讓爬蟲等待所有網路請求完成後再抓取，確保動態內容已載入。
    async with AsyncWebCrawler(page_load_state="networkidle") as crawler:
        result = await crawler.arun(
            url=target_url,
            target_selector=book_catalog_selector,
            output_format="json",
            max_pages=1
        )

    if result:
        print("\n--- 成功提取書籍目錄 (JSON 格式) ---")
        
        json_data = json.loads(result.model_dump_json())
        
        # 檢查 'extracted_content' 是否存在且有內容
        if json_data and 'extracted_content' in json_data and json_data['extracted_content']:
            extracted_content = json_data['extracted_content']
            
            # 將提取到的內容格式化輸出
            formatted_json = json.dumps(extracted_content, indent=2, ensure_ascii=False)
            print(formatted_json)
        else:
            print("未能提取到 'extracted_content'，或內容為空。印出 crawl4ai 的完整回傳結果：")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
            
    else:
        print("\n--- 提取資料失敗或找不到對應內容 ---")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())