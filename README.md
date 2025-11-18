# Buddhist Education System

A comprehensive digital library management system consisting of two integrated applications for Buddhist educational institutions.

## 🏗️ System Architecture

This repository contains two independent but complementary applications:

### 📚 Ebook Summary System (Python)
- **Purpose**: Automated monitoring and processing of Buddhist educational content
- **Technology**: Python 3.8+, Tkinter, Selenium, Google Gemini Pro 2.5
- **Features**: Web scraping, PDF processing, AI-powered summarization, email distribution

### 🤖 LINE Book Query Bot (TypeScript/Node.js)
- **Purpose**: Intelligent library assistant with natural language query capabilities
- **Technology**: Node.js 18+, TypeScript, Express.js, MySQL, Google Gemini 2.0 Flash
- **Features**: LINE messaging integration, conversational AI, database search

## 🚀 Quick Start

### Ebook Summary System
```bash
cd ebook
pip install -r requirements.txt
python newbook_summary_app.py
```

### LINE Book Query Bot
```bash
cd Line-bot-llm-mysql
npm install
npm run build
npm start
```

## 📋 Features

### Ebook Summary System
- ✅ Automated website monitoring (budaedu.org)
- ✅ PDF download and text extraction
- ✅ AI-powered content summarization
- ✅ Multi-format document generation (Word, Excel)
- ✅ Email distribution system
- ✅ Desktop GUI for configuration and monitoring

### LINE Book Query Bot
- ✅ Natural language book search
- ✅ Intelligent query processing with Gemini AI
- ✅ MySQL database integration
- ✅ Subscription management
- ✅ Daily notification system
- ✅ Admin dashboard and monitoring
- ✅ Error recovery and health monitoring

## 🔧 Configuration

### Environment Setup
Both applications require API keys and configuration:

1. **Google Gemini API**: Required for AI processing
2. **LINE Messaging API**: Required for bot functionality
3. **MySQL Database**: Required for book data storage
4. **SMTP Settings**: Required for email notifications

### Configuration Files
- `ebook/config_template.json` - Ebook system configuration template
- `Line-bot-llm-mysql/.env.example` - LINE bot environment template

## 📖 Documentation

- [Ebook System README](ebook/README.md)
- [LINE Bot README](Line-bot-llm-mysql/README.md)
- [Deployment Guide](Line-bot-llm-mysql/DEPLOYMENT.md)
- [Automation Setup](Line-bot-llm-mysql/AUTOMATION_SETUP_GUIDE.md)

## 🏛️ Project Structure

```
/
├── .kiro/                          # Kiro IDE configuration
│   ├── specs/                      # Feature specifications
│   └── steering/                   # Development guidelines
├── ebook/                          # Python ebook summary system
│   ├── *.py                        # Core modules
│   ├── test/                       # Test files and sample PDFs
│   └── requirements.txt            # Python dependencies
└── Line-bot-llm-mysql/            # TypeScript LINE bot
    ├── src/                        # Source code
    ├── scripts/                    # Deployment scripts
    └── migrations/                 # Database migrations
```

## 🛠️ Development

### Prerequisites
- Python 3.8+ (for ebook system)
- Node.js 18+ (for LINE bot)
- MySQL 8.0+ (for database)
- Chrome/Chromium (for web scraping)

### Testing
```bash
# Ebook system tests
cd ebook
python test_book_scraper.py
python test_gemini_processor.py

# LINE bot tests
cd Line-bot-llm-mysql
npm test
```

## 🚀 Deployment

### Docker Deployment (LINE Bot)
```bash
cd Line-bot-llm-mysql
docker-compose up -d
```

### Manual Deployment
See [DEPLOYMENT.md](Line-bot-llm-mysql/DEPLOYMENT.md) for detailed instructions.

## 📊 Monitoring

Both systems include comprehensive logging and monitoring:
- Real-time processing logs
- Error tracking and recovery
- Performance metrics
- Health check endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is developed for Buddhist educational institutions. Please respect the intended use for educational and religious purposes.

## 🆘 Support

For issues and questions:
1. Check the documentation in each project's README
2. Review the troubleshooting guides
3. Check existing issues in the repository
4. Create a new issue with detailed information

## 🔄 Integration

The two systems can work together:
- Ebook system processes new content
- LINE bot provides access to processed content
- Shared notification system for updates
- Unified user experience across platforms

---

**Built with ❤️ for Buddhist Education**