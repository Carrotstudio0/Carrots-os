#!/usr/bin/env python3
"""
CarrotOS Power Manager - System power and performance management
Handles: Power profiles, CPU frequency scaling, battery management
"""

import subprocess
from pathlib import Path
from typing import Dict, List
from enum import Enum
import json

class PowerProfile(Enum):
    """Power profile modes"""
    PERFORMANCE = "performance"
    BALANCED = "balanced"
    POWER_SAVER = "power_saver"
    CUSTOM = "custom"

class PowerManager:
    """Manage system power"""
    
    CONFIG_DIR = Path("/etc/carrot-power")
    STATE_FILE = Path("/var/lib/carrot-power/state.json")
    
    def __init__(self):
        self.current_profile = PowerProfile.BALANCED
        self.load_config()
    
    def load_config(self):
        """Load power configuration"""
        if self.STATE_FILE.exists():
            try:
                data = json.loads(self.STATE_FILE.read_text())
                profile_name = data.get('profile', 'balanced')
                self.current_profile = PowerProfile[profile_name.upper()]
            except:
                self.current_profile = PowerProfile.BALANCED
    
    def save_config(self):
        """Save power configuration"""
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'profile': self.current_profile.value,
        }
        
        self.STATE_FILE.write_text(json.dumps(data, indent=2))
    
    def set_profile(self, profile: PowerProfile) -> bool:
        """Set power profile"""
        print(f"Setting power profile: {profile.value}")
        
        try:
            if profile == PowerProfile.PERFORMANCE:
                self.apply_performance_profile()
            elif profile == PowerProfile.BALANCED:
                self.apply_balanced_profile()
            elif profile == PowerProfile.POWER_SAVER:
                self.apply_power_saver_profile()
            
            self.current_profile = profile
            self.save_config()
            return True
        except Exception as e:
            print(f"Error setting profile: {e}")
            return False
    
    def apply_performance_profile(self):
        """Apply performance profile"""
        # Max CPU frequency
        self.set_cpu_frequency("turbo")
        
        # Disable power saving features
        self.set_screen_brightness(100)
        
        print("Performance profile applied")
    
    def apply_balanced_profile(self):
        """Apply balanced profile"""
        # Normal CPU frequency
        self.set_cpu_frequency("normal")
        
        # Normal screen brightness
        self.set_screen_brightness(75)
        
        print("Balanced profile applied")
    
    def apply_power_saver_profile(self):
        """Apply power saver profile"""
        # Low CPU frequency
        self.set_cpu_frequency("powersave")
        
        # Reduced screen brightness
        self.set_screen_brightness(40)
        
        # Sleep after 5 minutes
        self.set_sleep_delay(300)
        
        print("Power saver profile applied")
    
    def set_cpu_frequency(self, mode: str) -> bool:
        """Set CPU frequency scaling"""
        try:
            # Use cpupower if available
            if mode == "turbo":
                driver = "performance"
            elif mode == "powersave":
                driver = "powersave"
            else:
                driver = "schedutil"
            
            # Set governor for all CPUs
            result = subprocess.run(
                ['cpupower', 'frequency-set', '-g', driver],
                capture_output=True,
                timeout=10
            )
            
            return result.returncode == 0
        except:
            return False
    
    def get_cpu_frequency(self) -> Dict[str, str]:
        """Get current CPU frequency"""
        try:
            result = subprocess.run(
                ['cpupower', 'frequency-info'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            frequencies = {}
            for line in result.stdout.split('\n'):
                if 'current CPU frequency' in line:
                    frequencies['current'] = line.split(':')[-1].strip()
                elif 'CPUs which run at the same frequency' in line:
                    frequencies['governor'] = line.split(':')[-1].strip()
            
            return frequencies
        except:
            return {}
    
    def set_screen_brightness(self, percentage: int) -> bool:
        """Set screen brightness"""
        try:
            # Use brightnessctl if available
            result = subprocess.run(
                ['brightnessctl', 'set', f'{percentage}%'],
                capture_output=True,
                timeout=10
            )
            
            return result.returncode == 0
        except:
            # Try xrandr as fallback
            try:
                percentage_float = percentage / 100.0
                result = subprocess.run(
                    ['xrandr', '--output', 'HDMI-1', '--brightness', str(percentage_float)],
                    capture_output=True,
                    timeout=10
                )
                return result.returncode == 0
            except:
                return False
    
    def get_screen_brightness(self) -> int:
        """Get current screen brightness"""
        try:
            result = subprocess.run(
                ['brightnessctl', 'get'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            current = int(result.stdout.strip())
            
            # Get max
            result = subprocess.run(
                ['brightnessctl', 'max'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            max_val = int(result.stdout.strip())
            
            return int((current / max_val) * 100)
        except:
            return 50
    
    def set_sleep_delay(self, seconds: int) -> bool:
        """Set sleep/suspend delay"""
        try:
            # Use systemd to set idle delay
            config_dir = Path("/etc/systemd/sleep.conf.d")
            config_dir.mkdir(parents=True, exist_ok=True)
            
            sleep_time = seconds // 60  # Convert to minutes
            
            config_content = f"""[Sleep]
SuspendState=mem
HibernateDelay={sleep_time}m
SuspendMode=mem
"""
            
            (config_dir / "carrot-suspend.conf").write_text(config_content)
            
            # Reload systemd
            subprocess.run(['systemctl', 'daemon-reload'], capture_output=True)
            
            return True
        except:
            return False
    
    def enable_power_saving_features(self) -> bool:
        """Enable power saving features"""
        try:
            # Disable USB autosuspend
            features = {
                '/sys/module/i915/parameters/enable_fbc': '1',  # Intel: Enable frame buffer compression
                '/proc/sys/kernel/sched_migration_cost_ns': '5000000',  # Reduce context switching
                '/sys/module/i915/parameters/enable_psr': '1',  # Panel Self Refresh
            }
            
            for path, value in features.items():
                p = Path(path)
                if p.exists():
                    try:
                        p.write_text(value)
                    except:
                        pass
            
            return True
        except:
            return False
    
    def get_battery_info(self) -> Dict[str, str]:
        """Get battery information"""
        try:
            result = subprocess.run(
                ['upower', '-i', '/org/freedesktop/UPower/devices/battery_BAT0'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            battery_info = {}
            for line in result.stdout.split('\n'):
                if 'percentage' in line.lower():
                    battery_info['percentage'] = line.split(':')[-1].strip()
                elif 'state' in line.lower():
                    battery_info['state'] = line.split(':')[-1].strip()
                elif 'time to empty' in line.lower():
                    battery_info['time_remaining'] = line.split(':')[-1].strip()
            
            return battery_info
        except:
            return {}
    
    def get_thermal_info(self) -> Dict[str, str]:
        """Get thermal information"""
        try:
            result = subprocess.run(
                ['sensors'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            thermals = {}
            for line in result.stdout.split('\n'):
                if '°C' in line:
                    parts = line.split('°C')[0].split()
                    if len(parts) >= 2:
                        label = parts[0]
                        value = parts[-1]
                        thermals[label] = value
            
            return thermals
        except:
            return {}
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        return {
            'profile': self.current_profile.value,
            'brightness': self.get_screen_brightness(),
            'cpu_frequency': self.get_cpu_frequency(),
            'battery': self.get_battery_info(),
            'thermal': self.get_thermal_info(),
        }

def main():
    """Test power manager"""
    manager = PowerManager()
    
    print(f"Current profile: {manager.current_profile.value}")
    
    # Get system stats
    stats = manager.get_system_stats()
    print(f"System stats: {json.dumps(stats, indent=2)}")
    
    # Set balanced profile
    manager.set_profile(PowerProfile.BALANCED)

if __name__ == '__main__':
    main()
