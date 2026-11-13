#ifndef MyAppVersion
  #define MyAppVersion "1.3.0"
#endif

[Setup]
AppId={{8E4A9D2C-5B71-4F3A-9C6E-2D8B4A1F7053}
AppName=MatuChat
AppVersion={#MyAppVersion}
AppPublisher=lucklyeeg
DefaultDirName={autopf}\MatuChat
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=MatuChat-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\MatuChat.exe
CloseApplications=yes

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\MatuChat\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\MatuChat"; Filename: "{app}\MatuChat.exe"
Name: "{autodesktop}\MatuChat"; Filename: "{app}\MatuChat.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MatuChat.exe"; Description: "{cm:LaunchProgram,MatuChat}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{userappdata}\MatuChat');
    if DirExists(DataDir) then
    begin
      if MsgBox('Kay' + #$0131 + 'tl' + #$0131 + ' ayarlar ve API anahtarlar' + #$0131 + ' da silinsin mi?', mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
        DelTree(DataDir, True, True, True);
    end;
  end;
end;
