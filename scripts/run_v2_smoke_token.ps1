param(
    [switch]$StrictByok
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir '..')

if (-not $env:LOTG_PYTHON_EXE -or [string]::IsNullOrWhiteSpace($env:LOTG_PYTHON_EXE)) {
    $env:LOTG_PYTHON_EXE = (Join-Path $RepoRoot '..\.venv\Scripts\python.exe')
}

if (-not (Test-Path $env:LOTG_PYTHON_EXE)) {
    throw "Python executable not found at $($env:LOTG_PYTHON_EXE). Set LOTG_PYTHON_EXE and retry."
}

if (-not $env:LOTG_TOKEN -or [string]::IsNullOrWhiteSpace($env:LOTG_TOKEN)) {
    throw 'LOTG_TOKEN is required for token-based smoke test.'
}

if (-not $env:LOTG_BASE_URL -or [string]::IsNullOrWhiteSpace($env:LOTG_BASE_URL)) {
    $env:LOTG_BASE_URL = 'http://localhost:8000'
}

if (-not $env:LOTG_TIMEOUT_SECONDS -or [string]::IsNullOrWhiteSpace($env:LOTG_TIMEOUT_SECONDS)) {
    $env:LOTG_TIMEOUT_SECONDS = '3'
}

if ($StrictByok) {
    $env:LOTG_STRICT_BYOK = 'true'
} elseif (-not $env:LOTG_STRICT_BYOK -or [string]::IsNullOrWhiteSpace($env:LOTG_STRICT_BYOK)) {
    $env:LOTG_STRICT_BYOK = 'false'
}

Write-Host "Running V2 smoke test"
Write-Host "Base URL: $($env:LOTG_BASE_URL)"
Write-Host "Timeout: $($env:LOTG_TIMEOUT_SECONDS)s"
Write-Host "Strict BYOK: $($env:LOTG_STRICT_BYOK)"

Set-Location $RepoRoot
& $env:LOTG_PYTHON_EXE -u scripts\v2_endpoint_smoke.py
