$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$exePath = Join-Path $root "release\AutoProtectAgent.exe"
$pidFile = Join-Path $root "release\agent-exe.pid"

if (-not (Test-Path $exePath)) {
    throw "AutoProtectAgent.exe not found. Build first with scripts\\build-exe.ps1."
}

$running = Get-Process -Name "AutoProtectAgent" -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -eq $exePath
}
if ($running) {
    $pidValue = $running[0].Id
    Set-Content -Path $pidFile -Value $pidValue
    Write-Host "EXE agent already running (PID: $pidValue)."
    exit 0
}

if (Test-Path $pidFile) {
    $existingPid = (Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if ($existingPid) {
        $existingProc = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
        if ($existingProc) {
            Write-Host "EXE agent already running (PID: $existingPid)."
            exit 0
        }
    }
}

$process = Start-Process -FilePath $exePath -PassThru -WorkingDirectory (Split-Path $exePath)
Set-Content -Path $pidFile -Value $process.Id

Write-Host "EXE agent started (PID: $($process.Id))."
Write-Host "Put files in: $(Join-Path $root 'release\outgoing')"
Write-Host "Send files from: $(Join-Path $root 'release\ready-to-send')"
