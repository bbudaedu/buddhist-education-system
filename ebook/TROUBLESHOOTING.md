# 故障排除指南
# Troubleshooting Guide

## 🔍 常見問題

### 問題 1: `generated_documents/website_monitoring` 目錄是空的

**症狀**：
- 執行完成後，`website_monitoring` 目錄下的子目錄都是空的
- 沒有產生 Excel 檔案

**可能原因**：

#### 原因 A: 程式還在執行中 ⏳
Media processor 處理時間較長（可能需要 5-10 分鐘），程式可能還沒執行完成。

**檢查方法**：
```bash
# 查看最新日誌的最後幾行
python -c "import glob; import os; files = glob.glob('ebook/logs/daily_monitoring_*.log'); latest = max(files, key=os.path.getmtime); lines = open(latest, 'r', encoding='utf-8', errors='ignore').readlines(); print(''.join(lines[-20:]))"
```

**解決方案**：
- 等待程式執行完成
- 查看日誌中是否有 "Monitoring cycle completed" 訊息

#### 原因 B: 程式在 Media 處理時卡住 🔒
Media processor 可能因為網路問題或網站回應慢而卡住。

**檢查方法**：
```bash
# 查看日誌中的最後時間戳
# 如果超過 10 分鐘沒有新日誌，可能卡住了
```

**解決方案**：
1. 終止程式（Ctrl+C）
2. 暫時停用 Media processor
3. 修改 `config.json`：
```json
{
  "website_monitoring": {
    "content_types": {
      "media": {
        "enabled": false  // 暫時停用
      }
    }
  }
}
```

#### 原因 C: 程式執行失敗 ❌
程式在資料同步前就失敗了。

**檢查方法**：
```bash
# 搜尋錯誤訊息
python -c "import glob; import os; files = glob.glob('ebook/logs/daily_monitoring_*.log'); latest = max(files, key=os.path.getmtime); lines = open(latest, 'r', encoding='utf-8', errors='ignore').readlines(); errors = [l for l in lines if 'ERROR' in l or 'Exception' in l]; print(''.join(errors))"
```

**解決方案**：
- 查看錯誤訊息
- 根據錯誤類型進行修復

#### 原因 D: 沒有爬取到資料 📭
所有爬蟲都沒有爬取到資料。

**檢查方法**：
```bash
# 查看處理結果
python -c "import glob; import os; files = glob.glob('ebook/logs/daily_monitoring_*.log'); latest = max(files, key=os.path.getmtime); lines = open(latest, 'r', encoding='utf-8', errors='ignore').readlines(); results = [l for l in lines if 'Extracted' in l or 'processed' in l]; print(''.join(results[-10:]))"
```

**解決方案**：
- 檢查網站是否可訪問
- 檢查 ChromeDriver 是否正常
- 查看爬蟲日誌中的詳細錯誤

---

### 問題 2: 程式執行時間過長

**症狀**：
- 程式執行超過 10 分鐘還沒完成
- 日誌長時間沒有更新

**可能原因**：
1. Media processor 處理時間過長
2. 網站回應緩慢
3. ChromeDriver 卡住

**解決方案**：

#### 方案 A: 停用耗時的處理器
修改 `config.json`：
```json
{
  "website_monitoring": {
    "content_types": {
      "carousel": {"enabled": true},
      "cancellation": {"enabled": true},
      "news": {"enabled": true},
      "media": {"enabled": false}  // 停用 media
    }
  }
}
```

#### 方案 B: 添加超時設定
修改 `config.json`：
```json
{
  "chrome_devtools": {
    "timeout": 30,  // 減少超時時間
    "page_load_timeout": 30
  }
}
```

#### 方案 C: 分批執行
不要一次執行所有爬蟲，分批執行：
```bash
# 只執行輪播和停課
python -c "
from website_monitor import WebsiteMonitor
monitor = WebsiteMonitor()
monitor.initialize_components()
# 只處理特定類型
"
```

---

### 問題 3: 沒有產生 JSON 摘要檔案

**症狀**：
- `generated_documents` 目錄下沒有 `monitoring_summary_*.json`

**可能原因**：
- 程式在產生摘要前就失敗了
- JSON 序列化錯誤

**解決方案**：
1. 查看日誌最後的錯誤訊息
2. 確認程式執行到 "Monitoring cycle completed" 階段
3. 檢查 `generated_documents` 目錄權限

---

### 問題 4: LINE 通知沒有發送

**症狀**：
- 程式執行完成但沒有收到 LINE 通知

**可能原因**：

#### 原因 A: 沒有產生 JSON 檔案
Node.js 監控 JSON 檔案來觸發通知，如果沒有 JSON 檔案就不會發送通知。

**檢查方法**：
```bash
dir generated_documents\monitoring_summary_*.json
```

**解決方案**：
- 確保程式執行完成
- 確保產生了 JSON 摘要檔案

#### 原因 B: Node.js 服務沒有運行
**檢查方法**：
```bash
curl http://localhost:3000/health
```

**解決方案**：
```bash
cd Line-bot-llm-mysql
npm start
```

#### 原因 C: 沒有訂閱用戶
**檢查方法**：
```bash
curl http://localhost:3000/admin/stats/subscriptions
```

**解決方案**：
- 透過 LINE bot 發送 "訂閱新書通知"

---

## 🛠️ 除錯工具

### 工具 1: 檢查執行狀態
```bash
cd ebook
python -c "
import glob
import os
from datetime import datetime

files = glob.glob('logs/daily_monitoring_*.log')
if files:
    latest = max(files, key=os.path.getmtime)
    mtime = os.path.getmtime(latest)
    age = (datetime.now().timestamp() - mtime) / 60
    print(f'最新日誌: {os.path.basename(latest)}')
    print(f'最後更新: {age:.1f} 分鐘前')
    
    lines = open(latest, 'r', encoding='utf-8', errors='ignore').readlines()
    print(f'總行數: {len(lines)}')
    print(f'\\n最後 5 行:')
    print(''.join(lines[-5:]))
else:
    print('沒有找到日誌檔案')
"
```

### 工具 2: 檢查爬取結果
```bash
python -c "
import glob
import os

files = glob.glob('logs/daily_monitoring_*.log')
if files:
    latest = max(files, key=os.path.getmtime)
    lines = open(latest, 'r', encoding='utf-8', errors='ignore').readlines()
    
    results = {}
    for line in lines:
        if 'Extracted' in line and 'carousel' in line:
            results['carousel'] = line.strip()
        elif 'Processed' in line and 'cancellation' in line:
            results['cancellation'] = line.strip()
        elif 'news' in line.lower() and ('extracted' in line.lower() or 'processed' in line.lower()):
            results['news'] = line.strip()
        elif 'media' in line.lower() and ('extracted' in line.lower() or 'processed' in line.lower()):
            results['media'] = line.strip()
    
    print('爬取結果:')
    for key, value in results.items():
        print(f'  {key}: {value}')
else:
    print('沒有找到日誌檔案')
"
```

### 工具 3: 檢查輸出檔案
```bash
python -c "
import os
import glob

print('檢查輸出檔案...')
print()

# 檢查 JSON 摘要
json_files = glob.glob('generated_documents/monitoring_summary_*.json')
print(f'JSON 摘要檔案: {len(json_files)} 個')
if json_files:
    latest = max(json_files, key=os.path.getmtime)
    print(f'  最新: {os.path.basename(latest)}')

# 檢查 Excel 檔案
excel_files = glob.glob('generated_documents/*.xlsx')
print(f'Excel 檔案: {len(excel_files)} 個')

# 檢查 website_monitoring 目錄
for content_type in ['carousel', 'cancellation', 'news', 'media']:
    dir_path = f'generated_documents/website_monitoring/{content_type}'
    if os.path.exists(dir_path):
        files = os.listdir(dir_path)
        print(f'{content_type}: {len(files)} 個檔案')
"
```

---

## 📋 建議的執行流程

### 1. 首次執行前
```bash
# 檢查系統設定
cd ebook
python check_monitoring_setup.py

# 測試 JSON 序列化
python test_json_output.py
```

### 2. 執行監控
```bash
# 手動測試（建議）
test_daily_monitoring.bat

# 或透過排程器
cd ../Line-bot-llm-mysql
npm start
```

### 3. 監控執行狀態
```bash
# 每 2 分鐘檢查一次日誌
# 確認程式還在執行

# 查看最後更新時間
dir /O-D logs\daily_monitoring_*.log
```

### 4. 執行完成後檢查
```bash
# 檢查 JSON 檔案
dir generated_documents\monitoring_summary_*.json

# 檢查 Excel 檔案
dir generated_documents\website_monitoring\*\*.xlsx

# 檢查 LINE 通知
curl http://localhost:3000/admin/stats/deliveries
```

---

## 🚨 緊急處理

### 程式卡住時
```bash
# 1. 終止程式
Ctrl+C

# 2. 查看最後的日誌
type logs\daily_monitoring_*.log | findstr /C:"Processing" | more

# 3. 停用問題處理器
# 編輯 config.json，停用卡住的處理器

# 4. 重新執行
test_daily_monitoring.bat
```

### 清理並重新開始
```bash
# 1. 備份現有資料
xcopy generated_documents generated_documents_backup\ /E /I

# 2. 清理輸出目錄
del /Q generated_documents\website_monitoring\*\*

# 3. 清理舊日誌（保留最近 7 天）
forfiles /P logs /S /M daily_monitoring_*.log /D -7 /C "cmd /c del @path"

# 4. 重新執行
test_daily_monitoring.bat
```

---

## 📞 獲取幫助

如果問題仍然存在：

1. **收集資訊**：
   - 最新的日誌檔案
   - 錯誤訊息
   - 執行環境資訊

2. **檢查文件**：
   - [完整說明](DAILY_MONITORING_README.md)
   - [通知流程](NOTIFICATION_FLOW.md)
   - [快速參考](QUICK_REFERENCE.md)

3. **常見解決方案**：
   - 重啟 ChromeDriver
   - 更新 Python 套件
   - 檢查網路連線
   - 確認網站可訪問
