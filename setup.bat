@echo off
setlocal enabledelayedexpansion
title QiBasic CodeGPT - Setup
color 0A

echo.
echo  =====================================================
echo   QiBasic CodeGPT - Windows Setup
echo   Powered by Ollama + DeepSeek-Coder
echo  =====================================================
echo.
echo  This will set up your local QiBasic AI assistant.
echo  Please wait and do NOT close this window.
echo.
pause

REM ── STEP 1: Check Ollama ───────────────────────────────────────────────────
echo.
echo  [STEP 1 of 3]  Checking Ollama...
echo  ─────────────────────────────────────────────────────

where ollama >nul 2>&1
IF ERRORLEVEL 1 (
    echo.
    echo  ERROR: Ollama is not installed or not found.
    echo.
    echo  Please install Ollama first:
    echo  1. Open your browser
    echo  2. Go to: https://ollama.com/download
    echo  3. Download and install for Windows
    echo  4. Run this setup again
    echo.
    pause
    exit /b 1
)

echo  Ollama is installed. Good!
echo.

REM Start Ollama service (safe to run even if already running)
echo  Starting Ollama service...
start "" /B ollama serve >nul 2>&1
timeout /t 3 /nobreak >nul
echo  Ollama service is ready.

REM ── STEP 2: Pull DeepSeek-Coder ────────────────────────────────────────────
echo.
echo  [STEP 2 of 3]  Setting up DeepSeek-Coder model...
echo  ─────────────────────────────────────────────────────

ollama list 2>nul | findstr /i "deepseek-coder" >nul 2>&1
IF ERRORLEVEL 1 (
    echo  DeepSeek-Coder not found. Downloading now...
    echo  This may take 5-15 minutes depending on your internet speed.
    echo  Model size: ~776MB  Please wait...
    echo.
    ollama pull deepseek-coder
    IF ERRORLEVEL 1 (
        echo.
        echo  ERROR: Failed to download DeepSeek-Coder.
        echo  Check your internet connection and try again.
        pause
        exit /b 1
    )
    echo.
    echo  DeepSeek-Coder downloaded successfully!
) ELSE (
    echo  DeepSeek-Coder already installed. Skipping download.
)

REM ── STEP 3: Create QiBasic CodeGPT ─────────────────────────────────────────
echo.
echo  [STEP 3 of 3]  Creating qibasic-codegpt model...
echo  ─────────────────────────────────────────────────────

IF NOT EXIST "Modelfile" (
    echo.
    echo  ERROR: Modelfile not found!
    echo  Make sure you are running this from inside the
    echo  qibasic-codegpt folder (where Modelfile exists).
    echo.
    pause
    exit /b 1
)

ollama create qibasic-codegpt -f Modelfile
IF ERRORLEVEL 1 (
    echo.
    echo  ERROR: Failed to create the model.
    echo  Make sure Ollama is running and try again.
    pause
    exit /b 1
)

echo.
echo  qibasic-codegpt model created!

REM ── Quick Test ─────────────────────────────────────────────────────────────
echo.
echo  ─────────────────────────────────────────────────────
echo  Running a quick test (Write Hello World)...
echo  ─────────────────────────────────────────────────────
echo.
ollama run qibasic-codegpt "Write a Hello World program in QBasic. Keep it short and simple."

REM ── Done ───────────────────────────────────────────────────────────────────
echo.
echo.
echo  =====================================================
echo   Setup Complete! QiBasic CodeGPT is ready!
echo  =====================================================
echo.
echo  HOW TO USE:
echo.
echo  Option 1 - Terminal Chat:
echo    Run:  start_chat.bat
echo.
echo  Option 2 - Web Browser Chat:
echo    Double-click:  chat.html
echo.
echo  Option 3 - Command (anytime):
echo    Open CMD and run: ollama run qibasic-codegpt
echo.
echo  =====================================================
echo.
pause
