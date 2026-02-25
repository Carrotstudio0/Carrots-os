@echo off
REM ═══════════════════════════════════════════════════════════════
REM   CarrotOS Windows Build Environment Setup
REM   إعداد بيئة بناء CarrotOS على Windows
REM ═══════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  CarrotOS Windows Build Setup                             ║
echo ║  فحص وإعداد بيئة البناء على ويندوز                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM ───────────────────────────────────────────────────────────────
REM 1. فحص Python
REM ───────────────────────────────────────────────────────────────
echo [1/4] فحص Python...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Python مثبت:
    python --version
) else (
    echo ❌ Python غير مثبت
    echo.
    echo 📥 يرجى تثبيت Python 3.11+ من:
    echo    https://www.python.org/downloads/windows/
    echo.
    echo 👉 أثناء التثبيت اختر: "Add Python to PATH"
    echo.
    pause
    goto :error
)
echo.

REM ───────────────────────────────────────────────────────────────
REM 2. فحص gcc/g++
REM ───────────────────────────────────────────────────────────────
echo [2/4] فحص gcc/g++...
gcc --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ gcc مثبت:
    gcc --version | findstr /R ".*"
) else (
    echo ❌ gcc غير مثبت
    echo.
    echo 📥 يرجى تثبيت MinGW-w64 من:
    echo    https://github.com/niXman/mingw-builds-binaries/releases
    echo.
    echo 👉 فك الضغط إلى: C:\mingw64
    echo 👉 أضف إلى PATH: C:\mingw64\bin
    echo.
    pause
    goto :error
)
echo.

REM ───────────────────────────────────────────────────────────────
REM 3. فحص make
REM ───────────────────────────────────────────────────────────────
echo [3/4] فحص GNU Make...
make --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ make مثبت:
    make --version | findstr /R ".*"
) else (
    echo ⚠️  make (mingw32-make) قد لا يكون في PATH
    echo.
    mingw32-make --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo 💡 mingw32-make متاح، سيتم إنشاء alias...
        doskey make=mingw32-make $*
        echo ✅ تم الإعداد
    ) else (
        echo ❌ GNU Make غير مثبت
        pause
        goto :error
    )
)
echo.

REM ───────────────────────────────────────────────────────────────
REM 4. تثبيت Python Dependencies
REM ───────────────────────────────────────────────────────────────
echo [4/4] تثبيت Python Dependencies...
echo.
pip install -r requirements.txt
if !errorlevel! equ 0 (
    echo ✅ تم تثبيت جميع المتطلبات بنجاح
) else (
    echo ❌ فشل تثبيت بعض المتطلبات
    pause
    goto :error
)
echo.

REM ───────────────────────────────────────────────────────────────
REM 5. التحقق النهائي
REM ───────────────────────────────────────────────────────────────
echo ╔════════════════════════════════════════════════════════════╗
echo ║           التحقق النهائي | Final Verification            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo Python:
python --version
echo.

echo gcc:
gcc --version | findstr /R ".*"
echo.

echo g++:
g++ --version | findstr /R ".*"
echo.

echo make:
make --version | findstr /R ".*"
echo.

REM ───────────────────────────────────────────────────────────────
REM 6. نصائح البناء
REM ───────────────────────────────────────────────────────────────
echo ╔════════════════════════════════════════════════════════════╗
echo ║               جاهز للبناء! Ready to Build!                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🚀 الأوامر التالية متاحة الآن:
echo.
echo   make validate      - فحص الملفات
echo   make all           - بناء كل شيء
echo   make iso           - إنشاء صورة ISO
echo   make clean         - حذف ملفات البناء
echo.
echo 📋 للمزيد من المعلومات:
echo   اقرأ: BUILD_COMPLETE_GUIDE.md
echo.
pause
goto :success

:error
echo.
echo ❌ حدث خطأ في الإعداد. يرجى التحقق من الخطوات أعلاه.
pause
exit /b 1

:success
echo.
echo ✅ تم الإعداد بنجاح!
echo.
exit /b 0
