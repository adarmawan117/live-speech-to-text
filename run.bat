@echo off
setlocal enabledelayedexpansion
title Live Speech to Text - ADR Programming
cd /d "%~dp0"

echo ======================================================
echo          Live Speech to Text - ADR Programming
echo ======================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment 'venv' tidak ditemukan!
    echo Silakan jalankan instalasi terlebih dahulu.
    echo.
    pause
    exit /b 1
)

"venv\Scripts\python.exe" main.py

echo.
echo ======================================================
echo Aplikasi telah berhenti.
echo ======================================================
pause
