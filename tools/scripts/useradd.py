#!/usr/bin/env python3
"""
CarrotOS useradd - Add a new user to the system
Usage: useradd [options] username
"""

import sys
import os
import subprocess
import hashlib
import crypt
from pathlib import Path
from datetime import datetime

class UserAdder:
    """Add new system users"""
    
    # Standard UID ranges
    SYSTEM_UID_MIN = 0
    SYSTEM_UID_MAX = 999
    USER_UID_MIN = 1000
    USER_UID_MAX = 60000
    
    SYSTEM_GID_MIN = 0
    SYSTEM_GID_MAX = 999
    USER_GID_MIN = 1000
    USER_GID_MAX = 60000
    
    def __init__(self):
        self.passwd_file = Path("/etc/passwd")
        self.shadow_file = Path("/etc/shadow")
        self.group_file = Path("/etc/group")
        
        self.uid = None
        self.gid = None
        self.home = None
        self.shell = "/bin/bash"
        self.comment = ""
        self.password = None
        self.system = False
        self.create_home = True
        
    def find_next_uid(self, system=False):
        """Find next available UID"""
        if system:
            uid_min = self.SYSTEM_UID_MIN
            uid_max = self.SYSTEM_UID_MAX
        else:
            uid_min = self.USER_UID_MIN
            uid_max = self.USER_UID_MAX
            
        used_uids = set()
        
        try:
            with open(self.passwd_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 3:
                        try:
                            used_uids.add(int(parts[2]))
                        except ValueError:
                            pass
        except FileNotFoundError:
            pass
            
        for uid in range(uid_min, uid_max + 1):
            if uid not in used_uids:
                return uid
                
        return None
    
    def find_next_gid(self, system=False):
        """Find next available GID"""
        if system:
            gid_min = self.SYSTEM_GID_MIN
            gid_max = self.SYSTEM_GID_MAX
        else:
            gid_min = self.USER_GID_MIN
            gid_max = self.USER_GID_MAX
            
        used_gids = set()
        
        try:
            with open(self.group_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 3:
                        try:
                            used_gids.add(int(parts[2]))
                        except ValueError:
                            pass
        except FileNotFoundError:
            pass
            
        for gid in range(gid_min, gid_max + 1):
            if gid not in used_gids:
                return gid
                
        return None
    
    def check_user_exists(self, username):
        """Check if user already exists"""
        try:
            with open(self.passwd_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 1 and parts[0] == username:
                        return True
        except FileNotFoundError:
            pass
        return False
    
    def hash_password(self, password):
        """Hash password using SHA512"""
        if password:
            return crypt.crypt(password, crypt.METHOD_SHA512)
        return "*"
    
    def create_new_user(self, username, uid=None, gid=None, home=None, shell=None, 
                       comment="", password=None, system=False, create_home=True):
        """Create a new user"""
        
        if self.check_user_exists(username):
            print(f"Error: User '{username}' already exists", file=sys.stderr)
            return False
        
        # Auto-assign UID if not provided
        if uid is None:
            uid = self.find_next_uid(system=system)
            if uid is None:
                print(f"Error: No available UIDs", file=sys.stderr)
                return False
        
        # Auto-assign same GID as UID for user groups
        if gid is None:
            gid = self.find_next_gid(system=system)
            if gid is None:
                print(f"Error: No available GIDs", file=sys.stderr)
                return False
        
        # Default home directory
        if home is None:
            if system:
                home = f"/var/{username}"
            else:
                home = f"/home/{username}"
        
        # Default shell
        if shell is None:
            shell = "/sbin/nologin" if system else "/bin/bash"
        
        # Hash the password
        password_hash = self.hash_password(password)
        
        # Get current date for shadow file
        days_since_epoch = (datetime.now() - datetime(1970, 1, 1)).days
        
        # Add passwd entry
        passwd_entry = f"{username}:x:{uid}:{gid}:{comment}:{home}:{shell}\n"
        
        try:
            with open(self.passwd_file, 'a') as f:
                f.write(passwd_entry)
        except IOError as e:
            print(f"Error writing /etc/passwd: {e}", file=sys.stderr)
            return False
        
        # Add shadow entry
        shadow_entry = f"{username}:{password_hash}:{days_since_epoch}:0:99999:7::\n"
        
        try:
            with open(self.shadow_file, 'a') as f:
                f.write(shadow_entry)
        except IOError as e:
            print(f"Error writing /etc/shadow: {e}", file=sys.stderr)
            return False
        
        # Add group entry (user's primary group)
        group_entry = f"{username}:!:{gid}:\n"
        
        try:
            with open(self.group_file, 'a') as f:
                f.write(group_entry)
        except IOError as e:
            print(f"Error writing /etc/group: {e}", file=sys.stderr)
            return False
        
        # Create home directory if requested
        if create_home and not system:
            try:
                os.makedirs(home, mode=0o700, exist_ok=True)
                # Set ownership (would need root)
                os.chown(home, uid, gid)
                
                # Create .bashrc and .profile
                bashrc = Path(home) / ".bashrc"
                bashrc.write_text("# .bashrc for CarrotOS\nexport PATH=$PATH:/usr/local/bin\nalias ll='ls -la'\n")
                os.chown(str(bashrc), uid, gid)
                
            except Exception as e:
                print(f"Warning: Could not create home directory: {e}", file=sys.stderr)
        
        print(f"User '{username}' created successfully")
        print(f"  UID: {uid}, GID: {gid}")
        print(f"  Home: {home}")
        print(f"  Shell: {shell}")
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add a new user to CarrotOS')
    parser.add_argument('username', help='Username to create')
    parser.add_argument('-u', '--uid', type=int, help='User ID')
    parser.add_argument('-g', '--gid', type=int, help='Group ID (default: same as UID)')
    parser.add_argument('-d', '--home', help='Home directory')
    parser.add_argument('-s', '--shell', help='Login shell (default: /bin/bash)')
    parser.add_argument('-c', '--comment', default='', help='User comment/GECOS field')
    parser.add_argument('-p', '--password', help='Password (plain text, will be hashed)')
    parser.add_argument('-r', '--system', action='store_true', help='Create system user')
    parser.add_argument('-M', '--no-create-home', action='store_true', help='Do not create home directory')
    
    args = parser.parse_args()
    
    # Check for root
    if os.geteuid() != 0:
        print("Error: useradd must be run as root", file=sys.stderr)
        sys.exit(1)
    
    adder = UserAdder()
    
    success = adder.create_new_user(
        username=args.username,
        uid=args.uid,
        gid=args.gid,
        home=args.home,
        shell=args.shell,
        comment=args.comment,
        password=args.password,
        system=args.system,
        create_home=not args.no_create_home
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
