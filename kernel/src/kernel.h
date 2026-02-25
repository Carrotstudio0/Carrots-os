/*
 * CarrotOS Kernel Main Header
 * Core kernel definitions and interfaces
 * 
 * This file defines the fundamental kernel structures and
 * communication interfaces between kernel subsystems.
 */

#ifndef __KERNEL_H__
#define __KERNEL_H__

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define KERNEL_VERSION_MAJOR     1
#define KERNEL_VERSION_MINOR     0
#define KERNEL_VERSION_PATCH     0
#define KERNEL_BUILD_DATE        __DATE__

/* Kernel magic number for validation */
#define KERNEL_MAGIC             0xC4RR07OS

/* Maximum CPU cores supported */
#define KERNEL_MAX_CPUS          64

/* Kernel panic macro */
#define kernel_panic(msg, ...) \
    do { \
        kernel_log_panic(msg, ##__VA_ARGS__); \
        asm volatile("hlt"); \
    } while(1)

/* Process/Thread states */
typedef enum {
    PROC_CREATED = 0,
    PROC_READY,
    PROC_RUNNING,
    PROC_BLOCKED,
    PROC_TERMINATED
} process_state_t;

/* Process Control Block */
typedef struct {
    uint32_t pid;
    uint32_t ppid;
    process_state_t state;
    uint64_t start_time;
    void *context;
    void *memory_space;
} pcb_t;

/* Interrupt handler type */
typedef void (*irq_handler_t)(void *context);

/* Core kernel subsystems */
struct kernel_subsystem {
    const char *name;
    int (*init)(void);
    int (*shutdown)(void);
};

/* Kernel initialization */
int kernel_main(void);
int kernel_init_Memory(void);
int kernel_init_interrupts(void);
int kernel_init_scheduler(void);
int kernel_init_io(void);
int kernel_init_filesystem(void);

/* Logging */
void kernel_log(const char *level, const char *msg, ...);
void kernel_log_panic(const char *msg, ...);

#endif /* __KERNEL_H__ */
