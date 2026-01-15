$EnvFilePath = "d:\AI Studio\newinfo\Line-bot-llm-mysql\.env"
$NewHost = "192.168.100.114"

Write-Host "🔄 Updating DB_HOST in .env to $NewHost..."

if (Test-Path $EnvFilePath) {
    $Content = Get-Content $EnvFilePath
    $NewContent = $Content -replace '^DB_HOST=.*$', "DB_HOST=$NewHost"
    $NewContent | Set-Content $EnvFilePath
    Write-Host "✅ .env updated successfully!"
    Write-Host "   Path: $EnvFilePath"
} else {
    Write-Error "❌ .env file not found at: $EnvFilePath"
    exit 1
}

Write-Host "`n🔄 Restarting Docker containers..."
Set-Location "d:\AI Studio\newinfo\Line-bot-llm-mysql"
docker compose restart line-bot-web line-bot-scheduler ebook-processor

Write-Host "`n🔍 Verifying connection..."
# Run verification script inside container to ensure connectivity from container network
docker compose exec line-bot-web node scripts/verify-db-connection.js

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Migration Verification Passed!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Migration Verification Failed. Please check logs above." -ForegroundColor Red
}
