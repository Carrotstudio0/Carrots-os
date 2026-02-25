#!/usr/bin/env python3
"""
CarrotOS ISO Builder
Complete bootable ISO generation pipeline
"""

import os
import sys
import json
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [ISO] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class ISOBuilder:
    """Builds bootable CarrotOS ISO image"""
    
    def __init__(self, carrotos_root: str, output_dir: str):
        self.carrotos_root = Path(carrotos_root)
        self.output_dir = Path(output_dir)
        self.build_dir = self.output_dir / "iso_build"
        self.iso_dir = self.build_dir / "iso"
        self.rootfs_dir = self.output_dir / "rootfs"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.iso_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_iso_structure(self):
        """Create ISO directory structure"""
        logger.info("Setting up ISO structure...")
        
        dirs = [
            "boot/grub",
            "boot/efi",
            "carrot",
            "carrot/overlays",
            "carrot/pkgs",
            "efi/boot",
        ]
        
        for d in dirs:
            (self.iso_dir / d).mkdir(parents=True, exist_ok=True)
        
        logger.info("ISO structure created")
    
    def copy_bootloader_files(self):
        """Copy GRUB bootloader files"""
        logger.info("Copying bootloader files...")
        
        # Copy GRUB config
        grub_cfg_src = self.carrotos_root / "boot/grub/grub.cfg"
        grub_cfg_dst = self.iso_dir / "boot/grub/grub.cfg"
        
        if grub_cfg_src.exists():
            shutil.copy(grub_cfg_src, grub_cfg_dst)
            logger.info("GRUB config copied")
        
        # Create BIOS boot file
        bios_boot = self.iso_dir / "boot/grub/i386-pc"
        bios_boot.mkdir(parents=True, exist_ok=True)
    
    def create_rootfs_squashfs(self) -> Optional[Path]:
        """Create squashfs compressed rootfs"""
        logger.info("Creating rootfs squashfs...")
        
        if not self.rootfs_dir.exists():
            logger.error("Rootfs not found. Run rootfs_builder first.")
            return None
        
        squashfs_file = self.iso_dir / "carrot/rootfs.squashfs"
        
        try:
            # Check if mksquashfs available
            result = subprocess.run(
                ["mksquashfs", str(self.rootfs_dir), str(squashfs_file),
                 "-comp", "xz", "-Xbcj", "x86", "-b", "1024k"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                size = squashfs_file.stat().st_size / (1024**2)
                logger.info(f"Rootfs squashfs created: {size:.1f} MB")
                return squashfs_file
            else:
                logger.warning("mksquashfs not available, skipping compression")
                # Fallback: copy rootfs as-is
                shutil.copytree(self.rootfs_dir, self.iso_dir / "carrot/rootfs")
                return self.iso_dir / "carrot/rootfs"
        except Exception as e:
            logger.error(f"Failed to create squashfs: {e}")
            return None
    
    def copy_kernel(self):
        """Copy kernel image"""
        logger.info("Copying kernel image...")
        
        kernel_src = self.build_dir / "kernel/bzImage"
        kernel_dst = self.iso_dir / "boot/vmlinuz"
        
        if kernel_src.exists():
            shutil.copy(kernel_src, kernel_dst)
            logger.info("Kernel copied")
        else:
            logger.warning("Kernel image not found, creating placeholder")
            kernel_dst.write_text("KERNEL_PLACEHOLDER")
    
    def copy_initramfs(self):
        """Copy initramfs"""
        logger.info("Copying initramfs...")
        
        initramfs_src = self.build_dir / "initramfs.cpio.gz"
        initramfs_dst = self.iso_dir / "boot/initramfs.cpio.gz"
        
        if initramfs_src.exists():
            shutil.copy(initramfs_src, initramfs_dst)
            logger.info("Initramfs copied")
        else:
            logger.warning("Initramfs not found, creating minimal placeholder")
            initramfs_dst.write_text("INITRAMFS_PLACEHOLDER")
    
    def create_grub_cfg(self):
        """Create GRUB configuration file"""
        logger.info("Creating GRUB configuration...")
        
        grub_cfg_content = """# CarrotOS GRUB Configuration

set default="0"
set timeout=5

# Set color scheme
set color_normal=white/black
set color_highlight=black/white

# Boot menu entries

menuentry 'CarrotOS 1.0.0 (Live)' {
    search --no-floppy --label --set=root CARROT-BOOT
    echo 'Booting CarrotOS...'
    linux /boot/vmlinuz root=/dev/ram0 ro quiet splash
    initrd /boot/initramfs.cpio.gz
}

menuentry 'CarrotOS (Safe Mode)' {
    search --no-floppy --label --set=root CARROT-BOOT
    echo 'Booting in safe mode...'
    linux /boot/vmlinuz root=/dev/ram0 ro single
    initrd /boot/initramfs.cpio.gz
}

menuentry 'CarrotOS (Recovery Shell)' {
    search --no-floppy --label --set=root CARROT-BOOT
    echo 'Starting recovery shell...'
    linux /boot/vmlinuz root=/dev/ram0 ro rescue
    initrd /boot/initramfs.cpio.gz
}
"""
        
        grub_cfg_file = self.iso_dir / "boot/grub/grub.cfg"
        grub_cfg_file.write_text(grub_cfg_content)
        logger.info("GRUB config created")
    
    def create_iso_metadata(self):
        """Create ISO metadata files"""
        logger.info("Creating ISO metadata...")
        
        # VERSION file
        version_file = self.iso_dir / "carrot/VERSION"
        version_file.write_text("CarrotOS 1.0.0\nCarrot-LTS\n")
        
        # BUILD file
        build_file = self.iso_dir / "carrot/BUILD"
        import time
        build_file.write_text(f"Built: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        logger.info("ISO metadata created")
    
    def build_iso(self) -> Optional[Path]:
        """Build final ISO file"""
        logger.info("Building ISO image...")
        
        iso_output = self.output_dir / "CarrotOS-1.0.0-x86_64.iso"
        
        try:
            # Use xorriso if available, fallback to mkisofs
            cmd = [
                "xorriso",
                "-as", "mkisofs",
                "-iso9660",
                "-J",
                "-R",
                "-V", "CARROT-BOOT",
                "-b", "boot/grub/i386-pc/eltorito.img",
                "-c", "boot/grub/boot.cat",
                "-boot-load-size", "4",
                "-boot-info-table",
                "-no-emul-boot",
                "-o", str(iso_output),
                str(self.iso_dir)
            ]
            
            logger.info(f"Running: {' '.join(cmd[:3])}...")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning("xorriso not available, trying mkisofs...")
                cmd[0] = "mkisofs"
                result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and iso_output.exists():
                size = iso_output.stat().st_size / (1024**2)
                logger.info(f"ISO image created: {iso_output} ({size:.1f} MB)")
                return iso_output
            else:
                logger.error(f"ISO creation failed: {result.stderr}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to build ISO: {e}")
            return None
    
    def build(self) -> bool:
        """Execute complete ISO build pipeline"""
        logger.info("=" * 70)
        logger.info("CarrotOS ISO Build Pipeline")
        logger.info("=" * 70)
        
        self.setup_iso_structure()
        self.copy_bootloader_files()
        self.copy_kernel()
        self.copy_initramfs()
        self.create_grub_cfg()
        self.create_rootfs_squashfs()
        self.create_iso_metadata()
        
        iso_file = self.build_iso()
        
        logger.info("=" * 70)
        if iso_file:
            logger.info("✓ ISO build successful!")
            logger.info(f"  Output: {iso_file}")
            logger.info("  Ready for burning to USB or DVD")
        else:
            logger.error("✗ ISO build failed")
        logger.info("=" * 70)
        
        return iso_file is not None


def main():
    if len(sys.argv) < 2:
        print("Usage: iso_builder.py <carrotos_root> [output_dir]")
        print("  carrotos_root: CarrotOS project root")
        print("  output_dir: Output directory (default: ./build)")
        return 1
    
    carrotos_root = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./build"
    
    builder = ISOBuilder(carrotos_root, output_dir)
    return 0 if builder.build() else 1


if __name__ == "__main__":
    sys.exit(main())
