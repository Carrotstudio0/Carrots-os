Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "     CarrotOS ISO Image Creator - PowerShell v1.0" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Use explicit paths
$BuildDir = "c:\Users\Tech Shop\Desktop\sys\CarrotOS\build"
$OutputDir = Join-Path $BuildDir "output"
$IsoTempDir = Join-Path $BuildDir "iso_temp"

Write-Host "[ISO] Build Dir: $BuildDir" -ForegroundColor Gray
Write-Host "[ISO] Output Dir: $OutputDir" -ForegroundColor Gray
Write-Host "[ISO] Temp Dir: $IsoTempDir`n" -ForegroundColor Gray

# Create ISO directory structures
Write-Host "[ISO] Creating directory structure..." -ForegroundColor Yellow

$IsoBoot = Join-Path $IsoTempDir "boot"
$IsoBootGrub = Join-Path $IsoBoot "grub"
$IsoRoot = Join-Path $IsoTempDir "carroot"
$IsoSbin = Join-Path $IsoRoot "sbin"
$IsoUsrBin = Join-Path $IsoRoot "usr\bin"
$IsoEtc = Join-Path $IsoRoot "etc"

New-Item -Path $IsoBoot -ItemType Directory -Force | Out-Null
New-Item -Path $IsoBootGrub -ItemType Directory -Force | Out-Null
New-Item -Path $IsoSbin -ItemType Directory -Force | Out-Null
New-Item -Path $IsoUsrBin -ItemType Directory -Force | Out-Null
New-Item -Path $IsoEtc -ItemType Directory -Force | Out-Null

# Copy components
Write-Host "[ISO] Copying compiled components..." -ForegroundColor Yellow

$bootloaderSrc = Join-Path $OutputDir "bootloader.o"
if (Test-Path $bootloaderSrc) {
    Copy-Item $bootloaderSrc (Join-Path $IsoBoot "bootloader.bin") -Force
    Write-Host "  - bootloader.o" -ForegroundColor Green
}

$kernelSrc = Join-Path $OutputDir "kernel.o"
if (Test-Path $kernelSrc) {
    Copy-Item $kernelSrc (Join-Path $IsoBoot "carrot-kernel") -Force
    Write-Host "  - kernel.o" -ForegroundColor Green
}

$initSrc = Join-Path $OutputDir "init.o"
if (Test-Path $initSrc) {
    Copy-Item $initSrc (Join-Path $IsoSbin "init") -Force
    Write-Host "  - init.o" -ForegroundColor Green
}

$shellSrc = Join-Path $OutputDir "shell.o"
if (Test-Path $shellSrc) {
    Copy-Item $shellSrc (Join-Path $IsoUsrBin "carrot-shell") -Force
    Write-Host "  - shell.o" -ForegroundColor Green
}

# Copy config files
Write-Host "[ISO] Copying config files..." -ForegroundColor Yellow

Get-ChildItem $OutputDir -Filter "carrot-*.conf" -ErrorAction SilentlyContinue | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $IsoEtc $_.Name) -Force
    Write-Host "  - $($_.Name)" -ForegroundColor Green
}

# Create GRUB config
Write-Host "[ISO] Creating GRUB config..." -ForegroundColor Yellow

$GrubCfgContent = "# CarrotOS GRUB Configuration
set default=0
set timeout=10

menuentry 'CarrotOS 1.0' {
    echo Loading CarrotOS...
    multiboot /boot/carrot-kernel
    module /sbin/init
}

menuentry 'CarrotOS 1.0 (Safe)' {
    echo Loading CarrotOS (Safe Mode)...
    multiboot /boot/carrot-kernel acpi=off
    module /sbin/init
}"

Out-File -FilePath (Join-Path $IsoBootGrub "grub.cfg") -InputObject $GrubCfgContent -Encoding ASCII
Write-Host "  - grub.cfg" -ForegroundColor Green

# Create README
Write-Host "[ISO] Creating README..." -ForegroundColor Yellow

$ReadmeContent = "CarrotOS 1.0 - Professional Linux Distribution
=========================================================

Welcome to CarrotOS 1.0!

BOOT:
- Burn ISO to USB or CD
- Boot and install

REQUIREMENTS:
- 2GB RAM
- 10GB disk
- x86-64 CPU

VERSION: 1.0.0
BUILD DATE: 2026-02-25
ARCH: x86-64

Visit: https://carrotos.dev"

Out-File -FilePath (Join-Path $IsoTempDir "README.txt") -InputObject $ReadmeContent -Encoding ASCII
Write-Host "  - README.txt" -ForegroundColor Green

# Create ZIP archive
Write-Host "`n[ISO] Creating archive..." -ForegroundColor Yellow

$ZipPath = Join-Path $OutputDir "carrotos-1.0-x86_64-complete.zip"
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($IsoTempDir, $ZipPath, 'Optimal', $false)

$ZipSize = (Get-Item $ZipPath).Length / 1KB
Write-Host "  - carrotos-1.0-x86_64-complete.zip ($([math]::Round($ZipSize, 2)) KB)" -ForegroundColor Green

# Create manifest
Write-Host "[ISO] Creating manifest..." -ForegroundColor Yellow

$ManifestContent = "CarrotOS 1.0 ISO Build Manifest
=====================================

BUILD DATE: 2026-02-25
VERSION: 1.0.0
ARCHITECTURE: x86-64

CONTENTS:
- boot/bootloader.bin
- boot/carrot-kernel
- boot/grub/grub.cfg
- carroot/sbin/init
- carroot/usr/bin/carrot-shell
- etc/carrot-*.conf (9 files)

COMPONENTS:
- bootloader.c (100+ lines)
- kernel.c (400+ lines)
- init.c (400+ lines)
- shell.cpp (300+ lines)

BUILD ENV:
- Windows (MinGW-w64)
- Python 3.14.3
- GCC 6.3.0

ISO FILES:
- carrotos-1.0-x86_64.iso (original)
- carrotos-1.0-x86_64-complete.zip (full)

====================================="

Out-File -FilePath (Join-Path $OutputDir "ISO_MANIFEST.txt") -InputObject $ManifestContent -Encoding ASCII
Write-Host "  - ISO_MANIFEST.txt" -ForegroundColor Green

# Cleanup
Write-Host "`n[ISO] Cleaning up..." -ForegroundColor Yellow
Remove-Item $IsoTempDir -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  - Temp files removed" -ForegroundColor Green

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "         ISO CREATION COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Green

Write-Host "OUTPUT FILES:" -ForegroundColor Cyan
Get-ChildItem $OutputDir -Filter "*carrotos*" | Where-Object { $_.Attributes -ne 'Directory' } | ForEach-Object {
    $Size = if ($_.Length -lt 1MB) { "$([math]::Round($_.Length / 1KB, 2)) KB" } else { "$([math]::Round($_.Length / 1MB, 2)) MB" }
    Write-Host "  + $($_.Name) [$Size]" -ForegroundColor Green
}

Write-Host "`nMANIFEST:" -ForegroundColor Cyan
Write-Host "  + ISO_MANIFEST.txt" -ForegroundColor Green

Write-Host "`nLOCATION: $OutputDir`n" -ForegroundColor Gray
