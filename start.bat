@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Maesi App Backend Platform 涓€閿惎鍔?

:: 1. 娓呯悊娈嬬暀 8000 绔彛
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

:: 2. 鍚姩 FastAPI 鍚庣
start "FastAPI-Backend" cmd /k "python -m uvicorn rag_service:app --reload --port 8000"

:: 3. 杞鑷绔彛
set IS_READY=0
for /l %%i in (1,1,10) do (
    if !IS_READY! equ 0 (
        netstat -aon | findstr :8000 | findstr LISTENING >nul 2>&1
        if !errorlevel! equ 0 (
            set IS_READY=1
        ) else (
            timeout /t 1 /nobreak >nul
        )
    )
)

:: 4. 鎴愬姛鎷夎捣骞堕潤榛橀€€鍑哄綋鍓嶈剼鏈?
if !IS_READY! equ 1 (
    start "" "%~dp0index.html"
    exit
) else (
    echo [ERROR] 鍚庣鍚姩澶辫触锛岃妫€鏌?FastAPI 绐楀彛锛?
    pause
)
