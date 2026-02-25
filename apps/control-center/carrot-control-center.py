#!/usr/bin/env python3
"""
Carrot Control Center - Comprehensive system control panel
Main dashboard for system management, monitoring, and configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import subprocess
import sys
import os
from pathlib import Path

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

# Try to import psutil
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not available - some features disabled")

# Import system managers
try:
    from update_manager import UpdateManager
    from power_manager import PowerManager, PowerProfile
    from driver_manager import DriverManager
    from theme_engine import ThemeManager
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    print("Make sure you're in CarrotOS directory and tools/ folder exists")

class CarrotControlCenter:
    """Main control center GUI"""
    
    # Theme colors
    BG_PRIMARY = "#1e1e2e"
    BG_SECONDARY = "#2a2a3e"
    FG_PRIMARY = "#ffffff"
    ACCENT_COLOR = "#ff8c00"
    SUCCESS_COLOR = "#4caf50"
    WARNING_COLOR = "#ff9800"
    ERROR_COLOR = "#f44336"
    
    def __init__(self, root):
        self.root = root
        self.root.title("Carrot Control Center")
        self.root.geometry("1200x700")
        self.root.configure(bg=self.BG_PRIMARY)
        
        # Initialize managers
        self.update_manager = UpdateManager()
        self.power_manager = PowerManager()
        self.driver_manager = DriverManager()
        self.theme_manager = ThemeManager()
        
        # Monitoring thread
        self.monitoring = True
        self.monitor_thread = None
        
        self.setup_ui()
        self.start_monitoring()
    
    def setup_ui(self):
        """Setup main UI"""
        
        # Header
        header = tk.Frame(self.root, bg=self.ACCENT_COLOR, height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="🥕 Carrot Control Center",
            font=("Arial", 18, "bold"),
            bg=self.ACCENT_COLOR,
            fg=self.FG_PRIMARY
        )
        title.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Sidebar navigation
        sidebar = tk.Frame(self.root, bg=self.BG_SECONDARY, width=200)
        sidebar.pack(fill=tk.Y, side=tk.LEFT)
        sidebar.pack_propagate(False)
        
        self.nav_buttons = {}
        sections = [
            ('Dashboard', self.show_dashboard),
            ('Performance', self.show_performance),
            ('Power', self.show_power),
            ('Updates', self.show_updates),
            ('Drivers', self.show_drivers),
            ('Display', self.show_display),
            ('Sound', self.show_sound),
            ('Network', self.show_network),
            ('Appearance', self.show_appearance),
            ('About', self.show_about),
        ]
        
        for section, command in sections:
            btn = tk.Button(
                sidebar,
                text=section,
                command=command,
                bg=self.BG_SECONDARY,
                fg=self.FG_PRIMARY,
                activebackground=self.ACCENT_COLOR,
                activeforeground=self.FG_PRIMARY,
                border=0,
                font=("Arial", 10),
                padx=20,
                pady=15
            )
            btn.pack(fill=tk.X)
            self.nav_buttons[section] = btn
        
        # Main content area
        self.content_frame = tk.Frame(self.root, bg=self.BG_PRIMARY)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Show dashboard initially
        self.show_dashboard()
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Dashboard view"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="System Dashboard",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # System info grid
        grid_frame = ttk.Frame(self.content_frame)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # CPU info
        cpu_box = self.create_info_box(grid_frame, "CPU", "0%", self.ACCENT_COLOR)
        cpu_box.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.cpu_label = cpu_box
        
        # Memory info
        mem_box = self.create_info_box(grid_frame, "Memory", "0%", self.WARNING_COLOR)
        mem_box.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.mem_label = mem_box
        
        # Disk info
        disk_box = self.create_info_box(grid_frame, "Disk", "0%", self.ERROR_COLOR)
        disk_box.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.disk_label = disk_box
        
        # System temp
        temp_box = self.create_info_box(grid_frame, "Temp", "0°C", self.SUCCESS_COLOR)
        temp_box.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.temp_label = temp_box
        
        # Details frame
        details = ttk.LabelFrame(self.content_frame, text="System Information")
        details.pack(fill=tk.X, pady=20)
        
        try:
            import platform
            info_text = f"""
Host:        {platform.node()}
OS:          CarrotOS
Kernel:      {platform.release()}
Architecture: {platform.machine()}
Python:      {platform.python_version()}
"""
            
            info_label = tk.Label(
                details,
                text=info_text,
                bg=self.BG_SECONDARY,
                fg=self.FG_PRIMARY,
                justify=tk.LEFT,
                font=("Courier", 10)
            )
            info_label.pack(padx=10, pady=10)
        except:
            pass
    
    def create_info_box(self, parent, title, value, color):
        """Create info box widget"""
        box = tk.Frame(parent, bg=self.BG_SECONDARY, border=2, relief=tk.RAISED)
        
        title_label = tk.Label(
            box,
            text=title,
            bg=self.BG_SECONDARY,
            fg=color,
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=10)
        
        value_label = tk.Label(
            box,
            text=value,
            bg=self.BG_SECONDARY,
            fg=self.FG_PRIMARY,
            font=("Arial", 20, "bold")
        )
        value_label.pack(pady=10)
        
        box.value_label = value_label
        return box
    
    def show_performance(self):
        """Performance monitoring view"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Performance Monitor",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Performance metrics
        metrics_frame = ttk.LabelFrame(self.content_frame, text="System Metrics")
        metrics_frame.pack(fill=tk.BOTH, expand=True)
        
        # CPU cores
        cpu_frame = ttk.Frame(metrics_frame)
        cpu_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(cpu_frame, text="CPU Cores:").pack(side=tk.LEFT)
        ttk.Label(cpu_frame, text=f"{psutil.cpu_count()} cores").pack(side=tk.LEFT, padx=10)
        
        # Processes
        proc_frame = ttk.Frame(metrics_frame)
        proc_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(proc_frame, text="Running Processes:").pack(side=tk.LEFT)
        ttk.Label(proc_frame, text=f"{len(psutil.pids())} processes").pack(side=tk.LEFT, padx=10)
        
        # Uptime
        uptime_frame = ttk.Frame(metrics_frame)
        uptime_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(uptime_frame, text="System Uptime:").pack(side=tk.LEFT)
        
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        ttk.Label(uptime_frame, text=f"{hours}h {minutes}m").pack(side=tk.LEFT, padx=10)
        
        # Process list
        process_frame = ttk.LabelFrame(self.content_frame, text="Top Processes")
        process_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollable text widget
        scrollbar = ttk.Scrollbar(process_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        process_text = tk.Text(
            process_frame,
            height=10,
            bg=self.BG_SECONDARY,
            fg=self.FG_PRIMARY,
            yscrollcommand=scrollbar.set
        )
        process_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=process_text.yview)
        
        # Get top processes
        processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']),
                          key=lambda p: p.info['cpu_percent'],
                          reverse=True)[:10]
        
        process_text.insert(tk.END, "PID\tName\t\t\tCPU%\n")
        process_text.insert(tk.END, "-" * 50 + "\n")
        
        for proc in processes:
            try:
                pid = proc.info['pid']
                name = proc.info['name'][:20]
                cpu = proc.info['cpu_percent']
                
                process_text.insert(tk.END, f"{pid}\t{name}\t\t{cpu:.1f}%\n")
            except:
                pass
        
        process_text.config(state=tk.DISABLED)
    
    def show_power(self):
        """Power settings view"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Power Management",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Power profile selection
        profile_frame = ttk.LabelFrame(self.content_frame, text="Power Profile")
        profile_frame.pack(fill=tk.X, padx=10, pady=10)
        
        profile_var = tk.StringVar(value=self.power_manager.current_profile.value)
        
        profiles = [
            ('Performance', PowerProfile.PERFORMANCE),
            ('Balanced', PowerProfile.BALANCED),
            ('Power Saver', PowerProfile.POWER_SAVER),
        ]
        
        for label, profile in profiles:
            rb = ttk.Radiobutton(
                profile_frame,
                text=label,
                variable=profile_var,
                value=profile.value,
                command=lambda p=profile: self.power_manager.set_profile(p)
            )
            rb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Brightness control
        brightness_frame = ttk.LabelFrame(self.content_frame, text="Screen Brightness")
        brightness_frame.pack(fill=tk.X, padx=10, pady=10)
        
        brightness_value = tk.IntVar(value=self.power_manager.get_screen_brightness())
        
        scale = ttk.Scale(
            brightness_frame,
            from_=10,
            to=100,
            variable=brightness_value,
            orient=tk.HORIZONTAL,
            command=lambda val: self.power_manager.set_screen_brightness(int(float(val)))
        )
        scale.pack(fill=tk.X, padx=10, pady=10)
        
        # Battery info
        battery = self.power_manager.get_battery_info()
        if battery:
            battery_frame = ttk.LabelFrame(self.content_frame, text="Battery")
            battery_frame.pack(fill=tk.X, padx=10, pady=10)
            
            for key, value in battery.items():
                row = ttk.Frame(battery_frame)
                row.pack(fill=tk.X, padx=10, pady=5)
                
                ttk.Label(row, text=f"{key.replace('_', ' ').title()}:").pack(side=tk.LEFT)
                ttk.Label(row, text=str(value)).pack(side=tk.LEFT, padx=10)
    
    def show_updates(self):
        """Updates view"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="System Updates",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Check for updates button
        ttk.Button(
            self.content_frame,
            text="Check for Updates",
            command=self.check_updates
        ).pack(pady=10)
        
        # Updates list
        updates_frame = ttk.LabelFrame(self.content_frame, text="Available Updates")
        updates_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(updates_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.updates_text = tk.Text(
            updates_frame,
            height=10,
            bg=self.BG_SECONDARY,
            fg=self.FG_PRIMARY,
            yscrollcommand=scrollbar.set
        )
        self.updates_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.updates_text.yview)
        
        self.updates_text.insert(tk.END, "Click 'Check for Updates' to scan for available updates\n")
    
    def check_updates(self):
        """Check for updates"""
        self.updates_text.insert(tk.END, "\nChecking for updates...\n")
        self.updates_text.see(tk.END)
        
        updates = self.update_manager.check_updates()
        
        if updates:
            self.updates_text.insert(tk.END, f"Found {len(updates)} updates:\n")
            for update in updates:
                self.updates_text.insert(tk.END,
                    f"  • {update.package} {update.from_version} → {update.version}\n")
        else:
            self.updates_text.insert(tk.END, "System is up to date!\n")
        
        self.updates_text.see(tk.END)
    
    def show_drivers(self):
        """Drivers view"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Hardware Drivers",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Auto install button
        ttk.Button(
            self.content_frame,
            text="Auto Install Missing Drivers",
            command=self.auto_install_drivers
        ).pack(pady=10)
        
        # Drivers list
        drivers_frame = ttk.LabelFrame(self.content_frame, text="Detected Devices")
        drivers_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(drivers_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.drivers_text = tk.Text(
            drivers_frame,
            height=10,
            bg=self.BG_SECONDARY,
            fg=self.FG_PRIMARY,
            yscrollcommand=scrollbar.set
        )
        self.drivers_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.drivers_text.yview)
        
        # Detect drivers
        self.driver_manager.detect_drivers()
        drivers = self.driver_manager.get_all_drivers()
        
        if drivers:
            self.drivers_text.insert(tk.END, f"Found {len(drivers)} devices:\n\n")
            for driver in drivers:
                self.drivers_text.insert(tk.END,
                    f"• {driver.type.value}\n  Device: {driver.device_name}\n  Status: {driver.status.value}\n\n")
        else:
            self.drivers_text.insert(tk.END, "No additional drivers detected\n")
        
        self.drivers_text.config(state=tk.DISABLED)
    
    def auto_install_drivers(self):
        """Auto install drivers"""
        if messagebox.askyesno("Confirm", "Install missing drivers? This may take some time."):
            self.driver_manager.auto_install_drivers()
            messagebox.showinfo("Success", "Driver installation complete")
            self.show_drivers()
    
    def show_display(self):
        """Display settings"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Display Settings",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Label(self.content_frame, text="Display settings are configured in BIOS/UEFI"
                  "\nor using your graphics driver settings.").pack(pady=20)
    
    def show_sound(self):
        """Sound settings"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Sound Settings",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Label(self.content_frame, text="Use PulseAudio volume control\n"
                  "or run: pactl to manage sound settings").pack(pady=20)
    
    def show_network(self):
        """Network settings"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Network Settings",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Network info
        try:
            net_if = psutil.net_if_addrs()
            for iface, addrs in net_if.items():
                frame = ttk.LabelFrame(self.content_frame, text=f"Interface: {iface}")
                frame.pack(fill=tk.X, pady=5)
                
                for addr in addrs:
                    ttk.Label(frame, text=f"{addr.family.name}: {addr.address}").pack(
                        anchor=tk.W, padx=10, pady=2)
        except:
            pass
    
    def show_appearance(self):
        """Appearance settings"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="Appearance",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Theme selection
        theme_frame = ttk.LabelFrame(self.content_frame, text="Theme")
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        theme_var = tk.StringVar(value=self.theme_manager.current_theme)
        
        for theme_name in self.theme_manager.get_all_themes():
            rb = ttk.Radiobutton(
                theme_frame,
                text=theme_name,
                variable=theme_var,
                value=theme_name,
                command=lambda t=theme_name: self.theme_manager.set_theme(t)
            )
            rb.pack(anchor=tk.W, padx=10, pady=5)
    
    def show_about(self):
        """About view"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="About CarrotOS",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        about_text = """
CarrotOS 1.0
Professional Linux Distribution

A complete, modern Linux operating system with:
• Professional installer for hard disk installation
• Complete user and group management system
• Comprehensive hardware driver support
• System update manager with rollback capability
• Multi-theme support (dark/light)
• Powerful control center for system management

Developed with Python, GTK+, and modern Linux tools.
Visit: https://carrotos.dev

© 2026 CarrotOS Project
"""
        
        info_label = tk.Label(
            self.content_frame,
            text=about_text,
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY,
            justify=tk.LEFT,
            font=("Arial", 11)
        )
        info_label.pack(pady=20, padx=20)
    
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def monitor_loop(self):
        """Monitor system metrics"""
        while self.monitoring:
            try:
                # Update dashboard if visible
                if hasattr(self, 'cpu_label'):
                    cpu_percent = psutil.cpu_percent(interval=0.5)
                    self.cpu_label.value_label.config(text=f"{cpu_percent:.1f}%")
                    
                    mem_percent = psutil.virtual_memory().percent
                    self.mem_label.value_label.config(text=f"{mem_percent:.1f}%")
                    
                    disk_percent = psutil.disk_usage('/').percent
                    self.disk_label.value_label.config(text=f"{disk_percent:.1f}%")
                    
                    # Thermal (if available)
                    try:
                        temps = psutil.sensors_temperatures()
                        if temps and 'coretemp' in temps:
                            temp = temps['coretemp'][0].current
                            self.temp_label.value_label.config(text=f"{temp:.1f}°C")
                    except:
                        pass
                
                time.sleep(2)
            except:
                break
    
    def on_closing(self):
        """Handle window closing"""
        self.monitoring = False
        self.root.destroy()

def main():
    """Main entry point"""
    if os.geteuid() != 0:
        messagebox.showerror("Error", "Control Center must be run as root")
        sys.exit(1)
    
    root = tk.Tk()
    app = CarrotControlCenter(root)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()
