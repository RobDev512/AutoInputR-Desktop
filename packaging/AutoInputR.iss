#define MyAppName "AutoInputR"
#define MyAppVersion "1.3.0"
#define MyAppPublisher "Robert"
#define MyAppExeName "AutoInputR_v1.2.exe"

[Setup]
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
SetupIconFile=..\assets\branding\Logo2AIR.ico
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
Source: "..\AutoInputR_v1.2.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\branding\LogoAIR.png"; DestDir: "{app}\assets\branding"; Flags: ignoreversion
Source: "..\assets\branding\Logo2AIR.png"; DestDir: "{app}\assets\branding"; Flags: ignoreversion
Source: "..\assets\branding\Logo2AIR.ico"; DestDir: "{app}\assets\branding"; Flags: ignoreversion

[Icons]
Name: "{group}\AutoInputR"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\AutoInputR"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir AutoInputR"; Flags: nowait postinstall skipifsilent