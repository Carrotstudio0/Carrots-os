#!/bin/sh
# CarrotOS Startup Script - Runs after init
# Located in /usr/lib/carrot/boot-setup.sh

LOG_FILE="/var/log/boot-setup.log"

log() {
    echo "[$(date '+%H:%M:%S')] $@" | tee -a "$LOG_FILE"
}

log "======================================"
log "CarrotOS Boot Setup Starting"
log "======================================"

# Stage 1: Mount system filesystems
log "[Stage 1] Mounting additional filesystems"
mount -t tmpfs tmpfs /tmp > /dev/null 2>&1 || log "  /tmp already mounted"
mount -t tmpfs tmpfs /var/tmp > /dev/null 2>&1 || log "  /var/tmp already mounted"

# Stage 2: Setup overlay system
log "[Stage 2] Setting up overlay filesystem"
if [ -d /overlay/base ] && [ -d /overlay/user ]; then
    log "  Overlay layers detected"
    # Would mount actual overlays here
fi

# Stage 3: Initialize network
log "[Stage 3] Starting network services"
if [ -x /usr/sbin/networkd ]; then
    nohup /usr/sbin/networkd > /var/log/network.log 2>&1 &
    log "  Network daemon started (PID $!)"
fi

# Stage 4: Start display manager
log "[Stage 4] Starting display manager"
sleep 2  # Wait for network

if [ -x /usr/bin/carrot-login ]; then
    nohup /usr/bin/carrot-login > /var/log/login.log 2>&1 &
    log "  Login manager started (PID $!)"
fi

log "======================================"
log "Boot setup complete"
log "======================================"
