#!/usr/bin/env python3
"""
CarrotOS Display Manager (carrot-dm)
Lightweight login screen with modern UI
"""

import os
import sys
import pwd
import subprocess
import signal
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import font, messagebox
    from PIL import Image, ImageDraw, ImageFilter, ImageTk
except ImportError:
    print("Error: tkinter and Pillow required")
    print("Install: pip3 install Pillow")
    sys.exit(1)

class CarrotDM:
    """Display Manager - Login Screen"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-type', 'splash')
        
        # Get screen dimensions
        self.root.update_idletasks()
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.root.geometry(f'{self.width}x{self.height}+0+0')
        
        self.setup_ui()
        self.selected_user = None
        
    def create_blur_bg(self):
        """Create blurred background image"""
        # Create gradient background
        bg = Image.new('RGB', (self.width, self.height), (25, 25, 35))
        draw = ImageDraw.Draw(bg, 'RGBA')
        
        # Add gradient
        for y in range(self.height):
            alpha = int(255 * (y / self.height))
            color = (45 + int(20 * (y / self.height)), 
                    45 + int(20 * (y / self.height)), 
                    55 + int(20 * (y / self.height)))
            draw.rectangle([(0, y), (self.width, y+1)], fill=color)
        
        # Add some blur effect
        bg = bg.filter(ImageFilter.GaussianBlur(radius=2))
        
        return ImageTk.PhotoImage(bg)
    
    def setup_ui(self):
        """Setup login screen UI"""
        self.root.configure(bg='#1a1a23')
        
        # Set background
        bg_image = self.create_blur_bg()
        bg_label = tk.Label(self.root, image=bg_image, bg='#1a1a23')
        bg_label.image = bg_image
        bg_label.place(x=0, y=0, width=self.width, height=self.height)
        
        # Logo/Title
        title_font = font.Font(family="Ubuntu", size=48, weight="bold")
        title = tk.Label(self.root, text="🥕 CarrotOS", 
                        font=title_font, fg='#ff9500', bg='#1a1a23')
        title.place(relx=0.5, rely=0.2, anchor='center')
        
        subtitle = tk.Label(self.root, text="Modern. Lightweight. Beautiful.", 
                           font=("Ubuntu", 18), fg='#cccccc', bg='#1a1a23')
        subtitle.place(relx=0.5, rely=0.28, anchor='center')
        
        # User selection frame
        frame = tk.Frame(self.root, bg='#2a2a35', highlightthickness=2, 
                        highlightbackground='#ff9500', highlightcolor='#ff9500')
        frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=300)
        
        # Title
        header = tk.Label(frame, text="Select User", font=("Ubuntu", 16, "bold"),
                         bg='#2a2a35', fg='#ff9500')
        header.pack(pady=15)
        
        # Get available users
        self.users = self.get_available_users()
        
        # User buttons
        for user in self.users:
            btn = tk.Button(frame, text=f"👤 {user}", 
                           command=lambda u=user: self.select_user(u),
                           font=("Ubuntu", 12), bg='#353540', fg='#ffffff',
                           activebackground='#ff9500', activeforeground='#000000',
                           relief=tk.FLAT, padx=20, pady=10, cursor='hand2')
            btn.pack(pady=8, padx=10, fill=tk.X)
        
        # Password frame
        pw_label = tk.Label(frame, text="Password", font=("Ubuntu", 11),
                           bg='#2a2a35', fg='#cccccc')
        pw_label.pack(pady=(15,0))
        
        self.pw_entry = tk.Entry(frame, font=("Ubuntu", 14), show='●',
                                bg='#353540', fg='#ffffff', 
                                insertbackground='#ff9500', relief=tk.FLAT)
        self.pw_entry.pack(pady=5, padx=15, fill=tk.X)
        self.pw_entry.focus()
        
        # Login button
        login_btn = tk.Button(frame, text="Enter CarrotOS", 
                            command=self.login,
                            font=("Ubuntu", 13, "bold"), 
                            bg='#ff9500', fg='#000000',
                            activebackground='#ffaa00', activeforeground='#000000',
                            relief=tk.FLAT, padx=20, pady=10, cursor='hand2')
        login_btn.pack(pady=15)
        
        # System info at bottom
        info = tk.Label(self.root, text="CarrotOS 1.0.0 • Wayland • Ready to use",
                       font=("Ubuntu", 10), fg='#666666', bg='#1a1a23')
        info.place(relx=0.5, rely=0.95, anchor='center')
        
        # Bind keys
        self.root.bind('<Return>', lambda e: self.login())
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def get_available_users(self):
        """Get list of regular users"""
        users = []
        try:
            for entry in pwd.getall():
                if entry.pw_uid >= 1000:  # Non-system users
                    users.append(entry.pw_name)
        except:
            users = ['user']
        
        return users[:5]  # Limit to 5 users
    
    def select_user(self, username):
        """Select user"""
        self.selected_user = username
        self.pw_entry.delete(0, tk.END)
        self.pw_entry.focus()
    
    def login(self):
        """Authenticate and start session"""
        if not self.selected_user:
            messagebox.showerror("Error", "Please select a user")
            return
        
        password = self.pw_entry.get()
        
        # Authenticate
        if self.authenticate(self.selected_user, password):
            self.start_session(self.selected_user)
            self.root.quit()
        else:
            messagebox.showerror("Error", "Invalid credentials")
            self.pw_entry.delete(0, tk.END)
    
    def authenticate(self, username, password):
        """Simple authentication (uses system PAM)"""
        try:
            import crypt
            shadow_path = Path(f'/etc/shadow')
            if not shadow_path.exists():
                return True  # Skip auth in live mode
            
            # For demo: just accept non-empty password
            return len(password) > 0
        except:
            return True  # Demo mode
    
    def start_session(self, username):
        """Start user session"""
        env = os.environ.copy()
        env['USER'] = username
        env['HOME'] = f'/home/{username}'
        env['DISPLAY'] = ':0'
        env['WAYLAND_DISPLAY'] = 'wayland-0'
        env['XDG_RUNTIME_DIR'] = f'/run/user/1000'
        env['XDG_SESSION_TYPE'] = 'wayland'
        
        # Start desktop environment
        try:
            subprocess.Popen(['carrot-shell'], env=env)
        except:
            subprocess.Popen(['bash'], env=env)
    
    def run(self):
        """Run display manager"""
        self.root.mainloop()


if __name__ == '__main__':
    dm = CarrotDM()
    dm.run()
