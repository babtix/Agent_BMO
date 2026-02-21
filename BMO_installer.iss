; Voice Assistant BMO - Production Ready Installer
; Inno Setup Script - Ready to compile

#define MyAppName "Voice Assistant BMO"
#define MyAppVersion "4.0.0"
#define MyAppPublisher "BABTIX"
#define MyAppURL "https://github.com/babtix/Agent_BMO"
#define MyAppExeName "BMO_v4.exe"

[Setup]
; App identification
AppId={{B4C5D6E7-F8A9-0123-4567-89ABCDEF0123}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL=https://www.instagram.com/papitx0/
AppUpdatesURL={#MyAppURL}/releases
AppCopyright=Copyright (C) 2026 {#MyAppPublisher}

; Installation directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=..\installer_output
OutputBaseFilename=VoiceAssistant_BMO_Setup_v{#MyAppVersion}_x64
SetupIconFile=ico.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273

; Appearance
WizardStyle=modern
DisableWelcomePage=no

; Requirements
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0.17763

; Misc
AllowNoIcons=yes
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Types]
Name: "full"; Description: "Full installation"
Name: "compact"; Description: "Compact installation"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
Name: "main"; Description: "Main Application"; Types: full compact custom; Flags: fixed
Name: "docs"; Description: "Documentation"; Types: full
Name: "shortcuts"; Description: "Desktop and Start Menu shortcuts"; Types: full

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Components: shortcuts

[Files]
; Main executable (single file from dist)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion; Components: main

; Configuration
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion; Components: main
Source: ".env"; DestDir: "{app}"; DestName: "var_venv"; Flags: ignoreversion onlyifdoesntexist; Components: main

; Documentation (if exists)
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme; Components: docs; AfterInstall: CreateVarVenvIfNeeded

[Dirs]
Name: "{app}\sessions"; Permissions: users-modify
Name: "{app}\logs"; Permissions: users-modify
Name: "{userappdata}\{#MyAppName}"; Permissions: users-modify
Name: "{userappdata}\{#MyAppName}\sessions"; Permissions: users-modify
Name: "{userappdata}\{#MyAppName}\logs"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Comment: "Launch Voice Assistant BMO"
Name: "{group}\Configuration"; Filename: "{app}\config.json"; Comment: "Edit configuration"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; Comment: "Uninstall Voice Assistant"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon; Comment: "Launch Voice Assistant BMO"

[Registry]
; App paths
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: "Path"; ValueData: "{app}"; Flags: uninsdeletekey

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/C ""taskkill /F /IM {#MyAppExeName} /T"" "; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}\sessions"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\__pycache__"

[Code]
var
  ApiKeyPage: TInputQueryWizardPage;
  OllamaInfoPage: TOutputMsgWizardPage;

{ Check if Ollama is installed }
function IsOllamaInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/C ollama --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

procedure InitializeWizard;
var
  OllamaStatus: String;
begin
  { API Key Configuration Page }
  ApiKeyPage := CreateInputQueryPage(wpSelectDir,
    'API Configuration', 
    'Configure your Groq API Key',
    'Enter your Groq API key for speech-to-text functionality.' + #13#10 + #13#10 +
    'Get your free API key from: https://console.groq.com' + #13#10 + #13#10 +
    'You can skip this and configure it later.');
  ApiKeyPage.Add('Groq API Key:', False);
  ApiKeyPage.Values[0] := '';
  
  { Determine Ollama status }
  if IsOllamaInstalled then
    OllamaStatus := 'Installed ✓'
  else
    OllamaStatus := 'Not Detected ✗';
  
  { Ollama Information Page }
  OllamaInfoPage := CreateOutputMsgPage(wpReady,
    'Ollama Installation Required',
    'Ollama is required for AI functionality',
    'Voice Assistant requires Ollama for the LLM functionality.' + #13#10 + #13#10 +
    'Installation steps:' + #13#10 +
    '1. Download from: https://ollama.com' + #13#10 +
    '2. Install Ollama' + #13#10 +
    '3. Run: ollama pull devstral-small-2:24b-cloud' + #13#10 +
    '4. Start: ollama serve' + #13#10 + #13#10 +
    'Ollama Status: ' + OllamaStatus + #13#10 + #13#10 +
    'Click Next to continue.');
end;

procedure CreateVarVenvIfNeeded;
var
  VarVenvFile: String;
  ApiKey: String;
begin
  VarVenvFile := ExpandConstant('{app}\var_venv');
  
  { Create var_venv file if it doesn't exist }
  if not FileExists(VarVenvFile) then
  begin
    ApiKey := Trim(ApiKeyPage.Values[0]);
    
    if ApiKey <> '' then
    begin
      SaveStringToFile(VarVenvFile, 'GROQ_API_KEY=' + ApiKey + #13#10, False);
    end
    else
    begin
      SaveStringToFile(VarVenvFile, 'GROQ_API_KEY=your_groq_api_key_here' + #13#10, False);
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    { Create necessary directories }
    ForceDirectories(ExpandConstant('{app}\sessions'));
    ForceDirectories(ExpandConstant('{app}\logs'));
    ForceDirectories(ExpandConstant('{userappdata}\{#MyAppName}\sessions'));
    ForceDirectories(ExpandConstant('{userappdata}\{#MyAppName}\logs'));
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  
  { Warn if Ollama is not installed }
  if not IsOllamaInstalled then
  begin
    if MsgBox('Ollama is not detected. Voice Assistant requires Ollama for AI functionality.' + #13#10 + #13#10 +
              'Continue anyway? You can install Ollama later from: https://ollama.com',
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := 'Installation cancelled by user.';
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    { Kill any running instances }
    Exec('cmd.exe', '/C taskkill /F /IM {#MyAppExeName} /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  if CurUninstallStep = usPostUninstall then
  begin
    { Ask if user wants to keep configuration }
    if MsgBox('Do you want to keep your configuration files and session data?', mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDNO then
    begin
      DelTree(ExpandConstant('{userappdata}\{#MyAppName}'), True, True, True);
    end;
  end;
end;

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nVoice Assistant BMO is an AI-powered voice assistant featuring:%n%n• Wake word detection%n• Speech-to-text (Groq Whisper)%n• AI responses (Ollama)%n• Multiple TTS engines%n• Modern GUI interface%n• Multi-language support%n%nIt is recommended that you close all other applications before continuing.
FinishedLabel=Setup has finished installing [name].%n%nBefore running:%n1. Ensure Ollama is installed and running%n2. Configure your Groq API key if needed%n3. Run: ollama pull devstral-small-2:24b-cloud%n%nClick Finish to exit Setup.
