import sys
import os
import logging
from gemini_processor import GeminiProcessor
from config_manager import ConfigManager

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OCR_Test")

def test_book(processor, pdf_path, title):
    logger.info(f"=== 測試書籍: {title} ===")
    if not os.path.exists(pdf_path):
        logger.error(f"找不到檔案: {pdf_path}")
        return
    
    book_info = {
        'title': title,
        'download_path': pdf_path,
        'pdf_url': 'http://test.com',
        'filename': os.path.basename(pdf_path)
    }
    
    try:
        result = processor.process_book(book_info)
        print("\n" + "="*50)
        print(f"書名: {result['title']}")
        print(f"處理方法: {result['processing_method']}")
        print(f"摘要內容:\n{result['summary']}")
        print("="*50 + "\n")
    except Exception as e:
        logger.error(f"處理失敗: {e}")

if __name__ == "__main__":
    # 讀取 API Key (從環境變數或 config.json)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # 嘗試從 config.json 讀取
        try:
            config = ConfigManager("config.json", logger).config
            api_key = config.get("gemini_api_key")
        except:
            pass
            
    if not api_key:
        print("錯誤: 找不到 GEMINI_API_KEY")
        sys.exit(1)
        
    processor = GeminiProcessor(api_key, logger)
    
    # 測試這兩本
    books = [
        ("/app/downloads/CH355-87-01-001.PDF", "佛說觀無量壽佛經"),
        ("/app/downloads/CH722-01-01-001.PDF", "弘一大師演講錄")
    ]
    
    for path, title in books:
        test_book(processor, path, title)
