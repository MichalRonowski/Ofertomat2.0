; Inno Setup Script dla Ofertomat 2.0
; Tworzy profesjonalny instalator dla Windows

#define MyAppName "Ofertomat 2.0"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Twoja Firma"
#define MyAppURL "https://www.ofertomat.pl"
#define MyAppExeName "Ofertomat2.0.exe"

[Setup]
; Podstawowe informacje
AppId={{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Ścieżki instalacji
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Pliki wyjściowe
OutputDir=Output
OutputBaseFilename=Ofertomat2.0_Setup
SetupIconFile=compiler:Languages\Polish.isl

; Kompresja
Compression=lzma2
SolidCompression=yes

; Wymagania systemowe
WizardStyle=modern
MinVersion=10.0
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Język
ShowLanguageDialog=no

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Główny plik wykonawczy
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Przykładowe dane
Source: "produkty_gastronomia_przyklad.csv"; DestDir: "{app}"; Flags: ignoreversion

; Dokumentacja
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Ikona w Menu Start
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Ikona na pulpicie
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Uruchom po instalacji
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Usuń bazę danych przy deinstalacji (opcjonalnie)
Type: files; Name: "{app}\ofertomat.db"
Type: dirifempty; Name: "{app}"

[Code]
// Sprawdź, czy aplikacja jest uruchomiona przed instalacją
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

// Funkcja sprawdzająca wersję Windows
function IsWindows10OrLater: Boolean;
begin
  Result := (GetWindowsVersion >= $0A000000);
end;
