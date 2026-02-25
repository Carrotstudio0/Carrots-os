# CarrotOS Build and Installation Complete Guide

## Overview

CarrotOS is a complete, modular Linux distribution built with:
- **Python 3.8+** for userspace system managers and GUI applications
- **C** for kernel-mode code and bootloader
- **C++** for desktop environment components
- Comprehensive configuration system with auto-detection

## Project Structure

```
CarrotOS/
├── boot/                 # Bootloader (GRUB configuration)
│   ├── efi/             # EFI boot files
│   ├── grub/            # GRUB 2 configuration
│   └── bootloader.c     # Bootloader implementation
├── kernel/              # Kernel source
│   ├── config/          # Kernel configuration
│   ├── patches/         # Kernel patches
│   └── kernel.c         # Kernel implementation
├── core/
│   ├── init/            # Init process (PID 1)
│   │   └── src/
│   │       └── init.c   # Init system implementation
│   ├── ipc/             # Inter-process communication
│   ├── logging/         # System logging
│   └── session/         # Session management
├── desktop/
│   ├── shell/           # Desktop environment
│   │   └── src/
│   │       └── shell.cpp # Desktop shell implementation
│   ├── compositor/      # Display server
│   └── themes/          # Theme components
├── tools/               # System management tools
│   ├── driver_manager.py        # Hardware driver management
│   ├── update_manager.py        # System updates with rollback
│   ├── user_manager.py          # User management
│   ├── network_manager.py       # Network configuration
│   ├── power_manager.py         # Power profiles
│   ├── theme_engine.py          # Theme system
│   ├── carrot-installer.py      # OS installer
│   ├── disk_manager.py          # Disk/partition management
│   └── build/
│       ├── build.py             # Main build system
│       ├── validator.py         # Configuration validator
│       ├── download_manager.py  # Package downloader
│       └── iso_builder.py       # ISO creation
├── apps/                # GUI Applications
│   ├── control-center/
│   │   └── carrot-control-center.py
│   ├── driver-manager/
│   │   └── carrot-driver-gui.py
│   ├── terminal/
│   ├── files/
│   ├── settings/
│   └── ...
├── rootfs/              # Filesystem structure
│   └── base/
│       └── etc/
│           ├── carrot-desktop.conf      # Desktop configuration
│           ├── carrot-boot.conf         # Boot configuration
│           ├── carrot-update.conf       # Updates configuration
│           ├── carrot-driver.conf       # Driver configuration
│           ├── carrot-power.conf        # Power management configuration
│           ├── carrot-theme.conf        # Theme configuration
│           ├── carrot-users.conf        # User management configuration
│           ├── carrot-network.conf      # Network configuration
│           └── carrot-installer.conf    # Installer configuration
├── services/            # System services
│   ├── system/
│   │   ├── display.service.yaml
│   │   ├── network.service.yaml
│   │   └── update.service.yaml
│   └── ...
├── security/            # Security components
│   ├── policies/
│   ├── keys/
│   └── ...
├── build/               # Build configuration
│   ├── manifests/
│   ├── profiles/
│   └── ...
├── docs/                # Documentation
├── releases/            # Release packages
└── Makefile             # Build system
```

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+, Fedora 33+, Debian 11+)
- **RAM**: 2GB minimum (4GB recommended for building)
- **Disk Space**: 10GB minimum (20GB recommended)
- **CPU**: x86-64 compatible processor

### Build Tools Required

```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3 python3-pip git \
    gcc g++ make binutils grub2 xorriso cpio

# Fedora
sudo dnf install gcc gcc-c++ make python3 python3-pip git \
    grub2-tools xorriso cpio

# Arch
sudo pacman -S base-devel python3 git grub xorriso
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

Key Python packages:
- PyYAML - Configuration files
- psutil - System monitoring
- subprocess - Process management
- requests - Package downloads

## Building CarrotOS

### Step 1: Validate Configuration
```bash
make validate
```
Checks all files and configurations are present and valid.

### Step 2: Install Dependencies
```bash
make install-deps
```
Installs Python packages and build tools.

### Step 3: Build Components

Build all components:
```bash
make all
```

Build specific components:
```bash
make kernel          # Build Linux kernel
make bootloader      # Build bootloader
make init            # Build init process (PID 1)
make shell           # Build desktop shell
make build-python    # Build Python system managers
```

### Step 4: Create Installation Media

Build bootable ISO:
```bash
make iso
```

Creates `carrotos-1.0-x86_64.iso` in build/output/

## Installation

### From Live ISO
1. Boot from ISO (USB stick or VM)
2. Run installer: `carrot-installer`
3. Follow 8-step installation wizard:
   - Welcome screen
   - Disk partitioning
   - Network configuration
   - User creation
   - Package selection
   - Security options
   - Installation summary
   - Install and reboot

### Command Line Installation (Advanced)
```bash
carrot-installer --non-interactive \
    --disk /dev/sda \
    --filesystem ext4 \
    --enable-efi \
    --username carrot \
    --timezone UTC
```

## System Managers

### Driver Manager
Auto-detects and installs hardware drivers:
```bash
python3 /usr/bin/carrot-driver-manager
```

### Update Manager
System updates with automatic rollback:
```bash
python3 /usr/bin/carrot-update-manager
```

### User Manager
User and group administration:
```bash
python3 /usr/bin/carrot-user-manager
```

### Network Manager
Network configuration and firewall:
```bash
python3 /usr/bin/carrot-network-manager
```

### Power Manager
Power profiles and performance tuning:
```bash
python3 /usr/bin/carrot-power-manager
```

### Theme Engine
Desktop appearance customization:
```bash
python3 /usr/bin/carrot-theme-engine
```

## Configuration Files

All system configuration is in `/etc/carrot-*.conf`:

- `/etc/carrot-desktop.conf` - Desktop environment settings
- `/etc/carrot-boot.conf` - Boot parameters
- `/etc/carrot-update.conf` - Update preferences
- `/etc/carrot-driver.conf` - Driver detection options
- `/etc/carrot-power.conf` - Power management profiles
- `/etc/carrot-theme.conf` - Theme settings
- `/etc/carrot-users.conf` - User management policies
- `/etc/carrot-network.conf` - Network configuration
- `/etc/carrot-installer.conf` - Installer options

## GUI Applications

CarrotOS includes 7 pre-configured applications:
1. **Carrot Control Center** - System settings and configuration
2. **Carrot Driver Manager** - Hardware driver GUI
3. **Terminal** - Command line interface
4. **File Manager** - File browser
5. **Text Editor** - Text editing
6. **Settings** - System preferences
7. **Software Center** - Application installer

## System Architecture

### Boot Sequence
1. GRUB bootloader loads kernel
2. Kernel initializes (memory, interrupts, devices)
3. Init process (PID 1) starts system services
4. Services startup according to runlevels:
   - Runlevel 3: Multi-user with network
   - Runlevel 5: Graphical desktop
5. Desktop shell launches
6. User login

### Process Architecture
```
Init (PID 1)
├── System Daemons
│   ├── syslogd - System logging
│   ├── networkd - Network management
│   ├── sshd - SSH remote access
│   └── update daemon - System updates
├── Desktop Environment
│   ├── Carrot Shell - Window manager
│   ├── Compositor - Display server
│   └── Applications - User programs
└── User Session
    ├── Login Manager (GDM/LightDM)
    └── User Applications
```

## Testing

Run validation tests:
```bash
make test
```

Check specific components:
```bash
python3 -m py_compile tools/*.py
```

## Troubleshooting

### Build Errors
```bash
# Clean and rebuild
make clean
make all

# Check validator
make validate
```

### Runtime Issues
Check system logs:
```bash
journalctl -u carrot-service-name
tail -f /var/log/carrot-*.log
```

### Driver Issues
Run driver detection:
```bash
python3 tools/driver_manager.py --detect
```

## Performance Tuning

### Power Profiles
```bash
# High performance
carrot-power-manager --profile performance

# Balanced (default)
carrot-power-manager --profile balanced

# Power saving
carrot-power-manager --profile powersave
```

### Kernel Parameters
Edit `/etc/carrot-boot.conf`:
```
[kernel]
cmdline=ro quiet splash transparent_hugepage=madvise
modules=ext4,xhci_hcd,ahci
```

## Security

### Firewall Configuration
```bash
# Enable UFW firewall
carrot-network-manager --enable-firewall

# Allow specific port
carrot-network-manager --allow-port 22
```

### User Security
```bash
# Set password policy
carrot-user-manager --set-password-policy \
    --min-length 12 \
    --expiration 90 \
    --enforce-complexity
```

## Next Steps

1. **Customize**: Edit configuration files in `/etc/carrot-*.conf`
2. **Extend**: Add custom applications to `/usr/bin`
3. **Optimize**: Tune performance with power profiles
4. **Secure**: Configure firewall and user policies
5. **Deploy**: Create custom ISO with your changes

## Additional Resources

- **Documentation**: See `docs/` directory
- **API Reference**: See source code headers
- **Contributing**: See `CONTRIBUTING.md`
- **License**: GPL v3 (see LICENSE)

## Support

- Project Repository: https://github.com/carrotos/carrotos
- Issue Tracker: https://github.com/carrotos/carrotos/issues
- Community Forum: https://forum.carrotos.org

---

**CarrotOS Version 1.0**
© 2024 CarrotOS Project - GPL v3 License
