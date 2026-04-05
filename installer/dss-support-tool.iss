[Setup]
AppName=DSS Support Tool
AppVersion=0.1.0
DefaultDirName={autopf}\DSS Support Tool
DefaultGroupName=DSS Support Tool
OutputDir=output
OutputBaseFilename=dss-support-tool-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\DSSSupportDesktop\*"; DestDir: "{app}\desktop"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\DSSSupportTray\*"; DestDir: "{app}\tray"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DSS Support Tool"; Filename: "{app}\desktop\DSSSupportDesktop.exe"
Name: "{group}\DSS Support Tray"; Filename: "{app}\tray\DSSSupportTray.exe"
Name: "{group}\Uninstall DSS Support Tool"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\tray\DSSSupportTray.exe"; Description: "Launch DSS Support Tray"; Flags: nowait postinstall skipifsilent
