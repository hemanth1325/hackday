$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$venv = Join-Path $root ".venv"
$venvPython = Join-Path $venv "Scripts\python.exe"

if (-not (Test-Path $venv)) {
    python -m venv $venv
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $root "requirements.txt")

New-Item -ItemType Directory -Force -Path (Join-Path $root "outgoing") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $root "keys") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $root "logs") | Out-Null

$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$shortcutPath = Join-Path $startupDir "SensitiveFolderAutoProtect.lnk"
$startScript = Join-Path $root "scripts\start-auto-protect-agent.ps1"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$startScript`""
$shortcut.WorkingDirectory = $root
$shortcut.WindowStyle = 7
$shortcut.Description = "Auto-encrypt sensitive data for files dropped in outgoing folder"
$shortcut.Save()

& $startScript

Write-Host ""
Write-Host "One-time setup complete."
Write-Host "Auto-start enabled at Windows login."
Write-Host "Put files here (auto encrypted in same folder): $(Join-Path $root 'outgoing')"
