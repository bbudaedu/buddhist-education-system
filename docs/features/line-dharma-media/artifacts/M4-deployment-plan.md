# M4 Deployment Plan
# LINE Dharma Media Feature

**Feature**: LINE Dharma Media (最新法寶 & 最新影音)  
**Milestone**: M4 - 部署與發布  
**Status**: 準備中  
**Prepared by**: DevOps + QA Team  
**Last Updated**: 2025-11-26

---

## 部署前檢查清單

### 1. 程式碼準備 ✅
- [x] M2 開發完成並合併到 main branch
- [x] M3 QA 測試通過（95.65%）
- [x] 所有 PRD 驗收標準滿足
- [x] 無 Critical (P0) Bug
- [x] 程式碼已 Code Review

### 2. 環境配置
- [ ] 環境變數檢查 (`.env` 檔案)
  - [ ] `LINE_CHANNEL_SECRET`
  - [ ] `LINE_CHANNEL_ACCESS_TOKEN`
  - [ ] `GEMINI_API_KEY`
  - [ ] `DATABASE_URL`
- [ ] API Endpoint 配置
  - [ ] `BUDAEDU_API_BASE_URL`
- [ ] 快取設定
  - [ ] Cache TTL = 60 秒

### 3. 資料庫準備
- [ ] 資料庫欄位新增：`subscribers.subscribed_videos`
- [ ] 資料庫遷移腳本準備
- [ ] 備份現有資料庫
- [ ] 測試遷移腳本

### 4. 依賴檢查
- [ ] Node.js 版本 ≥ 18
- [ ] npm dependencies 已安裝
- [ ] TypeScript 編譯成功
- [ ] 外部 API 可達性測試

---

## 部署步驟

### Phase 1: 建置與測試環境部署

#### Step 1.1: 建置應用程式

```bash
# 進入專案目錄
cd Line-bot-llm-mysql

# 安裝依賴
npm install

# TypeScript 編譯
npm run build

# 檢查建置產物
ls dist/
```

**驗收標準**:
- [ ] 編譯無錯誤
- [ ] `dist/` 目錄包含所有編譯檔案

#### Step 1.2: 部署到測試環境

```bash
# 設定測試環境變數
cp .env.test .env

# 啟動應用程式（測試模式）
npm start
```

**健康檢查**:
```bash
# 檢查服務健康狀態
curl http://localhost:3000/health

# 預期回應: {"status": "OK"}
```

#### Step 1.3: 資料庫遷移（測試環境）

```bash
# 執行資料庫遷移
npm run migrate

# 驗證新欄位
mysql -u [user] -p books_3f
```

```sql
-- 檢查 subscribed_videos 欄位
DESC subscribers;

-- 應該包含:
-- subscribed_videos BOOLEAN DEFAULT FALSE
```

#### Step 1.4: 測試環境驗證

**自動化測試**:
```bash
# 執行 E2E 測試（針對測試環境）
cd tests/e2e/dharma-media
BASE_URL=https://test.yourdomain.com npm test
```

**手動驗證**:
- [ ] 測試「最新法寶」指令
- [ ] 測試「最新影音」指令
- [ ] 測試 Quick Reply 訂閱功能
- [ ] 測試資料庫訂閱狀態更新

---

### Phase 2: 生產環境部署

#### Step 2.1: 生產環境準備

```bash
# 設定生產環境變數
cp .env.production .env

# 確認環境變數
cat .env | grep -E "LINE_|GEMINI_|DATABASE_"
```

**安全檢查**:
- [ ] API keys 已更新為生產 keys
- [ ] Database 指向生產資料庫
- [ ] HTTPS 已啟用
- [ ] CORS 設定正確

#### Step 2.2: 資料庫備份（生產）

```bash
# 備份生產資料庫
mysqldump -u [user] -p books_3f > backup_$(date +%Y%m%d_%H%M%S).sql

# 驗證備份檔案
ls -lh backup_*.sql
```

#### Step 2.3: 執行資料庫遷移（生產）

```bash
# 生產環境遷移（小心！）
npm run migrate:prod

# 驗證遷移成功
mysql -u [user] -p books_3f -e "DESC subscribers;"
```

**回滾計劃**:
如果遷移失敗：
```bash
# 還原資料庫
mysql -u [user] -p books_3f < backup_[timestamp].sql
```

#### Step 2.4: 部署應用程式

```bash
# 停止舊版本
pm2 stop line-bot

# 拉取最新代碼
git pull origin main

# 安裝依賴和建置
npm install --production
npm run build

# 啟動新版本
pm2 start dist/index.js --name line-bot

# 檢查日誌
pm2 logs line-bot --lines 50
```

#### Step 2.5: Smoke Tests（煙霧測試）

**自動化 Smoke Tests**:
```bash
# 基本健康檢查
curl https://yourbot.com/health

# Webhook 端點檢查
curl -X POST https://yourbot.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"events":[]}'
```

**手動 Smoke Tests**:
使用真實 LINE App 測試：

1. **基本功能**:
   - [ ] 發送「最新法寶」→ 收到 5 本書籍 Carousel
   - [ ] 發送「最新影音」→ 收到 10 個影音 Carousel
   - [ ] 點擊 Quick Reply → 訂閱成功

2. **資料正確性**:
   - [ ] 書籍資料來自 budaedu.org API
   - [ ] 影音資料來自 budaedu.org API
   - [ ] 封面圖正確顯示

3. **效能檢查**:
   - [ ] 回應時間 < 3 秒
   - [ ] 快取機制生效

---

### Phase 3: 監控與驗證

#### Step 3.1: 設定監控

**應用程式監控**:
```bash
# PM2 監控
pm2 monit

# 自訂健康檢查腳本
*/5 * * * * curl https://yourbot.com/health || echo "Health check failed"
```

**效能監控指標**:
- [ ] CPU 使用率 < 70%
- [ ] 記憶體使用率 < 80%
- [ ] 回應時間 < 3 秒
- [ ] 錯誤率 < 1%

#### Step 3.2: 日誌監控

```bash
# 查看即時日誌
pm2 logs line-bot --lines 100

# 監控錯誤日誌
tail -f /var/log/line-bot/error.log
```

**關注的錯誤**:
- API 連線失敗
- 資料庫查詢錯誤
- LINE Messaging API 錯誤
- 快取失效

#### Step 3.3: 用戶反饋收集

**第一週監控**:
- [ ] 監控用戶使用情況
- [ ] 收集用戶反饋
- [ ] 追蹤錯誤率
- [ ] 驗證快取命中率 > 80%

---

## 風險管理

### 已知風險

| 風險 | 影響 | 機率 | 緩解措施 | 應急計劃 |
|------|------|------|----------|----------|
| 資料庫遷移失敗 | High | Low | 事先測試遷移腳本 | 使用備份還原 |
| API 回應過慢 | Medium | Medium | 快取機制 (60s TTL) | 增加快取時間 |
| LINE Messaging API 限制 | Medium | Low | 監控 API 用量 | 實作請求節流 |
| 生產環境配置錯誤 | High | Low | 多次檢查環境變數 | 快速回滾到穩定版本 |
| 並發請求過載 | Medium | Low | 負載測試已完成 | 水平擴展 |

### 回滾計劃

如果部署後發現 Critical Bug：

```bash
# 1. 停止現有版本
pm2 stop line-bot

# 2. 回退到上一個版本
git checkout [previous-stable-tag]
npm install
npm run build

# 3. 還原資料庫（如果有遷移）
mysql -u [user] -p books_3f < backup_[timestamp].sql

# 4. 重新啟動
pm2 start dist/index.js --name line-bot

# 5. 驗證回滾成功
curl https://yourbot.com/health
```

---

## 上線公告

### 內部公告

**工程團隊**:
> M2 Dharma Media Feature 已部署到生產環境！  
> - 新功能：「最新法寶」、「最新影音」  
> - 測試通過率：95.65%  
> - 請監控未來 24 小時的錯誤日誌

### 用戶公告（可選）

**LINE Bot 推播**:
> 🎉 新功能上線！  
> 現在可以使用以下指令：  
> 📚 「最新法寶」- 查看最新書籍  
> 🎥 「最新影音」- 查看直播與影音  
> 💡 點擊 Quick Reply 按鈕即可訂閱更新通知！

---

## 部署後檢查清單

### 第一天
- [ ] 監控錯誤日誌（每小時檢查一次）
- [ ] 驗證所有功能正常運作
- [ ] 檢查資料庫寫入正常
- [ ] 確認 API 呼叫成功

### 第一週
- [ ] 收集用戶反饋
- [ ] 分析使用數據
- [ ] 調整快取策略（如需要）
- [ ] 優化效能（如需要）

### 第一個月
- [ ] 產生使用報告
- [ ] 評估功能成效
- [ ] 規劃下一階段優化

---

## 成功標準

部署被視為成功，當：
- ✅ 所有 Smoke Tests 通過
- ✅ 錯誤率 < 1%
- ✅ 用戶回饋正面
- ✅ 系統穩定運行 48 小時無 Critical Bug
- ✅ 效能符合 NFR 要求（< 3秒）

---

**部署負責人**: DevOps Team  
**緊急聯絡**: [電話/Email]  
**備註**: 本計劃基於 M3 QA 測試結果（95.65% 通過率）
