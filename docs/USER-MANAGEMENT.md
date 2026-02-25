# CarrotOS User Management System

Complete user and group management system for CarrotOS with CLI tools and GUI interface.

## 📋 System Files

### /etc/passwd - User Database
- **Location**: `/rootfs/base/etc/passwd`
- **Format**: `username:x:uid:gid:comment:home:shell`
- **Permissions**: 644 (world readable)
- **Contains**: User account information
- **Entries**:
  - **System users** (UID 0-999): root, daemon, bin, sys, mail, backup, www-data, etc.
  - **Regular users** (UID 1000+): user, admin, guest, developer

### /etc/shadow - Password Database
- **Location**: `/rootfs/base/etc/shadow`
- **Format**: `username:password_hash:last_changed:min:max:warn:inactive:expire`
- **Permissions**: 000 (root only) ⚠️
- **Contains**: Hashed passwords and password aging information
- **Hashing**: SHA512 (bcrypt compatible)
- **Password Policy**:
  - Minimum age: 0 days
  - Maximum age: 99999 days
  - Warning period: 7 days before expiration
  - Inactive period: (empty - never locks account)

### /etc/group - Group Database
- **Location**: `/rootfs/base/etc/group`
- **Format**: `groupname:password:gid:members`
- **Permissions**: 644 (world readable)
- **Contains**: Group information and membership
- **Entries**:
  - **System groups** (GID 0-999): System administration and service groups
  - **User groups** (GID 1000+): Primary groups for regular users
  - **Special groups**:
    - `sudo` (GID 27): Members can execute sudo commands
    - `wheel`: Alternate sudo group (if applicable)

### /etc/sudoers - Sudo Configuration
- **Location**: `/rootfs/base/etc/sudoers`
- **Format**: Sudo policy language
- **Permissions**: 440 (root:root only)
- **Edit**: NEVER edit directly - use `visudo` command
- **Policies**:
  - root: Full access (ALL=(ALL:ALL) ALL)
  - %sudo group: Full access without password
  - admin user: Specific command access without password
  - developer user: Development tools access
  - user account: Limited command access

## 🛠️ CLI Tools

### useradd - Add New User

**Location**: `/tools/scripts/useradd.py`

**Usage**:
```bash
sudo useradd [options] username
```

**Options**:
- `-u, --uid UID`: Specific user ID (auto-assigned if not provided)
- `-g, --gid GID`: Group ID (defaults to UID)
- `-d, --home DIR`: Home directory (default: /home/username)
- `-s, --shell SHELL`: Login shell (default: /bin/bash)
- `-c, --comment TEXT`: User comment/GECOS field
- `-p, --password PASS`: Password (plain text, will be hashed)
- `-r, --system`: Create system user
- `-M, --no-create-home`: Don't create home directory

**UID Ranges**:
- System UIDs: 0-999
- Regular UIDs: 1000-60000

**Examples**:
```bash
# Add regular user
sudo useradd -d /home/john -s /bin/bash -c "John Doe" john

# Add system user
sudo useradd -r -s /sbin/nologin -M www

# Add user with password
sudo useradd -p mypassword user_name

# Auto-assign UID/GID
sudo useradd newuser
```

### userdel - Delete User

**Location**: `/tools/scripts/userdel.py`

**Usage**:
```bash
sudo userdel [options] username
```

**Options**:
- `-r, --remove`: Remove home directory
- `-f, --force`: Force deletion without confirmation

**Examples**:
```bash
# Delete user and home directory
sudo userdel -r username

# Force delete without confirmation
sudo userdel -f username

# Delete user only (keep home directory)
sudo userdel username
```

**Safety**: 
- Cannot delete root user
- Requires confirmation unless -f flag used
- Home directory preserved by default

### usermod - Modify User

**Location**: `/tools/scripts/usermod.py`

**Usage**:
```bash
sudo usermod [options] username
```

**Options**:
- `-c, --comment TEXT`: Change comment/GECOS
- `-d, --home DIR`: Change home directory
- `-m, --move-home`: Move existing home directory to new location
- `-s, --shell SHELL`: Change login shell
- `-p, --password PASS`: Change password
- `-a, --append-groups GROUPS`: Add to groups (comma-separated)
- `-r, --remove-from-groups GROUPS`: Remove from groups

**Examples**:
```bash
# Change shell
sudo usermod -s /sbin/nologin username

# Change home directory and move files
sudo usermod -d /home/newdir -m username

# Add user to groups
sudo usermod -a admin,developers username

# Change password
sudo usermod -p newpassword username

# Change comment
sudo usermod -c "New Full Name" username
```

### groupadd - Add New Group

**Location**: `/tools/scripts/groupadd.py`

**Usage**:
```bash
sudo groupadd [options] groupname
```

**Options**:
- `-g, --gid GID`: Specific group ID
- `-r, --system`: Create system group
- `-U, --members USERS`: Initial members (comma-separated)

**GID Ranges**:
- System GIDs: 0-999
- Regular GIDs: 1000-60000

**Examples**:
```bash
# Create regular group
sudo groupadd developers

# Create system group
sudo groupadd -r sysadmin

# Create group with members
sudo groupadd -U "user1,user2" project_team

# Create with specific GID
sudo groupadd -g 2000 team_a
```

### groupmod - Modify Group

**Location**: `/tools/scripts/groupmod.py`

**Usage**:
```bash
sudo groupmod [options] groupname
```

**Options**:
- `-g, --gid GID`: Change group ID
- `-a, --add-members USERS`: Add members (comma-separated)
- `-r, --remove-members USERS`: Remove members

**Examples**:
```bash
# Add members to group
sudo groupmod -a user1,user2 developers

# Remove members from group
sudo groupmod -r user3 developers

# Change group ID
sudo groupmod -g 2005 developers

# Add and remove in one command
sudo groupmod -a newuser -r olduser developers
```

### passwd - Change Password

**Location**: `/tools/scripts/passwd.py`

**Usage**:
```bash
passwd [options] [username]
```

**Options**:
- `-l, --lock`: Lock password (prepend ! to hash)
- `-u, --unlock`: Unlock password (remove !)
- `-p, --password PASS`: Set password (non-interactive)

**Examples**:
```bash
# Change own password (interactive)
passwd

# Change another user's password (root only)
sudo passwd username

# Lock user account
sudo passwd -l username

# Unlock user account
sudo passwd -u username

# Set password non-interactively
sudo passwd -p newpassword username
```

**Security**:
- Regular users can only change their own password
- Root can change any user's password
- Passwords must be 8+ characters (warning if shorter)
- Interactive mode prompts for confirmation

## 🖥️ GUI Tools

### CarrotOS User Manager

**Location**: `/apps/user-manager/carrot-users.py`

**Launch**:
```bash
sudo python3 /apps/user-manager/carrot-users.py
```

**Requires**: Root privileges

**Features**:

#### Users Tab
- **View**: List all system users with UID, GID, home, shell
- **Add User**: Create new user with custom settings
- **Edit User**: Modify user properties (shell, comment)
- **Delete User**: Remove user and optionally home directory
- **Change Password**: Set new password for any user
- **Refresh**: Reload user list

#### Groups Tab
- **View**: List all groups with GID and members
- **Add Group**: Create new group
- **Edit Group**: Add/remove members from group
- **Delete Group**: Remove group (not yet implemented)
- **Refresh**: Reload group list

#### Security Tab
- **Sudo Management**:
  - Add user to sudo group
  - Remove user from sudo group
- **Password Policies**: View current policy settings
- **System Information**: UID/GID range information

## 📚 Common Tasks

### Create New Administrator

```bash
# Add admin user with sudo access
sudo useradd -u 1001 -g 1001 -d /home/admin -s /bin/bash -c "Administrator" admin

# Add to sudo group (already in sudoers for admin user)
sudo groupmod -a admin sudo
```

### Create Service User

```bash
# Create non-interactive system user
sudo useradd -r -s /sbin/nologin -M -d /var/service service_name
```

### Set Up Development Team

```bash
# Create developers group
sudo groupadd developers

# Add users to group
sudo groupmod -a dev1,dev2,dev3 developers

# Grant sudo access to group
```

### Lock/Unlock Account

```bash
# Lock account (disable login)
sudo passwd -l username

# Unlock account
sudo passwd -u username
```

### Reset User Password

```bash
# As root, set new password
sudo passwd -p newpassword username

# Or interactively
sudo passwd username
```

### Transfer Files to New Home

```bash
# Create new home directory and copy files
sudo useradd -d /home/newhome username
sudo usermod -d /home/newhome -m olduser
```

## 🔒 Security Considerations

### File Permissions
```
-rw-r--r-- /etc/passwd        # User readable
---------- /etc/shadow        # Root only (must be 000)
-rw-r--r-- /etc/group         # User readable
-r--r----- /etc/sudoers       # Root readable
```

### Password Security
- ✅ Stored as SHA512 hashes
- ✅ Minimum 8 characters recommended
- ✅ Interactive mode requires confirmation
- ✅ Password aging enforced (99999 day max)
- ✅ Shadow file protects password hashes

### Sudo Security
- ✅ Sudo group for administration
- ✅ Command-specific restrictions available
- ✅ Logging to /var/log/sudo.log
- ✅ Rootkit protection with command validation

### Best Practices
1. Use strong passwords (8+ characters, mix case/numbers)
2. Create separate admin account instead of using root
3. Use sudo group rather than root account
4. Lock inactive user accounts
5. Regularly audit /etc/sudoers file
6. Change default passwords immediately

## 📊 System Architecture

### UID/GID Allocation
- **0**: Root user/group
- **1-99**: System accounts
- **100-999**: Local system accounts
- **1000-60000**: Regular user accounts

### User Database Files
```
/etc/passwd       ← User account information
/etc/shadow       ← Hashed passwords (protected)
/etc/group        ← Group information
/etc/sudoers      ← Sudo access control
/var/log/sudo.log ← Sudo command history
```

### Tool Integration
```
useradd    ──┐
userdel    ──┤
usermod    ──┼──> /etc/passwd + /etc/shadow + /etc/group
groupadd   ──┤
groupmod   ──┤
passwd     ──┘

carrot-users.py (GUI) ──> Calls above CLI tools via subprocess
```

## 🐛 Troubleshooting

### "Only root can..."
**Solution**: Use `sudo` to run the command
```bash
sudo useradd newuser
```

### UID already in use
**Solution**: Specify different UID or let system auto-assign
```bash
sudo useradd -u 1005 newuser
```

### Home directory already exists
**Solution**: Use specific home directory or move existing
```bash
sudo useradd -d /home/newlocation username
```

### Password not accepted
**Solution**: Verify shadow file permissions and hashes
```bash
ls -la /etc/shadow
sudo passwd -p newpass username
```

### User stays in group after removal
**Solution**: Manually edit /etc/group or use groupmod
```bash
sudo groupmod -r username groupname
```

## 📝 File Formats

### /etc/passwd Format
```
username:x:uid:gid:comment:home:shell
admin:x:1001:1001:Administrator:/home/admin:/bin/bash
```

### /etc/shadow Format
```
username:password_hash:last_change:min:max:warn:inactive:expire
admin:$6$saltstring$hash:19000:0:99999:7::
```

### /etc/group Format
```
groupname:x:gid:member1,member2,member3
sudo:x:27:admin,user
```

## 🚀 Advanced Usage

### Batch User Creation
```bash
# Create multiple users from file
for user in user1 user2 user3; do
    sudo useradd -d /home/$user $user
done
```

### User Statistics
```bash
# Count total users
wc -l /etc/passwd

# List system users
awk -F: '$3 < 1000 {print}' /etc/passwd

# List regular users
awk -F: '$3 >= 1000 {print}' /etc/passwd
```

### Sudo Without Password
Edit `/etc/sudoers` with visudo:
```
admin ALL=(ALL) NOPASSWD: ALL
```

## 📖 References

- Standard Linux user management
- Linux Standard Base (LSB) compliance
- POSIX user/group standards
- Shadow password suite
- Sudo documentation
