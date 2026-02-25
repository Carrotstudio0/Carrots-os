#!/usr/bin/env python3
"""
CarrotOS Terminal Emulator
VT100-compatible terminal with modern UI
"""

import os
import sys
import subprocess
import threading
import queue
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import font, scrolledtext
except ImportError:
    print("Error: tkinter required")
    sys.exit(1)

class CarrotTerminal:
    """Modern Terminal Emulator"""
    
    def __init__(self, command=None):
        self.root = tk.Tk()
        self.root.title("Carrot Terminal")
        self.root.geometry("900x600")
        self.root.configure(bg='#0d0d0d')
        
        self.process = None
        self.command_queue = queue.Queue()
        self.output_queue = queue.Queue()
        
        self.setup_ui()
        self.start_shell()
        
        if command:
            self.execute_command(command)
    
    def setup_ui(self):
        """Setup terminal UI"""
        # Top bar with info
        top_bar = tk.Frame(self.root, bg='#1a1a23', height=30)
        top_bar.pack(fill=tk.X, padx=0, pady=0)
        
        title = tk.Label(top_bar, text="🖥️  CarrotOS Terminal",
                        font=("Ubuntu", 11, "bold"), bg='#1a1a23', fg='#ff9500')
        title.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Terminal display
        terminal_frame = tk.Frame(self.root, bg='#0d0d0d')
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create terminal text widget with scrollbar
        scrollbar = tk.Scrollbar(terminal_frame, bg='#1a1a23')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.terminal = tk.Text(
            terminal_frame,
            bg='#0d0d0d',
            fg='#00ff00',
            font=("DejaVu Sans Mono", 11),
            insertbackground='#00ff00',
            relief=tk.FLAT,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED
        )
        self.terminal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.terminal.yview)
        
        # Configure tags for colors
        self.terminal.tag_config('info', foreground='#00ff00')
        self.terminal.tag_config('error', foreground='#ff3333')
        self.terminal.tag_config('warning', foreground='#ffaa00')
        self.terminal.tag_config('success', foreground='#00ff00')
        self.terminal.tag_config('input', foreground='#cccccc')
        
        # Input line at bottom
        input_frame = tk.Frame(self.root, bg='#1a1a23')
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        prompt_label = tk.Label(input_frame, text="$ ", 
                               font=("DejaVu Sans Mono", 11),
                               bg='#1a1a23', fg='#00ff00')
        prompt_label.pack(side=tk.LEFT)
        
        self.input_field = tk.Entry(
            input_frame,
            font=("DejaVu Sans Mono", 11),
            bg='#1a1a23',
            fg='#cccccc',
            insertbackground='#00ff00',
            relief=tk.FLAT,
            bd=0
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_field.bind('<Return>', self.handle_input)
        self.input_field.focus()
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready",
                                  bg='#1a1a23', fg='#666666',
                                  anchor=tk.W, padx=5, pady=3)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Start output thread
        self.update_output()
    
    def start_shell(self):
        """Start shell process"""
        try:
            shell = os.environ.get('SHELL', '/bin/bash')
            self.process = subprocess.Popen(
                [shell],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Start output thread
            self.output_thread = threading.Thread(target=self.read_output, daemon=True)
            self.output_thread.start()
            
            self.print_output("CarrotOS Terminal v1.0.0\n", 'info')
            self.print_output("Type 'help' for commands, 'exit' to quit\n\n", 'info')
            self.print_output(f"$ ", 'info')
            
        except Exception as e:
            self.print_output(f"Error: {e}\n", 'error')
    
    def read_output(self):
        """Read output from shell"""
        try:
            while True:
                if self.process and self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        self.output_queue.put(('output', line))
                    else:
                        break
        except:
            pass
    
    def print_output(self, text, tag='info'):
        """Print to terminal"""
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, text, tag)
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)
    
    def handle_input(self, event):
        """Handle user input"""
        command = self.input_field.get()
        self.input_field.delete(0, tk.END)
        
        if not command:
            return
        
        self.print_output(command + '\n', 'input')
        
        # Handle built-in commands
        if command == 'exit':
            self.root.quit()
            return
        elif command == 'help':
            self.print_output("CarrotOS Terminal Help:\n", 'info')
            self.print_output("  exit     - Close terminal\n", 'info')
            self.print_output("  help     - Show this help\n", 'info')
            self.print_output("  clear    - Clear screen\n", 'info')
            self.print_output("  whoami   - Show current user\n", 'info')
            self.print_output("  date     - Show date/time\n\n", 'info')
            self.print_output("$ ", 'info')
            return
        elif command == 'clear':
            self.terminal.config(state=tk.NORMAL)
            self.terminal.delete(1.0, tk.END)
            self.terminal.config(state=tk.DISABLED)
            self.print_output("$ ", 'info')
            return
        elif command == 'whoami':
            user = os.environ.get('USER', 'unknown')
            self.print_output(f"{user}\n$ ", 'info')
            return
        
        # Execute command in shell
        try:
            if self.process:
                self.process.stdin.write(command + '\n')
                self.process.stdin.flush()
        except:
            self.print_output("Error executing command\n$ ", 'error')
    
    def execute_command(self, command):
        """Execute a command"""
        self.input_field.insert(0, command)
        self.handle_input(None)
    
    def update_output(self):
        """Update terminal with output"""
        try:
            while True:
                msg_type, msg = self.output_queue.get_nowait()
                if msg_type == 'output':
                    self.print_output(msg)
        except queue.Empty:
            pass
        
        self.root.after(100, self.update_output)
    
    def run(self):
        """Run terminal"""
        self.root.mainloop()


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    term = CarrotTerminal(cmd)
    term.run()
