#!/usr/bin/env python3
"""
CarrotOS Update Manager - System and Application Update System
Handles system updates, application updates, and rollback functionality
"""

import os
import sys
import json
import hashlib
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import tarfile
import tempfile

class UpdateType(Enum):
    """Update types"""
    SECURITY = "security"
    BUGFIX = "bugfix"
    FEATURE = "feature"
    SYSTEM = "system"

class UpdateStatus(Enum):
    """Update status"""
    AVAILABLE = "available"
    DOWNLOADED = "downloaded"
    INSTALLED = "installed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class Update:
    """Update information"""
    package: str
    version: str
    from_version: str
    update_type: UpdateType
    description: str
    size: int  # bytes
    timestamp: str
    checksum: str
    status: UpdateStatus = UpdateStatus.AVAILABLE
    changelog: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'package': self.package,
            'version': self.version,
            'from_version': self.from_version,
            'update_type': self.update_type.value,
            'description': self.description,
            'size': self.size,
            'timestamp': self.timestamp,
            'checksum': self.checksum,
            'status': self.status.value,
            'changelog': self.changelog,
        }

@dataclass
class Snapshot:
    """System snapshot for rollback"""
    version: str
    timestamp: str
    description: str
    packages: Dict[str, str]  # package: version
    size: int  # bytes
    checksum: str
    location: str  # path to snapshot

class UpdateManager:
    """Manage system and application updates"""
    
    UPDATE_DIR = Path("/var/lib/carrot-updater")
    CACHE_DIR = Path("/var/cache/carrot-updater")
    LOG_FILE = Path("/var/log/carrot-updates.log")
    SNAPSHOT_DIR = Path("/var/lib/carrot-snapshots")
    CONFIG_FILE = Path("/etc/carrot-updater/config.json")
    INSTALLED_FILE = UPDATE_DIR / "installed.json"
    SNAPSHOTS_FILE = UPDATE_DIR / "snapshots.json"
    
    def __init__(self):
        self.updates: List[Update] = []
        self.snapshots: List[Snapshot] = []
        self.config = self.load_config()
        self.installed_packages = self.load_installed()
        self.available_snapshots = self.load_snapshots()
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        for d in [self.UPDATE_DIR, self.CACHE_DIR, self.SNAPSHOT_DIR]:
            d.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> dict:
        """Load update configuration"""
        if self.CONFIG_FILE.exists():
            try:
                return json.loads(self.CONFIG_FILE.read_text())
            except:
                pass
        
        # Default configuration
        return {
            'auto_update': True,
            'check_interval': 86400,  # 24 hours
            'auto_backup': True,
            'keep_snapshots': 5,
            'update_servers': [
                'https://updates.carrotos.dev/stable',
                'https://mirrors.carrotos.dev/updates',
            ],
            'update_channels': ['stable', 'testing'],
            'current_channel': 'stable',
        }
    
    def load_installed(self) -> Dict[str, str]:
        """Load installed packages"""
        if self.INSTALLED_FILE.exists():
            try:
                return json.loads(self.INSTALLED_FILE.read_text())
            except:
                pass
        return {}
    
    def load_snapshots(self) -> List[Snapshot]:
        """Load snapshot information"""
        if self.SNAPSHOTS_FILE.exists():
            try:
                data = json.loads(self.SNAPSHOTS_FILE.read_text())
                return [Snapshot(**s) for s in data]
            except:
                pass
        return []
    
    def save_snapshots(self):
        """Save snapshot information"""
        data = [asdict(s) for s in self.available_snapshots]
        self.SNAPSHOTS_FILE.write_text(json.dumps(data, indent=2))
    
    def log(self, message: str, level: str = "INFO"):
        """Log message"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        self.LOG_FILE.write_text(self.LOG_FILE.read_text() + log_entry, 'a')
        print(log_entry.strip())
    
    def check_updates(self) -> List[Update]:
        """Check for available updates"""
        self.log("Checking for updates...")
        
        updates = []
        
        # In real implementation, would query update servers
        # For now, return empty list
        
        self.updates = updates
        self.log(f"Found {len(updates)} available updates")
        return updates
    
    def get_available_updates(self) -> List[Update]:
        """Get available updates"""
        return self.updates
    
    def download_update(self, update: Update) -> bool:
        """Download update package"""
        self.log(f"Downloading update: {update.package} {update.version}")
        
        try:
            # In real implementation, would download from update server
            cache_file = self.CACHE_DIR / f"{update.package}_{update.version}.carrot"
            
            if not cache_file.exists():
                self.log(f"Download package to {cache_file}")
                # Simulate download
                cache_file.touch()
            
            # Verify checksum
            if not self.verify_checksum(cache_file, update.checksum):
                self.log(f"Checksum verification failed for {update.package}", "ERROR")
                return False
            
            update.status = UpdateStatus.DOWNLOADED
            self.log(f"Update downloaded successfully: {cache_file}")
            return True
        
        except Exception as e:
            self.log(f"Download failed: {e}", "ERROR")
            return False
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            actual_checksum = sha256_hash.hexdigest()
            return actual_checksum == expected_checksum
        except:
            return False
    
    def create_snapshot(self, description: str) -> Optional[Snapshot]:
        """Create system snapshot for rollback"""
        self.log(f"Creating system snapshot: {description}")
        
        try:
            # Get current system version
            version_file = Path("/etc/carrotos-release")
            if version_file.exists():
                version = version_file.read_text().strip()
            else:
                version = "unknown"
            
            # Create backup of important directories
            snapshot_name = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            snapshot_path = self.SNAPSHOT_DIR / snapshot_name
            snapshot_path.mkdir(parents=True, exist_ok=True)
            
            # Backup important files
            backup_dirs = [
                '/etc',
                '/var/lib/carrot-updater',
                '/usr/local',
            ]
            
            for source_dir in backup_dirs:
                if Path(source_dir).exists():
                    dest = snapshot_path / source_dir.lstrip('/')
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(source_dir, str(dest), dirs_exist_ok=True)
            
            # Create snapshot metadata
            snapshot = Snapshot(
                version=version,
                timestamp=datetime.now().isoformat(),
                description=description,
                packages=self.installed_packages.copy(),
                size=self.get_directory_size(snapshot_path),
                checksum=self.calculate_directory_checksum(snapshot_path),
                location=str(snapshot_path),
            )
            
            self.available_snapshots.append(snapshot)
            self.save_snapshots()
            
            # Keep only N recent snapshots
            if len(self.available_snapshots) > self.config['keep_snapshots']:
                # Remove oldest
                oldest = self.available_snapshots[0]
                shutil.rmtree(oldest.location, ignore_errors=True)
                self.available_snapshots.pop(0)
                self.save_snapshots()
            
            self.log(f"Snapshot created: {snapshot_name} ({self.format_size(snapshot.size)})")
            return snapshot
        
        except Exception as e:
            self.log(f"Snapshot creation failed: {e}", "ERROR")
            return None
    
    def install_update(self, update: Update) -> bool:
        """Install an update"""
        self.log(f"Installing update: {update.package} {update.version}")
        
        try:
            # Create pre-update snapshot
            if self.config['auto_backup']:
                self.create_snapshot(f"Before update: {update.package} {update.from_version}->{update.version}")
            
            # Extract and apply update
            cache_file = self.CACHE_DIR / f"{update.package}_{update.version}.carrot"
            
            if not cache_file.exists():
                self.log(f"Update package not found: {cache_file}", "ERROR")
                return False
            
            # In real implementation, would extract and apply
            # For now, just log it
            
            # Update installed packages
            self.installed_packages[update.package] = update.version
            self.INSTALLED_FILE.write_text(json.dumps(self.installed_packages, indent=2))
            
            update.status = UpdateStatus.INSTALLED
            self.log(f"Update installed successfully: {update.package} {update.version}")
            return True
        
        except Exception as e:
            update.status = UpdateStatus.FAILED
            self.log(f"Installation failed: {e}", "ERROR")
            return False
    
    def rollback_to_snapshot(self, snapshot: Snapshot) -> bool:
        """Rollback to a previous snapshot"""
        self.log(f"Rolling back to snapshot: {snapshot.version} ({snapshot.timestamp})")
        
        try:
            if not Path(snapshot.location).exists():
                self.log(f"Snapshot location not found: {snapshot.location}", "ERROR")
                return False
            
            # Create pre-rollback snapshot
            self.create_snapshot(f"Before rollback to {snapshot.timestamp}")
            
            # Restore files
            snapshot_path = Path(snapshot.location)
            
            for backup_item in snapshot_path.rglob('*'):
                if backup_item.is_file():
                    # Calculate relative path
                    rel_path = backup_item.relative_to(snapshot_path)
                    target_path = Path('/') / rel_path
                    
                    # Restore file
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_item, target_path)
            
            # Restore installed packages
            self.installed_packages = snapshot.packages.copy()
            self.INSTALLED_FILE.write_text(json.dumps(self.installed_packages, indent=2))
            
            self.log(f"Rollback completed successfully")
            return True
        
        except Exception as e:
            self.log(f"Rollback failed: {e}", "ERROR")
            return False
    
    def get_snapshots(self) -> List[Snapshot]:
        """Get available snapshots"""
        return self.available_snapshots
    
    def delete_snapshot(self, snapshot: Snapshot) -> bool:
        """Delete a snapshot"""
        try:
            shutil.rmtree(snapshot.location, ignore_errors=True)
            self.available_snapshots.remove(snapshot)
            self.save_snapshots()
            self.log(f"Snapshot deleted: {snapshot.location}")
            return True
        except Exception as e:
            self.log(f"Failed to delete snapshot: {e}", "ERROR")
            return False
    
    @staticmethod
    def get_directory_size(directory: Path) -> int:
        """Calculate directory size"""
        total = 0
        for item in directory.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total
    
    @staticmethod
    def calculate_directory_checksum(directory: Path) -> str:
        """Calculate checksum of directory contents"""
        sha256_hash = hashlib.sha256()
        for file_path in sorted(directory.rglob('*')):
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    sha256_hash.update(f.read())
        return sha256_hash.hexdigest()
    
    @staticmethod
    def format_size(size: int) -> str:
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def get_update_history(self) -> List[Dict]:
        """Get update history"""
        history = []
        
        if self.LOG_FILE.exists():
            for line in self.LOG_FILE.read_text().split('\n'):
                if '[INFO]' in line or '[ERROR]' in line:
                    history.append({'log': line})
        
        return history
    
    def cleanup_cache(self, keep_days: int = 7):
        """Cleanup old cache files"""
        self.log(f"Cleaning cache (keep {keep_days} days)")
        
        cutoff = datetime.now().timestamp() - (keep_days * 86400)
        
        for cache_file in self.CACHE_DIR.glob('*'):
            if cache_file.stat().st_mtime < cutoff:
                cache_file.unlink()
                self.log(f"Removed cached file: {cache_file.name}")

# Example usage
def main():
    """Test update manager"""
    manager = UpdateManager()
    manager.ensure_directories()
    
    # Check for updates
    updates = manager.check_updates()
    print(f"Available updates: {len(updates)}")
    
    # Get snapshots
    snapshots = manager.get_snapshots()
    print(f"Available snapshots: {len(snapshots)}")
    
    # Create snapshot
    snapshot = manager.create_snapshot("Test snapshot")
    if snapshot:
        print(f"Snapshot created: {snapshot.location}")

if __name__ == '__main__':
    main()
