@echo off
setlocal enabledelayedexpansion
title Build Installer - Live Speech to Text
color 0A

echo =======================================================
echo          BUILD INSTALLER - LIVE SPEECH TO TEXT
echo                    ADR Programming
echo =======================================================
echo.

set "ISCC_PATH="

:: Cari lokasi ISCC.exe
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    for /f "tokens=*" %%i in ('where iscc 2^>nul') do set "ISCC_PATH=%%i"
)

if not defined ISCC_PATH (
    echo [ERROR] Inno Setup Compiler (ISCC.exe) tidak ditemukan!
    echo Silakan install Inno Setup 6 terlebih dahulu.
    echo.
    pause
    exit /b 1
)

echo [INFO] Menggunakan compiler: "!ISCC_PATH!"
echo.
echo [MEMPROSES] Mengompilasi installer.iss menjadi file setup...
"!ISCC_PATH!" "installer.iss"

if errorlevel 1 (
    echo.
    echo [ERROR] Gagal mengompilasi installer!
    pause
    exit /b 1
)

echo.
echo =======================================================
echo [BERHASIL] File installer setup berhasil dibuat!
echo Lokasi output: Output\LiveSpeechToText_Setup.exe
echo =======================================================
echo.
pause

