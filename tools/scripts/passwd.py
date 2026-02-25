#!/usr/bin/env python3
"""
CarrotOS passwd - Change user password
Usage: passwd [options] [username]
"""

import sys
import os
import crypt
import getpass
from pathlib import Path
from datetime import datetime

class PasswordManager:
    """Manage user passwords"""
    
    def __init__(self):
        self.shadow_file = Path("/etc/shadow")
        self.passwd_file = Path("/etc/passwd")
    
    def find_user(self, username):
        """Find user in passwd file"""
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
    
    def find_shadow_entry(self, username):
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
    
    def hash_password(self, password):
        """Hash password using SHA512"""
        return crypt.crypt(password, crypt.METHOD_SHA512)
    
    def update_password(self, username, new_password):
        """Update user password"""
        
        if not self.find_user(username):
            print(f"Error: User '{username}' not found", file=sys.stderr)
            return False
        
        password_hash = self.hash_password(new_password)
        days_since_epoch = (datetime.now() - datetime(1970, 1, 1)).days
        
        try:
            with open(self.shadow_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    continue
                parts = line.strip().split(':')
                if len(parts) >= 1 and parts[0] == username:
                    # Update password and last change date
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
    
    def change_password(self, username, current_password=None, new_password=None, 
                       new_password_confirm=None):
        """Change password with validation"""
        
        # If not root and changing another user's password, deny
        if os.geteuid() != 0 and username != os.getlogin():
            print("Error: Only root can change another user's password", file=sys.stderr)
            return False
        
        # Prompt for current password if not root and changing own password
        if os.geteuid() != 0 and username == os.getlogin():
            if current_password is None:
                current_password = getpass.getpass(f"Changing password for {username}\nCurrent password: ")
            
            # Verify current password (simple check)
            shadow = self.find_shadow_entry(username)
            if shadow:
                supplied_hash = crypt.crypt(current_password, shadow['password'].split('$')[2])
                if supplied_hash != shadow['password']:
                    print("Error: Incorrect password", file=sys.stderr)
                    return False
        
        # Prompt for new password if not provided
        if new_password is None:
            new_password = getpass.getpass("New password: ")
        
        # Prompt for confirmation if not provided
        if new_password_confirm is None:
            new_password_confirm = getpass.getpass("Confirm new password: ")
        
        # Validate passwords match
        if new_password != new_password_confirm:
            print("Error: Passwords do not match", file=sys.stderr)
            return False
        
        # Validate password strength
        if len(new_password) < 8:
            print("Warning: Password is less than 8 characters (weak)", file=sys.stderr)
            confirm = input("Continue anyway? (y/N): ").strip().lower()
            if confirm != 'y':
                return False
        
        # Update password
        if not self.update_password(username, new_password):
            return False
        
        print(f"Password for user '{username}' updated successfully")
        return True
    
    def lock_password(self, username):
        """Lock user password (prepend ! to hash)"""
        try:
            with open(self.shadow_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    continue
                parts = line.strip().split(':')
                if len(parts) >= 1 and parts[0] == username:
                    if not parts[1].startswith('!'):
                        parts[1] = '!' + parts[1]
                    lines[i] = ':'.join(parts) + '\n'
                    break
            
            with open(self.shadow_file, 'w') as f:
                f.writelines(lines)
            
            print(f"Password for user '{username}' locked")
            return True
        except IOError as e:
            print(f"Error updating /etc/shadow: {e}", file=sys.stderr)
            return False
    
    def unlock_password(self, username):
        """Unlock user password (remove leading ! from hash)"""
        try:
            with open(self.shadow_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    continue
                parts = line.strip().split(':')
                if len(parts) >= 1 and parts[0] == username:
                    if parts[1].startswith('!'):
                        parts[1] = parts[1][1:]
                    lines[i] = ':'.join(parts) + '\n'
                    break
            
            with open(self.shadow_file, 'w') as f:
                f.writelines(lines)
            
            print(f"Password for user '{username}' unlocked")
            return True
        except IOError as e:
            print(f"Error updating /etc/shadow: {e}", file=sys.stderr)
            return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Change user password on CarrotOS')
    parser.add_argument('username', nargs='?', help='Username (default: current user)')
    parser.add_argument('-l', '--lock', action='store_true', help='Lock password')
    parser.add_argument('-u', '--unlock', action='store_true', help='Unlock password')
    parser.add_argument('-p', '--password', help='New password (non-interactive)')
    
    args = parser.parse_args()
    
    # Default to current user if not specified
    if args.username is None:
        try:
            args.username = os.getlogin()
        except:
            print("Error: Could not determine current user", file=sys.stderr)
            sys.exit(1)
    
    manager = PasswordManager()
    
    if args.lock:
        if os.geteuid() != 0:
            print("Error: Only root can lock passwords", file=sys.stderr)
            sys.exit(1)
        success = manager.lock_password(args.username)
    elif args.unlock:
        if os.geteuid() != 0:
            print("Error: Only root can unlock passwords", file=sys.stderr)
            sys.exit(1)
        success = manager.unlock_password(args.username)
    else:
        success = manager.change_password(args.username, new_password=args.password)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
