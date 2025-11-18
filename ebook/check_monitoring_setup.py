#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Monitoring Setup
檢查監控系統設定

This script verifies that all required components for daily monitoring are present.
"""

import os
import sys
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists


def check_monitoring_setup():
    """Check all required components for monitoring system"""
    print("=" * 80)
    print("Checking Daily Monitoring System Setup")
    print("=" * 80)
    print()
    
    all_ok = True
    
    # Check main execution scripts
    print("📋 Main Execution Scripts:")
    all_ok &= check_file_exists("run_daily_monitoring.py", "Daily monitoring script")
    all_ok &= check_file_exists("run_daily_monitoring_utf8.bat", "UTF-8 batch file")
    all_ok &= check_file_exists("test_daily_monitoring.bat", "Test script")
    print()
    
    # Check core monitoring components
    print("🔧 Core Monitoring Components:")
    all_ok &= check_file_exists("monitoring_controller.py", "Monitoring controller")
    all_ok &= check_file_exists("website_monitor.py", "Website monitor")
    all_ok &= check_file_exists("config_manager.py", "Config manager")
    print()
    
    # Check scrapers
    print("🕷️ Scrapers:")
    all_ok &= check_file_exists("book_scraper.py", "Book scraper")
    all_ok &= check_file_exists("carousel_scraper.py", "Carousel scraper")
    all_ok &= check_file_exists("bulletin_scraper.py", "Bulletin scraper")
    print()
    
    # Check processors
    print("⚙️ Processors:")
    all_ok &= check_file_exists("run_news_scraper_correct.py", "News scraper (correct version)")
    all_ok &= check_file_exists("media_processor.py", "Media processor")
    all_ok &= check_file_exists("notification_processor.py", "Notification processor")
    print()
    
    # Check support components
    print("📦 Support Components:")
    all_ok &= check_file_exists("document_generator.py", "Document generator")
    all_ok &= check_file_exists("email_sender.py", "Email sender")
    all_ok &= check_file_exists("progress_manager.py", "Progress manager")
    print()
    
    # Check configuration
    print("⚙️ Configuration:")
    config_exists = check_file_exists("config.json", "Main configuration")
    if not config_exists:
        print("   ℹ️  config.json will be created from config_template.json on first run")
    else:
        all_ok &= config_exists
    all_ok &= check_file_exists("config_template.json", "Configuration template")
    print()
    
    # Check directories
    print("📁 Directories:")
    dirs_to_check = [
        ("logs", "Log directory"),
        ("downloads", "Download directory"),
        ("generated_documents", "Output directory"),
        ("chromedriver-win64", "ChromeDriver directory")
    ]
    
    for dir_path, description in dirs_to_check:
        exists = os.path.isdir(dir_path)
        status = "✅" if exists else "⚠️"
        print(f"{status} {description}: {dir_path}")
        if not exists:
            print(f"   ℹ️  Will be created automatically on first run")
    print()
    
    # Check ChromeDriver
    print("🌐 ChromeDriver:")
    chromedriver_paths = [
        "chromedriver-win64/chromedriver.exe",
        "chromedriver.exe"
    ]
    
    chromedriver_found = False
    for cd_path in chromedriver_paths:
        if os.path.exists(cd_path):
            print(f"✅ ChromeDriver found: {cd_path}")
            chromedriver_found = True
            break
    
    if not chromedriver_found:
        print("❌ ChromeDriver not found!")
        print("   ℹ️  Please download ChromeDriver from:")
        print("   https://chromedriver.chromium.org/downloads")
        all_ok = False
    print()
    
    # Summary
    print("=" * 80)
    if all_ok:
        print("✅ All required components are present!")
        print()
        print("You can now:")
        print("  1. Test manually: test_daily_monitoring.bat")
        print("  2. Run via Node.js scheduler: npm start (in Line-bot-llm-mysql)")
        print()
        return 0
    else:
        print("❌ Some components are missing!")
        print()
        print("Please ensure all required files are present before running.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(check_monitoring_setup())
