import sys
import os

# Add the project root and src/core to sys.path so that ebook modules can import each other
current_dir = os.path.dirname(os.path.abspath(__file__))
# 專案根目錄
project_root = os.path.dirname(current_dir)
# core目錄
core_dir = os.path.join(current_dir, "core")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)

from fastapi import FastAPI, BackgroundTasks
from src.api import routes
from src.core.monitoring_logger import get_monitoring_logger

logger = get_monitoring_logger()
# Scheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

app = FastAPI(title="New Book Notifier Service", version="1.0.0")

scheduler = AsyncIOScheduler()

def run_process_task():
    """
    Background worker for schedule execution using API logic
    """
    from src.core.main_processor import MainProcessor
    from src.core.config_manager import ConfigManager
    from src.core.api_data_fetcher import BudaeduAPIFetcher
    
    logger.log_info("Starting scheduled new book monitoring task (API Mode)...")
    try:
        # Load configuration
        config_manager = ConfigManager()
        if not config_manager.load_config():
            logger.log_error("Failed to load configuration. Make sure .env is correctly set matching config_template.")
            return

        # Fetch new books from API
        api_fetcher = BudaeduAPIFetcher(logger=logger)
        api_books = api_fetcher.fetch_latest_books(limit=10)
        
        if not api_books:
            logger.log_info("No new books found from API.")
            return

        # Run processor with API data
        processor = MainProcessor(config_manager.config, logger)
        success = processor.run_with_api_data(api_books)
        
        if success:
            logger.log_info("Scheduled API task finished successfully.")
        else:
            logger.log_error("Scheduled API task finished with errors.")
    except Exception as e:
        logger.log_error(f"Unexpected error in scheduled task: {e}")

@app.on_event("startup")
async def startup_event():
    logger.log_info("Starting New Book Notifier Service...")
    
    # 每天早上 8:00 與 下午 15:00 執行監控 (可以自行調整)
    scheduler.add_job(
        run_process_task,
        trigger=CronTrigger(hour="8,15", minute="0"),
        id="daily_new_book_monitor",
        replace_existing=True
    )
    scheduler.start()
    logger.log_info("Scheduled job 'daily_new_book_monitor' added for 08:00 and 15:00.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down service...")
    scheduler.shutdown()

# Include routers
app.include_router(routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
