; Inno Setup Script for J.A.R.V.I.S. Prime Desktop
#define MyAppName "J.A.R.V.I.S. Prime"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Stark Industries / Antigravity"
#define MyAppExeName "JARVIS.exe"

[Setup]
AppId={{D1A39F0B-6311-4E62-959F-AE6E02F366FA}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\JARVIS Prime
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=C:\Users\KINGSAID\.gemini\antigravity\scratch\jarvis-prime\dist_installer
OutputBaseFilename=JARVIS_Prime_Setup_v2.0
SetupIconFile=C:\Users\KINGSAID\.gemini\antigravity\scratch\jarvis-prime\jarvis\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "Запускать Джарвиса при старте Windows (Автозагрузка)"; GroupDescription: "Автозапуск:"

[Files]
Source: "C:\Users\KINGSAID\.gemini\antigravity\scratch\jarvis-prime\dist\JARVIS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\jarvis\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\jarvis\icon.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
