# ISO Layout Contract

The ISO assembly process writes assets into this layout:
- /boot/vmlinuz
- /boot/initramfs.img
- /boot/grub/grub.cfg
- /EFI/BOOT/*.EFI
- /carrot/rootfs/base.squashfs
- /carrot/overlays/*.sqfs
- /carrot/manifests/*.yaml
