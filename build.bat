@echo off
REM CarrotOS Windows Build System - Simple Batch Wrapper
REM Usage: build.bat [option]

setlocal enabledelayedexpansion

if "%1"=="" (
    echo CarrotOS Windows Build System
    echo.
    echo Usage: build.bat [option]
    echo Options:
    echo   validate     - Check environment setup
    echo   kernel       - Build kernel only
    echo   init         - Build init system only
    echo   python       - Validate Python apps
    echo   iso          - Create ISO image
    echo   all          - Build everything
    echo   clean        - Remove build artifacts
    echo   burn         - Burn ISO to USB (interactive^)
    echo.
    exit /b 0
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "& '.\build.ps1' -%1"
exit /b %ERRORLEVEL%
