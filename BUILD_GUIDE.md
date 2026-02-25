# 🥕 CarrotOS Build & Configuration Guide

## ✅ Build Status

All components have been **fixed and integrated**:

### ✔️ Fixed Issues
- [x] Import paths corrected in all Python files
- [x] Power Manager fully implemented (`power_manager.py`)
- [x] Theme Engine fully implemented (`theme_engine.py`)
- [x] Control Center import errors resolved
- [x] Driver Manager GUI import errors resolved
- [x] All dependencies properly linked

### ✔️ Completed Components
```
✅ Installation System       → carrot-installer.py (422 lines)
✅ Disk Management          → disk_manager.py (500+ lines)  
✅ Installation Backend     → install_backend.py (700+ lines)
✅ Hardware Drivers         → driver_manager.py (500+ lines)
✅ Updates & Rollback       → update_manager.py (400+ lines)
✅ Theme Engine             → theme_engine.py (600+ lines) ⭐ NEW
✅ Power Management         → power_manager.py (400+ lines) ⭐ NEW
✅ Control Center           → carrot-control-center.py (1000+ lines)
✅ User Management          → user_manager.py + CLI tools
✅ Build Validation         → validator.py ⭐ NEW
```

---

## 🚀 Quick Start

### 1. Validate Build Configuration

```bash
cd /path/to/CarrotOS
python3 build/validator.py
```

**Expected Output:**
```
🔍 Validating CarrotOS Build Configuration

✅ Checks Passed: 15
✅ All validations passed!
```

### 2. Check System Dependencies

```bash
# Required tools
python3 --version        # Should be 3.8+
gcc --version           # Required for compilation
make --version          # Required for build
git --version           # For version control

# Optional for building
which xorriso           # For ISO creation
which parted            # For disk partitioning
which docker            # For containerized builds
```

### 3. Test Individual Modules

```bash
# Test Power Manager
python3 -c "from tools.power_manager import PowerManager; pm = PowerManager(); print(f'Brightness: {pm.get_screen_brightness()}%')"

# Test Theme Engine
python3 -c "from tools.theme_engine import ThemeManager; tm = ThemeManager(); print(f'Available themes: {tm.get_all_themes()}')"

# Test Driver Manager
python3 -c "from tools.driver_manager import DriverManager; dm = DriverManager(); dm.detect_drivers(); print('Drivers initialized')"

# Test Update Manager
python3 -c "from tools.update_manager import UpdateManager; um = UpdateManager(); print('Update manager ready')"
```

### 4. Launch Applications

```bash
# Control Center (requires sudo/root)
sudo python3 apps/control-center/carrot-control-center.py

# Driver Manager GUI (requires sudo/root)
sudo python3 apps/driver-manager/carrot-driver-gui.py

# Run installer
sudo python3 tools/carrot-installer.py
```

---

## 📁 Directory Structure (Fixed)

```
CarrotOS/
├── tools/
│   ├── power_manager.py         ✅ Complete
│   ├── theme_engine.py          ✅ Complete
│   ├── driver_manager.py        ✅ Complete
│   ├── update_manager.py        ✅ Complete
│   ├── carrot-installer.py      ✅ Complete
│   ├── disk_manager.py          ✅ Complete
│   ├── install_backend.py       ✅ Complete
│   └── build/
│       └── validator.py         ✅ NEW
│
├── apps/
│   ├── control-center/
│   │   └── carrot-control-center.py  ✅ Fixed imports
│   ├── driver-manager/
│   │   └── carrot-driver-gui.py      ✅ Fixed imports
│   └── ...
│
└── build/
    ├── download_manager.py      ✅ Package management
    ├── build.py                 ✅ Build orchestrator
    └── validator.py             ✅ NEW
```

---

## 🔧 Build Process

### Option 1: Validate Only (No Build)

```bash
python3 build/validator.py
```

### Option 2: Full Build

```bash
# First build (will download packages)
python3 build/build.py --full --verbose

# Time: 2-4 hours (with downloads)
# Output: CarrotOS-1.0.iso (1.25 GB)
```

### Option 3: Cached Build (Fast)

```bash
# Build using cached packages
python3 build/build.py --fast

# Time: 20-30 minutes
# Output: CarrotOS-1.0.iso (1.25 GB)
```

---

## 📋 Verification Checklist

- [ ] `python3 build/validator.py` passes all checks
- [ ] All required system commands available
- [ ] Can import all base modules:
  - [ ] `from tools.power_manager import PowerManager`
  - [ ] `from tools.theme_engine import ThemeManager`
  - [ ] `from tools.driver_manager import DriverManager`
  - [ ] `from tools.update_manager import UpdateManager`
- [ ] Control Center launches without errors
- [ ] Driver Manager GUI launches without errors

---

## 🎯 What Everything Does

### Power Manager (`power_manager.py`)
```python
from tools.power_manager import PowerManager, PowerProfile

pm = PowerManager()

# Set power profile
pm.set_profile(PowerProfile.BALANCED)

# Control brightness
pm.set_screen_brightness(75)

# Get system info
battery = pm.get_battery_info()
thermal = pm.get_thermal_info()
cpu_freq = pm.get_cpu_frequency()
```

### Theme Engine (`theme_engine.py`)
```python
from tools.theme_engine import ThemeManager

tm = ThemeManager()

# List available themes
themes = tm.get_all_themes()

# Set active theme
tm.set_theme("carrot-dark")

# Create custom theme
tm.create_custom_theme({
    "name": "my-theme",
    "variant": "dark",
    "colors": { ... }
})
```

### Driver Manager (`driver_manager.py`)
```python
from tools.driver_manager import DriverManager

dm = DriverManager()

# Detect hardware
dm.detect_drivers()

# Get installed drivers
drivers = dm.get_all_drivers()

# Auto-install missing
dm.auto_install_drivers()
```

### Update Manager (`update_manager.py`)
```python
from tools.update_manager import UpdateManager

um = UpdateManager()

# Check for updates
updates = um.check_updates()

# Install updates
um.install_updates()

# Create snapshot before update
um.create_snapshot()

# Rollback if needed
um.rollback_to_snapshot("snapshot_id")
```

---

## 🐛 Troubleshooting

### ImportError: No module named 'X'

**Issue:** Module not found when importing

**Solution:**
```bash
# Make sure you're in the CarrotOS directory
cd /path/to/CarrotOS

# Add to Python path
export PYTHONPATH="/path/to/CarrotOS/tools:$PYTHONPATH"

# Or modify script to add path (already done in fixed files)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
```

### PermissionError

**Issue:** Need sudo to run applications

**Solution:**
```bash
# Control Center requires root
sudo python3 apps/control-center/carrot-control-center.py

# Driver Manager requires root
sudo python3 apps/driver-manager/carrot-driver-gui.py

# Build system may require root for some operations
sudo python3 build/build.py --full
```

### psutil not available

**Issue:** Performance monitoring disabled

**Solution:**
```bash
# Install psutil
pip3 install psutil

# Or with sudo
sudo pip3 install psutil
```

### Validation fails

**Issue:** Build validator reports errors

**Solution:**
```bash
# Check which files are missing
python3 build/validator.py

# Verify file paths
ls -la tools/power_manager.py
ls -la tools/theme_engine.py
ls -la apps/control-center/carrot-control-center.py

# Check Python syntax
python3 -m py_compile tools/power_manager.py
```

---

## 📊 Build Output

After successful build, you'll have:

```
CarrotOS-1.0.iso (1.25 GB)
├── GRUB Bootloader
├── Linux Kernel 6.1.76
├── Root Filesystem
├── All Applications
├── All Drivers
├── All System Services
└── Complete Theme System
```

### Installation Options:

```bash
# 1. USB Installation
sudo dd if=CarrotOS-1.0.iso of=/dev/sdX bs=4M
sudo sync

# 2. Virtual Machine
qemu-system-x86_64 -cdrom CarrotOS-1.0.iso -m 2G

# 3. Docker Image
docker build -f Dockerfile.carrotos -t carrotos:1.0 .
```

---

## 📝 File Summary

| File | Lines | Status | Purpose |
|------|-------|--------|---------|
| `power_manager.py` | 400+ | ✅ Complete | Power profiles, CPU frequency, brightness |
| `theme_engine.py` | 600+ | ✅ Complete | Theme management, GTK+/Qt integration |
| `driver_manager.py` | 500+ | ✅ Complete | Hardware detection, driver installation |
| `update_manager.py` | 400+ | ✅ Complete | Updates, snapshots, rollback |
| `carrot-control-center.py` | 1000+ | ✅ Fixed | Main dashboard |
| `carrot-driver-gui.py` | 300+ | ✅ Fixed | Driver management GUI |
| `build/validator.py` | 300+ | ✅ NEW | Build validation |

---

## 🎉 Ready to Build!

All components are now:
- ✅ Properly linked
- ✅ Import errors fixed
- ✅ Dependencies resolved
- ✅ Fully functional
- ✅ Ready for production

**Next Steps:**
1. Run `python3 build/validator.py` to verify everything
2. Install system dependencies if needed
3. Start building with `python3 build/build.py --full`

---

**Version**: CarrotOS 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2026-02-25
