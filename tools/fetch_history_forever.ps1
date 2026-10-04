$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot
$historyDir = Join-Path $root "danmaku\history"
$log = Join-Path $historyDir "fetch_forever.log"
$summaryFile = Join-Path $historyDir "summary.json"

Set-Location $root
$env:DANMAKU_PACE = "2.0"
$env:DANMAKU_RISK_COOLDOWN = "600"

while ($true) {
    $stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Path $log -Value "[$stamp] start fetch_history_danmaku"

    python tools\fetch_history_danmaku.py --workers 1 --order deficit --no-prompt 2>&1 |
        Tee-Object -FilePath (Join-Path $historyDir "fetch_stdout.log") -Append

    $done = $false
    if (Test-Path $summaryFile) {
        try {
            $summary = Get-Content -Path $summaryFile -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($summary.pages -gt 0 -and $summary.pages_done -ge $summary.pages -and $summary.errors -eq 0 -and -not $summary.aborted) {
                $done = $true
            }
        }
        catch {
            Add-Content -Path $log -Value "summary parse failed: $($_.Exception.Message)"
        }
    }

    if ($done) {
        $stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        Add-Content -Path $log -Value "[$stamp] all pages complete"
        python tools\fetch_danmaku.py --aggregate-only 2>&1 |
            Tee-Object -FilePath (Join-Path $historyDir "aggregate.log") -Append
        break
    }

    $stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Path $log -Value "[$stamp] incomplete; retry in 30 minutes"
    Start-Sleep -Seconds 1800
}
