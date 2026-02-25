# قائمة خطوات البناء على Windows
# CarrotOS Windows Setup Checklist

## ✓ الخطوة 1: تثبيت MinGW-w64 (Compiler)

### الطريقة الأولى: باستخدام Chocolatey (الأسرع ⚡)

```powershell
# 1. افتح PowerShell كـ Administrator
# 2. شغل:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 3. بعد التثبيت، شغل:
choco install mingw-w64-gcc
choco install nasm
choco install make
```

### الطريقة الثانية: التحميل اليدوي (Manual Download)

```
1. اذهب إلى: https://www.mingw-w64.org/downloads/
2. اختر: Online Installer
3. بعد التنزيل:
   - شغل المثبت
   - اختر: x86_64 (للمعالجات الحديثة)
   - اختر: GCC 13.2 أو أحدث
   - اختر: POSIX threads
   - اختر المسار: C:\mingw64
   
4. بعد الانتهاء:
   - فتح Enviroment Variables
   - أضف: C:\mingw64\bin إلى PATH
   - أعد تشغيل PowerShell
```

## ✓ الخطوة 2: التحقق من التثبيت

```powershell
# افتح PowerShell جديد وشغل:
gcc --version
nasm --version
python --version
make --version

# يجب أن تظهر جميع الإصدارات بدون أخطاء
```

## ✓ الخطوة 3: تثبيت Python والمتطلبات

```powershell
# إذا لم يكن Python مثبتاً:
choco install python

# بعد التثبيت:
pip install --upgrade pip
pip install pyyaml pillow pyinstaller

# التحقق:
python -m pip list | grep -E "yaml|pillow"
```

## ✓ الخطوة 4: تجهيز المجلد

```powershell
# انتقل إلى مجلد المشروع
cd c:\Users\Tech Shop\Desktop\sys\CarrotOS

# تحقق من البيئة
.\build.ps1 -Validate

# إذا حصلت على "Ready to build" ✓ فأنت جاهز!
```

## ✓ الخطوة 5: بناء النظام

```powershell
# خيار 1: بناء كل شيء
.\build.ps1 -BuildAll

# أو بناء أجزاء محددة:
.\build.ps1 -BuildKernel
.\build.ps1 -BuildInit
.\build.ps1 -BuildISO

# خيار 2: استخدام build.bat (أبسط)
build.bat all
build.bat kernel
build.bat iso
```

## ✓ الخطوة 6: حرق ISO على USB

```powershell
# طريقة 1: داخل السكريبت
.\build.ps1 -BurnISO -Drive "e:"

# طريقة 2: استخدام Rufus (الموصى به)
# 1. حمل: https://rufus.ie/
# 2. افتح Rufus
# 3. اختر USB Drive
# 4. اختر الملف: build-artifacts\build\carrot-os.iso
# 5. اضغط Start
```

## 📁 الملفات الناتجة

```
build-artifacts/
├── build/
│   ├── kernel.o          (Kernel object file)
│   ├── boot.o            (Boot code object file)
│   ├── carrot.bin        (Binary executable)
│   ├── init              (Init system binary)
│   ├── carrot-os.iso     (ISO image)
│   └── carrot-os.img     (Raw disk image)
```

## 🔧 حل المشاكل الشائعة

### مشكلة 1: "gcc not found"
```powershell
# تحقق من المسار
$env:PATH -split ";"

# إذا لم تظهر C:\mingw64\bin، أضفها:
$env:PATH += ";C:\mingw64\bin"

# لجعلها دائمة:
[Environment]::SetEnvironmentVariable("PATH", $env:PATH, [EnvironmentVariableTarget]::User)
```

### مشكلة 2: "Python module not found"
```powershell
# أعد تثبيت المكتبات:
pip uninstall -y yaml pillow
pip install pyyaml pillow --force-reinstall
```

### مشكلة 3: Permission denied على .ps1
```powershell
# شغل:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### مشكلة 4: Linker errors
```powershell
# تأكد من أن gcc و nasm مثبتان:
which gcc
which nasm

# قد تحتاج نسخة gcc مختلفة
# جرب: choco uninstall mingw && choco install mingw-w64-gcc --version=13.1.0
```

## 🎯 التحقق من النتيجة

```powershell
# عندما ترى:
# [HH:MM:SS SUCCESS] Kernel built successfully: carrot.bin (XXX KB)
# [HH:MM:SS SUCCESS] ISO created: 700.00 MB (341504 sectors)

# فأنت نجحت! ✅
```

## 🐛 الدعم والتصحيح

إذا واجهت مشكلة:

1. تأكد من تشغيل PowerShell كـ Administrator
2. استخدم: `.\build.ps1 -Validate` للتشخيص الكامل
3. تحقق من المسافات والأحرف الخاصة في المسار
4. استخدم مسار مختصر: `c:\carrotos` لتجنب المسافات

## 📌 الملاحظات المهمة

- ✅ هذا النظام يعمل **بدون WSL** و **بدون Docker**
- ✅ يعمل على Windows 10/11 x86_64
- ✅ كل الأدوات مجانية ومفتوحة المصدر
- ⚠️ الوقت الأول قد يستغرق 10-15 دقيقة للتثبيت
- ⚠️ الحد الأدنى للـ RAM: 4 GB
- ⚠️ تأكد من امتلاكك صلاحيات Administrator
