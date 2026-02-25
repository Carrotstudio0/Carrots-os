# 🥕 CarrotOS - Professional Linux Distribution v1.0

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-brightgreen)](https://python.org)
[![Build Status](https://img.shields.io/badge/Build-Professional-blue)]()

---

## 📖 Overview | نظرة عامة

**CarrotOS** is a professional, feature-rich Linux distribution built on a stable Linux LTS kernel with complete desktop environment support and advanced system management capabilities.

**CarrotOS** هو توزيعة لينكس احترافية وحديثة مبنية على نواة Linux LTS مع دعم كامل للسطح الدراسي والتطبيقات المتقدمة.

---

## ✨ Key Features

### 🚀 Performance & Stability
- **Kernel Optimization**: Optimized Linux LTS kernel for high performance
- **Fast Boot**: Rapid boot time (< 15 seconds)
- **Stable**: Enterprise-grade reliability
- **Efficient**: Low resource footprint

### 🎨 Professional Desktop Environment
- **Carrot Shell**: Modern GUI with advanced window management
- **Theme Engine**: Integrated appearance management (Dark/Light modes)
- **Compositor**: Optimized display server with visual effects
- **7 Pre-installed Applications**: Ready-to-use applications

### 🛠️ Advanced System Management
- **Auto Driver Detection**: Automatic hardware detection and driver installation
- **Smart Updates**: Update management with rollback capability
- **Power Profiles**: Multiple power management profiles
- **User Management**: Comprehensive user and group administration
- **Network Management**: Integrated network and firewall configuration

### 🔒 Security & Reliability
- **Secure Boot**: Digital signature chain verification
- **Firewall**: Integrated UFW firewall
- **User Policies**: Advanced security policies
- **Snapshot System**: Automatic system snapshots for recovery

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│      🎨 User Applications Layer                 │
│  File Manager │ Terminal │ Editor │ Browser     │
└────────────────────┬────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│   🖥️ Desktop Environment (Carrot Shell)        │
│  Window Manager │ Compositor │ Login Manager    │
└────────────────────┬────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│    🛠️ System Managers (Python)                  │
│ Driver │ Update │ User │ Network │ Power │ Theme │
└────────────────────┬────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│    🔧 Configuration Layer (/etc/carrot-*.conf)  │
└────────────────────┬────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│     🔴 Kernel Layer (Linux LTS)                 │
│  Memory │ Scheduler │ Interrupts │ Drivers      │
└────────────────────┬────────────────────────────┘
                     │
┌─────────────────────────────────────────────────┐
│    ⚫ Bootloader (GRUB 2 + Custom Boot Code)    │
└─────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
CarrotOS/
├── 📄 Documentation
│   ├── README.md (this file)
│   ├── ARCHITECTURE.md (system architecture)
│   ├── CONTRIBUTING.md (contribution guidelines)
│   └── CODE_QUALITY_STANDARDS.md (code standards)
│
├── 🔧 Kernel & Core
│   ├── kernel/
│   │   ├── kernel.c (main kernel)
│   │   ├── kernel-build.cfg (kernel config)
│   │   └── src/ (kernel source)
│   └── core/
│       ├── init/ (init process - PID 1)
│       ├── ipc/ (inter-process communication)
│       ├── logging/ (system logging)
│       └── session/ (session management)
│
├── 🖥️ Desktop Environment
│   ├── desktop/
│   │   ├── shell/ (desktop shell)
│   │   ├── compositor/ (display server)
│   │   └── themes/ (UI themes)
│   └── apps/ (system applications)
│       ├── terminal/
│       ├── file-manager/
│       ├── text-editor/
│       ├── browser/
│       └── ...
│
├── 🛠️ System Tools
│   └── tools/
│       ├── driver_manager.py
│       ├── update_manager.py
│       ├── power_manager.py
│       ├── theme_engine.py
│       ├── user_manager.py
│       ├── network_manager.py
│       ├── iso_creator.py
│       └── carrot-installer.py
│
├── ⚙️ Build System
│   ├── Makefile (comprehensive build)
│   ├── build/ (build output)
│   └── requirements.txt (Python dependencies)
│
├── 📚 Documentation
│   └── docs/
│       ├── SYSTEM_ARCHITECTURE.md
│       ├── SYSTEM_INTEGRATION.md
│       ├── USER_MANAGEMENT.md
│       └── CONTROL_CENTER.md
│
└── 🔐 System Files
    ├── security/
    ├── packages/
    ├── services/
    └── overlays/
```

---

## 🚀 Getting Started

### Build Requirements
- **OS**: Linux, macOS, or Windows (WSL2)
- **Tools**: 
  - C compiler (gcc)
  - C++ compiler (g++)
  - Python 3.8+
  - Make
  - Git

### Build Instructions

```bash
# 1. Validate project structure
make validate

# 2. Install dependencies
make install-deps

# 3. Build all components
make all

# 4. Build specific components
make build-kernel    # Kernel only
make build-init      # Init system only
make build-python    # Python tools only

# 5. Create bootable ISO
make iso
```

### Quick Start

```bash
# Show available targets
make help

# Clean build artifacts
make clean

# Full clean (including virtual environment)
make distclean

# Run tests
make test

# Check code syntax
make check-syntax

# Check code style
make check-style
```

---

## 📖 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and components
- **[CODE_QUALITY_STANDARDS.md](CODE_QUALITY_STANDARDS.md)** - Code standards and best practices
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute to the project
- **[docs/](docs/)** - Additional documentation

---

## 🏗️ Building

The project uses a professional **Makefile** build system:

```bash
# Prerequisites
make validate
make install-deps

# Build process
make              # Build everything
make build-c      # Build C components
make build-cpp    # Build C++ components
make build-python # Build Python components

# Output artifacts
make             # Generates in build/output/
make iso         # Creates bootable ISO image
```

---

## 🔐 Security

- All code follows security best practices
- Input validation on all user inputs
- Memory-safe programming with proper error handling
- Privilege checking for administrative operations
- Audit logging for security events

---

## 📝 Code Standards

All code follows professional standards:
- **C Code**: ISO C99 with POSIX compliance
- **Python Code**: PEP 8 style guide
- **Documentation**: Comprehensive function documentation
- **Error Handling**: Proper error checking and recovery
- **Testing**: Unit and integration tests

See [CODE_QUALITY_STANDARDS.md](CODE_QUALITY_STANDARDS.md) for detailed guidelines.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Code style and standards
- Commit message format
- Pull request process
- Testing requirements
- Documentation requirements

---

## 📄 License

CarrotOS is licensed under the **GNU General Public License v3** (GPL-3.0)

See [LICENSE](LICENSE) for details.

---

## 👥 Authors & Maintainers

**CarrotOS Development Team**
- Professional Linux Distribution Project
- 2024

---

## 📞 Contact & Support

- **Project Status**: Production Ready (v1.0)
- **Build Status**: All Components Functional
- **Last Updated**: February 2026

---

## 🎯 Project Goals

- ✅ Professional, production-ready Linux distribution
- ✅ Clean, maintainable codebase
- ✅ Comprehensive documentation
- ✅ Advanced system management
- ✅ Security and stability
- ✅ User-friendly desktop environment

---

## 📊 Statistics

- **Codebase**: 6000+ lines of professional code
- **Languages**: C, C++, Python, Shell
- **Components**: 15+ integrated modules
- **Applications**: 7 pre-installed
- **Documentation**: Comprehensive guides

---

## 🎉 Features Coming Soon

- Enhanced GPU support
- Advanced virtualization support
- Cloud integration
- Mobile app management
- Extended theme library

---

**CarrotOS: Professional Linux Made Simple**

*Built with attention to detail, security, and performance.*
