#!/usr/bin/env python3
"""
Disk partitioning module for CarrotOS Installer
Handles disk detection, partitioning, and formatting
"""

import subprocess
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass
class Disk:
    """Disk information"""
    device: str
    size: int  # bytes
    model: str
    vendor: str
    partitions: int
    removable: bool
    
    @property
    def size_gb(self) -> float:
        """Size in GB"""
        return self.size / (1024**3)
    
    @property
    def size_str(self) -> str:
        """Human readable size"""
        if self.size_gb > 1024:
            return f"{self.size_gb/1024:.1f}TB"
        return f"{self.size_gb:.1f}GB"

@dataclass
class Partition:
    """Partition information"""
    device: str
    number: int
    size: int  # bytes
    type: str  # ext4, swap, fat32, etc.
    mount_point: Optional[str] = None
    label: Optional[str] = None
    
    @property
    def size_gb(self) -> float:
        """Size in GB"""
        return self.size / (1024**3)

class DiskManager:
    """Manage disk operations"""
    
    # Partition minimum sizes (in MB)
    PARTITION_SIZES = {
        'efi': 512,
        'boot': 1024,
        'swap': 4096,
        'root': 20480,
        'home': 10240,
    }
    
    def __init__(self):
        self.disks: List[Disk] = []
        self.mount_prefix = "/target"
    
    def detect_disks(self) -> List[Disk]:
        """Detect available disks"""
        try:
            # Use lsblk to detect disks
            result = subprocess.run(
                ['lsblk', '-d', '-b', '-o', 'NAME,SIZE,MODEL,VENDOR,TYPE,RM',
                 '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return self._detect_disks_fallback()
            
            try:
                data = json.loads(result.stdout)
                disks = []
                
                for blockdevice in data.get('blockdevices', []):
                    if blockdevice['type'] == 'disk':
                        disk = Disk(
                            device=f"/dev/{blockdevice['name']}",
                            size=int(blockdevice['size']),
                            model=blockdevice.get('model', 'Unknown').strip(),
                            vendor=blockdevice.get('vendor', 'Unknown').strip(),
                            partitions=self._count_partitions(f"/dev/{blockdevice['name']}"),
                            removable=blockdevice.get('rm') == 1
                        )
                        
                        # Only include disks larger than 10GB
                        if disk.size_gb >= 10:
                            disks.append(disk)
                
                self.disks = disks
                return disks
            
            except json.JSONDecodeError:
                return self._detect_disks_fallback()
        
        except Exception as e:
            print(f"Error detecting disks: {e}")
            return self._detect_disks_fallback()
    
    def _detect_disks_fallback(self) -> List[Disk]:
        """Fallback disk detection using /sys"""
        disks = []
        
        try:
            sys_block = Path("/sys/block")
            
            for dev_path in sys_block.iterdir():
                if dev_path.name in ['loop', 'ram', 'zram']:
                    continue
                
                # Skip if removable (USB drives)
                removable = (dev_path / "removable").read_text().strip() == "1"
                
                size_path = dev_path / "size"
                if size_path.exists():
                    size = int(size_path.read_text().strip()) * 512
                    
                    # Only disks >= 10GB
                    if size >= 10 * 1024**3:
                        model_path = dev_path / "device" / "model"
                        model = model_path.read_text().strip() if model_path.exists() else "Unknown"
                        
                        disk = Disk(
                            device=f"/dev/{dev_path.name}",
                            size=size,
                            model=model,
                            vendor="Unknown",
                            partitions=self._count_partitions(f"/dev/{dev_path.name}"),
                            removable=removable
                        )
                        disks.append(disk)
        
        except Exception as e:
            print(f"Error in fallback detection: {e}")
        
        return disks
    
    def _count_partitions(self, device: str) -> int:
        """Count partitions on device"""
        try:
            result = subprocess.run(
                ['lsblk', '-o', 'NAME', '--list', device],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Subtract 1 for the device itself
            return len(result.stdout.strip().split('\n')) - 1 if result.returncode == 0 else 0
        except:
            return 0
    
    def create_partitions_simple(self, device: str) -> List[Partition]:
        """Create simple partition scheme (root + swap)"""
        partitions = []
        
        # Get disk size
        disk = next((d for d in self.disks if d.device == device), None)
        if not disk:
            raise ValueError(f"Disk {device} not found")
        
        total_size_mb = int(disk.size / (1024**2))
        
        # Allocate swap (4GB or 1/4 of RAM, whichever is smaller)
        swap_size_mb = min(4096, int(total_size_mb * 0.1))
        root_size_mb = total_size_mb - swap_size_mb - 512  # 512 for EFI/boot
        
        # EFI partition
        partitions.append(Partition(
            device=f"{device}1",
            number=1,
            size=512 * 1024**2,
            type="fat32",
            mount_point="/boot/efi",
            label="EFI"
        ))
        
        # Root partition
        partitions.append(Partition(
            device=f"{device}2",
            number=2,
            size=root_size_mb * 1024**2,
            type="ext4",
            mount_point="/",
            label="root"
        ))
        
        # Swap partition
        partitions.append(Partition(
            device=f"{device}3",
            number=3,
            size=swap_size_mb * 1024**2,
            type="swap",
            label="swap"
        ))
        
        return partitions
    
    def create_partitions_advanced(self, device: str) -> List[Partition]:
        """Create advanced partition scheme"""
        partitions = []
        
        disk = next((d for d in self.disks if d.device == device), None)
        if not disk:
            raise ValueError(f"Disk {device} not found")
        
        total_size_mb = int(disk.size / (1024**2))
        
        # Fixed sizes
        efi_size = self.PARTITION_SIZES['efi']
        boot_size = self.PARTITION_SIZES['boot']
        root_size = self.PARTITION_SIZES['root']
        swap_size = self.PARTITION_SIZES['swap']
        
        # Home gets remainder
        home_size = total_size_mb - efi_size - boot_size - root_size - swap_size
        
        if home_size < self.PARTITION_SIZES['home']:
            raise ValueError("Disk too small for advanced partitioning")
        
        # EFI
        partitions.append(Partition(
            device=f"{device}1",
            number=1,
            size=efi_size * 1024**2,
            type="fat32",
            mount_point="/boot/efi",
            label="EFI"
        ))
        
        # Boot
        partitions.append(Partition(
            device=f"{device}2",
            number=2,
            size=boot_size * 1024**2,
            type="ext4",
            mount_point="/boot",
            label="boot"
        ))
        
        # Root
        partitions.append(Partition(
            device=f"{device}3",
            number=3,
            size=root_size * 1024**2,
            type="ext4",
            mount_point="/",
            label="root"
        ))
        
        # Home
        partitions.append(Partition(
            device=f"{device}4",
            number=4,
            size=home_size * 1024**2,
            type="ext4",
            mount_point="/home",
            label="home"
        ))
        
        # Swap
        partitions.append(Partition(
            device=f"{device}5",
            number=5,
            size=swap_size * 1024**2,
            type="swap",
            label="swap"
        ))
        
        return partitions
    
    def clear_disk(self, device: str) -> bool:
        """Clear all partitions on device"""
        try:
            # Unmount all partitions
            subprocess.run(['umount', '-R', device], capture_output=True)
            
            # Clear partition table
            subprocess.run(['dd', 'if=/dev/zero', f'of={device}', 'bs=1M', 'count=10'],
                          timeout=30)
            
            return True
        except Exception as e:
            print(f"Error clearing disk: {e}")
            return False
    
    def create_partition_table(self, device: str, gpt: bool = True) -> bool:
        """Create partition table (GPT or MBR)"""
        try:
            table_type = 'gpt' if gpt else 'msdos'
            subprocess.run(['parted', '-s', device, 'mklabel', table_type],
                          check=True, timeout=10)
            return True
        except Exception as e:
            print(f"Error creating partition table: {e}")
            return False
    
    def create_partition(self, device: str, partition: Partition) -> bool:
        """Create a single partition"""
        try:
            # Calculate start and end in MB
            start_mb = (partition.number - 1) * 512  # Rough estimate
            size_mb = int(partition.size / (1024**2))
            
            subprocess.run([
                'parted', '-s', device, 'mkpart', 'primary',
                f'{start_mb}M', f'{start_mb + size_mb}M'
            ], check=True, timeout=30)
            
            return True
        except Exception as e:
            print(f"Error creating partition: {e}")
            return False
    
    def format_partition(self, partition: Partition) -> bool:
        """Format a partition"""
        try:
            if partition.type == 'ext4':
                subprocess.run([
                    'mkfs.ext4', '-F', '-L', partition.label or '',
                    partition.device
                ], check=True, timeout=60)
            
            elif partition.type == 'fat32':
                subprocess.run([
                    'mkfs.fat', '-F32', '-n', partition.label or '',
                    partition.device
                ], check=True, timeout=60)
            
            elif partition.type == 'swap':
                subprocess.run([
                    'mkswap', '-L', partition.label or '',
                    partition.device
                ], check=True, timeout=60)
            
            return True
        except Exception as e:
            print(f"Error formatting partition: {e}")
            return False
    
    def mount_partition(self, partition: Partition) -> bool:
        """Mount a partition"""
        if not partition.mount_point or partition.type == 'swap':
            return True
        
        try:
            mount_path = f"{self.mount_prefix}{partition.mount_point}"
            Path(mount_path).mkdir(parents=True, exist_ok=True)
            
            subprocess.run([
                'mount', partition.device, mount_path
            ], check=True, timeout=10)
            
            return True
        except Exception as e:
            print(f"Error mounting partition: {e}")
            return False
    
    def get_disk_info(self, device: str) -> Optional[Disk]:
        """Get information about a disk"""
        return next((d for d in self.disks if d.device == device), None)

# Example usage
def main():
    """Test disk manager"""
    manager = DiskManager()
    
    # Detect disks
    disks = manager.detect_disks()
    
    print("Available disks:")
    for disk in disks:
        print(f"  {disk.device}: {disk.size_str} ({disk.model})")
    
    if disks:
        # Example: create simple partition scheme
        device = disks[0].device
        print(f"\nSimple partitioning for {device}:")
        
        parts = manager.create_partitions_simple(device)
        for part in parts:
            print(f"  {part.device}: {part.size_gb:.1f}GB ({part.type}) -> {part.mount_point}")

if __name__ == '__main__':
    main()
