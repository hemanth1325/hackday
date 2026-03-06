$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$exePath = Join-Path $root "release\AutoProtectAgent.exe"
$pidFile = Join-Path $root "release\agent-exe.pid"

$targetProcesses = Get-Process -Name "AutoProtectAgent" -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -eq $exePath
}
if ($targetProcesses) {
    $targetProcesses | ForEach-Object { Stop-Process -Id $_.Id -Force }
    Write-Host "Stopped EXE agent process count: $($targetProcesses.Count)"
} else {
    if (Test-Path $pidFile) {
        $pidValue = (Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
        if ($pidValue) {
            $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
            if ($process) {
                Stop-Process -Id $pidValue -Force
                Write-Host "EXE agent stopped (PID: $pidValue)."
            } else {
                Write-Host "Process not running; removed stale PID file."
            }
        } else {
            Write-Host "PID file was empty; cleaned up."
        }
    } else {
        Write-Host "No running EXE agent found."
    }
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
