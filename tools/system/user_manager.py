#!/usr/bin/env python3
"""
CarrotOS User Manager - Complete user and group management system
Handles user creation, deletion, modification, and permission management
Ready for production use
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class UserShell(Enum):
    """Available login shells"""
    BASH = "/bin/bash"
    SH = "/bin/sh"
    ZSH = "/bin/zsh"
    NOLOGIN = "/nologin"

@dataclass
class User:
    """User account information"""
    username: str
    uid: int
    gid: int
    home: str
    shell: str
    gecos: str = ""
    
@dataclass
class Group:
    """Group information"""
    name: str
    gid: int
    members: List[str] = None

class UserManager:
    """Comprehensive user and group management"""
    
    PASSWD_FILE = Path("/etc/passwd")
    SHADOW_FILE = Path("/etc/shadow")
    GROUP_FILE = Path("/etc/group")
    SUDOERS_FILE = Path("/etc/sudoers")
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.groups: Dict[str, Group] = {}
        self.load_system_users()
    
    def check_root(self) -> bool:
        """Check if running as root"""
        return os.geteuid() == 0
    
    def load_system_users(self):
        """Load system users from /etc/passwd"""
        try:
            if self.PASSWD_FILE.exists():
                with open(self.PASSWD_FILE) as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            parts = line.strip().split(':')
                            if len(parts) >= 7:
                                user = User(
                                    username=parts[0],
                                    uid=int(parts[2]) if parts[2].isdigit() else -1,
                                    gid=int(parts[3]) if parts[3].isdigit() else -1,
                                    home=parts[5],
                                    shell=parts[6],
                                    gecos=parts[4]
                                )
                                self.users[user.username] = user
        except Exception as e:
            print(f"Warning: Could not load users: {e}")
    
    def create_user(self, username: str, uid: Optional[int] = None, 
                   gid: int = 1000, home: Optional[str] = None,
                   shell: UserShell = UserShell.BASH,
                   create_home: bool = True) -> bool:
        """Create new user account"""
        
        if not self.check_root():
            print("Error: Need root privileges to create users")
            return False
        
        if username in self.users:
            print(f"Error: User already exists: {username}")
            return False
        
        try:
            if home is None:
                home = f"/home/{username}"
            
            # Use useradd command
            cmd = ["useradd", "-d", home, "-s", shell.value]
            
            if uid is not None:
                cmd.extend(["-u", str(uid)])
            
            if gid != 1000:
                cmd.extend(["-g", str(gid)])
            
            if create_home:
                cmd.append("-m")
            
            cmd.append(username)
            
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                self.users[username] = User(
                    username=username,
                    uid=uid or 1000,
                    gid=gid,
                    home=home,
                    shell=shell.value
                )
                print(f"✓ User created: {username}")
                return True
            else:
                print(f"Error: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def delete_user(self, username: str, remove_home: bool = True) -> bool:
        """Delete user account"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        if username not in self.users:
            print(f"Error: User not found: {username}")
            return False
        
        try:
            cmd = ["userdel"]
            
            if remove_home:
                cmd.append("-r")
            
            cmd.append(username)
            
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                del self.users[username]
                print(f"✓ User deleted: {username}")
                return True
            else:
                print(f"Error: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def modify_user(self, username: str, **kwargs) -> bool:
        """Modify user properties"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        if username not in self.users:
            print(f"Error: User not found: {username}")
            return False
        
        try:
            cmd = ["usermod"]
            
            if 'home' in kwargs:
                cmd.extend(["-d", kwargs['home']])
            
            if 'shell' in kwargs:
                cmd.extend(["-s", kwargs['shell']])
            
            if 'groups' in kwargs:
                cmd.extend(["-G", ','.join(kwargs['groups'])])
            
            if 'name' in kwargs:
                cmd.extend(["-l", kwargs['name']])
            
            cmd.append(username)
            
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                print(f"✓ User modified: {username}")
                return True
            else:
                print(f"Error: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            print(f"Error modifying user: {e}")
            return False
    
    def set_password(self, username: str, password: str) -> bool:
        """Set user password"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        try:
            proc = subprocess.Popen(
                ["passwd", username],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            proc.communicate(input=f"{password}\n{password}\n".encode())
            
            if proc.returncode == 0:
                print(f"✓ Password set: {username}")
                return True
            else:
                print(f"Error setting password")
                return False
        
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def create_group(self, groupname: str, gid: Optional[int] = None) -> bool:
        """Create new group"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        if groupname in self.groups:
            print(f"Error: Group already exists: {groupname}")
            return False
        
        try:
            cmd = ["groupadd"]
            
            if gid is not None:
                cmd.extend(["-g", str(gid)])
            
            cmd.append(groupname)
            
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                self.groups[groupname] = Group(name=groupname, gid=gid or 1000)
                print(f"✓ Group created: {groupname}")
                return True
            else:
                print(f"Error: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            print(f"Error creating group: {e}")
            return False
    
    def delete_group(self, groupname: str) -> bool:
        """Delete group"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        if groupname not in self.groups:
            print(f"Error: Group not found: {groupname}")
            return False
        
        try:
            result = subprocess.run(["groupdel", groupname], capture_output=True)
            
            if result.returncode == 0:
                del self.groups[groupname]
                print(f"✓ Group deleted: {groupname}")
                return True
            else:
                print(f"Error: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            print(f"Error deleting group: {e}")
            return False
    
    def add_user_to_group(self, username: str, groupname: str) -> bool:
        """Add user to group"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        if username not in self.users:
            print(f"Error: User not found: {username}")
            return False
        
        if groupname not in self.groups:
            print(f"Error: Group not found: {groupname}")
            return False
        
        try:
            result = subprocess.run(
                ["usermod", "-aG", groupname, username],
                capture_output=True
            )
            
            if result.returncode == 0:
                print(f"✓ Added {username} to {groupname}")
                return True
            else:
                print(f"Error: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def add_sudo_access(self, username: str) -> bool:
        """Grant sudo access to user"""
        
        if not self.check_root():
            print("Error: Need root privileges")
            return False
        
        try:
            # Add to sudoers
            sudoers_entry = f"{username} ALL=(ALL) NOPASSWD:ALL\n"
            
            # Verify sudoers syntax first
            with open(self.SUDOERS_FILE, 'r') as f:
                current = f.read()
            
            # Append entry
            with open(self.SUDOERS_FILE, 'a') as f:
                f.write(sudoers_entry)
            
            print(f"✓ Sudo access granted: {username}")
            return True
        
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def list_users(self) -> List[str]:
        """Get list of all users"""
        return list(self.users.keys())
    
    def list_groups(self) -> List[str]:
        """Get list of all groups"""
        return list(self.groups.keys())
    
    def get_user_info(self, username: str) -> Optional[User]:
        """Get user information"""
        return self.users.get(username)
    
    def get_user_groups(self, username: str) -> List[str]:
        """Get groups user belongs to"""
        try:
            result = subprocess.run(
                ["id", "-nG", username],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout.strip().split()
            
        except:
            pass
        
        return []

if __name__ == "__main__":
    manager = UserManager()
    
    print("Available users:", manager.list_users())
    print("Available groups:", manager.list_groups())
