# CarrotOS Bare Metal - USB Burning Script
# استخدام متقدم

param(
    [string]$ISOPath = "carrotos-1.0-bare-metal.iso",
    [string]$DriveLetter = ""
)

Write-Host "╔═══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  CarrotOS 1.0 - Bare Metal USB Burner    ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $ISOPath)) {
    Write-Host "❌ ملف ISO غير موجود: $ISOPath" -ForegroundColor Red
    exit 1
}

Write-Host "✓ ملف ISO موجود: $ISOPath"
Write-Host ""

# إذا لم يتم تحديد درايف
if (-not $DriveLetter) {
    Write-Host "🔍 الأقراص المتاحة:" -ForegroundColor Yellow
    Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Root -match '^[A-Z]:\\'} | ForEach-Object {
        $letter = $_.Name
        Write-Host "  • $letter"
    }
    Write-Host ""
    $DriveLetter = Read-Host "اختر حرف الفلاشة (مثل D, E)"
}

$FlashPath = "$DriveLetter`:\"

if (-not (Test-Path $FlashPath)) {
    Write-Host "❌ محرك الأقراص غير موجود: $FlashPath" -ForegroundColor Red
    exit 1
}

Write-Host "⚠️  تحذير: سيتم حذف جميع البيانات على $DriveLetter!" -ForegroundColor Yellow
$confirm = Read-Host "هل أنت متأكد؟ (نعم/لا)"

if ($confirm -ne "نعم" -and $confirm -ne "yes") {
    Write-Host "تم الإلغاء"
    exit 0
}

Write-Host ""
Write-Host "💾 جاري الحرق..." -ForegroundColor Cyan
Write-Host "ملاحظة: استخدم Rufus أو Etcher للحرق الآمن" -ForegroundColor Yellow
Write-Host ""
Write-Host "الأمر المقترح (استخدم كـ Admin):" -ForegroundColor Green
Write-Host "dd if=$ISOPath of=\\.\\$DriveLetter bs=4MB --progress"
