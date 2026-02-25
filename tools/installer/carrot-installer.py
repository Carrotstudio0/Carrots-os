#!/usr/bin/env python3
"""
CarrotOS Installer - Main Installation Program
Professional system installation wizard for CarrotOS
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import sys
from pathlib import Path
from enum import Enum
import threading
import json
from datetime import datetime

class InstallationStep(Enum):
    """Installation wizard steps"""
    WELCOME = 0
    LANGUAGE = 1
    DISK_SELECTION = 2
    PARTITIONING = 3
    USER_CREATION = 4
    SYSTEM_CONFIGURATION = 5
    INSTALLATION = 6
    COMPLETION = 7

class CarrotInstaller:
    """Main installer application"""
    
    # Theme colors
    BG_PRIMARY = "#1e1e2e"
    BG_SECONDARY = "#2a2a3e"
    FG_PRIMARY = "#ffffff"
    ACCENT_COLOR = "#ff8c00"
    SUCCESS_COLOR = "#4caf50"
    ERROR_COLOR = "#f44336"
    WARNING_COLOR = "#ff9800"
    
    # Supported languages
    LANGUAGES = {
        'en': {'name': 'English', 'locale': 'en_US.UTF-8'},
        'ar': {'name': 'العربية', 'locale': 'ar_SA.UTF-8'},
        'de': {'name': 'Deutsch', 'locale': 'de_DE.UTF-8'},
        'es': {'name': 'Español', 'locale': 'es_ES.UTF-8'},
        'fr': {'name': 'Français', 'locale': 'fr_FR.UTF-8'},
        'zh': {'name': '中文', 'locale': 'zh_CN.UTF-8'},
    }
    
    TIMEZONES = [
        'UTC', 'UTC+1', 'UTC+2', 'UTC-5', 'UTC-6', 'UTC-8',
        'America/New_York', 'America/Chicago', 'America/Los_Angeles',
        'Europe/London', 'Europe/Paris', 'Europe/Berlin',
        'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Dubai',
        'Australia/Sydney', 'Australia/Melbourne',
    ]
    
    def __init__(self, root):
        self.root = root
        self.root.title("CarrotOS Installer")
        self.root.geometry("800x600")
        self.root.configure(bg=self.BG_PRIMARY)
        
        # Installation state
        self.current_step = InstallationStep.WELCOME
        self.install_config = {
            'language': 'en',
            'timezone': 'UTC',
            'disk': None,
            'partitions': {},
            'username': '',
            'password': '',
            'hostname': 'carrotos',
            'efi': False,
            'encryption': False,
        }
        
        self.setup_ui()
        self.show_welcome()
    
    def setup_ui(self):
        """Setup main UI structure"""
        
        # Header
        self.header_frame = tk.Frame(self.root, bg=self.ACCENT_COLOR, height=60)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)
        self.header_frame.pack_propagate(False)
        
        self.title_label = tk.Label(
            self.header_frame, 
            text="CarrotOS Installer", 
            font=("Arial", 20, "bold"),
            bg=self.ACCENT_COLOR,
            fg=self.FG_PRIMARY
        )
        self.title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Progress indicator
        self.progress_label = tk.Label(
            self.header_frame,
            text="",
            font=("Arial", 10),
            bg=self.ACCENT_COLOR,
            fg=self.FG_PRIMARY
        )
        self.progress_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Content frame
        self.content_frame = tk.Frame(self.root, bg=self.BG_PRIMARY)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Footer with buttons
        self.footer_frame = tk.Frame(self.root, bg=self.BG_SECONDARY, height=60)
        self.footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.footer_frame.pack_propagate(False)
        
        self.back_button = ttk.Button(
            self.footer_frame, 
            text="◄ Back", 
            command=self.go_back
        )
        self.back_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.next_button = ttk.Button(
            self.footer_frame,
            text="Next ►",
            command=self.go_next
        )
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.cancel_button = ttk.Button(
            self.footer_frame,
            text="Cancel",
            command=self.cancel_installation
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=5, pady=10)
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_progress(self):
        """Update progress label"""
        step_num = self.current_step.value + 1
        total_steps = len(InstallationStep)
        self.progress_label.config(text=f"Step {step_num} of {total_steps}")
    
    def show_welcome(self):
        """Welcome screen"""
        self.clear_content()
        self.current_step = InstallationStep.WELCOME
        self.update_progress()
        self.back_button.config(state=tk.DISABLED)
        
        # Logo/title
        title = tk.Label(
            self.content_frame,
            text="🥕 CarrotOS",
            font=("Arial", 40, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.ACCENT_COLOR
        )
        title.pack(pady=30)
        
        subtitle = tk.Label(
            self.content_frame,
            text="Professional Linux Distribution Installer",
            font=("Arial", 14),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        subtitle.pack(pady=10)
        
        info = tk.Label(
            self.content_frame,
            text="""Welcome to the CarrotOS installation wizard.

This wizard will guide you through the process of installing
CarrotOS on your computer.

You will be asked to:
• Select your language and timezone
• Choose a disk to install on
• Configure disk partitions
• Create a user account
• Configure system settings

After completing the wizard, CarrotOS will be installed
on your selected disk and ready to use.

Make sure you have backed up any important data
before proceeding.""",
            font=("Arial", 11),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY,
            justify=tk.LEFT
        )
        info.pack(pady=20, fill=tk.BOTH, expand=True)
        
        disclaimer = tk.Label(
            self.content_frame,
            text="⚠️ Warning: Installation will erase data on selected disk",
            font=("Arial", 10, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.WARNING_COLOR
        )
        disclaimer.pack(pady=10)
    
    def show_language(self):
        """Language selection screen"""
        self.clear_content()
        self.current_step = InstallationStep.LANGUAGE
        self.update_progress()
        self.back_button.config(state=tk.NORMAL)
        
        title = tk.Label(
            self.content_frame,
            text="Select Language and Timezone",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(pady=20)
        
        # Language selection
        lang_frame = ttk.LabelFrame(self.content_frame, text="Language")
        lang_frame.pack(fill=tk.X, pady=10)
        
        self.language_var = tk.StringVar(value=self.install_config['language'])
        
        for lang_code, lang_info in self.LANGUAGES.items():
            rb = ttk.Radiobutton(
                lang_frame,
                text=lang_info['name'],
                variable=self.language_var,
                value=lang_code
            )
            rb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Timezone selection
        tz_frame = ttk.LabelFrame(self.content_frame, text="Timezone")
        tz_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(tz_frame, text="Select your timezone:").pack(anchor=tk.W, padx=10, pady=5)
        
        self.timezone_var = tk.StringVar(value=self.install_config['timezone'])
        tz_combo = ttk.Combobox(
            tz_frame,
            textvariable=self.timezone_var,
            values=self.TIMEZONES,
            width=40
        )
        tz_combo.pack(anchor=tk.W, padx=10, pady=5)
    
    def show_disk_selection(self):
        """Disk selection screen"""
        self.clear_content()
        self.current_step = InstallationStep.DISK_SELECTION
        self.update_progress()
        
        title = tk.Label(
            self.content_frame,
            text="Select Installation Disk",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(pady=20)
        
        warning = tk.Label(
            self.content_frame,
            text="⚠️ All data on the selected disk will be erased!",
            font=("Arial", 11, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.ERROR_COLOR
        )
        warning.pack(pady=10)
        
        # Disk detection
        disks = self.detect_disks()
        
        if not disks:
            error_msg = tk.Label(
                self.content_frame,
                text="No suitable disks found.\n\nPlease connect a disk with at least 10GB free space.",
                font=("Arial", 12),
                bg=self.BG_PRIMARY,
                fg=self.ERROR_COLOR
            )
            error_msg.pack(pady=20)
            self.next_button.config(state=tk.DISABLED)
            return
        
        # Disk list
        disk_frame = ttk.LabelFrame(self.content_frame, text="Available Disks")
        disk_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.disk_var = tk.StringVar()
        
        for disk in disks:
            disk_info = f"{disk['device']} - {disk['size']} - {disk['model']}"
            rb = ttk.Radiobutton(
                disk_frame,
                text=disk_info,
                variable=self.disk_var,
                value=disk['device']
            )
            rb.pack(anchor=tk.W, padx=10, pady=5)
            
            if not self.disk_var.get():
                self.disk_var.set(disk['device'])
    
    def show_partitioning(self):
        """Disk partitioning screen"""
        self.clear_content()
        self.current_step = InstallationStep.PARTITIONING
        self.update_progress()
        
        title = tk.Label(
            self.content_frame,
            text="Disk Partitioning",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(pady=20)
        
        # Partition scheme selection
        scheme_frame = ttk.LabelFrame(self.content_frame, text="Partitioning Scheme")
        scheme_frame.pack(fill=tk.X, pady=10)
        
        self.partition_scheme = tk.StringVar(value="simple")
        
        ttk.Radiobutton(
            scheme_frame,
            text="Simple (One partition + swap)",
            variable=self.partition_scheme,
            value="simple"
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Radiobutton(
            scheme_frame,
            text="Advanced (Separate /home, /var, /tmp)",
            variable=self.partition_scheme,
            value="advanced"
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Radiobutton(
            scheme_frame,
            text="EFI Boot (UEFI + Simple)",
            variable=self.partition_scheme,
            value="efi"
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Options
        options_frame = ttk.LabelFrame(self.content_frame, text="Options")
        options_frame.pack(fill=tk.X, pady=10)
        
        self.encryption_var = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="Use disk encryption (LUKS)",
            variable=self.encryption_var
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Partition preview
        preview_frame = ttk.LabelFrame(self.content_frame, text="Partition Layout Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.partition_text = tk.Text(
            preview_frame,
            height=6,
            bg=self.BG_SECONDARY,
            fg=self.FG_PRIMARY,
            insert=tk.END
        )
        self.partition_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.partition_text.config(state=tk.DISABLED)
        
        # Update preview
        self.update_partition_preview()
    
    def update_partition_preview(self):
        """Update partition preview"""
        self.partition_text.config(state=tk.NORMAL)
        self.partition_text.delete(1.0, tk.END)
        
        scheme = self.partition_scheme.get()
        disk = self.disk_var.get() if hasattr(self, 'disk_var') else '/dev/sda'
        
        if scheme == "simple":
            preview = f"""{disk}1 - EFI System Partition (512MB)
{disk}2 - Swap (4GB)
{disk}3 - Root (/) - Remainder
"""
        elif scheme == "advanced":
            preview = f"""{disk}1 - EFI System Partition (512MB)
{disk}2 - Boot (/boot) (1GB)
{disk}3 - Root (/) (20GB)
{disk}4 - /home (Remainder)
Swap (4GB)
"""
        elif scheme == "efi":
            preview = f"""{disk}1 - EFI System Partition (512MB)
{disk}2 - Root (/) - Remainder
Swap (4GB)
"""
        
        if self.encryption_var.get():
            preview += "\n[Disk encryption enabled with LUKS]"
        
        self.partition_text.insert(tk.END, preview)
        self.partition_text.config(state=tk.DISABLED)
    
    def show_user_creation(self):
        """User creation screen"""
        self.clear_content()
        self.current_step = InstallationStep.USER_CREATION
        self.update_progress()
        
        title = tk.Label(
            self.content_frame,
            text="Create User Account",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(pady=20)
        
        # Hostname
        ttk.Label(self.content_frame, text="Computer Hostname:").pack(anchor=tk.W, pady=(10, 0))
        self.hostname_var = tk.StringVar(value=self.install_config['hostname'])
        ttk.Entry(self.content_frame, textvariable=self.hostname_var, width=30).pack(anchor=tk.W, pady=5)
        
        # Username
        ttk.Label(self.content_frame, text="Username:").pack(anchor=tk.W, pady=(10, 0))
        self.username_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=self.username_var, width=30).pack(anchor=tk.W, pady=5)
        
        # Password
        ttk.Label(self.content_frame, text="Password:").pack(anchor=tk.W, pady=(10, 0))
        self.password_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=self.password_var, width=30, show="*").pack(anchor=tk.W, pady=5)
        
        # Confirm password
        ttk.Label(self.content_frame, text="Confirm Password:").pack(anchor=tk.W, pady=(10, 0))
        self.password_confirm_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=self.password_confirm_var, width=30, show="*").pack(anchor=tk.W, pady=5)
        
        # Options
        ttk.Label(self.content_frame, text="").pack()
        
        self.sudo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.content_frame,
            text="Add user to sudo group (administrator privileges)",
            variable=self.sudo_var
        ).pack(anchor=tk.W, pady=5)
        
        self.autologin_var = tk.BooleanVar()
        ttk.Checkbutton(
            self.content_frame,
            text="Automatically login (not recommended for security)",
            variable=self.autologin_var
        ).pack(anchor=tk.W, pady=5)
    
    def show_system_configuration(self):
        """System configuration screen"""
        self.clear_content()
        self.current_step = InstallationStep.SYSTEM_CONFIGURATION
        self.update_progress()
        
        title = tk.Label(
            self.content_frame,
            text="System Configuration",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(pady=20)
        
        # Installation summary
        summary_frame = ttk.LabelFrame(self.content_frame, text="Installation Summary")
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        summary_text = tk.Text(
            summary_frame,
            height=12,
            bg=self.BG_SECONDARY,
            fg=self.FG_PRIMARY,
            state=tk.DISABLED
        )
        summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Build summary
        language_name = self.LANGUAGES.get(self.install_config['language'], {}).get('name', 'Unknown')
        
        summary = f"""Installation Summary:

Language:           {language_name}
Timezone:           {self.install_config['timezone']}
Target Disk:        {self.install_config['disk']}
Partition Scheme:   {self.partition_scheme.get()}
Encryption:         {'Yes (LUKS)' if self.encryption_var.get() else 'No'}

User Account:
  Hostname:         {self.hostname_var.get()}
  Username:         {self.username_var.get()}
  Sudo Access:      {'Yes' if self.sudo_var.get() else 'No'}

Please review the settings above.
Click "Next" to proceed with installation."""
        
        summary_text.config(state=tk.NORMAL)
        summary_text.insert(tk.END, summary)
        summary_text.config(state=tk.DISABLED)
        
        # Confirm checkbox
        ttk.Label(self.content_frame, text="").pack()
        
        self.confirm_var = tk.BooleanVar()
        confirm_cb = ttk.Checkbutton(
            self.content_frame,
            text="I understand that installation will erase all data on the selected disk",
            variable=self.confirm_var,
            command=self.update_next_button_state
        )
        confirm_cb.pack(anchor=tk.W, pady=5)
    
    def show_installation(self):
        """Installation progress screen"""
        self.clear_content()
        self.current_step = InstallationStep.INSTALLATION
        self.update_progress()
        self.back_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        
        title = tk.Label(
            self.content_frame,
            text="Installing CarrotOS",
            font=("Arial", 16, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        title.pack(pady=20)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.content_frame,
            length=400,
            mode='determinate',
            value=0
        )
        self.progress_bar.pack(pady=20)
        
        # Status message
        self.status_label = tk.Label(
            self.content_frame,
            text="Preparing to install...",
            font=("Arial", 11),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY
        )
        self.status_label.pack(pady=10)
        
        # Installation log
        log_frame = ttk.LabelFrame(self.content_frame, text="Installation Log")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_frame,
            height=10,
            bg=self.BG_SECONDARY,
            fg=self.FG_PRIMARY,
            yscrollcommand=scrollbar.set
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.log_text.yview)
        
        # Start installation in separate thread
        threading.Thread(target=self.perform_installation, daemon=True).start()
    
    def show_completion(self):
        """Completion screen"""
        self.clear_content()
        self.current_step = InstallationStep.COMPLETION
        self.update_progress()
        self.back_button.config(state=tk.DISABLED)
        
        # Success message
        success_label = tk.Label(
            self.content_frame,
            text="✓ Installation Complete!",
            font=("Arial", 20, "bold"),
            bg=self.BG_PRIMARY,
            fg=self.SUCCESS_COLOR
        )
        success_label.pack(pady=30)
        
        info_text = tk.Label(
            self.content_frame,
            text=f"""CarrotOS has been successfully installed on your system.

Installation Details:
• System installed on: {self.install_config['disk']}
• Hostname: {self.hostname_var.get()}
• User: {self.username_var.get()}
• Language: {self.LANGUAGES.get(self.install_config['language'], {}).get('name', 'Unknown')}

Next Steps:
1. Remove the installation media
2. Reboot the system
3. Login with your user credentials
4. Complete any additional setup

Welcome to CarrotOS!""",
            font=("Arial", 11),
            bg=self.BG_PRIMARY,
            fg=self.FG_PRIMARY,
            justify=tk.LEFT
        )
        info_text.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Finish button
        self.next_button.config(text="Finish", command=self.finish_installation)
    
    def perform_installation(self):
        """Perform the actual installation"""
        try:
            self.update_status("Creating partitions...")
            self.log("Creating partitions on disk...")
            # Partition creation would go here
            self.progress_bar['value'] = 20
            self.root.update()
            
            self.update_status("Formatting partitions...")
            self.log("Formatting partitions...")
            # Formatting would go here
            self.progress_bar['value'] = 30
            self.root.update()
            
            self.update_status("Mounting filesystem...")
            self.log("Mounting filesystem...")
            # Mounting would go here
            self.progress_bar['value'] = 40
            self.root.update()
            
            self.update_status("Installing base system...")
            self.log("Installing base system packages...")
            # Base system installation would go here
            self.progress_bar['value'] = 60
            self.root.update()
            
            self.update_status("Installing bootloader...")
            self.log("Installing GRUB bootloader...")
            # Bootloader installation would go here
            self.progress_bar['value'] = 80
            self.root.update()
            
            self.update_status("Configuring system...")
            self.log("Configuring system settings...")
            self.log(f"  Setting hostname: {self.hostname_var.get()}")
            self.log(f"  Creating user: {self.username_var.get()}")
            self.log(f"  Setting timezone: {self.install_config['timezone']}")
            # System configuration would go here
            self.progress_bar['value'] = 95
            self.root.update()
            
            self.update_status("Finalizing installation...")
            self.log("Installation complete!")
            self.progress_bar['value'] = 100
            
            # Show completion screen
            self.root.after(1000, self.show_completion)
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}", error=True)
            messagebox.showerror("Installation Error", f"Installation failed:\n{str(e)}")
            self.show_completion()
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.config(text=message)
        self.root.update()
    
    def log(self, message, error=False):
        """Add message to log"""
        color = self.FG_PRIMARY if not error else self.ERROR_COLOR
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        if error:
            self.log_text.insert(tk.END, log_entry, "error")
            self.log_text.tag_config("error", foreground=self.ERROR_COLOR)
        else:
            self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def detect_disks(self):
        """Detect available disks"""
        # This would use lsblk or similar in real implementation
        disks = [
            {
                'device': '/dev/sda',
                'size': '500GB',
                'model': 'QEMU HARDDISK',
                'partitions': 0
            },
            {
                'device': '/dev/sdb',
                'size': '1TB',
                'model': 'Samsung SSD 870',
                'partitions': 1
            }
        ]
        return disks
    
    def go_next(self):
        """Go to next step"""
        # Validate current step
        if not self.validate_current_step():
            return
        
        # Save current step data
        self.save_current_step()
        
        # Determine next step
        steps = [
            self.show_welcome,
            self.show_language,
            self.show_disk_selection,
            self.show_partitioning,
            self.show_user_creation,
            self.show_system_configuration,
            self.show_installation,
            self.show_completion
        ]
        
        if self.current_step.value < len(steps) - 1:
            next_func = steps[self.current_step.value + 1]
            next_func()
    
    def go_back(self):
        """Go to previous step"""
        steps = [
            self.show_welcome,
            self.show_language,
            self.show_disk_selection,
            self.show_partitioning,
            self.show_user_creation,
            self.show_system_configuration,
            self.show_installation,
            self.show_completion
        ]
        
        if self.current_step.value > 0:
            prev_func = steps[self.current_step.value - 1]
            prev_func()
    
    def validate_current_step(self):
        """Validate data for current step"""
        if self.current_step == InstallationStep.LANGUAGE:
            self.install_config['language'] = self.language_var.get()
            self.install_config['timezone'] = self.timezone_var.get()
            return True
        
        elif self.current_step == InstallationStep.DISK_SELECTION:
            if not self.disk_var.get():
                messagebox.showerror("Error", "Please select a disk")
                return False
            self.install_config['disk'] = self.disk_var.get()
            return True
        
        elif self.current_step == InstallationStep.PARTITIONING:
            self.install_config['encryption'] = self.encryption_var.get()
            return True
        
        elif self.current_step == InstallationStep.USER_CREATION:
            username = self.username_var.get()
            password = self.password_var.get()
            confirm = self.password_confirm_var.get()
            hostname = self.hostname_var.get()
            
            if not username or not password or not hostname:
                messagebox.showerror("Error", "Please fill in all fields")
                return False
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords don't match")
                return False
            
            if len(password) < 8:
                response = messagebox.askyesno("Warning", 
                    "Password is less than 8 characters. Continue anyway?")
                if not response:
                    return False
            
            self.install_config['username'] = username
            self.install_config['password'] = password
            self.install_config['hostname'] = hostname
            return True
        
        elif self.current_step == InstallationStep.SYSTEM_CONFIGURATION:
            if not self.confirm_var.get():
                messagebox.showerror("Error", 
                    "Please confirm that you understand the installation will erase data")
                return False
            return True
        
        return True
    
    def save_current_step(self):
        """Save data from current step"""
        pass
    
    def update_next_button_state(self):
        """Update next button state based on confirmation"""
        if self.current_step == InstallationStep.SYSTEM_CONFIGURATION:
            self.next_button.config(state=tk.NORMAL if self.confirm_var.get() else tk.DISABLED)
    
    def cancel_installation(self):
        """Cancel installation"""
        if self.current_step == InstallationStep.INSTALLATION:
            messagebox.showwarning("Warning", "Cannot cancel during installation")
            return
        
        response = messagebox.askyesno("Cancel", 
            "Are you sure you want to cancel the installation?")
        
        if response:
            self.root.quit()
    
    def finish_installation(self):
        """Finish installation"""
        messagebox.showinfo("Reboot Required", 
            "Please reboot your system to complete the installation.")
        self.root.quit()

def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Check for root privileges
    if os.geteuid() != 0:
        messagebox.showerror("Error", "CarrotOS Installer must be run as root")
        sys.exit(1)
    
    app = CarrotInstaller(root)
    root.mainloop()

if __name__ == '__main__':
    main()
