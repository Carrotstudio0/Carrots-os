/**
 * CarrotOS Init System - main.c
 * PID 1 - Core system initialization and service management
 * 
 * (C) 2024 CarrotOS Project
 * GPL v3 License
 * 
 * Responsibilities:
 * - Mount essential filesystems (/proc, /sys, /dev, /tmp, /run)
 * - Initialize system logging (syslog)
 * - Parse service configuration files
 * - Spawn and monitor system services
 * - Handle shutdown sequences and cleanup
 * - Reap zombie processes
 * - Manage runlevels (multiuser, GUI)
 * - Handle signals for graceful shutdown
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <syslog.h>
#include <errno.h>

/* ============ Configuration ============ */
#define MAX_SERVICES        256
#define MAX_RUNLEVEL        5
#define RUNLEVEL_SINGLE     1
#define RUNLEVEL_MULTIUSER  2
#define RUNLEVEL_GUI        5
#define SERVICE_NAME_LEN    64
#define SERVICE_PATH_LEN    256
#define SERVICE_ARGS_LEN    512

/* ============ Service Structure ============ */
typedef struct {
    char name[SERVICE_NAME_LEN];
    char path[SERVICE_PATH_LEN];
    char args[SERVICE_ARGS_LEN];
    int pid;
    int respawn;        /* Auto-restart on failure */
    int runlevel;
    int active;
    int enabled;
    int restart_count;
    int max_respawn;    /* Max respawn attempts */
} service_t;

/* ============ Global State ============ */
static service_t services[MAX_SERVICES];
static int num_services = 0;
static int current_runlevel = RUNLEVEL_GUI;
static volatile int shutdown_requested = 0;
static volatile int reap_children = 0;
static int init_errors = 0;

/* ============ Function Declarations ============ */
static void init_log(const char *fmt, ...);
static void init_log_err(const char *fmt, ...);
static void init_mount_filesystems(void);
static void init_setup_logging(void);
static void init_load_services(void);
static void init_spawn_services(void);
static void init_reap_children(void);
static void signal_handler(int sig);
static void init_shutdown(void);
static int spawn_service(service_t *service);
static int load_service_file(const char *filename);

/**
 * init_log - Log message through syslog
 */
static void init_log(const char *fmt, ...) {
    va_list args;
    char buffer[256];
    
    va_start(args, fmt);
    vsnprintf(buffer, sizeof(buffer), fmt, args);
    va_end(args);
    
    syslog(LOG_INFO, "[init] %s", buffer);
    fprintf(stderr, "[init] %s\n", buffer);
}

/**
 * init_log_err - Log error message
 */
static void init_log_err(const char *fmt, ...) {
    va_list args;
    char buffer[256];
    
    va_start(args, fmt);
    vsnprintf(buffer, sizeof(buffer), fmt, args);
    va_end(args);
    
    syslog(LOG_ERR, "[init] ERROR: %s", buffer);
    fprintf(stderr, "[init] ERROR: %s\n", buffer);
    init_errors++;
}

/**
 * init_mount_filesystems - Mount essential filesystems
 * Mounts /proc, /sys, /dev, /tmp, /run, etc.
 */
static void init_mount_filesystems(void) {
    int ret;
    
    init_log("Mounting essential filesystems...");
    
    /* Mount procfs at /proc */
    ret = mount("proc", "/proc", "proc", MS_NOEXEC | MS_NOSUID | MS_NODEV, NULL);
    if (ret != 0 && errno != EBUSY) {
        init_log_err("Failed to mount /proc: %s", strerror(errno));
    } else {
        init_log("✓ /proc mounted (procfs)");
    }
    
    /* Mount sysfs at /sys */
    ret = mount("sys", "/sys", "sysfs", MS_NOEXEC | MS_NOSUID | MS_NODEV, NULL);
    if (ret != 0 && errno != EBUSY) {
        init_log_err("Failed to mount /sys: %s", strerror(errno));
    } else {
        init_log("✓ /sys mounted (sysfs)");
    }
    
    /* Mount devtmpfs at /dev */
    ret = mount("devtmpfs", "/dev", "devtmpfs", MS_NOSUID | MS_STRICTATIME, "size=10M");
    if (ret != 0 && errno != EBUSY) {
        init_log_err("Failed to mount /dev: %s", strerror(errno));
    } else {
        init_log("✓ /dev mounted (devtmpfs)");
    }
    
    /* Create /dev/pts and mount devpts */
    mkdir("/dev/pts", 0755);
    ret = mount("devpts", "/dev/pts", "devpts", MS_NOSUID | MS_NOEXEC, 
                "gid=5,mode=620");
    if (ret != 0 && errno != EBUSY) {
        init_log_err("Failed to mount /dev/pts: %s", strerror(errno));
    } else {
        init_log("✓ /dev/pts mounted (devpts)");
    }
    
    /* Mount tmpfs at /tmp */
    ret = mount("tmpfs", "/tmp", "tmpfs", MS_NOEXEC | MS_NOSUID | MS_NODEV, 
                "size=256M,mode=1777");
    if (ret != 0 && errno != EBUSY) {
        init_log_err("Failed to mount /tmp: %s", strerror(errno));
    } else {
        init_log("✓ /tmp mounted (tmpfs)");
    }
    
    /* Mount tmpfs at /run */
    mkdir("/run", 0755);
    ret = mount("tmpfs", "/run", "tmpfs", MS_NOEXEC | MS_NOSUID | MS_NODEV, 
                "size=128M,mode=0755");
    if (ret != 0 && errno != EBUSY) {
        init_log_err("Failed to mount /run: %s", strerror(errno));
    } else {
        init_log("✓ /run mounted (tmpfs)");
    }
    
    /* Setup loopback device */
    system("ip link set lo up");
    system("ip addr add 127.0.0.1/8 dev lo");
    
    init_log("Filesystem mounting complete");
}

/**
 * init_setup_logging - Initialize syslog and logging
 */
static void init_setup_logging(void) {
    init_log("Initializing system logging...");
    
    /* Open syslog connection */
    openlog("init", LOG_PID | LOG_CONS, LOG_DAEMON);
    
    init_log("Syslog initialized");
    init_log("CarrotOS Init System v1.0 started (PID %d)", getpid());
}

/**
 * load_service_file - Load a service definition from config file
 */
static int load_service_file(const char *filename) {
    FILE *f;
    char line[512];
    char name[SERVICE_NAME_LEN];
    char path[SERVICE_PATH_LEN];
    char args[SERVICE_ARGS_LEN];
    int runlevel = 2;
    int respawn = 0;
    
    if (num_services >= MAX_SERVICES) {
        init_log_err("Too many services (max %d)", MAX_SERVICES);
        return -1;
    }
    
    f = fopen(filename, "r");
    if (!f) {
        init_log_err("Cannot open service file: %s", filename);
        return -1;
    }
    
    memset(name, 0, sizeof(name));
    memset(path, 0, sizeof(path));
    memset(args, 0, sizeof(args));
    
    while (fgets(line, sizeof(line), f)) {
        char *key, *value, *saveptr;
        
        /* Skip comments and empty lines */
        if (line[0] == '#' || line[0] == '\n') continue;
        
        key = strtok_r(line, "=", &saveptr);
        if (!key) continue;
        
        value = strtok_r(NULL, "\n", &saveptr);
        if (!value) continue;
        
        /* Trim whitespace */
        while (*key == ' ' || *key == '\t') key++;
        while (*value == ' ' || *value == '\t') value++;
        
        if (strcmp(key, "Name") == 0) {
            strncpy(name, value, SERVICE_NAME_LEN - 1);
        } else if (strcmp(key, "Path") == 0) {
            strncpy(path, value, SERVICE_PATH_LEN - 1);
        } else if (strcmp(key, "Args") == 0) {
            strncpy(args, value, SERVICE_ARGS_LEN - 1);
        } else if (strcmp(key, "Runlevel") == 0) {
            runlevel = atoi(value);
        } else if (strcmp(key, "Respawn") == 0) {
            respawn = (strcmp(value, "yes") == 0 ||
                       strcmp(value, "true") == 0);
        }
    }
    fclose(f);
    
    /* Validate service entry */
    if (strlen(name) == 0 || strlen(path) == 0) {
        init_log_err("Invalid service file: %s (missing Name or Path)", filename);
        return -1;
    }
    
    /* Add service to list */
    strncpy(services[num_services].name, name, SERVICE_NAME_LEN - 1);
    strncpy(services[num_services].path, path, SERVICE_PATH_LEN - 1);
    strncpy(services[num_services].args, args, SERVICE_ARGS_LEN - 1);
    services[num_services].runlevel = runlevel;
    services[num_services].respawn = respawn;
    services[num_services].active = 0;
    services[num_services].enabled = 1;
    services[num_services].pid = -1;
    services[num_services].restart_count = 0;
    services[num_services].max_respawn = 5;
    
    init_log("Service loaded: %s (runlevel %d, respawn=%d)",
             name, runlevel, respawn);
    
    num_services++;
    return 0;
}

/**
 * init_load_services - Load service definitions from /etc/carrot/services/
 */
static void init_load_services(void) {
    init_log("Loading service definitions...");
    
    /* In a real implementation, this would:
     * 1. Scan /etc/carrot/services/ directory
     * 2. Load each .service.yaml file
     * 3. Parse service dependencies
     * 4. Build service startup order
     */
    
    init_log("Loaded %d services", num_services);
}

/**
 * spawn_service - Spawn a single service process
 */
static int spawn_service(service_t *service) {
    pid_t pid;
    char *argv[16];
    int argc = 0;
    char args_copy[SERVICE_ARGS_LEN];
    char *arg, *saveptr;
    
    if (!service->enabled) {
        return 0;
    }
    
    pid = fork();
    if (pid < 0) {
        init_log_err("fork() failed for service %s: %s",
                     service->name, strerror(errno));
        return -1;
    }
    
    if (pid == 0) {
        /* Child process */
        init_log("Spawning service: %s (PID will be %d)", 
                 service->name, getpid());
        
        /* Prepare arguments */
        argv[argc++] = service->path;
        
        if (strlen(service->args) > 0) {
            strncpy(args_copy, service->args, sizeof(args_copy) - 1);
            arg = strtok_r(args_copy, " ", &saveptr);
            while (arg && argc < 15) {
                argv[argc++] = arg;
                arg = strtok_r(NULL, " ", &saveptr);
            }
        }
        
        argv[argc] = NULL;
        
        /* Execute service */
        execv(service->path, argv);
        
        /* execv should not return */
        init_log_err("execv() failed for %s: %s", 
                     service->path, strerror(errno));
        exit(127);
    }
    
    /* Parent process */
    service->pid = pid;
    service->active = 1;
    init_log("Service %s spawned with PID %d", service->name, pid);
    
    return 0;
}

/**
 * init_spawn_services - Spawn all services for current runlevel
 */
static void init_spawn_services(void) {
    int i;
    
    init_log("Spawning services for runlevel %d...", current_runlevel);
    
    for (i = 0; i < num_services; i++) {
        if (services[i].runlevel <= current_runlevel) {
            spawn_service(&services[i]);
        }
    }
    
    init_log("Service spawning complete");
}

/**
 * init_reap_children - Reap zombie child processes
 */
static void init_reap_children(void) {
    int status, i;
    pid_t pid;
    
    while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
        /* Find and update service that exited */
        for (i = 0; i < num_services; i++) {
            if (services[i].pid == pid) {
                init_log("Service %s (PID %d) terminated (status %d)",
                         services[i].name, pid, WEXITSTATUS(status));
                
                services[i].active = 0;
                services[i].pid = -1;
                
                /* Respawn if enabled */
                if (services[i].respawn && 
                    services[i].restart_count < services[i].max_respawn) {
                    init_log("Respawning service %s (attempt %d/%d)",
                             services[i].name,
                             services[i].restart_count + 1,
                             services[i].max_respawn);
                    services[i].restart_count++;
                    spawn_service(&services[i]);
                }
                break;
            }
        }
    }
}

/**
 * signal_handler - Handle signals sent to init
 */
static void signal_handler(int sig) {
    switch (sig) {
        case SIGTERM:
        case SIGINT:
            init_log("Init received SIGTERM/SIGINT, initiating shutdown...");
            shutdown_requested = 1;
            break;
            
        case SIGCHLD:
            reap_children = 1;
            break;
            
        case SIGHUP:
            init_log("Init received SIGHUP, reloading services...");
            /* Reload service configuration */
            break;
            
        case SIGUSR1:
            init_log("Init received SIGUSR1");
            break;
            
        case SIGUSR2:
            init_log("Init received SIGUSR2");
            break;
    }
}

/**
 * init_shutdown - Gracefully shutdown all services
 */
static void init_shutdown(void) {
    int i, retries;
    
    init_log("Initiating system shutdown...");
    
    /* Send SIGTERM to all services */
    for (i = 0; i < num_services; i++) {
        if (services[i].active && services[i].pid > 0) {
            init_log("Terminating service %s (PID %d)",
                     services[i].name, services[i].pid);
            kill(services[i].pid, SIGTERM);
        }
    }
    
    /* Wait up to 10 seconds for services to terminate */
    for (retries = 100; retries > 0; retries--) {
        int active_count = 0;
        
        usleep(100000);  /* 100ms */
        
        for (i = 0; i < num_services; i++) {
            if (services[i].active && services[i].pid > 0) {
                active_count++;
            }
        }
        
        if (active_count == 0) {
            break;
        }
    }
    
    /* Force kill any remaining services */
    for (i = 0; i < num_services; i++) {
        if (services[i].active && services[i].pid > 0) {
            init_log("Force killing service %s (PID %d)",
                     services[i].name, services[i].pid);
            kill(services[i].pid, SIGKILL);
        }
    }
    
    /* Unmount filesystems */
    init_log("Unmounting filesystems...");
    umount2("/tmp", MNT_FORCE);
    umount2("/run", MNT_FORCE);
    umount2("/dev/pts", MNT_FORCE);
    umount2("/dev", MNT_FORCE);
    umount2("/sys", MNT_FORCE);
    umount2("/proc", MNT_FORCE);
    
    init_log("Shutdown complete");
    init_log("Init errors: %d", init_errors);
    
    closelog();
}

/**
 * main - Init main entry point
 */
int main(int argc, char **argv) {
    struct sigaction sa;
    
    /* Register signal handlers */
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGCHLD, &sa, NULL);
    sigaction(SIGHUP, &sa, NULL);
    sigaction(SIGUSR1, &sa, NULL);
    sigaction(SIGUSR2, &sa, NULL);
    
    /* Initialize system */
    init_setup_logging();
    init_log("============================================");
    init_log("CarrotOS Init System v1.0");
    init_log("PID 1 - Core System Process");
    init_log("============================================");
    
    /* Stage 1: Mount critical filesystems */
    init_mount_filesystems();
    
    /* Stage 2: Load service definitions */
    init_load_services();
    
    /* Stage 3: Spawn services */
    init_spawn_services();
    
    init_log("System ready, entering main loop");
    init_log("============================================");
    
    /* Main loop: wait for signals and manage services */
    while (!shutdown_requested) {
        if (reap_children) {
            reap_children = 0;
            init_reap_children();
        }
        
        pause();
    }
    
    /* Shutdown sequence */
    init_shutdown();
    
    return 0;
}

