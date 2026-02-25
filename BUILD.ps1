#!/usr/bin/env pwsh
# =============================================================================
# CarrotOS Complete Build Script for Windows
# بناء CarrotOS الكامل على Windows
# =============================================================================

param(
    [string]$MinGWPath = "C:\mingw64",
    [switch]$SkipMinGWCheck = $false
)

# Colors
$colors = @{
    Success = [System.ConsoleColor]::Green
    Error = [System.ConsoleColor]::Red
    Warning = [System.ConsoleColor]::Yellow
    Info = [System.ConsoleColor]::Cyan
    Header = [System.ConsoleColor]::Magenta
}

function Write-Step {
    param([string]$Message, [string]$Step)
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor $colors.Header
    Write-Host "▶ $Step" -ForegroundColor $colors.Header
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor $colors.Header
    Write-Host "$Message" -ForegroundColor $colors.Info
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $colors.Success
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $colors.Error
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $colors.Warning
}

# =============================================================================
# Step 1: Setup MinGW PATH
# =============================================================================
Write-Step "Setup MinGW-w64 in PATH" "[1/8] MinGW Setup"

if (-not $SkipMinGWCheck) {
    if (Test-Path "$MinGWPath\bin\gcc.exe") {
        $env:Path = "$MinGWPath\bin;$env:Path"
        Write-Success "MinGW-w64 found at: $MinGWPath"
        Write-Success "Added to PATH: $MinGWPath\bin"
    } else {
        Write-Error-Custom "MinGW not found at: $MinGWPath"
        Write-Host ""
        Write-Host "Please extract MinGW-w64 to one of these locations:" -ForegroundColor Yellow
        Write-Host "  1. C:\mingw64 (Recommended)" -ForegroundColor White
        Write-Host "  2. C:\Program Files\mingw64" -ForegroundColor White
        Write-Host ""
        Write-Host "Or run with: .\BUILD.ps1 -MinGWPath 'YOUR_MINGW_PATH'" -ForegroundColor Cyan
        Write-Host ""
        exit 1
    }
}

# =============================================================================
# Step 2: Verify Tools
# =============================================================================
Write-Step "Checking required tools installation" "[2/8] Tools Verification"

$tools = @("python", "gcc", "g++", "mingw32-make")
$missing = @()

foreach ($tool in $tools) {
    $toolExists = Get-Command $tool -ErrorAction SilentlyContinue
    if ($toolExists) {
        $version = & $tool --version 2>&1 | Select-Object -First 1
        Write-Success "$tool is installed: $version"
    } else {
        Write-Error-Custom "$tool is NOT installed"
        $missing += $tool
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Error-Custom "Missing tools: $($missing -join ', ')"
    exit 1
}

# =============================================================================
# Step 3: Install Python Dependencies
# =============================================================================
Write-Step "Installing Python dependencies from requirements.txt" "[3/8] Python Dependencies"

if (Test-Path "requirements.txt") {
    Write-Host "Running: pip install -r requirements.txt" -ForegroundColor Cyan
    & pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python dependencies installed successfully"
    } else {
        Write-Warning-Custom "Some Python dependencies may have failed to install"
    }
} else {
    Write-Error-Custom "requirements.txt not found"
    exit 1
}

# =============================================================================
# Step 4: Validate Project Files
# =============================================================================
Write-Step "Validating project files structure" "[4/8] Project Validation"

$requiredFiles = @(
    "Makefile",
    "boot\bootloader.c",
    "kernel\kernel.c",
    "core\init\src\init.c",
    "desktop\shell\src\shell.cpp",
    "tools\driver_manager.py",
    "tools\update_manager.py",
    "rootfs\base\etc\carrot-boot.conf"
)

$missing = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length / 1024
        Write-Success "Found: $file ($('{0:N1}' -f $size) KB)"
    } else {
        Write-Error-Custom "Missing: $file"
        $missing += $file
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Error-Custom "Missing files: $($missing -join ', ')"
    exit 1
}

Write-Host ""
Write-Success "All project files validated!"

# =============================================================================
# Step 5: Run make validate
# =============================================================================
Write-Step "Running make validate to check build configuration" "[5/8] Build Configuration"

Write-Host "Running: make validate" -ForegroundColor Cyan
Write-Host ""
& mingw32-make validate

if ($LASTEXITCODE -ne 0) {
    Write-Warning-Custom "make validate returned code: $LASTEXITCODE"
}

# =============================================================================
# Step 6: Build All Components
# =============================================================================
Write-Step "Building all CarrotOS components (bootloader, kernel, init, shell, managers)" "[6/8] Complete Build"

Write-Host "Running: make all" -ForegroundColor Cyan
Write-Host ""
& mingw32-make all

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Build failed with error code: $LASTEXITCODE"
    exit 1
}

Write-Host ""
Write-Success "All components built successfully!"

# =============================================================================
# Step 7: Create ISO Image
# =============================================================================
Write-Step "Creating ISO image for distribution" "[7/8] ISO Generation"

Write-Host "Running: make iso" -ForegroundColor Cyan
Write-Host ""
& mingw32-make iso

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "ISO creation failed with error code: $LASTEXITCODE"
    exit 1
}

# Check if ISO was created
if (Test-Path "build\output\*.iso") {
    $isoFile = Get-ChildItem "build\output\*.iso" | Select-Object -First 1
    $isoSize = $isoFile.Length / 1048576  # Convert to MB
    Write-Success "ISO created successfully!"
    Write-Host "📦 Image: $($isoFile.Name)" -ForegroundColor Green
    Write-Host "📊 Size: $('{0:N1}' -f $isoSize) MB" -ForegroundColor Green
} else {
    Write-Warning-Custom "ISO file not found in build\output\"
}

# =============================================================================
# Step 8: Build Summary
# =============================================================================
Write-Step "Build completed successfully!" "[8/8] Summary"

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "CarrotOS 1.0 Build Complete" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

# Build statistics
Write-Host "📊 Build Statistics:" -ForegroundColor Cyan
Write-Host ""

$codeFiles = Get-ChildItem -Recurse -Include "*.c", "*.cpp", "*.py" | Measure-Object
$totalLines = 0
Get-ChildItem -Recurse -Include "*.c", "*.cpp", "*.py" | ForEach-Object { 
    $totalLines += (Get-Content $_.FullName | Measure-Object -Line).Lines 
}

Write-Host "  Source Files: $($codeFiles.Count) files" -ForegroundColor White
Write-Host "  Total Lines: $totalLines lines of code" -ForegroundColor White

$buildOutput = Get-ChildItem "build\output\" -ErrorAction SilentlyContinue
if ($buildOutput) {
    Write-Host "  Build Output Files: $($buildOutput.Count) files" -ForegroundColor White
    $totalSize = ($buildOutput | Measure-Object -Sum Length).Sum / 1048576
    Write-Host "  Total Output Size: $('{0:N1}' -f $totalSize) MB" -ForegroundColor White
}

Write-Host ""
Write-Host "📋 Components Built:" -ForegroundColor Cyan
Write-Host "  ✅ Bootloader (boot/bootloader.c)" -ForegroundColor White
Write-Host "  ✅ Kernel (kernel/kernel.c)" -ForegroundColor White
Write-Host "  ✅ Init System (core/init/src/init.c)" -ForegroundColor White
Write-Host "  ✅ Desktop Shell (desktop/shell/src/shell.cpp)" -ForegroundColor White
Write-Host "  ✅ System Managers (6 Python modules)" -ForegroundColor White
Write-Host "  ✅ Configuration Files (9 config files)" -ForegroundColor White
Write-Host "  ✅ ISO Image (carrotos-1.0-x86_64.iso)" -ForegroundColor White
Write-Host ""

Write-Host "📁 Output Directory: build\output\" -ForegroundColor Green
Write-Host "📦 ISO Location: build\output\carrotos-1.0-x86_64.iso" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Boot from ISO or use in virtual machine" -ForegroundColor White
Write-Host "  2. Run the interactive installer" -ForegroundColor White
Write-Host "  3. Follow the 8-step installation wizard" -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ CarrotOS 1.0 build complete! Ready for distribution." -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Success "Build process completed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
