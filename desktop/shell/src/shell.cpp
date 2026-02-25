/**
 * CarrotOS Desktop Shell
 * Carrot Desktop Environment - Main shell implementation
 * 
 * (C) 2024 CarrotOS Project
 * GPL v3 License
 */

#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <memory>
#include <cstdlib>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>

#define SHELL_VERSION "1.0"
#define SHELL_NAME "Carrot Shell"

/* Forward declarations */
class DesktopEnvironment;
class Window;
class Panel;
class Launcher;
class TaskBar;

/**
 * Window class - Represents a desktop window
 */
class Window {
public:
    int window_id;
    std::string title;
    int x, y, width, height;
    bool visible;
    int process_id;
    
    Window(int id, const std::string &t) 
        : window_id(id), title(t), x(0), y(0), 
          width(800), height(600), visible(true), process_id(0) {}
    
    void show() { visible = true; }
    void hide() { visible = false; }
    void move(int new_x, int new_y) { x = new_x; y = new_y; }
    void resize(int new_width, int new_height) { width = new_width; height = new_height; }
    void focus() { /* Focus window */ }
    void close() { visible = false; }
};

/**
 * Panel class - Desktop panel (top/bottom bar)
 */
class Panel {
public:
    enum Position { TOP, BOTTOM };
    
    Position position;
    int height;
    std::vector<std::string> widgets;
    
    Panel(Position pos = TOP, int h = 32) 
        : position(pos), height(h) {}
    
    void add_widget(const std::string &widget) {
        widgets.push_back(widget);
    }
    
    void draw() {
        std::cout << "[PANEL] Drawing panel with " << widgets.size() 
                  << " widgets\n";
    }
};

/**
 * Launcher class - Application launcher
 */
class Launcher {
public:
    struct AppEntry {
        std::string name;
        std::string exec;
        std::string icon;
    };
    
private:
    std::vector<AppEntry> applications;
    
public:
    void load_applications() {
        std::cout << "[LAUNCHER] Loading applications\n";
        
        /* Load desktop applications from ~/.local/share/applications */
        /* Example entries */
        applications.push_back({"File Manager", "/usr/bin/caja", "folder"});
        applications.push_back({"Web Browser", "/usr/bin/firefox", "firefox"});
        applications.push_back({"Terminal", "/usr/bin/gnome-terminal", "terminal"});
        applications.push_back({"Text Editor", "/usr/bin/gedit", "text-editor"});
        applications.push_back({"Calculator", "/usr/bin/gnome-calculator", "calculator"});
        applications.push_back({"Settings", "/usr/bin/cinnamon-settings", "settings"});
        
        std::cout << "[LAUNCHER] Loaded " << applications.size() 
                  << " applications\n";
    }
    
    void launch_application(const std::string &name) {
        for (const auto &app : applications) {
            if (app.name == name) {
                std::cout << "[LAUNCHER] Launching: " << app.name << "\n";
                pid_t pid = fork();
                if (pid == 0) {
                    execl(app.exec.c_str(), app.exec.c_str(), nullptr);
                    exit(127);
                }
                return;
            }
        }
        std::cerr << "[LAUNCHER] Application not found: " << name << "\n";
    }
    
    void show_menu() {
        std::cout << "[LAUNCHER] Showing application menu\n";
        for (const auto &app : applications) {
            std::cout << "  - " << app.name << "\n";
        }
    }
};

/**
 * TaskBar class - Shows running applications
 */
class TaskBar {
public:
    struct TaskItem {
        std::string name;
        int window_id;
        bool active;
    };
    
private:
    std::vector<TaskItem> tasks;
    
public:
    void add_task(int window_id, const std::string &name) {
        tasks.push_back({name, window_id, false});
    }
    
    void remove_task(int window_id) {
        for (auto it = tasks.begin(); it != tasks.end(); ++it) {
            if (it->window_id == window_id) {
                tasks.erase(it);
                break;
            }
        }
    }
    
    void activate_task(int window_id) {
        for (auto &task : tasks) {
            task.active = (task.window_id == window_id);
        }
    }
    
    void draw() {
        std::cout << "[TASKBAR] Drawing taskbar with " << tasks.size() 
                  << " tasks\n";
    }
};

/**
 * Theme class - Manages desktop themes
 */
class Theme {
public:
    enum Style { LIGHT, DARK };
    
    std::string name;
    Style style;
    std::string color_scheme;
    std::string icon_theme;
    
    Theme(const std::string &n, Style s) 
        : name(n), style(s) {
        if (s == LIGHT) {
            color_scheme = "light";
            icon_theme = "Papirus";
        } else {
            color_scheme = "dark";
            icon_theme = "Papirus-Dark";
        }
    }
    
    void apply() {
        std::cout << "[THEME] Applying theme: " << name << "\n";
        std::cout << "[THEME] Color scheme: " << color_scheme << "\n";
        std::cout << "[THEME] Icon theme: " << icon_theme << "\n";
    }
};

/**
 * DesktopEnvironment class - Main desktop shell
 */
class DesktopEnvironment {
private:
    std::string name;
    std::string version;
    bool running;
    int next_window_id;
    
    std::vector<std::shared_ptr<Window>> windows;
    std::unique_ptr<Panel> top_panel;
    std::unique_ptr<Panel> bottom_panel;
    std::unique_ptr<Launcher> launcher;
    std::unique_ptr<TaskBar> taskbar;
    std::unique_ptr<Theme> current_theme;
    
    std::map<int, int> child_processes;  /* window_id -> process_id */
    
public:
    DesktopEnvironment() 
        : name("Carrot Shell"), version(SHELL_VERSION), running(false), 
          next_window_id(1) {
        top_panel = std::make_unique<Panel>(Panel::TOP, 32);
        bottom_panel = std::make_unique<Panel>(Panel::BOTTOM, 24);
        launcher = std::make_unique<Launcher>();
        taskbar = std::make_unique<TaskBar>();
        current_theme = std::make_unique<Theme>("Carrot Default", Theme::DARK);
    }
    
    void initialize() {
        std::cout << "=== " << name << " v" << version << " ===\n";
        std::cout << "[SHELL] Initializing desktop environment\n";
        
        /* Apply theme */
        current_theme->apply();
        
        /* Load applications */
        launcher->load_applications();
        
        /* Setup panels */
        top_panel->add_widget("clock");
        top_panel->add_widget("system-monitor");
        bottom_panel->add_widget("taskbar");
        
        std::cout << "[SHELL] Desktop environment initialized\n";
    }
    
    void start() {
        running = true;
        std::cout << "[SHELL] Starting desktop shell\n";
    }
    
    void stop() {
        running = false;
        std::cout << "[SHELL] Stopping desktop shell\n";
    }
    
    bool is_running() const {
        return running;
    }
    
    std::shared_ptr<Window> create_window(const std::string &title) {
        auto window = std::make_shared<Window>(next_window_id++, title);
        windows.push_back(window);
        taskbar->add_task(window->window_id, title);
        std::cout << "[SHELL] Created window: " << title 
                  << " (ID: " << window->window_id << ")\n";
        return window;
    }
    
    void close_window(int window_id) {
        for (auto it = windows.begin(); it != windows.end(); ++it) {
            if ((*it)->window_id == window_id) {
                taskbar->remove_task(window_id);
                
                /* Kill associated process if any */
                if (child_processes.find(window_id) != child_processes.end()) {
                    kill(child_processes[window_id], SIGTERM);
                    child_processes.erase(window_id);
                }
                
                windows.erase(it);
                std::cout << "[SHELL] Closed window ID: " << window_id << "\n";
                break;
            }
        }
    }
    
    void focus_window(int window_id) {
        for (auto &window : windows) {
            if (window->window_id == window_id) {
                window->focus();
                taskbar->activate_task(window_id);
                std::cout << "[SHELL] Focused window ID: " << window_id << "\n";
                return;
            }
        }
    }
    
    void launch_application(const std::string &app_name) {
        std::cout << "[SHELL] Launching application: " << app_name << "\n";
        
        auto window = create_window(app_name);
        
        pid_t pid = fork();
        if (pid == 0) {
            /* Child process */
            launcher->launch_application(app_name);
            exit(0);
        } else if (pid > 0) {
            child_processes[window->window_id] = pid;
        }
    }
    
    void draw() {
        std::cout << "[SHELL] Drawing desktop\n";
        top_panel->draw();
        
        std::cout << "[SHELL] Drawing " << windows.size() << " windows\n";
        for (auto &window : windows) {
            if (window->visible) {
                std::cout << "  - Window: " << window->title << " (" 
                          << window->width << "x" << window->height << ")\n";
            }
        }
        
        taskbar->draw();
        bottom_panel->draw();
    }
    
    void main_loop() {
        std::cout << "[SHELL] Entering main event loop\n";
        
        while (running) {
            /* Handle child process signals */
            sigset_t set;
            sigemptyset(&set);
            sigaddset(&set, SIGCHLD);
            
            int sig;
            if (sigwait(&set, &sig) == 0 && sig == SIGCHLD) {
                int status;
                pid_t pid;
                while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
                    /* Find and close window for this process */
                    for (auto &entry : child_processes) {
                        if (entry.second == pid) {
                            close_window(entry.first);
                            break;
                        }
                    }
                }
            }
            
            sleep(1);
        }
    }
    
    void shutdown() {
        std::cout << "[SHELL] Shutting down desktop environment\n";
        
        /* Close all windows */
        std::vector<int> window_ids;
        for (auto &window : windows) {
            window_ids.push_back(window->window_id);
        }
        
        for (int id : window_ids) {
            close_window(id);
        }
        
        stop();
    }
};

/**
 * Signal handlers
 */
DesktopEnvironment *g_shell = nullptr;

void signal_handler_int(int sig) {
    std::cout << "\n[SHELL] Received SIGINT, shutting down...\n";
    if (g_shell) {
        g_shell->shutdown();
    }
    exit(0);
}

void signal_handler_term(int sig) {
    std::cout << "[SHELL] Received SIGTERM, shutting down...\n";
    if (g_shell) {
        g_shell->shutdown();
    }
    exit(0);
}

/**
 * main - Desktop shell entry point
 */
int main(int argc, char *argv[]) {
    std::cout << "=== Carrot Desktop Shell ===\n";
    std::cout << "Version: " << SHELL_VERSION << "\n\n";
    
    /* Create desktop environment */
    DesktopEnvironment shell;
    g_shell = &shell;
    
    /* Setup signal handlers */
    signal(SIGINT, signal_handler_int);
    signal(SIGTERM, signal_handler_term);
    signal(SIGCHLD, SIG_DFL);
    
    /* Initialize */
    shell.initialize();
    shell.start();
    
    /* Draw initial screen */
    shell.draw();
    
    /* Enter main loop */
    shell.main_loop();
    
    /* Cleanup */
    shell.shutdown();
    
    return 0;
}
