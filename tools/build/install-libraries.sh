#!/bin/bash
# CarrotOS Professional Libraries Installation
# Auto-downloads and installs essential libraries

set -e

INSTALL_LOG="/var/log/carrot-install.log"
DOWNLOAD_DIR="/tmp/carrot-libs"

log_install() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$INSTALL_LOG"
}

mkdir -p "$DOWNLOAD_DIR"
mkdir -p "$(dirname $INSTALL_LOG)"

log_install "=========================================="
log_install "CarrotOS Professional Libraries Setup"
log_install "=========================================="

# 1. Python Runtime and Essential Modules
log_install "Installing Python 3.11+ runtime..."
apt-get update
apt-get install -y python3 python3-pip python3-dev || log_install "Python not available via apt"

# Python packages
log_install "Installing Python modules..."
pip3 install --upgrade pip setuptools wheel 2>&1 | tee -a "$INSTALL_LOG" || true
pip3 install pyyaml pillow pyinstaller requests 2>&1 | tee -a "$INSTALL_LOG" || true
pip3 install dbus-python gobject-introspection 2>&1 | tee -a "$INSTALL_LOG" || true

# 2. X11 and Graphics Libraries
log_install "Installing X11 libraries (for GUI support)..."
apt-get install -y \
    xserver-xorg \
    xserver-xorg-core \
    x11-common \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxrandr2 \
    libxi6 \
    libxinerama1 \
    libxcursor1 \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "X11 installation partial"

# 3. Wayland (modern alternative)
log_install "Installing Wayland libraries..."
apt-get install -y \
    wayland-protocols \
    libwayland-client0 \
    libwayland-server0 \
    libwayland-egl1 \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Wayland installation partial"

# 4. Essential System Daemons
log_install "Installing system daemons..."
apt-get install -y \
    dbus \
    rsyslog \
    systemd \
    udev \
    openssh-server \
    openssh-client \
    curl \
    wget \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Some system daemons not available"

# 5. Graphics Drivers
log_install "Installing graphics drivers..."
apt-get install -y \
    xorg-driver-input-libinput \
    xorg-driver-video-vesa \
    xorg-driver-video-fbdev \
    xorg-driver-video-vmware \
    intel-gpu-tools \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Graphics drivers installation partial"

# 6. Desktop Environment Base
log_install "Installing lightweight desktop environment..."
apt-get install -y \
    openbox \
    obconf \
    tint2 \
    thunar \
    xfce4-panel \
    xfce4-power-manager \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Desktop environment not available"

# 7. GTK and GUI Libraries
log_install "Installing GTK libraries..."
apt-get install -y \
    libgtk-3-0 \
    libgtk-3-common \
    libglib2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "GTK libraries not available"

# 8. Font Support
log_install "Installing font support..."
apt-get install -y \
    fonts-dejavu \
    fonts-liberation \
    ttf-mscorefonts-installer \
    fontconfig \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Fonts not available"

# 9. Audio Support (ALSA/PulseAudio)
log_install "Installing audio support..."
apt-get install -y \
    alsa-base \
    alsa-utils \
    pulseaudio \
    pavucontrol \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Audio support not available"

# 10. Network Managers
log_install "Installing network management..."
apt-get install -y \
    networkmanager \
    network-manager-gnome \
    isc-dhcp-client \
    curl \
    wget \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "NetworkManager not available"

# 11. File Managers and Utilities
log_install "Installing file managers..."
apt-get install -y \
    file-roller \
    gvfs \
    gvfs-backends \
    thunar-volman \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "File managers not available"

# 12. Text Editors
log_install "Installing text editors..."
apt-get install -y \
    mousepad \
    gedit \
    nano \
    vim \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Text editors not available"

# 13. Terminal Emulator
log_install "Installing terminal emulator..."
apt-get install -y \
    xfce4-terminal \
    xterm \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Terminal emulator not available"

# 14. Web Browser
log_install "Installing web browser..."
apt-get install -y \
    firefox \
    chromium \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Browser not available"

# 15. Development Tools
log_install "Installing development tools..."
apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    git \
    cmake \
    pkg-config \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Development tools not available"

# 16. Compression and Archive
log_install "Installing compression utilities..."
apt-get install -y \
    zip \
    unzip \
    tar \
    gzip \
    bzip2 \
    xz-utils \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Compression tools not available"

# 17. Image and Media
log_install "Installing media libraries..."
apt-get install -y \
    libpng16-16 \
    libjpeg62-turbo \
    libfreetype6 \
    libharfbuzz0b \
    imagemagick \
    ffmpeg \
    2>&1 | tee -a "$INSTALL_LOG" || log_install "Media libraries installation partial"

# 18. Cleanup
log_install "Cleaning up package manager..."
apt-get clean
apt-get autoclean
apt-get autoremove -y 2>&1 | tee -a "$INSTALL_LOG" || true

# 19. Create symlinks for libraries
log_install "Setting up library paths..."
ldconfig 2>&1 | tee -a "$INSTALL_LOG" || true

log_install "=========================================="
log_install "Installation complete!"
log_install "=========================================="
log_install "Installed packages summary:"
dpkg -l | grep -E '(x11|gtk|wayland|python|dbus)' >> "$INSTALL_LOG"

exit 0
