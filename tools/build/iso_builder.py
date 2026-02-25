#!/usr/bin/env python3
"""
CarrotOS ISO Creator for Windows
Builds bootable ISO without external dependencies
"""

import os
import sys
import struct
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

class ISOBuilder:
    """Create ISO 9660 images on Windows"""
    
    # Constants
    SECTOR_SIZE = 2048
    ISO_VERSION = 1
    
    # Timestamps format
    TIMESTAMP = "2024022500000000+000"
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.sectors_written = 0
        self.files = []
        
    def log(self, level: str, message: str):
        """Logging with colors"""
        colors = {
            "INFO": "\033[36m",
            "SUCCESS": "\033[32m",
            "WARNING": "\033[33m",
            "ERROR": "\033[31m",
        }
        reset = "\033[0m"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = colors.get(level, "\033[0m")
        print(f"{color}[{timestamp} {level}]{reset} {message}")
    
    def write_sector(self, data: bytes, file_obj) -> int:
        """Write a padded sector"""
        if len(data) < self.SECTOR_SIZE:
            data = data + b'\x00' * (self.SECTOR_SIZE - len(data))
        file_obj.write(data[:self.SECTOR_SIZE])
        self.sectors_written += 1
        return self.sectors_written - 1
    
    def create_pvd(self) -> bytes:
        """Create Primary Volume Descriptor"""
        pvd = bytearray(self.SECTOR_SIZE)
        
        # Type code
        pvd[0] = 0x01
        
        # Standard identifier
        pvd[1:6] = b'CD001'
        
        # Version
        pvd[6] = 0x01
        
        # System identifier (ASCII-padded)
        pvd[8:40] = b'Windows' + b' ' * 25
        
        # Volume identifier
        pvd[40:72] = b'CARROTOS' + b' ' * 24
        
        # Logical block size (2048 bytes)
        pvd[128:130] = struct.pack('<H', self.SECTOR_SIZE)
        pvd[130:132] = struct.pack('>H', self.SECTOR_SIZE)
        
        # Volume space size (total sectors)
        total_size = 700 * 1024 * 1024 // self.SECTOR_SIZE  # 700 MB
        pvd[80:84] = struct.pack('<I', total_size)
        pvd[84:88] = struct.pack('>I', total_size)
        
        # Escape sequences (for Unicode support)
        pvd[88:120] = b'%/E' + b'\x00' * 29
        
        # Volume set size
        pvd[121] = 0x01
        pvd[122] = 0x01
        
        # Volume sequence number
        pvd[124] = 0x01
        pvd[125] = 0x01
        
        # Logical block size (again for redundancy)
        pvd[128:130] = struct.pack('<H', self.SECTOR_SIZE)
        pvd[130:132] = struct.pack('>H', self.SECTOR_SIZE)
        
        # Path table size (simplified)
        pvd[132:136] = struct.pack('<I', self.SECTOR_SIZE)
        pvd[136:140] = struct.pack('>I', self.SECTOR_SIZE)
        
        # Type L path table location
        pvd[140:144] = struct.pack('<I', 1)
        
        # Optional type L path table
        pvd[144:148] = struct.pack('<I', 0)
        
        # Type M path table location
        pvd[148:152] = struct.pack('>I', 2)
        
        # Optional type M path table
        pvd[152:156] = struct.pack('>I', 0)
        
        # Terminator
        pvd[-1] = 0xFF
        
        return bytes(pvd)
    
    def create_boot_catalog(self) -> bytes:
        """Create El Torito boot catalog"""
        catalog = bytearray(self.SECTOR_SIZE)
        
        # Validation entry
        catalog[0:2] = b'\x01\x00'  # Header ID
        catalog[2] = 0x00  # Platform (BIOS x86)
        catalog[4:6] = b'\x00\x00'  # Reserved
        
        # Checksum (simplified)
        checksum = (sum(catalog[0:16]) & 0xFFFF) ^ 0xFFFF
        catalog[28:30] = struct.pack('<H', checksum)
        
        # Boot entry
        catalog[32] = 0x88  # Bootable
        catalog[33] = 0x00  # Boot media (1.44 MB floppy)
        catalog[34:36] = b'\x00\x00'  # Load segment
        catalog[36] = 0x00  # System type
        catalog[37] = 0x00  # Unused
        catalog[38:40] = struct.pack('<H', 1)  # Sector count
        catalog[40:44] = struct.pack('<I', 17)  # Load RBA (sector 17)
        
        return bytes(catalog)
    
    def create_directory_record(self, name: str, is_dir: bool = False, size: int = 0) -> bytes:
        """Create a directory record"""
        record = bytearray()
        name_len = len(name)
        
        # Record length (will be updated)
        record_len = 33 + name_len
        if record_len % 2:
            record_len += 1
        
        record.append(record_len)  # Directory record length
        record.append(0)  # Extended attribute record length
        
        # Location of extent (LBA)
        record.extend(struct.pack('<I', 0))  # Simplified
        record.extend(struct.pack('>I', 0))
        
        # Data length
        record.extend(struct.pack('<I', size))
        record.extend(struct.pack('>I', size))
        
        # Recording date and time
        now = datetime.now()
        record.append(now.year - 1900)
        record.append(now.month)
        record.append(now.day)
        record.append(now.hour)
        record.append(now.minute)
        record.append(now.second)
        record.append(0)  # Timezone
        
        # File flags
        flags = 0x02 if is_dir else 0x00
        record.append(flags)
        
        # File unit size
        record.append(0)
        
        # Gap size
        record.append(0)
        
        # Sequence number
        record.extend(struct.pack('<H', 1))
        record.extend(struct.pack('>H', 1))
        
        # File identifier length
        record.append(name_len)
        
        # File identifier
        record.extend(name.encode('ascii'))
        
        # Padding to even boundary
        if len(record) % 2:
            record.append(0)
        
        return bytes(record)
    
    def create_root_directory(self) -> bytes:
        """Create root directory record"""
        root = bytearray()
        
        # Add dot entry
        dot = self.create_directory_record(".", is_dir=True)
        root.extend(dot)
        
        # Add dotdot entry
        dotdot = self.create_directory_record("..", is_dir=True)
        root.extend(dotdot)
        
        return bytes(root)
    
    def build_iso(self, boot_image: str = None) -> bool:
        """Build the ISO 9660 image"""
        try:
            self.log("INFO", f"Creating ISO: {self.output_path}")
            
            with open(self.output_path, 'wb') as iso_file:
                # System area (sectors 0-15)
                self.log("INFO", "Writing system area...")
                for i in range(16):
                    self.write_sector(b'\x00' * self.SECTOR_SIZE, iso_file)
                
                # Path table L (sector 1)
                self.log("INFO", "Writing path tables...")
                self.write_sector(b'\x00' * self.SECTOR_SIZE, iso_file)
                
                # Path table M (sector 2)
                self.write_sector(b'\x00' * self.SECTOR_SIZE, iso_file)
                
                # Root directory (sector 3)
                self.log("INFO", "Writing root directory...")
                root_dir = self.create_root_directory()
                self.write_sector(root_dir, iso_file)
                
                # Boot catalog (sector 4)
                if boot_image:
                    self.log("INFO", "Writing boot catalog...")
                    boot_cat = self.create_boot_catalog()
                    self.write_sector(boot_cat, iso_file)
                
                # Boot image sectors
                if boot_image and os.path.exists(boot_image):
                    self.log("INFO", f"Adding boot image: {boot_image}")
                    with open(boot_image, 'rb') as boot_file:
                        while True:
                            data = boot_file.read(self.SECTOR_SIZE)
                            if not data:
                                break
                            self.write_sector(data, iso_file)
                
                # Primary Volume Descriptor (sector 16)
                self.log("INFO", "Writing PVD...")
                pvd = self.create_pvd()
                iso_file.seek(16 * self.SECTOR_SIZE)
                iso_file.write(pvd)
                
                # Volume Descriptor Set Terminator (sector 17)
                terminator = bytearray(self.SECTOR_SIZE)
                terminator[0] = 0xFF
                terminator[1:6] = b'CD001'
                terminator[6] = 0x01
                iso_file.seek(17 * self.SECTOR_SIZE)
                iso_file.write(terminator)
                
                # Pad to 700 MB
                current_pos = iso_file.tell()
                total_size = 700 * 1024 * 1024
                remaining = total_size - current_pos
                
                if remaining > 0:
                    iso_file.write(b'\x00' * remaining)
            
            iso_size_mb = os.path.getsize(self.output_path) / (1024 * 1024)
            self.log("SUCCESS", f"ISO created: {iso_size_mb:.2f} MB ({self.sectors_written} sectors)")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Failed to create ISO: {e}")
            return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("استخدام / Usage: iso_builder.py <output.iso> [boot_image]")
        sys.exit(1)
    
    output_iso = sys.argv[1]
    boot_image = sys.argv[2] if len(sys.argv) > 2 else None
    
    builder = ISOBuilder(output_iso)
    
    os.makedirs(os.path.dirname(output_iso) or '.', exist_ok=True)
    
    if builder.build_iso(boot_image):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
