#!/usr/bin/env python3
"""
CarrotOS Network Daemon
Simple network configuration and management
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[networkd] %(message)s')
logger = logging.getLogger(__name__)

class NetworkDaemon:
    """Simple network manager for CarrotOS"""
    
    def __init__(self):
        self.config_dir = Path("/etc/carrot/network")
        self.state_dir = Path("/run/networkd")
        self.interfaces = []
    
    def init_directories(self):
        """Initialize network directories"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def discover_interfaces(self):
        """Discover network interfaces"""
        logger.info("Discovering network interfaces...")
        
        try:
            result = subprocess.run(
                ["ip", "link", "show"],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if ':' in line and not line.startswith(' '):
                    parts = line.split(':')
                    if len(parts) > 1:
                        iface_name = parts[1].strip()
                        if iface_name not in ['lo']:
                            self.interfaces.append(iface_name)
            
            logger.info(f"Found interfaces: {', '.join(self.interfaces)}")
        except Exception as e:
            logger.error(f"Failed to discover interfaces: {e}")
    
    def setup_loopback(self):
        """Setup loopback interface"""
        logger.info("Setting up loopback interface...")
        
        try:
            subprocess.run(["ip", "link", "set", "lo", "up"], check=True)
            subprocess.run(
                ["ip", "addr", "add", "127.0.0.1/8", "dev", "lo"],
                check=False  # May already exist
            )
            logger.info("Loopback configured")
        except Exception as e:
            logger.error(f"Loopback setup failed: {e}")
    
    def configure_dhcp(self, interface: str):
        """Configure interface with DHCP"""
        logger.info(f"Configuring {interface} with DHCP...")
        
        try:
            # Bring link up
            subprocess.run(["ip", "link", "set", interface, "up"], check=True)
            
            # Try DHCP
            if os.path.exists("/usr/sbin/dhclient"):
                subprocess.Popen(
                    ["dhclient", interface],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logger.info(f"DHCP started on {interface}")
            else:
                logger.warning("DHCP client not found")
        except Exception as e:
            logger.error(f"DHCP configuration failed: {e}")
    
    def update_dns(self):
        """Update DNS configuration"""
        logger.info("Updating DNS configuration...")
        
        resolv_conf = Path("/etc/resolv.conf")
        dns_config = """# CarrotOS Resolver Configuration
nameserver 1.1.1.1
nameserver 1.0.0.1
options edns0 trust-ad
"""
        try:
            resolv_conf.write_text(dns_config)
            logger.info("DNS configured")
        except Exception as e:
            logger.error(f"DNS update failed: {e}")
    
    def run(self):
        """Main daemon loop"""
        logger.info("CarrotOS Network Daemon starting...")
        
        self.init_directories()
        self.discover_interfaces()
        self.setup_loopback()
        self.update_dns()
        
        # Configure each interface with DHCP
        for iface in self.interfaces:
            self.configure_dhcp(iface)
        
        logger.info("Network configuration complete")
        
        # Just keep running
        try:
            import time
            while True:
                time.sleep(60)
                # Could do periodic checks here
        except KeyboardInterrupt:
            logger.info("Shutdown")


def main():
    if os.getuid() != 0:
        print("Error: networkd must run as root")
        return 1
    
    daemon = NetworkDaemon()
    daemon.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
