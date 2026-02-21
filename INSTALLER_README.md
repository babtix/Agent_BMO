# BMO Installer - Quick Guide

## 🚀 Build Installer (3 Steps)

### Step 1: Build Executable
```cmd
python -m PyInstaller BMO_v4.spec
```

### Step 2: Run Build Script
```cmd
build_installer.bat
```

### Step 3: Find Installer
```
..\installer_output\VoiceAssistant_BMO_Setup_v4.0.0_x64.exe
```

## 📋 Prerequisites

1. **Inno Setup 6**
   - Download: https://jrsoftware.org/isdl.php
   - Install to default location

2. **Built Executable**
   - Must have `dist\BMO_v4.exe`
   - Build with PyInstaller first

## 🎯 Files

- **BMO_installer.iss** - Installer script (ready to use)
- **build_installer.bat** - Build automation
- **ico.ico** - Application icon
- **config.json** - Configuration file
- **.env** - Environment variables template

## ⚙️ What Gets Installed

```
C:\Program Files\Voice Assistant BMO\
├── BMO_v4.exe          # Main application
├── config.json         # Configuration
├── var_venv            # API keys
├── sessions\           # User sessions
└── logs\               # Log files
```

## 🎨 Installer Features

- ✅ API key configuration wizard
- ✅ Ollama installation check
- ✅ Desktop shortcut (optional)
- ✅ Start menu shortcuts
- ✅ Uninstaller
- ✅ Multi-language support (4 languages)
- ✅ Keep settings on uninstall option

## 🔧 Customization

Edit `BMO_installer.iss` to change:

```pascal
#define MyAppName "Voice Assistant BMO"
#define MyAppVersion "4.0.0"
#define MyAppPublisher "BABTIX"
#define MyAppURL "https://github.com/babtix/Agent_BMO"
```

## 🐛 Troubleshooting

### "Executable not found"
```cmd
python -m PyInstaller BMO_v4.spec
```

### "Inno Setup not found"
Install from: https://jrsoftware.org/isdl.php

### "Build failed"
- Check paths in BMO_installer.iss
- Verify all files exist
- Check Inno Setup error messages

## 📦 Manual Build

If build script doesn't work:

1. Open Inno Setup
2. File → Open → BMO_installer.iss
3. Build → Compile
4. Find installer in ..\installer_output\

## ✅ Test Installer

1. Run installer on clean Windows
2. Enter API key (or skip)
3. Complete installation
4. Launch application
5. Verify it works
6. Test uninstaller

## 🎉 Distribution

Once built, share:
```
VoiceAssistant_BMO_Setup_v4.0.0_x64.exe
```

Users just run the installer - no Python or dependencies needed!

---

**Need help?** Check the error messages or open an issue on GitHub.
