@echo off
chcp 65001 >nul
rem Warma Encyclopedia auto-updater (ASCII-only batch launcher)
cd /d "%~dp0"
set PY=C:\Users\Aigooz\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
if not exist "%PY%" set PY=python
echo ============================================
echo   Warma Encyclopedia Updater
echo   [1] Full auto update (needs Cookie in config.ini)
echo   [2] Ingest subtitles from inbox folder (SubBatch)
echo   [3] Show current status
echo ============================================
set /p choice=Select (1/2/3):
if "%choice%"=="1" "%PY%" tools\update.py run
if "%choice%"=="2" "%PY%" tools\update.py ingest
if "%choice%"=="3" "%PY%" tools\update.py status
echo.
pause