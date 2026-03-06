$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$exePath = Join-Path $root "release\AutoProtectAgent.exe"

if (-not (Test-Path $exePath)) {
    throw "AutoProtectAgent.exe not found. Build first with scripts\\build-exe.ps1."
}

$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$shortcutPath = Join-Path $startupDir "AutoProtectAgent.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exePath
$shortcut.WorkingDirectory = (Split-Path $exePath)
$shortcut.WindowStyle = 7
$shortcut.Description = "Auto-protect outgoing files with sensitive-data encryption"
$shortcut.Save()

Write-Host "Startup shortcut created:"
Write-Host $shortcutPath
Write-Host "AutoProtectAgent will start on next Windows login."
