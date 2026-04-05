$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$desktopDist = Join-Path $root "dist\DSSSupportDesktop"
$trayDist = Join-Path $root "dist\DSSSupportTray"
$installerRoot = Join-Path $root "installer"
$stagingRoot = Join-Path $installerRoot "staging"
$outputRoot = Join-Path $installerRoot "output"
$packageZip = Join-Path $stagingRoot "dss-support-tool-package.zip"
$installScript = Join-Path $installerRoot "install.ps1"
$stagedInstallScript = Join-Path $stagingRoot "install.ps1"
$sedPath = Join-Path $stagingRoot "dss-support-tool.sed"
$targetExe = Join-Path $outputRoot "dss-support-tool-installer.exe"

if (-not (Test-Path $desktopDist)) {
  throw "Desktop build not found at $desktopDist"
}

if (-not (Test-Path $trayDist)) {
  throw "Tray build not found at $trayDist"
}

New-Item -ItemType Directory -Force -Path $stagingRoot | Out-Null
New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null

Get-ChildItem -LiteralPath $stagingRoot -Force -ErrorAction SilentlyContinue | ForEach-Object {
  Remove-Item -LiteralPath $_.FullName -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $stagingRoot | Out-Null

Copy-Item -LiteralPath $installScript -Destination $stagedInstallScript -Force

Compress-Archive -Path $desktopDist, $trayDist -DestinationPath $packageZip -Force

$sedContent = @"
[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=0
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=
DisplayLicense=
FinishMessage=DSS Support Tool has been installed.
TargetName=$targetExe
FriendlyName=DSS Support Tool Installer
AppLaunched=powershell.exe -ExecutionPolicy Bypass -File install.ps1
PostInstallCmd=<None>
AdminQuietInstCmd=powershell.exe -ExecutionPolicy Bypass -File install.ps1
UserQuietInstCmd=powershell.exe -ExecutionPolicy Bypass -File install.ps1
SourceFiles=SourceFiles
[SourceFiles]
SourceFiles0=$stagingRoot
[SourceFiles0]
%FILE0%=
%FILE1%=
[Strings]
FILE0=install.ps1
FILE1=dss-support-tool-package.zip
"@

Set-Content -LiteralPath $sedPath -Value $sedContent -Encoding Ascii

& iexpress.exe /N $sedPath | Out-Null

if (-not (Test-Path $targetExe)) {
  throw "Installer build did not produce $targetExe"
}

Write-Host "Installer created at $targetExe"
