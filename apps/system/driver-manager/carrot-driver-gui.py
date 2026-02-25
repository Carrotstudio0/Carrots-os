#!/usr/bin/env python3
"""
CarrotOS Driver Manager GUI - Manage hardware drivers
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import threading
from pathlib import Path

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

try:
    from driver_manager import DriverManager, DriverType, DriverStatus
except ImportError as e:
    print(f"Error: Could not import driver_manager: {e}")
    print("Make sure you're running from CarrotOS directory")
    sys.exit(1)

class DriverManagerGUI:
    """Driver management GUI"""
    
    # Colors
    BG_COLOR = "#1e1e2e"
    FG_COLOR = "#ffffff"
    ACCENT_COLOR = "#ff8c00"
    SUCCESS_COLOR = "#4caf50"
    WARNING_COLOR = "#ff9800"
    ERROR_COLOR = "#f44336"
    
    def __init__(self, root):
        self.root = root
        self.root.title("CarrotOS Driver Manager")
        self.root.geometry("900x650")
        self.root.configure(bg=self.BG_COLOR)
        
        # Check if running as root
        if os.geteuid() != 0:
            messagebox.showerror("Error", "Driver Manager must be run as root")
            sys.exit(1)
        
        self.manager = DriverManager()
        
        self.setup_ui()
        self.refresh_drivers()
    
    def setup_ui(self):
        """Setup user interface"""
        
        # Header
        header = tk.Frame(self.root, bg=self.ACCENT_COLOR, height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="Driver Manager",
            font=("Arial", 18, "bold"),
            bg=self.ACCENT_COLOR,
            fg=self.FG_COLOR
        )
        title.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(toolbar, text="Scan Hardware", 
                  command=self.scan_hardware).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Install Missing Drivers",
                  command=self.install_all_missing).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh",
                  command=self.refresh_drivers).pack(side=tk.LEFT, padx=2)
        
        # Notebook for categories
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # GPU Tab
        self.gpu_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gpu_frame, text="GPU Drivers")
        self.create_driver_tab(self.gpu_frame, DriverType.GPU)
        
        # Audio Tab
        self.audio_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.audio_frame, text="Audio")
        self.create_driver_tab(self.audio_frame, DriverType.AUDIO)
        
        # Wireless Tab
        self.wireless_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.wireless_frame, text="Wireless")
        self.create_driver_tab(self.wireless_frame, DriverType.WIRELESS)
        
        # Ethernet Tab
        self.ethernet_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ethernet_frame, text="Ethernet")
        self.create_driver_tab(self.ethernet_frame, DriverType.ETHERNET)
        
        # All Drivers Tab
        self.all_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.all_frame, text="All Drivers")
        self.setup_all_tab()
        
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
    
    def create_driver_tab(self, parent, driver_type: DriverType):
        """Create a driver category tab"""
        
        # Store reference for later updating
        tree = ttk.Treeview(parent, columns=('Device', 'Status', 'Package'), height=15)
        tree.column('#0', width=150, stretch=tk.NO)
        tree.column('Device', width=200)
        tree.column('Status', width=150)
        tree.column('Package', width=350)
        
        tree.heading('#0', text='Driver')
        tree.heading('Device', text='Device')
        tree.heading('Status', text='Status')
        tree.heading('Package', text='Package Name')
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def install_selected():
            selection = tree.selection()
            if selection:
                messagebox.showinfo("Info", "Installation started...")
        
        def view_details():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                messagebox.showinfo("Driver Details", "Details would appear here")
        
        ttk.Button(button_frame, text="Install Selected",
                  command=install_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="View Details",
                  command=view_details).pack(side=tk.LEFT, padx=2)
        
        # Store tree reference
        setattr(self, f'{driver_type.value}_tree', tree)
    
    def setup_all_tab(self):
        """Setup All Drivers tab"""
        
        tree = ttk.Treeview(self.all_frame, columns=('Type', 'Device', 'Status', 'Package'), height=20)
        tree.column('#0', width=150, stretch=tk.NO)
        tree.column('Type', width=100)
        tree.column('Device', width=150)
        tree.column('Status', width=120)
        tree.column('Package', width=350)
        
        tree.heading('#0', text='Driver')
        tree.heading('Type', text='Type')
        tree.heading('Device', text='Device')
        tree.heading('Status', text='Status')
        tree.heading('Package', text='Package')
        
        scrollbar = ttk.Scrollbar(self.all_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        
        self.all_tree = tree
    
    def refresh_drivers(self):
        """Refresh driver list"""
        self.status_var.set("Refreshing drivers...")
        threading.Thread(target=self._refresh_thread, daemon=True).start()
    
    def _refresh_thread(self):
        """Refresh in thread"""
        try:
            self.manager.detect_drivers()
            self.root.after(0, self._update_display)
            self.status_var.set("Ready")
        except Exception as e:
            self.status_var.set(f"Error: {e}")
    
    def _update_display(self):
        """Update driver display"""
        
        # Update each category tab
        for driver_type in [DriverType.GPU, DriverType.AUDIO, DriverType.WIRELESS, DriverType.ETHERNET]:
            drivers = self.manager.get_drivers_by_type(driver_type)
            tree_name = f'{driver_type.value}_tree'
            
            if hasattr(self, tree_name):
                tree = getattr(self, tree_name)
                # Clear existing items
                for item in tree.get_children():
                    tree.delete(item)
                
                # Add drivers
                for driver in drivers:
                    status_color = self.SUCCESS_COLOR if driver.status == DriverStatus.INSTALLED else self.ERROR_COLOR
                    tree.insert('', tk.END, values=(
                        driver.device_name,
                        driver.status.value,
                        driver.package_name or "N/A"
                    ))
        
        # Update All Drivers tab
        for item in self.all_tree.get_children():
            self.all_tree.delete(item)
        
        for driver in self.manager.drivers:
            self.all_tree.insert('', tk.END, values=(
                driver.driver_type.value,
                driver.device_name,
                driver.status.value,
                driver.package_name or "N/A"
            ))
    
    def scan_hardware(self):
        """Scan for hardware"""
        self.status_var.set("Scanning hardware...")
        self.refresh_drivers()
    
    def install_all_missing(self):
        """Install all missing drivers"""
        missing = self.manager.get_drivers_needing_installation()
        
        if not missing:
            messagebox.showinfo("Info", "All drivers are installed!")
            return
        
        if messagebox.askyesno("Confirm", 
            f"Install {len(missing)} missing drivers?\nThis may take several minutes."):
            self.status_var.set(f"Installing {len(missing)} drivers...")
            threading.Thread(target=self._install_thread, daemon=True).start()
    
    def _install_thread(self):
        """Install in thread"""
        try:
            installed, failed = self.manager.install_all_missing()
            self.root.after(0, lambda: messagebox.showinfo("Complete", 
                f"Installed: {installed}\nFailed: {failed}"))
            self.root.after(0, self._update_display)
            self.status_var.set("Ready")
        except Exception as e:
            self.status_var.set(f"Error: {e}")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = DriverManagerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
