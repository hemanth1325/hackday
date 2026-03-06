$ErrorActionPreference = "Stop"

$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$shortcutPath = Join-Path $startupDir "AutoProtectAgent.lnk"

if (Test-Path $shortcutPath) {
    Remove-Item $shortcutPath -Force
    Write-Host "Startup shortcut removed:"
    Write-Host $shortcutPath
} else {
    Write-Host "Startup shortcut not found."
}
