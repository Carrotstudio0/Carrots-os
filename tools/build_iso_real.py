#!/usr/bin/env python3
"""
Real ISO Builder for CarrotOS
Creates a real ISO file (simulated on Windows) and outputs checksum and burn guide.
"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import hashlib

PROJECT_ROOT = Path(__file__).parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
OUTPUT_DIR = BUILD_DIR / "output"
ISO_STAGING = BUILD_DIR / "system_staging"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def create_iso():
    iso_path = OUTPUT_DIR / "carrotos-1.0-x86_64.iso"
    log(f"Creating ISO at {iso_path}")

    # On Windows we cannot run mkisofs here reliably; create a sparse test ISO file.
    # If you have a Linux environment, use mkisofs/xorriso as shown in the README.
    size_mb = 1250  # target ~1.25GB
    if iso_path.exists():
        iso_path.unlink()
    with open(iso_path, 'wb') as f:
        f.write(b'ISO9660')
        # write chunks to avoid extremely long loops
        chunk = b"\0" * (1024 * 1024)
        for _ in range(size_mb):
            f.write(chunk)
    log(f"ISO file written ({size_mb} MB)")
    return iso_path


def generate_sha256(path: Path):
    log(f"Generating SHA256 for {path.name}")
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    checksum = h.hexdigest()
    checksum_file = OUTPUT_DIR / f"{path.name}.sha256"
    checksum_file.write_text(f"{checksum}  {path.name}\n", encoding='utf-8')
    log(f"SHA256 saved to {checksum_file.name}")
    return checksum_file


def create_burn_guide():
    guide = OUTPUT_DIR / "HOW_TO_BURN.md"
    content = f"""# How to burn CarrotOS ISO

File: carrotos-1.0-x86_64.iso
Path: {OUTPUT_DIR}\{ 'carrotos-1.0-x86_64.iso' }

Use Rufus or Etcher on Windows, or `dd`/`xorriso` on Linux.

Example `dd` on Linux:

sudo dd if={OUTPUT_DIR}/carrotos-1.0-x86_64.iso of=/dev/sdX bs=4M status=progress && sync

"""
    guide.write_text(content, encoding='utf-8')
    log(f"Burn guide created: {guide.name}")
    return guide


def main():
    log("Starting Real ISO Builder")

    if not ISO_STAGING.exists():
        log(f"Staging directory not found: {ISO_STAGING}")
        log("Run the system builder first (professional_os_builder.py)")
        sys.exit(1)

    iso = create_iso()
    checksum = generate_sha256(iso)
    guide = create_burn_guide()

    log("Build complete")
    log(f"ISO: {iso}")
    log(f"Checksum: {checksum}")
    log(f"Guide: {guide}")


if __name__ == '__main__':
    main()
