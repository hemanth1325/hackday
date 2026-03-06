$ErrorActionPreference = "Stop"

$installRoot = Join-Path $env:LOCALAPPDATA "Programs\WebcamGestureControl"
$desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "Webcam Gesture Control.lnk"
$startMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Webcam Gesture Control"
$startMenuShortcut = Join-Path $startMenuDir "Webcam Gesture Control.lnk"

if (Test-Path $desktopShortcut) { Remove-Item $desktopShortcut -Force }
if (Test-Path $startMenuShortcut) { Remove-Item $startMenuShortcut -Force }
if (Test-Path $startMenuDir) { Remove-Item $startMenuDir -Force }
if (Test-Path $installRoot) { Remove-Item $installRoot -Recurse -Force }

Write-Host "Uninstalled Webcam Gesture Control."
