@echo off
chcp 65001 >nul
title Warma 表格一键更新
cd /d "%~dp0"

echo ============================================
echo   Warma 表格一键更新
echo ============================================
echo.

set "PY=C:\Users\Aigooz\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%PY%" (
    echo [错误] 未找到 Python 运行时，请手动检查路径。
    pause
    exit /b 1
)

echo 正在同步 registry.json 与 B 站元数据...
"%PY%" tools\update_warma_xlsx.py
if errorlevel 1 (
    echo.
    echo [失败] 更新过程中出现错误，请查看上方日志。
    pause
    exit /b 1
)

echo.
echo [完成] 两个表格已更新到最新数据。
echo       备份保存在 F:\warma百科\backup_xlsx\
echo.
echo [GitHub sync] Pushing changes...
git add -A 2>nul
git diff --cached --quiet 2>nul || (
    for /f "tokens=2 delims==" %%%%I in ('wmic os get localdatetime /value 2^^^>nul') do set dt=%%%%I
    git commit -m "Auto sync tables %%dt:~0,4%%-%%dt:~4,2%%-%%dt:~6,2%%" --quiet 2>nul
    git push origin master --quiet 2>nul
    if not errorlevel 1 (
        echo GitHub synced.
    ) else (
        echo GitHub push failed (offline?^).
    )
)
echo.
pause
