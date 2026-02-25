#!/usr/bin/env python3
"""
CarrotOS groupmod - Modify a system group
Usage: groupmod [options] groupname
"""

import sys
import os
from pathlib import Path

class GroupModifier:
    """Modify system groups"""
    
    def __init__(self):
        self.group_file = Path("/etc/group")
    
    def find_group(self, groupname):
        """Find group in group file"""
        try:
            with open(self.group_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 1 and parts[0] == groupname:
                        return {
                            'name': parts[0],
                            'password': parts[1] if len(parts) > 1 else '!',
                            'gid': int(parts[2]) if len(parts) > 2 else 0,
                            'members': parts[3].split(',') if len(parts) > 3 and parts[3] else []
                        }
        except FileNotFoundError:
            pass
        return None
    
    def update_group_field(self, groupname, **kwargs):
        """Update group file fields"""
        try:
            with open(self.group_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    continue
                parts = line.strip().split(':')
                if len(parts) >= 1 and parts[0] == groupname:
                    # Update fields
                    if 'gid' in kwargs:
                        parts[2] = str(kwargs['gid'])
                    if 'members' in kwargs:
                        parts[3] = ','.join(kwargs['members'])
                    
                    lines[i] = ':'.join(parts) + '\n'
                    break
            
            with open(self.group_file, 'w') as f:
                f.writelines(lines)
            return True
        except IOError as e:
            print(f"Error updating /etc/group: {e}", file=sys.stderr)
            return False
    
    def gid_exists(self, gid, exclude_group=None):
        """Check if GID is already used"""
        try:
            with open(self.group_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 3:
                        try:
                            if int(parts[2]) == gid and (exclude_group is None or parts[0] != exclude_group):
                                return True
                        except ValueError:
                            pass
        except FileNotFoundError:
            pass
        return False
    
    def add_member(self, groupname, username):
        """Add member to group"""
        group = self.find_group(groupname)
        if not group:
            print(f"Error: Group '{groupname}' not found", file=sys.stderr)
            return False
        
        if username in group['members']:
            print(f"User '{username}' is already in group '{groupname}'")
            return True
        
        group['members'].append(username)
        return self.update_group_field(groupname, members=group['members'])
    
    def remove_member(self, groupname, username):
        """Remove member from group"""
        group = self.find_group(groupname)
        if not group:
            print(f"Error: Group '{groupname}' not found", file=sys.stderr)
            return False
        
        if username not in group['members']:
            print(f"User '{username}' is not in group '{groupname}'")
            return True
        
        group['members'] = [m for m in group['members'] if m != username]
        return self.update_group_field(groupname, members=group['members'])
    
    def modify_group(self, groupname, **modifiers):
        """Modify group account"""
        
        group = self.find_group(groupname)
        if not group:
            print(f"Error: Group '{groupname}' not found", file=sys.stderr)
            return False
        
        changes = []
        
        # Handle GID change
        if 'gid' in modifiers:
            new_gid = modifiers['gid']
            if self.gid_exists(new_gid, exclude_group=groupname):
                print(f"Error: GID {new_gid} is already in use", file=sys.stderr)
                return False
            
            self.update_group_field(groupname, gid=new_gid)
            changes.append(f"  GID: {new_gid}")
        
        # Handle add members
        if 'add_members' in modifiers:
            for username in modifiers['add_members']:
                if username not in group['members']:
                    group['members'].append(username)
                    changes.append(f"  Added member: {username}")
            
            self.update_group_field(groupname, members=group['members'])
        
        # Handle remove members
        if 'remove_members' in modifiers:
            for username in modifiers['remove_members']:
                if username in group['members']:
                    group['members'] = [m for m in group['members'] if m != username]
                    changes.append(f"  Removed member: {username}")
            
            self.update_group_field(groupname, members=group['members'])
        
        if changes:
            print(f"Group '{groupname}' modified:")
            for change in changes:
                print(change)
            return True
        else:
            print("No changes specified")
            return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Modify a group on CarrotOS')
    parser.add_argument('groupname', help='Group name to modify')
    parser.add_argument('-g', '--gid', type=int, help='Change group ID')
    parser.add_argument('-a', '--add-members', help='Add members (comma-separated)')
    parser.add_argument('-r', '--remove-members', help='Remove members (comma-separated)')
    
    args = parser.parse_args()
    
    # Check for root
    if os.geteuid() != 0:
        print("Error: groupmod must be run as root", file=sys.stderr)
        sys.exit(1)
    
    modifiers = {}
    
    if args.gid:
        modifiers['gid'] = args.gid
    
    if args.add_members:
        modifiers['add_members'] = [m.strip() for m in args.add_members.split(',')]
    
    if args.remove_members:
        modifiers['remove_members'] = [m.strip() for m in args.remove_members.split(',')]
    
    if not modifiers:
        print("Error: No modifications specified", file=sys.stderr)
        sys.exit(1)
    
    modifier = GroupModifier()
    success = modifier.modify_group(args.groupname, **modifiers)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
