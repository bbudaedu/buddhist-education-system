#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查監控系統運行狀態
"""

import os
import json
import psutil
from datetime import datetime
from pathlib import Path

def check_running_processes():
    """檢查是否有監控進程在運行"""
    print("=" * 60)
    print("檢查運行中的監控進程")
    print("=" * 60)
    
    monitoring_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('comprehensive_monitoring_integration.py' in str(cmd) for cmd in cmdline):
                create_time = datetime.fromtimestamp(proc.info['create_time'])
                uptime = datetime.now() - create_time
                
                monitoring_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': ' '.join(cmdline),
                    'create_time': create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'uptime': str(uptime).split('.')[0]  # 移除微秒
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if monitoring_processes:
        print(f"\n✓ 找到 {len(monitoring_processes)} 個監控進程:")
        for proc in monitoring_processes:
            print(f"\n  PID: {proc['pid']}")
            print(f"  啟動時間: {proc['create_time']}")
            print(f"  運行時長: {proc['uptime']}")
            print(f"  命令: {proc['cmdline'][:100]}...")
        return True
    else:
        print("\n✗ 沒有找到運行中的監控進程")
        return False

def check_log_files():
    """檢查最新的日誌檔案"""
    print("\n" + "=" * 60)
    print("檢查日誌檔案")
    print("=" * 60)
    
    log_dir = Path('logs')
    if not log_dir.exists():
        print("\n✗ 日誌目錄不存在")
        return
    
    # 查找最新的日誌檔案
    log_files = list(log_dir.glob('**/*.log'))
    if not log_files:
        print("\n✗ 沒有找到日誌檔案")
        return
    
    # 按修改時間排序
    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"\n最近的 5 個日誌檔案:")
    for log_file in log_files[:5]:
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        size = log_file.stat().st_size
        print(f"\n  {log_file.name}")
        print(f"    路徑: {log_file}")
        print(f"    修改時間: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    大小: {size:,} bytes")
        
        # 讀取最後幾行
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"    最後一行: {lines[-1].strip()[:80]}...")
        except Exception as e:
            print(f"    無法讀取: {e}")

def check_monitoring_data():
    """檢查監控資料"""
    print("\n" + "=" * 60)
    print("檢查監控資料")
    print("=" * 60)
    
    data_dir = Path('monitoring_data')
    if not data_dir.exists():
        print("\n✗ 監控資料目錄不存在")
        return
    
    # 檢查快取檔案
    cache_file = Path('.website_monitoring_progress_cache.json')
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            print(f"\n✓ 找到進度快取檔案:")
            print(f"  最後更新: {cache_data.get('last_update', 'Unknown')}")
            print(f"  會話 ID: {cache_data.get('session_id', 'Unknown')}")
            
            if 'current_session' in cache_data:
                session = cache_data['current_session']
                print(f"  當前會話:")
                print(f"    開始時間: {session.get('start_time', 'Unknown')}")
                print(f"    狀態: {session.get('status', 'Unknown')}")
        except Exception as e:
            print(f"\n✗ 無法讀取快取檔案: {e}")
    else:
        print("\n- 沒有找到進度快取檔案")

def check_chrome_processes():
    """檢查 Chrome 進程"""
    print("\n" + "=" * 60)
    print("檢查 Chrome/ChromeDriver 進程")
    print("=" * 60)
    
    chrome_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        try:
            name = proc.info['name'].lower()
            if 'chrome' in name or 'chromedriver' in name:
                create_time = datetime.fromtimestamp(proc.info['create_time'])
                uptime = datetime.now() - create_time
                
                chrome_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'uptime': str(uptime).split('.')[0]
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if chrome_processes:
        print(f"\n✓ 找到 {len(chrome_processes)} 個 Chrome 相關進程:")
        for proc in chrome_processes[:10]:  # 只顯示前10個
            print(f"  PID {proc['pid']}: {proc['name']} (運行 {proc['uptime']})")
    else:
        print("\n- 沒有找到 Chrome 相關進程")

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("佛教教育網站監控系統 - 狀態檢查")
    print("=" * 60)
    print(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 執行各項檢查
    has_process = check_running_processes()
    check_log_files()
    check_monitoring_data()
    check_chrome_processes()
    
    # 總結
    print("\n" + "=" * 60)
    print("檢查總結")
    print("=" * 60)
    
    if has_process:
        print("\n✓ 監控系統正在運行")
        print("\n建議操作:")
        print("  - 查看日誌了解詳細狀態")
        print("  - 等待監控週期完成")
        print("  - 檢查 generated_documents/ 目錄的輸出")
    else:
        print("\n✗ 監控系統未運行")
        print("\n啟動監控:")
        print("  方法 1: START_HERE.bat")
        print("  方法 2: start_monitoring.bat")
        print("  方法 3: python comprehensive_monitoring_integration.py start")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
