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
; === LAUNCHER y CONFIGURACION ===
Source: "launcher-src\dist\SequitoLauncher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "launcher-src\config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "launcher-src\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; === EJECUTABLES y DLLs DEL JUEGO ===
Source: "WoW.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "turtle-wow.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dbghelp.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "DivxDecoder.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "fmod.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "ijl15.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "nampower.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "no1600x1200.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "Scan.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "SDL.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "twloader.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "unicows.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "realmlist.wtf"; DestDir: "{app}"; Flags: ignoreversion

; === DATOS DEL JUEGO (MPQs) ===
Source: "Data\*"; DestDir: "{app}\Data"; Flags: ignoreversion recursesubdirs createallsubdirs

; === ADDONS DEL CLAN (solo carpetas de addons, sin archivos sueltos de desarrollo) ===
Source: "Interface\AddOns\Atlas-TW\*"; DestDir: "{app}\Interface\AddOns\Atlas-TW"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\aux-addon\*"; DestDir: "{app}\Interface\AddOns\aux-addon"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\BigWigs\*"; DestDir: "{app}\Interface\AddOns\BigWigs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_AuctionUI\*"; DestDir: "{app}\Interface\AddOns\Blizzard_AuctionUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_BattlefieldMinimap\*"; DestDir: "{app}\Interface\AddOns\Blizzard_BattlefieldMinimap"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_BindingUI\*"; DestDir: "{app}\Interface\AddOns\Blizzard_BindingUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_CombatText\*"; DestDir: "{app}\Interface\AddOns\Blizzard_CombatText"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_CraftUI\*"; DestDir: "{app}\Interface\AddOns\Blizzard_CraftUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_GMSurveyUI\*"; DestDir: "{app}\Interface\AddOns\Blizzard_GMSurveyUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_InspectUI\*"; DestDir: "{app}\Interface\AddOns\Blizzard_InspectUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_MacroUI\*"; DestDir: "{app}\Interface\AddOns\Blizzard_MacroUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_RaidUI\*"; DestDir: "{app}\Interface\AddOns\Blizzard_RaidUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_TalentUI\*"; DestDir: "{app}\Interface\AddOns\Blizzard_TalentUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_TradeSkillUI\*"; DestDir: "{app}\Interface\AddOns\Blizzard_TradeSkillUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Blizzard_TrainerUI\*"; DestDir: "{app}\Interface\AddOns\Blizzard_TrainerUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\DoTimer\*"; DestDir: "{app}\Interface\AddOns\DoTimer"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\EquipCompare\*"; DestDir: "{app}\Interface\AddOns\EquipCompare"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\gm-addon\*"; DestDir: "{app}\Interface\AddOns\gm-addon"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\HealBot\*"; DestDir: "{app}\Interface\AddOns\HealBot"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\NampowerSettings\*"; DestDir: "{app}\Interface\AddOns\NampowerSettings"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\pfUI\*"; DestDir: "{app}\Interface\AddOns\pfUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\QuestVoice\*"; DestDir: "{app}\Interface\AddOns\QuestVoice"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\ShaguTweaks-master\*"; DestDir: "{app}\Interface\AddOns\ShaguTweaks-master"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\TerrorMeter\*"; DestDir: "{app}\Interface\AddOns\TerrorMeter"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\TerrorSquadAI\*"; DestDir: "{app}\Interface\AddOns\TerrorSquadAI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\TurtleHonorSpyEnhanced\*"; DestDir: "{app}\Interface\AddOns\TurtleHonorSpyEnhanced"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\TurtleLoot\*"; DestDir: "{app}\Interface\AddOns\TurtleLoot"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Turtle_General\*"; DestDir: "{app}\Interface\AddOns\Turtle_General"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\Turtle_GroupUI\*"; DestDir: "{app}\Interface\AddOns\Turtle_GroupUI"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\WCS_Brain\*"; DestDir: "{app}\Interface\AddOns\WCS_Brain"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Interface\AddOns\WIM\*"; DestDir: "{app}\Interface\AddOns\WIM"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Crear los accesos directos
Name: "{group}\Séquito del Terror Launcher"; Filename: "{app}\SequitoLauncher.exe"; IconFilename: "{app}\assets\logo.ico"
Name: "{autodesktop}\Séquito del Terror Launcher"; Filename: "{app}\SequitoLauncher.exe"; IconFilename: "{app}\assets\logo.ico"; Tasks: desktopicon

[Run]
; Ejecutar el Launcher al terminar
Filename: "{app}\SequitoLauncher.exe"; Description: "Lanzar el juego ahora"; Flags: nowait postinstall skipifsilent
