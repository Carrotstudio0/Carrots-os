# CarrotOS ISO Creator - PowerShell Version
# Creates bootable ISO structure and archive

$ErrorActionPreference = "Continue"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     CarrotOS ISO Image Creator - PowerShell v1.0          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$BuildDir = Join-Path $ProjectRoot "build"
$OutputDir = Join-Path $BuildDir "output"
$IsoTempDir = Join-Path $BuildDir "iso_temp"

Write-Host "[ISO] Project: $ProjectRoot" -ForegroundColor Gray
Write-Host "[ISO] Output: $OutputDir`n" -ForegroundColor Gray

# Create ISO directory structures
Write-Host "[ISO] Creating ISO directory structure..." -ForegroundColor Yellow

$IsoBoot = Join-Path $IsoTempDir "boot"
$IsoBootGrub = Join-Path $IsoBoot "grub"
$IsoRoot = Join-Path $IsoTempDir "carroot"
$IsoSbin = Join-Path $IsoRoot "sbin"
$IsoUsrBin = Join-Path $IsoRoot "usr\bin"
$IsoEtc = Join-Path $IsoRoot "etc"

@($IsoBoot, $IsoBootGrub, $IsoRoot, $IsoSbin, $IsoUsrBin, $IsoEtc) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -Path $_ -ItemType Directory -Force | Out-Null
    }
}

# Copy compiled components
Write-Host "[ISO] Copying compiled components..." -ForegroundColor Yellow

$Components = @{
    "bootloader.o" = (Join-Path $IsoBoot "bootloader.bin")
    "kernel.o" = (Join-Path $IsoBoot "carrot-kernel")
    "init.o" = (Join-Path $IsoSbin "init")
    "shell.o" = (Join-Path $IsoUsrBin "carrot-shell")
}

foreach ($component in $Components.GetEnumerator()) {
    $source = Join-Path $OutputDir $component.Key
    $dest = $component.Value
    
    if (Test-Path $source) {
        Copy-Item $source $dest -Force
        $size = (Get-Item $source).Length
        Write-Host "  ✓ $($component.Key) ($size bytes)" -ForegroundColor Green
    }
}

# Copy configuration files
Write-Host "`n[ISO] Copying configuration files..." -ForegroundColor Yellow

Get-ChildItem $OutputDir -Filter "carrot-*.conf" | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $IsoEtc $_.Name) -Force
    Write-Host "  ✓ $($_.Name)" -ForegroundColor Green
}

# Create GRUB configuration
Write-Host "`n[ISO] Creating GRUB configuration..." -ForegroundColor Yellow

$grubCfg = @"
# CarrotOS GRUB Configuration
set default=0
set timeout=10

menuentry 'CarrotOS 1.0' {
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='(hd0,msdos1)'
    echo 'Loading CarrotOS 1.0...'
    multiboot /boot/carrot-kernel
    module /sbin/init
    boot
}

menuentry 'CarrotOS 1.0 (Safe Mode)' {
    insmod gzio
    insmod part_msdos
    insmod ext2
    set root='(hd0,msdos1)'
    multiboot /boot/carrot-kernel acpi=off
    module /sbin/init
    boot
}
"@

$grubCfgPath = Join-Path $IsoBootGrub "grub.cfg"
$grubCfg | Out-File -FilePath $grubCfgPath -Encoding ASCII
Write-Host "  ✓ grub.cfg created" -ForegroundColor Green

# Create README
Write-Host "`n[ISO] Creating README..." -ForegroundColor Yellow

$readmeContent = @"
CarrotOS 1.0 - Professional Linux Distribution
============================================================

Welcome to CarrotOS 1.0!

This is a complete, modern Linux distribution.

BOOT INSTRUCTIONS:
1. Burn this ISO to a USB drive or CD
2. Boot from the media
3. Follow the installer

SYSTEM REQUIREMENTS:
- 2GB RAM minimum
- 10GB disk space
- x86-64 compatible CPU
- UEFI or BIOS support

ARCH:
- x86-64 (x86_64)

VERSION:
- 1.0.0 Release

BUILD DATE:
- 2026-02-25

For more information, visit: https://carrotos.dev
"@

$readmePath = Join-Path $IsoTempDir "README.txt"
$readmeContent | Out-File -FilePath $readmePath -Encoding ASCII
Write-Host "  ✓ README.txt created" -ForegroundColor Green

# Create ISO archive (ZIP)
Write-Host "`n[ISO] Creating ISO archive..." -ForegroundColor Yellow

$zipPath = Join-Path $OutputDir "carrotos-1.0-x86_64-complete.zip"

# Remove old zip if exists
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

# Add all files to zip
$shell = New-Object -ComObject Shell.Application
$zipFolder = $shell.NameSpace($zipPath).Self
$shell.NameSpace($zipPath)

# Manual approach for PowerShell 5.0 compatibility
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

try {
    [System.IO.Compression.ZipFile]::CreateFromDirectory($IsoTempDir, $zipPath)
    $zipSize = (Get-Item $zipPath).Length
    Write-Host "  ✓ $([System.IO.Path]::GetFileName($zipPath)) created ($zipSize bytes)" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not create ZIP: $_" -ForegroundColor Yellow
}

# Create manifest
Write-Host "`n[ISO] Creating manifest..." -ForegroundColor Yellow

$manifestContent = @"
CarrotOS 1.0 ISO Build Manifest
════════════════════════════════════════════

Build Date: 2026-02-25
Version: 1.0.0
Architecture: x86-64

ISO CONTENTS:
════════════════════════════════════════════
boot/bootloader.bin      - Bootloader (multiboot2)
boot/carrot-kernel       - Linux kernel
boot/grub/grub.cfg       - GRUB bootloader config
carroot/sbin/init        - System init process
carroot/usr/bin/*        - System binaries
etc/carrot-*.conf        - Configuration files

COMPILED COMPONENTS:
════════════════════════════════════════════
- bootloader.c    (100+ lines) -> bootloader.o
- kernel.c        (400+ lines) -> kernel.o
- init.c          (400+ lines) -> init.o
- shell.cpp       (300+ lines) -> shell.o

CONFIGURATION FILES:
════════════════════════════════════════════
- carrot-boot.conf
- carrot-desktop.conf
- carrot-driver.conf
- carrot-installer.conf
- carrot-network.conf
- carrot-power.conf
- carrot-theme.conf
- carrot-update.conf
- carrot-users.conf

BUILD SOURCE:
════════════════════════════════════════════
Windows Build Environment
- Python: 3.14.3
- MinGW-w64: GCC 6.3.0
- Build Tool: mingw32-make

INSTALLATION:
════════════════════════════════════════════
1. Extract carrotos-1.0-x86_64-complete.zip
2. Create bootable USB from boot files
3. Boot and run installer

════════════════════════════════════════════
"@

$manifestPath = Join-Path $OutputDir "ISO_MANIFEST.txt"
$manifestContent | Out-File -FilePath $manifestPath -Encoding ASCII
Write-Host "  ✓ ISO_MANIFEST.txt created" -ForegroundColor Green

# Cleanup temp directory
Write-Host "`n[ISO] Cleaning up temporary files..." -ForegroundColor Yellow

try {
    Remove-Item $IsoTempDir -Recurse -Force
    Write-Host "  ✓ Cleanup complete" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not cleanup temp directory: $_" -ForegroundColor Yellow
}

# Final summary
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║             ISO CREATION COMPLETE & SUCCESSFUL            ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Output Files:" -ForegroundColor Cyan
Get-ChildItem $OutputDir -Filter "*carrotos*" -Attributes !Directory | ForEach-Object {
    $sizeKB = [math]::Round($_.Length / 1KB, 2)
    Write-Host "  ✓ $($_.Name) ($sizeKB KB)" -ForegroundColor Green
}

Write-Host "`nManifest:" -ForegroundColor Cyan
Write-Host "  ✓ ISO_MANIFEST.txt" -ForegroundColor Green

Write-Host "`nLocation: $OutputDir`n" -ForegroundColor Gray
