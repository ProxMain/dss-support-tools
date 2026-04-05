$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
  throw "Virtual environment Python not found at $python"
}

Write-Host "Building DSS Support Tool executables..."

& $python -m PyInstaller `
  --noconfirm `
  --clean `
  --name DSSSupportDesktop `
  --icon "img\space-seals-app-icon.ico" `
  --windowed `
  --collect-submodules dss_support_tool `
  --hidden-import dss_support_tool.service `
  --hidden-import PySide6 `
  --hidden-import PySide6.QtWebEngineWidgets `
  --add-data "src\dss_support_tool\static;dss_support_tool\static" `
  --add-data "img\space-seals-app-icon.png;dss_support_tool\assets" `
  --add-data "..\langpack-browser\dist;dss_support_tool\langpack_dist" `
  --add-data "..\tool-scraper\data;tool-scraper\data" `
  "src\dss_support_tool\desktop.py"
if ($LASTEXITCODE -ne 0) {
  throw "Desktop build failed with exit code $LASTEXITCODE"
}

& $python -m PyInstaller `
  --noconfirm `
  --clean `
  --name DSSSupportTray `
  --icon "img\space-seals-app-icon.ico" `
  --windowed `
  --collect-submodules dss_support_tool `
  --hidden-import dss_support_tool.service `
  --hidden-import PySide6 `
  --hidden-import PySide6.QtWebEngineWidgets `
  --add-data "src\dss_support_tool\static;dss_support_tool\static" `
  --add-data "img\space-seals-app-icon.png;dss_support_tool\assets" `
  --add-data "..\langpack-browser\dist;dss_support_tool\langpack_dist" `
  --add-data "..\tool-scraper\data;tool-scraper\data" `
  "src\dss_support_tool\tray.py"
if ($LASTEXITCODE -ne 0) {
  throw "Tray build failed with exit code $LASTEXITCODE"
}

Write-Host "Build complete."
