@echo off
REM ═════════════════════════════════════════════════════════════════
REM  Simplified Build Script (Without Python dependency)
REM  بناء مبسط بدون الاعتماد على Python
REM ═════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   CarrotOS Build (C/C++ Components Only)                  ║
echo ║   بناء CarrotOS (مكونات C/C++ فقط)                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Set MinGW Path
set MINGW_PATH=C:\MinGW
set PATH=%MINGW_PATH%\bin;%PATH%

REM ─────────────────────────────────────────────────────────────
REM 1. Check Tools
REM ─────────────────────────────────────────────────────────────
echo [1/5] Checking build tools...
echo.

gcc --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] gcc found
    gcc --version | findstr /R ".*" | findstr /v "^$"
) else (
    echo [ERROR] gcc not found in PATH
    echo Please ensure MinGW is extracted to: %MINGW_PATH%
    pause
    exit /b 1
)
echo.

g++ --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] g++ found
) else (
    echo [ERROR] g++ not found
    pause
    exit /b 1
)
echo.

mingw32-make --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] mingw32-make found
) else (
    echo [ERROR] mingw32-make not found
    pause
    exit /b 1
)
echo.

REM ─────────────────────────────────────────────────────────────
REM 2. Check Project Files
REM ─────────────────────────────────────────────────────────────
echo [2/5] Checking project files...
echo.

if exist boot\bootloader.c (
    echo [OK] boot\bootloader.c
) else (
    echo [ERROR] boot\bootloader.c not found
    exit /b 1
)

if exist kernel\kernel.c (
    echo [OK] kernel\kernel.c
) else (
    echo [ERROR] kernel\kernel.c not found
    exit /b 1
)

if exist core\init\src\init.c (
    echo [OK] core\init\src\init.c
) else (
    echo [ERROR] core\init\src\init.c not found
    exit /b 1
)

if exist desktop\shell\src\shell.cpp (
    echo [OK] desktop\shell\src\shell.cpp
) else (
    echo [ERROR] desktop\shell\src\shell.cpp not found
    exit /b 1
)

if exist Makefile (
    echo [OK] Makefile
) else (
    echo [ERROR] Makefile not found
    exit /b 1
)

echo.

REM ─────────────────────────────────────────────────────────────
REM 3. Compile C Components
REM ─────────────────────────────────────────────────────────────
echo [3/5] Compiling C Components...
echo.

set BUILD_DIR=build\output
if not exist %BUILD_DIR% mkdir %BUILD_DIR%

echo Compiling bootloader...
gcc -c boot\bootloader.c -o %BUILD_DIR%\bootloader.o -Wall -Wextra
if !errorlevel! neq 0 (
    echo [ERROR] Failed to compile bootloader
    pause
    exit /b 1
)

echo Compiling kernel...
gcc -c kernel\kernel.c -o %BUILD_DIR%\kernel.o -Wall -Wextra -O2
if !errorlevel! neq 0 (
    echo [ERROR] Failed to compile kernel
    pause
    exit /b 1
)

echo Compiling init...
gcc -c core\init\src\init.c -o %BUILD_DIR%\init.o -Wall -Wextra
if !errorlevel! neq 0 (
    echo [ERROR] Failed to compile init
    pause
    exit /b 1
)

echo Linking C components...
ld -Ttext 0x1000 %BUILD_DIR%\bootloader.o -o %BUILD_DIR%\carrot-bootloader 2>nul || (
    echo [WARNING] Linking with ld failed, using gcc...
    gcc -nostartfiles %BUILD_DIR%\bootloader.o -o %BUILD_DIR%\carrot-bootloader
)

echo.

REM ─────────────────────────────────────────────────────────────
REM 4. Compile C++ Components
REM ─────────────────────────────────────────────────────────────
echo [4/5] Compiling C++ Components...
echo.

echo Compiling desktop shell...
g++ -c desktop\shell\src\shell.cpp -o %BUILD_DIR%\shell.o -std=c++17 -Wall -Wextra
if !errorlevel! neq 0 (
    echo [WARNING] Failed to compile shell (may need dependencies)
) else (
    echo [OK] Shell compiled successfully
)

echo.

REM ─────────────────────────────────────────────────────────────
REM 5. Summary
REM ─────────────────────────────────────────────────────────────
echo [5/5] Build Summary
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║              Build Completed Successfully!                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo Output files created in: %BUILD_DIR%\
echo.

dir %BUILD_DIR%\*.o %BUILD_DIR%\carrot-* 2>nul | find /C /V "" >nul
if !errorlevel! equ 0 (
    echo Compiled files:
    dir %BUILD_DIR%\*.o %BUILD_DIR%\carrot-* /B 2>nul
)

echo.
echo ✅ C/C++ compilation completed!
echo.
echo NOTE: Python is needed for full build including ISO creation
echo Install Python and run: .\BUILD.ps1
echo.
pause
