# How to burn CarrotOS ISO

File: carrotos-1.0-x86_64.iso
Path: C:\Users\Tech Shop\Desktop\sys\CarrotOS\build\output\carrotos-1.0-x86_64.iso

Use Rufus or Etcher on Windows, or `dd`/`xorriso` on Linux.

Example `dd` on Linux:

sudo dd if=C:\Users\Tech Shop\Desktop\sys\CarrotOS\build\output/carrotos-1.0-x86_64.iso of=/dev/sdX bs=4M status=progress && sync

