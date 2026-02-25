/*
 * CarrotOS Terminal Emulator
 * Basic terminal/console application
 */

#ifndef __TERMINAL_H__
#define __TERMINAL_H__

#include <stdint.h>

/* Terminal configuration */
typedef struct {
    uint32_t cols;
    uint32_t rows;
    char font_family[64];
    uint32_t font_size;
    char bg_color[8];
    char fg_color[8];
    char cursor_style[16];
} terminal_config_t;

/* Terminal operations */
int term_init(terminal_config_t *config);
int term_run(void);
void term_shutdown(void);

int term_exec_command(const char *cmd);
int term_clear_screen(void);
int term_print(const char *text);

#endif /* __TERMINAL_H__ */
