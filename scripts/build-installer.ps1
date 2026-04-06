$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$version = "0.2.0"

$desktopDist = Join-Path $root "dist\DSSSupportDesktop"
$trayDist = Join-Path $root "dist\DSSSupportTray"
$installerScript = Join-Path $root "installer\dss-support-tool.iss"
$isccPath = Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"
$outputRoot = Join-Path $root "installer\output"

if (-not (Test-Path $desktopDist)) {
  throw "Desktop build not found at $desktopDist"
}

if (-not (Test-Path $trayDist)) {
  throw "Tray build not found at $trayDist"
}

New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null

if (-not (Test-Path $installerScript)) {
  throw "Inno Setup script not found at $installerScript"
}

if (-not (Test-Path $isccPath)) {
  throw "Inno Setup compiler not found at $isccPath"
}

& $isccPath $installerScript

$targetExe = Join-Path $outputRoot "dss-support-tool-setup-$version.exe"
if (-not (Test-Path $targetExe)) {
  throw "Installer build did not produce $targetExe"
}

Write-Host "Installer created at $targetExe"
