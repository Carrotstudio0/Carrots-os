#!/usr/bin/env python3
"""
Installation backend for CarrotOS Installer
Handles system installation, configuration, and bootloader
"""

import subprocess
import os
import shutil
from pathlib import Path
from typing import Callable, Optional
import json

class InstallationBackend:
    """Main installation backend"""
    
    def __init__(self, target_mount: str = "/target", 
                 progress_callback: Optional[Callable] = None):
        self.target_mount = target_mount
        self.progress_callback = progress_callback or self._default_callback
        self.log_file = Path("/tmp/carrotos_install.log")
    
    def _default_callback(self, message: str, progress: int = 0):
        """Default progress callback"""
        print(f"[{progress}%] {message}")
    
    def log(self, message: str):
        """Log message"""
        self.log_file.write_text(self.log_file.read_text() + f"{message}\n", 'a')
        print(f"[LOG] {message}")
    
    def report_progress(self, message: str, progress: int):
        """Report progress"""
        self.progress_callback(message, progress)
        self.log(message)
    
    def setup_target(self):
        """Setup target installation directory"""
        self.report_progress("Setting up target system", 10)
        
        # Create directory structure
        dirs = [
            'bin', 'sbin', 'usr/bin', 'usr/sbin', 'usr/local/bin',
            'etc', 'var', 'var/log', 'var/lib', 'var/cache',
            'home', 'root', 'tmp', 'boot', 'dev', 'proc', 'sys',
            'opt', 'srv', 'media', 'mnt', 'run'
        ]
        
        for d in dirs:
            path = Path(self.target_mount) / d
            path.mkdir(parents=True, exist_ok=True)
            
            # Set permissions for sensitive directories
            if d in ['root', 'tmp']:
                path.chmod(0o700)
            elif d in ['var/log', 'var/cache']:
                path.chmod(0o755)
        
        self.report_progress("Target directory structure created", 15)
        return True
    
    def install_base_system(self):
        """Install base system files"""
        self.report_progress("Installing base system", 20)
        
        # Copy kernel files
        self.install_kernel()
        
        # Copy system files
        self.install_system_files()
        
        # Install package manager (carrot-pkg)
        self.install_package_manager()
        
        self.report_progress("Base system installed", 35)
        return True
    
    def install_kernel(self):
        """Install kernel"""
        try:
            self.log("Installing kernel...")
            
            # In real implementation, compile or copy prebuilt kernel
            boot_dir = Path(self.target_mount) / "boot"
            boot_dir.mkdir(exist_ok=True)
            
            # Create dummy kernel files for demo
            (boot_dir / "vmlinuz-5.15.0-carrotos").touch()
            (boot_dir / "initrd.img-5.15.0-carrotos").touch()
            
            return True
        except Exception as e:
            self.log(f"Error installing kernel: {e}")
            return False
    
    def install_system_files(self):
        """Install system configuration files"""
        try:
            self.log("Installing system files...")
            
            etc_files = {
                '/etc/os-release': """NAME="CarrotOS"
VERSION="1.0"
ID=carrotos
ID_LIKE=linux
VERSION_ID=1.0
PRETTY_NAME="CarrotOS 1.0"
HOME_URL="https://carrotos.dev"
""",
                '/etc/hostname': "",  # Will be set during user creation
                '/etc/timezone': "UTC",
                '/etc/shells': """/bin/bash
/bin/sh
/sbin/nologin
""",
            }
            
            for path, content in etc_files.items():
                target_path = Path(self.target_mount) / path.lstrip('/')
                target_path.parent.mkdir(parents=True, exist_ok=True)
                if content or not target_path.exists():
                    target_path.write_text(content)
            
            return True
        except Exception as e:
            self.log(f"Error installing system files: {e}")
            return False
    
    def install_package_manager(self):
        """Install package manager"""
        try:
            self.log("Installing package manager...")
            
            # Create carrot-pkg structure
            pkg_dirs = [
                '/etc/carrot-pkg',
                '/etc/carrot-pkg/repos.d',
                '/var/lib/carrot-pkg',
                '/var/lib/carrot-pkg/db',
                '/var/cache/carrot-pkg',
            ]
            
            for d in pkg_dirs:
                path = Path(self.target_mount) / d.lstrip('/')
                path.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            self.log(f"Error installing package manager: {e}")
            return False
    
    def install_gui_system(self):
        """Install GUI and desktop files"""
        self.report_progress("Installing GUI system", 40)
        
        try:
            # Create desktop directories
            desktop_dirs = [
                '/usr/share/applications',
                '/usr/share/pixmaps',
                '/usr/share/themes/carrot-default',
                '/usr/local/bin',
            ]
            
            for d in desktop_dirs:
                path = Path(self.target_mount) / d.lstrip('/')
                path.mkdir(parents=True, exist_ok=True)
            
            self.log("GUI system directories created")
            return True
        except Exception as e:
            self.log(f"Error installing GUI: {e}")
            return False
    
    def configure_bootloader(self, device: str, efi: bool = True):
        """Install and configure GRUB bootloader"""
        self.report_progress("Configuring bootloader", 50)
        
        try:
            boot_dir = Path(self.target_mount) / "boot"
            grub_cfg = boot_dir / "grub" / "grub.cfg"
            grub_cfg.parent.mkdir(parents=True, exist_ok=True)
            
            # Create basic GRUB configuration
            grub_config = """# CarrotOS GRUB Configuration
set default="0"
set timeout=5
set gfxmode=auto
set gfxpayload=keep

### BEGIN /etc/grub.d/10_linux###
menuentry 'CarrotOS GNU/Linux' {
    insmod gzio
    insmod part_gpt
    insmod ext2
    set root='hd0,gpt2'
    linux /vmlinuz-5.15.0-carrotos root=/dev/mapper/root ro quiet splash
    initrd /initrd.img-5.15.0-carrotos
}
### END /etc/grub.d/10_linux###
"""
            
            grub_cfg.write_text(grub_config)
            
            self.log(f"GRUB configured for device {device}")
            
            if efi:
                self.log("Setting up EFI boot")
                efi_dir = boot_dir / "EFI" / "carrotos"
                efi_dir.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            self.log(f"Error configuring bootloader: {e}")
            return False
    
    def setup_network(self):
        """Setup network configuration"""
        self.report_progress("Setting up network", 60)
        
        try:
            etc_dir = Path(self.target_mount) / "etc"
            
            # Network interfaces file
            interfaces = """# Network interfaces configuration
auto lo
iface lo inet loopback

# ethernet interface
auto eth0
iface eth0 inet dhcp
"""
            
            (etc_dir / "network" / "interfaces").parent.mkdir(parents=True, exist_ok=True)
            (etc_dir / "network" / "interfaces").write_text(interfaces)
            
            # Hostname resolution
            hosts = """127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
fe00::0         ip6-localnet
ff00::0         ip6-mcastprefix
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
"""
            
            (etc_dir / "hosts").write_text(hosts)
            
            self.log("Network configuration completed")
            return True
        except Exception as e:
            self.log(f"Error setting up network: {e}")
            return False
    
    def configure_locale(self, language: str, timezone: str):
        """Configure locale and timezone"""
        self.report_progress(f"Configuring locale: {language}", 65)
        
        try:
            etc_dir = Path(self.target_mount) / "etc"
            
            # Timezone
            (etc_dir / "timezone").write_text(timezone)
            
            # Locale configuration
            locale_map = {
                'en': 'en_US.UTF-8',
                'ar': 'ar_SA.UTF-8',
                'de': 'de_DE.UTF-8',
                'es': 'es_ES.UTF-8',
                'fr': 'fr_FR.UTF-8',
                'zh': 'zh_CN.UTF-8',
            }
            
            locale = locale_map.get(language, 'en_US.UTF-8')
            
            locale_gen = f"{locale} UTF-8\n"
            (etc_dir / "locale.gen").write_text(locale_gen)
            
            # LANG environment
            (etc_dir / "default" / "locale").parent.mkdir(parents=True, exist_ok=True)
            (etc_dir / "default" / "locale").write_text(f"LANG={locale}\nLC_ALL={locale}\n")
            
            self.log(f"Locale configured: {locale}")
            return True
        except Exception as e:
            self.log(f"Error configuring locale: {e}")
            return False
    
    def create_user(self, username: str, password: str, hostname: str, 
                   sudo_access: bool = True, autologin: bool = False):
        """Create user account and configure system"""
        self.report_progress(f"Creating user: {username}", 70)
        
        try:
            # Set hostname
            etc_dir = Path(self.target_mount) / "etc"
            (etc_dir / "hostname").write_text(hostname)
            
            # Create /etc/passwd
            passwd_entry = f"{username}:x:1000:1000:{username}:/home/{username}:/bin/bash\n"
            passwd_file = etc_dir / "passwd"
            
            if passwd_file.exists():
                passwd_file.write_text(passwd_file.read_text() + passwd_entry)
            else:
                # Create base passwd file
                base_passwd = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/sbin/nologin
bin:x:2:2:bin:/bin:/sbin/nologin
sys:x:3:3:sys:/dev:/sbin/nologin
"""
                passwd_file.write_text(base_passwd + passwd_entry)
            
            # Create /etc/shadow
            shadow_file = etc_dir / "shadow"
            # In real implementation, hash the password
            shadow_entry = f"{username}:*:18000:0:99999:7::\n"
            shadow_file.write_text(shadow_entry)
            shadow_file.chmod(0o000)  # Only root can read
            
            # Create user home directory
            home_dir = Path(self.target_mount) / "home" / username
            home_dir.mkdir(parents=True, exist_ok=True)
            
            # Create .bashrc
            bashrc = home_dir / ".bashrc"
            bashrc.write_text("""# .bashrc for CarrotOS
export LANG=en_US.UTF-8
export PATH=$PATH:/usr/local/bin
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
""")
            
            self.log(f"User '{username}' created with home directory")
            
            # Add to sudo group
            if sudo_access:
                group_file = etc_dir / "group"
                sudo_entry = f"{username}:x:27:{username}\n"
                if group_file.exists():
                    group_file.write_text(group_file.read_text() + sudo_entry)
                self.log(f"User '{username}' added to sudo group")
            
            return True
        except Exception as e:
            self.log(f"Error creating user: {e}")
            return False
    
    def install_applications(self):
        """Install default applications"""
        self.report_progress("Installing applications", 75)
        
        try:
            # Create /usr/local/bin for GUI applications
            bin_dir = Path(self.target_mount) / "usr" / "local" / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            
            # Applications to install (in real implementation, copy actual files)
            apps = [
                'carrot-terminal',
                'carrot-files',
                'carrot-editor',
                'carrot-browser',
                'carrot-settings',
                'carrot-shell',
            ]
            
            for app in apps:
                (bin_dir / app).touch()
            
            self.log(f"Installed {len(apps)} applications")
            return True
        except Exception as e:
            self.log(f"Error installing applications: {e}")
            return False
    
    def configure_services(self):
        """Configure system services"""
        self.report_progress("Configuring services", 80)
        
        try:
            # Create systemd directory
            systemd_dir = Path(self.target_mount) / "etc" / "systemd" / "system"
            systemd_dir.mkdir(parents=True, exist_ok=True)
            
            # Create basic services
            services = {
                'carrot-display-manager.service': """[Unit]
Description=CarrotOS Display Manager
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/carrot-dm
Restart=on-failure

[Install]
WantedBy=graphical.target
""",
                'carrot-shell.service': """[Unit]
Description=CarrotOS Desktop Shell
After=display-manager.service

[Service]
Type=simple
ExecStart=/usr/bin/carrot-shell

[Install]
WantedBy=graphical.target
""",
            }
            
            for service_name, service_content in services.items():
                (systemd_dir / service_name).write_text(service_content)
            
            self.log(f"Configured {len(services)} services")
            return True
        except Exception as e:
            self.log(f"Error configuring services: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify installation"""
        self.report_progress("Verifying installation", 90)
        
        try:
            required_dirs = [
                'bin', 'sbin', 'usr', 'etc', 'var', 'home', 'root', 'boot'
            ]
            
            for d in required_dirs:
                path = Path(self.target_mount) / d
                if not path.exists():
                    self.log(f"Missing required directory: {d}")
                    return False
            
            required_files = [
                'etc/passwd',
                'etc/hostname',
                'boot/grub/grub.cfg',
            ]
            
            for f in required_files:
                path = Path(self.target_mount) / f
                if not path.exists():
                    self.log(f"Missing required file: {f}")
                    return False
            
            self.log("Installation verification passed")
            return True
        except Exception as e:
            self.log(f"Error verifying installation: {e}")
            return False
    
    def finalize_installation(self) -> bool:
        """Finalize installation"""
        self.report_progress("Finalizing installation", 95)
        
        try:
            # Create installation info
            install_info = {
                'version': '1.0',
                'installed': True,
                'timestamp': str(__import__('datetime').datetime.now()),
            }
            
            info_file = Path(self.target_mount) / "etc" / "carrotos-install.info"
            info_file.write_text(json.dumps(install_info, indent=2))
            
            self.log("Installation finalized successfully")
            return True
        except Exception as e:
            self.log(f"Error finalizing installation: {e}")
            return False
    
    def run_full_installation(self, device: str, username: str, password: str,
                            hostname: str, language: str, timezone: str,
                            efi: bool = True, encryption: bool = False) -> bool:
        """Run complete installation"""
        try:
            self.setup_target()
            self.install_base_system()
            self.install_gui_system()
            self.configure_bootloader(device, efi=efi)
            self.setup_network()
            self.configure_locale(language, timezone)
            self.create_user(username, password, hostname)
            self.install_applications()
            self.configure_services()
            
            if self.verify_installation():
                self.finalize_installation()
                self.report_progress("Installation complete!", 100)
                return True
            else:
                self.report_progress("Installation verification failed", 100)
                return False
        
        except Exception as e:
            self.log(f"Installation failed: {e}")
            self.report_progress(f"Installation failed: {e}", 100)
            return False

def main():
    """Test installation backend"""
    backend = InstallationBackend()
    print("Installation backend initialized")

if __name__ == '__main__':
    main()
