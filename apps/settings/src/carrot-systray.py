#!/usr/bin/env python3
"""
CarrotOS System Monitor
CPU, RAM, and process monitoring
"""

import sys
import os
import psutil
import time

class SystemMonitor:
    """System resource monitor"""
    
    def __init__(self):
        pass
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def get_memory_info(self) -> tuple:
        """Get memory usage"""
        try:
            mem = psutil.virtual_memory()
            return mem.percent, mem.used // (1024*1024), mem.total // (1024*1024)
        except:
            return 0.0, 0, 0
    
    def get_processes(self, limit: int = 10):
        """Get top processes by memory usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by memory usage
            processes.sort(key=lambda p: p.info['memory_percent'], reverse=True)
            return processes[:limit]
        except:
            return []
    
    def show_header(self):
        """Display header"""
        print("\n╔═══════════════════════════════════════╗")
        print("║  CarrotOS System Monitor v1.0.0     ║")
        print("╚═══════════════════════════════════════╝\n")
    
    def show_dashboard(self):
        """Display system dashboard"""
        self.show_header()
        
        # CPU
        cpu = self.get_cpu_usage()
        cpu_bar = "█" * int(cpu / 5) + "░" * (20 - int(cpu / 5))
        print(f"CPU Usage: [{cpu_bar}] {cpu:.1f}%")
        
        # Memory
        mem_percent, mem_used, mem_total = self.get_memory_info()
        mem_bar = "█" * int(mem_percent / 5) + "░" * (20 - int(mem_percent / 5))
        print(f"Memory:    [{mem_bar}] {mem_percent:.1f}% ({mem_used}MB / {mem_total}MB)")
        
        # Disk
        try:
            disk = psutil.disk_usage('/')
            disk_bar = "█" * int(disk.percent / 5) + "░" * (20 - int(disk.percent / 5))
            print(f"Disk:      [{disk_bar}] {disk.percent:.1f}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")
        except:
            print("Disk:      [error reading disk info]")
        
        # Top processes
        print("\nTop Processes:")
        print("  PID    Name                      Memory %")
        print("  " + "─" * 50)
        
        for proc in self.get_processes(5):
            try:
                name = proc.info['name'][:25]
                print(f"  {proc.info['pid']:<5} {name:<25} {proc.info['memory_percent']:>6.1f}%")
            except:
                pass
        
        print()
    
    def run_interactive(self, refresh_rate: float = 2.0):
        """Run interactive monitor"""
        try:
            while True:
                self.show_dashboard()
                time.sleep(refresh_rate)
        except KeyboardInterrupt:
            print("\n[monitor] Exit")


def main():
    monitor = SystemMonitor()
    monitor.run_interactive()
    return 0


if __name__ == "__main__":
    sys.exit(main())
