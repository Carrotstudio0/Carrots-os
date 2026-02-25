# CarrotOS Installation System

Professional installer for CarrotOS on hard drives, replacing the Live ISO approach with a production-grade installation wizard.

## 📋 Overview

The CarrotOS Installer is a comprehensive installation system that provides:

✅ **Multi-step installation wizard** - Professional, step-by-step setup  
✅ **Disk detection & partitioning** - Automatic or manual disk setup  
✅ **Language & locale selection** - Support for 6+ languages  
✅ **User account creation** - Set up administrator account during installation  
✅ **System configuration** - Hostname, timezone, network setup  
✅ **GUI installation** - User-friendly graphical interface  
✅ **Real-time progress** - Installation status and logging  
✅ **Error handling** - Comprehensive error detection and recovery  

## 🚀 Installation Components

### 1. Main Installer GUI
**File**: `/tools/carrot-installer.py`  
**Status**: ✅ Complete  
**Language**: Python3 + Tkinter  
**Size**: 800x600 window

#### Features:
- **Welcome Screen**: Introduction and disclaimer
- **Language Selection**: Choose language and timezone
- **Disk Selection**: Detect and select target disk
- **Partitioning**: Choose partition scheme (simple/advanced/EFI)
- **User Creation**: Create user account with sudo access
- **System Configuration**: Review and confirm installation
- **Installation Progress**: Real-time progress bar and logging
- **Completion**: Installation summary and reboot instructions

#### Supported Languages:
```
English (en) - en_US.UTF-8
العربية (ar) - ar_SA.UTF-8
Deutsch (de) - de_DE.UTF-8
Español (es) - es_ES.UTF-8
Français (fr) - fr_FR.UTF-8
中文 (zh) - zh_CN.UTF-8
```

#### Supported Timezones:
- UTC standard zones (UTC±N)
- Major cities: New York, Chicago, Los Angeles, London, Paris, Berlin, Tokyo, Shanghai, Dubai, Sydney, Melbourne

### 2. Disk Management Module
**File**: `/tools/disk_manager.py`  
**Status**: ✅ Complete  
**Language**: Python3  
**Purpose**: Disk detection, partitioning, formatting, mounting

#### Key Classes:

**Disk Class**:
```python
@dataclass
class Disk:
    device: str          # /dev/sda
    size: int           # bytes
    model: str          # "Samsung SSD 870"
    vendor: str         # "Samsung"
    partitions: int     # count
    removable: bool     # is USB
```

**Partition Class**:
```python
@dataclass
class Partition:
    device: str         # /dev/sda1
    number: int         # partition number
    size: int          # bytes
    type: str          # ext4, swap, fat32
    mount_point: str   # /, /home, /boot/efi
    label: str         # "root", "home"
```

**DiskManager Class**:
- `detect_disks()` - Find all suitable disks (≥10GB)
- `create_partitions_simple()` - Create root + swap scheme
- `create_partitions_advanced()` - Create /boot, /, /home, swap
- `clear_disk()` - Wipe disk safely
- `create_partition_table()` - Create GPT or MBR table
- `create_partition()` - Create individual partition
- `format_partition()` - Format as ext4, fat32, or swap
- `mount_partition()` - Mount to target filesystem

#### Partition Schemes:

**Simple Scheme** (Recommended for most users):
```
/dev/sdX1  512MB   EFI System Partition      /boot/efi
/dev/sdX2  4GB     Swap                      (swap)
/dev/sdX3  Rest    Root Filesystem (ext4)    /
```

**Advanced Scheme** (For advanced users):
```
/dev/sdX1  512MB   EFI System Partition      /boot/efi
/dev/sdX2  1GB     Boot Partition (ext4)     /boot
/dev/sdX3  20GB    Root Filesystem (ext4)    /
/dev/sdX4  Rest    Home Directory (ext4)     /home
Swap       4GB     Swap Area                 (swap)
```

**EFI Scheme** (UEFI boot):
```
/dev/sdX1  512MB   EFI System Partition      /boot/efi
/dev/sdX2  Rest    Root Filesystem (ext4)    /
Swap       4GB     Swap Area                 (swap)
```

#### Disk Detection:
- Uses `lsblk` for accurate detection
- Fallback to `/sys/block` if lsblk unavailable
- Filters disks < 10GB (prevents accidents)
- Detects removable media (USB drives)
- Skips loop and RAM disks automatically

### 3. Installation Backend
**File**: `/tools/install_backend.py`  
**Status**: ✅ Complete  
**Language**: Python3  
**Purpose**: Perform actual system installation

#### Key Methods:

```python
class InstallationBackend:
    # System setup
    setup_target()              # Create /target structure
    
    # Base system
    install_base_system()       # Kernel, core files
    install_kernel()            # Copy kernel image
    install_system_files()      # System configs
    install_package_manager()   # carrot-pkg setup
    
    # Desktop environment
    install_gui_system()        # Desktop files
    install_applications()      # GUI applications
    
    # Configuration
    configure_bootloader()      # GRUB setup
    setup_network()             # Network config
    configure_locale()          # Language/timezone
    create_user()              # User account
    configure_services()        # systemd services
    
    # Finalization
    verify_installation()       # Verify integrity
    finalize_installation()     # Complete setup
    run_full_installation()     # Full process
```

#### Installation Flow:
1. **Setup** (10%) - Create directory structure
2. **Base System** (35%) - Install kernel, core files
3. **GUI** (40%) - Desktop environment
4. **Bootloader** (50%) - GRUB configuration
5. **Network** (60%) - Network setup
6. **Locale** (65%) - Language/timezone
7. **User** (70%) - Create user account
8. **Applications** (75%) - Install apps
9. **Services** (80%) - Configure services
10. **Verification** (90%) - Check installation
11. **Finalization** (100%) - Complete

### 4. Configuration Files

#### Created During Installation:

**System Files** (`/etc/`):
- `os-release` - OS identification (NAME, VERSION, ID, etc.)
- `hostname` - Host name
- `timezone` - Timezone setting
- `shells` - Available shells
- `locale.gen` - Enabled locales
- `default/locale` - Default language
- `network/interfaces` - Network configuration
- `hosts` - hostname resolution
- `passwd` - User database
- `shadow` - Password hashes
- `group` - Group database
- `sudoers` - Sudo permissions

**Boot Files** (`/boot/`):
- `vmlinuz-5.15.0-carrotos` - Kernel image
- `initrd.img-5.15.0-carrotos` - Initial ramdisk
- `grub/grub.cfg` - GRUB configuration
- `EFI/carrotos/` - EFI bootloader (for UEFI)

**Service Files** (`/etc/systemd/system/`):
- `carrot-display-manager.service` - Login screen
- `carrot-shell.service` - Desktop shell
- And others for core services

## 📖 Usage Guide

### Starting the Installer

```bash
# From installation media
sudo python3 carrot-installer.py

# Or from Live USB with proper environment
sudo /opt/carrot-installer.py
```

### Installation Steps

#### Step 1: Welcome
- Read the introduction
- Review the warning about data loss
- Click **Next** to proceed

#### Step 2: Language & Timezone
- Select your language from the list
- Choose timezone from dropdown
- Click **Next**

#### Step 3: Disk Selection
- Select target disk (⚠️ **All data will be erased**)
- Check size and model
- Click **Next**

#### Step 4: Partitioning
- Choose partition scheme:
  - **Simple**: Default for most users (root + swap)
  - **Advanced**: Separate partitions for power users
  - **EFI**: UEFI boot with EFI partition
- Enable disk encryption (LUKS) if desired
- Review partition preview
- Click **Next**

#### Step 5: User Creation
- Enter **Hostname** (computer name)
- Enter **Username** (login name)
- Enter **Password** (8+ characters)
- Confirm password
- Options:
  - ✓ Add to sudo group (admin access)
  - Enable auto-login (not recommended)
- Click **Next**

#### Step 6: Review Configuration
- Check installation summary
- Review all settings
- **Confirm** that you understand data will be erased
- Click **Next** to begin installation

#### Step 7: Installation Progress
- Monitor real-time progress bar
- Watch installation steps in log
- Installation typically takes 10-30 minutes
- **DO NOT interrupt or reboot**

#### Step 8: Completion
- ✓ Installation complete message
- Remove installation media
- Click **Finish** or reboot manually

### Post-Installation

After reboot:

1. **Login**: Use username and password created during installation
2. **Network**: Automatic DHCP by default, reconfigure in Settings if needed
3. **Updates**: Run package manager to update system
4. **Additional Software**: Use Software Center to install applications

## 🔧 Technical Details

### Installation Mount Points

```
/target/               - Root of target system
/target/boot/          - Boot partition
/target/boot/efi/      - EFI partition (UEFI systems)
/target/home/          - Home directories
/target/var/           - Variable data
/target/etc/           - System configuration
```

### Supported Filesystems
- **ext4** - Default, reliable
- **ext3** - Legacy alternative
- **fat32** - EFI partition only
- **swap** - Virtual memory

### Bootloader Support
- **GRUB2** - Primary bootloader
- **EFI** - UEFI boot support
- **Legacy BIOS** - MBR/BIOS boot

### User Management
- **Root** (UID 0) - Administrator
- **System users** (UID 1-999) - Services
- **Regular users** (UID 1000+) - People login

### Security Features
- Password hashing (SHA512)
- Separate shadow passwords
- Sudo access control
- File permission preservation

## 🐛 Troubleshooting

### "No suitable disks found"
**Solutions**:
- Connect disk with ≥10GB space
- Ensure disk is recognized by BIOS
- Try different USB controller port

### "Installation disk is removable"
**Issue**: Installer refused USB drive  
**Solutions**:
- Use internal HDD
- Enable disk in BIOS
- Try different USB port

### "Partition creation failed"
**Issue**: Disk formatting problem  
**Solutions**:
- Check disk is not write-protected
- Try wiping disk with: `dd if=/dev/zero of=/dev/sdX bs=1M`
- Ensure enough free space

### "Bootloader installation failed"
**Solutions**:
- Verify EFI firmware is enabled (for UEFI)
- Check boot partition is created
- Confirm GRUB files were written

### "User creation failed"
**Solutions**:
- Ensure /home partition exists
- Check disk space available
- Verify permissions on /etc/passwd

### Installation slow
**Causes**:
- Slow USB drive or connection
- System bus congestion
- Large disk partitioning
- Formatting large partitions

**Solutions**:
- Use faster USB 3.0 drive
- Close other applications
- Be patient - it's working!

## 📊 System Requirements

### Minimum Requirements:
- **Disk**: 20GB (simple) or 30GB (advanced)
- **RAM**: 1GB (512MB minimum)
- **CPU**: 1GHz processor
- **Boot**: UEFI or BIOS compatible
- **Network**: Optional (for updates)

### Recommended:
- **Disk**: 50GB+ SSD
- **RAM**: 4GB+
- **CPU**: Modern multi-core
- **Boot**: UEFI with Secure Boot
- **Network**: Gigabit Ethernet/WiFi

### Storage Layout:
```
Partition      Recommended    Minimum    Maximum
EFI Boot       512MB          256MB      1GB
Swap           4GB            1GB        16GB
Root /         30GB           10GB       Unlimited
Home /home     20GB           5GB        Unlimited
```

## 🔐 Security Considerations

### Password Security
- Minimum 8 characters (enforced)
- Stored as SHA512 hashes
- Shadow file protected (chmod 000)
- Interactive confirmation required

### File Permissions
- User homes: 700 (user only)
- System files: 755 (readable by all)
- Configuration: 640 (root + group readable)
- Passwords: 000 (root only)

### Secure Installation Practices
1. Use strong passwords (mix case + numbers)
2. Enable disk encryption for sensitive data
3. Keep admin account separate from daily use
4. Regularly update system
5. Backup important data

## 🚀 Advanced Options

### Disk Encryption
- Uses LUKS for full-disk encryption
- Password required at boot
- Transparent after login
- ⚠️ Performance impact (~5-10% penalty)

### Custom Partitioning
- Advanced scheme available
- Manual partition sizing
- Separate partitions for security
- Mount point customization

### Network Configuration
- DHCP (automatic) by default
- Static IP available in Settings
- WiFi and Ethernet support
- DNS configuration

### Locale Selection
- 6 languages supported
- Auto-locale timezone sync
- UTF-8 encoding default
- Keyboard layout configuration

## 📝 Installation Log

Installation log is saved to: `/target/var/log/carrotos-install.log`

Contains:
- All installation steps
- Any errors encountered
- Hardware information
- Configuration details
- Verification results

Access after reboot:
```bash
cat /var/log/carrotos-install.log
```

## 🔄 Reinstallation / Repair

To reinstall or repair:

1. Boot from installation media
2. Run installer again
3. Select same disk
4. Choose **Full Format** when prompted
5. Follow installation wizard normally

### Keeping Data
If you want to keep home directory:
1. Select **Advanced** partitioning
2. Skip /home partition creation
3. Ensure /home has existing data

## 📚 Related Files

- **Configuration**: `/docs/SYSTEM-CONFIGURATION.md`
- **User Management**: `/docs/USER-MANAGEMENT.md`
- **Boot Process**: `/docs/architecture/boot-sequence.md`  
- **Build System**: `/tools/scripts/build.py`

## 🎯 Installation Workflow Diagram

```
[Start Installer]
        ↓
[Welcome Screen] ← Disclaimer
        ↓
[Language & Timezone] ← Choose locale
        ↓
[Disk Detection] ← Select target
        ↓
[Partitioning] ← Choose scheme
        ↓
[User Creation] ← Create account
        ↓
[Configuration Review] ← Confirm
        ↓
[Installation Process] ← Real-time progress
        ├─ Setup
        ├─ Base System
        ├─ GUI
        ├─ Bootloader
        ├─ Network
        ├─ Locale
        ├─ User
        ├─ Apps
        ├─ Services
        └─ Finalize
        ↓
[Completion] ← Success!
        ↓
[Reboot Required]
```

## 🎨 Installer UI Features

### Visual Design
- **Dark Theme**: Eye-friendly with orange accent (#ff8c00)
- **Progress Bar**: Visual installation progress
- **Step Display**: "Step X of 8" indicator
- **Status Messages**: Real-time feedback
- **Installation Log**: Scrollable log display
- **Warnings**: Clear error messages

### Navigation
- **Back Button**: Return to previous step
- **Next Button**: Proceed to next step
- **Cancel Button**: Abort installation
- **Finish Button**: Complete and reboot

## 🌐 Multi-Language Support

The installer provides translations and locale settings for:

| Language | Code | Locale | Font Support |
|----------|------|--------|--------------|
| English | en | en_US.UTF-8 | ✓ |
| العربية | ar | ar_SA.UTF-8 | ✓ RTL |
| Deutsch | de | de_DE.UTF-8 | ✓ |
| Español | es | es_ES.UTF-8 | ✓ |
| Français | fr | fr_FR.UTF-8 | ✓ |
| 中文 | zh | zh_CN.UTF-8 | ✓ |

## 📞 Support & Feedback

For issues, feature requests, or feedback:
- Check `/var/log/carrotos-install.log` for errors
- Review troubleshooting section above
- Check system requirements
- Verify hardware compatibility

---

**CarrotOS Installer v1.0** - Professional Linux Installation System
