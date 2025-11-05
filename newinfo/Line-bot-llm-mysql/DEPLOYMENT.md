# Deployment Guide

This guide covers deploying the LINE Bot with Daily Book Notifications system.

## Prerequisites

- Docker and Docker Compose installed
- Node.js 18+ (for development)
- MySQL 8.0+ (if not using Docker)
- Python 3.8+ (for ebook processor integration)

## Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Configure the required environment variables in `.env`:

### Required Variables
```bash
# LINE Configuration
LINE_CHANNEL_SECRET=your_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
DB_HOST=mysql  # Use 'mysql' for Docker Compose, 'localhost' for local DB
DB_PORT=3306
DB_USER=bookdb_user
DB_PASSWORD=your_secure_password_here
DB_NAME=book_library
DB_ROOT_PASSWORD=your_root_password_here  # For Docker MySQL
```

### Optional Configuration
```bash
# Scheduler Configuration
SCHEDULER_ENABLED=true
SCHEDULER_DAILY_TIME=02:00
SCHEDULER_MAX_RETRIES=3
SCHEDULER_RETRY_DELAY_MINUTES=30
SCHEDULER_TIMEZONE=Asia/Taipei

# Notification Configuration
NOTIFICATION_MAX_RECIPIENTS_PER_BATCH=100
NOTIFICATION_DELIVERY_TIMEOUT_MS=30000
NOTIFICATION_MAX_BOOKS_PER_MESSAGE=5
NOTIFICATION_ENABLE_RICH_MESSAGES=true
NOTIFICATION_RETRY_FAILED_DELIVERIES=true
NOTIFICATION_MAX_DELIVERY_RETRIES=3
NOTIFICATION_DELIVERY_RETRY_DELAY_MINUTES=15

# Ebook Integration
EBOOK_PROCESSOR_PATH=../ebook/main_processor.py
PYTHON_EXECUTABLE=python
EBOOK_OUTPUT_PATH=../ebook/generated_documents
```

## Deployment Options

### Option 1: Docker Compose (Recommended)

This is the easiest way to deploy the complete system with all services.

#### Quick Deployment
```bash
# Linux/macOS
npm run deploy

# Windows
npm run deploy:win
```

#### Manual Deployment
```bash
# Build and start all services
docker-compose up -d

# Run database migrations
docker-compose run --rm line-bot-web npm run migrate

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Individual Services

#### Web Service Only
```bash
# Build the image
docker build -t line-book-bot .

# Run web service (disable scheduler)
docker run -d \
  --name line-bot-web \
  -p 3000:3000 \
  -e SCHEDULER_ENABLED=false \
  --env-file .env \
  line-book-bot
```

#### Scheduler Service Only
```bash
# Run scheduler service
docker run -d \
  --name line-bot-scheduler \
  -e SCHEDULER_ENABLED=true \
  --env-file .env \
  -v $(pwd)/../ebook:/app/ebook:ro \
  line-book-bot npm run scheduler:start
```

### Option 3: Local Development

```bash
# Install dependencies
npm install

# Run database migrations
npm run migrate

# Start web server
npm run dev

# Start scheduler (in separate terminal)
npm run scheduler
```

## Database Setup

### Automatic Migration (Recommended)
The deployment scripts automatically run database migrations. The system will:

1. Create a `migrations` table to track executed migrations
2. Execute all `.sql` files in the `migrations/` directory
3. Skip already executed migrations

### Manual Migration
```bash
# Using npm script
npm run migrate

# Using Docker
docker-compose run --rm line-bot-web npm run migrate

# Using ts-node directly
npx ts-node scripts/migrate.ts
```

### Migration Files
- `001_create_user_subscriptions.sql` - User subscription management
- `002_create_notification_logs.sql` - Notification delivery tracking
- `003_create_delivery_failures.sql` - Failed delivery logging

## Service Architecture

The deployment includes three main services:

### 1. Web Service (`line-bot-web`)
- Handles LINE webhook events
- Processes user messages and subscription commands
- Serves health check endpoint
- Port: 3000

### 2. Scheduler Service (`line-bot-scheduler`)
- Runs daily ebook processing
- Sends notifications to subscribed users
- Handles retry logic for failed operations
- No exposed ports (internal service)

### 3. MySQL Database (`mysql`)
- Stores user subscriptions
- Tracks notification logs and delivery failures
- Port: 3306

## Monitoring and Maintenance

### Health Checks
```bash
# Check web service health
curl http://localhost:3000/health

# Check all service status
docker-compose ps

# View service logs
docker-compose logs -f [service-name]
```

### Log Management
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f line-bot-web
docker-compose logs -f line-bot-scheduler
docker-compose logs -f mysql

# Follow logs with timestamps
docker-compose logs -f -t
```

### Database Maintenance
```bash
# Access MySQL console
docker-compose exec mysql mysql -u root -p

# Backup database
docker-compose exec mysql mysqldump -u root -p book_library > backup.sql

# Restore database
docker-compose exec -T mysql mysql -u root -p book_library < backup.sql
```

## Scaling and Performance

### Horizontal Scaling
- Web service can be scaled horizontally
- Scheduler should run as a single instance to avoid duplicate processing
- Use load balancer for multiple web service instances

### Resource Requirements
- **Web Service**: 512MB RAM, 1 CPU core
- **Scheduler Service**: 256MB RAM, 0.5 CPU core
- **MySQL**: 1GB RAM, 1 CPU core (minimum)

### Performance Tuning
```bash
# Adjust notification batch size
NOTIFICATION_MAX_RECIPIENTS_PER_BATCH=50

# Increase delivery timeout for slow networks
NOTIFICATION_DELIVERY_TIMEOUT_MS=60000

# Reduce retry attempts for faster failure handling
NOTIFICATION_MAX_DELIVERY_RETRIES=2
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check MySQL service status
docker-compose ps mysql

# Check database logs
docker-compose logs mysql

# Verify environment variables
docker-compose config
```

#### 2. LINE Webhook Verification Failed
- Verify `LINE_CHANNEL_SECRET` is correct
- Check webhook URL configuration in LINE Developer Console
- Ensure web service is accessible from internet

#### 3. Scheduler Not Running
```bash
# Check scheduler logs
docker-compose logs line-bot-scheduler

# Verify scheduler configuration
echo $SCHEDULER_ENABLED
echo $SCHEDULER_DAILY_TIME
```

#### 4. Ebook Integration Issues
- Verify Python ebook processor path: `EBOOK_PROCESSOR_PATH`
- Check Python executable: `PYTHON_EXECUTABLE`
- Ensure ebook directory is mounted correctly

### Debug Mode
```bash
# Enable debug logging
NODE_ENV=development docker-compose up

# Run with verbose output
docker-compose up --verbose
```

## Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use strong passwords for database
- Rotate API keys regularly

### Network Security
- Use HTTPS for webhook endpoints
- Implement rate limiting for public endpoints
- Restrict database access to application services only

### Container Security
- Run containers as non-root user (already configured)
- Keep base images updated
- Scan images for vulnerabilities

## Backup and Recovery

### Automated Backups
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec mysql mysqldump -u root -p$DB_ROOT_PASSWORD book_library > "backup_$DATE.sql"
```

### Recovery Process
1. Stop all services: `docker-compose down`
2. Restore database from backup
3. Start services: `docker-compose up -d`
4. Verify system health

## Updates and Maintenance

### Application Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose build
docker-compose up -d

# Run any new migrations
docker-compose run --rm line-bot-web npm run migrate
```

### Dependency Updates
```bash
# Update npm dependencies
npm update

# Rebuild Docker images
docker-compose build --no-cache
```