#!/usr/bin/env python3
"""
CarrotOS Hardware Driver Manager - Detect and manage hardware drivers
Handles GPU, audio, wireless, and other hardware drivers
"""

import os
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class DriverType(Enum):
    """Driver types"""
    GPU = "gpu"
    AUDIO = "audio"
    WIRELESS = "wireless"
    ETHERNET = "ethernet"
    CHIPSET = "chipset"
    OTHER = "other"

class DriverStatus(Enum):
    """Driver status"""
    INSTALLED = "installed"
    AVAILABLE = "available"
    NOT_NEEDED = "not_needed"
    FAILED = "failed"

@dataclass
class Driver:
    """Driver information"""
    name: str
    driver_type: DriverType
    device_name: str
    device_id: str
    vendor: str
    status: DriverStatus
    installed_version: Optional[str] = None
    available_version: Optional[str] = None
    package_name: Optional[str] = None

class HardwareDetector:
    """Detect hardware components"""
    
    def __init__(self):
        self.drivers: List[Driver] = []
    
    def detect_gpu(self) -> List[Tuple[str, str, str]]:
        """Detect GPU hardware"""
        gpus = []
        
        try:
            # Try lspci
            result = subprocess.run(['lspci', '-v'], capture_output=True, text=True)
            
            # Intel GPU
            if 'Intel' in result.stdout and ('Graphics' in result.stdout or 'VGA' in result.stdout):
                match = re.search(r'Intel.*?(UHD|Iris|Arc|HD Graphics.*?)[\n,]', result.stdout)
                if match:
                    gpus.append(('Intel', match.group(1).strip(), 'intel'))
            
            # AMD GPU
            if 'AMD' in result.stdout or 'Radeon' in result.stdout:
                match = re.search(r'(Radeon.*?)[\n,]', result.stdout)
                if match:
                    gpus.append(('AMD', match.group(1).strip(), 'amd'))
            
            # NVIDIA GPU
            if 'NVIDIA' in result.stdout:
                match = re.search(r'NVIDIA.*?(GeForce.*?)[\n,]', result.stdout)
                if match:
                    gpus.append(('NVIDIA', match.group(1).strip(), 'nvidia'))
        
        except:
            pass
        
        return gpus
    
    def detect_audio(self) -> List[Tuple[str, str]]:
        """Detect audio hardware"""
        audio_devices = []
        
        try:
            result = subprocess.run(['lspci', '-v'], capture_output=True, text=True)
            
            if 'Audio device' in result.stdout:
                match = re.search(r'Audio device:.*?([A-Za-z0-9\-]+)', result.stdout)
                if match:
                    audio_devices.append((match.group(1).strip(), 'generic_audio'))
        
        except:
            pass
        
        # Try ALSA
        try:
            result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                audio_devices.append(('ALSA Audio', 'alsa'))
        except:
            pass
        
        return audio_devices
    
    def detect_wireless(self) -> List[Tuple[str, str, str]]:
        """Detect wireless hardware"""
        wireless = []
        
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            
            # Qualcomm/Atheros
            if 'Qualcomm' in result.stdout or 'Atheros' in result.stdout:
                match = re.search(r'Qualcomm.*?(AR.*?)[\n$]', result.stdout)
                if match:
                    wireless.append(('Qualcomm Atheros', match.group(1).strip(), 'ath'))
            
            # Intel
            if 'Intel' in result.stdout and 'Wireless' in result.stdout:
                match = re.search(r'Intel.*?(Wi-Fi|Wireless|AX.*?)[\n$]', result.stdout)
                if match:
                    wireless.append(('Intel', match.group(1).strip(), 'intel_wifi'))
            
            # Broadcom
            if 'Broadcom' in result.stdout:
                match = re.search(r'Broadcom.*?([A-Z0-9]+)[\n$]', result.stdout)
                if match:
                    wireless.append(('Broadcom', match.group(1).strip(), 'bcm'))
        
        except:
            pass
        
        return wireless
    
    def detect_ethernet(self) -> List[Tuple[str, str]]:
        """Detect ethernet hardware"""
        ethernet = []
        
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            
            # Look for ethernet interfaces
            for line in result.stdout.split('\n'):
                if 'eth' in line or 'eno' in line or 'enp' in line:
                    match = re.search(r'(\d+):\s*([\w]+):', line)
                    if match:
                        ethernet.append((match.group(2), 'generic_ethernet'))
        
        except:
            pass
        
        return ethernet
    
    def detect_all_hardware(self) -> Dict[str, list]:
        """Detect all hardware"""
        return {
            'gpu': self.detect_gpu(),
            'audio': self.detect_audio(),
            'wireless': self.detect_wireless(),
            'ethernet': self.detect_ethernet(),
        }

class DriverManager:
    """Manage system drivers"""
    
    DRIVER_DATABASE = {
        # GPU Drivers
        'intel': {
            'type': DriverType.GPU,
            'package': 'intel-gpu-tools',
            'description': 'Intel GPU drivers',
            'modules': ['i915', 'i810.drm'],
            'version': '1.1.1',
        },
        'amd': {
            'type': DriverType.GPU,
            'package': 'amdgpu-core',
            'description': 'AMD GPU drivers (AMDGPU)',
            'modules': ['amdgpu', 'amd_iommu_v2'],
            'version': '1.2.0',
        },
        'nvidia': {
            'type': DriverType.GPU,
            'package': 'nvidia-driver-520',
            'description': 'NVIDIA GPU drivers',
            'modules': ['nvidia', 'nvidia_uvm'],
            'version': '520.56.06',
        },
        # Audio Drivers
        'alsa': {
            'type': DriverType.AUDIO,
            'package': 'alsa-utils',
            'description': 'Advanced Linux Sound Architecture',
            'modules': ['snd_hda_intel', 'snd_usb_audio'],
            'version': '1.2.7',
        },
        'pulseaudio': {
            'type': DriverType.AUDIO,
            'package': 'pulseaudio',
            'description': 'PulseAudio sound server',
            'modules': [],
            'version': '16.0',
        },
        # Wireless Drivers
        'intel_wifi': {
            'type': DriverType.WIRELESS,
            'package': 'firmware-iwlwifi',
            'description': 'Intel WiFi firmware',
            'modules': ['iwlwifi', 'cfg80211'],
            'version': '20230310',
        },
        'ath': {
            'type': DriverType.WIRELESS,
            'package': 'firmware-atheros',
            'description': 'Atheros WiFi firmware',
            'modules': ['ath10k_core', 'ath11k'],
            'version': '20230315',
        },
        'bcm': {
            'type': DriverType.WIRELESS,
            'package': 'firmware-brcm80211',
            'description': 'Broadcom WiFi firmware',
            'modules': ['brcmfmac', 'brcmsmac'],
            'version': '20230310',
        },
        # Ethernet
        'generic_ethernet': {
            'type': DriverType.ETHERNET,
            'package': 'linux-image',
            'description': 'Generic Ethernet driver',
            'modules': ['e1000', 'r8169', 'virtio_net'],
            'version': '5.15.0',
        },
    }
    
    def __init__(self):
        self.detector = HardwareDetector()
        self.drivers: List[Driver] = []
        self.detect_drivers()
    
    def detect_drivers(self):
        """Detect and initialize drivers"""
        hardware = self.detector.detect_all_hardware()
        
        self.drivers = []
        
        # GPU drivers
        for vendor, device, driver_id in hardware['gpu']:
            self.drivers.append(Driver(
                name=f"{vendor} GPU",
                driver_type=DriverType.GPU,
                device_name=device,
                device_id=driver_id,
                vendor=vendor,
                status=self.get_driver_status(driver_id),
                package_name=self.DRIVER_DATABASE.get(driver_id, {}).get('package')
            ))
        
        # Audio drivers
        for device, driver_id in hardware['audio']:
            self.drivers.append(Driver(
                name=f"Audio ({device})",
                driver_type=DriverType.AUDIO,
                device_name=device,
                device_id=driver_id,
                vendor="Generic",
                status=self.get_driver_status(driver_id),
                package_name=self.DRIVER_DATABASE.get(driver_id, {}).get('package')
            ))
        
        # Wireless drivers
        for vendor, device, driver_id in hardware['wireless']:
            self.drivers.append(Driver(
                name=f"{vendor} WiFi",
                driver_type=DriverType.WIRELESS,
                device_name=device,
                device_id=driver_id,
                vendor=vendor,
                status=self.get_driver_status(driver_id),
                package_name=self.DRIVER_DATABASE.get(driver_id, {}).get('package')
            ))
        
        # Ethernet drivers
        for device, driver_id in hardware['ethernet']:
            self.drivers.append(Driver(
                name=f"Ethernet ({device})",
                driver_type=DriverType.ETHERNET,
                device_name=device,
                device_id=driver_id,
                vendor="Generic",
                status=self.get_driver_status(driver_id),
                package_name=self.DRIVER_DATABASE.get(driver_id, {}).get('package')
            ))
    
    def get_driver_status(self, driver_id: str) -> DriverStatus:
        """Get driver status"""
        # Check if driver is loaded
        try:
            driver_info = self.DRIVER_DATABASE.get(driver_id, {})
            modules = driver_info.get('modules', [])
            
            for module in modules:
                try:
                    result = subprocess.run(
                        ['modinfo', module],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return DriverStatus.INSTALLED
                except:
                    pass
        except:
            pass
        
        return DriverStatus.AVAILABLE
    
    def install_driver(self, driver: Driver) -> bool:
        """Install driver"""
        if not driver.package_name:
            return False
        
        try:
            # Update package lists
            subprocess.run(['apt-get', 'update', '-q'], timeout=30)
            
            # Install package
            result = subprocess.run([
                'apt-get', 'install', '-y', driver.package_name
            ], timeout=300)
            
            if result.returncode == 0:
                # Update driver status
                driver.status = DriverStatus.INSTALLED
                driver.installed_version = self.DRIVER_DATABASE[driver.device_id]['version']
                return True
        except:
            pass
        
        return False
    
    def get_drivers_by_type(self, driver_type: DriverType) -> List[Driver]:
        """Get drivers by type"""
        return [d for d in self.drivers if d.driver_type == driver_type]
    
    def get_drivers_needing_installation(self) -> List[Driver]:
        """Get drivers that need installation"""
        return [d for d in self.drivers if d.status != DriverStatus.INSTALLED]
    
    def get_driver_info(self, driver_id: str) -> Dict:
        """Get driver information"""
        return self.DRIVER_DATABASE.get(driver_id, {})
    
    def install_all_missing(self) -> Tuple[int, int]:
        """Install all missing drivers"""
        to_install = self.get_drivers_needing_installation()
        installed = 0
        failed = 0
        
        for driver in to_install:
            if self.install_driver(driver):
                installed += 1
            else:
                failed += 1
        
        return installed, failed

def main():
    """Test driver manager"""
    print("CarrotOS Hardware Driver Manager")
    print("================================\n")
    
    manager = DriverManager()
    
    print(f"Detected {len(manager.drivers)} drivers:\n")
    
    for driver in manager.drivers:
        status_icon = "✓" if driver.status == DriverStatus.INSTALLED else "✗"
        print(f"  [{status_icon}] {driver.name}")
        print(f"      Type: {driver.driver_type.value}")
        print(f"      Status: {driver.status.value}")
        print(f"      Package: {driver.package_name}")
        print()

if __name__ == '__main__':
    main()
