# Carrot Control Center - System Management Dashboard

## Overview

**Carrot Control Center** is a professional, comprehensive system management dashboard that unifies control over all major system components including performance monitoring, power management, hardware drivers, system updates, and appearance settings.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│            Carrot Control Center                    │
├─────────────────────────────────────────────────────┤
│ Sidebar Navigation    │    Content Area             │
│                       │                             │
│ • Dashboard           │  System Metrics Display     │
│ • Performance         │  CPU, RAM, Disk            │
│ • Power               │  Network, Temp             │
│ • Updates             │                             │
│ • Drivers             │  Real-time Graphs          │
│ • Display             │  Process Monitor           │
│ • Sound               │                             │
│ • Network             │  Configuration Controls    │
│ • Appearance          │  Theme Switcher            │
│ • About               │  Brightness Slider         │
│                       │                             │
└─────────────────────────────────────────────────────┘
```

## Main Features

### 1. Dashboard
- **Real-time System Metrics**
  - CPU usage (%)
  - Memory usage (%)
  - Disk usage (%)
  - System temperature (°C)
  
- **System Information**
  - Hostname
  - OS name (CarrotOS)
  - Kernel version
  - Architecture
  - Python version

### 2. Performance Monitor
- **System Metrics**
  - Number of CPU cores
  - Running process count
  - System uptime (hours/minutes)
  
- **Top Processes Table**
  - PID
  - Process name
  - CPU usage percentage
  - Top 10 processes sorted by CPU

### 3. Power Management
- **Power Profiles**
  - **Performance**: Maximum CPU frequency, 100% brightness
  - **Balanced**: Normal CPU frequency, 75% brightness
  - **Power Saver**: Low frequency, 40% brightness, 5min sleep timeout

- **Brightness Control**
  - Slider: 10% - 100%
  - Real-time application

- **Battery Information**
  - Current charge percentage
  - Battery state (charging/discharging/full)
  - Time remaining

### 4. Updates Management
- **Automatic Update Checking**
  - System updates
  - Application updates
  - Security patches
  
- **Update History**
  - Available updates list
  - Update types and descriptions
  - Installation status

- **Rollback Capability**
  - Revert to previous system state
  - Snapshot management

### 5. Hardware Drivers
- **Driver Detection**
  - GPU (Intel/AMD/NVIDIA)
  - Audio devices (HDA/PulseAudio)
  - Network devices (Intel/Realtek/Broadcom)
  
- **Auto Installation**
  - Automatic driver detection
  - Firmware download
  - Package installation
  
- **Driver Status**
  - NOT_DETECTED
  - DETECTED
  - INSTALLED
  - NEEDS_UPDATE
  - FAILED

### 6. Display Settings
- BIOS/UEFI configuration reference
- Graphics driver settings

### 7. Sound Settings
- PulseAudio integration
- System volume control
- Audio device management

### 8. Network Settings
- Network interface information
- IP address display (IPv4/IPv6)
- Network configuration status

### 9. Appearance
- **Theme Switcher**
  - carrot-light: Light theme with dark text
  - carrot-dark: Dark theme with light text
  - carrot-system: Auto-switching based on time
  
- Real-time theme application

### 10. About
- Version information
- Feature list
- Project information

## User Interface Design

### Color Scheme
- **Primary Background**: #1e1e2e (Dark gray)
- **Secondary Background**: #2a2a3e (Darker gray)
- **Primary Text**: #ffffff (White)
- **Accent**: #ff8c00 (Orange)
- **Success**: #4caf50 (Green)
- **Warning**: #ff9800 (Yellow)
- **Error**: #f44336 (Red)

### Layout Structure
- **Header**: 60px height, orange accent, application title
- **Sidebar**: 200px width, navigation buttons
- **Content**: Responsive main area with scrollable content

## System Integration

### Dependencies
```python
from update_manager import UpdateManager
from power_manager import PowerManager, PowerProfile
from driver_manager import DriverManager
from theme_engine import ThemeManager
```

### Manager Classes
1. **UpdateManager** - System and application updates
2. **PowerManager** - Power profiles and CPU frequency
3. **DriverManager** - Hardware detection and driver management
4. **ThemeManager** - Theme selection and application

### Configuration Files
- `/etc/carrot-power/config.json` - Power settings
- `/etc/carrot-desktop/themes.conf` - Active theme
- `/var/lib/carrot-control-center` - State information
- `/var/cache/carrot-drivers` - Downloaded drivers

## Monitoring Features

### Real-time Updates
- CPU usage (every 2 seconds)
- Memory usage (every 2 seconds)
- Disk usage (every 2 seconds)
- System temperature (every 2 seconds)
- Process monitoring (top 10)

### Background Thread
- Non-blocking monitoring
- Smooth UI updates
- Graceful shutdown

## Installation & Launch

### Requirements
- Python 3.8+
- tkinter (usually included with Python)
- psutil library
- Root privileges (for power/driver management)

### Installation
```bash
sudo pip3 install psutil
sudo cp carrot-control-center.py /usr/bin/carrot-control-center
sudo chmod +x /usr/bin/carrot-control-center
```

### Launch
```bash
sudo carrot-control-center
```

### Desktop Integration
```ini
[Desktop Entry]
Type=Application
Name=Carrot Control Center
Exec=sudo carrot-control-center
Icon=carrot
Categories=System;Settings;
```

## Code Structure

### Main Class: CarrotControlCenter
```python
class CarrotControlCenter:
    # Initialization
    __init__(root)
    
    # UI Setup
    setup_ui()
    clear_content()
    create_info_box(parent, title, value, color)
    
    # View Methods
    show_dashboard()
    show_performance()
    show_power()
    show_updates()
    show_drivers()
    show_display()
    show_sound()
    show_network()
    show_appearance()
    show_about()
    
    # Action Methods
    check_updates()
    auto_install_drivers()
    
    # Monitoring
    start_monitoring()
    monitor_loop()
    on_closing()
```

## Usage Examples

### Check System Updates
1. Click "Updates" in sidebar
2. Click "Check for Updates" button
3. View available updates
4. Click "Install" to apply updates

### Change Power Profile
1. Click "Power" in sidebar
2. Select desired power profile (Performance/Balanced/Power Saver)
3. Changes apply immediately

### Install Missing Drivers
1. Click "Drivers" in sidebar
2. View detected devices
3. Click "Auto Install Missing Drivers"
4. System automatically downloads and installs drivers

### Change Theme
1. Click "Appearance" in sidebar
2. Select theme (carrot-light, carrot-dark, carrot-system)
3. Changes apply immediately

### Monitor System Performance
1. Dashboard shows real-time metrics
2. Performance tab shows top processes
3. Metrics update every 2 seconds

## Security Considerations

1. **Root Privileges Required**
   - Power management requires root
   - Driver installation requires root
   - System updates require root

2. **Authentication**
   - Control Center checks for root at startup
   - Denies access if not running as root

3. **Safe Operations**
   - Confirmation dialogs for destructive operations
   - Driver installation safety checks
   - Rollback capability for failed updates

## Performance Impact

- **CPU Usage**: < 2% when idle
- **Memory Usage**: ~50-80 MB
- **Update Frequency**: 2-second intervals
- **Thread Count**: 1 background monitoring thread

## Future Enhancements

1. **Advanced Features**
   - CPU temperature graphs
   - Network traffic graphs
   - Disk I/O statistics
   - Memory usage breakdown by process

2. **User Preferences**
   - Customizable theme colors
   - Adjustable monitoring interval
   - Startup behavior settings
   - Notification preferences

3. **System Integration**
   - System tray icon
   - Notifications for updates
   - Hardware degradation warnings
   - Performance optimization suggestions

4. **Mobile Support**
   - Web-based control panel
   - Remote monitoring capability
   - Smartphone integration

## Troubleshooting

### Control Center Won't Start
**Problem**: Permission denied
**Solution**: Run with sudo
```bash
sudo carrot-control-center
```

### Drivers Not Detecting
**Problem**: No devices found
**Solution**: 
1. Ensure lspci is installed: `sudo apt install pciutils`
2. Manually scan: Hardware > Rescan Devices

### Power Profile Not Applying
**Problem**: Changes don't persist
**Solution**:
1. Check cpupower installation: `sudo apt install linux-cpupower`
2. Verify /etc/carrot-power directory exists

### Updates Not Found
**Problem**: "System is up to date" when updates exist
**Solution**:
1. Update package cache: `sudo apt update`
2. Restart Control Center
3. Click "Check for Updates" again

## Integration with Other Systems

### With Installer
- Runs after first boot
- Configures detected hardware
- Applies user theme preferences

### With Update Manager
- Shows available updates
- Manages update installation
- Provides rollback option

### With Driver Manager
- Auto-detects hardware
- Lists installed drivers
- Installs missing drivers

### With Theme Engine
- Applies selected theme immediately
- Shows preview of themes
- Manages custom themes

### With Power Manager
- Controls power profiles
- Manages brightness
- Monitors battery status

## File Locations

```
/usr/bin/carrot-control-center          - Executable
/usr/share/applications/carrot-control-center.desktop - Desktop entry
/var/cache/carrot-control-center        - Cache directory
/var/lib/carrot-control-center          - State directory
/var/log/carrot-control-center.log      - Log file
```

## Version History

### Version 1.0 (Current)
- Initial release
- 10 major sections
- Real-time monitoring
- Integration with all major system managers
- Support for power profiles
- Driver auto-installation
- Theme switching
- Update management

## Contributing

To improve the Control Center:
1. Test all sections thoroughly
2. Report bugs with reproduction steps
3. Suggest UI improvements
4. Add new system monitoring features
5. Improve performance monitoring

## License

Part of the CarrotOS Project
Licensed under same terms as CarrotOS

## Support

For issues or questions:
- Check documentation: `/docs/CONTROL-CENTER.md`
- View logs: `/var/log/carrot-control-center.log`
- Report bugs: https://carrotos.dev/issues

---

**Last Updated**: 2026
**Maintainer**: CarrotOS Development Team
