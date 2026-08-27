@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title 迈思 AI 系统一键启动

:: 1. 清理残留 8000 端口
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

:: 2. 启动 FastAPI 后端
start "FastAPI-Backend" cmd /k "python -m uvicorn rag_service:app --reload --port 8000"

:: 3. 轮询自检端口
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

:: 4. 成功拉起并静默退出当前脚本
if !IS_READY! equ 1 (
    start "" "%~dp0index.html"
    exit
) else (
    echo [ERROR] 后端启动失败，请检查 FastAPI 窗口！
    pause
)