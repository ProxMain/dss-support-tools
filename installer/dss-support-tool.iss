[Setup]
AppName=DSS Support Tool
AppVersion=0.2.0
AppVerName=DSS Support Tool 0.2.0
AppPublisher=Space Seals
DefaultDirName={autopf}\DSS Support Tool
DefaultGroupName=DSS Support Tool
OutputDir=output
OutputBaseFilename=dss-support-tool-setup-0.2.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\img\space-seals-app-icon.ico
UninstallDisplayIcon={app}\desktop\DSSSupportDesktop.exe
WizardImageFile=..\img\SPACESEALS-Banner.png
WizardSmallImageFile=..\img\SPACESEALS-Logo.png

[Files]
Source: "..\dist\DSSSupportDesktop\*"; DestDir: "{app}\desktop"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\DSSSupportTray\*"; DestDir: "{app}\tray"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DSS Support Tool"; Filename: "{app}\desktop\DSSSupportDesktop.exe"; IconFilename: "{app}\desktop\DSSSupportDesktop.exe"
Name: "{group}\DSS Support Tray"; Filename: "{app}\tray\DSSSupportTray.exe"; IconFilename: "{app}\tray\DSSSupportTray.exe"
Name: "{group}\Uninstall DSS Support Tool"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\tray\DSSSupportTray.exe"; Description: "Launch DSS Support Tray"; Flags: nowait postinstall skipifsilent
