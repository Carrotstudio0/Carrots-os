@echo off
REM نظام CarrotOS Bare Metal - برنامج حرق على USB
REM استخدم Rufus أو Etcher لضمان النتائج المثلى

echo ================================
echo CarrotOS 1.0 - USB Flash Burner
echo ================================
echo.

echo المتطلبات:
echo - Rufus (https://rufus.ie/)
echo - أو Balena Etcher (https://www.balena.io/etcher/)
echo.

echo ملف ISO:
echo %CD%\carrotos-1.0-bare-metal.iso
echo.

echo الخطوات:
echo 1. احفظ الملف ISO أعلاه
echo 2. شغل Rufus
echo 3. اختر الملف ISO
echo 4. اختر فلاشة USB
echo 5. اضغط START
echo.

echo تحذير: سيتم حذف محتويات الفلاشة!
echo.

pause
