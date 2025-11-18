# LINE Book Query Bot (書庫查詢機器人)

A smart library assistant that integrates LINE Messaging API with Google Gemini 2.5 Pro to help users query book databases using natural language.

## Features

- 🤖 Natural language book queries in LINE chat
- 🧠 AI-powered intent understanding via Gemini 2.5 Pro Function Calling
- 📚 MySQL database integration for book information
- 💬 Smart response formatting (text for 1-2 books, carousel for 3+ books)
- 📰 Latest bulletins/news display with Flex Carousel
- 🔔 Subscription management for news, cancellations, and new books
- ⚡ Quick Reply buttons for easy subscription access
- 🔒 Secure webhook validation and error handling
- 🐳 Docker containerization support

## Prerequisites

- Node.js 18+ 
- MySQL database with books table
- LINE Developer Account
- Google Cloud Account (for Gemini API)

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# LINE Configuration
LINE_CHANNEL_SECRET=your_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here

# Gemini Configuration  
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=bookdb_user
DB_PASSWORD=your_db_password_here
DB_NAME=book_library

# Server Configuration
PORT=3000
NODE_ENV=production
```

### Getting API Keys

#### LINE Developer Console
1. Go to [LINE Developers Console](https://developers.line.biz/)
2. Create a new provider or select existing one
3. Create a Messaging API channel
4. Get Channel Secret from "Basic settings" tab
5. Get Channel Access Token from "Messaging API" tab
6. Set webhook URL to `https://your-domain.com/webhook`

#### Google Gemini API
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy the API key to your environment variables

## Database Setup

The application expects a MySQL database with a `books` table:

```sql
-- Example table structure (adjust according to your existing schema)
CREATE TABLE books (
  book_id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  quantity INT DEFAULT 0,
  shelf_location VARCHAR(100),
  library_branch VARCHAR(100)
);

-- Example data
INSERT INTO books (title, quantity, shelf_location, library_branch) VALUES
('金剛經', 3, 'A1-23', '總館'),
('心經', 5, 'A1-24', '總館'),
('論語', 2, 'B2-15', '分館');
```

## Installation & Development

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd line-book-query-bot

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Edit .env with your actual values

# Build the project
npm run build

# Start development server
npm run dev

# Run tests
npm test

# Lint code
npm run lint
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Docker Deployment

### Build and Run with Docker

```bash
# Build Docker image
npm run docker:build
# or
docker build -t line-book-bot .

# Run container
npm run docker:run
# or
docker run -p 3000:3000 --env-file .env line-book-bot
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    env_file:
      - .env
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  mysql_data:
```

Run with:
```bash
docker-compose up -d
```

## Cloud Deployment

### Google Cloud Run

1. **Build and push to Container Registry:**
```bash
# Set project ID
export PROJECT_ID=your-gcp-project-id

# Build and tag image
docker build -t gcr.io/$PROJECT_ID/line-book-bot .

# Push to registry
docker push gcr.io/$PROJECT_ID/line-book-bot
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy line-book-bot \
  --image gcr.io/$PROJECT_ID/line-book-bot \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-env-vars="NODE_ENV=production" \
  --set-secrets="LINE_CHANNEL_SECRET=line-channel-secret:latest,LINE_CHANNEL_ACCESS_TOKEN=line-access-token:latest,GEMINI_API_KEY=gemini-api-key:latest,DB_PASSWORD=db-password:latest"
```

3. **Set other environment variables:**
```bash
gcloud run services update line-book-bot \
  --set-env-vars="DB_HOST=your-db-host,DB_USER=your-db-user,DB_NAME=book_library,GEMINI_MODEL=gemini-2.0-flash"
```

### Vercel Deployment

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Deploy:**
```bash
vercel --prod
```

3. **Set environment variables in Vercel dashboard or CLI:**
```bash
vercel env add LINE_CHANNEL_SECRET
vercel env add LINE_CHANNEL_ACCESS_TOKEN
vercel env add GEMINI_API_KEY
# ... add all other environment variables
```

## API Endpoints

- `POST /webhook` - LINE webhook endpoint
- `GET /health` - Health check endpoint

## Project Structure

```
src/
├── index.ts                 # Express server entry point
├── config/
│   └── index.ts            # Environment configuration
├── types/
│   └── book.ts             # Type definitions
├── services/
│   ├── databaseService.ts  # MySQL operations
│   ├── geminiService.ts    # Gemini AI integration
│   └── lineMessagingService.ts # LINE API messaging
├── handlers/
│   ├── webhookHandler.ts   # Webhook processing
│   └── errorHandler.ts     # Error handling
└── utils/                  # Utility functions
```

## Usage

1. Add the LINE bot as a friend using QR code from LINE Developer Console
2. Send natural language queries like:
   - "有沒有金剛經相關的書？"
   - "我想找論語"
   - "有什麼佛經類的書籍？"
3. The bot will search the database and respond with book information

## Troubleshooting

### Common Issues

**Webhook not receiving messages:**
- Verify webhook URL is correctly set in LINE Developer Console
- Check that your server is accessible from the internet
- Ensure SSL certificate is valid (LINE requires HTTPS)

**Database connection errors:**
- Verify database credentials in `.env`
- Check if database server is running and accessible
- Ensure `books` table exists with correct schema

**Gemini API errors:**
- Verify API key is correct and has proper permissions
- Check API quotas and billing in Google Cloud Console
- Ensure model name is correct (`gemini-2.0-flash`)

**LINE API errors:**
- Verify Channel Access Token is valid
- Check if bot is added as friend
- Ensure Channel Secret matches

### Logs

Check application logs for detailed error information:

```bash
# Local development
npm run dev

# Docker logs
docker logs <container-id>

# Cloud Run logs
gcloud logs read --service=line-book-bot
```

## Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:ci

# Run specific test file
npm test -- webhookHandler.test.ts
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting
6. Submit a pull request

## Latest Bulletins Feature

### Overview
The bot now supports displaying latest bulletins/news from the Buddhist Education Foundation website with an interactive Flex Carousel and Quick Reply buttons for easy subscription management.

### Usage

**Display Latest Bulletins:**
```
User: 最新消息
Bot: [Flex Carousel with up to 10 bulletins + Quick Reply buttons]
```

**Quick Reply Options:**
- 📰 訂閱最新消息 - Subscribe to news updates
- ⚠️ 訂閱停課通知 - Subscribe to class cancellations
- 📚 訂閱新書通知 - Subscribe to new book notifications
- 📊 訂閱狀態查詢 - Check subscription status
- ❌ 取消訂閱 - Unsubscribe from all

### API Integration
- **Endpoint:** `https://publish.budaedu.org/laravel/public/api/bulletins`
- **URL Format:** `https://www.budaedu.org/#/bulletins/{id}`
- **Features:** Automatic HTML tag removal, text truncation, SSL handling

### Documentation
- [Complete Feature Guide](./docs/BULLETIN_FEATURE.md)
- [Quick Start Guide](./BULLETIN_QUICK_START.md)
- [Message Examples](./BULLETIN_MESSAGE_EXAMPLES.md)
- [Flow Diagrams](./BULLETIN_FLOW_DIAGRAM.md)
- [Cheat Sheet](./BULLETIN_CHEATSHEET.md)

### Testing
```bash
# Test bulletin API connection
npx ts-node test-bulletin-service.ts
```

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs for error details
3. Create an issue in the repository with:
   - Error message
   - Steps to reproduce
   - Environment details (Node.js version, deployment platform, etc.)