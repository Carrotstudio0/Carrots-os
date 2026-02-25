/*
 * CarrotOS Session Manager
 * session.h - User session management
 * 
 * Handles:
 * - Login sessions
 * - Session persistence
 * - User environment setup
 * - Session lifecycle
 */

#ifndef __SESSION_H__
#define __SESSION_H__

#include <stdint.h>
#include <time.h>

typedef struct {
    uint32_t session_id;
    uint32_t uid;
    uint32_t gid;
    char username[64];
    char seat[64];
    char vt[16];
    time_t start_time;
    time_t last_activity;
    int shell_pid;
    int desktop_pid;
    char session_type[32]; /* "wayland", "x11", "tty" */
    int active;
} session_t;

/* Session operations */
int session_create(uint32_t uid, const char *username, const char *seat);
int session_destroy(uint32_t session_id);
int session_activate(uint32_t session_id);
int session_lock(uint32_t session_id);
int session_unlock(uint32_t session_id);

#endif /* __SESSION_H__ */
