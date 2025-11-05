#!/bin/bash

# Production deployment script for LINE Bot with notification system
# Usage: ./scripts/deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting deployment for environment: $ENVIRONMENT"

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "❌ Error: .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
source "$PROJECT_DIR/.env"

echo "📦 Building Docker images..."
cd "$PROJECT_DIR"

# Build the application
docker-compose build

echo "🗄️  Running database migrations..."
# Run migrations in a temporary container
docker-compose run --rm line-bot-web npm run migrate

echo "🔄 Starting services..."
# Start all services
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if web service is healthy
echo "🏥 Checking service health..."
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ Web service is healthy"
else
    echo "❌ Web service health check failed"
    docker-compose logs line-bot-web
    exit 1
fi

# Check if scheduler is running
if docker-compose ps line-bot-scheduler | grep -q "Up"; then
    echo "✅ Scheduler service is running"
else
    echo "❌ Scheduler service is not running"
    docker-compose logs line-bot-scheduler
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "Services status:"
docker-compose ps

echo ""
echo "To view logs:"
echo "  Web service: docker-compose logs -f line-bot-web"
echo "  Scheduler:   docker-compose logs -f line-bot-scheduler"
echo "  Database:    docker-compose logs -f mysql"
echo ""
echo "To stop services:"
echo "  docker-compose down"