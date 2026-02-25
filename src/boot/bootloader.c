/*
 * CarrotOS Bootloader
 * Entry point for x86-64 systems
 * 
 * This file contains the primary bootloader that handles:
 * - UEFI/BIOS compatibility
 * - Memory initialization
 * - Processor setup
 * - Handoff to kernel
 * 
 * NOTE: This is cross-compilation code for Linux/x86-64 kernel.
 * Include errors in IDE are normal on Windows - configure cross-compiler.
 */

#ifndef __BOOTLOADER_H__
#define __BOOTLOADER_H__

#include <stdint.h>
#include <stddef.h>

/* Multiboot2 header for GRUB compatibility */
#define MULTIBOOT2_HEADER_MAGIC          0xe85250d6
#define MULTIBOOT2_ARCHITECTURE_I386     0
#define MULTIBOOT2_HEADER_TAG_END        0

typedef struct {
    uint32_t magic;
    uint32_t architecture;
    uint32_t header_length;
    uint32_t checksum;
} multiboot2_header_t;

/* Bootloader info structure */
typedef struct {
    uint32_t flags;
    uint32_t mem_lower;
    uint32_t mem_upper;
    uint32_t boot_device;
    char *cmdline;
    uint32_t mods_count;
    void *mods_addr;
} boot_info_t;

/* Memory map entry */
typedef struct {
    uint64_t base;
    uint64_t length;
    uint32_t type;
    uint32_t reserved;
} memory_map_entry_t;

void bootloader_init(void);
void setup_gdt(void);
void setup_idt(void);
void enable_paging(void);

/* Page table entry structures */
#define PAGE_SIZE                       4096
#define PAGE_PRESENT                    (1 << 0)
#define PAGE_WRITE                      (1 << 1)
#define PAGE_USER                       (1 << 2)

typedef uint64_t page_table_entry_t;

/* GDT Segment descriptor */
typedef struct {
    uint16_t limit_low;
    uint16_t base_low;
    uint8_t base_mid;
    uint8_t access;
    uint8_t limit_high;
    uint8_t base_high;
} __attribute__((packed)) gdt_entry_t;

/* IDT Gate descriptor */
typedef struct {
    uint16_t base_low;
    uint16_t selector;
    uint8_t reserved;
    uint8_t type;
    uint16_t base_high;
} __attribute__((packed)) idt_entry_t;

#endif /* __BOOTLOADER_H__ */

/* Implementation section */

/**
 * bootloader_entry - Multiboot2 entry point
 * This is called by GRUB with multiboot2 header
 */
void bootloader_entry(uint32_t magic, multiboot2_header_t *mbi) {
    if (magic != 0x36d76289) {
        /* Not Multiboot2 bootloader */
        while(1);
    }
    
    bootloader_init();
}

/**
 * bootloader_init - Initialize the bootloader
 * Sets up GDT, IDT, enables paging, and hands off to kernel
 */
void bootloader_init(void) {
    /* Setup Global Descriptor Table */
    setup_gdt();
    
    /* Setup Interrupt Descriptor Table */
    setup_idt();
    
    /* Enable paging */
    enable_paging();
    
    /* Jump to kernel entry */
    /* kernel_main is linked at 0xFFFFFFFF80000000 */
}

/**
 * setup_gdt - Initialize Global Descriptor Table
 * Configures kernel code, kernel data, user code, user data segments
 */
void setup_gdt(void) {
    /* GDT setup would go here */
    /* This is a stub - full implementation requires assembly */
}

/**
 * setup_idt - Initialize Interrupt Descriptor Table
 * Configures interrupt handlers for CPU exceptions
 */
void setup_idt(void) {
    /* IDT setup would go here */
    /* This is a stub - full implementation requires assembly */
}

/**
 * enable_paging - Enable 64-bit paging
 * Sets up page tables for kernel space mapping
 */
void enable_paging(void) {
    /* Paging setup would go here */
    /* This is a stub - full implementation requires assembly */
}
