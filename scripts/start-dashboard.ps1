$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$venv = Join-Path $root ".venv"
$venvPython = Join-Path $venv "Scripts\python.exe"

if (-not (Test-Path $venv)) {
    python -m venv $venv
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $root "requirements.txt")

& $venvPython -m streamlit run (Join-Path $root "app\dashboard.py") --server.port 8501 --server.headless true
