#!/usr/bin/env python3
"""
CarrotOS Rootfs Generator
Creates complete root filesystem from source packages
"""

import os
import sys
import json
import yaml
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class RootfsBuilder:
    """Builds complete CarrotOS root filesystem"""
    
    def __init__(self, root_dir: str, output_dir: str):
        self.root = Path(root_dir)
        self.output_dir = Path(output_dir)
        self.rootfs_dir = self.output_dir / "rootfs"
        self.cache_dir = self.output_dir / "cache"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def create_directory_structure(self):
        """Create Linux FHS compliant directory structure"""
        logger.info("Creating directory structure...")
        
        dirs = [
            "bin", "sbin", "usr/bin", "usr/sbin", "usr/lib", "usr/share",
            "usr/share/applications", "usr/share/icons", "usr/share/themes",
            "usr/share/pixmaps", "usr/share/fonts", "usr/share/doc",
            "lib", "lib64", "var", "var/log", "var/lib", "var/lib/carrotpkg",
            "var/cache", "var/tmp", "var/run", "var/spool",
            "etc", "etc/init.d", "etc/profile.d", "etc/carrot",
            "etc/carrot/services", "etc/carrot/overlays",
            "proc", "sys", "dev", "dev/shm", "dev/pts",
            "tmp", "root", "home", "home/user",
            "mnt", "media", "opt",
            "srv", "run", "boot"
        ]
        
        for d in dirs:
            dir_path = self.rootfs_dir / d
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"  Created {d}")
    
    def create_essential_files(self):
        """Create essential system files"""
        logger.info("Creating essential system files...")
        
        # /etc/passwd
        passwd_content = """root:x:0:0:root:/root:/bin/bash
user:x:1000:1000:Regular User:/home/user:/bin/bash
nobody:x:65534:65534:nobody:/nonexistent:/sbin/nologin
"""
        (self.rootfs_dir / "etc/passwd").write_text(passwd_content)
        (self.rootfs_dir / "etc/passwd").chmod(0o644)
        
        # /etc/group
        group_content = """root:x:0:
user:x:1000:
wheel:x:10:user
audio:x:29:user
video:x:44:user
nobody:x:65534:
"""
        (self.rootfs_dir / "etc/group").write_text(group_content)
        (self.rootfs_dir / "etc/group").chmod(0o644)
        
        # /etc/hostname
        (self.rootfs_dir / "etc/hostname").write_text("carrotos\n")
        
        # /etc/hosts
        hosts_content = """127.0.0.1   localhost carrotos
::1         localhost carrotos
"""
        (self.rootfs_dir / "etc/hosts").write_text(hosts_content)
        
        # /etc/fstab
        fstab_content = """# Root filesystem
/dev/root  /           overlayfs  defaults  0  0

# Virtual filesystems
proc       /proc       proc       defaults  0  0
sysfs      /sys        sysfs      defaults  0  0
devpts     /dev/pts    devpts     defaults  0  0
tmpfs      /dev/shm    tmpfs      defaults  0  0
tmpfs      /run        tmpfs      defaults  0  0
tmpfs      /tmp        tmpfs      defaults  0  0

# Optional
# LABEL=CARROT-BOOT  /boot  ext2  ro,noatime  0  0
"""
        (self.rootfs_dir / "etc/fstab").write_text(fstab_content)
        
        # /etc/ld.so.conf
        ldconf_content = """# Dynamic linker configuration
/lib
/lib64
/usr/lib
/usr/lib64
/usr/local/lib
/usr/local/lib64
"""
        (self.rootfs_dir / "etc/ld.so.conf").write_text(ldconf_content)
        
        # /etc/profile (shell defaults)
        profile_content = """#!/bin/sh
# /etc/profile - Shell initialization

export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export MANPATH=/usr/local/share/man:/usr/share/man
export INFOPATH=/usr/local/share/info:/usr/share/info
export EDITOR=nano
export PAGER=less

# Set terminal type
if [ -z "$TERM" ]; then
    export TERM=linux
fi

# Source profile.d scripts
if [ -d /etc/profile.d ]; then
    for profile in /etc/profile.d/*.sh; do
        [ -r "$profile" ] && . "$profile"
    done
fi
"""
        (self.rootfs_dir / "etc/profile").write_text(profile_content)
        (self.rootfs_dir / "etc/profile").chmod(0o755)
        
        logger.info("  Essential files created")
    
    def install_busybox(self):
        """Install busybox utilities"""
        logger.info("Setting up BusyBox utilities...")
        
        # Create shell script placeholder for busybox
        busybox_init = """#!/bin/sh
# BusyBox minimal init
/bin/busybox --install -s /bin
/bin/busybox --install -s /sbin
/bin/busybox --install -s /usr/bin
/bin/busybox --install -s /usr/sbin
echo "BusyBox initialized"
"""
        busybox_path = self.rootfs_dir / "bin/busybox"
        busybox_path.write_text(busybox_init)
        busybox_path.chmod(0o755)
        
        # Create symlinks for common utilities
        common_utils = [
            "sh", "bash", "ls", "cat", "grep", "sed", "awk",
            "find", "tar", "gzip", "mount", "umount", "mkdir",
            "cp", "mv", "rm", "ln", "id", "whoami", "su"
        ]
        
        for util in common_utils:
            link_path = self.rootfs_dir / f"bin/{util}"
            if not link_path.exists():
                link_path.symlink_to("busybox")
        
        logger.info("  BusyBox utilities installed")
    
    def create_service_structure(self):
        """Create service and init structure"""
        logger.info("Creating service structure...")
        
        # Copy service definitions
        services_src = self.root / "services/system"
        services_dst = self.rootfs_dir / "etc/carrot/services"
        
        if services_src.exists():
            for svc_file in services_src.glob("*.yaml"):
                shutil.copy(svc_file, services_dst / svc_file.name)
        
        logger.info("  Service structure created")
    
    def create_overlay_structure(self):
        """Create overlay layer directories"""
        logger.info("Creating overlay structure...")
        
        overlay_files = [
            "etc/carrot/overlays/overlay-order.yaml",
            "overlay/base/.gitkeep",
            "overlay/user/.gitkeep",
            "overlay/temp/.gitkeep"
        ]
        
        for ofile in overlay_files:
            fpath = self.rootfs_dir / ofile
            fpath.parent.mkdir(parents=True, exist_ok=True)
            if ofile.endswith(".yaml"):
                # Copy actual overlay order
                src = self.root / "build/manifests/overlay-order.yaml"
                if src.exists():
                    shutil.copy(src, fpath)
            else:
                fpath.touch()
        
        logger.info("  Overlay structure created")
    
    def build(self):
        """Build complete rootfs"""
        logger.info("=" * 60)
        logger.info("Building CarrotOS Root Filesystem")
        logger.info("=" * 60)
        
        if self.rootfs_dir.exists():
            logger.warning(f"Removing existing rootfs: {self.rootfs_dir}")
            shutil.rmtree(self.rootfs_dir)
        
        self.rootfs_dir.mkdir(parents=True, exist_ok=True)
        
        self.create_directory_structure()
        self.create_essential_files()
        self.install_busybox()
        self.create_service_structure()
        self.create_overlay_structure()
        
        logger.info("=" * 60)
        logger.info(f"Rootfs built at: {self.rootfs_dir}")
        logger.info(f"Total size: {self.get_dir_size()}")
        logger.info("=" * 60)
        
        return True
    
    def get_dir_size(self) -> str:
        """Get directory size in human readable format"""
        total = sum(
            f.stat().st_size for f in self.rootfs_dir.rglob('*')
            if f.is_file()
        )
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total < 1024:
                return f"{total:.2f} {unit}"
            total /= 1024
        return f"{total:.2f} TB"


def main():
    if len(sys.argv) < 2:
        print("Usage: rootfs_builder.py <carrotos_root> [output_dir]")
        print("  carrotos_root: Path to CarrotOS project root")
        print("  output_dir: Output directory (default: ./build)")
        return 1
    
    root_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./build"
    
    builder = RootfsBuilder(root_dir, output_dir)
    return 0 if builder.build() else 1


if __name__ == "__main__":
    sys.exit(main())
