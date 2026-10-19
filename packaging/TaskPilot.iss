#define MyAppName "TaskPilot"
#define MyAppVersion "1.4.0"
#define MyAppPublisher "Robert"
#define MyAppExeName "TaskPilot.exe"

[Setup]
; Se conserva el AppId historico para permitir actualizaciones desde AutoInputR.
AppId={{A74C5D9D-2144-48D5-9F5E-8A1C6C2E1201}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\installer
OutputBaseFilename={#MyAppName}_Setup_v{#MyAppVersion}
SetupIconFile=..\assets\branding\TaskPilotIcon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones adicionales:"; Flags: unchecked

[Files]
Source: "..\TaskPilot.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\branding\TaskPilotLogo.png"; DestDir: "{app}\assets\branding"; Flags: ignoreversion
Source: "..\assets\branding\TaskPilotLogoHorizontal.png"; DestDir: "{app}\assets\branding"; Flags: ignoreversion
Source: "..\assets\branding\TaskPilotLogoTransparent.png"; DestDir: "{app}\assets\branding"; Flags: ignoreversion
Source: "..\assets\branding\TaskPilotMono.png"; DestDir: "{app}\assets\branding"; Flags: ignoreversion
Source: "..\assets\branding\TaskPilotIcon.png"; DestDir: "{app}\assets\branding"; Flags: ignoreversion
Source: "..\assets\branding\TaskPilotIcon.ico"; DestDir: "{app}\assets\branding"; Flags: ignoreversion

[Icons]
Name: "{group}\TaskPilot"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\TaskPilot"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir TaskPilot"; Flags: nowait postinstall skipifsilent
