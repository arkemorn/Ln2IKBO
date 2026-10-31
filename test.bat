@echo off
setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
python -m unittest discover -s tests -v
set "APP_EXIT_CODE=%ERRORLEVEL%"
if not "%APP_EXIT_CODE%"=="0" echo Test run failed. Exit code: %APP_EXIT_CODE%
echo.
pause
exit /b %APP_EXIT_CODE%
