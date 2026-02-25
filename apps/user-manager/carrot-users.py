#!/usr/bin/env python3
"""
CarrotOS User Management GUI
A comprehensive graphical interface for managing system users and groups
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class UserManagerGUI:
    """User and Group Management GUI Interface"""
    
    # Colors
    BG_COLOR = "#1e1e2e"
    FG_COLOR = "#ffffff"
    BUTTON_COLOR = "#ff8c00"
    BUTTON_HOVER = "#ffa33c"
    SUCCESS_COLOR = "#4caf50"
    WARNING_COLOR = "#ff9800"
    ERROR_COLOR = "#f44336"
    ADMIN_USER = "admin"
    
    def __init__(self, root):
        self.root = root
        self.root.title("CarrotOS User Manager")
        self.root.geometry("900x600")
        self.root.configure(bg=self.BG_COLOR)
        
        # Check if running as root
        if os.geteuid() != 0:
            messagebox.showerror("Error", "This application must be run as root")
            sys.exit(1)
        
        self.setup_ui()
        self.load_users()
        self.load_groups()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Users tab
        self.users_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.users_frame, text="Users")
        self.setup_users_tab()
        
        # Groups tab
        self.groups_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.groups_frame, text="Groups")
        self.setup_groups_tab()
        
        # Security tab
        self.security_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.security_frame, text="Security")
        self.setup_security_tab()
    
    def setup_users_tab(self):
        """Setup Users management tab"""
        
        # Toolbar
        toolbar = ttk.Frame(self.users_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Add User", command=self.add_user_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit User", command=self.edit_user_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete User", command=self.delete_user_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Change Password", command=self.change_password_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=self.load_users).pack(side=tk.LEFT, padx=2)
        
        # Users list
        list_frame = ttk.Frame(self.users_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Columns
        columns = ('Username', 'UID', 'GID', 'Home', 'Shell')
        self.users_tree = ttk.Treeview(list_frame, columns=columns, height=15)
        self.users_tree.column('#0', width=0, stretch=tk.NO)
        self.users_tree.column('Username', anchor=tk.W, width=120)
        self.users_tree.column('UID', anchor=tk.CENTER, width=60)
        self.users_tree.column('GID', anchor=tk.CENTER, width=60)
        self.users_tree.column('Home', anchor=tk.W, width=250)
        self.users_tree.column('Shell', anchor=tk.W, width=200)
        
        self.users_tree.heading('#0', text='', anchor=tk.W)
        self.users_tree.heading('Username', text='Username', anchor=tk.W)
        self.users_tree.heading('UID', text='UID', anchor=tk.CENTER)
        self.users_tree.heading('GID', text='GID', anchor=tk.CENTER)
        self.users_tree.heading('Home', text='Home Directory', anchor=tk.W)
        self.users_tree.heading('Shell', text='Shell', anchor=tk.W)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscroll=scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_groups_tab(self):
        """Setup Groups management tab"""
        
        # Toolbar
        toolbar = ttk.Frame(self.groups_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Add Group", command=self.add_group_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit Group", command=self.edit_group_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Group", command=self.delete_group_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=self.load_groups).pack(side=tk.LEFT, padx=2)
        
        # Groups list
        list_frame = ttk.Frame(self.groups_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('Group Name', 'GID', 'Members')
        self.groups_tree = ttk.Treeview(list_frame, columns=columns, height=15)
        self.groups_tree.column('#0', width=0, stretch=tk.NO)
        self.groups_tree.column('Group Name', anchor=tk.W, width=150)
        self.groups_tree.column('GID', anchor=tk.CENTER, width=80)
        self.groups_tree.column('Members', anchor=tk.W, width=600)
        
        self.groups_tree.heading('#0', text='', anchor=tk.W)
        self.groups_tree.heading('Group Name', text='Group Name', anchor=tk.W)
        self.groups_tree.heading('GID', text='GID', anchor=tk.CENTER)
        self.groups_tree.heading('Members', text='Members', anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.groups_tree.yview)
        self.groups_tree.configure(yscroll=scrollbar.set)
        
        self.groups_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_security_tab(self):
        """Setup Security settings tab"""
        
        content = ttk.Frame(self.security_frame)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sudo group section
        ttk.Label(content, text="Sudo Group Management", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=10)
        
        sudo_frame = ttk.LabelFrame(content, text="Sudo Privileges")
        sudo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(sudo_frame, text="Add User to Sudo Group", 
                  command=self.add_to_sudo).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(sudo_frame, text="Remove User from Sudo", 
                  command=self.remove_from_sudo).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Password policies section
        ttk.Label(content, text="Password Policies", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 0))
        
        policy_info = """
        Current Password Policy:
        • Minimum password age: 0 days
        • Maximum password age: 99999 days
        • Password warning period: 7 days
        • Minimum password length: 8 characters (recommended)
        • Hashing algorithm: SHA512
        
        To change policies, edit /etc/login.defs (system-wide)
        or use passwd -x, passwd -n commands.
        """
        
        ttk.Label(content, text=policy_info, justify=tk.LEFT).pack(anchor=tk.W, pady=5)
        
        # System information
        ttk.Label(content, text="System Information", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 0))
        
        info_frame = ttk.Frame(content)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"System User UID Range: 0-999").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Regular User UID Range: 1000-60000").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"System Group GID Range: 0-999").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Regular Group GID Range: 1000-60000").pack(anchor=tk.W)
    
    def load_users(self):
        """Load users from /etc/passwd"""
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        try:
            with open('/etc/passwd', 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 7:
                        username = parts[0]
                        uid = parts[2]
                        gid = parts[3]
                        home = parts[5]
                        shell = parts[6]
                        
                        self.users_tree.insert('', tk.END, values=(username, uid, gid, home, shell))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {e}")
    
    def load_groups(self):
        """Load groups from /etc/group"""
        # Clear existing items
        for item in self.groups_tree.get_children():
            self.groups_tree.delete(item)
        
        try:
            with open('/etc/group', 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split(':')
                    if len(parts) >= 4:
                        groupname = parts[0]
                        gid = parts[2]
                        members = parts[3] if parts[3] else "(no members)"
                        
                        self.groups_tree.insert('', tk.END, values=(groupname, gid, members))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load groups: {e}")
    
    def add_user_dialog(self):
        """Dialog to add new user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New User")
        dialog.geometry("400x400")
        
        # Username
        ttk.Label(dialog, text="Username:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var).pack(fill=tk.X, padx=10, pady=5)
        
        # Home directory
        ttk.Label(dialog, text="Home Directory:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        home_var = tk.StringVar(value="/home/")
        ttk.Entry(dialog, textvariable=home_var).pack(fill=tk.X, padx=10, pady=5)
        
        # Shell
        ttk.Label(dialog, text="Login Shell:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        shell_var = tk.StringVar(value="/bin/bash")
        ttk.Combobox(dialog, textvariable=shell_var, 
                    values=["/bin/bash", "/bin/sh", "/sbin/nologin"]).pack(fill=tk.X, padx=10, pady=5)
        
        # System user checkbox
        system_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="System User", variable=system_var).pack(anchor=tk.W, padx=10, pady=5)
        
        # Password
        ttk.Label(dialog, text="Password (optional):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        password_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=password_var, show="*").pack(fill=tk.X, padx=10, pady=5)
        
        def create_user():
            username = username_var.get()
            home = home_var.get()
            shell = shell_var.get()
            password = password_var.get()
            system = system_var.get()
            
            if not username:
                messagebox.showerror("Error", "Username is required")
                return
            
            try:
                cmd = ['python3', '/usr/local/bin/useradd.py', username]
                if home and not system:
                    cmd.extend(['-d', home])
                if shell:
                    cmd.extend(['-s', shell])
                if password:
                    cmd.extend(['-p', password])
                if system:
                    cmd.append('-r')
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"User '{username}' created successfully")
                    self.load_users()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", result.stderr)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Create User", command=create_user).pack(pady=10)
    
    def edit_user_dialog(self):
        """Dialog to edit selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to edit")
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        
        if username == "root":
            messagebox.showwarning("Warning", "Cannot edit root user")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit User: {username}")
        dialog.geometry("400x300")
        
        # Shell
        ttk.Label(dialog, text="Login Shell:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        shell_var = tk.StringVar(value=item['values'][4])
        ttk.Combobox(dialog, textvariable=shell_var,
                    values=["/bin/bash", "/bin/sh", "/sbin/nologin"]).pack(fill=tk.X, padx=10, pady=5)
        
        # Comment
        ttk.Label(dialog, text="Comment:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        comment_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=comment_var).pack(fill=tk.X, padx=10, pady=5)
        
        def save_changes():
            try:
                shell = shell_var.get()
                comment = comment_var.get()
                
                cmd = ['python3', '/usr/local/bin/usermod.py', username]
                if shell:
                    cmd.extend(['-s', shell])
                if comment:
                    cmd.extend(['-c', comment])
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"User '{username}' updated successfully")
                    self.load_users()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", result.stderr)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).pack(pady=10)
    
    def delete_user_dialog(self):
        """Dialog to delete selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        
        if username == "root":
            messagebox.showerror("Error", "Cannot delete root user")
            return
        
        if messagebox.askyesno("Confirm", f"Delete user '{username}'?\n\nThis will also remove the home directory."):
            try:
                cmd = ['python3', '/usr/local/bin/userdel.py', '-r', username]
                result = subprocess.run(cmd, capture_output=True, text=True, input='y\n')
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"User '{username}' deleted successfully")
                    self.load_users()
                else:
                    messagebox.showerror("Error", result.stderr)
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def change_password_dialog(self):
        """Dialog to change user password"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Change Password: {username}")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="New Password:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        password_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=password_var, show="*").pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dialog, text="Confirm Password:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        confirm_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=confirm_var, show="*").pack(fill=tk.X, padx=10, pady=5)
        
        def set_password():
            if password_var.get() != confirm_var.get():
                messagebox.showerror("Error", "Passwords don't match")
                return
            
            try:
                cmd = ['python3', '/usr/local/bin/passwd.py', '-p', password_var.get(), username]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"Password for '{username}' changed successfully")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", result.stderr)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Change Password", command=set_password).pack(pady=10)
    
    def add_group_dialog(self):
        """Dialog to add new group"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Group")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="Group Name:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        groupname_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=groupname_var).pack(fill=tk.X, padx=10, pady=5)
        
        system_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="System Group", variable=system_var).pack(anchor=tk.W, padx=10, pady=5)
        
        def create_group():
            groupname = groupname_var.get()
            if not groupname:
                messagebox.showerror("Error", "Group name is required")
                return
            
            try:
                cmd = ['python3', '/usr/local/bin/groupadd.py', groupname]
                if system_var.get():
                    cmd.append('-r')
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"Group '{groupname}' created successfully")
                    self.load_groups()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", result.stderr)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Create Group", command=create_group).pack(pady=10)
    
    def edit_group_dialog(self):
        """Dialog to edit selected group"""
        selection = self.groups_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a group to edit")
            return
        
        item = self.groups_tree.item(selection[0])
        groupname = item['values'][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Group: {groupname}")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="Add Members (comma-separated):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        add_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=add_var).pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dialog, text="Remove Members (comma-separated):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        remove_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=remove_var).pack(fill=tk.X, padx=10, pady=5)
        
        def save_changes():
            try:
                cmd = ['python3', '/usr/local/bin/groupmod.py', groupname]
                if add_var.get():
                    cmd.extend(['-a', add_var.get()])
                if remove_var.get():
                    cmd.extend(['-r', remove_var.get()])
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"Group '{groupname}' updated")
                    self.load_groups()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", result.stderr)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).pack(pady=10)
    
    def delete_group_dialog(self):
        """Dialog to delete selected group"""
        selection = self.groups_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a group to delete")
            return
        
        item = self.groups_tree.item(selection[0])
        groupname = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete group '{groupname}'?"):
            messageboxshowinfo("Info", "Group deletion is not yet implemented\nEdit the /etc/group file directly")
    
    def add_to_sudo(self):
        """Add user to sudo group"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add User to Sudo")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Username:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var).pack(fill=tk.X, padx=10, pady=5)
        
        def add_sudo():
            username = username_var.get()
            if not username:
                messagebox.showerror("Error", "Username is required")
                return
            
            try:
                cmd = ['python3', '/usr/local/bin/groupmod.py', 'sudo', '-a', username]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"User '{username}' added to sudo group")
                    self.load_groups()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", result.stderr)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Add to Sudo", command=add_sudo).pack(pady=10)
    
    def remove_from_sudo(self):
        """Remove user from sudo group"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Remove User from Sudo")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Username:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        username_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=username_var).pack(fill=tk.X, padx=10, pady=5)
        
        def remove_sudo():
            username = username_var.get()
            if not username:
                messagebox.showerror("Error", "Username is required")
                return
            
            try:
                cmd = ['python3', '/usr/local/bin/groupmod.py', 'sudo', '-r', username]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    messagebox.showinfo("Success", f"User '{username}' removed from sudo group")
                    self.load_groups()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", result.stderr)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Remove from Sudo", command=remove_sudo).pack(pady=10)

def main():
    """Main entry point"""
    root = tk.Tk()
    app = UserManagerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
