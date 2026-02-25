/*
 * CarrotOS File Manager
 * Basic file browser and manager
 */

#ifndef __FILE_MANAGER_H__
#define __FILE_MANAGER_H__

#include <stdint.h>
#include <time.h>

/* File entry */
typedef struct {
    char name[256];
    char path[512];
    uint64_t size;
    uint32_t permissions;
    char owner[64];
    time_t modified;
    uint32_t is_dir;
    char mime_type[128];
} file_entry_t;

/* Directory listing */
typedef struct {
    file_entry_t *entries;
    uint32_t count;
} dir_listing_t;

/* File operations */
dir_listing_t* fm_list_directory(const char *path);
int fm_copy_file(const char *src, const char *dst);
int fm_move_file(const char *src, const char *dst);
int fm_delete_file(const char *path);
int fm_create_directory(const char *path);

#endif /* __FILE_MANAGER_H__ */
