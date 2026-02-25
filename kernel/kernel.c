/**
 * CarrotOS Kernel
 * Main kernel entry point and core functionality
 * 
 * (C) 2024 CarrotOS Project
 * GPL v3 License
 */

#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* Kernel version information */
#define KERNEL_VERSION_MAJOR    1
#define KERNEL_VERSION_MINOR    0
#define KERNEL_VERSION_PATCH    0

/* Memory management constants */
#define PAGE_SIZE               4096
#define KERNEL_HEAP_START       0xFFFFFFFF82000000
#define KERNEL_HEAP_SIZE        (16 * 1024 * 1024)  /* 16 MB */
#define KERNEL_STACK_SIZE       (2 * PAGE_SIZE)     /* 8 KB */

/* CPU feature flags */
typedef struct {
    uint32_t has_pae;           /* Physical Address Extension */
    uint32_t has_pse;           /* Page Size Extension */
    uint32_t has_rdmsr;         /* Read MSR */
    uint32_t has_wrmsr;         /* Write MSR */
    uint32_t has_apic;          /* APIC */
    uint32_t has_x2apic;        /* Extended APIC */
} cpu_features_t;

/* Memory region descriptor */
typedef struct {
    uint64_t base;
    uint64_t size;
    uint32_t type;              /* 1 = Available, 3 = ACPI reclaimable, etc */
} memory_region_t;

/* Kernel state */
typedef struct {
    uint32_t boot_magic;
    uint32_t kernel_version;
    cpu_features_t cpu;
    uint32_t num_memory_regions;
    memory_region_t *memory_map;
} kernel_state_t;

/* Global kernel state */
static kernel_state_t kernel_state = {0};

/* Memory allocator simple free list */
typedef struct free_block {
    struct free_block *next;
    size_t size;
} free_block_t;

static free_block_t *kernel_heap_free_list = NULL;
static uint8_t kernel_heap[KERNEL_HEAP_SIZE] = {0};

/* Forward declarations */
void kernel_panic(const char *message);
void *kmalloc(size_t size);
void kfree(void *ptr);
void detect_cpu_features(void);
void init_memory_allocator(void);
void init_interrupts(void);
void init_timer(void);
void init_scheduler(void);
void init_devices(void);
void start_init_process(void);

/**
 * kernel_main - Main kernel entry point
 * Called by bootloader with multiboot2 information
 */
void kernel_main(uint32_t magic, void *multiboot_data) {
    /* Store boot information */
    kernel_state.boot_magic = magic;
    kernel_state.kernel_version = (KERNEL_VERSION_MAJOR << 16) | 
                                   (KERNEL_VERSION_MINOR << 8) | 
                                   KERNEL_VERSION_PATCH;
    
    /* Initialize kernel subsystems in order */
    init_memory_allocator();
    detect_cpu_features();
    init_interrupts();
    init_timer();
    init_devices();
    init_scheduler();
    
    /* Start the init process (PID 1) */
    start_init_process();
    
    /* Kernel should never reach here */
    kernel_panic("Kernel returned from init");
}

/**
 * init_memory_allocator - Initialize kernel heap allocator
 */
void init_memory_allocator(void) {
    /* Initialize the free list with entire heap as one free block */
    kernel_heap_free_list = (free_block_t *)kernel_heap;
    kernel_heap_free_list->size = KERNEL_HEAP_SIZE - sizeof(free_block_t);
    kernel_heap_free_list->next = NULL;
}

/**
 * kmalloc - Allocate memory from kernel heap
 * Simple first-fit allocation strategy
 */
void *kmalloc(size_t size) {
    if (size == 0) return NULL;
    
    /* Add space for free block header */
    size += sizeof(free_block_t);
    
    free_block_t *current = kernel_heap_free_list;
    free_block_t *previous = NULL;
    
    /* Find first block that fits */
    while (current != NULL) {
        if (current->size >= size) {
            /* Block is large enough */
            free_block_t *allocated = current;
            
            if (current->size > size) {
                /* Split the block */
                free_block_t *remaining = (free_block_t *)((uint8_t *)current + size);
                remaining->size = current->size - size;
                remaining->next = current->next;
                
                if (previous == NULL) {
                    kernel_heap_free_list = remaining;
                } else {
                    previous->next = remaining;
                }
            } else {
                /* Use entire block */
                if (previous == NULL) {
                    kernel_heap_free_list = current->next;
                } else {
                    previous->next = current->next;
                }
            }
            
            return (void *)allocated;
        }
        
        previous = current;
        current = current->next;
    }
    
    /* No suitable block found */
    return NULL;
}

/**
 * kfree - Free memory back to kernel heap
 * Simple free that adds block back to free list
 */
void kfree(void *ptr) {
    if (ptr == NULL) return;
    
    free_block_t *block = (free_block_t *)ptr;
    block->next = kernel_heap_free_list;
    kernel_heap_free_list = block;
}

/**
 * detect_cpu_features - Detect available CPU features
 * Checks CPUID for important features
 */
void detect_cpu_features(void) {
    memset(&kernel_state.cpu, 0, sizeof(cpu_features_t));
    
    /* In a full implementation, this would use CPUID instruction
     * For now, we set some defaults for x86-64 */
    kernel_state.cpu.has_pae = 1;      /* PAE always available on x86-64 */
    kernel_state.cpu.has_pse = 1;      /* PSE always available on x86-64 */
    kernel_state.cpu.has_rdmsr = 1;
    kernel_state.cpu.has_wrmsr = 1;
}

/**
 * init_interrupts - Initialize interrupt handling
 * Sets up IDT and exception handlers
 */
void init_interrupts(void) {
    /* This would set up the Interrupt Descriptor Table
     * and register handlers for CPU exceptions (0-31)
     * and hardware interrupts (32+) */
}

/**
 * init_timer - Initialize system timer
 * Sets up PIT or APIC timer for scheduling
 */
void init_timer(void) {
    /* Initialize timer for the scheduler
     * This would typically set up PIT or APIC timer
     * to interrupt every 10ms (100 Hz) */
}

/**
 * init_devices - Initialize hardware devices
 * Probes PCI bus, initializes drivers
 */
void init_devices(void) {
    /* Device initialization:
     * - Scan PCI bus
     * - Load device drivers
     * - Initialize disk controllers
     * - Initialize network devices */
}

/**
 * init_scheduler - Initialize process scheduler
 * Sets up scheduler queues and selects first process
 */
void init_scheduler(void) {
    /* Initialize the process scheduler:
     * - Create run queues for each priority level
     * - Set up load balancing
     * - Initialize context switching */
}

/**
 * start_init_process - Fork and execute /sbin/init
 * Creates the first userspace process (PID 1)
 */
void start_init_process(void) {
    /* This would:
     * - Create a new process structure
     * - Load /sbin/init binary
     * - Switch to user mode
     * - Execute init */
}

/**
 * kernel_panic - Halt system with error message
 * Called when unrecoverable error occurs
 */
void kernel_panic(const char *message) {
    /* Print panic message */
    /* Stop all CPUs */
    /* Halt system */
    while(1) {
        #ifdef __GNUC__
            __asm__ __volatile__("hlt");
        #else
            /* Fallback for non-GCC compilers */
            while(1);
        #endif
    }
}

/**
 * Kernel exception handlers (stubs)
 */
void exception_handler_0(void) { kernel_panic("Division by Zero"); }
void exception_handler_1(void) { kernel_panic("Debug"); }
void exception_handler_2(void) { kernel_panic("NMI"); }
void exception_handler_3(void) { kernel_panic("Breakpoint"); }
void exception_handler_6(void) { kernel_panic("Invalid Opcode"); }
void exception_handler_8(void) { kernel_panic("Double Fault"); }
void exception_handler_11(void) { kernel_panic("Segment Not Present"); }
void exception_handler_12(void) { kernel_panic("Stack Segment Fault"); }
void exception_handler_13(void) { kernel_panic("General Protection Fault"); }
void exception_handler_14(void) { kernel_panic("Page Fault"); }

/**
 * IRQ handlers (stubs)
 */
void irq_handler_0(void) { /* Timer */ }
void irq_handler_1(void) { /* Keyboard */ }
void irq_handler_2(void) { /* Cascade */ }
void irq_handler_3(void) { /* COM2 */ }
void irq_handler_4(void) { /* COM1 */ }
void irq_handler_5(void) { /* LPT2 */ }
void irq_handler_6(void) { /* Floppy */ }
void irq_handler_7(void) { /* LPT1 */ }
void irq_handler_8(void) { /* CMOS RTC */ }
void irq_handler_9(void) { /* Free */ }
void irq_handler_10(void) { /* Free */ }
void irq_handler_11(void) { /* Free */ }
void irq_handler_12(void) { /* PS/2 Mouse */ }
void irq_handler_13(void) { /* Coprocessor */ }
void irq_handler_14(void) { /* Primary ATA */ }
void irq_handler_15(void) { /* Secondary ATA */ }
