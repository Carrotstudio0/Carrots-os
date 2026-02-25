/*
 * CarrotOS Kernel Entry Point
 * main.c - Primary kernel initialization and main loop
 */

#include "kernel.h"

/* Kernel subsystems initialization order */
static struct kernel_subsystem subsystems[] = {
    {"Memory Manager", kernel_init_Memory, NULL},
    {"Interrupt Manager", kernel_init_interrupts, NULL},
    {"Scheduler", kernel_init_scheduler, NULL},
    {"I/O Manager", kernel_init_io, NULL},
    {"Filesystem", kernel_init_filesystem, NULL},
    {NULL, NULL, NULL}
};

/**
 * kernel_main - Entry point after bootloader
 * Initializes all kernel subsystems in order
 */
int kernel_main(void) {
    kernel_log("INFO", "CarrotOS Kernel %d.%d.%d starting...",
               KERNEL_VERSION_MAJOR,
               KERNEL_VERSION_MINOR,
               KERNEL_VERSION_PATCH);

    /* Initialize each subsystem */
    for (int i = 0; subsystems[i].name != NULL; i++) {
        kernel_log("INFO", "Initializing %s...", subsystems[i].name);
        if (subsystems[i].init() != 0) {
            kernel_panic("Failed to initialize %s", subsystems[i].name);
        }
    }

    kernel_log("INFO", "Kernel initialization complete");
    kernel_log("INFO", "Starting system services...");

    /* Main kernel loop - scheduler takes over */
    return 0;
}

/**
 * kernel_log - Simple logging facility
 */
void kernel_log(const char *level, const char *msg, ...) {
    /* Placeholder - will output to framebuffer/serial */
    /* Format: [LEVEL] message */
}

/**
 * kernel_log_panic - Log panic and halt
 */
void kernel_log_panic(const char *msg, ...) {
    /* Output to serial port or framebuffer */
}
