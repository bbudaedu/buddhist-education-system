# CI/CD Integration Guide
# Dharma Media E2E Tests

**Purpose**: 自動化測試整合到 CI/CD Pipeline  
**Framework**: GitHub Actions + Playwright  
**Last Updated**: 2025-11-26

---

## GitHub Actions Workflow

### 完整 Workflow 配置

建立 `.github/workflows/dharma-media-e2e.yml`:

```yaml
name: Dharma Media E2E Tests

on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'Line-bot-llm-mysql/src/handlers/dharmaMediaHandler.ts'
      - 'Line-bot-llm-mysql/src/services/flexMessageService.ts'
      - 'Line-bot-llm-mysql/src/services/dharmaBookService.ts'
      - 'Line-bot-llm-mysql/src/services/videoStreamingService.ts'
      - 'tests/e2e/dharma-media/**'
  
  pull_request:
    branches:
      - main
    paths:
      - 'Line-bot-llm-mysql/src/**'
      - 'tests/e2e/dharma-media/**'

  # 允許手動觸發
  workflow_dispatch:

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
          cache-dependency-path: Line-bot-llm-mysql/package-lock.json
      
      - name: Install dependencies (LINE Bot)
        run: |
          cd Line-bot-llm-mysql
          npm ci
      
      - name: Build LINE Bot
        run: |
          cd Line-bot-llm-mysql
          npm run build
      
      - name: Install E2E test dependencies
        run: |
          cd tests/e2e/dharma-media
          npm ci
      
      - name: Install Playwright browsers
        run: |
          cd tests/e2e/dharma-media
          npx playwright install chromium
      
      - name: Start LINE Bot (background)
        run: |
          cd Line-bot-llm-mysql
          npm start &
          echo $! > .bot.pid
        env:
          LINE_CHANNEL_SECRET: ${{ secrets.LINE_CHANNEL_SECRET }}
          LINE_CHANNEL_ACCESS_TOKEN: ${{ secrets.LINE_CHANNEL_ACCESS_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
      
      - name: Wait for service to be ready
        run: |
          timeout 60 bash -c 'until curl -f http://localhost:3000/health; do sleep 2; done'
      
      - name: Run E2E tests
        run: |
          cd tests/e2e/dharma-media
          npm test
        env:
          BASE_URL: http://localhost:3000
          CI: true
      
      - name: Stop LINE Bot
        if: always()
        run: |
          if [ -f Line-bot-llm-mysql/.bot.pid ]; then
            kill $(cat Line-bot-llm-mysql/.bot.pid) || true
          fi
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results-${{ matrix.node-version }}
          path: tests/e2e/dharma-media/test-results/
          retention-days: 30
      
      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report-${{ matrix.node-version }}
          path: tests/e2e/dharma-media/playwright-report/
          retention-days: 30
      
      - name: Upload test report (Markdown)
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: markdown-report-${{ matrix.node-version }}
          path: tests/e2e/dharma-media/test-results/test-report.md
          retention-days: 30
      
      - name: Comment PR with test results
        if: github.event_name == 'pull_request' && always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const reportPath = 'tests/e2e/dharma-media/test-results/test-report.md';
            
            if (fs.existsSync(reportPath)) {
              const report = fs.readFileSync(reportPath, 'utf8');
              
              // Extract summary
              const summaryMatch = report.match(/## 📊 測試統計([\s\S]*?)---/);
              const summary = summaryMatch ? summaryMatch[1] : 'Report not available';
              
              await github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: `## 🧪 E2E Test Results\n\n${summary}\n\n[View full report in artifacts]`
              });
            }
      
      - name: Fail if tests failed
        if: failure()
        run: |
          echo "E2E tests failed!"
          exit 1
```

---

## Secrets 配置

在 GitHub Repository Settings → Secrets and variables → Actions 中設定：

```
LINE_CHANNEL_SECRET=your_test_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_test_access_token
GEMINI_API_KEY=your_gemini_api_key
TEST_DATABASE_URL=mysql://user:pass@host:3306/books_3f_test
```

---

## 通知設定

### Slack 通知

新增 Slack notification step:

```yaml
      - name: Notify Slack on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            🔴 Dharma Media E2E Tests Failed!
            Branch: ${{ github.ref }}
            Commit: ${{ github.sha }}
            Author: ${{ github.actor }}
          fields: repo,message,commit,author,action,eventName,ref,workflow
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
      
      - name: Notify Slack on success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: |
            ✅ Dharma Media E2E Tests Passed!
            All tests completed successfully.
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Email 通知

```yaml
      - name: Send email on failure
        if: failure()
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 465
          username: ${{ secrets.MAIL_USERNAME }}
          password: ${{ secrets.MAIL_PASSWORD }}
          subject: E2E Tests Failed - Dharma Media
          to: qa-team@example.com,devops@example.com
          from: GitHub Actions
          body: |
            E2E tests for Dharma Media feature have failed.
            
            Branch: ${{ github.ref }}
            Commit: ${{ github.sha }}
            
            Please check the test results in GitHub Actions artifacts.
```

---

## 分支保護規則

在 GitHub Repository Settings → Branches → Branch protection rules:

```yaml
Branch name pattern: main

Require status checks to pass before merging:
  - ✅ e2e-tests

Require branches to be up to date before merging:
  - ✅ Enabled
```

---

## 測試覆蓋率報告

### 整合 Code Coverage

修改 `playwright.config.ts`:

```typescript
export default defineConfig({
  // ... other config
  
  use: {
    // Collect coverage
    coverage: {
      enabled: true,
      provider: 'v8',
    }
  },
});
```

GitHub Actions step:

```yaml
      - name: Generate coverage report
        run: |
          cd tests/e2e/dharma-media
          npx nyc report --reporter=lcov
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./tests/e2e/dharma-media/coverage/lcov.info
          flags: e2e-tests
          name: dharma-media-e2e
```

---

## 定期測試排程

### 每日測試

```yaml
on:
  schedule:
    # 每天 UTC 02:00 (台北時間 10:00)
    - cron: '0 2 * * *'
```

### 完整排程範例

```yaml
name: Nightly E2E Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 02:00 UTC
  workflow_dispatch:      # Manual trigger

jobs:
  nightly-tests:
    runs-on: ubuntu-latest
    
    steps:
      # ... (same as above)
      
      - name: Generate nightly report
        if: always()
        run: |
          cd tests/e2e/dharma-media
          npm run report:generate
      
      - name: Upload nightly report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: nightly-report-$(date +%Y%m%d)
          path: tests/e2e/dharma-media/test-results/
```

---

## Docker 整合（進階）

### Dockerfile for Testing

```dockerfile
FROM mcr.microsoft.com/playwright:v1.40.0-focal

WORKDIR /app

# Copy package files
COPY Line-bot-llm-mysql/package*.json ./Line-bot-llm-mysql/
COPY tests/e2e/dharma-media/package*.json ./tests/e2e/dharma-media/

# Install dependencies
RUN cd Line-bot-llm-mysql && npm ci
RUN cd tests/e2e/dharma-media && npm ci

# Copy source code
COPY Line-bot-llm-mysql/ ./Line-bot-llm-mysql/
COPY tests/e2e/dharma-media/ ./tests/e2e/dharma-media/

# Build application
RUN cd Line-bot-llm-mysql && npm run build

CMD ["npm", "test"]
```

### GitHub Actions with Docker

```yaml
jobs:
  docker-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build test container
        run: docker build -t dharma-media-tests -f Dockerfile.test .
      
      - name: Run tests in container
        run: |
          docker run --rm \
            -e LINE_CHANNEL_SECRET=${{ secrets.LINE_CHANNEL_SECRET }} \
            -e LINE_CHANNEL_ACCESS_TOKEN=${{ secrets.LINE_CHANNEL_ACCESS_TOKEN }} \
            -v $(pwd)/test-results:/app/tests/e2e/dharma-media/test-results \
            dharma-media-tests
```

---

## 最佳實踐

### ✅ 建議做法

1. **快速反饋**
   - 保持測試執行時間 < 5 分鐘
   - 失敗時立即通知

2. **測試隔離**
   - 使用獨立測試資料庫
   - 每次測試後清理資料

3. **版本管理**
   - 鎖定 Playwright 版本
   - 使用 package-lock.json

4. **Artifacts 保留**
   - 保留測試報告 30 天
   - 保留截圖和影片（失敗時）

### ❌ 避免做法

1. **不要**在生產資料庫上執行測試
2. **不要**在 CI 中使用真實的 API keys（使用 test keys）
3. **不要**忽略間歇性失敗（flaky tests）
4. **不要**讓測試執行時間過長（> 10 分鐘）

---

## Troubleshooting

### 常見問題

**1. Playwright 安裝失敗**
```yaml
- name: Install Playwright with retry
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 5
    max_attempts: 3
    command: cd tests/e2e/dharma-media && npx playwright install chromium
```

**2. 服務未啟動**
```yaml
- name: Debug service status
  if: failure()
  run: |
    curl -v http://localhost:3000/health || true
    cat Line-bot-llm-mysql/logs/*.log || true
```

**3. 測試逾時**
```yaml
# 增加逾時時間
- name: Run E2E tests
  timeout-minutes: 15
  run: npm test
```

---

**維護者**: DevOps Team  
**文檔版本**: 1.0  
**最後更新**: 2025-11-26
