@echo off
chcp 65001 >nul
echo ========================================
echo 執行輪播爬蟲 (Carousel Scraper)
echo ========================================
echo.

cd /d "%~dp0.."

echo 開始爬取輪播資訊...
python -c "from carousel_scraper import CarouselScraper; import logging; import json; import os; from datetime import datetime; logging.basicConfig(level=logging.INFO, format='%%(asctime)s - %%(levelname)s - %%(message)s'); logger = logging.getLogger(); scraper = CarouselScraper('chromedriver-win64/chromedriver.exe', 'downloads', logger); scraper.setup_driver(); scraper.navigate_to_website('https://www.budaedu.org/#/'); items = scraper.extract_carousel_banners(); scraper.cleanup(); output_file = os.path.join('downloads', f'carousel_{datetime.now().strftime(\"%%Y%%m%%d_%%H%%M%%S\")}.json'); os.makedirs('downloads', exist_ok=True); open(output_file, 'w', encoding='utf-8').write(json.dumps(items, ensure_ascii=False, indent=2)); print(f'\n找到 {len(items)} 個輪播項目'); [print(f\"- {item.get('title', 'N/A')}\") for item in items]; print(f'\n結果已存到: {output_file}')"

echo.
echo ========================================
echo 執行完成！結果已存到 downloads 目錄
echo ========================================
pause
