# 📅 全自動新書檢查系統設置指南

## 🎯 系統概述

本系統已配置為全自動執行，每天定時檢查新書並發送 LINE 通知給訂閱用戶。

## ⚙️ 當前配置

### 📅 排程設定
- **執行時間**: 每天凌晨 2:00 (Asia/Taipei)
- **時區**: Asia/Taipei (台北時間)
- **重試次數**: 3 次
- **重試間隔**: 30 分鐘
- **狀態**: ✅ 已啟用

### 🔄 自動化流程
1. **每日 02:00** - 自動執行 Python ebook processor
2. **檢查新書** - 掃描 budaedu.org 網站
3. **下載 PDF** - 自動下載新書 PDF 檔案
4. **AI 處理** - 使用 Gemini AI 生成摘要
5. **發送通知** - 透過 LINE Bot 發送給訂閱用戶
6. **錯誤重試** - 失敗時自動重試（每小時 :15 分）

## 🚀 啟動自動化系統

### 1. 確認配置
```bash
# 檢查 .env 文件中的排程配置
SCHEDULER_ENABLED=true
SCHEDULER_DAILY_TIME=02:00
SCHEDULER_TIMEZONE=Asia/Taipei
```

### 2. 啟動服務
```bash
cd Line-bot-llm-mysql
npm run build
npm start
```

### 3. 驗證狀態
```bash
# 檢查排程器狀態
node check-scheduler-status.js
```

## 📊 監控和管理

### 檢查系統狀態
```bash
# 系統健康檢查
curl http://localhost:3001/health/detailed

# 排程器狀態
curl http://localhost:3001/admin/status

# 訂閱統計
curl http://localhost:3001/admin/stats/subscriptions
```

### 手動觸發測試
```bash
# 手動觸發新書檢查
curl -X POST http://localhost:3001/admin/notifications/trigger \
  -H "Content-Type: application/json" \
  -d '{"triggeredBy": "Manual Test"}'

# 使用測試腳本
node trigger-real-books-notification.js
```

## 🔧 配置選項

### 修改執行時間
```bash
# 編輯 .env 文件
SCHEDULER_DAILY_TIME=08:00  # 改為早上 8:00 執行
```

### 調整重試設定
```bash
SCHEDULER_MAX_RETRIES=5           # 最多重試 5 次
SCHEDULER_RETRY_DELAY_MINUTES=60  # 重試間隔 60 分鐘
```

### 通知設定
```bash
NOTIFICATION_MAX_BOOKS_PER_MESSAGE=10  # 每則訊息最多 10 本書
NOTIFICATION_MAX_RECIPIENTS_PER_BATCH=50  # 每批次最多 50 位收件人
```

## 📱 用戶訂閱管理

### 用戶如何訂閱
1. 加入 LINE Bot 好友
2. 發送「訂閱新書」
3. 系統自動記錄訂閱狀態

### 管理訂閱用戶
```bash
# 查看訂閱統計
curl http://localhost:3001/admin/stats/subscriptions

# 查看投遞統計
curl http://localhost:3001/admin/stats/deliveries
```

## 🛠️ 故障排除

### 常見問題

#### 1. 排程器未執行
```bash
# 檢查服務狀態
node check-scheduler-status.js

# 檢查日誌
# 查看 LINE Bot 服務輸出
```

#### 2. Python 處理器失敗
```bash
# 手動測試 Python 處理器
cd ../ebook
python notification_processor.py
```

#### 3. 通知發送失敗
```bash
# 檢查 LINE API 配置
# 驗證 CHANNEL_ACCESS_TOKEN 和 CHANNEL_SECRET
```

### 日誌監控
- LINE Bot 服務會輸出詳細的執行日誌
- 包含排程執行、處理結果、錯誤訊息等
- 可透過 `getProcessOutput` 查看即時日誌

## 📈 效能監控

### 系統指標
- **處理時間**: 平均每本書 60 秒
- **成功率**: 目標 95% 以上
- **通知延遲**: 處理完成後 5 分鐘內發送

### 監控端點
- `GET /health/metrics` - 系統效能指標
- `GET /admin/performance` - 效能摘要
- `GET /admin/audit` - 操作審計日誌

## 🔒 安全考量

### 環境變數保護
- 所有敏感資訊存放在 `.env` 文件
- 不要將 `.env` 文件提交到版本控制
- 定期更新 API 金鑰

### 存取控制
- 管理端點建議加上認證
- 限制來源 IP 存取
- 監控異常操作

## 📋 維護檢查清單

### 每日檢查
- [ ] 確認排程器正常執行
- [ ] 檢查是否有新書處理
- [ ] 驗證通知發送成功

### 每週檢查
- [ ] 檢查系統效能指標
- [ ] 清理舊的日誌檔案
- [ ] 更新訂閱統計報告

### 每月檢查
- [ ] 檢查 API 配額使用情況
- [ ] 更新系統依賴套件
- [ ] 備份重要配置和資料

## 🎉 系統已就緒！

✅ **自動化系統已完全配置並運行中**

- 下次執行時間: **每天凌晨 2:00**
- 監控狀態: **健康**
- 用戶可隨時訂閱接收通知

系統將自動：
1. 檢查新書
2. 生成摘要
3. 發送 LINE 通知
4. 處理錯誤重試
5. 記錄操作日誌

無需人工干預，系統將持續為用戶提供最新的書籍資訊！🚀