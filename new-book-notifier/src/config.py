import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    載入 .env 變數或環境變數的統一個入口。
    供 FastAPI 與內部核心模組使用。
    """
    gemini_api_key: str = ""
    chromedriver_path: str = "/usr/bin/chromedriver"
    target_url: str = "https://www.budaedu.org"
    baseline_book_title: str = "CH754-02"
    download_dir: str = "/app/downloads"
    
    # 郵件通知
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_recipients: str = "" # 逗號分隔的信箱清單
    
    # Webhook
    line_bot_webhook_url: str = "http://localhost:3000/api/new-books/webhook"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
