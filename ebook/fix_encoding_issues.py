#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復編碼問題的腳本
Fix Encoding Issues Script

這個腳本用於修復 Windows 系統上的中文編碼顯示問題
"""

import os
import sys
import locale
import logging
from datetime import datetime

def setup_console_encoding():
    """設置控制台編碼為 UTF-8"""
    try:
        # 設置 Python 的預設編碼
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
        
        # 設置環境變數
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # 嘗試設置系統 locale
        try:
            locale.setlocale(locale.LC_ALL, 'zh_TW.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'Chinese_Taiwan.UTF-8')
            except locale.Error:
                try:
                    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
                except locale.Error:
                    print("Warning: Could not set UTF-8 locale")
        
        print("✅ Console encoding setup completed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup console encoding: {e}")
        return False

def test_chinese_output():
    """測試中文輸出"""
    test_strings = [
        "測試中文輸出",
        "開始處理電子書",
        "處理完成",
        "錯誤訊息",
        "成功",
        "失敗"
    ]
    
    print("\n=== 中文輸出測試 ===")
    for i, text in enumerate(test_strings, 1):
        print(f"{i}. {text}")
    
    print("=== 測試完成 ===\n")

def setup_logging_with_utf8():
    """設置支援 UTF-8 的日誌記錄"""
    log_filename = f"encoding_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # 創建自定義的 logging handler
    class UTF8FileHandler(logging.FileHandler):
        def __init__(self, filename, mode='a', encoding='utf-8', delay=False):
            super().__init__(filename, mode, encoding, delay)
    
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            UTF8FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # 測試日誌輸出
    logger.info("=== 日誌編碼測試開始 ===")
    logger.info("測試中文日誌輸出")
    logger.info("開始處理電子書")
    logger.info("處理進度: 50%")
    logger.info("處理完成")
    logger.info("=== 日誌編碼測試結束 ===")
    
    print(f"✅ 日誌文件已創建: {log_filename}")
    return logger

def check_system_encoding():
    """檢查系統編碼設置"""
    print("\n=== 系統編碼檢查 ===")
    
    print(f"系統預設編碼: {sys.getdefaultencoding()}")
    print(f"檔案系統編碼: {sys.getfilesystemencoding()}")
    print(f"標準輸出編碼: {sys.stdout.encoding}")
    print(f"標準錯誤編碼: {sys.stderr.encoding}")
    
    try:
        current_locale = locale.getlocale()
        print(f"當前 locale: {current_locale}")
    except Exception as e:
        print(f"無法獲取 locale: {e}")
    
    # 檢查環境變數
    encoding_vars = ['PYTHONIOENCODING', 'LC_ALL', 'LANG']
    for var in encoding_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")
    
    print("=== 檢查完成 ===\n")

def create_batch_file():
    """創建 Windows 批次檔案來設置編碼"""
    batch_content = """@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set LC_ALL=zh_TW.UTF-8
echo Setting console to UTF-8 encoding...
echo Console encoding setup completed.
echo.
echo Running Python script with UTF-8 encoding...
python "%~dp0notification_processor.py" %*
"""
    
    batch_file = "run_with_utf8.bat"
    try:
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        print(f"✅ 批次檔案已創建: {batch_file}")
        print("使用方法: 執行 run_with_utf8.bat 來啟動通知處理器")
        return True
    except Exception as e:
        print(f"❌ 創建批次檔案失敗: {e}")
        return False

def main():
    """主函數"""
    print("🔧 編碼問題修復工具")
    print("=" * 50)
    
    # 1. 設置控制台編碼
    print("1. 設置控制台編碼...")
    setup_console_encoding()
    
    # 2. 檢查系統編碼
    print("2. 檢查系統編碼...")
    check_system_encoding()
    
    # 3. 測試中文輸出
    print("3. 測試中文輸出...")
    test_chinese_output()
    
    # 4. 設置日誌記錄
    print("4. 設置日誌記錄...")
    logger = setup_logging_with_utf8()
    
    # 5. 創建批次檔案
    print("5. 創建批次檔案...")
    create_batch_file()
    
    print("\n" + "=" * 50)
    print("🎉 編碼修復完成!")
    print("\n建議:")
    print("1. 使用 run_with_utf8.bat 來執行 Python 腳本")
    print("2. 確保 Windows 控制台支援 UTF-8 (Windows 10 1903+ 或 Windows 11)")
    print("3. 如果仍有問題，請檢查 Windows 系統的區域設定")

if __name__ == "__main__":
    main()