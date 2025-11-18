#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試編碼修復的腳本
Test Encoding Fix Script
"""

import sys
import logging
from datetime import datetime

def setup_utf8_logging():
    """設置 UTF-8 日誌記錄"""
    # 設置控制台輸出編碼
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    # 設置日誌
    log_filename = f"encoding_test_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """主測試函數"""
    logger = setup_utf8_logging()
    
    logger.info("=" * 60)
    logger.info("開始編碼測試")
    logger.info("=" * 60)
    
    # 測試各種中文字符
    test_messages = [
        "初始化系統模組...",
        "載入進度快取...",
        "搜尋新書...",
        "開始處理 1 本新書...",
        "處理書籍 1/1...",
        "正在處理書籍: 佛教入門指南(修訂版) CH826-21",
        "已點擊電子檔下載連結",
        "找到 1 個可用 PDF 連結",
        "獲取第一個 PDF 連結: https://www2.budaedu.org/dharma-data/book-efile/CH826-21-01-001.pdf",
        "已設定下載目標 (等待下載)",
        "成功獲取 PDF 連結: CH826-21-01-001.pdf",
        "開始下載 PDF: CH826-21-01-001.pdf",
        "檔案大小: 10.42 MB",
        "✓ PDF 下載成功: CH826-21-01-001.pdf (10922069 bytes)",
        "✓ 成功處理: 佛教入門指南(修訂版) CH826-21",
        "開始 AI 處理: 佛教入門指南(修訂版) CH826-21",
        "PDF 大小 (10.42 MB) <= 30MB, 使用 PDF 提取方法",
        "PDF 有 774 頁",
        "成功從 773/774 頁提取文字",
        "成功從 PDF 提取 462169 個字符",
        "成功生成摘要 (423 個字符)",
        "✓ 成功處理: 佛教入門指南(修訂版) CH826-21",
        "進度: 1 成功, 0 失敗, 1/1 完成",
        "生成文件...",
        "生成文件，包含 1 本書籍",
        "創建新的 Word 文件",
        "Word 文件創建成功",
        "Word 文件保存成功: generated_documents\\新書簡介_2025-10-31.docx (37585 bytes)",
        "創建新的 Excel 工作簿",
        "Excel 文件保存成功: generated_documents\\新書詳細資料_2025-10-31.xlsx (6420 bytes)",
        "文件生成完成:",
        "  Word 文件: generated_documents\\新書簡介_2025-10-31.docx",
        "  Excel 文件: generated_documents\\新書詳細資料_2025-10-31.xlsx",
        "生成通知資料...",
        "通知資料已生成:",
        "  時間戳記檔案: generated_documents\\notification_data_20251031_162703.json",
        "  最新檔案: generated_documents\\notification_data_latest.json",
        "  成功處理書籍數: 1",
        "發送郵件...",
        "附件檔案驗證通過: 新書簡介_2025-10-31.docx (37585 bytes)",
        "附件檔案驗證通過: 新書詳細資料_2025-10-31.xlsx (6420 bytes)",
        "連接到 SMTP 伺服器: smtp.gmail.com:587",
        "處理完成，清理資源...",
        "WebDriver 已關閉",
        "模組清理完成",
        "✅ 通知處理器成功完成"
    ]
    
    for i, message in enumerate(test_messages, 1):
        logger.info(f"測試 {i:2d}: {message}")
    
    logger.info("=" * 60)
    logger.info("編碼測試完成")
    logger.info("=" * 60)
    
    print("\n如果您能正確看到上述所有中文字符，則編碼修復成功！")
    print("If you can see all Chinese characters correctly above, the encoding fix is successful!")

if __name__ == "__main__":
    main()