/*
 * CarrotOS Desktop Compositor
 * Main header for Wayland/Weston integration
 * 
 * Responsibility:
 * - Display server lifecycle
 * - Input handling (keyboard, mouse, touchscreen)
 * - Window management
 * - Graphics rendering
 */

#ifndef __DESKTOP_COMPOSITOR_H__
#define __DESKTOP_COMPOSITOR_H__

#include <stdint.h>
#include <wayland-server.h>

/* Display output */
typedef struct {
    char name[64];
    uint32_t width;
    uint32_t height;
    uint32_t refresh_rate;
    uint32_t rotation;
    struct wl_output *wl_output;
} display_output_t;

/* Input device */
typedef struct {
    char name[64];
    uint32_t capabilities;
    int fd;
} input_device_t;

/* Compositor context */
typedef struct {
    struct wl_display *display;
    struct weston_compositor *compositor;
    display_output_t outputs[4];
    int num_outputs;
    input_device_t inputs[16];
    int num_inputs;
} compositor_context_t;

extern compositor_context_t *g_compositor;

int compositor_init(void);
int compositor_add_output(uint32_t width, uint32_t height, uint32_t refresh);
int compositor_run(void);
void compositor_shutdown(void);

#endif /* __DESKTOP_COMPOSITOR_H__ */
