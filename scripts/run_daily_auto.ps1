# Daily auto pipeline (email + full chat via saved Grok session).
# Scheduled by Windows Task Scheduler — you do NOT need to run this manually each day.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Python = "C:\Python\Python312\python.exe"
if (-not (Test-Path $Python)) {
    $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $Python) {
    Write-Error "Python not found"
    exit 1
}

$LogDir = Join-Path $Root "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir ("daily_{0:yyyyMMdd_HHmmss}.log" -f (Get-Date))

function Log([string]$msg) {
    $line = "[{0:yyyy-MM-dd HH:mm:ss}] {1}" -f (Get-Date), $msg
    Add-Content -Path $Log -Value $line -Encoding UTF8
    Write-Host $line
}

Log "=== grok-daily-digest auto start ==="
Log "Root=$Root"

# Wait a few minutes after Grok Tasks (15:00) so email is delivered
# Task is scheduled at 15:20 by default; extra small delay for slow mail
Start-Sleep -Seconds 30

$env:PYTHONUNBUFFERED = "1"
& $Python -u (Join-Path $Root "scripts\run_daily.py") --force *>> $Log 2>&1
$code = $LASTEXITCODE
Log "run_daily exit=$code"

# Optional: push digests to GitHub if git remote exists
if (Test-Path (Join-Path $Root ".git")) {
    try {
        git -C $Root add digests 2>> $Log
        $status = git -C $Root status --porcelain digests
        if ($status) {
            git -C $Root commit -m "chore(digest): auto archive $(Get-Date -Format yyyy-MM-dd)" 2>> $Log
            git -C $Root push origin main 2>> $Log
            Log "git push done"
        } else {
            Log "no digest changes to push"
        }
    } catch {
        Log "git step skipped/failed: $_"
    }
}

Log "=== done ==="
exit $code
