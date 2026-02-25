# CarrotOS

CarrotOS is a USB-bootable, modern desktop operating system architecture built on a Linux LTS kernel.
The repository is structured for native Windows development only (no WSL, no containers, no virtual machines).

## Design Principles
- Immutable base root filesystem (`squashfs`) with controlled mutability (`overlayfs`).
- Secure boot chain with signed artifacts.
- Clear separation of boot, kernel, core services, desktop shell, overlays, and release assets.
- Long-term extensibility for desktop, OEM, and custom editions.

## Repository Layout
- `boot/` bootloader assets and early boot config.
- `kernel/` kernel config and patch policy.
- `core/` PID1-adjacent service boundaries, session, IPC, logging.
- `desktop/` compositor integration and Carrot shell.
- `overlays/` layer model for edition/OEM/custom content.
- `rootfs/` base filesystem source layout.
- `build/` manifests and profile definitions.
- `iso/` final image layout contracts.
- `security/` security policies and key management boundaries.

## Current Status
Initial architecture scaffold and baseline manifests are created.
No build scripts are implemented yet.
