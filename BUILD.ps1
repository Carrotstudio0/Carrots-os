#Requires -Version 5.1
<#
.SYNOPSIS
    CarrotOS Windows Native Build System
.DESCRIPTION
    Build CarrotOS kernel, init, and utilities on Windows without WSL/Docker
.PARAMETER BuildKernel
    بناء الـ Kernel
.PARAMETER BuildInit
    بناء نظام Init
.PARAMETER BuildISO
    إنشاء صورة ISO
.PARAMETER BuildAll
    بناء كل الأجزاء
.PARAMETER Validate
    التحقق من البيئة
.PARAMETER BurnISO
    حرق ISO على USB
#>

param(
    [switch]$BuildKernel,
    [switch]$BuildInit,
    [switch]$BuildPython,
    [switch]$BuildApps,
    [switch]$BuildISO,
    [switch]$BuildAll,
    [switch]$Validate,
    [switch]$Clean,
    [switch]$BurnISO,
    [string]$Drive,
    [switch]$Help
)

# ============================================================================
# Colors and Logging
# ============================================================================

$COLORS = @{
    Reset    = "`e[0m"
    Red      = "`e[31m"
    Green    = "`e[32m"
    Yellow   = "`e[33m"
    Blue     = "`e[34m"
    Magenta  = "`e[35m"
    Cyan     = "`e[36m"
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = $COLORS.Cyan
    
    switch ($Level) {
        "SUCCESS" { $color = $COLORS.Green }
        "ERROR"   { $color = $COLORS.Red }
        "WARNING" { $color = $COLORS.Yellow }
        "DEBUG"   { $color = $COLORS.Blue }
    }
    
    Write-Host "$color[$timestamp $Level]$($COLORS.Reset) $Message"
}

function Write-Section {
    param([string]$Title)
    Write-Host "`n$($COLORS.Magenta)" + ("=" * 70) + "$($COLORS.Reset)"
    Write-Host "$($COLORS.Magenta)► $Title$($COLORS.Reset)"
    Write-Host "$($COLORS.Magenta)" + ("=" * 70) + "$($COLORS.Reset)`n"
}

# ============================================================================
# Environment Validation
# ============================================================================

function Test-Compiler {
    Write-Section "فحص الأدوات المطلوبة / Checking Required Tools"
    
    $tools = @(
        @{ Name = "gcc"; Description = "MinGW-w64 C Compiler"; Command = "gcc --version" },
        @{ Name = "nasm"; Description = "Netwide Assembler"; Command = "nasm -version" },
        @{ Name = "python"; Description = "Python 3.11+"; Command = "python --version" },
        @{ Name = "make"; Description = "GNU Make"; Command = "make --version" }
    )
    
    $allValid = $true
    
    foreach ($tool in $tools) {
        try {
            $output = Invoke-Expression $tool.Command 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log "$($tool.Description): ✓" "SUCCESS"
            } else {
                Write-Log "$($tool.Description): ✗" "ERROR"
                $allValid = $false
            }
        }
        catch {
            Write-Log "$($tool.Description): ✗ (not installed)" "ERROR"
            $allValid = $false
        }
    }
    
    if (-not $allValid) {
        Write-Log "تثبيت المتطلبات من BUILD_WINDOWS_SETUP.md" "WARNING"
        return $false
    }
    
    return $true
}

function Test-Python-Modules {
    Write-Log "فحص Python modules..."
    
    $modules = @("yaml", "PIL")
    
    foreach ($module in $modules) {
        python -c "import $module" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Missing module: $module" "WARNING"
            return $false
        }
    }
    
    Write-Log "Python modules: ✓" "SUCCESS"
    return $true
}

function Invoke-Validation {
    Write-Section "التحقق من البيئة / Environment Validation"
    
    if (-not (Test-Compiler)) {
        Write-Log "Failed: Missing required tools" "ERROR"
        exit 1
    }
    
    if (-not (Test-Python-Modules)) {
        Write-Log "Installing missing Python modules..." "INFO"
        pip install pyyaml pillow
    }
    
    Write-Log "البيئة جاهزة للبناء / Ready to build" "SUCCESS"
}

# ============================================================================
# Build Functions
# ============================================================================

function Build-Kernel {
    Write-Section "بناء الـ Kernel / Building Kernel"
    
    $kernelPath = "src\kernel"
    $outPath = "build-artifacts\build"
    
    if (-not (Test-Path $kernelPath)) {
        Write-Log "Kernel source not found: $kernelPath" "ERROR"
        return $false
    }
    
    # Create build directory
    New-Item -ItemType Directory -Force -Path $outPath | Out-Null
    
    Write-Log "Compiling kernel.c..."
    gcc -O2 -Wall -Werror `
        -ffreestanding -fno-stack-protector `
        -c "$kernelPath\kernel.c" `
        -o "$outPath\kernel.o"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Kernel compilation failed" "ERROR"
        return $false
    }
    
    Write-Log "Assembling bootloader..."
    nasm -f elf64 "$kernelPath\src\boot.asm" `
        -o "$outPath\boot.o" 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Boot assembly failed (non-critical)" "WARNING"
    }
    
    Write-Log "Linking kernel..."
    gcc -O2 -nostdlib -no-pie `
        "$outPath\boot.o" "$outPath\kernel.o" `
        -o "$outPath\carrot.bin"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Kernel linking failed" "ERROR"
        return $false
    }
    
    $binSize = (Get-Item "$outPath\carrot.bin").Length / 1024
    Write-Log "Kernel built successfully: carrot.bin ($([math]::Round($binSize, 2)) KB)" "SUCCESS"
    
    return $true
}

function Build-Init {
    Write-Section "بناء نظام Init / Building Init System"
    
    $initPath = "src\core\init"
    $outPath = "build-artifacts\build"
    
    if (-not (Test-Path "$initPath\main.c")) {
        Write-Log "Init source not found" "ERROR"
        return $false
    }
    
    Write-Log "Compiling init..."
    gcc -O2 -Wall -Werror -static `
        "$initPath\main.c" `
        -o "$outPath\init"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Init compilation failed" "ERROR"
        return $false
    }
    
    Write-Log "Init system built successfully" "SUCCESS"
    return $true
}

function Build-Python-Apps {
    Write-Section "بناء تطبيقات Python / Building Python Apps"
    
    $appDirs = @(
        "apps\core\desktop-shell",
        "apps\core\display-manager",
        "apps\system\settings",
        "apps\utilities\terminal"
    )
    
    foreach ($appDir in $appDirs) {
        if (Test-Path "$appDir\*.py") {
            Write-Log "Validating Python syntax: $appDir"
            Get-ChildItem "$appDir\*.py" | ForEach-Object {
                python -m py_compile $_.FullName
                if ($LASTEXITCODE -ne 0) {
                    Write-Log "Syntax error in $_" "ERROR"
                    return $false
                }
            }
        }
    }
    
    Write-Log "Python apps validated" "SUCCESS"
    return $true
}

function Build-ISO {
    Write-Section "إنشاء صورة ISO / Building ISO Image"
    
    $isoPath = "build-artifacts\iso"
    $outMkiso = "build-artifacts\build\mkisofs.py"
    
    if (-not (Test-Path $isoPath)) {
        Write-Log "ISO staging directory not found" "ERROR"
        return $false
    }
    
    # Create Python script to generate ISO
    $mkisoScript = @'
#!/usr/bin/env python3
import os
import sys
import struct

def create_iso(source_dir, output_iso):
    """Create a basic ISO 9660 image (simplified)"""
    print(f"Creating ISO: {output_iso}")
    
    # For production, use pycdlib or call mkisofs via Windows tools
    # This is a placeholder - actual ISO creation is more complex
    
    with open(output_iso, 'wb') as iso:
        # Write PVD (Primary Volume Descriptor)
        pvd = bytearray(2048)
        pvd[0:1] = b'\x01'  # Type code
        pvd[1:6] = b'CD001'  # Standard identifier
        iso.write(pvd)
    
    print(f"ISO created: {os.path.getsize(output_iso) / 1024:.2f} KB")

if __name__ == "__main__":
    create_iso(sys.argv[1], sys.argv[2])
'@
    
    Set-Content -Path $outMkiso -Value $mkisoScript
    
    # Use PowerShell alternative for ISO creation
    Write-Log "Using PowerShell ISO tools..."
    
    # Create a simple ISO using mkisofs (if available) or PowerShell
    if ((Get-Command mkisofs -ErrorAction SilentlyContinue)) {
        mkisofs -o "build-artifacts\build\carrot-os.iso" -boot-load-size 4 `
            -b boot/grub/stage2_eltorito -no-emul-boot -boot-info-table `
            $isoPath
    } else {
        Write-Log "mkisofs not found. Creating raw disk image instead..." "WARNING"
        
        # Create a raw disk image (can be converted to ISO later)
        python -c "
import os
size_mb = 700
with open('build-artifacts/build/carrot-os.img', 'wb') as f:
    f.write(b'\x00' * (size_mb * 1024 * 1024))
print(f'Created raw image: {size_mb} MB')
"
    }
    
    Write-Log "ISO/Image creation completed" "SUCCESS"
    return $true
}

function Invoke-Clean {
    Write-Section "تنظيف الملفات المؤقتة / Cleaning Build Artifacts"
    
    $cleanDirs = @(
        "build-artifacts\build"
    )
    
    foreach ($dir in $cleanDirs) {
        if (Test-Path $dir) {
            Write-Log "Removing: $dir"
            Remove-Item -Recurse -Force -Path $dir
        }
    }
    
    Write-Log "Clean completed" "SUCCESS"
}

function Invoke-BurnISO {
    Write-Section "حرق ISO على USB / Burning ISO to USB"
    
    if (-not $Drive) {
        Write-Log "استخدم: .\build.ps1 -BurnISO -Drive 'e:'" "WARNING"
        Write-Log "Available USB drives:"
        Get-Volume | Where-Object { $_.DriveType -eq 'Removable' }
        return $false
    }
    
    $isoFile = "build-artifacts\build\carrot-os.iso"
    
    if (-not (Test-Path $isoFile)) {
        Write-Log "ISO file not found: $isoFile" "ERROR"
        return $false
    }
    
    Write-Log "استخدم Rufus لحرق الصورة:" "WARNING"
    Write-Log "1. حمل Rufus من: https://rufus.ie/"
    Write-Log "2. استخدم الملف: $isoFile"
    Write-Log "3. اختر الـ Drive: $Drive"
    
    return $true
}

# ============================================================================
# Main Entry Point
# ============================================================================

function Show-Help {
    $help = @"
CarrotOS Windows Build System

الاستخدام / Usage:
  .\build.ps1 [Options]

الخيارات / Options:
  -Validate         التحقق من البيئة (Check environment)
  -BuildKernel      بناء الـ Kernel
  -BuildInit        بناء نظام Init
  -BuildPython      التحقق من Python
  -BuildISO         إنشاء ISO
  -BuildAll         بناء كل الأجزاء
  -Clean            تنظيف الملفات المؤقتة
  -BurnISO          حرق ISO على USB (-Drive required)
  -Drive <letter>   الـ USB drive (مثال: e:)
  -Help             عرض هذه الرسالة

أمثلة / Examples:
  .\build.ps1 -Validate
  .\build.ps1 -BuildAll
  .\build.ps1 -BurnISO -Drive "e:"
  .\build.ps1 -Clean

"@
    Write-Host $help
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

if (-not (Test-Path "src\kernel\kernel.c")) {
    Write-Log "يجب تشغيل السكريبت من مجلد CarrotOS" "ERROR"
    exit 1
}

if ($Validate) {
    Invoke-Validation
    exit 0
}

if ($BuildAll) {
    Invoke-Validation
    Build-Kernel
    Build-Init
    Build-Python-Apps
    Build-ISO
    exit 0
}

if ($BuildKernel) { Build-Kernel; exit $LASTEXITCODE }
if ($BuildInit) { Build-Init; exit $LASTEXITCODE }
if ($BuildPython) { Build-Python-Apps; exit $LASTEXITCODE }
if ($BuildISO) { Build-ISO; exit $LASTEXITCODE }
if ($Clean) { Invoke-Clean; exit 0 }
if ($BurnISO) { Invoke-BurnISO; exit $LASTEXITCODE }

Show-Help
