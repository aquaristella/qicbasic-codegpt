@echo off
title QiBasic CodeGPT - Chat
color 0B

echo.
echo  =====================================================
echo   QiBasic CodeGPT - Terminal Chat
echo  =====================================================
echo.
echo  Type your question and press ENTER.
echo  Type /bye to exit.
echo.
echo  Example questions:
echo    - Write a Hello World program
echo    - Write a FOR loop from 1 to 10
echo    - Explain what DIM means
echo    - Fix this code: FOR i 1 TO 10 PRINT i
echo.
echo  ─────────────────────────────────────────────────────
echo.

REM Start Ollama if not running
start "" /B ollama serve >nul 2>&1
timeout /t 2 /nobreak >nul

ollama run qibasic-codegpt

echo.
echo  Chat ended. Press any key to close.
pause >nul
