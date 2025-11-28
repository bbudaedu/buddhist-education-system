# Test Buddhist Education API endpoints
$ErrorActionPreference = 'Continue'

$baseUrl = "https://publish.budaedu.org/laravel/public/api"

# Test endpoints
$endpoints = @(
    "books",
    "dharmas",
    "lectures",
    "videos",
    "series",
    "media",
    "livestreams",
    "courses"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing Buddhist Education API Endpoints" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

foreach ($endpoint in $endpoints) {
    $url = "$baseUrl/$endpoint`?limit=2"
    Write-Host "Testing: $url" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -ErrorAction Stop
        Write-Host "✓ SUCCESS - $endpoint endpoint exists!" -ForegroundColor Green
        Write-Host "  Response preview:" -ForegroundColor Gray
        $response | ConvertTo-Json -Depth 2 -Compress | Write-Host
        Write-Host ""
    }
    catch {
        if ($_.Exception.Response.StatusCode.value__ -eq 404) {
            Write-Host "✗ 404 - $endpoint endpoint not found" -ForegroundColor Red
        }
        else {
            Write-Host "✗ ERROR - $($_.Exception.Message)" -ForegroundColor Red
        }
        Write-Host ""
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing Complete" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
