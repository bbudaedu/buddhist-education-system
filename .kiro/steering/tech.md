# Technology Stack

## Ebook Summary System (Python)

### Core Technologies
- **Python 3.8+** - Main runtime
- **Tkinter** - Desktop GUI framework
- **Selenium 4.0+** - Web automation and scraping
- **Google Gemini Pro 2.5** - AI content processing
- **ChromeDriver** - Browser automation driver

### Key Libraries
- `google-genai>=1.0.0` - Gemini AI API integration
- `pypdf>=3.0.0` - PDF text extraction
- `python-docx>=0.8.11` - Word document generation
- `openpyxl>=3.0.0` - Excel file creation
- `selenium>=4.0.0` - Web scraping
- `urllib3>=1.26.0` - HTTP requests

### Common Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run main application
python newbook_summary_app.py

# Run individual modules for testing
python test_book_scraper.py
python test_gemini_processor.py
python test_email_sender.py
```

## LINE Book Query Bot (TypeScript/Node.js)

### Core Technologies
- **Node.js 18+** - Runtime environment
- **TypeScript 5.0** - Primary language
- **Express.js** - Web framework
- **MySQL 8.0** - Database
- **Google Gemini 2.0 Flash** - AI processing
- **LINE Messaging API** - Chat interface

### Key Dependencies
- `@line/bot-sdk` - LINE API integration
- `@google/generative-ai` - Gemini AI client
- `mysql2` - MySQL database driver
- `express` - Web server framework
- `dotenv` - Environment configuration

### Build System & Commands
```bash
# Development
npm install
npm run dev

# Production build
npm run build
npm start

# Testing
npm test
npm run test:ci

# Code quality
npm run lint
npm run lint:fix

# Docker deployment
npm run docker:build
npm run docker:run
```

### TypeScript Configuration
- Target: ES2020
- Strict mode enabled
- Path aliases configured (`@/*` for src)
- Source maps and declarations generated
- Comprehensive type checking enabled