/*
 * CarrotOS Logging Subsystem
 * logging.h - Kernel logging infrastructure
 * 
 * Provides:
 * - Kernel ring buffer
 * - Log levels (PANIC, ERROR, WARN, INFO, DEBUG)
 * - Multiple outputs (serial, framebuffer, file)
 */

#ifndef __LOGGING_H__
#define __LOGGING_H__

#include <stdarg.h>

/* Log levels */
typedef enum {
    LOG_PANIC = 0,
    LOG_ERROR = 1,
    LOG_WARN = 2,
    LOG_INFO = 3,
    LOG_DEBUG = 4
} log_level_t;

/* Kernel log ring buffer */
#define KERNEL_LOG_BUFFER_SIZE (256 * 1024) /* 256KB */
#define KERNEL_LOG_MAX_LINE 1024

typedef struct {
    char buffer[KERNEL_LOG_BUFFER_SIZE];
    size_t write_pos;
    size_t read_pos;
    uint32_t total_messages;
} kernel_ring_buffer_t;

/* Logging functions */
void kernel_log_init(void);
void kernel_log(log_level_t level, const char *format, ...);
void kernel_log_hex_dump(const void *data, size_t size);
void kernel_log_backtrace(void);

/* Log output targets */
void log_output_serial(const char *msg);
void log_output_framebuffer(const char *msg);
void log_output_file(const char *msg);

#endif /* __LOGGING_H__ */
