$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$pythonExe = if (Test-Path $venvPython) { $venvPython } else { "python" }

$releaseDir = Join-Path $root "release"
$pyiWork = Join-Path $root "build\pyinstaller-work"
$pyiSpec = Join-Path $root "build\pyinstaller-spec"

New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
New-Item -ItemType Directory -Force -Path $pyiWork | Out-Null
New-Item -ItemType Directory -Force -Path $pyiSpec | Out-Null

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r (Join-Path $root "requirements.txt")
& $pythonExe -m pip install pyinstaller

& $pythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --name AutoProtectAgent `
    --distpath $releaseDir `
    --workpath $pyiWork `
    --specpath $pyiSpec `
    (Join-Path $root "app\auto_protect_agent.py")

& $pythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --name SensitiveProtectorCLI `
    --distpath $releaseDir `
    --workpath $pyiWork `
    --specpath $pyiSpec `
    (Join-Path $root "app\sensitive_protector.py")

Write-Host ""
Write-Host "Build completed. EXEs:"
Get-ChildItem $releaseDir -Filter *.exe | Select-Object FullName, Length, LastWriteTime
