---
description: QA 測試工作流程 - E2E 測試執行與驗收標準檢查
---

# QA Testing Workflow

此工作流程定義了完整的 QA 測試流程，從測試準備到驗收簽核，確保每個功能都符合 PRD 驗收標準。

---

## 測試階段概覽

```
PRD 定義
    ↓
M0-M2 開發
    ↓
M3 測試階段 ← 你在這裡
    ├─ 單元測試
    ├─ 整合測試
    ├─ E2E 測試
    └─ 手動驗證
    ↓
驗收簽核
    ↓
M4 部署
```

---

## 步驟 1: 測試準備

### 1.1 閱讀測試目標

在開始測試前，務必閱讀以下文檔：

```bash
# 必讀文檔
- docs/features/[feature-name]/PRD.md          # 驗收標準
- docs/features/[feature-name]/TASKS.md        # 實作範圍
- docs/features/[feature-name]/MILESTONES.md   # 里程碑定義
```

### 1.2 建立測試環境

// turbo
```bash
# 進入測試目錄
cd tests/e2e/[feature-name]

# 安裝依賴
npm install

# 安裝瀏覽器（Playwright）
npx playwright install chromium
```

### 1.3 配置環境變數

```bash
# 複製環境變數模板
cp .env.example .env

# 編輯配置
# - BASE_URL: 測試目標 URL
# - TEST_USER_ID: 測試用戶 ID
# - 其他必要的 API keys
```

---

## 步驟 2: 執行自動化測試

### 2.1 單元測試

```bash
# Node.js/TypeScript 專案
cd Line-bot-llm-mysql
npm test

# Python 專案
cd ebook
pytest tests/
```

**驗收標準**:
- [ ] 單元測試覆蓋率 ≥ 80%
- [ ] 所有測試通過
- [ ] 無已知的測試失敗

### 2.2 E2E 自動化測試

```bash
cd tests/e2e/[feature-name]

# 執行所有測試
npm test

# 執行特定測試套件
npm run test:books      # 書籍功能
npm run test:videos     # 影音功能
npm run test:performance # 效能測試

# UI 模式（互動式除錯）
npm run test:ui

# Debug 模式
npm run test:debug
```

**測試覆蓋要求**:
- [ ] 所有 PRD 功能驗收標準（FR-XXX）
- [ ] 所有技術驗收標準（NFR）
- [ ] 邊緣案例與錯誤處理
- [ ] URL 與資料格式驗證

### 2.3 效能測試

```bash
# 執行效能測試套件
npm run test:performance
```

**效能基準**:
- [ ] API 回應時間 < 3 秒
- [ ] 快取機制生效（60 秒 TTL）
- [ ] 並發請求處理正常
- [ ] 系統可用性 > 99%

---

## 步驟 3: 測試報告生成

### 3.1 自動生成報告

測試完成後，自動生成以下報告：

```bash
# Playwright 會自動生成：
- playwright-report/index.html    # HTML 互動報告
- test-results/results.json        # JSON 格式結果
- test-results/junit.xml           # JUnit 格式（CI/CD 用）
- test-results/test-report.md      # 自訂 Markdown 報告
- test-results/bug-report.md       # Bug 追蹤文檔（如有失敗）
```

### 3.2 查看測試報告

```bash
# 開啟 HTML 報告
npm run test:report

# 查看 Markdown 報告
cat test-results/test-report.md
```

### 3.3 生成程式碼差異文檔

```bash
# 生成 M2 程式碼變更文檔
npm run report:diff
```

---

## 步驟 4: PRD 驗收標準檢查

### 4.1 功能驗收檢查清單

根據 PRD 定義，逐項檢查：

```markdown
## 功能驗收 (Functional Acceptance)

### FR-001: [功能描述]
- [ ] 測試案例: test-name.spec.ts:行號
- [ ] 狀態: ✅ Passed / ❌ Failed
- [ ] 備註: [如有失敗，說明原因]

### FR-002: [功能描述]
- [ ] 測試案例: test-name.spec.ts:行號
- [ ] 狀態: ✅ Passed / ❌ Failed
- [ ] 備註:

[繼續所有 FR 項目...]
```

### 4.2 技術驗收檢查清單

```markdown
## 技術驗收 (Technical Acceptance)

### NFR: API 回應時間
- [ ] 測試結果: < 3 秒
- [ ] 實際效能: [X] ms
- [ ] 狀態: ✅ / ❌

### NFR: 快取機制
- [ ] 測試結果: 60 秒 TTL
- [ ] 快取命中率: [X]%
- [ ] 狀態: ✅ / ❌

[繼續所有 NFR 項目...]
```

### 4.3 計算通過率

```bash
# 從測試報告提取數據
總測試案例: [N]
通過: [X] ([X/N * 100]%)
失敗: [Y] ([Y/N * 100]%)
跳過: [Z] ([Z/N * 100]%)
```

**驗收標準**:
- 🟢 **優秀**: 通過率 ≥ 95%
- 🟡 **可接受**: 通過率 ≥ 90%
- 🔴 **需改進**: 通過率 < 90%

---

## 步驟 5: 手動測試

某些測試需要在真實環境中手動執行：

### 5.1 LINE Bot 真實環境測試

**測試環境準備**:
- [ ] LINE Bot 已部署到測試環境
- [ ] 加入測試 Bot 為好友
- [ ] 準備測試資料

**測試執行**:

#### 測試「最新法寶」
1. 發送訊息：`最新法寶`
2. 驗證：
   - [ ] 收到 Carousel 訊息（5 張卡片）
   - [ ] 每張卡片顯示封面圖或預設圖示
   - [ ] 包含：書名、作者、日期、詳情、下載按鈕
   - [ ] 底部有 Quick Reply 按鈕
   - [ ] [Android] 點擊「下載 PDF」在外部瀏覽器開啟

#### 測試「最新影音」
1. 發送訊息：`最新影音`
2. 驗證：
   - [ ] 收到 Carousel 訊息（10 張卡片）
   - [ ] 前 5 張標記 `[直播]`，後 5 張標記 `[影音]`
   - [ ] 顯示講師照片或縮圖
   - [ ] 底部有「🎥 訂閱最新影音」Quick Reply

#### 測試 Quick Reply
1. 點擊「🎥 訂閱最新影音」
2. 驗證：
   - [ ] 收到確認訊息
   - [ ] 資料庫 `subscribers.subscribed_videos = 1`

### 5.2 跨瀏覽器/裝置測試

**測試矩陣**:
- [ ] LINE iOS App
- [ ] LINE Android App
- [ ] 不同網路環境（WiFi, 4G, 5G）

---

## 步驟 6: Bug 處理流程

### 6.1 Bug 嚴重程度分類

**🔴 Critical (P0)**:
- 核心功能無法使用
- 資料遺失或損壞
- 安全性漏洞

**🟠 High (P1)**:
- 主要功能受影響
- 效能嚴重下降
- PRD 驗收標準未通過

**🟡 Medium (P2)**:
- 次要功能問題
- UI/UX 小瑕疵
- 效能輕微下降

**🟢 Low (P3)**:
- 文字錯誤
- UI 美化建議
- 邊緣案例問題

### 6.2 Bug 記錄格式

自動生成的 `bug-report.md` 包含：

```markdown
## Bug #[N]: [標題]

**嚴重程度**: 🔴/🟠/🟡/🟢
**狀態**: Open / In Progress / Fixed / Closed
**發現於**: E2E 測試 / 手動測試

### 問題描述
[詳細描述]

### 重現步驟
1. [步驟 1]
2. [步驟 2]
3. [觀察結果]

### 期望行為
[應該如何]

### 實際行為
[實際如何]

### 錯誤訊息
```
[錯誤訊息或截圖]
```

### 建議修復
[如有建議]
```

### 6.3 Bug 通知機制

```bash
# 如果有 P0/P1 Bug，自動通知
npm run notify:bugs
```

**通知對象**:
- Backend Engineer (程式碼問題)
- QA Team Lead (測試問題)
- Feature Owner (驗收決策)

---

## 步驟 7: 驗收決策

### 7.1 驗收決策矩陣

| 通過率 | P0 Bug | P1 Bug | 決策 |
|--------|--------|--------|------|
| ≥ 95% | 0 | 0-2 | ✅ **批准部署** |
| ≥ 90% | 0 | 3-5 | ⚠️ **條件批准**（修復 P1 後部署）|
| ≥ 85% | 0 | >5 | 🔴 **不批准**（需修復）|
| <85% | - | - | 🔴 **不批准** |
| 任何 | >0 | - | 🔴 **不批准**（Critical Bug 必須修復）|

### 7.2 QA 簽核文檔

建立驗收簽核文檔：

```markdown
# QA 驗收簽核 - [Feature Name]

## 測試執行摘要
- **執行日期**: YYYY-MM-DD
- **測試案例**: [N] 個
- **通過率**: [X]%
- **執行時間**: [X] 秒/分鐘

## PRD 驗收標準
- ✅ 功能驗收: [X/N] 通過
- ✅ 技術驗收: [X/N] 通過

## Bug 統計
- 🔴 P0: [N] 個
- 🟠 P1: [N] 個
- 🟡 P2: [N] 個
- 🟢 P3: [N] 個

## QA 決策
**狀態**: ✅ 批准部署 / ⚠️ 條件批准 / 🔴 不批准

**理由**: [說明]

**建議行動**: [如有]

---
**QA 負責人**: [姓名]
**簽核日期**: YYYY-MM-DD
```

---

## 步驟 8: CI/CD 整合

### 8.1 GitHub Actions 配置

建立 `.github/workflows/e2e-tests.yml`:

```yaml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd tests/e2e/[feature-name]
          npm install
      
      - name: Install Playwright
        run: npx playwright install chromium
      
      - name: Run E2E tests
        run: |
          cd tests/e2e/[feature-name]
          npm test
      
      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: tests/e2e/[feature-name]/test-results/
      
      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: tests/e2e/[feature-name]/playwright-report/
```

### 8.2 測試失敗通知

配置 Slack/Email 通知：

```yaml
      - name: Notify on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'E2E Tests Failed!'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 最佳實踐

### ✅ 應該做的

1. **測試前閱讀 PRD**
   - 理解驗收標準
   - 了解功能範圍
   - 識別關鍵測試點

2. **保持測試獨立**
   - 每個測試獨立執行
   - 不依賴執行順序
   - 清理測試數據

3. **及早測試、頻繁測試**
   - 開發過程中持續測試
   - 不要等到最後才測試
   - 使用 CI/CD 自動化

4. **記錄測試結果**
   - 截圖保存失敗案例
   - 詳細記錄 Bug
   - 追蹤測試覆蓋率

### ❌ 避免做的

1. **不要跳過測試**
   - 即使時間緊迫，也要執行關鍵測試
   - 不要假設「應該沒問題」

2. **不要只測試正常流程**
   - 測試邊緣案例
   - 測試錯誤處理
   - 測試極端輸入

3. **不要隱瞞測試失敗**
   - 誠實報告問題
   - 及早通知團隊
   - 不要「改」測試讓它通過

4. **不要忽視效能測試**
   - 效能是用戶體驗的一部分
   - 設定合理的效能基準
   - 監控效能趨勢

---

## 檢查清單

測試流程運作良好的標誌：

- ✅ 測試可以自動執行
- ✅ 測試報告自動生成
- ✅ 測試失敗會立即通知
- ✅ 所有 PRD 驗收標準有測試覆蓋
- ✅ 測試通過率穩定在 95% 以上
- ✅ Bug 被及早發現和修復
- ✅ 團隊信任測試結果
- ✅ 測試成為部署的守門員

---

## 下一步

- 執行完成後，使用 [milestone-tracking](./milestone-tracking.md) 更新進度
- 通過驗收後，使用 [artifact-generation](./artifact-generation.md) 生成最終文檔
- 準備 M4 部署，參考部署工作流程（待建立）

---

**記住**：好的測試不是為了找碴，而是為了確保用戶獲得高品質的產品！🎯
