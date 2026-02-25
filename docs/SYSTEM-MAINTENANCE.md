# CarrotOS System Maintenance Documentation

## Overview

This document covers the complete system maintenance infrastructure for CarrotOS, including:
- System updates with snapshot-based rollback
- Hardware driver detection and installation
- Maintenance tools and utilities

---

## Part 1: System Updates Manager

### 1.1 Overview

The CarrotOS Update Manager provides enterprise-grade system and application updates with automatic rollback capability through snapshots.

**Key Features:**
- Automatic pre-update snapshots
- Security, bugfix, feature, and system updates
- Checksum verification for downloaded packages
- Rollback to any previous system state
- Multi-channel support (stable, testing)
- Automatic cleanup of old cache

### 1.2 Architecture

```
Update Manager System:
├── UpdateManager (Main Interface)
│   ├── update_manager.py
│   ├── config.json (/etc/carrot-updater/)
│   └── Metadata storage (/var/lib/carrot-updater/)
├── GUI Interface
│   ├── carrot-updater-gui.py
│   └── 3 Tabs: Updates, Snapshots, Settings
├── Storage
│   ├── /var/cache/carrot-updater/ (Downloaded packages)
│   ├── /var/lib/carrot-updater/ (Metadata)
│   ├── /var/lib/carrot-snapshots/ (Full system snapshots)
│   └── /var/log/carrot-updates.log (Log file)
└── System Integration
    ├── Automatic pre-update backup
    ├── Version tracking
    └── Checksum verification
```

### 1.3 Update Types

| Type | Description | Frequency | Risk |
|------|-------------|-----------|------|
| SECURITY | Security patches | As needed | Low (vetted) |
| BUGFIX | Bug fixes | Weekly | Low (tested) |
| FEATURE | New features | Monthly | Medium (new code) |
| SYSTEM | Major system updates | Quarterly | Higher (foundation changes) |

### 1.4 Update Status Tracking

```
AVAILABLE        → Update available on server
    ↓
DOWNLOADED       → Package downloaded and verified
    ↓
INSTALLED        → Applied to system
    ↓
[ERROR]          → Falls back to last snapshot
    ↓
ROLLED_BACK      → System restored, update queued for retry
```

### 1.5 Configuration

**File**: `/etc/carrot-updater/config.json`

```json
{
  "auto_update": true,                    // Enable automatic updates
  "check_interval": 86400,                // Check every 24 hours
  "auto_backup": true,                    // Create snapshot before update
  "keep_snapshots": 5,                    // Maintain max 5 snapshots
  "update_channels": ["stable", "testing"],  // Available channels
  "current_channel": "stable"             // Currently active channel
}
```

### 1.6 Installation

```bash
# Update Manager is pre-installed at:
/tools/update_manager.py

# GUI is available at:
/apps/update-center/carrot-updater-gui.py

# To launch GUI:
sudo carrot-updater-gui

# Log file:
tail -f /var/log/carrot-updates.log
```

### 1.7 Command-Line Usage

#### Check for Updates
```python
from update_manager import UpdateManager

manager = UpdateManager()
updates = manager.check_updates()

for update in updates:
    print(f"{update.name} v{update.version} - {update.update_type}")
```

#### Download and Install
```python
# Download specific update
manager.download_update(update)

# Install (creates snapshot first)
result = manager.install_update(update)
if result:
    print("Success!")
else:
    print("Update failed, rolled back")
```

#### Snapshot Management
```python
# Create manual snapshot
snapshot_id = manager.create_snapshot("Before major update")

# List all snapshots
snapshots = manager.get_snapshots()

# Rollback to snapshot
manager.rollback_to_snapshot(snapshot_id)
```

### 1.8 Update Center GUI

**Launch**: `sudo carrot-updater-gui`

#### Updates Tab
- List available updates with:
  - Name and description
  - Type (security, bugfix, feature, system)
  - Download size
  - Installation time estimate
- Buttons:
  - "Check for Updates" - Query update servers
  - "Install All" - Install all available updates
  - "Install Selected" - Install checked items
  - "View Details" - Show changelog and requirements

**Update Installation Flow**:
```
1. User clicks "Install All"
2. System checks disk space
3. Creates snapshot (auto-backup)
4. Downloads all updates with verification
5. Installs in dependency order
6. Verifies integrity
7. Reports success/failure
8. Offers rollback if failed
```

#### Snapshots Tab
- List all system snapshots:
  - Date created
  - Description
  - Size on disk
  - System version at snapshot

- Buttons:
  - "Create Snapshot" - Manual backup
  - "Restore Selected" - Rollback to snapshot
  - "Delete" - Remove old snapshot
  - "Details" - View full snapshot info

**Snapshot Operations**:
```
Create Snapshot:
├── Compress /etc (config files)
├── Compress /var/lib (database)
├── Compress /usr/local (local software)
├── Store metadata (version, timestamp)
├── Store in /var/lib/carrot-snapshots/
└── Keep max N snapshots (default: 5)

Restore Snapshot:
├── Verify snapshot integrity
├── Create backup of current state
├── Extract all snapshot files
├── Restore file permissions
├── Verify system integrity
└── Reboot if needed
```

#### Settings Tab
- Configuration options:
  - Enable/disable auto-updates
  - Update check interval (hours)
  - Enable automatic pre-update snapshots
  - Number of snapshots to keep
  - Update channels (stable/testing)
  - Proxy settings
  - Download speed limits

### 1.9 Troubleshooting

#### Update Fails to Install
```bash
# Check disk space
df -h

# Check logs
tail -f /var/log/carrot-updates.log

# Manual rollback
sudo -c "from update_manager import UpdateManager; m = UpdateManager(); m.rollback_to_snapshot(snapshot_id)"
```

#### Snapshot Restore Issues
```bash
# Verify snapshot integrity
ls -la /var/lib/carrot-snapshots/

# Check available space
df -h

# Manual restoration from commands
```

#### Update Server Connection
```bash
# Test connectivity
ping repo.carrotos.org

# Check network configuration
ip route show

# Verify proxy settings in config.json
```

---

## Part 2: Hardware Driver Manager

### 2.1 Overview

The CarrotOS Driver Manager automatically detects hardware and manages driver installation for GPUs, audio devices, wireless adapters, and network interfaces.

**Key Features:**
- Automatic hardware detection via lspci/lsblk
- Support for major vendors (Intel, AMD, NVIDIA, Qualcomm, Broadcomm)
- One-click driver installation
- Driver status tracking
- Integration with APT package manager

### 2.2 Architecture

```
Driver Manager System:
├── Hardware Detection
│   ├── detect_gpu() - GPU detection
│   ├── detect_audio() - Audio device detection
│   ├── detect_wireless() - WiFi card detection
│   └── detect_ethernet() - Network adapter detection
├── Driver Database
│   ├── 13+ drivers pre-configured
│   ├── Version tracking
│   └── Kernel module mapping
├── Installation
│   ├── APT-based installation
│   ├── Module loading
│   └── Status verification
└── GUI Interface
    ├── carrot-driver-gui.py
    ├── 5 Tabs: GPU, Audio, Wireless, Ethernet, All
    └── Real-time detection and installation
```

### 2.3 Hardware Detection

#### Detection Methods

**GPU Detection (`detect_gpu()`)**
```
Input:  lspci output
Output: Detected GPU devices

Supported:
├── Intel i915 (3000+ series)
│   └── Drivers: intel-gpu-tools, kernel i915 module
├── AMD amdgpu (Radeon RX series)
│   └── Drivers: amdgpu-core, kernel amdgpu module
└── NVIDIA (520+ series)
    └── Drivers: nvidia-driver-520, kernel nvidia module
```

**Audio Detection (`detect_audio()`)**
```
Input:  lspci output
Output: Detected audio devices

Supported:
├── ALSA (Advanced Linux Sound Architecture)
│   └── snd_hda_intel, snd_usb_audio
├── PulseAudio Daemon
│   └── Userspace audio server
└── Advanced audio codecs
```

**Wireless Detection (`detect_wireless()`)**
```
Input:  lspci output, ip link show
Output: Detected wireless adapters

Supported:
├── Intel WiFi (iwlwifi)
│   ├── Devices: AC, AX, BE series
│   └── Firmware: iwlwifi-*.ucode
├── Qualcomm Atheros (ath10k, ath11k)
│   ├── Devices: QCA, AR series
│   └── Firmware: ath10k-cal-*.bin
└── Broadcomm (brcmfmac, brcmsmac)
    ├── Devices: BCM series
    └── Firmware: brcmfmac-*.bin
```

**Ethernet Detection (`detect_ethernet()`)**
```
Input:  lsblk, ip link show
Output: Network adapters

Supported:
├── Intel e1000 (1000base-T)
├── Realtek r8169 (Gigabit)
└── VirtIO virtio_net (Virtual machines)
```

### 2.4 Supported Drivers

| Driver | Type | Package | Kernel Modules | Devices |
|--------|------|---------|-----------------|---------|
| Intel GPU | GPU | intel-gpu-tools | i915, i810.drm | External displays |
| AMD GPU | GPU | amdgpu-core | amdgpu, amd_iommu_v2 | HDMI outputs |
| NVIDIA | GPU | nvidia-driver-520 | nvidia, nvidia_uvm | 520+ series |
| ALSA | Audio | alsa-utils | snd_hda_intel, snd_usb_audio | HDA, USB |
| PulseAudio | Audio | pulseaudio | (userspace daemon) | Audio routing |
| Intel WiFi | Wireless | firmware-iwlwifi | iwlwifi, cfg80211 | Intel NICs |
| Atheros | Wireless | firmware-atheros | ath10k_core, ath11k | Qualcomm NICs |
| Broadcomm | Wireless | firmware-brcm80211 | brcmfmac, brcmsmac | BCM NICs |
| Ethernet | Ethernet | linux-image | e1000, r8169, virtio_net | All Ethernet |

### 2.5 Installation

```bash
# Driver Manager is pre-installed at:
/tools/driver_manager.py

# GUI is available at:
/apps/driver-manager/carrot-driver-gui.py

# To launch GUI:
sudo carrot-driver-gui
```

### 2.6 Command-Line Usage

#### Detect Hardware
```python
from driver_manager import DriverManager, DriverType

manager = DriverManager()

# Detect all hardware
all_drivers = manager.detect_drivers()

# Get drivers by type
gpu_drivers = manager.get_drivers_by_type(DriverType.GPU)
audio_drivers = manager.get_drivers_by_type(DriverType.AUDIO)

# Get drivers needing installation
missing = manager.get_drivers_needing_installation()
```

#### Install Drivers
```python
# Install single driver
manager.install_driver(gpu_driver)

# Install all missing drivers
installed, failed = manager.install_all_missing()
print(f"Installed: {installed}, Failed: {failed}")
```

#### Check Driver Status
```python
for driver in manager.drivers:
    status = manager.get_driver_status(driver.device_id)
    print(f"{driver.name}: {status}")
```

### 2.7 Driver Manager GUI

**Launch**: `sudo carrot-driver-gui`

#### Tabs Overview

**GPU Drivers Tab**
- Lists detected GPUs:
  - Driver name
  - Device (GPU model)
  - Installation status
  - Package name
- Features:
  - One-click installation
  - View technical details
  - Version information

**Audio Tab**
- Audio device drivers
- ALSA and PulseAudio status
- Codec support
- Installation options

**Wireless Tab**
- WiFi adapter detection
- Driver and firmware status
- Connection support info
- Installation capability

**Ethernet Tab**
- Network adapter drivers
- Connection status
- Speed/duplex info
- Installation controls

**All Drivers Tab**
- Complete driver inventory
- Filter by type
- Global installation options
- Comprehensive status view

#### Installation Workflow

```
1. User opens Driver Manager
2. System scans hardware (lspci, lsblk)
3. Matches against driver database
4. Shows installation status:
   - ✓ INSTALLED (green)
   - ⚠ AVAILABLE (yellow)
   - ✗ NOT_NEEDED (gray)
   - ✗ FAILED (red)
5. User selects drivers to install
6. Click "Install Selected" or "Install All"
7. System:
   - Checks dependencies
   - Downloads packages via APT
   - Loads kernel modules
   - Verifies installation
   - Updates status display
```

### 2.8 Troubleshooting

#### GPU Not Detected
```bash
# List all PCI devices
lspci | grep -i vga

# Check for driver
modinfo i915  # Intel
modinfo amdgpu  # AMD
modinfo nvidia  # NVIDIA

# Load module manually
sudo modprobe i915
sudo modprobe amdgpu
sudo modprobe nvidia
```

#### WiFi Not Working
```bash
# Check wireless devices
ip link show
iw dev
iwconfig

# Check loaded modules
lsmod | grep iwlwifi  # Intel
lsmod | grep ath10k   # Atheros
lsmod | grep brcmfmac # Broadcomm

# Reload driver
sudo modprobe -r wl
sudo modprobe wl
```

#### Audio Issues
```bash
# Check audio devices
arecord -l  # Recording devices
aplay -l    # Playback devices

# Check ALSA modules
arecord -L

# Check PulseAudio
pactl list short devices

# Restart audio service
sudo systemctl restart alsa-utils
sudo systemctl restart pulseaudio
```

#### Ethernet Not Connected
```bash
# Check network interfaces
ip link show
ethtool eth0  # Show status

# Check loaded drivers
lsmod | grep e1000
lsmod | grep r8169
lsmod | grep virtio_net

# Restart networking
sudo systemctl restart networking
sudo ip link set eth0 up
```

---

## Part 3: Software Center Integration

### 3.1 Update & Driver Integration

The Software Center app integrates with both:

**In Settings Tab:**
- Check for system updates button links to Update Center
- Check for driver updates button links to Driver Manager
- Shows notification when updates available

**In Home View:**
- "System Updates" widget
- "Driver Status" widget
- Quick status indicators

### 3.2 Automatic Update Notifications

```
1. Every 24 hours (configurable):
   - Check for updates
   - Check for driver updates
   
2. If available:
   - Show desktop notification
   - Log in journalctl
   - Display in Software Center

3. User can:
   - Dismiss notification
   - Update now (opens Update Center)
   - Snooze until tomorrow
```

---

## Part 4: System Recovery

### 4.1 Recovery Procedures

#### Boot Into Recovery Mode
```
1. GRUB boot menu (press ESC at boot)
2. Select "Recovery Mode" option
3. System boots with:
   - Minimal services
   - Read-write /
   - Access to all tools
```

#### Manual Snapshot Restoration

```bash
# List available snapshots
ls /var/lib/carrot-snapshots/

# View snapshot details
cat /var/lib/carrot-snapshots/{id}/metadata.json

# Mount snapshot (read-only)
mount -o loop /var/lib/carrot-snapshots/{id}/root.tar.gz /mnt

# Restore from snapshot
cd /var/lib/carrot-snapshots/{id}/
tar xzf etc.tar.gz -C /
tar xzf var-lib.tar.gz -C /
tar xzf usr-local.tar.gz -C /
```

### 4.2 Emergency Recovery

**If system fails to boot:**
```
1. Boot from Live USB
2. Mount root filesystem
3. Run carrot-recovery tool
4. Select snapshot to restore
5. Reboot into restored system
```

---

## Part 5: Maintenance Schedule

### Recommended Schedule

**Daily:**
- Check /var/log/carrot-updates.log
- Monitor disk space

**Weekly:**
- Check for security updates
- Verify backup snapshots

**Monthly:**
- Full system backup
- Review driver status
- Update driver database

**Quarterly:**
- Major version updates
- Security audit
- Performance optimization

---

## Part 6: Performance Monitoring

### Update System Impact
- Update download: ~50-200 MB (varies)
- Installation time: 5-30 minutes
- Snapshot creation: 2-5 minutes (first time), 30-60 seconds (incremental)
- Rollback time: 5-15 minutes

### Driver Installation Impact
- Driver download: 50-500 MB
- Installation: 2-10 minutes
- Module loading: Immediate after reboot
- System performance: Minimal impact

---

## Part 7: Security Considerations

### Update Security
- All updates verified with checksums
- Updates signed by development team
- Secure channels (HTTPS)
- Rollback capability protects against malicious updates

### Driver Security
- Drivers from official repositories only
- Kernel module signature verification
- SELinux/AppArmor policies for drivers
- Regular security audits

### Best Practices
```
✓ Enable automatic security updates
✓ Keep snapshots for 30 days minimum
✓ Test updates in non-critical systems first
✓ Maintain recent backup snapshots
✓ Monitor update logs regularly
✓ Keep driver database updated
```

---

## Part 8: Advanced Configuration

### Update Server Configuration
```json
{
  "servers": [
    {"url": "https://updates.carrotos.org", "priority": 1},
    {"url": "https://mirror1.carrotos.org", "priority": 2},
    {"url": "https://mirror2.carrotos.org", "priority": 3}
  ]
}
```

### Driver Installation Preferences
```json
{
  "gpu_prefer": "proprietary",  // "proprietary" or "open-source"
  "audio_backend": "pulseaudio",  // "alsa" or "pulseaudio"
  "wireless_firmware": "all",    // Install all or preferred
  "auto_install_missing": false
}
```

---

## Summary

CarrotOS provides enterprise-grade system maintenance:
- **Updates**: Automatic with snapshot-based rollback
- **Drivers**: Auto-detection with one-click installation
- **Integration**: Seamless with Software Center
- **Recovery**: Multiple fallback options
- **Security**: Verified updates and drivers

This ensures system stability, hardware compatibility, and long-term maintainability.
