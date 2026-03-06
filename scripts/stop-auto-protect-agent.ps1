$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$pidFile = Join-Path $root "agent.pid"

if (-not (Test-Path $pidFile)) {
    Write-Host "Agent PID file not found. Agent may already be stopped."
    exit 0
}

$pidValue = (Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
if (-not $pidValue) {
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    Write-Host "PID file was empty; cleaned up."
    exit 0
}

$process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Id $pidValue -Force
    Write-Host "Auto-protect agent stopped (PID: $pidValue)."
} else {
    Write-Host "Process not running; removing stale PID file."
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
