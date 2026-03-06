$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$shortcutPath = Join-Path $startupDir "SensitiveFolderAutoProtect.lnk"

if (Test-Path $shortcutPath) {
    Remove-Item $shortcutPath -Force
    Write-Host "Removed startup shortcut:"
    Write-Host $shortcutPath
} else {
    Write-Host "Startup shortcut not found."
}

& (Join-Path $root "scripts\stop-auto-protect-agent.ps1")
