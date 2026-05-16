#Requires -Version 5.1
<#
.SYNOPSIS
Creates a Desktop shortcut that launches Anna's Boekenpaleis (docker compose + cloudflared named tunnel).

.DESCRIPTION
Run this once. Double-clicking the resulting shortcut on your Desktop will run scripts/launch.cmd, which starts the compose stack and opens the named tunnel.

.PARAMETER Name
File name of the shortcut on the Desktop (without .lnk). Defaults to "Anna's Boekenpaleis".

.EXAMPLE
powershell -ExecutionPolicy Bypass -File .\scripts\install-shortcut.ps1
#>
[CmdletBinding()]
param(
    [string]$Name = "Anna's Boekenpaleis"
)

$ErrorActionPreference = 'Stop'

$repoRoot   = Split-Path -Parent $PSScriptRoot
$launcher   = Join-Path $repoRoot 'scripts\launch.cmd'
$iconSource = Join-Path $repoRoot 'favicon.ico'

if (-not (Test-Path $launcher)) { throw "Launcher not found: $launcher" }

$desktop  = [Environment]::GetFolderPath('Desktop')
$lnkPath  = Join-Path $desktop "$Name.lnk"

$shell    = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($lnkPath)
$shortcut.TargetPath       = $launcher
$shortcut.WorkingDirectory = $repoRoot
$shortcut.WindowStyle      = 1   # normal window so you can see cloudflared logs
$shortcut.Description      = "Start Anna's Boekenpaleis (Docker + Cloudflare tunnel)"
if (Test-Path $iconSource) { $shortcut.IconLocation = "$iconSource,0" }
$shortcut.Save()

Write-Host "Created shortcut: $lnkPath" -ForegroundColor Green
Write-Host "Double-click it to start the app." -ForegroundColor Green
