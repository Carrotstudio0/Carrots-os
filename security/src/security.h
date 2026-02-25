/*
 * CarrotOS Security Module
 * security.h - System security definitions and interfaces
 * 
 * Implements:
 * - Mandatory Access Control (MAC)
 * - Discretionary Access Control (DAC)
 * - SELinux/AppArmor integration
 * - Cryptographic operations
 */

#ifndef __SECURITY_H__
#define __SECURITY_H__

#include <stdint.h>

/* User ID and Group ID */
typedef struct {
    uint32_t uid;
    uint32_t gid;
    uint32_t egid;
    uint32_t groups[32];
    uint32_t ngroups;
} user_context_t;

/* File permissions (traditional Unix) */
typedef struct {
    uint16_t mode;
    uint32_t uid;
    uint32_t gid;
    uint8_t acl_entries;
} file_permissions_t;

/* Security context (SELinux style) */
typedef struct {
    char user[64];
    char role[64];
    char type[64];
    char level[64];
} security_context_t;

/* Capability (Linux CAP) */
typedef uint64_t capability_set_t;

/* Audit event */
typedef struct {
    uint64_t event_id;
    uint64_t timestamp;
    uint32_t uid;
    char action[128];
    char result[32];
    char object[256];
} audit_event_t;

/* Security functions */
int security_init(void);
int security_check_permission(user_context_t *user, const char *resource, int access_type);
int security_set_context(uint32_t pid, security_context_t *context);
int security_get_context(uint32_t pid, security_context_t *context);

/* Capability management */
int cap_has(capability_set_t caps, int cap);
int cap_set(uint32_t pid, capability_set_t caps);
int cap_drop(uint32_t pid, capability_set_t caps);

/* Audit logging */
int audit_log_event(audit_event_t *event);
int audit_get_log(audit_event_t **log, int *count);

#endif /* __SECURITY_H__ */
