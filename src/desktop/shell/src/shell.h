/*
 * CarrotOS Desktop Shell
 * Shell interface and window manager
 * Implements launcher, taskbar, notifications, and workspace switching
 */

#ifndef __SHELL_H__
#define __SHELL_H__

#include <stdint.h>

/* Workspace definition */
typedef struct {
    uint32_t id;
    char name[64];
    uint32_t window_count;
    void *window_list;
} workspace_t;

/* Window state */
typedef enum {
    WINDOW_CREATED,
    WINDOW_MAPPED,
    WINDOW_FOCUSED,
    WINDOW_HIDDEN,
    WINDOW_DESTROYED
} window_state_t;

/* Window properties */
typedef struct {
    uint32_t window_id;
    uint32_t app_id;
    char title[256];
    window_state_t state;
    uint32_t x, y, width, height;
} window_t;

/* Shell operations */
int shell_init(void);
int shell_run(void);
void shell_shutdown(void);

int shell_add_workspace(const char *name);
int shell_switch_workspace(uint32_t workspace_id);

int shell_create_window(uint32_t app_id, const char *title);
int shell_focus_window(uint32_t window_id);
int shell_minimize_window(uint32_t window_id);
int shell_maximize_window(uint32_t window_id);

#endif /* __SHELL_H__ */
