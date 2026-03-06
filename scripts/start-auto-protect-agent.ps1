$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$pythonExe = if (Test-Path $venvPython) { $venvPython } else { "python" }

$inputDir = Join-Path $root "outgoing"
$keyDir = Join-Path $root "keys"
$keyFile = Join-Path $keyDir "receiver.key"
$pidFile = Join-Path $root "agent.pid"
$logDir = Join-Path $root "logs"
$stdoutLog = Join-Path $logDir "agent.out.log"
$stderrLog = Join-Path $logDir "agent.err.log"
$clawmatryConfigPath = Join-Path $root "clawmatry.config.json"

New-Item -ItemType Directory -Force -Path $inputDir | Out-Null
New-Item -ItemType Directory -Force -Path $keyDir | Out-Null
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

if (Test-Path $pidFile) {
    $existingPid = (Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if ($existingPid) {
        $existingProc = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
        if ($existingProc) {
            Write-Host "Auto-protect agent is already running (PID: $existingPid)."
            exit 0
        }
    }
}

$extraArgs = ""
if (Test-Path $clawmatryConfigPath) {
    $cfg = Get-Content $clawmatryConfigPath -Raw | ConvertFrom-Json
    if ($cfg.upload_url) {
        $extraArgs += " --upload-url `"$($cfg.upload_url)`""
    }
    if ($cfg.upload_token) {
        $extraArgs += " --upload-token `"$($cfg.upload_token)`""
    }
    if ($cfg.upload_auth_header) {
        $extraArgs += " --upload-auth-header `"$($cfg.upload_auth_header)`""
    }
    if ($cfg.upload_field) {
        $extraArgs += " --upload-field `"$($cfg.upload_field)`""
    }
    if ($cfg.upload_only_if_sensitive -eq $true) {
        $extraArgs += " --upload-only-if-sensitive"
    }
}

$arguments = "-m app.sensitive_protector watch --input-dir `"$inputDir`" --in-place --key-file `"$keyFile`" --interval-seconds 2$extraArgs"

$process = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList $arguments `
    -WindowStyle Hidden `
    -PassThru `
    -WorkingDirectory $root `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog
Set-Content -Path $pidFile -Value $process.Id

Write-Host "Auto-protect agent started."
Write-Host "PID: $($process.Id)"
Write-Host "Drop files into: $inputDir"
Write-Host "Files are encrypted in-place inside: $inputDir"
if (Test-Path $clawmatryConfigPath) {
    Write-Host "Clawmatry upload config loaded: $clawmatryConfigPath"
}
Write-Host "Logs: $stdoutLog"
