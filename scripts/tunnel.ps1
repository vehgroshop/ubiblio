#Requires -Version 5.1
[CmdletBinding()]
param(
    [int]$Port = 8000,
    [int]$TimeoutSeconds = 120
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "Starting docker compose (dev)..." -ForegroundColor Cyan
docker compose -f docker-compose.dev.yml up -d
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

Write-Host "Waiting for http://127.0.0.1:$Port to respond..." -ForegroundColor Cyan
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$ready = $false
while ((Get-Date) -lt $deadline) {
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:$Port" -UseBasicParsing -TimeoutSec 3
        $ready = $true
        break
    } catch {
        # Any HTTP response (even 4xx/5xx) means the server is up
        if ($_.Exception.Response) { $ready = $true; break }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) { throw "App did not start on port $Port within $TimeoutSeconds seconds" }

Write-Host "App is up. Launching cloudflared tunnel..." -ForegroundColor Green
cloudflared tunnel --url "http://127.0.0.1:$Port"
