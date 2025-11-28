# Project Structure

## Repository Organization

This is a multi-project repository containing two independent applications with unified Kiro management:

```
/
├── .kiro/                          # Unified Kiro IDE configuration
│   ├── specs/                      # All project specifications
│   │   ├── ebook-features/         # Ebook-specific features
│   │   ├── linebot-features/       # LINE bot-specific features
│   │   └── integration-features/   # Cross-project integrations
│   └── steering/                   # Unified steering rules
├── ebook/                          # Python ebook summary system
└── Line-bot-llm-mysql/            # TypeScript LINE bot application
```

## Unified SPEC Management

### SPEC Categories
- **ebook-features/**: Features specific to the Python ebook system
- **linebot-features/**: Features specific to the TypeScript LINE bot
- **integration-features/**: Features that connect both systems

### SPEC Naming Convention
- Use descriptive names with project prefix when needed
- Example: `ebook-pdf-processor`, `linebot-carousel-messages`, `integration-daily-notifications`

## Ebook Summary System (`/ebook/`)

### Core Structure
```
ebook/
├── *.py                           # Main application modules
├── test_*.py                      # Unit test files
├── requirements.txt               # Python dependencies
├── config.json                    # Runtime configuration (generated)
├── config_template.json           # Configuration template
├── README.md                      # Documentation
├── chromedriver-win64/            # ChromeDriver binaries
├── downloads/                     # PDF download directory
├── generated_documents/           # Output Word/Excel files
├── test/                          # Additional test files
└── __pycache__/                   # Python bytecode cache
```

### Key Files
- `newbook_summary_app.py` - Main GUI application
- `main_processor.py` - Core processing logic
- `book_scraper.py` - Web scraping functionality
- `gemini_processor.py` - AI processing
- `email_sender.py` - SMTP email functionality
- `document_generator.py` - Word/Excel generation
- `progress_manager.py` - Processing state management

### Naming Conventions
- Snake_case for Python files and variables
- Descriptive module names indicating functionality
- Test files prefixed with `test_`
- Log files with timestamp format: `log_YYYY-MM-DD_HH-MM-SS.txt`

## LINE Book Query Bot (`/Line-bot-llm-mysql/`)

### Core Structure
```
Line-bot-llm-mysql/
├── src/                           # TypeScript source code
│   ├── index.ts                   # Application entry point
│   ├── config/                    # Configuration management
│   ├── types/                     # TypeScript type definitions
│   ├── services/                  # Business logic services
│   └── handlers/                  # Request/webhook handlers
├── dist/                          # Compiled JavaScript output
├── node_modules/                  # NPM dependencies
├── package.json                   # NPM configuration
├── tsconfig.json                  # TypeScript configuration
├── .eslintrc.js                   # ESLint configuration
├── .env                          # Environment variables (local)
├── .env.example                  # Environment template
├── Dockerfile                    # Container configuration
└── README.md                     # Documentation
```

### TypeScript Architecture
- **Services Layer**: Database, Gemini AI, LINE messaging
- **Handlers Layer**: Webhook processing, error handling
- **Types Layer**: Shared TypeScript interfaces
- **Config Layer**: Environment and application configuration

### Path Aliases
- `@/*` maps to `src/*`
- `@/config/*` maps to `src/config/*`
- `@/types/*` maps to `src/types/*`
- `@/services/*` maps to `src/services/*`
- `@/handlers/*` maps to `src/handlers/*`

### Naming Conventions
- camelCase for TypeScript files, variables, and functions
- PascalCase for classes and interfaces
- kebab-case for npm scripts and Docker images
- Service files suffixed with `Service.ts`
- Handler files suffixed with `Handler.ts`

## Configuration Management

### Python Project
- `config_template.json` - Template with default values
- `config.json` - Runtime configuration (auto-generated)
- Environment-specific settings in JSON format

### TypeScript Project
- `.env.example` - Environment variable template
- `.env` - Local environment variables (gitignored)
- Configuration loaded via `dotenv` package

## Development Patterns

### Error Handling
- Python: Comprehensive logging with rotating log files
- TypeScript: Structured error handling with proper HTTP status codes

### Testing
- Python: Individual test files for each module
- TypeScript: Jest-based unit testing with coverage reports

### Documentation
- Both projects maintain detailed README files
- Inline code documentation in respective language conventions
- Configuration templates for easy setup

## Working Directory Guidelines for SPEC Development

### Single Project Features
- **Ebook features**: Work in `./ebook/` directory
- **LINE bot features**: Work in `./Line-bot-llm-mysql/` directory

### Integration Features
- May require changes in both directories
- Clearly specify which files belong to which project in SPEC documentation