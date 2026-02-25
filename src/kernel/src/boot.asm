;;; CarrotOS Bootloader - 64-bit UEFI/BIOS Multi-boot
;;; Compatible with NASM on Windows
;;; Builds a simple kernel entry point

[BITS 64]
[ORG 0x100000]

; Multiboot Header (for GRUB/compatibility)
align 8
multiboot_header:
    dd 0x1BADB002          ; Magic number
    dd 0x00000003          ; Flags
    dd -(0x1BADB002 + 3)   ; Checksum
    dd multiboot_header    ; Header address
    dd 0x100000            ; Load address
    dd 0                   ; Load end address
    dd 0                   ; BSS end address
    dd kernel_entry        ; Entry point

; Stack and memory
section .bss
align 4096
boot_stack:
    resb 4096
boot_stack_top:

kernel_space:
    resb 65536

; Kernel entry point
section .text
global kernel_entry

kernel_entry:
    ; Set up stack
    mov rsp, boot_stack_top
    
    ; Clear registers
    xor eax, eax
    xor ebx, ebx
    xor ecx, ecx
    xor edx, edx
    
    ; Call main kernel function
    call kernel_main
    
    ; Halt on return
    cli
.halt:
    hlt
    jmp .halt

; Simple kernel main (called from C)
extern kernel_main

; Data segment
section .data
    boot_message db "CarrotOS Kernel Loading...", 0x0A, 0

; Exports
global _start
_start:
    jmp kernel_entry
