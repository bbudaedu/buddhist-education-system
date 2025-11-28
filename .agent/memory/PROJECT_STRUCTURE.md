# Buddhist Education System - Project Structure

# Project Structure Map

## 核心目錄
- `.agent/`: Agent 的大腦 (規則、記憶、工作流)
- `ebook/`: Python 爬蟲與後端服務 (Legacy System)
- `Line-bot-llm-mysql/`: TypeScript LINE Bot 主程式 (Modern System)
- `docs/`: 專案文檔與 Artifacts

## 關鍵路徑規則
- **新功能文檔**：一律放在 `docs/features/[feature-name]/`
- **API 定義**：參考 `Line-bot-llm-mysql/src/types/`
- **爬蟲輸出**：`ebook/output/` (不要提交到 Git)

## 📁 Repository Overview

This is a monorepo containing two integrated applications for Buddhist educational institutions:

```
buddhist-education-system/
├── .kiro/                          # Kiro IDE configuration
│   ├── specs/                      # Feature specifications
│   └── steering/                   # Development guidelines
│
├── ebook/                          # Python Ebook Summary System
│   ├── *.py                        # Core Python modules
│   ├── requirements.txt            # Python dependencies
│   ├── config_template.json        # Configuration template
│   ├── chromedriver-win64/         # ChromeDriver binaries
│   └── README.md                   # Detailed documentation
│
├── Line-bot-llm-mysql/            # TypeScript LINE Bot
│   ├── src/                        # TypeScript source code
│   │   ├── handlers/               # Request handlers
│   │   ├── services/               # Business logic
│   │   └── types/                  # Type definitions
│   ├── migrations/                 # Database migrations
│   ├── package.json                # NPM configuration
│   ├── tsconfig.json               # TypeScript config
│   └── README.md                   # Detailed documentation
│
├── docs/                           # Additional documentation
├── README.md                       # Main project README
├── QUICK_START.md                  # Quick start guide
└── .gitignore                      # Git ignore rules

```

## 🎯 System Components

### Ebook Summary System (`/ebook/`)

**Purpose**: Automated monitoring and processing of Buddhist educational content

**Key Features**:
- Web scraping from budaedu.org
- PDF download and text extraction
- AI-powered summarization (Google Gemini Pro 2.5)
- Document generation (Word, Excel)
- Email distribution
- Desktop GUI (Tkinter)

**Main Modules**:
- `newbook_summary_app.py` - Main GUI application
- `book_scraper.py` - Web scraping functionality
- `gemini_processor.py` - AI processing
- `document_generator.py` - Document generation
- `email_sender.py` - Email functionality
- `website_monitor.py` - Website monitoring
- `notification_processor.py` - Notification handling

### LINE Book Query Bot (`/Line-bot-llm-mysql/`)

**Purpose**: Intelligent library assistant with natural language query capabilities

**Key Features**:
- LINE Messaging API integration
- Natural language processing (Google Gemini 2.0 Flash)
- MySQL database integration
- Subscription management
- Daily notifications
- Bulletin/news display
- Carousel messages

**Main Services**:
- `webhookHandler.ts` - LINE webhook processing
- `geminiService.ts` - AI integration
- `databaseService.ts` - Database operations
- `lineMessagingService.ts` - LINE messaging
- `subscriptionService.ts` - Subscription management
- `bulletinService.ts` - Bulletin handling

## 🔧 Configuration Files

### Python Project
- `config_template.json` - Configuration template
- `config.json` - Runtime config (auto-generated, gitignored)
- `requirements.txt` - Python dependencies

### TypeScript Project
- `.env.example` - Environment variable template
- `.env` - Local environment (gitignored)
- `package.json` - NPM dependencies
- `tsconfig.json` - TypeScript configuration

## 📚 Documentation

### Main Documentation
- `README.md` - Project overview
- `QUICK_START.md` - Quick start guide
- `ebook/README.md` - Ebook system documentation
- `Line-bot-llm-mysql/README.md` - LINE bot documentation

### Feature Documentation
- `docs/` - Additional feature documentation
- `.kiro/specs/` - Feature specifications
- `.kiro/steering/` - Development guidelines

## 🚀 Getting Started

### Ebook System
```bash
cd ebook
pip install -r requirements.txt
python newbook_summary_app.py
```

### LINE Bot
```bash
cd Line-bot-llm-mysql
npm install
npm run build
npm start
```

## 🔐 Security Notes

The following files contain sensitive information and are gitignored:
- `config.json` - Ebook system configuration
- `.env` - LINE bot environment variables
- `*.backup_*` - Configuration backups
- `*_progress_cache.json` - Progress cache files

## 📦 Dependencies

### Python (Ebook System)
- Python 3.8+
- Selenium 4.0+
- Google Gemini API
- Tkinter (GUI)
- pypdf, python-docx, openpyxl

### TypeScript (LINE Bot)
- Node.js 18+
- TypeScript 5.0
- Express.js
- MySQL 8.0
- @line/bot-sdk
- @google/generative-ai

## 🛠️ Development Tools

- **Kiro IDE** - Unified development environment
- **Git** - Version control
- **Docker** - Containerization (LINE bot)
- **ChromeDriver** - Web automation

## 📝 License

This project is developed for Buddhist educational institutions. Please respect the intended use for educational and religious purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the documentation in each project's README
2. Review the troubleshooting guides
3. Create an issue in the repository

---

**Built with ❤️ for Buddhist Education**
