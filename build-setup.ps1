# ═══════════════════════════════════════════════════════════════════════
# CarrotOS Windows Build Setup (PowerShell)
# إعداد بيئة بناء CarrotOS على Windows
# ═══════════════════════════════════════════════════════════════════════

param(
    [switch]$AutoFix = $false,
    [switch]$Verbose = $false
)

# ───────────────────────────────────────────────────────────────────────
# الألوان
# ───────────────────────────────────────────────────────────────────────
$colors = @{
    Green = [System.ConsoleColor]::Green
    Red = [System.ConsoleColor]::Red
    Yellow = [System.ConsoleColor]::Yellow
    Cyan = [System.ConsoleColor]::Cyan
}

function Write-Result {
    param(
        [string]$Message,
        [string]$Status = "INFO"
    )
    
    $color = $colors.Cyan
    $symbol = "ℹ️ "
    
    switch ($Status) {
        "SUCCESS" { $color = $colors.Green; $symbol = "✅ " }
        "ERROR" { $color = $colors.Red; $symbol = "❌ " }
        "WARNING" { $color = $colors.Yellow; $symbol = "⚠️  " }
    }
    
    Write-Host "$symbol$Message" -ForegroundColor $color
}

# ───────────────────────────────────────────────────────────────────────
# البداية
# ───────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  CarrotOS Windows Build Environment Setup                ║" -ForegroundColor Cyan
Write-Host "║  إعداد بيئة بناء CarrotOS على Windows                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ───────────────────────────────────────────────────────────────────────
# 1. فحص Python
# ───────────────────────────────────────────────────────────────────────
Write-Host "[1/5] فحص Python..." -ForegroundColor Cyan
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if ($pythonPath) {
    $version = & python --version 2>&1
    Write-Result "Python مثبت: $version" "SUCCESS"
} else {
    Write-Result "Python غير مثبت" "ERROR"
    Write-Host ""
    Write-Host "📥 يرجى تثبيت Python 3.11+ من:" -ForegroundColor Yellow
    Write-Host "   https://www.python.org/downloads/windows/" -ForegroundColor White
    Write-Host ""
    Write-Host "👉 أثناء التثبيت اختر: 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
Write-Host ""

# ───────────────────────────────────────────────────────────────────────
# 2. فحص gcc/g++
# ───────────────────────────────────────────────────────────────────────
Write-Host "[2/5] فحص gcc/g++..." -ForegroundColor Cyan
$gccPath = Get-Command gcc -ErrorAction SilentlyContinue
if ($gccPath) {
    $version = & gcc --version 2>&1 | Select-Object -First 1
    Write-Result "gcc مثبت: $version" "SUCCESS"
} else {
    Write-Result "gcc غير مثبت" "ERROR"
    Write-Host ""
    Write-Host "📥 يرجى تثبيت MinGW-w64 من:" -ForegroundColor Yellow
    Write-Host "   https://github.com/niXman/mingw-builds-binaries/releases" -ForegroundColor White
    Write-Host ""
    Write-Host "👉 فك الضغط إلى: C:\mingw64" -ForegroundColor Yellow
    Write-Host "👉 أضف إلى PATH: C:\mingw64\bin" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
Write-Host ""

# ───────────────────────────────────────────────────────────────────────
# 3. فحص make
# ───────────────────────────────────────────────────────────────────────
Write-Host "[3/5] فحص GNU Make..." -ForegroundColor Cyan
$makePath = Get-Command make -ErrorAction SilentlyContinue
if ($makePath) {
    $version = & make --version 2>&1 | Select-Object -First 1
    Write-Result "make مثبت: $version" "SUCCESS"
} else {
    Write-Result "make في PATH غير متاح، البحث عن mingw32-make..." "WARNING"
    $mingwMake = Get-Command mingw32-make -ErrorAction SilentlyContinue
    if ($mingwMake) {
        Write-Result "mingw32-make متاح" "SUCCESS"
        Write-Host "💡 سيتم استخدام mingw32-make بدلاً من make" -ForegroundColor Yellow
    } else {
        Write-Result "GNU Make غير مثبت" "ERROR"
        exit 1
    }
}
Write-Host ""

# ───────────────────────────────────────────────────────────────────────
# 4. فحص متطلبات الملفات
# ───────────────────────────────────────────────────────────────────────
Write-Host "[4/5] فحص ملفات المشروع..." -ForegroundColor Cyan
$requiredFiles = @(
    "Makefile",
    "requirements.txt",
    "boot\bootloader.c",
    "kernel\kernel.c",
    "core\init\src\init.c",
    "desktop\shell\src\shell.cpp"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Result "موجود: $file" "SUCCESS"
    } else {
        Write-Result "مفقود: $file" "ERROR"
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Result "بعض الملفات مفقودة!" "ERROR"
    exit 1
}
Write-Host ""

# ───────────────────────────────────────────────────────────────────────
# 5. تثبيت Python Dependencies
# ───────────────────────────────────────────────────────────────────────
Write-Host "[5/5] تثبيت Python Dependencies..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "requirements.txt") {
    Write-Result "تثبيت المتطلبات من requirements.txt..." "INFO"
    & pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Result "تم تثبيت جميع المتطلبات بنجاح" "SUCCESS"
    } else {
        Write-Result "فشل تثبيت بعض المتطلبات" "WARNING"
    }
} else {
    Write-Result "ملف requirements.txt غير موجود" "WARNING"
}
Write-Host ""

# ───────────────────────────────────────────────────────────────────────
# الملخص النهائي
# ───────────────────────────────────────────────────────────────────────
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           ملخص الإعداد | Setup Summary                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 المعلومات المثبتة:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Python: " -NoNewline; & python --version
Write-Host "gcc: " -NoNewline; & gcc --version | Select-Object -First 1
Write-Host "make: " -NoNewline; if ($makePath) { & make --version | Select-Object -First 1 } else { Write-Host "mingw32-make (available)" }
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        جاهز للبناء! Ready to Build CarrotOS!             ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 أوامر البناء المتاحة:" -ForegroundColor Green
Write-Host ""
Write-Host "  make validate      - فحص الملفات" -ForegroundColor White
Write-Host "  make all           - بناء كل شيء" -ForegroundColor White
Write-Host "  make iso           - إنشاء صورة ISO" -ForegroundColor White
Write-Host "  make clean         - حذف ملفات البناء" -ForegroundColor White
Write-Host ""

Write-Host "📋 للمزيد:" -ForegroundColor Green
Write-Host "  اقرأ: BUILD_COMPLETE_GUIDE.md" -ForegroundColor White
Write-Host ""

Write-Result "✅ تم الإعداد بنجاح! البيئة جاهزة للبناء." "SUCCESS"
Write-Host ""
