#!/usr/bin/env python3
"""
CarrotOS Settings Application
System configuration and preferences
"""

import os
import sys
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    print("Error: tkinter required")
    sys.exit(1)

class CarrotSettings:
    """System Settings Panel"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Carrot Settings")
        self.root.geometry("900x650")
        self.root.configure(bg='#1a1a23')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings interface"""
        # Main container
        main_frame = tk.PanedWindow(self.root, bg='#1a1a23', 
                                   relief=tk.FLAT, borderwidth=0)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar (categories)
        sidebar = tk.Frame(main_frame, bg='#2a2a35', width=200)
        main_frame.add(sidebar, before='end')
        
        # Title in sidebar
        title = tk.Label(sidebar, text="Settings", 
                        font=("Ubuntu", 18, "bold"),
                        bg='#2a2a35', fg='#ff9500')
        title.pack(pady=15, padx=10)
        
        # Categories
        self.categories = [
            ("System", "display: settings 24"),
            ("Display", "📺"),
            ("Sound", "🔊"),
            ("Network", "🌐"),
            ("Users", "👤"),
            ("Appearance", "🎨"),
            ("Keyboard", "⌨️"),
            ("Mouse", "🖱️"),
            ("Power", "⚡"),
            ("About", "ℹ️"),
        ]
        
        self.cat_buttons = {}
        for name, icon in self.categories:
            btn = tk.Button(sidebar, text=f"{icon} {name}",
                          command=lambda n=name: self.show_category(n),
                          bg='#2a2a35', fg='#cccccc',
                          font=("Ubuntu", 10),
                          relief=tk.FLAT, padx=15, pady=10,
                          activebackground='#ff9500',
                          activeforeground='#000000',
                          justify=tk.LEFT, anchor=tk.W)
            btn.pack(fill=tk.X, padx=0, pady=2)
            self.cat_buttons[name] = btn
        
        # Content area
        self.content_frame = tk.Frame(main_frame, bg='#1a1a23')
        main_frame.add(self.content_frame, after=sidebar)
        
        # Show first category
        self.show_category("System")
    
    def show_category(self, category):
        """Show category settings"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Highlight button
        for btn in self.cat_buttons.values():
            btn.config(bg='#2a2a35')
        self.cat_buttons[category].config(bg='#ff9500', fg='#000000')
        
        # Show content
        if category == "System":
            self.show_system_settings()
        elif category == "Display":
            self.show_display_settings()
        elif category == "Sound":
            self.show_sound_settings()
        elif category == "Network":
            self.show_network_settings()
        elif category == "Users":
            self.show_users_settings()
        elif category == "Appearance":
            self.show_appearance_settings()
        elif category == "Keyboard":
            self.show_keyboard_settings()
        elif category == "Mouse":
            self.show_mouse_settings()
        elif category == "Power":
            self.show_power_settings()
        elif category == "About":
            self.show_about_settings()
    
    def show_system_settings(self):
        """System settings"""
        frame = tk.Frame(self.content_frame, bg='#1a1a23')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title = tk.Label(frame, text="System Information",
                        font=("Ubuntu", 16, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # System info
        info = [
            ("Operating System", "CarrotOS 1.0.0"),
            ("Kernel Version", "5.15.0-carrot-lts"),
            ("Hostname", os.uname()[1]),
            ("Architecture", os.uname()[4]),
            ("Display Server", "Wayland"),
            ("Init System", "carrot-init"),
        ]
        
        for label, value in info:
            frame_row = tk.Frame(frame, bg='#1a1a23')
            frame_row.pack(fill=tk.X, pady=8)
            
            label_widget = tk.Label(frame_row, text=f"{label}:",
                                   font=("Ubuntu", 11, "bold"),
                                   bg='#1a1a23', fg='#ff9500',
                                   width=20, anchor=tk.W)
            label_widget.pack(side=tk.LEFT)
            
            value_widget = tk.Label(frame_row, text=value,
                                   font=("Ubuntu", 11),
                                   bg='#1a1a23', fg='#cccccc',
                                   anchor=tk.W)
            value_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def show_display_settings(self):
        """Display settings"""
        frame = tk.Frame(self.content_frame, bg='#1a1a23')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title = tk.Label(frame, text="Display Settings",
                        font=("Ubuntu", 16, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Brightness
        row = tk.Frame(frame, bg='#1a1a23')
        row.pack(fill=tk.X, pady=10)
        
        tk.Label(row, text="Brightness",
                font=("Ubuntu", 11), bg='#1a1a23', fg='#cccccc',
                width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        brightness = tk.Scale(row, from_=0, to=100, orient=tk.HORIZONTAL,
                             bg='#2a2a35', fg='#ff9500',
                             troughcolor='#353540')
        brightness.set(80)
        brightness.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Resolution
        row = tk.Frame(frame, bg='#1a1a23')
        row.pack(fill=tk.X, pady=10)
        
        tk.Label(row, text="Resolution",
                font=("Ubuntu", 11), bg='#1a1a23', fg='#cccccc',
                width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        resolution_var = tk.StringVar(value="1920x1080")
        resolution_combo = ttk.Combobox(row, textvariable=resolution_var,
                                       values=["1920x1080", "1680x1050", 
                                              "1440x900", "1280x720"],
                                       state='readonly', width=15)
        resolution_combo.pack(side=tk.LEFT, padx=10)
    
    def show_sound_settings(self):
        """Sound settings"""
        frame = tk.Frame(self.content_frame, bg='#1a1a23')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title = tk.Label(frame, text="Sound Settings",
                        font=("Ubuntu", 16, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Volume
        row = tk.Frame(frame, bg='#1a1a23')
        row.pack(fill=tk.X, pady=10)
        
        tk.Label(row, text="Volume",
                font=("Ubuntu", 11), bg='#1a1a23', fg='#cccccc',
                width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        volume = tk.Scale(row, from_=0, to=100, orient=tk.HORIZONTAL,
                         bg='#2a2a35', fg='#00ff00',
                         troughcolor='#353540')
        volume.set(70)
        volume.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def show_network_settings(self):
        """Network settings"""
        frame = tk.Frame(self.content_frame, bg='#1a1a23')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title = tk.Label(frame, text="Network Settings",
                        font=("Ubuntu", 16, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # WiFi
        row = tk.Frame(frame, bg='#1a1a23')
        row.pack(fill=tk.X, pady=10)
        
        tk.Label(row, text="WiFi Enabled",
                font=("Ubuntu", 11), bg='#1a1a23', fg='#cccccc',
                width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        wifi_var = tk.BooleanVar(value=True)
        tk.Checkbutton(row, variable=wifi_var,
                      bg='#1a1a23', fg='#ff9500',
                      activebackground='#1a1a23',
                      activeforeground='#ff9500').pack(side=tk.LEFT)
    
    def show_users_settings(self):
        """Users settings"""
        frame = tk.Frame(self.content_frame, bg='#1a1a23')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title = tk.Label(frame, text="User Accounts",
                        font=("Ubuntu", 16, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(anchor=tk.W, pady=(0, 20))
        
        current_user = os.environ.get('USER', 'user')
        tk.Label(frame, text=f"Current User: {current_user}",
                font=("Ubuntu", 12), bg='#1a1a23', fg='#cccccc').pack(anchor=tk.W)
    
    def show_appearance_settings(self):
        """Appearance settings"""
        frame = tk.Frame(self.content_frame, bg='#1a1a23')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title = tk.Label(frame, text="Appearance",
                        font=("Ubuntu", 16, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Theme
        row = tk.Frame(frame, bg='#1a1a23')
        row.pack(fill=tk.X, pady=10)
        
        tk.Label(row, text="Theme",
                font=("Ubuntu", 11), bg='#1a1a23', fg='#cccccc',
                width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        theme_var = tk.StringVar(value="Dark")
        theme_combo = ttk.Combobox(row, textvariable=theme_var,
                                  values=["Dark", "Light", "Auto"],
                                  state='readonly', width=15)
        theme_combo.pack(side=tk.LEFT, padx=10)
    
    def show_keyboard_settings(self):
        """Keyboard settings"""
        frame = tk.Frame(self.content_frame, bg='#1a1a23')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title = tk.Label(frame, text="Keyboard Settings",
                        font=("Ubuntu", 16, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Keyboard layout
        row = tk.Frame(frame, bg='#1a1a23')
        row.pack(fill=tk.X, pady=10)
        
        tk.Label(row, text="Keyboard Layout",
                font=("Ubuntu", 11), bg='#1a1a23', fg='#cccccc',
                width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        layout_var = tk.StringVar(value="US")
        layout_combo = ttk.Combobox(row, textvariable=layout_var,
                                   values=["US", "UK", "FR", "DE"],
                                   state='readonly', width=15)
        layout_combo.pack(side=tk.LEFT, padx=10)
    
    def show_mouse_settings(self):
        """Mouse settings"""
        frame = tk.Frame(self.content_frame, bg='#1a1a23')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title = tk.Label(frame, text="Mouse Settings",
                        font=("Ubuntu", 16, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Sensitivity
        row = tk.Frame(frame, bg='#1a1a23')
        row.pack(fill=tk.X, pady=10)
        
        tk.Label(row, text="Mouse Speed",
                font=("Ubuntu", 11), bg='#1a1a23', fg='#cccccc',
                width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        speed = tk.Scale(row, from_=1, to=10, orient=tk.HORIZONTAL,
                        bg='#2a2a35', fg='#00ff00',
                        troughcolor='#353540')
        speed.set(5)
        speed.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def show_power_settings(self):
        """Power settings"""
        frame = tk.Frame(self.content_frame, bg='#1a1a23')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title = tk.Label(frame, text="Power Settings",
                        font=("Ubuntu", 16, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Screen timeout
        row = tk.Frame(frame, bg='#1a1a23')
        row.pack(fill=tk.X, pady=10)
        
        tk.Label(row, text="Screen Timeout",
                font=("Ubuntu", 11), bg='#1a1a23', fg='#cccccc',
                width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        timeout_var = tk.StringVar(value="5")
        timeout_combo = ttk.Combobox(row, textvariable=timeout_var,
                                    values=["1", "2", "5", "10", "15", "30"],
                                    state='readonly', width=15)
        timeout_combo.pack(side=tk.LEFT, padx=10)
        
        tk.Label(row, text="minutes", font=("Ubuntu", 11),
                bg='#1a1a23', fg='#888888').pack(side=tk.LEFT, padx=5)
    
    def show_about_settings(self):
        """About system"""
        frame = tk.Frame(self.content_frame, bg='#1a1a23')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title = tk.Label(frame, text="About CarrotOS",
                        font=("Ubuntu", 16, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(anchor=tk.W, pady=(0, 20))
        
        about_text = """
CarrotOS v1.0.0
A Modern, Lightweight Linux Distribution

Build: carrot-lts-build-1
Release: 2026-02-25

System Features:
  ✓ Wayland Display Server
  ✓ Custom Carrot Desktop Environment
  ✓ OverlayFS Support
  ✓ Lightweight by Design
  ✓ Fast Boot
  ✓ Beautiful UI

© 2026 CarrotOS Project
Licensed under GPL-3.0+

Website: https://carrotos.org
Repository: https://github.com/carrotos/carrotos
        """
        
        tk.Label(frame, text=about_text,
                font=("Ubuntu", 10),
                bg='#1a1a23', fg='#cccccc',
                justify=tk.LEFT, anchor=tk.NW).pack(fill=tk.BOTH, expand=True)
    
    def run(self):
        """Run settings"""
        self.root.mainloop()


if __name__ == '__main__':
    settings = CarrotSettings()
    settings.run()
