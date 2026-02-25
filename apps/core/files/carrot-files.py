#!/usr/bin/env python3
"""
CarrotOS File Manager
Modern lightweight file explorer
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, simpledialog
    from PIL import Image, ImageTk
except ImportError:
    print("Dependencies needed: pip3 install Pillow")
    sys.exit(1)

class CarrotFileManager:
    """Modern File Manager"""
    
    def __init__(self, root_path=None):
        self.root = tk.Tk()
        self.root.title("Carrot Files")
        self.root.geometry("900x600")
        self.root.configure(bg='#1a1a23')
        
        self.current_path = Path(root_path or os.path.expanduser('~'))
        self.clipboard_file = None
        self.clipboard_mode = None
        
        self.setup_ui()
        self.load_files()
    
    def setup_ui(self):
        """Setup file manager interface"""
        # Top bar
        top_frame = tk.Frame(self.root, bg='#2a2a35', height=60)
        top_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Navigation buttons
        btn_frame = tk.Frame(top_frame, bg='#2a2a35')
        btn_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.back_btn = tk.Button(btn_frame, text="← Back", command=self.go_back,
                                 bg='#353540', fg='#ff9500', relief=tk.FLAT, padx=10)
        self.back_btn.pack(side=tk.LEFT, padx=5)
        
        self.forward_btn = tk.Button(btn_frame, text="Forward →", command=self.go_forward,
                                    bg='#353540', fg='#ff9500', relief=tk.FLAT, padx=10)
        self.forward_btn.pack(side=tk.LEFT, padx=5)
        
        self.home_btn = tk.Button(btn_frame, text="🏠 Home", command=self.go_home,
                                 bg='#353540', fg='#ff9500', relief=tk.FLAT, padx=10)
        self.home_btn.pack(side=tk.LEFT, padx=5)
        
        # Address bar
        addr_frame = tk.Frame(top_frame, bg='#2a2a35')
        addr_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.addr_entry = tk.Entry(addr_frame, font=("Monospace", 10),
                                  bg='#353540', fg='#cccccc', 
                                  insertbackground='#ff9500', relief=tk.FLAT)
        self.addr_entry.pack(fill=tk.X, pady=10)
        self.addr_entry.bind('<Return>', lambda e: self.navigate_to())
        
        # Main content area
        content_frame = tk.Frame(self.root, bg='#1a1a23')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for files
        self.tree = ttk.Treeview(content_frame, columns=('Size', 'Modified'), 
                                height=20, style='Treeview')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.column("#0", width=400)
        self.tree.column("Size", width=100)
        self.tree.column("Modified", width=200)
        
        self.tree.heading("#0", text="Name", anchor=tk.W)
        self.tree.heading("Size", text="Size", anchor=tk.W)
        self.tree.heading("Modified", text="Modified", anchor=tk.W)
        
        self.tree.bind('<Double-Button-1>', lambda e: self.open_item())
        self.tree.bind('<Button-3>', lambda e: self.show_context_menu(e))
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", 
                                  bg='#2a2a35', fg='#888888', 
                                  anchor=tk.W, padx=10, pady=5)
        self.status_bar.pack(fill=tk.X)
    
    def load_files(self):
        """Load and display files in current directory"""
        self.addr_entry.delete(0, tk.END)
        self.addr_entry.insert(0, str(self.current_path))
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            items = sorted(self.current_path.iterdir(), 
                          key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                try:
                    is_dir = item.is_dir()
                    icon = "📁" if is_dir else "📄"
                    
                    # Size
                    if is_dir:
                        size = "-"
                    else:
                        size = self.format_size(item.stat().st_size)
                    
                    # Modified
                    mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                    
                    self.tree.insert('', 'end', text=f"{icon} {item.name}",
                                    values=(size, mtime))
                except:
                    pass
            
            count = len(items)
            self.status_bar.config(text=f"{count} items")
            
        except PermissionError:
            messagebox.showerror("Error", "Permission denied")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def navigate_to(self):
        """Navigate to address bar path"""
        path = self.addr_entry.get()
        try:
            new_path = Path(path).expanduser()
            if new_path.is_dir():
                self.current_path = new_path
                self.load_files()
            else:
                messagebox.showerror("Error", "Not a directory")
        except:
            messagebox.showerror("Error", "Invalid path")
    
    def go_back(self):
        """Go to parent directory"""
        if self.current_path.parent != self.current_path:
            self.current_path = self.current_path.parent
            self.load_files()
    
    def go_forward(self):
        """Go forward (placeholder)"""
        pass
    
    def go_home(self):
        """Go to home directory"""
        self.current_path = Path.home()
        self.load_files()
    
    def open_item(self):
        """Open selected file or directory"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        name = self.tree.item(item, 'text').split(' ', 1)[1]
        path = self.current_path / name
        
        if path.is_dir():
            self.current_path = path
            self.load_files()
        else:
            # Open with default app
            try:
                import subprocess
                subprocess.Popen(['xdg-open', str(path)])
            except:
                pass
    
    def show_context_menu(self, event):
        """Show context menu"""
        menu = tk.Menu(self.root, tearoff=0, bg='#2a2a35', fg='#ffffff')
        
        menu.add_command(label="Copy", command=self.copy_file)
        menu.add_command(label="Cut", command=self.cut_file)
        menu.add_command(label="Paste", command=self.paste_file)
        menu.add_separator()
        menu.add_command(label="Delete", command=self.delete_file)
        menu.add_command(label="Rename", command=self.rename_file)
        menu.add_separator()
        menu.add_command(label="Properties", command=self.show_properties)
        
        menu.post(event.x_root, event.y_root)
    
    def copy_file(self):
        """Copy selected file"""
        selection = self.tree.selection()
        if selection:
            name = self.tree.item(selection[0], 'text').split(' ', 1)[1]
            self.clipboard_file = self.current_path / name
            self.clipboard_mode = 'copy'
    
    def cut_file(self):
        """Cut selected file"""
        selection = self.tree.selection()
        if selection:
            name = self.tree.item(selection[0], 'text').split(' ', 1)[1]
            self.clipboard_file = self.current_path / name
            self.clipboard_mode = 'cut'
    
    def paste_file(self):
        """Paste file"""
        if not self.clipboard_file:
            return
        
        try:
            dest = self.current_path / self.clipboard_file.name
            
            if self.clipboard_mode == 'copy':
                if self.clipboard_file.is_dir():
                    shutil.copytree(self.clipboard_file, dest)
                else:
                    shutil.copy2(self.clipboard_file, dest)
            elif self.clipboard_mode == 'cut':
                shutil.move(str(self.clipboard_file), str(dest))
            
            self.load_files()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def delete_file(self):
        """Delete selected file"""
        selection = self.tree.selection()
        if not selection:
            return
        
        name = self.tree.item(selection[0], 'text').split(' ', 1)[1]
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            try:
                path = self.current_path / name
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                self.load_files()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def rename_file(self):
        """Rename file"""
        selection = self.tree.selection()
        if not selection:
            return
        
        name = self.tree.item(selection[0], 'text').split(' ', 1)[1]
        new_name = simpledialog.askstring("Rename", f"New name for '{name}':")
        
        if new_name:
            try:
                old_path = self.current_path / name
                new_path = self.current_path / new_name
                old_path.rename(new_path)
                self.load_files()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def show_properties(self):
        """Show file properties"""
        selection = self.tree.selection()
        if not selection:
            return
        
        name = self.tree.item(selection[0], 'text').split(' ', 1)[1]
        path = self.current_path / name
        
        try:
            stat = path.stat()
            size = self.format_size(stat.st_size) if path.is_file() else "-"
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            msg = f"Name: {name}\n"
            msg += f"Type: {'Directory' if path.is_dir() else 'File'}\n"
            msg += f"Size: {size}\n"
            msg += f"Modified: {mtime}\n"
            msg += f"Owner: {stat.st_uid}\n"
            msg += f"Permissions: {oct(stat.st_mode)[-3:]}"
            
            messagebox.showinfo("Properties", msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def run(self):
        """Run file manager"""
        self.root.mainloop()


if __name__ == '__main__':
    start_path = sys.argv[1] if len(sys.argv) > 1 else None
    fm = CarrotFileManager(start_path)
    fm.run()
