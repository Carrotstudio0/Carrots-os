#!/usr/bin/env python3
"""
CarrotOS File Manager
Lightweight file browser
"""

import sys
import os
from pathlib import Path

class FileManager:
    """Simple file manager"""
    
    def __init__(self, start_path: str = "."):
        self.current_dir = Path(start_path).resolve()
    
    def list_directory(self):
        """List current directory"""
        print(f"\n📁 {self.current_dir}\n")
        print("Name                     Type      Size")
        print("─" * 60)
        
        try:
            for item in sorted(self.current_dir.iterdir()):
                if item.is_dir():
                    print(f"{item.name:<24} [FOLDER]  -")
                else:
                    size_kb = item.stat().st_size // 1024
                    print(f"{item.name:<24} [FILE]    {size_kb} KB")
        except PermissionError:
            print("[ERROR] Permission denied")
    
    def run_interactive(self):
        """Interactive file browser"""
        print("\n╔═══════════════════════════════════════╗")
        print("║  CarrotOS File Manager v1.0.0       ║")
        print("╚═══════════════════════════════════════╝")
        
        while True:
            self.list_directory()
            
            cmd = input("\nCommand (cd/ls/quit): ").strip().split()
            
            if not cmd:
                continue
            
            if cmd[0] == "quit":
                break
            elif cmd[0] == "cd" and len(cmd) > 1:
                try:
                    new_path = self.current_dir / cmd[1]
                    if new_path.is_dir():
                        self.current_dir = new_path
                    else:
                        print("[ERROR] Not a directory")
                except Exception as e:
                    print(f"[ERROR] {e}")
            elif cmd[0] == "ls":
                pass  # Just list again


def main():
    start_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~")
    manager = FileManager(start_path)
    manager.run_interactive()
    return 0


if __name__ == "__main__":
    sys.exit(main())
