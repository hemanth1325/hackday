$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$pythonExe = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Virtual environment not found. Run scripts/install-sensitive-protector.ps1 first."
}

& $pythonExe -m app.sensitive_protector protect `
    --input (Join-Path $root "examples\sensitive-input.txt") `
    --output (Join-Path $root "examples\sensitive-output.txt") `
    --key-file (Join-Path $root "examples\receiver.key")

& $pythonExe -m app.sensitive_protector decrypt `
    --input (Join-Path $root "examples\sensitive-output.txt") `
    --output (Join-Path $root "examples\sensitive-restored.txt") `
    --key-file (Join-Path $root "examples\receiver.key")

Write-Host ""
Write-Host "Input file:"
Get-Content (Join-Path $root "examples\sensitive-input.txt")
Write-Host ""
Write-Host "Protected file:"
Get-Content (Join-Path $root "examples\sensitive-output.txt")
Write-Host ""
Write-Host "Restored file:"
Get-Content (Join-Path $root "examples\sensitive-restored.txt")
