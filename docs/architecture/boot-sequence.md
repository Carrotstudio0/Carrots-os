# Boot Sequence

1. BIOS or UEFI firmware loads GRUB2 from USB media.
2. GRUB2 reads menu entries and selected policy profile.
3. Kernel and initramfs are loaded with explicit boot parameters.
4. Kernel initializes required built-in drivers for USB/storage/filesystem.
5. Initramfs starts `carrot-init` responsibilities.
6. Base root image (`squashfs`) is mounted read-only.
7. Overlay stack is resolved in priority order.
8. `overlayfs` unified root is mounted.
9. `switch_root` transitions into the unified system root.
10. Core services start, then display manager and user session.
11. Wayland compositor launches Carrot shell.
