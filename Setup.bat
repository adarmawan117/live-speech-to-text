@echo off
setlocal enabledelayedexpansion
title Setup dan Instalasi - Live Speech to Text
color 0B

echo =======================================================
echo     SETUP DAN INSTALASI - LIVE SPEECH TO TEXT
echo                  ADR Programming
echo =======================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "ICON_FILE=%SCRIPT_DIR%assets\icon.ico"
set "TARGET_LAUNCHER=%SCRIPT_DIR%Live Speech to Text.vbs"
set "DESKTOP_LNK=%USERPROFILE%\Desktop\Live Speech to Text.lnk"
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\ADR Programming"
set "STARTMENU_LNK=%STARTMENU_DIR%\Live Speech to Text.lnk"

:: 1. Verifikasi Venv
if not exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment 'venv' belum ditemukan!
    echo Silakan jalankan instalasi dependensi terlebih dahulu.
    echo.
    pause
    exit /b 1
)

:: 2. Verifikasi Icon
if not exist "%ICON_FILE%" (
    echo [PERINGATAN] File icon.ico belum ada di folder assets.
)

echo [MEMPROSES] Membuat Shortcut di Desktop...
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP_LNK%'); $s.TargetPath = '%TARGET_LAUNCHER%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = '%ICON_FILE%'; $s.Description = 'Live Speech to Text - Voice Typing by ADR Programming'; $s.Save()"

echo [MEMPROSES] Membuat Shortcut di Start Menu...
if not exist "%STARTMENU_DIR%" mkdir "%STARTMENU_DIR%"
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTMENU_LNK%'); $s.TargetPath = '%TARGET_LAUNCHER%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = '%ICON_FILE%'; $s.Description = 'Live Speech to Text - Voice Typing by ADR Programming'; $s.Save()"

echo.
echo =======================================================
echo [BERHASIL] Instalasi Shortcut Selesai!
echo =======================================================
echo - Desktop Shortcut    : %DESKTOP_LNK%
echo - Start Menu Shortcut : %STARTMENU_LNK%
echo - Icon Aplikasi       : assets\icon.ico (Microphone Cyan)
echo.
echo Anda sekarang bisa membuka aplikasi langsung dari Desktop atau Start Menu!
echo.
pause
