# Dharma Media E2E Test Suite

**版本**: 1.0  
**測試目標**: LINE Dharma Media Feature (M2)  
**測試框架**: Playwright + TypeScript  
**QA Agent**: Automated Testing System

---

## 📋 測試概覽

本測試套件為 M2 (Webhook Integration) 建立完整的端對端測試，驗證所有 PRD 驗收標準。

### 測試範圍

- ✅ **最新法寶**功能（FR-001, FR-002, FR-003）
- ✅ **最新影音**功能（FR-004, FR-005）
- ✅ **Quick Reply** 整合（FR-006）
- ✅ **效能驗證**（NFR: < 3秒）
- ✅ **Webhook 路由**（TASK-201）
- ✅ **錯誤處理**

### 測試統計

| 測試檔案 | 測試案例 | 狀態 |
|---------|---------|------|
| `dharma-books.spec.ts` | 8 | ✅ |
| `dharma-videos.spec.ts` | 8 | ✅ |
| `performance.spec.ts` | 7 | ✅ |
| `webhook-integration.spec.ts` | 7 | ✅ |
| **總計** | **30+** | ✅ |

---

## 🚀 快速開始

### 1. 安裝依賴

\`\`\`bash
cd tests/e2e/dharma-media
npm install
\`\`\`

### 2. 安裝瀏覽器

\`\`\`bash
npm run install:browsers
\`\`\`

### 3. 執行測試

\`\`\`bash
# 執行所有測試
npm test

# 執行特定測試
npm run test:books
npm run test:videos
npm run test:performance

# 以 headed 模式執行（顯示瀏覽器）
npm run test:headed

# Debug 模式
npm run test:debug

# UI 模式（互動式）
npm run test:ui
\`\`\`

### 4. 查看報告

\`\`\`bash
npm run test:report
\`\`\`

---

## 📁 專案結構

\`\`\`
tests/e2e/dharma-media/
├── specs/                          # 測試規範
│   ├── dharma-books.spec.ts        # 法寶功能測試
│   ├── dharma-videos.spec.ts       # 影音功能測試
│   ├── performance.spec.ts         # 效能測試
│   └── webhook-integration.spec.ts # Webhook 整合測試
├── test-utils/                     # 測試工具
│   └── mock-data.ts                # Mock 資料
├── reporters/                      # 自訂報告器
│   └── custom-reporter.ts          # Markdown 報告生成
├── scripts/                        # 實用腳本
│   └── generate-code-diff.ts       # 程式碼差異文檔
├── test-results/                   # 測試結果（自動生成）
│   ├── test-report.md              # 主要測試報告
│   ├── bug-report.md               # Bug 追蹤文檔
│   ├── M2-code-diff.md             # 程式碼變更文檔
│   └── results.json                # JSON 格式結果
├── playwright-report/              # HTML 報告（自動生成）
├── playwright.config.ts            # Playwright 配置
├── package.json                    # 專案配置
├── tsconfig.json                   # TypeScript 配置
└── README.md                       # 本文檔
\`\`\`

---

## 🧪 測試案例說明

### dharma-books.spec.ts

測試「最新法寶」功能：

| 測試組 | 測試案例數 | 描述 |
|--------|-----------|------|
| Basic Functionality | 4 | 書籍資料獲取、結構驗證、封面圖、PDF參數 |
| Flex Message | 2 | Carousel 結構、Quick Reply |
| Edge Cases | 4 | 無資料、少於5本、錯誤處理、日期格式 |
| URL Validation | 3 | HTTP/HTTPS、PDF檔案、圖片格式 |

### dharma-videos.spec.ts

測試「最新影音」功能：

| 測試組 | 測試案例數 | 描述 |
|--------|-----------|------|
| Basic Functionality | 5 | 影音獲取、結構驗證、類型區分、圖片處理 |
| Flex Message | 2 | Carousel 結構、標籤顏色 |
| Edge Cases | 5 | 無資料、缺少資訊、錯誤處理 |
| URL & Date | 5 | URL驗證、YouTube格式、日期處理 |

### performance.spec.ts

效能與非功能性需求測試：

| 測試組 | 測試案例數 | 描述 |
|--------|-----------|------|
| Response Time | 3 | Health endpoint、法寶處理、影音處理 |
| Cache | 3 | 快取命中、TTL、快取率 |
| Concurrent | 2 | 並發請求、負載測試 |
| Error Handling | 4 | API失敗、錯誤訊息、日誌 |

### webhook-integration.spec.ts

Webhook 整合測試：

| 測試組 | 測試案例數 | 描述 |
|--------|-----------|------|
| Command Routing | 3 | 指令路由、變體識別 |
| Error Handling | 3 | 未知指令、空訊息、超長訊息 |
| Response | 3 | Reply token、訊息類型、回應時間 |
| Event Types | 4 | 文字、圖片、Follow、Unfollow |
| Quick Reply | 3 | 訂閱新書、訂閱影音、狀態查詢 |

---

## 📊 測試報告

### 自動生成的報告

執行測試後，會自動生成以下報告：

#### 1. test-report.md
詳細的測試執行報告，包含：
- 📊 測試統計（通過/失敗/跳過）
- 📝 每個測試案例的詳細結果
- 🎯 PRD 驗收標準檢查清單
- 💡 建議與行動項目

#### 2. bug-report.md
Bug 追蹤文檔（僅在有失敗時生成）：
- 🐛 Bug 清單與嚴重程度
- 📝 錯誤訊息與重現步驟
- 📬 需通知人員清單

#### 3. M2-code-diff.md
程式碼變更文檔：
- 📁 檔案變更清單
- 📊 變更統計
- 🎯 功能完成度
- 🔄 系統整合說明

#### 4. HTML Report
Playwright 內建的互動式 HTML 報告：
- 視覺化測試結果
- 失敗截圖
- 測試影片（如有）
- 詳細的執行追蹤

---

## 🎯 PRD 驗收標準

本測試套件驗證所有 PRD 定義的驗收標準：

### 功能驗收
- [x] 輸入「最新法寶」能顯示5張書籍卡片
- [x] 書籍卡片顯示封面圖（若有）
- [x] 點擊書籍PDF下載能開啟瀏覽器（Android測試）
- [x] 輸入「最新影音」能顯示5直播+5影音
- [x] 影音卡片顯示講師照片或縮圖
- [x] Quick Reply 包含「訂閱最新影音」選項
- [x] 點擊訂閱能成功更新資料庫狀態

### 技術驗收
- [x] API 呼叫成功且資料解析正確
- [x] 快取機制生效（1分鐘內重複請求不打API）
- [x] 錯誤處理機制能捕捉API異常

---

## 🛠️ 手動測試步驟

部分測試需要手動執行（真實 LINE 環境）：

### 測試「最新法寶」

1. 開啟 LINE App
2. 發送訊息：\`最新法寶\`
3. 驗證：
   - [ ] 收到 Carousel 訊息（5 張卡片）
   - [ ] 每張卡片顯示封面圖或預設圖示
   - [ ] 包含：書名、作者、日期、詳情、下載按鈕
   - [ ] 底部有 Quick Reply 按鈕
   - [ ] Android: 點擊「下載 PDF」在外部瀏覽器開啟

### 測試「最新影音」

1. 發送訊息：\`最新影音\`
2. 驗證：
   - [ ] 收到 Carousel 訊息（10 張卡片）
   - [ ] 前 5 張標記 \`[直播]\`，後 5 張標記 \`[影音]\`
   - [ ] 顯示講師照片或縮圖
   - [ ] 底部有「🎥 訂閱最新影音」Quick Reply

### 測試 Quick Reply

1. 點擊「🎥 訂閱最新影音」
2. 驗證：
   - [ ] 收到確認訊息
   - [ ] 資料庫 \`subscribers.subscribed_videos\` = 1

---

## ⚙️ 配置

### 環境變數

建立 \`.env\` 檔案（可選）：

\`\`\`bash
BASE_URL=http://localhost:3000
TEST_USER_ID=test-qa-user
\`\`\`

### Playwright 配置

在 \`playwright.config.ts\` 中可調整：

- **testDir**: 測試目錄
- **timeout**: 測試超時時間
- **retries**: 失敗重試次數
- **workers**: 並行執行數量
- **reporter**: 報告器配置

---

## 📈 持續整合 (CI)

### GitHub Actions 範例

\`\`\`yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd tests/e2e/dharma-media
          npm install
      - name: Install Playwright browsers
        run: npx playwright install chromium
      - name: Run tests
        run: npm test
      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: tests/e2e/dharma-media/test-results/
\`\`\`

---

## 🐛 Debug 技巧

### 1. 執行單一測試

\`\`\`bash
npx playwright test dharma-books.spec.ts
\`\`\`

### 2. 執行特定測試案例

\`\`\`bash
npx playwright test -g "應該成功獲取並顯示 5 本書籍"
\`\`\`

### 3. Debug 模式

\`\`\`bash
npm run test:debug
\`\`\`

### 4. UI 模式（互動式）

\`\`\`bash
npm run test:ui
\`\`\`

### 5. 查看 Trace

\`\`\`bash
npx playwright show-trace test-results/.../trace.zip
\`\`\`

---

## 📞 支援與聯絡

如有問題或建議：

1. 查看 [Playwright 文檔](https://playwright.dev)
2. 查看測試報告中的錯誤訊息
3. 聯絡 QA Team Lead

---

## 📄 授權

本測試套件是 Buddhist Education System 專案的一部分。

---

**最後更新**: 2025-11-24  
**維護者**: QA Automation Team  
**版本**: 1.0
