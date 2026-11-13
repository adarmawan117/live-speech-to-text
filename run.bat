@echo off
setlocal
title Live Speech to Text - ADR Programming
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment 'venv' tidak ditemukan!
    echo Silakan jalankan instalasi terlebih dahulu.
    echo.
    pause
    exit /b 1
)

"venv\Scripts\python.exe" main.py
if errorlevel 1 (
    echo.
    echo [ERROR] Aplikasi terhenti karena terjadi kesalahan.
    pause
)
