param(
    [string]$SourceDir = "",
    [switch]$Launch
)

$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
if ([string]::IsNullOrWhiteSpace($SourceDir)) {
    $SourceDir = Join-Path $projectRoot "dist\WebcamGestureControl"
}

$installRoot = Join-Path $env:LOCALAPPDATA "Programs\WebcamGestureControl"
$exePath = Join-Path $installRoot "WebcamGestureControl.exe"

if (-not (Test-Path $SourceDir)) {
    throw "Source build folder not found: $SourceDir. Run scripts/build-exe.ps1 first."
}

if (Test-Path $installRoot) {
    Remove-Item $installRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $installRoot -Force | Out-Null
Copy-Item -Path (Join-Path $SourceDir "*") -Destination $installRoot -Recurse -Force

if (-not (Test-Path $exePath)) {
    throw "Install failed: executable missing at $exePath"
}

$desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "Webcam Gesture Control.lnk"
$startMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Webcam Gesture Control"
$startMenuShortcut = Join-Path $startMenuDir "Webcam Gesture Control.lnk"

if (-not (Test-Path $startMenuDir)) {
    New-Item -ItemType Directory -Path $startMenuDir -Force | Out-Null
}

$shell = New-Object -ComObject WScript.Shell

$desktopLink = $shell.CreateShortcut($desktopShortcut)
$desktopLink.TargetPath = $exePath
$desktopLink.WorkingDirectory = $installRoot
$desktopLink.IconLocation = $exePath
$desktopLink.Save()

$startLink = $shell.CreateShortcut($startMenuShortcut)
$startLink.TargetPath = $exePath
$startLink.WorkingDirectory = $installRoot
$startLink.IconLocation = $exePath
$startLink.Save()

Write-Host "Installed to: $installRoot"
Write-Host "Desktop shortcut: $desktopShortcut"
Write-Host "Start menu shortcut: $startMenuShortcut"

if ($Launch) {
    Start-Process -FilePath $exePath -WorkingDirectory $installRoot
}
