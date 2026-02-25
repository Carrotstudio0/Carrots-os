#!/usr/bin/env python3
"""
CarrotOS userdel - Delete a system user
Usage: userdel [options] username
"""

import sys
import os
import shutil
from pathlib import Path

class UserDeleter:
    """Delete system users"""
    
    def __init__(self):
        self.passwd_file = Path("/etc/passwd")
        self.shadow_file = Path("/etc/shadow")
        self.group_file = Path("/etc/group")
        
    def find_user(self, username):
        """Find user in passwd file"""
        try:
            with open(self.passwd_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 1 and parts[0] == username:
                        return {
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
    
    def remove_user_from_file(self, filepath, username):
        """Remove user from a file (passwd, shadow, group)"""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            new_lines = [line for line in lines if not line.startswith(f"{username}:")]
            
            with open(filepath, 'w') as f:
                f.writelines(new_lines)
            
            return True
        except IOError as e:
            print(f"Error updating {filepath}: {e}", file=sys.stderr)
            return False
    
    def remove_user_from_groups(self, username):
        """Remove user from group membership lists"""
        try:
            with open(self.group_file, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                if line.startswith('#'):
                    new_lines.append(line)
                    continue
                
                parts = line.rstrip('\n').split(':')
                if len(parts) >= 4:
                    # Remove username from group members
                    members = parts[3].split(',') if parts[3] else []
                    members = [m for m in members if m != username]
                    parts[3] = ','.join(members)
                    new_lines.append(':'.join(parts) + '\n')
                else:
                    new_lines.append(line)
            
            with open(self.group_file, 'w') as f:
                f.writelines(new_lines)
            
            return True
        except IOError as e:
            print(f"Error updating {self.group_file}: {e}", file=sys.stderr)
            return False
    
    def delete_user(self, username, remove_home=True):
        """Delete a user account"""
        
        # Find user
        user = self.find_user(username)
        if not user:
            print(f"Error: User '{username}' not found", file=sys.stderr)
            return False
        
        # Prevent deletion of root user
        if user['uid'] == 0:
            print("Error: Cannot delete root user", file=sys.stderr)
            return False
        
        # Remove from passwd
        if not self.remove_user_from_file(self.passwd_file, username):
            return False
        
        # Remove from shadow
        if not self.remove_user_from_file(self.shadow_file, username):
            return False
        
        # Remove from group memberships
        if not self.remove_user_from_groups(username):
            return False
        
        # Remove user's primary group
        if not self.remove_user_from_file(self.group_file, username):
            return False
        
        # Remove home directory if requested
        if remove_home and user['home']:
            home_path = Path(user['home'])
            if home_path.exists():
                try:
                    shutil.rmtree(home_path)
                    print(f"Removed home directory: {user['home']}")
                except Exception as e:
                    print(f"Warning: Could not remove home directory: {e}", file=sys.stderr)
        
        print(f"User '{username}' deleted successfully")
        print(f"  UID: {user['uid']}")
        if remove_home and user['home']:
            print(f"  Home directory removed: {user['home']}")
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Delete a user from CarrotOS')
    parser.add_argument('username', help='Username to delete')
    parser.add_argument('-r', '--remove', action='store_true', dest='remove_home',
                       help='Remove user\'s home directory')
    parser.add_argument('-f', '--force', action='store_true', help='Force deletion')
    
    args = parser.parse_args()
    
    # Check for root
    if os.geteuid() != 0:
        print("Error: userdel must be run as root", file=sys.stderr)
        sys.exit(1)
    
    # Confirm deletion if not forced
    if not args.force:
        confirmation = input(f"Delete user '{args.username}'? (y/N): ").strip().lower()
        if confirmation != 'y':
            print("Cancelled")
            sys.exit(0)
    
    deleter = UserDeleter()
    success = deleter.delete_user(args.username, remove_home=args.remove_home)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
