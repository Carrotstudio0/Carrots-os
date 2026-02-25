#!/usr/bin/env python3
"""
CarrotOS Desktop Shell
Modern desktop environment with panel and app launcher
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from threading import Thread
import time

try:
    import tkinter as tk
    from tkinter import font
except ImportError:
    print("Error: tkinter required")
    sys.exit(1)

class DesktopApp:
    """Desktop application entry"""
    
    def __init__(self, name, icon, cmd, category='System'):
        self.name = name
        self.icon = icon
        self.cmd = cmd
        self.category = category
        self.process = None
    
    def launch(self):
        """Launch application"""
        try:
            self.process = subprocess.Popen(self.cmd, shell=True, 
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error launching {self.name}: {e}")

class CarrotDesktopShell:
    """Desktop Shell - Main UI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-type', 'desktop')
        self.root.overrideredirect(True)
        
        # Get screen size
        self.root.update_idletasks()
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        
        # Setup
        self.setup_apps()
        self.setup_ui()
        self.show_launcher = False
        
        # Start background thread for clock
        clock_thread = Thread(target=self.update_clock, daemon=True)
        clock_thread.start()
    
    def setup_apps(self):
        """Setup available applications"""
        self.apps = [
            DesktopApp("Files", "📁", "carrot-files", "System"),
            DesktopApp("Terminal", "🖥️", "carrot-terminal", "System"),
            DesktopApp("Editor", "📝", "carrot-editor", "Accessories"),
            DesktopApp("Browser", "🌐", "carrot-browser", "Internet"),
            DesktopApp("Settings", "⚙️", "carrot-settings", "System"),
            DesktopApp("Monitor", "📊", "carrot-monitor", "System"),
        ]
    
    def setup_ui(self):
        """Setup desktop UI"""
        self.root.geometry(f'{self.width}x{self.height}+0+0')
        self.root.configure(bg='#1a1a23')
        
        # Create background (could load from wallpaper)
        bg = tk.Label(self.root, bg='#1a1a23')
        bg.place(x=0, y=0, width=self.width, height=self.height)
        
        # Top panel
        self.setup_panel()
        
        # Watch for clicks to show launcher
        bg.bind('<Button-1>', self.on_desktop_click)
    
    def setup_panel(self):
        """Setup top panel"""
        panel = tk.Frame(self.root, bg='#0d0d0d', height=40)
        panel.place(x=0, y=0, width=self.width, height=40)
        
        # Activities button (app launcher)
        activities_btn = tk.Button(panel, text="🥕 Activities",
                                  command=self.toggle_launcher,
                                  bg='#1a1a23', fg='#ff9500',
                                  font=("Ubuntu", 11, "bold"),
                                  relief=tk.FLAT, padx=15, pady=5,
                                  activebackground='#ff9500',
                                  activeforeground='#000000',
                                  cursor='hand2')
        activities_btn.place(x=10, y=5)
        
        # Quick launcher (taskbar)
        self.taskbar_frame = tk.Frame(panel, bg='#0d0d0d')
        self.taskbar_frame.place(x=150, y=5, width=400, height=30)
        
        # Quick access buttons
        self.taskbar_buttons = {}
        x_pos = 0
        for app in self.apps[:5]:
            btn = tk.Button(self.taskbar_frame, text=app.icon,
                          command=lambda a=app: a.launch(),
                          bg='#1a1a23', fg='#ffffff',
                          font=("Ubuntu", 14),
                          relief=tk.RAISED, padx=8, pady=2,
                          activebackground='#ff9500',
                          activeforeground='#000000',
                          cursor='hand2')
            btn.place(x=x_pos, y=0)
            self.taskbar_buttons[app.name] = btn
            x_pos += 45
        
        # System tray area
        tray_frame = tk.Frame(panel, bg='#0d0d0d')
        tray_frame.place(x=self.width - 250, y=5)
        
        # Clock
        self.clock_label = tk.Label(tray_frame, text="00:00",
                                   bg='#0d0d0d', fg='#cccccc',
                                   font=("Ubuntu", 10),
                                   padx=10)
        self.clock_label.pack(side=tk.RIGHT)
        
        # Notifications
        self.notification_label = tk.Label(tray_frame, text="",
                                          bg='#0d0d0d', fg='#888888',
                                          font=("Ubuntu", 9),
                                          padx=10)
        self.notification_label.pack(side=tk.RIGHT)
        
        # System icons
        icons = ["🔊", "🔋", "🌐", "👤"]
        for icon in icons:
            icon_btn = tk.Button(tray_frame, text=icon,
                               bg='#0d0d0d', fg='#ffffff',
                               font=("Ubuntu", 10),
                               relief=tk.FLAT, padx=5, pady=2,
                               activebackground='#ff9500',
                               activeforeground='#000000')
            icon_btn.pack(side=tk.RIGHT, padx=2)
    
    def toggle_launcher(self):
        """Toggle application launcher"""
        if self.show_launcher:
            self.hide_launcher()
        else:
            self.show_launcher_window()
    
    def show_launcher_window(self):
        """Show application launcher"""
        self.show_launcher = True
        
        # Create launcher window
        launcher = tk.Toplevel(self.root)
        launcher.attributes('-type', 'dialog')
        launcher.geometry(f'{600}x{self.height - 100}+{(self.width-600)//2}+50')
        launcher.configure(bg='#1a1a23')
        launcher.title("Applications")
        launcher.protocol("WM_DELETE_WINDOW", lambda: self.hide_launcher())
        
        # Title
        title = tk.Label(launcher, text="Applications",
                        font=("Ubuntu", 18, "bold"),
                        bg='#1a1a23', fg='#ff9500')
        title.pack(pady=15)
        
        # Search bar
        search_frame = tk.Frame(launcher, bg='#1a1a23')
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        search_entry = tk.Entry(search_frame, font=("Ubuntu", 12),
                               bg='#2a2a35', fg='#cccccc',
                               insertbackground='#ff9500',
                               relief=tk.FLAT)
        search_entry.pack(fill=tk.X)
        search_entry.focus()
        
        # Apps grid
        apps_frame = tk.Frame(launcher, bg='#1a1a23')
        apps_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Display apps in grid
        col = 0
        row = 0
        for app in self.apps:
            app_btn = tk.Button(apps_frame, text=f"{app.icon}\n{app.name}",
                              command=lambda a=app: [a.launch(), launcher.destroy()],
                              bg='#2a2a35', fg='#ffffff',
                              font=("Ubuntu", 11),
                              relief=tk.RAISED, padx=20, pady=15,
                              activebackground='#ff9500',
                              activeforeground='#000000',
                              cursor='hand2',
                              width=15, height=4)
            app_btn.grid(row=row, column=col, padx=10, pady=10)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Close on Escape
        launcher.bind('<Escape>', lambda e: launcher.destroy())
        
        # Update window
        launcher.focus()
    
    def hide_launcher(self):
        """Hide launcher"""
        self.show_launcher = False
    
    def on_desktop_click(self, event):
        """Handle desktop click"""
        # Could show context menu or toggle launcher
        pass
    
    def update_clock(self):
        """Update clock in panel"""
        while True:
            try:
                now = datetime.now().strftime("%H:%M")
                self.clock_label.config(text=now)
            except:
                pass
            time.sleep(60)
    
    def run(self):
        """Run desktop shell"""
        self.root.mainloop()


if __name__ == '__main__':
    shell = CarrotDesktopShell()
    shell.run()
