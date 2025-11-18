#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for summary text cleanup functionality
測試摘要文字清理功能的腳本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_processor import GeminiProcessor
import logging

def test_summary_cleanup():
    """Test the clean_summary_text function with various inputs"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create processor instance (API key not needed for cleanup testing)
    processor = GeminiProcessor("dummy-key", logger)
    
    # Test cases with problematic prefixes
    test_cases = [
        {
            "input": "好的，這是一份為書籍「淨心與淨土 CH861-36」生成的 300 字摘要：本書探討佛教修行的核心理念...",
            "expected_start": "本書探討佛教修行的核心理念"
        },
        {
            "input": "以下是這本書的摘要：佛教教育在現代社會中扮演重要角色...",
            "expected_start": "佛教教育在現代社會中扮演重要角色"
        },
        {
            "input": "這是一份書籍摘要，內容如下：修行者需要具備正確的心態...",
            "expected_start": "修行者需要具備正確的心態"
        },
        {
            "input": "摘要：淨土宗是佛教的重要宗派之一...",
            "expected_start": "淨土宗是佛教的重要宗派之一"
        },
        {
            "input": "本書探討了禪修的基本方法和理論基礎...",  # No prefix to remove
            "expected_start": "本書探討了禪修的基本方法和理論基礎"
        }
    ]
    
    print("=" * 60)
    print("測試摘要文字清理功能")
    print("=" * 60)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case["input"]
        expected_start = test_case["expected_start"]
        
        print(f"\n測試案例 {i}:")
        print(f"輸入: {input_text[:80]}...")
        
        # Clean the text
        cleaned = processor.clean_summary_text(input_text)
        
        print(f"清理後: {cleaned[:80]}...")
        
        # Check if it starts with expected text
        if cleaned.startswith(expected_start):
            print("✅ 通過")
        else:
            print("❌ 失敗")
            print(f"期望開頭: {expected_start}")
            print(f"實際開頭: {cleaned[:len(expected_start)]}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有測試通過！")
    else:
        print("❌ 部分測試失敗")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    test_summary_cleanup()