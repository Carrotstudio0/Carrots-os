#!/bin/sh
# CarrotOS Desktop Session Initialization
# ~/.xinitrc / ~/.config/wayland-session

# Set environment
export LANG=en_US.UTF-8
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/1000
export XDG_DESKTOP_DIR=~/Desktop
export XDG_DOWNLOAD_DIR=~/Downloads
export XDG_DOCUMENTS_DIR=~/Documents
export XDG_DATA_DIRS=/usr/local/share:/usr/share

# Set theme
export GTK_THEME=carrot-default
export QT_STYLE_OVERRIDE=gtk3
export GTK_CSD=1

# Start D-Bus session
eval $(dbus-launch --sh-syntax) 2>/dev/null || true

# Start Wayland/X11 session
echo "[session] Starting Carrot Desktop Environment" >> ~/.carrot/session.log

# Desktop Shell with Wayland
if command -v weston >/dev/null 2>&1; then
    echo "[session] Starting Weston compositor" >> ~/.carrot/session.log
    exec weston --user
elif command -v Xvfb >/dev/null 2>&1; then
    echo "[session] Starting Xvfb" >> ~/.carrot/session.log
    Xvfb :0 -screen 0 1280x720x24 &
    XPID=$!
    
    # Start window manager
    openbox --replace &
    
    # Start shell
    /usr/bin/carrot-shell-launcher
    
    wait
else
    # Fallback to shell
    /bin/bash --login
fi
