#!/usr/bin/env python3
"""
CarrotOS Terminal Emulator
Lightweight terminal application
"""

import sys
import os
import subprocess
import readline

class TerminalEmulator:
    """Simple terminal emulator"""
    
    def __init__(self):
        self.shell = os.environ.get("SHELL", "/bin/bash")
        self.prompt = f"{os.environ.get('USER', 'user')}@{os.environ.get('HOSTNAME', 'carrotos')}$ "
    
    def run(self):
        """Run terminal"""
        print("\n╔═══════════════════════════════════════╗")
        print("║  CarrotOS Terminal Emulator v1.0.0   ║")
        print("╚═══════════════════════════════════════╝\n")
        
        try:
            subprocess.call([self.shell, "-i"])
        except KeyboardInterrupt:
            print("\n[terminal] Exit")


def main():
    term = TerminalEmulator()
    term.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
