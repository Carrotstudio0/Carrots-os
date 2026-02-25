#!/usr/bin/env python3
"""
CarrotOS Network Manager - Network configuration and management
Handles network interfaces, DNS, DHCP, WiFi, and firewall configuration
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import os

@dataclass
class NetworkInterface:
    """Network interface information"""
    name: str
    ip_address: str = ""
    netmask: str = ""
    gateway: str = ""
    dns_servers: List[str] = None
    mac_address: str = ""
    mtu: int = 1500
    enabled: bool = True

class NetworkManager:
    """Manage system networking"""
    
    ETC_NETWORK = Path("/etc/network")
    INTERFACES_FILE = ETC_NETWORK / "interfaces"
    SYSTEMD_NETWORK = Path("/etc/systemd/network")
    RESOLV_CONF = Path("/etc/resolv.conf")
    CONFIG_DIR = Path("/etc/carrot-network")
    
    def __init__(self):
        self.interfaces: Dict[str, NetworkInterface] = {}
        self.config_dir = self.CONFIG_DIR
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.load_interfaces()
    
    def check_root(self) -> bool:
        """Check if running as root"""
        return os.geteuid() == 0
    
    def load_interfaces(self):
        """Load network interfaces"""
        try:
            result = subprocess.run(
                ["ip", "link", "show"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ':' in line and not line.startswith(' '):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            iface_name = parts[1].strip()
                            if iface_name and iface_name != 'lo':
                                self.interfaces[iface_name] = NetworkInterface(
                                    name=iface_name
                                )
        except Exception as e:
            print(f"Warning: Could not load interfaces: {e}")
    
    def get_interface_ip(self, interface: str) -> Optional[str]:
        """Get IP address for interface"""
        try:
            result = subprocess.run(
                ["ip", "addr", "show", interface],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'inet ' in line:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            return parts[1].split('/')[0]
        except:
            pass
        
        return None
    
    def set_static_ip(self, interface: str, ip: str, netmask: str, 
                     gateway: str, dns: List[str] = None) -> bool:
        """Configure static IP address"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        try:
            # Create netplan config
            netplan_dir = Path("/etc/netplan")
            netplan_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = netplan_dir / f"{interface}.yaml"
            
            dns_list = dns or ["1.1.1.1", "8.8.8.8"]
            
            config = f"""network:
  version: 2
  ethernets:
    {interface}:
      dhcp4: no
      dhcp6: no
      addresses:
        - {ip}/{self._cidr_from_netmask(netmask)}
      gateway4: {gateway}
      nameservers:
        addresses: {dns_list}
"""
            
            config_file.write_text(config)
            
            # Apply netplan
            subprocess.run(["netplan", "apply"], check=False)
            
            print(f"✓ Static IP configured: {interface}")
            return True
        
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def set_dhcp(self, interface: str) -> bool:
        """Enable DHCP for interface"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        try:
            netplan_dir = Path("/etc/netplan")
            netplan_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = netplan_dir / f"{interface}.yaml"
            
            config = f"""network:
  version: 2
  ethernets:
    {interface}:
      dhcp4: true
      dhcp6: true
"""
            
            config_file.write_text(config)
            subprocess.run(["netplan", "apply"], check=False)
            
            print(f"✓ DHCP enabled: {interface}")
            return True
        
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def set_dns(self, dns_servers: List[str]) -> bool:
        """Set DNS servers"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        try:
            config_dir = Path("/etc/systemd/resolved.conf.d")
            config_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = config_dir / "carrot.conf"
            
            dns_str = " ".join(dns_servers)
            
            config = f"""[Resolve]
DNS={dns_str}
FallbackDNS=1.1.1.1 8.8.8.8
"""
            
            config_file.write_text(config)
            
            # Restart systemd-resolved
            subprocess.run(
                ["systemctl", "restart", "systemd-resolved"],
                check=False
            )
            
            print(f"✓ DNS configured: {dns_servers}")
            return True
        
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def enable_wifi(self, ssid: str, password: str) -> bool:
        """Connect to WiFi network"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        try:
            # Create wpa_supplicant config
            wpa_dir = Path("/etc/wpa_supplicant")
            wpa_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = wpa_dir / "wpa_supplicant.conf"
            
            config = f"""ctrl_interface=/run/wpa_supplicant
network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
"""
            
            config_file.write_text(config)
            
            print(f"✓ WiFi network configured: {ssid}")
            return True
        
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def enable_firewall(self) -> bool:
        """Enable UFW firewall"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        try:
            subprocess.run(["ufw", "enable"], check=False)
            subprocess.run(["ufw", "default", "deny", "incoming"], check=False)
            subprocess.run(["ufw", "default", "allow", "outgoing"], check=False)
            
            print("✓ Firewall enabled")
            return True
        
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def allow_port(self, port: int, protocol: str = "tcp") -> bool:
        """Allow port through firewall"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        try:
            subprocess.run(
                ["ufw", "allow", f"{port}/{protocol}"],
                check=False
            )
            
            print(f"✓ Port allowed: {port}/{protocol}")
            return True
        
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def list_interfaces(self) -> List[str]:
        """Get all network interfaces"""
        return list(self.interfaces.keys())
    
    def get_interface_info(self, interface: str) -> Optional[NetworkInterface]:
        """Get interface information"""
        return self.interfaces.get(interface)
    
    @staticmethod
    def _cidr_from_netmask(netmask: str) -> int:
        """Convert netmask to CIDR notation"""
        try:
            parts = netmask.split('.')
            binary = ''.join([bin(int(p))[2:].zfill(8) for p in parts])
            return binary.count('1')
        except:
            return 24

if __name__ == "__main__":
    nm = NetworkManager()
    print("Network interfaces:", nm.list_interfaces())
