/**
 * CarrotOS Professional Kernel Header
 * Comprehensive kernel interface and data structures
 * 
 * (C) 2024 CarrotOS Project
 * GPL v3 License
 * 
 * This file defines the fundamental kernel structures and
 * communication interfaces between kernel subsystems.
 */

#ifndef __KERNEL_H__
#define __KERNEL_H__

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* ============ Kernel Version Info ============ */
#define KERNEL_VERSION_MAJOR     1
#define KERNEL_VERSION_MINOR     0
#define KERNEL_VERSION_PATCH     0
#define KERNEL_BUILD_DATE        __DATE__
#define KERNEL_MAGIC             0xC4RR07OS

/* ============ Memory Configuration ============ */
#define PAGE_SIZE                4096
#define PAGE_SHIFT               12
#define PAGE_MASK                (~(PAGE_SIZE - 1))
#define KERNEL_HEAP_START        0xFFFFFFFF82000000
#define KERNEL_HEAP_SIZE         (16 * 1024 * 1024)
#define KERNEL_STACK_SIZE        (8 * PAGE_SIZE)
#define KERNEL_VIRTUAL_OFFSET    0xFFFFFFFF80000000

/* ============ Process Configuration ============ */
#define KERNEL_MAX_CPUS          64
#define KERNEL_MAX_PROCESSES     2048
#define KERNEL_PRIORITY_LEVELS   10
#define KERNEL_TIME_QUANTUM_MS   10

/* ============ Error Codes ============ */
typedef enum {
    KERN_SUCCESS            = 0,
    KERN_ENOENT             = 1,
    KERN_EINVAL             = 2,
    KERN_ENOMEM             = 3,
    KERN_EBUSY              = 4,
    KERN_EACCES             = 5,
    KERN_EIO                = 6,
    KERN_ENODEV             = 7,
    KERN_ENOTIMPLEMENTED    = 8,
    KERN_EGENERIC           = 255
} kern_error_t;

/* ============ Process/Thread States ============ */
typedef enum {
    PROC_CREATED    = 0,
    PROC_READY      = 1,
    PROC_RUNNING    = 2,
    PROC_BLOCKED    = 3,
    PROC_SLEEPING   = 4,
    PROC_STOPPED    = 5,
    PROC_TERMINATED = 6,
    PROC_ZOMBIE     = 7
} process_state_t;

/* ============ CPU Features ============ */
typedef struct {
    uint32_t has_pae;
    uint32_t has_pse;
    uint32_t has_msr;
    uint32_t has_apic;
    uint32_t has_x2apic;
    uint32_t has_rdmsr;
    uint32_t has_wrmsr;
    uint32_t has_tsc;
} cpu_features_t;

/* ============ Memory Map Entry ============ */
typedef struct {
    uint64_t base;
    uint64_t size;
    uint32_t type;
    uint32_t flags;
} memory_region_t;

/* ============ Process Control Block ============ */
typedef struct process_struct {
    uint32_t pid;
    uint32_t ppid;
    uint32_t uid;
    uint32_t gid;
    uint8_t priority;
    process_state_t state;
    uint64_t start_time;
    uint32_t cpu_time_ms;
    void *stack_ptr;
    void *context;
    void *memory_space;
    struct process_struct *next;
    struct process_struct *prev;
} pcb_t;

/* ============ Interrupt Handler Types ============ */
typedef void (*irq_handler_t)(void *context);
typedef void (*exception_handler_t)(void *context, uint32_t code);

/* ============ Kernel Subsystem ============ */
typedef struct {
    const char *name;
    int (*init)(void);
    int (*shutdown)(void);
} kernel_subsystem_t;

/* ============ Global Kernel State ============ */
typedef struct {
    uint32_t kernel_version;
    cpu_features_t cpu_features;
    uint32_t num_memory_regions;
    memory_region_t *memory_map;
    uint64_t total_memory;
    uint32_t num_cpus;
    uint64_t system_uptime_ms;
} kernel_state_t;

extern kernel_state_t kernel_state;

/* ============ Memory Management API ============ */
extern int kernel_init_memory(void);
extern void *kmalloc(size_t size);
extern void *krealloc(void *ptr, size_t new_size);
extern void kfree(void *ptr);
extern void kernel_memory_dump_stats(void);

/* ============ Interrupt & Exception API ============ */
extern int kernel_init_interrupts(void);
extern void kernel_register_irq_handler(int irq, irq_handler_t handler);
extern void kernel_register_exception_handler(int exception, exception_handler_t handler);
extern void kernel_enable_interrupts(void);
extern void kernel_disable_interrupts(void);

/* ============ Timer & Scheduling API ============ */
extern int kernel_init_timer(void);
extern int kernel_init_scheduler(void);
extern void kernel_yield(void);
extern uint64_t kernel_get_uptime_ms(void);
extern uint64_t kernel_get_ticks(void);

/* ============ Device Management API ============ */
extern int kernel_init_devices(void);
extern int kernel_scan_pci_bus(void);
extern int kernel_init_io(void);
extern int kernel_init_filesystem(void);

/* ============ Process Management API ============ */
extern int kernel_init_process_management(void);
extern pcb_t *kernel_create_process(const char *name, uint8_t priority);
extern int kernel_destroy_process(uint32_t pid);
extern pcb_t *kernel_get_current_process(void);
extern pcb_t *kernel_find_process(uint32_t pid);

/* ============ CPU Features API ============ */
extern void kernel_detect_cpu_features(void);
extern void kernel_print_cpu_info(void);

/* ============ Logging & Diagnostics API ============ */
extern void kernel_log(const char *level, const char *fmt, ...);
extern void kernel_panic(const char *fmt, ...);
extern void kernel_dump_kernel_state(void);
extern void kernel_log_panic(const char *msg, ...);

/* ============ System Management API ============ */
extern int kernel_main(void);
extern int kernel_init_memory(void);
extern void kernel_cpu_halt(void);
extern void kernel_cpu_busy_wait(uint32_t ms);

/* ============ Helper Macros ============ */
#define KERNEL_ASSERT(condition, msg) \
    do { \
        if (!(condition)) { \
            kernel_panic("ASSERTION FAILED: %s (%s:%d)", msg, __FILE__, __LINE__); \
        } \
    } while(0)

#define KERNEL_BUG_ON(condition, msg) \
    do { \
        if (condition) { \
            kernel_panic("BUG: %s (%s:%d)", msg, __FILE__, __LINE__); \
        } \
    } while(0)

#endif /* __KERNEL_H__ */
