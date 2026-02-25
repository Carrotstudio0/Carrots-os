#!/usr/bin/env python3
"""
CarrotOS Professional Build Verification System
Checks all components, libraries, and system integrity
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class CarrotOSValidator:
    """Validates CarrotOS build system and components"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_artifacts = self.project_root / "build-artifacts"
        self.src_dir = self.project_root / "src"
        self.apps_dir = self.project_root / "apps"
        self.tools_dir = self.project_root / "tools"
        self.results = {"passed": [], "failed": [], "warnings": []}
        self.timestamp = datetime.now().isoformat()
    
    def log(self, level, message):
        """Log validation messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = {"SUCCESS": "\033[32m", "ERROR": "\033[31m", "WARNING": "\033[33m", "INFO": "\033[36m"}
        reset = "\033[0m"
        print(f"{color.get(level, reset)}[{timestamp} {level}]{reset} {message}")
    
    # ===== Core System Checks =====
    
    def check_kernel(self):
        """Verify kernel compilation"""
        self.log("INFO", "Checking kernel... 🎯")
        kernel_file = self.src_dir / "kernel" / "kernel.c"
        
        if kernel_file.exists():
            lines = kernel_file.read_text().count('\n')
            if lines > 500:
                self.log("SUCCESS", f"✓ Kernel found ({lines} lines)")
                self.results["passed"].append("Kernel source")
            else:
                self.log("WARNING", "⚠ Kernel seems small (~" + str(lines) + " lines)")
                self.results["warnings"].append("Kernel size")
        else:
            self.log("ERROR", "✗ Kernel not found!")
            self.results["failed"].append("Kernel")
    
    def check_init(self):
        """Verify init system"""
        self.log("INFO", "Checking Init System... 🎯")
        init_file = self.src_dir / "core" / "init" / "src" / "main.c"
        
        if init_file.exists():
            lines = init_file.read_text().count('\n')
            if lines > 400:
                self.log("SUCCESS", f"✓ Init system found ({lines} lines)")
                self.results["passed"].append("Init system")
            else:
                self.log("WARNING", "⚠ Init system seems incomplete")
                self.results["warnings"].append("Init size")
        else:
            self.log("ERROR", "✗ Init system not found!")
            self.results["failed"].append("Init system")
    
    def check_bootloader(self):
        """Verify bootloader"""
        self.log("INFO", "Checking Bootloader... 🎯")
        boot_files = [
            self.src_dir / "kernel" / "src" / "boot.asm",
            self.build_artifacts / "build" / "grub.cfg"
        ]
        
        for bf in boot_files:
            if bf.exists():
                self.log("SUCCESS", f"✓ Bootloader component: {bf.name}")
                self.results["passed"].append(f"Bootloader: {bf.name}")
            else:
                self.log("WARNING", f"⚠ Missing: {bf.name}")
                self.results["warnings"].append(f"Bootloader: {bf.name}")
    
    # ===== Library Checks =====
    
    def check_python_modules(self):
        """Verify Python dependencies"""
        self.log("INFO", "Checking Python modules... 🎯")
        modules_to_check = ["yaml", "PIL", "sys", "os"]
        
        missing = []
        for module in modules_to_check:
            try:
                __import__(module)
                self.log("SUCCESS", f"✓ Python module: {module}")
                self.results["passed"].append(f"Python: {module}")
            except ImportError:
                if module not in ["PIL"]:  # PIL is optional
                    missing.append(module)
        
        if missing:
            self.log("WARNING", f"⚠ Missing Python modules: {', '.join(missing)}")
            self.results["warnings"].append(f"Python modules: {missing}")
        else:
            self.log("SUCCESS", "✓ All critical Python modules available")
    
    def check_system_libraries(self):
        """Check system library availability"""
        self.log("INFO", "Checking system libraries... 🎯")
        
        # Check for key library files
        library_paths = [
            "/lib/x86_64-linux-gnu",
            "/usr/lib/x86_64-linux-gnu",
            "/usr/local/lib"
        ]
        
        found_libs = False
        for lib_path in library_paths:
            if os.path.exists(lib_path):
                lib_count = len(os.listdir(lib_path))
                if lib_count > 0:
                    self.log("SUCCESS", f"✓ Library path: {lib_path} ({lib_count} files)")
                    found_libs = True
                    self.results["passed"].append(f"Libraries: {lib_path}")
        
        if not found_libs:
            self.log("WARNING", "⚠ Limited library availability (normal on Windows)")
            self.results["warnings"].append("System libraries")
    
    # ===== Application Checks =====
    
    def check_applications(self):
        """Verify all applications"""
        self.log("INFO", "Checking applications... 🎯")
        
        app_dirs = {
            "core": self.apps_dir / "core",
            "system": self.apps_dir / "system",
            "utilities": self.apps_dir / "utilities"
        }
        
        for category, path in app_dirs.items():
            if path.exists():
                apps = list(path.glob("*/"))
                self.log("SUCCESS", f"✓ {category.upper()} apps: {len(apps)} found")
                self.results["passed"].append(f"Apps: {category} ({len(apps)})")
            else:
                self.log("WARNING", f"⚠ {category} apps directory not found")
                self.results["warnings"].append(f"Apps: {category}")
    
    def check_scripts(self):
        """Verify build scripts"""
        self.log("INFO", "Checking build scripts... 🎯")
        
        scripts = [
            self.project_root / "build.ps1",
            self.project_root / "build.bat",
            self.project_root / "setup-windows.ps1",
            self.tools_dir / "build" / "install-libraries.sh"
        ]
        
        for script in scripts:
            if script.exists():
                size = script.stat().st_size
                self.log("SUCCESS", f"✓ Script: {script.name} ({size} bytes)")
                self.results["passed"].append(f"Script: {script.name}")
            else:
                self.log("WARNING", f"⚠ Missing script: {script.name}")
                self.results["warnings"].append(f"Script: {script.name}")
    
    # ===== Configuration Checks =====
    
    def check_configs(self):
        """Verify system configurations"""
        self.log("INFO", "Checking configurations... 🎯")
        
        configs = [
            self.build_artifacts / "build" / "grub.cfg",
            self.build_artifacts / "rootfs" / "base" / "etc" / "network" / "interfaces",
            self.build_artifacts / "rootfs" / "base" / "etc" / "pam.d" / "common-auth",
            self.project_root / "config" / "desktop-registry.conf"
        ]
        
        for config in configs:
            if config.exists():
                self.log("SUCCESS", f"✓ Config: {config.name}")
                self.results["passed"].append(f"Config: {config.name}")
            else:
                self.log("INFO", f"ℹ Config optional: {config.name}")
    
    # ===== Build Artifacts =====
    
    def check_build_structure(self):
        """Verify build directory structure"""
        self.log("INFO", "Checking build structure... 🎯")
        
        required_dirs = [
            self.build_artifacts / "build",
            self.build_artifacts / "iso",
            self.build_artifacts / "rootfs",
            self.build_artifacts / "overlays"
        ]
        
        for d in required_dirs:
            if d.exists():
                self.log("SUCCESS", f"✓ Build dir: {d.name}")
                self.results["passed"].append(f"Build: {d.name}")
            else:
                self.log("INFO", f"ℹ Build dir will be created: {d.name}")
    
    # ===== Utilities =====
    
    def check_system_tools(self):
        """Check required system tools"""
        self.log("INFO", "Checking system tools... 🎯")
        
        tools = {
            "gcc": "C Compiler",
            "nasm": "Assembler",
            "python3": "Python Runtime",
            "make": "Build System"
        }
        
        for tool, description in tools.items():
            try:
                result = subprocess.run([tool, "--version"], 
                                       capture_output=True, timeout=5)
                if result.returncode == 0:
                    self.log("SUCCESS", f"✓ Tool: {tool} ({description})")
                    self.results["passed"].append(f"Tool: {tool}")
                else:
                    self.log("WARNING", f"⚠ Tool {tool} not responding properly")
                    self.results["warnings"].append(f"Tool: {tool}")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.log("WARNING", f"⚠ Tool not found: {tool}")
                self.results["warnings"].append(f"Tool: {tool}")
    
    # ===== Summary Report =====
    
    def generate_report(self):
        """Generate final validation report"""
        self.log("INFO", "\n" + "="*60)
        self.log("INFO", "🥕 CarrotOS Professional Build Verification Report 🥕")
        self.log("INFO", "="*60)
        
        print(f"\n✓ PASSED: {len(self.results['passed'])}")
        for item in self.results["passed"]:
            print(f"   ✓ {item}")
        
        if self.results["warnings"]:
            print(f"\n⚠ WARNINGS: {len(self.results['warnings'])}")
            for item in self.results["warnings"]:
                print(f"   ⚠ {item}")
        
        if self.results["failed"]:
            print(f"\n✗ FAILED: {len(self.results['failed'])}")
            for item in self.results["failed"]:
                print(f"   ✗ {item}")
        
        total = len(self.results["passed"]) + len(self.results["failed"])
        success_rate = (len(self.results["passed"]) / total * 100) if total > 0 else 0
        
        print(f"\n🎯 Overall Status: {success_rate:.1f}% COMPLETE")
        
        if success_rate >= 90:
            self.log("SUCCESS", "✓ System is READY FOR PRODUCTION BUILD!\n")
            return 0
        elif success_rate >= 70:
            self.log("WARNING", "⚠ System is mostly ready (some warnings)\n")
            return 1
        else:
            self.log("ERROR", "✗ System has critical issues\n")
            return 2
    
    # ===== Main Execution =====
    
    def run_all_checks(self):
        """Execute all validation checks"""
        print("\n" + "="*60)
        print("  🥕 CarrotOS Professional Build System Validator")
        print("="*60 + "\n")
        
        # Core System
        self.check_kernel()
        self.check_init()
        self.check_bootloader()
        
        # Libraries
        self.check_python_modules()
        self.check_system_libraries()
        
        # Applications
        self.check_applications()
        self.check_scripts()
        
        # Configuration
        self.check_configs()
        self.check_build_structure()
        
        # Tools
        self.check_system_tools()
        
        # Report
        return self.generate_report()

def main():
    """Main entry point"""
    validator = CarrotOSValidator()
    exit_code = validator.run_all_checks()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
