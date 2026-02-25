# CarrotOS Windows Build Setup

## المتطلبات (Requirements)

### 1. MinGW-w64 (Compiler)
- **الحجم**: ~500 MB
- **الرابط**: https://www.mingw-w64.org/downloads/
- **الإصدار الموصى به**: GCC 13.2 x86_64

**خطوات التثبيت على Windows:**

```powershell
# استخدام Chocolatey (الطريقة الأسرع)
choco install mingw --version=13.2.0

# أو تحميل يدوي:
# 1. اذهب إلى https://sourceforge.net/projects/mingw-w64/files/
# 2. حمل آخر إصدار x86_64
# 3. قم بالتثبيت في: C:\mingw64
# 4. أضف C:\mingw64\bin إلى system PATH
```

### 2. Nasm (Assembler)
```powershell
choco install nasm
```

### 3. Python 3.11+
```powershell
choco install python
# أو عبر: https://www.python.org/downloads/
```

### 4. Build Tools
```powershell
# في PowerShell (كـ Admin):
pip install pyinstaller pyyaml pillow
```

## التحقق من البيئة

```powershell
# تحقق من التثبيت:
gcc --version
nasm --version
python --version

# يجب أن تظهر الإصدارات بدون أخطاء
```

## بناء النظام

```powershell
# من داخل مجلد CarrotOS:
cd c:\Users\Tech Shop\Desktop\sys\CarrotOS

# تحقق من البيئة:
.\build.ps1 -Validate

# بناء كامل:
.\build.ps1 -BuildAll

# بناء مكون معين:
.\build.ps1 -BuildKernel
.\build.ps1 -BuildInit
.\build.ps1 -BuildISO

# حرق على USB:
.\build.ps1 -BurnISO -Drive "e:"
```

## الملفات الناتجة

- `build-artifacts/kernel/carrot.bin` - Kernel الثنائي
- `build-artifacts/iso/carrot-os.iso` - صورة ISO الكاملة
- `build-artifacts/build/carrot.img` - صورة Disk

## استكشاف الأخطاء

### Error: "gcc not found"
```powershell
$env:PATH += ";C:\mingw64\bin"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH, [EnvironmentVariableTarget]::User)

# ثم أعد تشغيل PowerShell
```

### Error: "Python module not found"
```powershell
pip install --upgrade pyinstaller pyyaml pillow
```

### خطأ في حرق ISO
- استخدم Rufus من خارج السكريبت
- الرابط: https://rufus.ie/
