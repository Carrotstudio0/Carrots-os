/*
 * CarrotOS Overlay System
 * overlay.h - Union filesystem (OverlayFS) management
 * 
 * Handles:
 * - Multiple overlay layers
 * - Layer resolution and composition
 * - Read-write / read-only separation
 * - Persistent vs. ephemeral layers
 */

#ifndef __OVERLAY_H__
#define __OVERLAY_H__

#include <stdint.h>

/* Overlay layer definition */
typedef struct {
    char name[128];
    char path[256];
    uint32_t layer_index;
    int readonly;
    uint64_t size_bytes;
    char description[256];
} overlay_layer_t;

/* Overlay stack */
typedef struct {
    overlay_layer_t *layers;
    uint32_t num_layers;
    char mount_point[256];
} overlay_stack_t;

/* Overlay operations */
int overlay_init(void);
int overlay_add_layer(const char *name, const char *path, int readonly);
int overlay_remove_layer(const char *name);
int overlay_mount_stack(overlay_stack_t *stack);
int overlay_unmount_stack(overlay_stack_t *stack);
int overlay_get_stack(overlay_stack_t **stack);
void overlay_print_stack(overlay_stack_t *stack);

#endif /* __OVERLAY_H__ */
