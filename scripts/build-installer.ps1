$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$version = "0.2.0"

$desktopDist = Join-Path $root "dist\DSSSupportDesktop"
$trayDist = Join-Path $root "dist\DSSSupportTray"
$installerScript = Join-Path $root "installer\dss-support-tool.iss"
$isccPath = Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"
$outputRoot = Join-Path $root "installer\output"
$tempOutputRoot = Join-Path $root "installer\build-temp"
$targetExe = Join-Path $outputRoot "dss-support-tool-setup-$version.exe"
$tempExe = Join-Path $tempOutputRoot "dss-support-tool-setup-$version.exe"

if (-not (Test-Path $desktopDist)) {
  throw "Desktop build not found at $desktopDist"
}

if (-not (Test-Path $trayDist)) {
  throw "Tray build not found at $trayDist"
}

New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null
New-Item -ItemType Directory -Force -Path $tempOutputRoot | Out-Null

Get-ChildItem -LiteralPath $tempOutputRoot -Force -ErrorAction SilentlyContinue | ForEach-Object {
  Remove-Item -LiteralPath $_.FullName -Recurse -Force
}

if (-not (Test-Path $installerScript)) {
  throw "Inno Setup script not found at $installerScript"
}

if (-not (Test-Path $isccPath)) {
  throw "Inno Setup compiler not found at $isccPath"
}

& $isccPath "/O$tempOutputRoot" $installerScript

if (-not (Test-Path $tempExe)) {
  throw "Installer build did not produce $tempExe"
}

Move-Item -LiteralPath $tempExe -Destination $targetExe -Force

Write-Host "Installer created at $targetExe"
