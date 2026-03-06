$ErrorActionPreference = "Stop"

$root = Split-Path -Path $PSScriptRoot -Parent
$example = Join-Path $root "clawmatry.config.example.json"
$config = Join-Path $root "clawmatry.config.json"

if (-not (Test-Path $example)) {
    throw "Example config not found: $example"
}

Copy-Item $example $config -Force
Write-Host "Created config file:"
Write-Host $config
Write-Host "Edit upload_url and upload_token, then restart agent."
