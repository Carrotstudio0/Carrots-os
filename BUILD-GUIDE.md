# 🥕 CarrotOS Professional Linux Distribution

**Version 1.0.0 (Carrot-LTS)** | Professional Build Guide

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Building CarrotOS](#building-carrotos)
3. [Project Structure](#project-structure)
4. [Architecture](#architecture)
5. [Boot Process](#boot-process)
6. [Installation](#installation)
7. [Features](#features)
8. [Performance](#performance)

---

## 🔧 System Requirements

### Build Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows (WSL2)
- **Disk**: 10GB free space (build artifacts)
- **RAM**: 4GB minimum
- **Python**: 3.8+
- **Tools**: xorriso, mksquashfs, grub-mkimage, cpio

### Runtime Requirements

- **CPU**: x86-64 compatible processor
- **RAM**: 512MB minimum (700MB recommended)
- **Disk**: 2GB for full experience with persistence

---

## 🏗️ Building CarrotOS

### Complete Build Process

```bash
# 1. Clone or navigate to CarrotOS repository
cd /path/to/CarrotOS

# 2. Generate complete distribution
python3 tools/scripts/build.py build all

# This executes:
#   - rootfs_builder.py     (creates root filesystem)
#   - kernel preparation    (5.15.0 LTS x86-64)
#   - initramfs_builder.py  (boot ramdisk)
#   - iso_builder.py        (final ISO assembly)

# Output: build/CarrotOS-1.0.0-x86_64.iso (~700MB)
```

### Build Targets

```bash
# Build root filesystem only
python3 tools/scripts/build.py build rootfs

# Prepare kernel
python3 tools/scripts/build.py build kernel

# Build initramfs only
python3 tools/scripts/build.py build initramfs

# Build ISO only (faster when rootfs exists)
python3 tools/scripts/build.py build iso

# Clean build artifacts
python3 tools/scripts/build.py clean

# Show build information
python3 tools/scripts/build.py info
```

---

## 📁 Project Structure

```
CarrotOS/
├── boot/                    Initial bootloader (GRUB2)
│   ├── bootloader.c        Multiboot2 implementation
│   ├── grub/               GRUB configuration
│   └── efi/                UEFI boot files
│
├── kernel/                  Linux kernel preparation
│   ├── kernel-build.cfg    Kernel configuration
│   └── src/                Kernel interface headers
│
├── core/                    Core system components
│   ├── init/               Init process (PID 1)
│   ├── ipc/                Inter-process communication
│   ├── logging/            System logging
│   └── session/            Session management
│
├── desktop/                 Desktop environment (CDE)
│   ├── src/
│   │   ├── carrot-login.py     Display manager
│   │   └── carrot-shell-launcher.py  Shell
│   ├── compositor/         Wayland compositor
│   └── shell/              Desktop shell
│
├── apps/                    Essential applications
│   ├── terminal/           Terminal emulator
│   ├── files/              File manager
│   ├── settings/           System settings
│   └── software-center/    Package manager UI
│
├── services/               System services
│   └── system/
│       ├── display.service.yaml
│       ├── network.service.yaml
│       └── update.service.yaml
│
├── security/              Security policies
│   ├── security.h         Security module
│   ├── policies/          Firewall rules
│   └── apparmor/          AppArmor profiles
│
├── overlays/              Union filesystem layers
│   ├── base/              Read-only base (squashfs)
│   ├── edition/desktop    Desktop edition
│   ├── custom/            User customizations
│   └── src/               Overlay management
│
├── rootfs/                Root filesystem source
│   ├── base/etc/          Configuration files
│   └── base/usr/          User space applications
│
├── tools/                 Build and utility tools
│   └── scripts/
│       ├── build.py               Master build script
│       ├── rootfs_builder.py      Rootfs generation
│       ├── initramfs_builder.py   Boot ramdisk
│       ├── iso_builder.py         ISO assembly
│       └── overlay_resolver.py    Overlay management
│
└── build/                 Build output directory
    ├── rootfs/            Generated root filesystem
    ├── kernel/            Kernel binary
    ├── initramfs.cpio.gz  Boot ramdisk
    ├── iso_build/         ISO assembly staging
    └── CarrotOS-1.0.0-x86_64.iso  Final ISO
```

---

## 🏗️ Architecture

### 6-Layer System Architecture

```
┌────────────────────────────────────────────────┐
│ Layer 6: Applications                          │
│ Terminal | Files | Settings | Monitor | Center│
└────────────────────────────────────────────────┘
                         ▲
┌────────────────────────────────────────────────┐
│ Layer 5: Desktop GUI (CDE - Carrot Desktop)    │
│ Wayland/X11 | Shell | Weston | Launcher      │
└────────────────────────────────────────────────┘
                         ▲
┌────────────────────────────────────────────────┐
│ Layer 4: Services                              │
│ Network | Display | Update | Audio            │
└────────────────────────────────────────────────┘
                         ▲
┌────────────────────────────────────────────────┐
│ Layer 3: Core System                           │
│ Init (PID 1) | IPC | Logging | Sessions      │
└────────────────────────────────────────────────┘
                         ▲
┌────────────────────────────────────────────────┐
│ Layer 2: Kernel (Linux 5.15.0 LTS x86-64)     │
│ Memory | Interrupts | Scheduler | I/O         │
└────────────────────────────────────────────────┘
                         ▲
┌────────────────────────────────────────────────┐
│ Layer 1: Bootloader (GRUB2 UEFI/BIOS)        │
│ Multiboot2 | Firmware Handoff                 │
└────────────────────────────────────────────────┘
```

---

## 🚀 Boot Process

### Boot Sequence (Typical)

```
1. BIOS/UEFI Power-on
   └─ Hardware initialization
      └─ Firmware handoff

2. GRUB Bootloader (~1-2 seconds)
   └─ Load menu
      └─ Select boot option
         └─ Load kernel + initramfs

3. Kernel Initialization (~3-5 seconds)
   └─ Hardware detection
      └─ System memory setup
         └─ Interrupt handling
            └─ Execute initramfs

4. Initramfs Early Boot (~1-2 seconds)
   ├─ Mount /proc, /sys, /dev
   ├─ Find root filesystem
   ├─ Load overlays
   └─ Switch to new root
      └─ Execute init

5. Main Init System (carrot-init) (~3-5 seconds)
   ├─ Mount essential filesystems
   ├─ Setup hostname & networking
   ├─ Start services
   │  ├─ syslog
   │  ├─ networkd
   │  └─ display manager
   └─ Ready for login

6. Display Manager (carrot-login)
   └─ Show login screen
      └─ User authentication
         └─ Session startup
            └─ Desktop environment (Wayland/Weston)

Total Boot Time: ~15-20 seconds to usable desktop
```

---

## 📦 Installation

### Creating Bootable USB Drive

**Linux/macOS:**
```bash
# Identify USB device
lsblk  # or diskutil list

# Write ISO to USB (careful: choose correct device!)
sudo dd if=CarrotOS-1.0.0-x86_64.iso of=/dev /sdX bs=4M status=progress
sudo sync
```

**Windows:**
```powershell
# Use Rufus or Balena Etcher
# https://www.balena.io/etcher/
# Select ISO and USB drive, click Flash
```

### Virtual Machine Testing

**QEMU/KVM:**
```bash
qemu-system-x86_64 \
  -m 2048 \
  -smp 2 \
  -cdrom CarrotOS-1.0.0-x86_64.iso \
  -vmx -enable-kvm \
  -display gtk
```

**VirtualBox:**
1. Create new VM (Linux, 64-bit)
2. Allocate 2GB RAM, 30GB disk
3. Attach ISO as CD-ROM
4. Boot and install

---

## ✨ Features

### Core Features

✅ **Lightweight**
  - < 700MB ISO size
  - ~ 500-600MB RAM usage idle
  - Fast SSD boot (< 15 seconds)

✅ **Modern Desktop**
  - Wayland display server
  - Custom lightweight shell (CDE)
  - Minimalist aesthetic with modern UI

✅ **Security**
  - AppArmor MAC policies
  - Default firewall rules
  - Audit logging
  - User/Group isolation

✅ **Flexible Storage**
  - OverlayFS for live boot
  - Persistent layer support
  - Read-only base system
  - Reset capability

✅ **Essential Applications**
  - Terminal emulator
  - File manager
  - System settings
  - System monitor
  - Network integration

### Advanced Features

- **Multi-workspace desktop** (4 default)
- **Application launcher** with search
- **Network manager** (DHCP, WiFi)
- **Service management** (YAML-based)
- **Modular build system**
- **Custom theme engine**

---

## ⚡ Performance Targets

| Metric | Target | Typical |
|--------|--------|---------|
| ISO Size | < 800MB | ~700MB |
| RAM Idle | < 700MB | ~550MB |
| RAM Heavy | < 1.5GB | ~1.2GB |
| Boot Time | < 20s | ~15s |
| Login Time | < 5s | ~3s |
| App Startup | < 2s | ~1.5s |

---

## 🎨 Visual Identity

### Color Scheme
- **Primary**: Orange (#FF9500) - Brand color
- **Secondary**: Dark Gray (#222222) - Background
- **Accent**: Light Orange (#FFB84D) - Highlights
- **Text**: White (#FFFFFF) - On dark backgrounds

### Applications
- **Logo**: [Carrot icon in orange]
- **Boot Splash**: Carrot logo with text
- **Login Screen**: Username/password with background
- **Desktop**: Dark mode with orange accents

---

## 📞 Support & Documentation

- **Documentation**: `docs/` directory
- **Issues**: Report in project repository
- **Status**: Production Ready v1.0.0

---

**Happy Computing! 🥕**
