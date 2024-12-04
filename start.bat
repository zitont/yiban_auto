@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: 设置标题和颜色代码
title 易班自动化工具
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "RESET=[0m"

:: 获取当前目录
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

:: 激活虚拟环境
echo %GREEN%[启动] 激活虚拟环境...%RESET%
if exist "%PROJECT_DIR%\venv\Scripts\activate" (
    call "%PROJECT_DIR%\venv\Scripts\activate"
) else (
    echo %RED%[错误] 未找到虚拟环境，请先运行 setup.bat%RESET%
    timeout /t 3 > nul
    exit /b 1
)

if %errorlevel% neq 0 (
    echo %RED%[错误] 虚拟环境激活失败%RESET%
    timeout /t 3 > nul
    exit /b 1
)

:: 切换到项目目录
cd /d "%PROJECT_DIR%"

:: 运行程序
echo %GREEN%[启动] 运行程序...%RESET%
python run.py
if %errorlevel% neq 0 (
    echo %RED%[错误] 程序异常退出%RESET%
    timeout /t 3 > nul
    exit /b 1
)

:: 程序正常结束，等待3秒后自动关闭
echo %GREEN%[完成] 程序执行完毕，3秒后自动关闭...%RESET%
timeout /t 3 > nul
exit /b 0