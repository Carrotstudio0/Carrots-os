#Requires -RunAsAdministrator
#Requires -Version 5.1
<#
.SYNOPSIS
    Automatic Windows Environment Setup for CarrotOS
.DESCRIPTION
    Installs MinGW-w64, NASM, Python and configures everything
#>

param(
    [switch]$SkipChocolatey = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $colors = @{
        "INFO"    = "`e[36m"
        "SUCCESS" = "`e[32m"
        "WARNING" = "`e[33m"
        "ERROR"   = "`e[31m"
    }
    $reset = "`e[0m"
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = $colors[$Level]
    Write-Host "$color[$timestamp $Level]$reset $Message"
}

function Test-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal $identity
    return $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

# Check admin rights
if (-not (Test-Administrator)) {
    Write-Log "This script requires Administrator privileges" "ERROR"
    Write-Log "Please run PowerShell as Administrator" "WARNING"
    exit 1
}

Write-Log "CarrotOS Windows Environment Setup" "INFO"
Write-Log "This will install MinGW-w64, NASM, and Python" "INFO"
Read-Host "Press Enter to continue (or Ctrl+C to cancel)"

# ============================================================================
# Setup Chocolatey
# ============================================================================

if (-not $SkipChocolatey) {
    Write-Log "Checking Chocolatey..." "INFO"
    
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Log "Installing Chocolatey..." "INFO"
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Chocolatey installed successfully" "SUCCESS"
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        } else {
            Write-Log "Chocolatey installation failed" "ERROR"
            exit 1
        }
    } else {
        Write-Log "Chocolatey already installed" "SUCCESS"
    }
}

# ============================================================================
# Install Tools
# ============================================================================

$packages = @(
    @{ Name = "mingw-w64"; Description = "C/C++ Compiler" },
    @{ Name = "nasm"; Description = "Assembler" },
    @{ Name = "python"; Description = "Python 3" }
)

foreach ($package in $packages) {
    Write-Log "Checking $($package.Description)..." "INFO"
    
    # Check if already installed
    choco list --local-only | Select-String $package.Name | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Log "$($package.Description) already installed" "SUCCESS"
    } else {
        Write-Log "Installing $($package.Description)..." "INFO"
        choco install $package.Name -y --ignore-checksums
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to install $($package.Description)" "WARNING"
        } else {
            Write-Log "$($package.Description) installed" "SUCCESS"
        }
    }
}

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# ============================================================================
# Verify Installation
# ============================================================================

Write-Log "Verifying installation..." "INFO"

$tools = @(
    @{ Name = "gcc"; Command = "gcc --version" },
    @{ Name = "nasm"; Command = "nasm --version" },
    @{ Name = "python"; Command = "python --version" }
)

$allValid = $true
foreach ($tool in $tools) {
    try {
        $output = Invoke-Expression $tool.Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "$($tool.Name): ✓" "SUCCESS"
            if ($Verbose) {
                Write-Host $output
            }
        } else {
            Write-Log "$($tool.Name): ✗" "ERROR"
            $allValid = $false
        }
    }
    catch {
        Write-Log "$($tool.Name): ✗ (not found)" "ERROR"
        $allValid = $false
    }
}

if (-not $allValid) {
    Write-Log "Some tools failed. Please check the errors above." "ERROR"
    exit 1
}

# ============================================================================
# Setup Python Packages
# ============================================================================

Write-Log "Installing Python packages..." "INFO"

$pythonModules = @("pyyaml", "pillow", "pyinstaller")

foreach ($module in $pythonModules) {
    Write-Log "Installing $module..." "INFO"
    pip install $module -q
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "$module installed" "SUCCESS"
    } else {
        Write-Log "Failed to install $module" "WARNING"
    }
}

# ============================================================================
# Final Validation
# ============================================================================

Write-Log "Final environment validation..." "INFO"

python -c "import yaml, PIL; print('All Python modules OK')" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Log "Python modules verified" "SUCCESS"
} else {
    Write-Log "Some Python modules are missing" "WARNING"
}

# ============================================================================
# Summary
# ============================================================================

Write-Host "`n$([char]0x1b)[36m$(('=' * 70))$([char]0x1b)[0m"
Write-Log "Setup completed successfully! ✓" "SUCCESS"
Write-Host "$([char]0x1b)[36m$(('=' * 70))$([char]0x1b)[0m`n"

Write-Log "You can now build CarrotOS using:" "INFO"
Write-Host "  cd $PWD"
Write-Host "  .\build.ps1 -Validate"
Write-Host "  .\build.ps1 -BuildAll`n"

Write-Log "Or use the batch file:" "INFO"
Write-Host "  build.bat all`n"

exit 0
