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

:: 1. Cari lokasi ISCC.exe standar
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"
) else (
    for /f "tokens=*" %%i in ('where iscc 2^>nul') do set "ISCC_PATH=%%i"
)

:: 2. Fallback ke compiler bawaan Antigravity IDE jika instalasi standar tidak ditemukan
if not defined ISCC_PATH (
    if exist "%LocalAppData%\Programs\Antigravity IDE\resources\app\node_modules\innosetup\bin\ISCC.exe" (
        set "ISCC_PATH=%LocalAppData%\Programs\Antigravity IDE\resources\app\node_modules\innosetup\bin\ISCC.exe"
    )
)

if not defined ISCC_PATH (
    echo [ERROR] Inno Setup Compiler [ISCC.exe] tidak ditemukan!
    echo Silakan unduh dan install Inno Setup 6 dari: https://jrsoftware.org/isdl.php
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
