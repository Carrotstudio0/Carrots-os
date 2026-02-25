# System Architecture

## Kernel Choice
CarrotOS standardizes on Linux LTS for hardware breadth, mature live-boot support, and long-term maintenance.

## Runtime Model
- Lower root: signed `squashfs` image.
- Upper layer: writable overlay from persistence partition or volatile `tmpfs`.
- Unified root: `overlayfs` mounted in initramfs before switch_root.

## Core Planes
- Boot Plane: firmware -> GRUB2 -> kernel/initramfs.
- Kernel Plane: storage/input/network/display and fs capabilities.
- Core Plane: service manager, IPC, policy, logging, session control.
- UX Plane: Wayland compositor + Carrot shell + system apps.
- Security Plane: signing, MAC, firewall baseline, sandbox boundaries.

## Extensibility
The system uses manifests for overlays, services, and package channels to enable edition and OEM customization.
