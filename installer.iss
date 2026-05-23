; Rota AI - Inno Setup installer script
; Requires: Inno Setup 6 (https://jrsoftware.org/isdl.php)
; Build: Open this file in Inno Setup, press F9 (or Ctrl+F9 to compile only)
; Output: installer-output\RotaAI-Setup.exe

#define AppName "Rota AI"
#define AppVersion "1.0.0"
#define AppPublisher "Rota AI"
#define AppURL "https://github.com/krthik20050/rota-ai"
#define AppExeName "RotaAI.exe"
#define SourceDir "dist\RotaAI"

[Setup]
AppId={{A7F3C2E1-4B8D-4F2A-9C1E-8D3F5A2B6E4C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer-output
OutputBaseFilename=RotaAI-Setup
SetupIconFile=desktop\assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "Start Rota AI when Windows starts"; GroupDescription: "Startup"

[Files]
; Everything PyInstaller built
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start menu
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
; Desktop (optional)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
; Startup (optional)
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: startupicon

[Run]
; Offer to launch after install
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any user-generated cache files on uninstall
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\_MEI*"
