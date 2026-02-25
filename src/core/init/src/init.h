/*
 * CarrotOS Init Process
 * PID 1 - System initialization and service manager
 * 
 * Minimal init implementation that starts essential services,
 * manages service lifecycle, and handles system shutdown.
 */

#ifndef __INIT_H__
#define __INIT_H__

#include <stdint.h>

#define INIT_PID 1

/* Runlevel definitions */
typedef enum {
    RUNLEVEL_HALT = 0,
    RUNLEVEL_SINGLE = 1,
    RUNLEVEL_MULTIUSER = 2,
    RUNLEVEL_GUI = 5,
    RUNLEVEL_REBOOT = 6
} runlevel_t;

/* Service state */
typedef enum {
    SERVICE_STOPPED,
    SERVICE_STARTING,
    SERVICE_RUNNING,
    SERVICE_STOPPING
} service_state_t;

/* Service entry */
typedef struct {
    char name[64];
    char path[256];
    char args[256];
    service_state_t state;
    uint32_t pid;
    uint8_t respawn;
    uint32_t runlevel;
} service_entry_t;

/* Init functions */
int init_main(void);
int init_parse_inittab(const char *path);
int init_mount_filesystems(void);
int init_setup_networking(void);
int init_spawn_services(runlevel_t runlevel);
void init_signal_handler(int sig);

#endif /* __INIT_H__ */
