const fs = require('fs');
const path = require('path');

/**
 * 自動化系統設置腳本
 */
class AutomationSetup {
  constructor() {
    this.envPath = path.join(__dirname, '.env');
  }

  /**
   * 檢查必要的配置
   */
  checkConfiguration() {
    console.log('🔍 檢查自動化配置...\n');

    // 檢查 .env 文件
    if (!fs.existsSync(this.envPath)) {
      console.log('❌ .env 文件不存在');
      return false;
    }

    const envContent = fs.readFileSync(this.envPath, 'utf8');
    const requiredVars = [
      'LINE_CHANNEL_SECRET',
      'LINE_CHANNEL_ACCESS_TOKEN',
      'GEMINI_API_KEY',
      'DB_HOST',
      'DB_USER',
      'DB_PASSWORD',
      'DB_NAME',
      'SCHEDULER_ENABLED',
      'SCHEDULER_DAILY_TIME',
      'EBOOK_PROCESSOR_PATH'
    ];

    const missingVars = [];
    requiredVars.forEach(varName => {
      if (!envContent.includes(varName + '=')) {
        missingVars.push(varName);
      }
    });

    if (missingVars.length > 0) {
      console.log('❌ 缺少必要的環境變數:');
      missingVars.forEach(varName => {
        console.log(`   - ${varName}`);
      });
      return false;
    }

    console.log('✅ 環境變數配置完整');
    return true;
  }

  /**
   * 檢查 Python 環境
   */
  async checkPythonEnvironment() {
    console.log('\n🐍 檢查 Python 環境...');

    try {
      const { spawn } = require('child_process');
      
      return new Promise((resolve) => {
        const python = spawn('python', ['--version']);
        
        python.stdout.on('data', (data) => {
          console.log(`✅ Python 版本: ${data.toString().trim()}`);
          resolve(true);
        });

        python.stderr.on('data', (data) => {
          console.log(`✅ Python 版本: ${data.toString().trim()}`);
          resolve(true);
        });

        python.on('error', () => {
          console.log('❌ Python 未安裝或不在 PATH 中');
          resolve(false);
        });
      });
    } catch (error) {
      console.log('❌ 無法檢查 Python 環境');
      return false;
    }
  }

  /**
   * 檢查 ebook 處理器
   */
  checkEbookProcessor() {
    console.log('\n📚 檢查 ebook 處理器...');

    const ebookPath = path.join(__dirname, '../ebook/notification_processor.py');
    
    if (!fs.existsSync(ebookPath)) {
      console.log('❌ notification_processor.py 不存在');
      console.log(`   預期路徑: ${ebookPath}`);
      return false;
    }

    console.log('✅ ebook 處理器存在');
    return true;
  }

  /**
   * 檢查輸出目錄
   */
  checkOutputDirectory() {
    console.log('\n📁 檢查輸出目錄...');

    const outputPath = path.join(__dirname, '../ebook/generated_documents');
    
    if (!fs.existsSync(outputPath)) {
      console.log('⚠️  輸出目錄不存在，正在創建...');
      try {
        fs.mkdirSync(outputPath, { recursive: true });
        console.log('✅ 輸出目錄已創建');
      } catch (error) {
        console.log('❌ 無法創建輸出目錄');
        return false;
      }
    } else {
      console.log('✅ 輸出目錄存在');
    }

    return true;
  }

  /**
   * 顯示配置摘要
   */
  showConfigurationSummary() {
    console.log('\n📋 自動化配置摘要:');
    
    const envContent = fs.readFileSync(this.envPath, 'utf8');
    const getEnvValue = (key) => {
      const match = envContent.match(new RegExp(`^${key}=(.*)$`, 'm'));
      return match ? match[1] : '未設定';
    };

    console.log(`   排程狀態: ${getEnvValue('SCHEDULER_ENABLED')}`);
    console.log(`   執行時間: ${getEnvValue('SCHEDULER_DAILY_TIME')}`);
    console.log(`   時區: ${getEnvValue('SCHEDULER_TIMEZONE')}`);
    console.log(`   Python 路徑: ${getEnvValue('PYTHON_EXECUTABLE')}`);
    console.log(`   處理器路徑: ${getEnvValue('EBOOK_PROCESSOR_PATH')}`);
  }

  /**
   * 執行完整檢查
   */
  async runFullCheck() {
    console.log('🛠️  自動化系統設置檢查');
    console.log('========================\n');

    const checks = [
      this.checkConfiguration(),
      await this.checkPythonEnvironment(),
      this.checkEbookProcessor(),
      this.checkOutputDirectory()
    ];

    const allPassed = checks.every(check => check === true);

    console.log('\n' + '='.repeat(50));
    
    if (allPassed) {
      console.log('🎉 所有檢查通過！自動化系統已就緒');
      console.log('\n📅 系統將在每天 02:00 自動執行');
      console.log('💡 使用以下命令管理系統:');
      console.log('   - automation.bat start   (啟動)');
      console.log('   - automation.bat status  (狀態)');
      console.log('   - automation.bat trigger (手動觸發)');
      
      this.showConfigurationSummary();
    } else {
      console.log('❌ 部分檢查失敗，請修復後重新執行');
    }

    return allPassed;
  }
}

// 執行檢查
const setup = new AutomationSetup();
setup.runFullCheck().catch(console.error);