[Setup]
; Información General
AppName=World of Warcraft - Séquito del Terror
AppVersion=1.12.1
AppPublisher=El Séquito del Terror / Capycraft
AppPublisherURL=https://sequitodelterror.netlify.app/
AppSupportURL=https://sequitodelterror.netlify.app/
AppUpdatesURL=https://sequitodelterror.netlify.app/

; Directorios de Instalación
DefaultDirName={sd}\WoW Capycraft Sequito
DefaultGroupName=Séquito del Terror WoW
DisableProgramGroupPage=yes

; Configuración del Instalador
OutputDir=Output
OutputBaseFilename=Instalador_Oficial_Sequito_WoW
SetupIconFile=launcher-src\assets\logo.ico
WizardStyle=modern

; Compresión (Extrema para empaquetar 5GB)
Compression=lzma2/ultra64
SolidCompression=yes
DiskSpanning=yes
DiskSliceSize=max

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Copiar el Launcher y configuraciones desde la carpeta de desarrollo del launcher
Source: "launcher-src\dist\SequitoLauncher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "launcher-src\config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "launcher-src\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Copiar TODOS los archivos del juego (Data, Interface, WoW.exe, etc) excluyendo los archivos fuente del launcher y de git
Source: "*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "launcher-src\*, Output\*, *.iss, .git\*, .vscode\*, *.log, test_install_dir\*"

[Icons]
; Crear los accesos directos
Name: "{group}\Séquito del Terror Launcher"; Filename: "{app}\SequitoLauncher.exe"; IconFilename: "{app}\assets\logo.ico"
Name: "{autodesktop}\Séquito del Terror Launcher"; Filename: "{app}\SequitoLauncher.exe"; IconFilename: "{app}\assets\logo.ico"; Tasks: desktopicon

[Run]
; Ejecutar el Launcher al terminar
Filename: "{app}\SequitoLauncher.exe"; Description: "Lanzar el juego ahora"; Flags: nowait postinstall skipifsilent
