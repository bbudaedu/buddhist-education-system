#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成文件腳本
使用已下載的 PDF 文件重新生成 Word 和 Excel 文件
"""

import os
import json
import logging
from datetime import datetime
from gemini_processor import GeminiProcessor
from document_generator import DocumentGenerator

def setup_logging():
    """設置日誌"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'regenerate_log_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    """載入配置"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_book_info_from_filename(filename):
    """從檔案名稱提取書籍資訊"""
    # 移除副檔名
    name_without_ext = os.path.splitext(filename)[0]
    
    # 嘗試解析格式：CH826-21-01-001 或 TCE15-01-001
    parts = name_without_ext.split('-')
    if len(parts) >= 3:
        book_code = parts[0]
        version = parts[1]
        return f"{book_code}-{version}"
    
    return name_without_ext

def main():
    logger = setup_logging()
    logger.info("開始重新生成文件...")
    
    try:
        # 載入配置
        config = load_config()
        
        # 初始化處理器
        ai_processor = GeminiProcessor(
            api_key=config['gemini_api_key'],
            logger=logger
        )
        
        document_generator = DocumentGenerator(logger=logger)
        
        # 掃描 downloads 目錄中的 PDF 文件
        downloads_dir = config.get('download_dir', 'downloads')
        pdf_files = [f for f in os.listdir(downloads_dir) if f.lower().endswith('.pdf')]
        
        logger.info(f"找到 {len(pdf_files)} 個 PDF 文件")
        
        processed_books = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"處理文件 {i}/{len(pdf_files)}: {pdf_file}")
            
            pdf_path = os.path.join(downloads_dir, pdf_file)
            book_title = extract_book_info_from_filename(pdf_file)
            
            try:
                # 檢查檔案大小
                file_size = os.path.getsize(pdf_path)
                file_size_mb = file_size / (1024 * 1024)
                
                # 生成摘要
                summary = ai_processor.generate_summary_from_pdf(pdf_path, book_title)
                
                # 判斷處理方式
                processing_method = 'google_search' if file_size > 30 * 1024 * 1024 else 'pdf_extraction'
                
                if summary and len(summary.strip()) > 0:
                    book_info = {
                        'title': book_title,
                        'filename': pdf_file,
                        'download_path': pdf_path,
                        'file_size_bytes': file_size,
                        'summary': summary,
                        'processing_method': processing_method,
                        'processing_success': True,
                        'pdf_url': f"downloads/{pdf_file}",  # 本地路徑作為連結
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    processed_books.append(book_info)
                    method_text = "Google搜尋" if processing_method == 'google_search' else "PDF提取"
                    logger.info(f"✅ {book_title}: 摘要生成成功 ({method_text}, {file_size_mb:.1f}MB)")
                else:
                    logger.warning(f"❌ {book_title}: 摘要生成失敗")
                    
            except Exception as e:
                logger.error(f"❌ {book_title}: 處理失敗 - {e}")
                continue
        
        if processed_books:
            logger.info(f"成功處理 {len(processed_books)} 本書籍，開始生成文件...")
            
            # 生成文件到指定資料夾
            output_dir = 'generated_documents'
            word_path, excel_path = document_generator.generate_both_documents(
                processed_books, 
                output_dir
            )
            
            logger.info("🎉 文件生成完成！")
            logger.info(f"📄 Word 文件: {word_path}")
            logger.info(f"📊 Excel 文件: {excel_path}")
            
            print("\n" + "="*60)
            print("🎉 重新生成完成！")
            print("="*60)
            print(f"📄 Word 文件: {word_path}")
            print(f"📊 Excel 文件: {excel_path}")
            print(f"📚 包含 {len(processed_books)} 本書籍的摘要")
            print("="*60)
            
        else:
            logger.error("沒有成功處理任何書籍")
            print("❌ 沒有成功處理任何書籍")
            
    except Exception as e:
        logger.error(f"重新生成過程發生錯誤: {e}", exc_info=True)
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()