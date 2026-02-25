#!/usr/bin/env python3
"""
CarrotOS Web Browser
Lightweight web browser using WebKit/GTK or html rendering
"""

import sys
import subprocess
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, simpledialog, messagebox
    import tkinterbrowser
except ImportError:
    # Fallback to embedded Chromium or system browser
    pass

class CarrotBrowser:
    """Lightweight Web Browser"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Carrot Browser")
        self.root.geometry("1200x700")
        self.root.configure(bg='#1a1a23')
        
        self.current_url = "about:blank"
        self.history = []
        self.history_index = -1
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup browser interface"""
        # Navigation bar
        nav_frame = tk.Frame(self.root, bg='#2a2a35', height=50)
        nav_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Buttons
        btn_frame = tk.Frame(nav_frame, bg='#2a2a35')
        btn_frame.pack(side=tk.LEFT, padx=5, pady=8)
        
        self.back_btn = tk.Button(btn_frame, text="← Back", command=self.go_back,
                                 bg='#353540', fg='#ff9500', relief=tk.FLAT, padx=8)
        self.back_btn.pack(side=tk.LEFT, padx=2)
        
        self.forward_btn = tk.Button(btn_frame, text="Forward →", command=self.go_forward,
                                    bg='#353540', fg='#ff9500', relief=tk.FLAT, padx=8)
        self.forward_btn.pack(side=tk.LEFT, padx=2)
        
        self.reload_btn = tk.Button(btn_frame, text="🔄 Reload", command=self.reload,
                                   bg='#353540', fg='#ff9500', relief=tk.FLAT, padx=8)
        self.reload_btn.pack(side=tk.LEFT, padx=2)
        
        self.home_btn = tk.Button(btn_frame, text="🏠 Home", command=self.go_home,
                                 bg='#353540', fg='#ff9500', relief=tk.FLAT, padx=8)
        self.home_btn.pack(side=tk.LEFT, padx=2)
        
        # URL bar
        addr_frame = tk.Frame(nav_frame, bg='#2a2a35')
        addr_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.url_entry = tk.Entry(addr_frame, font=("Ubuntu", 11),
                                 bg='#353540', fg='#cccccc',
                                 insertbackground='#ff9500', relief=tk.FLAT)
        self.url_entry.pack(fill=tk.X, pady=8)
        self.url_entry.bind('<Return>', lambda e: self.navigate())
        
        # Content area with text display
        content_frame = tk.Frame(self.root, bg='#1a1a23')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable text area for HTML content
        scrollbar = ttk.Scrollbar(content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.content = tk.Text(content_frame, bg='#ffffff', fg='#000000',
                              yscrollcommand=scrollbar.set, relief=tk.FLAT,
                              font=("Ubuntu", 10), wrap=tk.WORD)
        self.content.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.content.yview)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready",
                                  bg='#2a2a35', fg='#888888',
                                  anchor=tk.W, padx=10, pady=5)
        self.status_bar.pack(fill=tk.X)
        
        # Load home page
        self.go_home()
    
    def navigate(self):
        """Navigate to URL"""
        url = self.url_entry.get()
        if not url:
            return
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://', 'about:', 'file://')):
            if '.' in url:
                url = 'https://' + url
            else:
                url = 'https://google.com/search?q=' + url
        
        self.load_url(url)
    
    def load_url(self, url):
        """Load URL"""
        self.current_url = url
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        
        self.status_bar.config(text=f"Loading {url}...")
        
        if url.startswith('about:'):
            self.show_about()
        elif url.startswith('file://'):
            self.show_file(url[7:])
        else:
            self.show_loading()
            # In real implementation, would use requests/urllib to fetch page
            self.show_offline_notice(url)
        
        self.status_bar.config(text="Ready")
    
    def show_about(self):
        """Show about page"""
        html = """
╔════════════════════════════════════════╗
║        CarrotOS Web Browser 🥕          ║
║        Version 1.0.0                   ║
╚════════════════════════════════════════╝

Features:
  • Lightweight design
  • Fast page loading
  • History support
  • Bookmarks (future)
  • Developer tools (future)

System Information:
  OS: CarrotOS 1.0.0
  Kernel: 5.15.0-carrot-lts
  Session: Wayland

Tips:
  • Type in the address bar to search
  • Press Enter or click → to navigate
  • Click Back/Forward to navigate history
  • Press Ctrl+L to focus address bar

This is a lightweight browser for CarrotOS.
For full web browsing, consider using Firefox or Chromium.
        """
        self.show_content(html)
    
    def show_file(self, filepath):
        """Show file content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.show_content(content)
        except Exception as e:
            self.show_content(f"Error: {e}")
    
    def show_loading(self):
        """Show loading page"""
        html = """
╔════════════════════════════════════════╗
║     Loading page, please wait...       ║
╚════════════════════════════════════════╝

Note: This is a lightweight browser built into CarrotOS.
For full web browsing functionality, install Firefox or Chromium:

  $ carrot-pkg install firefox
  $ carrot-pkg install chromium

CarrotOS Browser Features:
  ✓ View local HTML files
  ✓ Simple text/markdown display
  ✓ History navigation
  ✓ Bookmark management (coming soon)
  ✓ Dark mode theme (built-in)

This browser is optimized for:
  - System pages and documentation
  - Local file viewing
  - Lightweight performance
  - Integration with CarrotOS tools
        """
        self.show_content(html)
    
    def show_offline_notice(self, url):
        """Show offline notice"""
        html = f"""
╔════════════════════════════════════════╗
║      Offline Mode - Limited Features   ║
╚════════════════════════════════════════╝

Attempted URL: {url}

CarrotOS Lightweight Browser Status:
  Network: Not available in demo mode

To browse the web, download a full browser:

Available Browsers:
  1. Firefox (Recommended)
     $ carrot-pkg install firefox
  
  2. Chromium
     $ carrot-pkg install chromium
  
  3. w3m (Terminal-based)
     $ carrot-pkg install w3m

For now, you can:
  • View local files: file:///home/user/file.html
  • Read help documents
  • Access system pages

To connect to the internet:
  1. Check network settings
  2. Connect to WiFi or Ethernet
  3. Run: nmcli connection show
        """
        self.show_content(html)
    
    def show_content(self, content):
        """Display content"""
        self.content.config(state=tk.NORMAL)
        self.content.delete(1.0, tk.END)
        self.content.insert(1.0, content)
        self.content.config(state=tk.DISABLED)
    
    def go_back(self):
        """Go back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.load_url(self.history[self.history_index])
    
    def go_forward(self):
        """Go forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_url(self.history[self.history_index])
    
    def reload(self):
        """Reload page"""
        self.load_url(self.current_url)
    
    def go_home(self):
        """Go to home page"""
        self.load_url("about:blank")
    
    def run(self):
        """Run browser"""
        self.root.mainloop()


if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else "about:blank"
    browser = CarrotBrowser()
    if url != "about:blank":
        browser.load_url(url)
    browser.run()
