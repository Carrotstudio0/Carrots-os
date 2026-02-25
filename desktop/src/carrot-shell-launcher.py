#!/usr/bin/env python3
"""
CarrotOS Shell Launcher
Application launcher, panel, and window manager coordinator
"""

import os
import sys
import json
import subprocess
import threading
from pathlib import Path
from typing import List, Dict

class CarrotShell:
    """Carrot Desktop Shell - lightweight desktop interface"""
    
    def __init__(self):
        self.config_dir = Path("/etc/carrot/shell")
        self.apps_dir = Path("/usr/share/applications")
        self.running_apps: Dict[str, subprocess.Popen] = {}
        self.workspaces = []
        self.current_workspace = 0
        
    def load_config(self):
        """Load shell configuration"""
        config_file = self.config_dir / "shell.conf"
        print("[shell] Loading configuration...")
        
        self.config = {
            "display_server": "wayland",
            "compositor": "weston",
            "theme": "carrot-default",
            "num_workspaces": 4,
            "panel_position": "top",
            "panel_height": 32
        }
        
        print("[shell] Config loaded")
    
    def discover_applications(self) -> List[Dict]:
        """Discover installed applications"""
        print("[shell] Discovering applications...")
        
        apps = [
            {
                "name": "Terminal",
                "icon": "utilities-terminal",
                "exec": "/usr/bin/carrot-terminal",
                "category": "Utilities"
            },
            {
                "name": "File Manager",
                "icon": "folder",
                "exec": "/usr/bin/carrot-files",
                "category": "Utilities"
            },
            {
                "name": "Settings",
                "icon": "preferences-system",
                "exec": "/usr/bin/carrot-settings",
                "category": "System"
            },
            {
                "name": "Text Editor",
                "icon": "accessories-text-editor",
                "exec": "/usr/bin/carrot-editor",
                "category": "Accessories"
            },
            {
                "name": "System Monitor",
                "icon": "utilities-system-monitor",
                "exec": "/usr/bin/carrot-systray",
                "category": "System"
            }
        ]
        
        print(f"[shell] Found {len(apps)} applications")
        return apps
    
    def launch_application(self, app_name: str, exec_path: str) -> bool:
        """Launch application"""
        print(f"[shell] Launching: {app_name}")
        
        try:
            proc = subprocess.Popen(
                [exec_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.running_apps[app_name] = proc
            return True
        except Exception as e:
            print(f"[shell ERROR] Failed to launch {app_name}: {e}")
            return False
    
    def switch_workspace(self, ws: int):
        """Switch to workspace"""
        if 0 <= ws < self.config["num_workspaces"]:
            self.current_workspace = ws
            print(f"[shell] Switched to workspace {ws + 1}")
    
    def initialize_panel_system(self):
        """Initialize panel and notification system"""
        print("[shell] Initializing panel system...")
        
        # Create panel configuration
        panel_config = {
            "position": "top",
            "height": 32,
            "items": [
                {"type": "launcher", "label": "Launcher"},
                {"type": "taskbar", "max_items": 10},
                {"type": "spacer"},
                {"type": "clock", "format": "%H:%M"},
                {"type": "volume"},
                {"type": "network"},
                {"type": "power"}
            ]
        }
        
        print("[shell] Panel configured")
    
    def manage_windows(self):
        """Window management loop"""
        print("[shell] Window manager starting...")
        
        # This would track and manage windows
        # For now, just a placeholder
    
    def setup_environment(self):
        """Setup desktop environment variables"""
        print("[shell] Setting up environment...")
        
        env_setup = {
            "XDG_DATA_DIRS": "/usr/local/share:/usr/share",
            "XDG_CONFIG_DIRS": "/etc/xdg",
            "QT_QPA_PLATFORMTHEME": "gtk3",
            "GTK_THEME": "carrot-default"
        }
        
        for key, value in env_setup.items():
            os.environ[key] = value
    
    def run(self):
        """Main shell event loop"""
        print("[shell] ╔════════════════════════════════════╗")
        print("[shell] ║   CarrotOS Desktop Environment    ║")
        print("[shell] ║   v1.0.0  (Carrot-LTS)           ║")
        print("[shell] ╚════════════════════════════════════╝\n")
        
        self.setup_environment()
        self.load_config()
        
        # Initialize workspaces
        for i in range(self.config["num_workspaces"]):
            self.workspaces.append({"id": i, "windows": []})
            print(f"[shell] Workspace {i+1} created")
        
        apps = self.discover_applications()
        self.initialize_panel_system()
        
        print("[shell] Desktop environment ready")
        print("[shell] Workspace manager running (ctrl+alt arrow keys to switch)")
        print("[shell] Alt+Tab to switch windows")
        print("[shell] Alt+F2 for run dialog")
        print()
        
        # Launch autostart applications
        autostart_apps = [
            ("Terminal", "/usr/bin/carrot-terminal"),
        ]
        
        for app_name, exec_path in autostart_apps:
            if os.path.exists(exec_path):
                # Don't auto-launch in hidden mode for now
                print(f"[shell] Ready to launch: {app_name}")
        
        # Main loop
        try:
            # Monitor running applications
            while True:
                import time
                time.sleep(1)
                
                # Check for dead processes
                dead_apps = []
                for app_name, proc in list(self.running_apps.items()):
                    if proc.poll() is not None:
                        dead_apps.append(app_name)
                
                for app_name in dead_apps:
                    print(f"[shell] Application closed: {app_name}")
                    del self.running_apps[app_name]
        
        except KeyboardInterrupt:
            print("\n[shell] Shutdown requested")
            for app in self.running_apps.values():
                try:
                    app.terminate()
                except:
                    pass


def main():
    """Entry point"""
    shell = CarrotShell()
    shell.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
