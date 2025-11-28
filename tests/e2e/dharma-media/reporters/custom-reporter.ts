import type {
    FullConfig, FullResult, Reporter, Suite, TestCase, TestResult
} from '@playwright/test/reporter';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Custom Playwright Reporter for Dharma Media E2E Tests
 * 
 * Generates:
 * - Detailed test execution report (Markdown)
 * - Test summary statistics
 * - Bug tracking document for failures
 */

class DharmaMediaReporter implements Reporter {
    private startTime: number = 0;
    private testResults: Array<{
        title: string;
        status: string;
        duration: number;
        error?: string;
    }> = [];

    onBegin(config: FullConfig, suite: Suite) {
        this.startTime = Date.now();
        console.log(`\n🧪 Starting Dharma Media E2E Tests...`);
        console.log(`   Total tests: ${suite.allTests().length}`);
    }

    onTestEnd(test: TestCase, result: TestResult) {
        this.testResults.push({
            title: test.title,
            status: result.status,
            duration: result.duration,
            error: result.error?.message
        });

        const icon = result.status === 'passed' ? '✅' :
            result.status === 'failed' ? '❌' :
                result.status === 'skipped' ? '⏭️' : '⚠️';

        console.log(`${icon} ${test.title} (${result.duration}ms)`);

        if (result.error) {
            console.log(`   Error: ${result.error.message}`);
        }
    }

    async onEnd(result: FullResult) {
        const duration = Date.now() - this.startTime;

        console.log(`\n📊 Test Execution Complete`);
        console.log(`   Duration: ${Math.round(duration / 1000)}s`);
        console.log(`   Status: ${result.status}`);

        // Generate reports
        await this.generateMarkdownReport(result, duration);
        await this.generateBugReport();

        console.log(`\n📄 Reports generated in test-results/\n`);
    }

    private async generateMarkdownReport(result: FullResult, duration: number) {
        const passed = this.testResults.filter(t => t.status === 'passed').length;
        const failed = this.testResults.filter(t => t.status === 'failed').length;
        const skipped = this.testResults.filter(t => t.status === 'skipped').length;
        const total = this.testResults.length;

        const passRate = ((passed / total) * 100).toFixed(2);

        const report = `
# Dharma Media E2E Test Report

**執行時間**: ${new Date().toLocaleString('zh-TW')}  
**執行時長**: ${Math.round(duration / 1000)} 秒  
**測試狀態**: ${result.status.toUpperCase()}  

---

## 📊 測試統計

| 指標 | 數量 | 百分比 |
|------|------|--------|
| ✅ 通過 | ${passed} | ${passRate}% |
| ❌ 失敗 | ${failed} | ${((failed / total) * 100).toFixed(2)}% |
| ⏭️ 跳過 | ${skipped} | ${((skipped / total) * 100).toFixed(2)}% |
| **總計** | **${total}** | **100%** |

---

## 📝 測試結果詳情

${this.testResults.map((test, index) => {
            const icon = test.status === 'passed' ? '✅' :
                test.status === 'failed' ? '❌' :
                    test.status === 'skipped' ? '⏭️' : '⚠️';

            let details = `### ${index + 1}. ${icon} ${test.title}\n`;
            details += `- **狀態**: ${test.status}\n`;
            details += `- **執行時間**: ${test.duration}ms\n`;

            if (test.error) {
                details += `- **錯誤訊息**: \`${test.error}\`\n`;
            }

            return details;
        }).join('\n')}

---

## 🎯 PRD 驗收標準檢查

### 功能驗收
- [ ] 輸入「最新法寶」能顯示5張書籍卡片 ${this.getTestStatus('應該成功獲取並顯示 5 本書籍')}
- [ ] 書籍卡片顯示封面圖（若有） ${this.getTestStatus('應該正確處理書籍封面圖 URL')}
- [ ] 點擊書籍PDF下載能開啟瀏覽器 ${this.getTestStatus('PDF URL 應包含 openExternalBrowser 參數')}
- [ ] 輸入「最新影音」能顯示5直播+5影音 ${this.getTestStatus('應該成功獲取 10 筆影音資料')}
- [ ] 影音卡片顯示講師照片或縮圖 ${this.getTestStatus('應該處理講師照片 URL')}
- [ ] Quick Reply 包含「訂閱最新影音」選項 ${this.getTestStatus('Quick Reply 應包含「訂閱最新影音」選項')}

### 技術驗收
- [ ] API 呼叫成功且資料解析正確 ${this.getTestStatus('書籍資料結構應包含所有必要欄位')}
- [ ] 快取機制生效 ${this.getTestStatus('60 秒內重複請求應使用快取')}
- [ ] 錯誤處理機制能捕捉異常 ${this.getTestStatus('應該優雅處理 API 失敗')}

---

## 💡 建議與行動項目

${failed > 0 ? `
### ⚠️ 需要修復的問題
${this.testResults.filter(t => t.status === 'failed').map(t =>
            `- **${t.title}**: ${t.error || '未知錯誤'}`
        ).join('\n')}
` : '### ✨ 所有測試通過！無需修復。'}

---

**報告生成時間**: ${new Date().toISOString()}  
**生成工具**: Dharma Media Custom Reporter v1.0
    `.trim();

        const reportPath = path.join('test-results', 'test-report.md');
        fs.mkdirSync(path.dirname(reportPath), { recursive: true });
        fs.writeFileSync(reportPath, report);
    }

    private async generateBugReport() {
        const failures = this.testResults.filter(t => t.status === 'failed');

        if (failures.length === 0) {
            return; // No bugs to report
        }

        const bugReport = `
# Bug Report - Dharma Media E2E Tests

**發現時間**: ${new Date().toLocaleString('zh-TW')}  
**測試環境**: E2E Automated Testing  
**Bug 數量**: ${failures.length}

---

${failures.map((bug, index) => `
## Bug #${index + 1}: ${bug.title}

**嚴重程度**: ${this.getBugSeverity(bug)}  
**狀態**: 🔴 Open  
**發現於**: E2E測試

### 問題描述
測試案例 "${bug.title}" 執行失敗。

### 錯誤訊息
\`\`\`
${bug.error || '未提供錯誤訊息'}
\`\`\`

### 重現步驟
1. 執行 E2E 測試套件
2. 運行測試: "${bug.title}"
3. 觀察失敗結果

### 期望行為
測試應該通過，符合 PRD 驗收標準。

### 實際行為
測試失敗，顯示上述錯誤訊息。

### 建議修復
請工程師團隊檢查相關程式碼並修復。

---
`).join('\n')}

## 📬 通知清單

需要通知以下人員：
- ✉️ Backend Engineer (Dharma Media Handler)
- ✉️ QA Team Lead
- ✉️ Feature Owner

---

**報告生成時間**: ${new Date().toISOString()}
    `.trim();

        const bugReportPath = path.join('test-results', 'bug-report.md');
        fs.writeFileSync(bugReportPath, bugReport);
    }

    private getTestStatus(testTitle: string): string {
        const test = this.testResults.find(t => t.title.includes(testTitle));
        return test?.status === 'passed' ? '✅' : '❌';
    }

    private getBugSeverity(bug: { title: string; error?: string }): string {
        if (bug.title.includes('FR-') || bug.title.includes('NFR')) {
            return '🔴 High (PRD Requirement)';
        } else if (bug.error?.includes('Error') || bug.error?.includes('Failed')) {
            return '🟠 Medium';
        }
        return '🟡 Low';
    }
}

export default DharmaMediaReporter;
