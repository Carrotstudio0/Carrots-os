#!/usr/bin/env python3
"""
CarrotOS Initramfs Generator
Creates lightweight initial ramdisk for boot
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class InitramfsBuilder:
    """Builds CarrotOS initramfs"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.initramfs_dir = self.output_dir / "initramfs_build"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_init_script(self):
        """Create main init script for initramfs"""
        logger.info("Creating init script...")
        
        init_script = """#!/bin/sh
# CarrotOS Initramfs Init Script
# Minimal init for early boot

set -e

# Mount critical filesystems
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev
mount -t tmpfs tmpfs /run

# Create necessary device nodes
mknod /dev/console c 5 1
mknod /dev/null c 1 3
mknod /dev/zero c 1 5
mknod /dev/random c 1 8
mknod /dev/urandom c 1 9

# Setup kernel modules
echo "carrotos initramfs start"

# Find and mount root filesystem
logger() {
    echo "[carrot-init] $@"
}

logger "Searching for root filesystem..."

# Wait for root device
ROOT_DEVICE=""
for i in 1 2 3 4 5; do
    if [ -L /dev/disk/by-label/CARROT-ROOT ]; then
        ROOT_DEVICE=$(readlink -f /dev/disk/by-label/CARROT-ROOT)
        break
    fi
    logger "Waiting for root device... ($i/5)"
    sleep 1
done

if [ -z "$ROOT_DEVICE" ]; then
    logger "ERROR: Could not find root device!"
    logger "Dropping to recovery shell"
    sh
    exit 1
fi

logger "Found root device: $ROOT_DEVICE"

# Mount root as read-only
mkdir -p /mnt/root
mount -r "$ROOT_DEVICE" /mnt/root

# Setup overlayfs layers
logger "Setting up overlay filesystem..."
mkdir -p /mnt/overlay-lower
mkdir -p /mnt/overlay-rw/upper
mkdir -p /mnt/overlay-rw/work

# Mount overlay
mount -t overlay overlayfs /mnt/root \\
    -o lowerdir=/mnt/overlay-lower:/mnt/root \\
    -o upperdir=/mnt/overlay-rw/upper \\
    -o workdir=/mnt/overlay-rw/work

logger "Overlay mounted successfully"

# Cleanup and switch root
logger "Switching to new root..."
cd /
umount /proc
umount /sys
umount /dev
umount /run

# Execute init in new root
exec chroot /mnt/root /sbin/init
"""
        
        init_path = self.initramfs_dir / "init"
        init_path.write_text(init_script)
        init_path.chmod(0o755)
        logger.info("  Init script created")
    
    def create_directory_structure(self):
        """Create minimalfs directory structure"""
        logger.info("Creating directory structure...")
        
        dirs = [
            "bin", "sbin", "lib", "lib64", "usr/bin", "usr/sbin",
            "usr/lib", "lib/modules", "proc", "sys", "dev", "dev/pts",
            "dev/shm", "run", "tmp", "mnt", "mnt/root", "mnt/overlay-lower",
            "mnt/overlay-rw/upper", "mnt/overlay-rw/work"
        ]
        
        for d in dirs:
            (self.initramfs_dir / d).mkdir(parents=True, exist_ok=True)
    
    def copy_minimal_binaries(self):
        """Create placeholder minimal binaries"""
        logger.info("Creating minimal utilities...")
        
        # Create busybox placeholder
        busybox_script = """#!/bin/sh
# Minimal busybox replacement
"""
        (self.initramfs_dir / "bin/busybox").write_text(busybox_script)
        (self.initramfs_dir / "bin/busybox").chmod(0o755)
        
        # Create symlinks
        for cmd in ["sh", "mount", "umount", "mkdir", "chroot", "sleep"]:
            link = self.initramfs_dir / f"bin/{cmd}"
            if not link.exists():
                link.symlink_to("busybox")
        
        for cmd in ["init", "mknod", "readlink"]:
            link = self.initramfs_dir / f"sbin/{cmd}"
            if not link.exists():
                link.symlink_to("../bin/busybox")
    
    def pack_initramfs(self) -> Path:
        """Pack initramfs into cpio archive"""
        logger.info("Packing initramfs...")
        
        output_file = self.output_dir / "initramfs.cpio.gz"
        
        # Create cpio archive
        cpio_file = self.output_dir / "initramfs.cpio"
        
        result = subprocess.run(
            f"cd {self.initramfs_dir} && find . -print0 | cpio --null -ov -H newc > {cpio_file}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"cpio failed: {result.stderr}")
            return None
        
        # Compress
        subprocess.run(
            ["gzip", str(cpio_file)],
            capture_output=True
        )
        
        gzip_cpio = cpio_file.with_suffix(".cpio.gz")
        if gzip_cpio.exists():
            shutil.move(gzip_cpio, output_file)
        
        logger.info(f"  Initramfs packed: {output_file}")
        return output_file
    
    def build(self) -> bool:
        """Build complete initramfs"""
        logger.info("=" * 60)
        logger.info("Building CarrotOS Initramfs")
        logger.info("=" * 60)
        
        if self.initramfs_dir.exists():
            shutil.rmtree(self.initramfs_dir)
        self.initramfs_dir.mkdir(parents=True, exist_ok=True)
        
        self.create_directory_structure()
        self.create_init_script()
        self.copy_minimal_binaries()
        self.pack_initramfs()
        
        logger.info("=" * 60)
        logger.info("Initramfs build complete")
        logger.info("=" * 60)
        return True


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./build"
    builder = InitramfsBuilder(output_dir)
    return 0 if builder.build() else 1


if __name__ == "__main__":
    sys.exit(main())
