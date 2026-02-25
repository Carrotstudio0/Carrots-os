# CarrotOS Project Overview

**CarrotOS** هو نظام تشغيل Linux محترف حديث مصمم للعمل على أجهزة سطح المكتب والخوادم الصغيرة.

## 🎯 الأهداف الرئيسية

- ✅ نظام تشغيل خفيف وسريع
- ✅ تجربة سطح مكتب حديثة وجميلة
- ✅ أمان قوي بشكل افتراضي
- ✅ مرنة وقابلة للتخصيص
- ✅ دعم محمول وأجهزة محمولة

## 📁 هيكل المشروع

```
CarrotOS/
├── boot/             - Bootloader (GRUB2, UEFI)
├── kernel/           - Linux kernel configuration (LTS)
├── core/             - نظام أساسي (init, IPC, logging)
├── desktop/          - Wayland compositor and shell
├── services/         - System services definitions
├── apps/             - Built-in applications
├── security/         - Security policies and modules
├── overlays/         - OverlayFS layers
├── rootfs/           - Root filesystem base
├── packages/         - Package management
├── tools/            - Build tools and utilities
├── build/            - Build configurations and manifests
└── docs/             - Documentation and architecture
```

## 🔧 البنية المعمارية

### Layer 1: Boot Layer (Bootloader)
- GRUB 2 with UEFI + BIOS support
- Secure Boot ready
- Configuration in `boot/grub/grub.cfg`

### Layer 2: Kernel Layer
- Linux 5.15.0 LTS
- x86-64 optimized
- Configuration: `kernel/kernel-build.cfg`

### Layer 3: Core System Layer
- Init process (PID 1) in `core/init/src/main.c`
- Logging subsystem
- IPC mechanisms
- Session management

### Layer 4: Service Layer
- Systemd-compatible service manager
- Network daemon
- Display server
- Update service
- Files in `services/system/*.service.yaml`

### Layer 5: Desktop/GUI Layer
- Wayland display server (Weston)
- CarrotOS Shell (C++ implementation)
- GTK3 + Qt5 support
- Located in `desktop/`

### Layer 6: Application Layer
- File Manager
- Terminal Emulator
- Settings/Control Center
- Software Center
- Located in `apps/`

## 🔐 Security Model

- **AppArmor** for MAC (Mandatory Access Control)
- **Firewall** with sensible defaults
- **Audit logging** enabled
- **SELinux-compatible** architecture

## 📦 OverlayFS Strategy

Base system uses union filesystem for flexibility:

1. **Base Layer** (read-only): Core system files
2. **Edition Layer** (read-only): Desktop-specific packages
3. **OEM Layer** (read-only): Manufacturer customizations
4. **Custom Layer** (read-write): User modifications
5. **Runtime Layer** (tmpfs): Session-specific changes

## 🛠️ Build System

- **Build tool**: Python-based custom build system
- **Manifest files**: YAML configuration
- **Output**: ISO image for live boot + persistent install

Build commands:
```bash
python3 tools/scripts/build.py build all      # Full build
python3 tools/scripts/build.py build kernel   # Kernel only
python3 tools/scripts/build.py build desktop  # Desktop only
```

## 📚 Documentation

- `docs/architecture/` - System design documents
- `docs/development/` - Developer guides
- `docs/security/` - Security documentation

## 🤝 Contributing

See CONTRIBUTING.md for contribution guidelines.

## 📜 License

CarrotOS is released under GPL-3.0+ license.
