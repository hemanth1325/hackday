param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $projectRoot

if ($Clean) {
    if (Test-Path ".\build") { Remove-Item ".\build" -Recurse -Force }
    if (Test-Path ".\dist") { Remove-Item ".\dist" -Recurse -Force }
    if (Test-Path ".\WebcamGestureControl.spec") { Remove-Item ".\WebcamGestureControl.spec" -Force }
}

python -m pip install pyinstaller | Out-Host

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --console `
    --name WebcamGestureControl `
    --collect-data mediapipe `
    --collect-binaries mediapipe `
    --collect-data cv2 `
    --collect-binaries cv2 `
    --hidden-import mediapipe.python.solutions.hands `
    --hidden-import pyautogui `
    --exclude-module matplotlib `
    --exclude-module jax `
    --exclude-module jaxlib `
    --exclude-module tensorflow `
    --exclude-module torch `
    --exclude-module mediapipe.model_maker `
    --exclude-module mediapipe.tasks.python.metadata.metadata_writers `
    --add-data "app/config/actions.json;app/config" `
    app/main.py | Out-Host

$exePath = Join-Path $projectRoot "dist\WebcamGestureControl\WebcamGestureControl.exe"
if (-not (Test-Path $exePath)) {
    throw "Build failed: executable not found at $exePath"
}

Write-Host "Build complete: $exePath"
