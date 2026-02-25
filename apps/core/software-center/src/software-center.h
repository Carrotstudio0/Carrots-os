/*
 * CarrotOS Software Center
 * Package manager and application store
 */

#ifndef __SOFTWARE_CENTER_H__
#define __SOFTWARE_CENTER_H__

#include <stdint.h>

/* Package metadata */
typedef struct {
    char name[128];
    char version[32];
    char description[512];
    char author[128];
    char license[64];
    uint64_t size;
    char category[64];
    char icon_url[256];
    float rating;
    uint32_t install_count;
} package_t;

/* Repository */
typedef struct {
    char name[128];
    char url[256];
    char signature_key[512];
    int enabled;
} repository_t;

/* Package operations */
int pkg_search(const char *query, package_t **results, int *count);
int pkg_install(const char *package_name);
int pkg_remove(const char *package_name);
int pkg_update(void);
int pkg_upgrade_system(void);

int repo_add(const char *name, const char *url);
int repo_remove(const char *name);
int repo_list(repository_t **repos, int *count);

#endif /* __SOFTWARE_CENTER_H__ */
