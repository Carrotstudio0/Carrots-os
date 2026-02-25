/**
 * CarrotOS Init Process (PID 1)
 * Manages system initialization and service startup
 * 
 * (C) 2024 CarrotOS Project
 * GPL v3 License
 */

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/mount.h>

#define INIT_VERSION "1.0"
#define MAX_SERVICES 32
#define MAX_RUNLEVELS 7

/* Runlevel configuration */
typedef enum {
    RUNLEVEL_0 = 0,  /* Halt */
    RUNLEVEL_1 = 1,  /* Single user */
    RUNLEVEL_2 = 2,  /* Multi-user */
    RUNLEVEL_3 = 3,  /* Multi-user with network */
    RUNLEVEL_4 = 4,  /* Unused */
    RUNLEVEL_5 = 5,  /* X11 graphical */
    RUNLEVEL_6 = 6   /* Reboot */
} runlevel_t;

/* Service status */
typedef enum {
    SERVICE_STOPPED = 0,
    SERVICE_RUNNING = 1,
    SERVICE_FAILED = 2,
    SERVICE_RESPAWN = 3
} service_status_t;

/* Service definition */
typedef struct {
    char name[32];
    char binary[128];
    char *argv[16];
    runlevel_t runlevel;
    int respawn;        /* Respawn if dies? */
    pid_t pid;
    service_status_t status;
} service_t;

/* Global init state */
typedef struct {
    runlevel_t current_runlevel;
    service_t services[MAX_SERVICES];
    int num_services;
    int running;
} init_state_t;

static init_state_t init_state = {0};

/* Forward declarations */
void init_system(void);
void mount_filesystems(void);
void setup_devices(void);
void load_services(void);
void start_service(service_t *service);
void stop_service(service_t *service);
void change_runlevel(runlevel_t level);
void signal_handler(int sig);
void main_loop(void);
void emergency_shell(void);
void system_shutdown(int reboot);

/**
 * main - Init process entry point
 * This is PID 1, the first userspace process
 */
int main(int argc, char *argv[]) {
    /* Ignore signals initially */
    signal(SIGTERM, SIG_IGN);
    signal(SIGINT, SIG_IGN);
    
    /* Initialize system */
    init_system();
    
    /* Update signal handlers */
    signal(SIGTERM, signal_handler);
    signal(SIGINT, signal_handler);
    signal(SIGCHLD, signal_handler);
    
    /* Enter main init loop */
    main_loop();
    
    return 0;
}

/**
 * init_system - Initialize the system from bootup
 */
void init_system(void) {
    printf("CarrotOS Init v%s\n", INIT_VERSION);
    
    /* Mount essential filesystems */
    mount_filesystems();
    
    /* Setup device files */
    setup_devices();
    
    /* Load service configuration */
    load_services();
    
    /* Start with runlevel 3 (multi-user with network) */
    change_runlevel(RUNLEVEL_3);
}

/**
 * mount_filesystems - Mount essential filesystems
 */
void mount_filesystems(void) {
    printf("[INIT] Mounting filesystems\n");
    
    /* Mount /proc */
    if (mount("proc", "/proc", "procfs", 0, NULL) != 0) {
        printf("[INIT] Warning: Failed to mount /proc\n");
    }
    
    /* Mount /sys */
    if (mount("sysfs", "/sys", "sysfs", 0, NULL) != 0) {
        printf("[INIT] Warning: Failed to mount /sys\n");
    }
    
    /* Mount /dev */
    if (mount("devtmpfs", "/dev", "devtmpfs", 0, NULL) != 0) {
        printf("[INIT] Warning: Failed to mount /dev\n");
    }
    
    /* Mount /run */
    if (mount("tmpfs", "/run", "tmpfs", 0, "size=50%") != 0) {
        printf("[INIT] Warning: Failed to mount /run\n");
    }
    
    printf("[INIT] Filesystems mounted\n");
}

/**
 * setup_devices - Create essential device nodes
 */
void setup_devices(void) {
    printf("[INIT] Setting up devices\n");
    
    /* In a real system, this would:
     * - Create device nodes
     * - Load udev or equivalent
     * - Load kernel modules required at boot */
}

/**
 * load_services - Load service configuration
 */
void load_services(void) {
    int i = 0;
    
    printf("[INIT] Loading service configuration\n");
    
    /* Essential services */
    
    /* Logging daemon */
    strcpy(init_state.services[i].name, "syslogd");
    strcpy(init_state.services[i].binary, "/sbin/syslogd");
    init_state.services[i].argv[0] = "/sbin/syslogd";
    init_state.services[i].argv[1] = NULL;
    init_state.services[i].runlevel = RUNLEVEL_3;
    init_state.services[i].respawn = 1;
    init_state.services[i].status = SERVICE_STOPPED;
    i++;
    
    /* Network manager */
    strcpy(init_state.services[i].name, "networkd");
    strcpy(init_state.services[i].binary, "/lib/systemd/systemd-networkd");
    init_state.services[i].argv[0] = "/lib/systemd/systemd-networkd";
    init_state.services[i].argv[1] = NULL;
    init_state.services[i].runlevel = RUNLEVEL_3;
    init_state.services[i].respawn = 1;
    init_state.services[i].status = SERVICE_STOPPED;
    i++;
    
    /* SSH daemon */
    strcpy(init_state.services[i].name, "sshd");
    strcpy(init_state.services[i].binary, "/usr/sbin/sshd");
    init_state.services[i].argv[0] = "/usr/sbin/sshd";
    init_state.services[i].argv[1] = "-D";
    init_state.services[i].argv[2] = NULL;
    init_state.services[i].runlevel = RUNLEVEL_3;
    init_state.services[i].respawn = 1;
    init_state.services[i].status = SERVICE_STOPPED;
    i++;
    
    /* Desktop environment (runlevel 5) */
    strcpy(init_state.services[i].name, "xserver");
    strcpy(init_state.services[i].binary, "/usr/bin/X");
    init_state.services[i].argv[0] = "/usr/bin/X";
    init_state.services[i].argv[1] = ":0";
    init_state.services[i].argv[2] = NULL;
    init_state.services[i].runlevel = RUNLEVEL_5;
    init_state.services[i].respawn = 1;
    init_state.services[i].status = SERVICE_STOPPED;
    i++;
    
    init_state.num_services = i;
    printf("[INIT] Loaded %d services\n", i);
}

/**
 * change_runlevel - Switch to a different runlevel
 */
void change_runlevel(runlevel_t level) {
    printf("[INIT] Changing to runlevel %d\n", level);
    
    init_state.current_runlevel = level;
    
    /* Stop services not for this runlevel */
    for (int i = 0; i < init_state.num_services; i++) {
        if (init_state.services[i].runlevel != level &&
            init_state.services[i].status != SERVICE_STOPPED) {
            stop_service(&init_state.services[i]);
        }
    }
    
    /* Start services for this runlevel */
    for (int i = 0; i < init_state.num_services; i++) {
        if (init_state.services[i].runlevel == level &&
            init_state.services[i].status != SERVICE_RUNNING) {
            start_service(&init_state.services[i]);
        }
    }
}

/**
 * start_service - Start a service
 */
void start_service(service_t *service) {
    pid_t pid = fork();
    
    if (pid == 0) {
        /* Child process - execute service */
        execv(service->binary, service->argv);
        /* If execv fails, exit immediately */
        exit(127);
    } else if (pid > 0) {
        /* Parent process - record PID */
        service->pid = pid;
        service->status = SERVICE_RUNNING;
        printf("[INIT] Started service '%s' (PID %d)\n", service->name, pid);
    } else {
        /* Fork failed */
        service->status = SERVICE_FAILED;
        printf("[INIT] Failed to start service '%s'\n", service->name);
    }
}

/**
 * stop_service - Stop a running service
 */
void stop_service(service_t *service) {
    if (service->status != SERVICE_RUNNING) {
        return;
    }
    
    printf("[INIT] Stopping service '%s' (PID %d)\n", service->name, service->pid);
    
    /* Send SIGTERM to service */
    kill(service->pid, SIGTERM);
    
    /* Wait for graceful shutdown (5 seconds) */
    int timeout = 5;
    while (timeout > 0 && service->status == SERVICE_RUNNING) {
        sleep(1);
        timeout--;
        
        /* Check if process exited */
        if (waitpid(service->pid, NULL, WNOHANG) > 0) {
            service->status = SERVICE_STOPPED;
            return;
        }
    }
    
    /* Force kill if still running */
    if (service->status == SERVICE_RUNNING) {
        printf("[INIT] Force killing service '%s'\n", service->name);
        kill(service->pid, SIGKILL);
        waitpid(service->pid, NULL, 0);
    }
    
    service->status = SERVICE_STOPPED;
}

/**
 * signal_handler - Handle init signals
 */
void signal_handler(int sig) {
    switch (sig) {
        case SIGCHLD:
            /* Child process died, handle respawning */
            {
                pid_t pid;
                int status;
                while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
                    for (int i = 0; i < init_state.num_services; i++) {
                        if (init_state.services[i].pid == pid) {
                            printf("[INIT] Service '%s' died\n", init_state.services[i].name);
                            
                            if (init_state.services[i].respawn && 
                                init_state.services[i].runlevel == init_state.current_runlevel) {
                                printf("[INIT] Respawning service '%s'\n", 
                                       init_state.services[i].name);
                                start_service(&init_state.services[i]);
                            } else {
                                init_state.services[i].status = SERVICE_STOPPED;
                            }
                            break;
                        }
                    }
                }
            }
            break;
            
        case SIGTERM:
        case SIGINT:
            /* Shutdown signal */
            printf("[INIT] Received shutdown signal\n");
            system_shutdown(0);
            break;
    }
}

/**
 * main_loop - Main init event loop
 */
void main_loop(void) {
    init_state.running = 1;
    
    while (init_state.running) {
        sleep(1);
        
        /* Check service health periodically */
        for (int i = 0; i < init_state.num_services; i++) {
            if (init_state.services[i].status == SERVICE_RUNNING) {
                if (waitpid(init_state.services[i].pid, NULL, WNOHANG) > 0) {
                    if (init_state.services[i].respawn) {
                        start_service(&init_state.services[i]);
                    } else {
                        init_state.services[i].status = SERVICE_STOPPED;
                    }
                }
            }
        }
    }
}

/**
 * emergency_shell - Drop to emergency shell
 * Used when system can't start normally
 */
void emergency_shell(void) {
    printf("\n*** Emergency Shell ***\n");
    printf("System failed to start. Root shell started.\n");
    
    pid_t pid = fork();
    if (pid == 0) {
        execl("/bin/sh", "/bin/sh", NULL);
        exit(127);
    } else if (pid > 0) {
        waitpid(pid, NULL, 0);
    }
}

/**
 * system_shutdown - Shutdown or reboot system
 */
void system_shutdown(int reboot) {
    printf("[INIT] System shutdown initiated\n");
    
    /* Stop all services */
    for (int i = 0; i < init_state.num_services; i++) {
        if (init_state.services[i].status == SERVICE_RUNNING) {
            stop_service(&init_state.services[i]);
        }
    }
    
    /* Unmount filesystems */
    sync();
    
    if (reboot) {
        reboot(RB_AUTOBOOT);
    } else {
        reboot(RB_POWER_OFF);
    }
}
