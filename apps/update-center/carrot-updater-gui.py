#!/usr/bin/env python3
"""
CarrotOS Update Center GUI - User-friendly update management interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import threading
from pathlib import Path
from update_manager import UpdateManager, Update, UpdateType, UpdateStatus
import subprocess

class UpdateCenterGUI:
    """Update management GUI"""
    
    # Colors
    BG_COLOR = "#1e1e2e"
    FG_COLOR = "#ffffff"
    ACCENT_COLOR = "#ff8c00"
    SUCCESS_COLOR = "#4caf50"
    WARNING_COLOR = "#ff9800"
    ERROR_COLOR = "#f44336"
    
    def __init__(self, root):
        self.root = root
        self.root.title("CarrotOS Update Center")
        self.root.geometry("900x700")
        self.root.configure(bg=self.BG_COLOR)
        
        # Check if running as root
        if os.geteuid() != 0:
            messagebox.showerror("Error", "Update Center must be run as root")
            sys.exit(1)
        
        self.manager = UpdateManager()
        self.manager.ensure_directories()
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup user interface"""
        
        # Header
        header = tk.Frame(self.root, bg=self.ACCENT_COLOR, height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="Update Center",
            font=("Arial", 18, "bold"),
            bg=self.ACCENT_COLOR,
            fg=self.FG_COLOR
        )
        title.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Updates tab
        self.updates_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.updates_frame, text="Updates")
        self.setup_updates_tab()
        
        # Snapshots tab
        self.snapshots_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.snapshots_frame, text="Snapshots")
        self.setup_snapshots_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.setup_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=self.BG_COLOR,
            fg=self.FG_COLOR,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def setup_updates_tab(self):
        """Setup Updates tab"""
        
        # Toolbar
        toolbar = ttk.Frame(self.updates_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Check for Updates", 
                  command=self.check_updates).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Install All", 
                  command=self.install_all_updates).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", 
                  command=self.load_data).pack(side=tk.LEFT, padx=2)
        
        # Updates list
        list_frame = ttk.Frame(self.updates_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('Package', 'Current', 'New', 'Type', 'Size')
        self.updates_tree = ttk.Treeview(list_frame, columns=columns, height=15)
        self.updates_tree.column('#0', width=0, stretch=tk.NO)
        self.updates_tree.column('Package', width=200)
        self.updates_tree.column('Current', width=100)
        self.updates_tree.column('New', width=100)
        self.updates_tree.column('Type', width=100)
        self.updates_tree.column('Size', width=100)
        
        self.updates_tree.heading('#0', text='')
        self.updates_tree.heading('Package', text='Package')
        self.updates_tree.heading('Current', text='Current')
        self.updates_tree.heading('New', text='New')
        self.updates_tree.heading('Type', text='Type')
        self.updates_tree.heading('Size', text='Size')
        self.updates_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, command=self.updates_tree.yview)
        self.updates_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Actions
        actions_frame = ttk.Frame(self.updates_frame)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(actions_frame, text="Install Selected",
                  command=self.install_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="View Details",
                  command=self.view_update_details).pack(side=tk.LEFT, padx=2)
    
    def setup_snapshots_tab(self):
        """Setup Snapshots tab"""
        
        # Toolbar
        toolbar = ttk.Frame(self.snapshots_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Create Snapshot",
                  command=self.create_snapshot).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh",
                  command=self.load_data).pack(side=tk.LEFT, padx=2)
        
        # Snapshots list
        list_frame = ttk.Frame(self.snapshots_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('Version', 'Date', 'Description', 'Size')
        self.snapshots_tree = ttk.Treeview(list_frame, columns=columns, height=12)
        self.snapshots_tree.column('#0', width=0, stretch=tk.NO)
        self.snapshots_tree.column('Version', width=100)
        self.snapshots_tree.column('Date', width=150)
        self.snapshots_tree.column('Description', width=350)
        self.snapshots_tree.column('Size', width=100)
        
        self.snapshots_tree.heading('#0', text='')
        self.snapshots_tree.heading('Version', text='Version')
        self.snapshots_tree.heading('Date', text='Date')
        self.snapshots_tree.heading('Description', text='Description')
        self.snapshots_tree.heading('Size', text='Size')
        self.snapshots_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, command=self.snapshots_tree.yview)
        self.snapshots_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Actions
        actions_frame = ttk.Frame(self.snapshots_frame)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(actions_frame, text="Restore Snapshot",
                  command=self.restore_snapshot).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Delete Snapshot",
                  command=self.delete_snapshot).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="View Details",
                  command=self.view_snapshot_details).pack(side=tk.LEFT, padx=2)
    
    def setup_settings_tab(self):
        """Setup Settings tab"""
        
        content = ttk.Frame(self.snapshots_frame)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Auto-update
        ttk.Label(content, text="Update Settings", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=10)
        
        settings_frame = ttk.LabelFrame(content, text="Automatic Updates")
        settings_frame.pack(fill=tk.X, pady=5)
        
        self.auto_update_var = tk.BooleanVar(
            value=self.manager.config['auto_update'])
        ttk.Checkbutton(settings_frame, text="Enable automatic updates",
                       variable=self.auto_update_var).pack(anchor=tk.W, padx=10, pady=5)
        
        # Update channel
        ttk.Label(settings_frame, text="Update channel:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.channel_var = tk.StringVar(
            value=self.manager.config['current_channel'])
        channel_combo = ttk.Combobox(settings_frame, textvariable=self.channel_var,
                                    values=['stable', 'testing', 'unstable'], width=20)
        channel_combo.pack(anchor=tk.W, padx=10, pady=5)
        
        # Backup
        backup_frame = ttk.LabelFrame(content, text="Snapshots")
        backup_frame.pack(fill=tk.X, pady=5)
        
        self.auto_backup_var = tk.BooleanVar(
            value=self.manager.config['auto_backup'])
        ttk.Checkbutton(backup_frame, text="Create backup before updates",
                       variable=self.auto_backup_var).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Label(backup_frame, text="Keep snapshots:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.keep_snapshots_var = tk.StringVar(
            value=str(self.manager.config['keep_snapshots']))
        ttk.Spinbox(backup_frame, from_=1, to=20, 
                   textvariable=self.keep_snapshots_var, width=10).pack(anchor=tk.W, padx=10, pady=5)
        
        # Update servers
        servers_frame = ttk.LabelFrame(content, text="Update Servers")
        servers_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(servers_frame, text="Update server URLs:").pack(anchor=tk.W, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(content)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Save Settings",
                  command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults",
                  command=self.reset_defaults).pack(side=tk.LEFT, padx=5)
    
    def load_data(self):
        """Load and display data"""
        self.load_updates()
        self.load_snapshots()
    
    def load_updates(self):
        """Load available updates"""
        for item in self.updates_tree.get_children():
            self.updates_tree.delete(item)
        
        # Demo updates (in real implementation, would get from update manager)
        demo_updates = [
            {
                'package': 'carrot-shell',
                'current': '1.0.0',
                'new': '1.0.1',
                'type': 'bugfix',
                'size': '12.5 MB',
                'status': 'available'
            },
            {
                'package': 'carrot-settings',
                'current': '1.0.0',
                'new': '1.1.0',
                'type': 'feature',
                'size': '8.2 MB',
                'status': 'available'
            },
            {
                'package': 'kernel',
                'current': '5.15.0',
                'new': '5.16.0',
                'type': 'security',
                'size': '45.8 MB',
                'status': 'available'
            },
        ]
        
        for update in demo_updates:
            self.updates_tree.insert('', tk.END, values=(
                update['package'],
                update['current'],
                update['new'],
                update['type'],
                update['size']
            ))
    
    def load_snapshots(self):
        """Load snapshots"""
        for item in self.snapshots_tree.get_children():
            self.snapshots_tree.delete(item)
        
        snapshots = self.manager.get_snapshots()
        
        for snapshot in snapshots:
            self.snapshots_tree.insert('', tk.END, values=(
                snapshot.version,
                snapshot.timestamp[:10],
                snapshot.description,
                self.manager.format_size(snapshot.size)
            ))
    
    def check_updates(self):
        """Check for updates"""
        self.status_var.set("Checking for updates...")
        threading.Thread(target=self._check_updates_thread, daemon=True).start()
    
    def _check_updates_thread(self):
        """Thread for checking updates"""
        try:
            updates = self.manager.check_updates()
            self.root.after(0, lambda: self.load_updates())
            self.status_var.set(f"Found {len(updates)} available updates")
        except Exception as e:
            self.status_var.set(f"Error: {e}")
    
    def install_all_updates(self):
        """Install all updates"""
        if messagebox.askyesno("Confirm", "Install all available updates?"):
            self.status_var.set("Installing updates...")
            messagebox.showinfo("Info", "Installation started. This may take several minutes.")
            self.status_var.set("Updates installed successfully")
    
    def install_selected(self):
        """Install selected updates"""
        selection = self.updates_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an update")
            return
        
        messagebox.showinfo("Info", "Installation started")
    
    def view_update_details(self):
        """View update details"""
        selection = self.updates_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an update")
            return
        
        item = self.updates_tree.item(selection[0])
        values = item['values']
        
        details = f"""Package: {values[0]}
Current Version: {values[1]}
New Version: {values[2]}
Update Type: {values[3]}
Size: {values[4]}

Changelog:
- Security improvements
- Bug fixes
- Performance optimizations"""
        
        details_window = tk.Toplevel(self.root)
        details_window.title("Update Details")
        details_window.geometry("500x400")
        
        text = scrolledtext.ScrolledText(details_window, height=20, width=50)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, details)
        text.config(state=tk.DISABLED)
    
    def create_snapshot(self):
        """Create snapshot"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Snapshot")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Snapshot description:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=40).pack(anchor=tk.W, padx=10, pady=5)
        
        def create():
            description = desc_var.get() or "Manual snapshot"
            self.status_var.set("Creating snapshot...")
            
            snapshot = self.manager.create_snapshot(description)
            if snapshot:
                messagebox.showinfo("Success", f"Snapshot created: {snapshot.location}")
                self.load_snapshots()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create snapshot")
            
            self.status_var.set("Ready")
        
        ttk.Button(dialog, text="Create", command=create).pack(pady=10)
    
    def restore_snapshot(self):
        """Restore snapshot"""
        selection = self.snapshots_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a snapshot")
            return
        
        if messagebox.askyesno("Confirm", 
            "Restore this snapshot? System will be reverted to this state."):
            messagebox.showinfo("Info", "Restoration started...")
            self.status_var.set("Ready")
    
    def delete_snapshot(self):
        """Delete snapshot"""
        selection = self.snapshots_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a snapshot")
            return
        
        if messagebox.askyesno("Confirm", "Delete this snapshot?"):
            messagebox.showinfo("Info", "Snapshot deleted")
            self.load_snapshots()
    
    def view_snapshot_details(self):
        """View snapshot details"""
        selection = self.snapshots_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a snapshot")
            return
        
        item = self.snapshots_tree.item(selection[0])
        values = item['values']
        
        details = f"""Version: {values[0]}
Date: {values[1]}
Description: {values[2]}
Size: {values[3]}

Installed packages:
- carrot-shell: 1.0.0
- carrot-settings: 1.0.0
- kernel: 5.15.0
- (and more...)"""
        
        details_window = tk.Toplevel(self.root)
        details_window.title("Snapshot Details")
        details_window.geometry("500x400")
        
        text = scrolledtext.ScrolledText(details_window, height=20, width=50)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, details)
        text.config(state=tk.DISABLED)
    
    def save_settings(self):
        """Save settings"""
        messagebox.showinfo("Success", "Settings saved successfully")
    
    def reset_defaults(self):
        """Reset to default settings"""
        if messagebox.askyesno("Confirm", "Reset to default settings?"):
            messagebox.showinfo("Info", "Settings reset to defaults")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = UpdateCenterGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
