/*
 * CarrotOS Settings/Control Center
 * System settings and configuration application
 */

#ifndef __SETTINGS_H__
#define __SETTINGS_H__

/* Settings categories */
typedef enum {
    SETTINGS_DISPLAY,
    SETTINGS_AUDIO,
    SETTINGS_NETWORK,
    SETTINGS_BLUETOOTH,
    SETTINGS_POWER,
    SETTINGS_SYSTEM,
    SETTINGS_ACCOUNTS,
    SETTINGS_PRIVACY,
    SETTINGS_APPEARANCE
} settings_category_t;

/* Settings panel structure */
typedef struct {
    settings_category_t category;
    char name[128];
    char description[256];
    char icon_path[256];
} settings_panel_t;

int settings_init(void);
int settings_run(void);
void settings_shutdown(void);

int settings_apply_changes(settings_category_t category);

#endif /* __SETTINGS_H__ */
