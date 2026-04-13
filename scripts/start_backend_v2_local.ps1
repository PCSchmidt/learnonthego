param(
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir '..')
$BackendDir = Join-Path $RepoRoot 'backend'

if (-not $env:LOTG_PYTHON_EXE -or [string]::IsNullOrWhiteSpace($env:LOTG_PYTHON_EXE)) {
    $env:LOTG_PYTHON_EXE = (Join-Path $RepoRoot '..\.venv\Scripts\python.exe')
}

if (-not $env:JWT_SECRET_KEY -or [string]::IsNullOrWhiteSpace($env:JWT_SECRET_KEY)) {
    $env:JWT_SECRET_KEY = 'local-dev-jwt-secret'
}

if (-not $env:ENABLE_V2_PIPELINE -or [string]::IsNullOrWhiteSpace($env:ENABLE_V2_PIPELINE)) {
    $env:ENABLE_V2_PIPELINE = 'true'
}

if (-not (Test-Path $env:LOTG_PYTHON_EXE)) {
    throw "Python executable not found at $($env:LOTG_PYTHON_EXE). Set LOTG_PYTHON_EXE and retry."
}

Write-Host "Starting LearnOnTheGo backend"
Write-Host "Backend dir: $BackendDir"
Write-Host "Python: $($env:LOTG_PYTHON_EXE)"
Write-Host "Port: $Port"
Write-Host "ENABLE_V2_PIPELINE=$($env:ENABLE_V2_PIPELINE)"

Set-Location $BackendDir
& $env:LOTG_PYTHON_EXE -m uvicorn main:app --host 0.0.0.0 --port $Port
