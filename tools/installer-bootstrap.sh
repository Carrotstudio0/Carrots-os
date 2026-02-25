#!/bin/bash
# CarrotOS Installer Bootstrap Script
# Prepares Live environment and launches the installer

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check root
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root"
    exit 1
fi

print_status "CarrotOS Installer Bootstrap"
echo ""

# Detect environment
if grep -q "LIVE" /etc/lsb-release 2>/dev/null; then
    ENVIRONMENT="LIVE"
    INSTALLER_PATH="/opt/carrot-installer"
else
    ENVIRONMENT="UNKNOWN"
    INSTALLER_PATH="/usr/local/bin/carrot-installer"
fi

print_status "Environment: $ENVIRONMENT"
print_status "Installer Path: $INSTALLER_PATH"

# Step 1: Check dependencies
print_status "Checking dependencies..."

REQUIRED_PACKAGES=(
    "python3"
    "parted"
    "lsblk"
    "grub-pc"
)

MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! command -v "$package" &> /dev/null; then
        if ! dpkg -l | grep -q "^ii.*$package"; then
            MISSING_PACKAGES+=("$package")
        fi
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    print_warning "Missing packages: ${MISSING_PACKAGES[@]}"
    print_status "Attempting to install missing packages..."
    
    # Update package lists
    apt-get update -q
    
    # Install missing packages
    for package in "${MISSING_PACKAGES[@]}"; do
        print_status "Installing $package..."
        apt-get install -y "$package" > /dev/null 2>&1 || true
    done
fi

print_success "All dependencies available"

# Step 2: Check storage for installation
print_status "Checking available storage..."

# Create target mount point
if [ ! -d "/target" ]; then
    mkdir -p /target
fi

# Find suitable installation disks
DISKS=$(lsblk -d -n -o NAME,SIZE,TYPE | grep disk | awk '{print $1, $2}')

if [ -z "$DISKS" ]; then
    print_error "No suitable disks found"
    print_error "Installation requires a disk with at least 20GB free space"
    exit 1
fi

DISK_COUNT=$(echo "$DISKS" | wc -l)
print_success "Found $DISK_COUNT disk(s):"

echo "$DISKS" | while read disk size; do
    echo "  /dev/$disk - $size"
done

# Step 3: Prepare installer environment
print_status "Preparing installer environment..."

# Create necessary directories
mkdir -p /var/log/carrotos
mkdir -p /var/lib/carrotos
mkdir -p /tmp/carrotos

print_success "Directories created"

# Step 4: Setup display
print_status "Configuring display..."

# Check for X11
if command -v X &> /dev/null; then
    DISPLAY=":0"
    export DISPLAY
    print_success "X11 display configured"
elif command -v Xvfb &> /dev/null; then
    # Virtual display
    Xvfb :0 -screen 0 1024x768x16 &
    DISPLAY=":0"
    export DISPLAY
    print_status "Virtual display created"
fi

# Step 5: Launch installer
print_status "Launching CarrotOS Installer..."
echo ""

# Check if installer exists
if [ ! -f "$INSTALLER_PATH" ]; then
    print_error "Installer not found: $INSTALLER_PATH"
    
    # Try alternative paths
    if [ -f "/opt/carrot-installer.py" ]; then
        INSTALLER_PATH="/opt/carrot-installer.py"
    elif [ -f "/usr/bin/carrot-installer" ]; then
        INSTALLER_PATH="/usr/bin/carrot-installer"
    else
        print_error "Could not find installer in common locations"
        exit 1
    fi
fi

# Make sure installer is executable
chmod +x "$INSTALLER_PATH"

# Run installer
if python3 "$INSTALLER_PATH"; then
    print_success "Installation completed successfully"
    
    # Offer options
    echo ""
    read -p "Reboot now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Rebooting system..."
        sync
        reboot
    else
        print_status "Installation complete. You can reboot manually when ready."
        print_status "Log file: /var/log/carrotos-install.log"
    fi
else
    print_error "Installation failed or was cancelled"
    
    # Show logs
    if [ -f "/var/log/carrotos-install.log" ]; then
        print_status "Recent log entries:"
        tail -20 /var/log/carrotos-install.log
    fi
    
    echo ""
    echo "You can:"
    echo "1. Rerun the installer: python3 $INSTALLER_PATH"
    echo "2. Check logs: tail -f /var/log/carrotos-install.log"
    echo "3. Reboot and try again"
fi

# Cleanup
print_status "Cleaning up..."
rm -rf /tmp/carrotos/*

exit 0
