#!/usr/bin/env python3
"""
CarrotOS Text Editor
Modern lightweight text editor with syntax highlighting
"""

import os
import sys
import re
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, font
except ImportError:
    print("Error: tkinter required")
    sys.exit(1)

class CarrotTextEditor:
    """Modern Text Editor"""
    
    def __init__(self, filepath=None):
        self.root = tk.Tk()
        self.root.title("Carrot Editor")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a23')
        
        self.filepath = filepath
        self.modified = False
        self.undo_stack = []
        self.redo_stack = []
        
        # Syntax highlighting patterns
        self.keywords = {
            'python': ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 
                      'import', 'from', 'return', 'True', 'False', 'None'],
            'c': ['int', 'char', 'void', 'if', 'else', 'for', 'while', 
                  'struct', 'typedef', 'return'],
            'bash': ['if', 'then', 'else', 'fi', 'for', 'do', 'done', 
                    'function', 'export'],
        }
        
        self.setup_ui()
        if filepath and Path(filepath).exists():
            self.open_file(filepath)
    
    def setup_ui(self):
        """Setup editor interface"""
        # Menu bar
        menubar = tk.Menu(self.root, bg='#2a2a35', fg='#cccccc')
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a35', fg='#cccccc')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file_dialog, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a35', fg='#cccccc')
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        
        # Toolbar
        toolbar = tk.Frame(self.root, bg='#2a2a35', height=40)
        toolbar.pack(fill=tk.X, padx=0, pady=0)
        
        self.file_label = tk.Label(toolbar, text="New file", 
                                  font=("Ubuntu", 10), bg='#2a2a35', fg='#ff9500')
        self.file_label.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Line counter and status
        self.status_bar = tk.Label(self.root, text="Line 1, Col 1 | UTF-8 | LF",
                                  bg='#2a2a35', fg='#888888', anchor=tk.E, padx=10)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # Main editor frame
        editor_frame = tk.Frame(self.root, bg='#1a1a23')
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Line numbers
        self.line_numbers = tk.Text(editor_frame, width=4, bg='#2a2a35', 
                                   fg='#666666', font=("Monospace", 12),
                                   relief=tk.FLAT, state=tk.DISABLED)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Text editor
        self.text = tk.Text(editor_frame, font=("Monospace", 12),
                           bg='#1a1a23', fg='#e0e0e0', 
                           insertbackground='#ff9500',
                           relief=tk.FLAT, undo=True, maxundo=-1,
                           wrap=tk.WORD)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tags for syntax highlighting
        self.text.tag_config('keyword', foreground='#ff9500', font=("Monospace", 12, "bold"))
        self.text.tag_config('string', foreground='#61bd00')
        self.text.tag_config('comment', foreground='#666666', font=("Monospace", 12, "italic"))
        self.text.tag_config('number', foreground='#00bfff')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(editor_frame, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)
        
        # Bind events
        self.text.bind('<KeyRelease>', self.on_text_change)
        self.text.bind('<Control-n>', lambda e: self.new_file())
        self.text.bind('<Control-o>', lambda e: self.open_file_dialog())
        self.text.bind('<Control-s>', lambda e: self.save_file())
        self.text.bind('<Control-z>', lambda e: self.undo())
        self.text.bind('<Control-y>', lambda e: self.redo())
        
        self.update_line_numbers()
    
    def on_text_change(self, event=None):
        """Handle text changes"""
        self.modified = True
        self.update_line_numbers()
        self.highlight_syntax()
        self.update_status()
    
    def update_line_numbers(self):
        """Update line number display"""
        lines = self.text.get(1.0, 'end-1c').split('\n')
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete(1.0, tk.END)
        
        for i, _ in enumerate(lines, 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        
        self.line_numbers.config(state=tk.DISABLED)
    
    def highlight_syntax(self):
        """Apply syntax highlighting"""
        # Remove all tags
        self.text.tag_remove('keyword', 1.0, tk.END)
        self.text.tag_remove('string', 1.0, tk.END)
        self.text.tag_remove('comment', 1.0, tk.END)
        self.text.tag_remove('number', 1.0, tk.END)
        
        text_content = self.text.get(1.0, tk.END)
        
        # Highlight strings
        for match in re.finditer(r'["\'].*?["\']', text_content):
            start = self.text.index(f"1.0 + {match.start()} chars")
            end = self.text.index(f"1.0 + {match.end()} chars")
            self.text.tag_add('string', start, end)
        
        # Highlight comments
        for match in re.finditer(r'#.*?(?=\n|$)', text_content):
            start = self.text.index(f"1.0 + {match.start()} chars")
            end = self.text.index(f"1.0 + {match.end()} chars")
            self.text.tag_add('comment', start, end)
        
        # Highlight keywords
        for keyword in self.keywords.get('python', []):
            for match in re.finditer(r'\b' + keyword + r'\b', text_content):
                start = self.text.index(f"1.0 + {match.start()} chars")
                end = self.text.index(f"1.0 + {match.end()} chars")
                self.text.tag_add('keyword', start, end)
        
        # Highlight numbers
        for match in re.finditer(r'\b\d+\b', text_content):
            start = self.text.index(f"1.0 + {match.start()} chars")
            end = self.text.index(f"1.0 + {match.end()} chars")
            self.text.tag_add('number', start, end)
    
    def update_status(self):
        """Update status bar"""
        line, col = self.text.index(tk.INSERT).split('.')
        char_count = len(self.text.get(1.0, tk.END)) - 1
        self.status_bar.config(text=f"Line {line}, Col {col} | {char_count} chars | UTF-8 | LF")
    
    def new_file(self):
        """Create new file"""
        if self.modified:
            if messagebox.askyesno("Unsaved Changes", "Save before creating new file?"):
                self.save_file()
        
        self.text.delete(1.0, tk.END)
        self.filepath = None
        self.modified = False
        self.file_label.config(text="New file")
        self.update_line_numbers()
    
    def open_file_dialog(self):
        """Open file dialog"""
        path = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*"), ("Python", "*.py"), 
                      ("C", "*.c"), ("Bash", "*.sh"), ("Text", "*.txt")]
        )
        if path:
            self.open_file(path)
    
    def open_file(self, filepath):
        """Open file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.text.delete(1.0, tk.END)
            self.text.insert(1.0, content)
            self.filepath = filepath
            self.modified = False
            self.file_label.config(text=f"📄 {Path(filepath).name}")
            self.update_line_numbers()
            self.highlight_syntax()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")
    
    def save_file(self):
        """Save file"""
        if not self.filepath:
            self.save_as_dialog()
            return
        
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(self.text.get(1.0, tk.END[0:-1]))
            
            self.modified = False
            self.file_label.config(text=f"📄 {Path(self.filepath).name}")
            messagebox.showinfo("Success", "File saved")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot save file: {e}")
    
    def save_as_dialog(self):
        """Save as dialog"""
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"), ("Python", "*.py"), 
                      ("C", "*.c"), ("Bash", "*.sh"), ("Text", "*.txt")]
        )
        if path:
            self.filepath = path
            self.save_file()
    
    def cut(self):
        """Cut text"""
        self.root.event_generate("<<Cut>>")
    
    def copy(self):
        """Copy text"""
        self.root.event_generate("<<Copy>>")
    
    def paste(self):
        """Paste text"""
        self.root.event_generate("<<Paste>>")
    
    def undo(self):
        """Undo"""
        try:
            self.text.edit_undo()
        except:
            pass
    
    def redo(self):
        """Redo"""
        try:
            self.text.edit_redo()
        except:
            pass
    
    def run(self):
        """Run editor"""
        self.root.mainloop()


if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    editor = CarrotTextEditor(filepath)
    editor.run()
