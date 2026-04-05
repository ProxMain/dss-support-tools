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
  --windowed `
  --collect-submodules dss_support_tool `
  --hidden-import dss_support_tool.service `
  --hidden-import PySide6 `
  --hidden-import PySide6.QtWebEngineWidgets `
  --add-data "src\dss_support_tool\static;dss_support_tool\static" `
  --add-data "..\langpack-browser\dist;dss_support_tool\langpack_dist" `
  --add-data "..\tool-scraper\data;tool-scraper\data" `
  "src\dss_support_tool\desktop.py"

& $python -m PyInstaller `
  --noconfirm `
  --clean `
  --name DSSSupportTray `
  --windowed `
  --collect-submodules dss_support_tool `
  --hidden-import dss_support_tool.service `
  --hidden-import PySide6 `
  --hidden-import PySide6.QtWebEngineWidgets `
  --add-data "src\dss_support_tool\static;dss_support_tool\static" `
  --add-data "..\langpack-browser\dist;dss_support_tool\langpack_dist" `
  --add-data "..\tool-scraper\data;tool-scraper\data" `
  "src\dss_support_tool\tray.py"

Write-Host "Build complete."
