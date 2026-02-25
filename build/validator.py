#!/usr/bin/env python3
"""
CarrotOS Build Configuration & Validation
Ensures all components are properly linked and dependencies are available
"""

import sys
from pathlib import Path
import json

class BuildValidator:
    """Validate CarrotOS build configuration"""
    
    REQUIRED_MODULES = {
        "tools": [
            "update_manager.py",
            "driver_manager.py",
            "power_manager.py",
            "theme_engine.py",
            "build.py"
        ],
        "apps/control-center": [
            "carrot-control-center.py"
        ],
        "apps/driver-manager": [
            "carrot-driver-gui.py"
        ]
    }
    
    OPTIONAL_MODULES = {
        "tools": [
            "rootfs_builder.py",
            "iso_builder.py"
        ]
    }
    
    def __init__(self, root_dir: Path):
        self.root = Path(root_dir)
        self.issues = []
        self.warnings = []
        self.success_count = 0
    
    def validate_all(self) -> bool:
        """Run all validations"""
        print("🔍 Validating CarrotOS Build Configuration\n")
        print("=" * 60)
        
        self.validate_required_files()
        self.validate_imports()
        self.validate_permissions()
        self.print_report()
        
        return len(self.issues) == 0
    
    def validate_required_files(self):
        """Check that all required files exist"""
        print("\n📁 Checking Required Files...")
        
        for subdir, files in self.REQUIRED_MODULES.items():
            dir_path = self.root / subdir
            
            if not dir_path.exists():
                self.issues.append(f"❌ Missing directory: {subdir}")
                continue
            
            for filename in files:
                file_path = dir_path / filename
                if file_path.exists():
                    self.success_count += 1
                    print(f"  ✓ {subdir}/{filename}")
                else:
                    self.issues.append(f"❌ Missing file: {subdir}/{filename}")
    
    def validate_imports(self):
        """Check Python imports work correctly"""
        print("\n🔗 Checking Python Imports...")
        
        # Add tools to path
        sys.path.insert(0, str(self.root / "tools"))
        
        test_imports = {
            "update_manager": ["UpdateManager"],
            "driver_manager": ["DriverManager", "DriverType", "DriverStatus"],
            "power_manager": ["PowerManager", "PowerProfile"],
            "theme_engine": ["ThemeManager", "Theme", "ColorScheme"]
        }
        
        for module_name, items in test_imports.items():
            try:
                module = __import__(module_name)
                
                for item in items:
                    if hasattr(module, item):
                        self.success_count += 1
                        print(f"  ✓ {module_name}.{item}")
                    else:
                        self.warnings.append(
                            f"⚠️  Missing export: {module_name}.{item}"
                        )
            except ImportError as e:
                self.issues.append(f"❌ Cannot import {module_name}: {e}")
    
    def validate_permissions(self):
        """Check file permissions"""
        print("\n🔐 Checking File Permissions...")
        
        executable_files = {
            "tools/build.py",
            "apps/control-center/carrot-control-center.py",
            "apps/driver-manager/carrot-driver-gui.py"
        }
        
        for rel_path in executable_files:
            file_path = self.root / rel_path
            if file_path.exists():
                # Just check if readable
                try:
                    with open(file_path, 'r') as f:
                        f.read(1)
                    self.success_count += 1
                    print(f"  ✓ {rel_path} (readable)")
                except PermissionError:
                    self.warnings.append(f"⚠️  {rel_path} (permission denied)")
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "=" * 60)
        print("\n📊 BUILD VALIDATION REPORT\n")
        
        if self.success_count > 0:
            print(f"✅ Checks Passed: {self.success_count}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings: {len(self.warnings)}")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.issues:
            print(f"\n❌ Critical Issues: {len(self.issues)}")
            for msg in self.issues:
                print(f"  {msg}")
        else:
            print("\n✅ All validations passed!")
        
        print("\n" + "=" * 60)
    
    def generate_report_json(self, output_file: Path):
        """Generate JSON report"""
        report = {
            "status": "valid" if not self.issues else "invalid",
            "timestamp": str(Path.cwd()),
            "checks": {
                "successful": self.success_count,
                "warnings": len(self.warnings),
                "issues": len(self.issues)
            },
            "warnings": self.warnings,
            "issues": self.issues
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

class DependencyChecker:
    """Check system dependencies for building"""
    
    REQUIRED_COMMANDS = [
        "python3",
        "gcc",
        "make",
        "git"
    ]
    
    OPTIONAL_COMMANDS = [
        "xorriso",
        "parted",
        "docker",
        "qemu-img"
    ]
    
    @staticmethod
    def check_all():
        """Check all dependencies"""
        import subprocess
        
        print("\n🔧 Checking System Dependencies\n")
        print("=" * 60)
        
        print("\n📦 Required Commands:")
        for cmd in DependencyChecker.REQUIRED_COMMANDS:
            result = subprocess.run(
                ["which", cmd],
                capture_output=True
            )
            if result.returncode == 0:
                print(f"  ✓ {cmd}")
            else:
                print(f"  ❌ {cmd} (NOT FOUND)")
        
        print("\n📦 Optional Commands:")
        for cmd in DependencyChecker.OPTIONAL_COMMANDS:
            result = subprocess.run(
                ["which", cmd],
                capture_output=True
            )
            if result.returncode == 0:
                print(f"  ✓ {cmd}")
            else:
                print(f"  ⚠️  {cmd}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    # Determine CarrotOS root directory
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent if script_dir.name == "tools" else script_dir
    
    # Run validation
    validator = BuildValidator(root_dir)
    is_valid = validator.validate_all()
    
    # Check dependencies
    DependencyChecker.check_all()
    
    # Generate report
    report_file = root_dir / "build_validation.json"
    validator.generate_report_json(report_file)
    print(f"\n💾 Report saved: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)
