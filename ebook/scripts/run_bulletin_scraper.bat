@echo off
chcp 65001 >nul
echo ========================================
echo 執行公告爬蟲 (Bulletin Scraper)
echo ========================================
echo.

cd /d "%~dp0.."

echo 開始爬取停課公告...
python -c "from bulletin_scraper import BulletinScraper; import logging; import json; import os; from datetime import datetime; logging.basicConfig(level=logging.INFO, format='%%(asctime)s - %%(levelname)s - %%(message)s'); logger = logging.getLogger(); scraper = BulletinScraper('chromedriver-win64/chromedriver.exe', 'downloads', logger); scraper.setup_driver(); scraper.navigate_to_bulletin_page(); bulletins = scraper.extract_cancellation_table(); scraper.cleanup(); output_file = os.path.join('downloads', f'bulletin_{datetime.now().strftime(\"%%Y%%m%%d_%%H%%M%%S\")}.json'); os.makedirs('downloads', exist_ok=True); open(output_file, 'w', encoding='utf-8').write(json.dumps(bulletins, ensure_ascii=False, indent=2)); print(f'\n找到 {len(bulletins)} 則公告'); [print(f\"- {item.get('course_name', 'N/A')}\") for item in bulletins]; print(f'\n結果已存到: {output_file}')"

echo.
echo ========================================
echo 執行完成！結果已存到 downloads 目錄
echo ========================================
pause
