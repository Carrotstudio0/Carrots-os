#!/usr/bin/env python3
"""
CarrotOS groupadd - Create a new system group
Usage: groupadd [options] groupname
"""

import sys
import os
from pathlib import Path

class GroupAdder:
    """Add new system groups"""
    
    SYSTEM_GID_MIN = 0
    SYSTEM_GID_MAX = 999
    USER_GID_MIN = 1000
    USER_GID_MAX = 60000
    
    def __init__(self):
        self.group_file = Path("/etc/group")
    
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
    
    def group_exists(self, groupname):
        """Check if group already exists"""
        try:
            with open(self.group_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 1 and parts[0] == groupname:
                        return True
        except FileNotFoundError:
            pass
        return False
    
    def gid_exists(self, gid):
        """Check if GID is already used"""
        try:
            with open(self.group_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 3:
                        try:
                            if int(parts[2]) == gid:
                                return True
                        except ValueError:
                            pass
        except FileNotFoundError:
            pass
        return False
    
    def add_group(self, groupname, gid=None, system=False, members=None):
        """Add a new group"""
        
        if self.group_exists(groupname):
            print(f"Error: Group '{groupname}' already exists", file=sys.stderr)
            return False
        
        # Auto-assign GID if not provided
        if gid is None:
            gid = self.find_next_gid(system=system)
            if gid is None:
                print(f"Error: No available GIDs", file=sys.stderr)
                return False
        else:
            # Check if specified GID is available
            if self.gid_exists(gid):
                print(f"Error: GID {gid} is already in use", file=sys.stderr)
                return False
        
        # Prepare members list
        members_str = ''
        if members:
            members_str = ','.join(members)
        
        # Group entry format: groupname:password:gid:members
        group_entry = f"{groupname}:!:{gid}:{members_str}\n"
        
        try:
            with open(self.group_file, 'a') as f:
                f.write(group_entry)
        except IOError as e:
            print(f"Error writing /etc/group: {e}", file=sys.stderr)
            return False
        
        print(f"Group '{groupname}' created successfully")
        print(f"  GID: {gid}")
        if members:
            print(f"  Members: {', '.join(members)}")
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add a new group to CarrotOS')
    parser.add_argument('groupname', help='Group name to create')
    parser.add_argument('-g', '--gid', type=int, help='Group ID')
    parser.add_argument('-r', '--system', action='store_true', help='Create system group')
    parser.add_argument('-U', '--members', help='Initial members (comma-separated)')
    
    args = parser.parse_args()
    
    # Check for root
    if os.geteuid() != 0:
        print("Error: groupadd must be run as root", file=sys.stderr)
        sys.exit(1)
    
    members = None
    if args.members:
        members = [m.strip() for m in args.members.split(',')]
    
    adder = GroupAdder()
    success = adder.add_group(
        groupname=args.groupname,
        gid=args.gid,
        system=args.system,
        members=members
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
