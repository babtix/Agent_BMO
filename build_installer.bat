@echo off
REM Voice Assistant BMO - Build Installer
REM Quick build script for Inno Setup

echo ========================================
echo Voice Assistant BMO - Build Installer
echo ========================================
echo.

REM Check if executable exists
if not exist "dist\BMO_v4.exe" (
    echo [ERROR] BMO_v4.exe not found in dist folder
    echo Please build the executable first:
    echo   python -m PyInstaller BMO_v4.spec
    pause
    exit /b 1
)

echo [OK] Executable found: dist\BMO_v4.exe
echo.

REM Check if Inno Setup is installed
set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if not exist "%INNO_PATH%" (
    echo [ERROR] Inno Setup not found at: %INNO_PATH%
    echo.
    echo Please install Inno Setup 6 from:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo [OK] Inno Setup found
echo.

REM Create output directory
if not exist "..\installer_output" mkdir "..\installer_output"

echo Building installer...
echo ========================================
"%INNO_PATH%" "BMO_installer.iss"

if errorlevel 1 (
    echo.
    echo [ERROR] Installer build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Installer built successfully!
echo ========================================
echo.
echo Output location: ..\installer_output\
dir ..\installer_output\*.exe
echo.
echo You can now distribute the installer!
echo.
pause
