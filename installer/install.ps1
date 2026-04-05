$ErrorActionPreference = "Stop"

$packageZip = Join-Path $PSScriptRoot "dss-support-tool-package.zip"
$installRoot = Join-Path $env:LOCALAPPDATA "Programs\DSS Support Tool"
$startMenuRoot = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\DSS Support Tool"
$desktopPath = [Environment]::GetFolderPath("Desktop")

if (-not (Test-Path $packageZip)) {
  throw "Package archive not found: $packageZip"
}

New-Item -ItemType Directory -Force -Path $installRoot | Out-Null

Get-ChildItem -LiteralPath $installRoot -Force -ErrorAction SilentlyContinue | ForEach-Object {
  Remove-Item -LiteralPath $_.FullName -Recurse -Force
}

Expand-Archive -Path $packageZip -DestinationPath $installRoot -Force

New-Item -ItemType Directory -Force -Path $startMenuRoot | Out-Null

$shell = New-Object -ComObject WScript.Shell

$desktopShortcut = $shell.CreateShortcut((Join-Path $desktopPath "DSS Support Tool.lnk"))
$desktopShortcut.TargetPath = Join-Path $installRoot "DSSSupportDesktop\DSSSupportDesktop.exe"
$desktopShortcut.WorkingDirectory = Join-Path $installRoot "DSSSupportDesktop"
$desktopShortcut.Save()

$trayShortcut = $shell.CreateShortcut((Join-Path $startMenuRoot "DSS Support Tray.lnk"))
$trayShortcut.TargetPath = Join-Path $installRoot "DSSSupportTray\DSSSupportTray.exe"
$trayShortcut.WorkingDirectory = Join-Path $installRoot "DSSSupportTray"
$trayShortcut.Save()

$appShortcut = $shell.CreateShortcut((Join-Path $startMenuRoot "DSS Support Tool.lnk"))
$appShortcut.TargetPath = Join-Path $installRoot "DSSSupportDesktop\DSSSupportDesktop.exe"
$appShortcut.WorkingDirectory = Join-Path $installRoot "DSSSupportDesktop"
$appShortcut.Save()

Start-Process -FilePath (Join-Path $installRoot "DSSSupportDesktop\DSSSupportDesktop.exe")
