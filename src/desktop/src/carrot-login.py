#!/usr/bin/env python3
"""
CarrotOS Login Manager (carrot-login)
Minimal display manager with login screen
"""

import sys
import os
import getpass
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class LoginManager:
    """Lightweight login manager for CarrotOS"""
    
    def __init__(self):
        self.config_dir = Path("/etc/carrot")
        self.users = self.load_users()
    
    def load_users(self):
        """Load users from /etc/passwd"""
        users = []
        try:
            with open("/etc/passwd") as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 5:
                        username = parts[0]
                        uid = int(parts[2])
                        # Skip system users
                        if uid >= 1000:
                            users.append(username)
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
        return users
    
    def show_splash(self):
        """Display login splash screen"""
        print("\x1b[2J\x1b[H")  # Clear screen, move to top
        print("""
        
    ╔═══════════════════════════════════════════════╗
    ║                                               ║
    ║          🥕  CarrotOS 1.0.0 (LTS)  🥕         ║
    ║                                               ║
    ║            Lightweight Desktop OS             ║
    ║                                               ║
    ╚═══════════════════════════════════════════════╝
    
    """)
        print("Initializing desktop environment...")
    
    def login_tui(self):
        """Text-based login interface"""
        self.show_splash()
        
        print("\n--- User Login ---\n")
        
        # Username
        while True:
            username = input("Username: ").strip()
            if username in self.users or username == "root":
                break
            print("User not found")
        
        # Password (simplified - no shadow check for now)
        password = getpass.getpass("Password: ")
        
        # For now, accept any non-empty password
        if not password:
            print("Invalid password")
            return None
        
        return username
    
    def login_graphical(self):
        """Graphical login screen using GTK or minimal X11"""
        logger.info("Attempting graphical login...")
        
        # For now, fallback to TUI
        # In production would use GTK/Qt
        return self.login_tui()
    
    def start_session(self, username: str):
        """Start user session"""
        logger.info(f"Starting session for user: {username}")
        
        # Set environment
        os.environ["USER"] = username
        os.environ["HOME"] = f"/home/{username}" if username != "root" else "/root"
        os.environ["SHELL"] = "/bin/bash"
        os.environ["DISPLAY"] = ":0"
        os.environ["XDG_RUNTIME_DIR"] = f"/run/user/1000"
        os.environ["WAYLAND_DISPLAY"] = "wayland-0"
        
        # Create runtime dir if needed
        run_user_dir = Path("/run/user/1000")
        run_user_dir.mkdir(parents=True, exist_ok=True)
        
        # Start desktop environment
        try:
            logger.info("Starting Carrot Desktop Environment...")
            
            # Try Wayland first
            if os.path.exists("/usr/bin/weston"):
                os.execvp("weston", ["weston"])
            # Fallback to shell
            else:
                os.execvp("/bin/bash", ["/bin/bash", "--login"])
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return False
        
        return True
    
    def run(self):
        """Main login loop"""
        logger.info("CarrotOS Login Manager starting...")
        
        while True:
            try:
                # Try graphical first, fallback to text
                username = self.login_graphical()
                
                if username:
                    if self.start_session(username):
                        break
            except KeyboardInterrupt:
                print("\n\nShutdown...")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Login error: {e}")


def main():
    # Check if running as root
    if os.getuid() != 0:
        print("Error: carrot-login must run as root")
        return 1
    
    # Initialize display server if needed
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        # Start Wayland server
        logger.info("Starting Wayland display server...")
        try:
            # This would normally fork weston
            pass
        except Exception as e:
            logger.error(f"Failed to start display server: {e}")
    
    manager = LoginManager()
    manager.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
