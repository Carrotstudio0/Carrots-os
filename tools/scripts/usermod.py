#!/usr/bin/env python3
"""
CarrotOS usermod - Modify a system user
Usage: usermod [options] username
"""

import sys
import os
import shutil
import crypt
from pathlib import Path
from datetime import datetime

class UserModifier:
    """Modify system users"""
    
    def __init__(self):
        self.passwd_file = Path("/etc/passwd")
        self.shadow_file = Path("/etc/shadow")
        self.group_file = Path("/etc/group")
        
    def find_user(self, username):
        """Find user in passwd file"""
        try:
            with open(self.passwd_file, 'r') as f:
                for idx, line in enumerate(f):
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 1 and parts[0] == username:
                        return {
                            'line_num': idx,
                            'name': parts[0],
                            'uid': int(parts[2]),
                            'gid': int(parts[3]),
                            'gecos': parts[4] if len(parts) > 4 else '',
                            'home': parts[5] if len(parts) > 5 else '',
                            'shell': parts[6] if len(parts) > 6 else ''
                        }
        except FileNotFoundError:
            pass
        return None
    
    def find_user_shadow(self, username):
        """Find user in shadow file"""
        try:
            with open(self.shadow_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 1 and parts[0] == username:
                        return {
                            'name': parts[0],
                            'password': parts[1] if len(parts) > 1 else '*',
                            'last_change': parts[2] if len(parts) > 2 else '0',
                            'min': parts[3] if len(parts) > 3 else '0',
                            'max': parts[4] if len(parts) > 4 else '99999',
                            'warn': parts[5] if len(parts) > 5 else '7',
                            'inactive': parts[6] if len(parts) > 6 else '',
                            'expire': parts[7] if len(parts) > 7 else ''
                        }
        except FileNotFoundError:
            pass
        return None
    
    def update_passwd_field(self, username, **kwargs):
        """Update passwd file fields"""
        try:
            with open(self.passwd_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    continue
                parts = line.strip().split(':')
                if len(parts) >= 1 and parts[0] == username:
                    # Update fields
                    if 'gecos' in kwargs:
                        parts[4] = kwargs['gecos']
                    if 'home' in kwargs:
                        parts[5] = kwargs['home']
                    if 'shell' in kwargs:
                        parts[6] = kwargs['shell']
                    if 'uid' in kwargs:
                        parts[2] = str(kwargs['uid'])
                    if 'gid' in kwargs:
                        parts[3] = str(kwargs['gid'])
                    
                    lines[i] = ':'.join(parts) + '\n'
                    break
            
            with open(self.passwd_file, 'w') as f:
                f.writelines(lines)
            return True
        except IOError as e:
            print(f"Error updating /etc/passwd: {e}", file=sys.stderr)
            return False
    
    def update_shadow_password(self, username, password):
        """Update password in shadow file"""
        password_hash = crypt.crypt(password, crypt.METHOD_SHA512) if password else '*'
        days_since_epoch = (datetime.now() - datetime(1970, 1, 1)).days
        
        try:
            with open(self.shadow_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    continue
                parts = line.strip().split(':')
                if len(parts) >= 1 and parts[0] == username:
                    parts[1] = password_hash
                    parts[2] = str(days_since_epoch)
                    lines[i] = ':'.join(parts) + '\n'
                    break
            
            with open(self.shadow_file, 'w') as f:
                f.writelines(lines)
            return True
        except IOError as e:
            print(f"Error updating /etc/shadow: {e}", file=sys.stderr)
            return False
    
    def add_to_group(self, username, groupname):
        """Add user to a group"""
        try:
            with open(self.group_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    continue
                parts = line.strip().split(':')
                if len(parts) >= 1 and parts[0] == groupname:
                    members = parts[3].split(',') if parts[3] else []
                    if username not in members:
                        members.append(username)
                    parts[3] = ','.join(members)
                    lines[i] = ':'.join(parts) + '\n'
                    break
            
            with open(self.group_file, 'w') as f:
                f.writelines(lines)
            return True
        except IOError as e:
            print(f"Error updating {self.group_file}: {e}", file=sys.stderr)
            return False
    
    def remove_from_group(self, username, groupname):
        """Remove user from a group"""
        try:
            with open(self.group_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    continue
                parts = line.strip().split(':')
                if len(parts) >= 1 and parts[0] == groupname:
                    members = parts[3].split(',') if parts[3] else []
                    members = [m for m in members if m != username]
                    parts[3] = ','.join(members)
                    lines[i] = ':'.join(parts) + '\n'
                    break
            
            with open(self.group_file, 'w') as f:
                f.writelines(lines)
            return True
        except IOError as e:
            print(f"Error updating {self.group_file}: {e}", file=sys.stderr)
            return False
    
    def move_home(self, username, old_home, new_home):
        """Move user home directory"""
        old_path = Path(old_home)
        new_path = Path(new_home)
        
        if not old_path.exists():
            print(f"Error: Current home directory {old_home} not found", file=sys.stderr)
            return False
        
        if new_path.exists():
            print(f"Error: New home directory {new_home} already exists", file=sys.stderr)
            return False
        
        try:
            shutil.move(str(old_path), str(new_path))
            print(f"Moved home directory from {old_home} to {new_home}")
            return True
        except Exception as e:
            print(f"Error moving home directory: {e}", file=sys.stderr)
            return False
    
    def modify_user(self, username, **modifiers):
        """Modify user account"""
        
        user = self.find_user(username)
        if not user:
            print(f"Error: User '{username}' not found", file=sys.stderr)
            return False
        
        changes = []
        
        # Handle each modification
        if 'comment' in modifiers:
            self.update_passwd_field(username, gecos=modifiers['comment'])
            changes.append(f"  Comment: {modifiers['comment']}")
        
        if 'home' in modifiers and modifiers['home'] != user['home']:
            # Move home directory if requested
            if modifiers.get('move_home'):
                if not self.move_home(username, user['home'], modifiers['home']):
                    return False
            
            self.update_passwd_field(username, home=modifiers['home'])
            changes.append(f"  Home: {modifiers['home']}")
        
        if 'shell' in modifiers:
            self.update_passwd_field(username, shell=modifiers['shell'])
            changes.append(f"  Shell: {modifiers['shell']}")
        
        if 'password' in modifiers:
            if not self.update_shadow_password(username, modifiers['password']):
                return False
            changes.append(f"  Password: updated")
        
        if 'groups' in modifiers:
            # Add to groups
            for group in modifiers['groups'].get('add', []):
                self.add_to_group(username, group)
                changes.append(f"  Added to group: {group}")
            
            # Remove from groups
            for group in modifiers['groups'].get('remove', []):
                self.remove_from_group(username, group)
                changes.append(f"  Removed from group: {group}")
        
        if changes:
            print(f"User '{username}' modified:")
            for change in changes:
                print(change)
            return True
        else:
            print("No changes specified")
            return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Modify a user on CarrotOS')
    parser.add_argument('username', help='Username to modify')
    parser.add_argument('-c', '--comment', help='Update comment/GECOS')
    parser.add_argument('-d', '--home', help='New home directory')
    parser.add_argument('-m', '--move-home', action='store_true', help='Move home directory')
    parser.add_argument('-s', '--shell', help='New login shell')
    parser.add_argument('-p', '--password', help='New password (plain text)')
    parser.add_argument('-a', '--append-groups', help='Add to groups (comma-separated)')
    parser.add_argument('-r', '--remove-from-groups', help='Remove from groups (comma-separated)')
    
    args = parser.parse_args()
    
    # Check for root
    if os.geteuid() != 0:
        print("Error: usermod must be run as root", file=sys.stderr)
        sys.exit(1)
    
    modifiers = {}
    
    if args.comment:
        modifiers['comment'] = args.comment
    if args.home:
        modifiers['home'] = args.home
        modifiers['move_home'] = args.move_home
    if args.shell:
        modifiers['shell'] = args.shell
    if args.password:
        modifiers['password'] = args.password
    
    if args.append_groups or args.remove_from_groups:
        modifiers['groups'] = {
            'add': args.append_groups.split(',') if args.append_groups else [],
            'remove': args.remove_from_groups.split(',') if args.remove_from_groups else []
        }
    
    if not modifiers:
        print("Error: No modifications specified", file=sys.stderr)
        sys.exit(1)
    
    modifier = UserModifier()
    success = modifier.modify_user(args.username, **modifiers)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
