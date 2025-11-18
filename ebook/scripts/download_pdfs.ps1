# PDF 下載腳本
$downloadDir = "D:\ebook\downloads"

# 建立下載目錄
if (!(Test-Path $downloadDir)) {
    New-Item -ItemType Directory -Path $downloadDir | Out-Null
    Write-Host "已建立下載目錄: $downloadDir"
}

# 下載清單
$downloads = @(
    @{url="https://www2.budaedu.org/dharma-data/book-efile/CH826-21-01-001.pdf"; filename="CH826-21-01-001.pdf"; title="始終心要今說(修訂版) CH826-21"},
    @{url="https://www2.budaedu.org/dharma-data/book-fascicle-efile/CH550-06-01-001.PDF"; filename="CH550-06-01-001.PDF"; title="菩提道次第廣論白話注釋（一）菩提道次第廣論白話注釋（二） 菩提道次第廣論白話注釋（三） 菩提道次第廣論白話注釋（四） 菩提道次第廣論白話注釋（五） CH550-06"},
    @{url="https://www2.budaedu.org/dharma-data/book-efile/CH370-28-01-001.PDF"; filename="CH370-28-01-001.PDF"; title="大乘入楞伽經 CH370-28"},
    @{url="https://www2.budaedu.org/dharma-data/book-efile/CH113-01-01-001.pdf"; filename="CH113-01-01-001.pdf"; title="全部佛法的綱要 CH113-01"},
    @{url="https://www2.budaedu.org/dharma-data/book-efile/TCE15-01-001.pdf"; filename="TCE15-01-001.pdf"; title="藏中英對照：明心108－蓮花心海的智慧寶藏 TCE15"},
    @{url="https://www2.budaedu.org/dharma-data/book-efile/CH378-40-01-001.PDF"; filename="CH378-40-01-001.PDF"; title="大方廣圓覺修多羅了義經講記(2021年修訂版) CH378-40"},
    @{url="https://www2.budaedu.org/dharma-data/book-efile/CH350-16-01-001.PDF"; filename="CH350-16-01-001.PDF"; title="佛說無量壽經(魏譯本) CH350-16"},
    @{url="https://www2.budaedu.org/dharma-data/book-fascicle-efile/CH382-26-01-001.pdf"; filename="CH382-26-01-001.pdf"; title="楞嚴經講記 CH382-26"},
)

# 開始下載
$count = 0
foreach ($item in $downloads) {
    $count++
    $filepath = Join-Path $downloadDir $item.filename
    Write-Host "[$count/$($downloads.Count)] 下載: $($item.title)"
    Write-Host "  檔案: $($item.filename)"
    
    try {
        # 使用 Invoke-WebRequest 下載
        Invoke-WebRequest -Uri $item.url -OutFile $filepath -UseBasicParsing
        Write-Host "  ✓ 下載成功" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ 下載失敗: $_" -ForegroundColor Red
    }
}

Write-Host "`n下載完成！檔案儲存在: $downloadDir"
