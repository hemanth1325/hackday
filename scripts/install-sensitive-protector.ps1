$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$venv = Join-Path $root ".venv"

if (-not (Test-Path $venv)) {
    python -m venv $venv
}

$pythonExe = Join-Path $venv "Scripts\python.exe"
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r (Join-Path $root "requirements.txt")

Write-Host "Sensitive File Protector installed."
Write-Host "Run:"
Write-Host "  .\.venv\Scripts\python.exe -m app.sensitive_protector protect --input examples\sensitive-input.txt --output examples\sensitive-output.txt --key-file examples\receiver.key"
