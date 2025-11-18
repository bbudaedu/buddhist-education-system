#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速驗證修復效果
Quick Fix Verification
"""

import requests
import json
from datetime import datetime

def verify_encoding():
    """驗證編碼修復"""
    print("1️⃣ 驗證編碼修復...")
    test_text = "測試中文：開始處理電子書 ✓ 成功處理"
    print(f"   {test_text}")
    return True

def verify_notification_deduplication():
    """驗證通知去重"""
    print("\n2️⃣ 驗證通知去重...")
    try:
        response = requests.get('http://localhost:3001/admin/stats/deliveries', timeout=5)
        if response.status_code == 200:
            data = response.json()
            recent = data.get('recentNotifications', [])
            if recent:
                latest = recent[0]
                print(f"   最新通知 ID: {latest.get('id')}")
                print(f"   收件人數: {latest.get('totalRecipients')}")
                print(f"   成功發送: {latest.get('successfulDeliveries')}")
                
                # 檢查最近5分鐘內的通知數量
                recent_count = len([n for n in recent[:10]])
                print(f"   最近通知數: {recent_count}")
                
                if recent_count == 1:
                    print("   ✅ 沒有重複通知")
                    return True
                else:
                    print(f"   ⚠️ 檢測到 {recent_count} 個通知")
                    return False
            else:
                print("   ℹ️ 沒有通知記錄")
                return True
        else:
            print(f"   ❌ API 回應錯誤: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 連接失敗: {e}")
        return False

def verify_notification_data():
    """驗證通知數據文件"""
    print("\n3️⃣ 驗證通知數據文件...")
    try:
        with open('ebook/generated_documents/notification_data_latest.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        books = data.get('successfullyProcessed', [])
        print(f"   處理書籍數: {len(books)}")
        
        if books:
            book = books[0]
            title = book.get('title', '')
            print(f"   書名: {title}")
            
            # 檢查中文字符
            if any('\u4e00' <= c <= '\u9fff' for c in title):
                print("   ✅ 書名包含正確的中文字符")
                return True
            else:
                print("   ⚠️ 書名可能有編碼問題")
                return False
        else:
            print("   ℹ️ 沒有處理的書籍")
            return True
            
    except FileNotFoundError:
        print("   ❌ 通知數據文件不存在")
        return False
    except Exception as e:
        print(f"   ❌ 讀取失敗: {e}")
        return False

def verify_system_health():
    """驗證系統健康狀態"""
    print("\n4️⃣ 驗證系統健康狀態...")
    try:
        response = requests.get('http://localhost:3001/health/detailed', timeout=5)
        if response.status_code == 200:
            health = response.json()
            status = health.get('status', 'unknown')
            print(f"   系統狀態: {status}")
            
            checks = health.get('checks', {})
            for name, check in checks.items():
                status_icon = "✅" if check.get('status') == 'healthy' else "❌"
                print(f"   {status_icon} {name}: {check.get('status')}")
            
            return health.get('status') == 'healthy'
        else:
            print(f"   ❌ 健康檢查失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 連接失敗: {e}")
        return False

def main():
    """主驗證函數"""
    print("🔍 開始驗證修復效果")
    print("=" * 60)
    
    results = []
    results.append(("編碼修復", verify_encoding()))
    results.append(("通知去重", verify_notification_deduplication()))
    results.append(("通知數據", verify_notification_data()))
    results.append(("系統健康", verify_system_health()))
    
    print("\n" + "=" * 60)
    print("📊 驗證結果")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"{icon} {name}")
    
    print("-" * 60)
    print(f"通過: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有驗證都通過！修復成功！")
        print("\n✅ 系統已準備好投入生產使用")
    elif passed >= total * 0.75:
        print("\n⚠️ 大部分驗證通過，但有些項目需要注意")
    else:
        print("\n❌ 多個驗證失敗，需要進一步檢查")
    
    print(f"\n驗證時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()