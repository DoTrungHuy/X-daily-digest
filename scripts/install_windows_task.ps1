# Install Windows Scheduled Task for fully automatic daily digest.
# Run once in PowerShell (can be non-admin for current-user task):
#   powershell -ExecutionPolicy Bypass -File scripts\install_windows_task.ps1

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Script = Join-Path $Root "scripts\run_daily_auto.ps1"
$TaskName = "GrokDailyDigest"

if (-not (Test-Path $Script)) {
    Write-Error "Missing $Script"
    exit 1
}

# 15:20 local time — after gork-daily 15:00 push
$Time = "15:20"

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Script`"" `
    -WorkingDirectory $Root

$Trigger = New-ScheduledTaskTrigger -Daily -At $Time

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

# Prefer running whether user is logged on or not if possible; Interactive for browser fallback
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Auto: Grok Tasks email + full chat archive to digests/ (after 15:00)" | Out-Null

Write-Host "OK: Scheduled task '$TaskName' installed."
Write-Host "  Runs daily at $Time (local time)"
Write-Host "  Script: $Script"
Write-Host "  Logs:   $Root\logs\"
Write-Host ""
Write-Host "One-time only (if not done): python scripts\grok_login.py"
Write-Host "Test now:  schtasks /Run /TN `"$TaskName`""
Write-Host "Remove:    Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false"
