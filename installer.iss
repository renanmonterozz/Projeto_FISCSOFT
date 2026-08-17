[Setup]
AppName=FISCSOFT
AppVersion=1.0
DefaultDirName={pf}\FISCSOFT
DefaultGroupName=FISCSOFT
OutputBaseFilename=FISCSOFT_Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
DisableDirPage=no
; Use project icon if present
SetupIconFile=assets\imagens\logo_fiscsoft.ico

[Files]
; Copia todo o conteúdo da pasta de build para a pasta de instalação
Source: "dist\\FISCSOFT\\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\FISCSOFT"; Filename: "{app}\FISCSOFT.exe"; IconFilename: "{app}\logo_fiscsoft.ico"
Name: "{userdesktop}\FISCSOFT"; Filename: "{app}\FISCSOFT.exe"; Tasks: desktopicon; IconFilename: "{app}\logo_fiscsoft.ico"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\FISCSOFT.exe"; Description: "Launch FISCSOFT"; Flags: nowait postinstall skipifsilent
