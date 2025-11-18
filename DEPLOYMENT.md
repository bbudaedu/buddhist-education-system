# Deployment Guide

## 📦 Deployment Options

### Ebook Summary System (Python)

#### Local Deployment

1. **Install Dependencies**
```bash
cd ebook
pip install -r requirements.txt
```

2. **Configure Settings**
```bash
# Copy template
cp config_template.json config.json

# Edit config.json with your settings:
# - Gemini API Key
# - ChromeDriver path
# - SMTP settings
# - Email recipients
```

3. **Run Application**
```bash
python newbook_summary_app.py
```

#### Scheduled Execution (Windows)

Use Windows Task Scheduler to run daily:

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 9:00 AM)
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\ebook\newbook_summary_app.py`
7. Start in: `C:\path\to\ebook\`

### LINE Book Query Bot (TypeScript)

#### Local Development

```bash
cd Line-bot-llm-mysql
npm install
cp .env.example .env
# Edit .env with your credentials
npm run dev
```

#### Production Build

```bash
npm run build
npm start
```

#### Docker Deployment

```bash
# Build image
docker build -t line-book-bot .

# Run container
docker run -d \
  --name line-book-bot \
  -p 3000:3000 \
  --env-file .env \
  line-book-bot
```

#### Cloud Deployment

##### Google Cloud Run

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy line-book-bot \
  --source . \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated
```

##### Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

##### Railway

1. Connect GitHub repository
2. Select `Line-bot-llm-mysql` as root directory
3. Add environment variables
4. Deploy automatically on push

## 🔐 Environment Variables

### Ebook System (config.json)

```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY",
  "chromedriver_path": "chromedriver-win64/chromedriver.exe",
  "target_url": "https://www.budaedu.org",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your-email@gmail.com",
  "smtp_password": "your-app-password",
  "email_recipients": "recipient@example.com"
}
```

### LINE Bot (.env)

```bash
# LINE Configuration
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_access_token

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=bookdb_user
DB_PASSWORD=your_db_password
DB_NAME=book_library

# Server Configuration
PORT=3000
NODE_ENV=production
```

## 🗄️ Database Setup

### MySQL Database

```sql
-- Create database
CREATE DATABASE book_library CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'bookdb_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON book_library.* TO 'bookdb_user'@'localhost';
FLUSH PRIVILEGES;

-- Run migrations
USE book_library;
SOURCE migrations/001_create_books_table.sql;
SOURCE migrations/002_create_subscriptions_table.sql;
SOURCE migrations/003_add_notification_types.sql;
```

## 🔄 CI/CD Setup

### GitHub Actions (Example)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy LINE Bot

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        working-directory: ./Line-bot-llm-mysql
        run: npm ci
      
      - name: Build
        working-directory: ./Line-bot-llm-mysql
        run: npm run build
      
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: line-book-bot
          region: asia-east1
          source: ./Line-bot-llm-mysql
```

## 🔍 Health Checks

### Ebook System

Check logs in `ebook/logs/` directory for execution status.

### LINE Bot

```bash
# Health check endpoint
curl http://localhost:3000/health

# Expected response
{"status":"ok","timestamp":"2024-01-01T00:00:00.000Z"}
```

## 🛡️ Security Best Practices

1. **Never commit sensitive files**
   - `config.json`
   - `.env`
   - API keys

2. **Use environment variables**
   - Store secrets in environment variables
   - Use secret management services (AWS Secrets Manager, Google Secret Manager)

3. **Enable HTTPS**
   - Use SSL certificates
   - LINE webhook requires HTTPS

4. **Regular updates**
   - Keep dependencies updated
   - Monitor security advisories

5. **Access control**
   - Limit database access
   - Use firewall rules
   - Implement rate limiting

## 📊 Monitoring

### Ebook System

- Check log files regularly
- Monitor email delivery
- Verify PDF downloads

### LINE Bot

- Monitor webhook responses
- Check database connections
- Track API usage and quotas
- Set up error alerts

## 🔧 Troubleshooting

### Common Issues

**Ebook System:**
- ChromeDriver version mismatch → Update ChromeDriver
- Gemini API quota exceeded → Check API usage
- Email sending fails → Verify SMTP settings

**LINE Bot:**
- Webhook not receiving messages → Check URL and SSL
- Database connection fails → Verify credentials
- Gemini API errors → Check API key and quotas

## 📞 Support

For deployment issues:
1. Check the troubleshooting guides
2. Review logs for error details
3. Verify all environment variables
4. Test API connections manually

---

**Ready to deploy? Follow the steps above and your system will be up and running!** 🚀
