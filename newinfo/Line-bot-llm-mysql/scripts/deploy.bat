@echo off
REM Production deployment script for LINE Bot with notification system (Windows)
REM Usage: scripts\deploy.bat [environment]

setlocal enabledelayedexpansion

set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=production

echo 🚀 Starting deployment for environment: %ENVIRONMENT%

REM Check if .env file exists
if not exist ".env" (
    echo ❌ Error: .env file not found. Please copy .env.example to .env and configure it.
    exit /b 1
)

echo 📦 Building Docker images...

REM Build the application
docker-compose build
if errorlevel 1 (
    echo ❌ Docker build failed
    exit /b 1
)

echo 🗄️  Running database migrations...
REM Run migrations in a temporary container
docker-compose run --rm line-bot-web npm run migrate
if errorlevel 1 (
    echo ❌ Database migration failed
    exit /b 1
)

echo 🔄 Starting services...
REM Start all services
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    exit /b 1
)

echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak > nul

echo 🏥 Checking service health...
REM Check if web service is healthy (Windows equivalent of curl)
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:3000/health' -UseBasicParsing | Out-Null; Write-Host '✅ Web service is healthy' } catch { Write-Host '❌ Web service health check failed'; docker-compose logs line-bot-web; exit 1 }"

REM Check if scheduler is running
docker-compose ps line-bot-scheduler | findstr "Up" > nul
if errorlevel 1 (
    echo ❌ Scheduler service is not running
    docker-compose logs line-bot-scheduler
    exit /b 1
) else (
    echo ✅ Scheduler service is running
)

echo 🎉 Deployment completed successfully!
echo.
echo Services status:
docker-compose ps

echo.
echo To view logs:
echo   Web service: docker-compose logs -f line-bot-web
echo   Scheduler:   docker-compose logs -f line-bot-scheduler
echo   Database:    docker-compose logs -f mysql
echo.
echo To stop services:
echo   docker-compose down

endlocal