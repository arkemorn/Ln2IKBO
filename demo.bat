@echo off
setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
python -m scripts.demo
set "APP_EXIT_CODE=%ERRORLEVEL%"
if not "%APP_EXIT_CODE%"=="0" echo Demo failed. Exit code: %APP_EXIT_CODE%
echo.
pause
exit /b %APP_EXIT_CODE%
