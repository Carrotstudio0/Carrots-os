#!/bin/bash
# CarrotOS Application Installation Script
# Installs all built-in applications and creates wrapper scripts

set -e

APP_DIR="/opt/carrot/apps"
BIN_DIR="/usr/local/bin"
SHARE_DIR="/usr/local/share/carrot"

echo "[*] Installing CarrotOS Applications..."

# Create directories
mkdir -p "$APP_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$SHARE_DIR/applications"
mkdir -p "$SHARE_DIR/icons"

# Install Display Manager
echo "[+] Installing Display Manager..."
cp apps/display-manager/carrot-dm.py "$APP_DIR/carrot-dm"
chmod +x "$APP_DIR/carrot-dm"
ln -sf "$APP_DIR/carrot-dm" "$BIN_DIR/carrot-dm"

# Install File Manager
echo "[+] Installing File Manager..."
cp apps/files/carrot-files.py "$APP_DIR/carrot-files"
chmod +x "$APP_DIR/carrot-files"
ln -sf "$APP_DIR/carrot-files" "$BIN_DIR/carrot-files"

# Install Text Editor
echo "[+] Installing Text Editor..."
cp apps/text-editor/carrot-editor.py "$APP_DIR/carrot-editor"
chmod +x "$APP_DIR/carrot-editor"
ln -sf "$APP_DIR/carrot-editor" "$BIN_DIR/carrot-editor"

# Install Web Browser
echo "[+] Installing Web Browser..."
cp apps/browser/carrot-browser.py "$APP_DIR/carrot-browser"
chmod +x "$APP_DIR/carrot-browser"
ln -sf "$APP_DIR/carrot-browser" "$BIN_DIR/carrot-browser"

# Install Terminal Emulator
echo "[+] Installing Terminal Emulator..."
cp apps/terminal/carrot-terminal.py "$APP_DIR/carrot-terminal"
chmod +x "$APP_DIR/carrot-terminal"
ln -sf "$APP_DIR/carrot-terminal" "$BIN_DIR/carrot-terminal"

# Install Desktop Shell
echo "[+] Installing Desktop Shell..."
cp apps/desktop-shell/carrot-shell.py "$APP_DIR/carrot-shell"
chmod +x "$APP_DIR/carrot-shell"
ln -sf "$APP_DIR/carrot-shell" "$BIN_DIR/carrot-shell"

# Install Settings
echo "[+] Installing Settings Application..."
cp apps/settings/carrot-settings.py "$APP_DIR/carrot-settings"
chmod +x "$APP_DIR/carrot-settings"
ln -sf "$APP_DIR/carrot-settings" "$BIN_DIR/carrot-settings"

# Install Desktop Entry Files
echo "[+] Installing Desktop Entries..."
cat > "$SHARE_DIR/applications/carrot-files.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Version=1.0
Name=Carrot Files
Comment=File Manager
Exec=carrot-files %U
Icon=folder
Categories=System;
StartupNotify=true
EOF

cat > "$SHARE_DIR/applications/carrot-editor.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Version=1.0
Name=Carrot Editor
Comment=Text Editor
Exec=carrot-editor %F
Icon=accessories-text-editor
Categories=Accessories;
StartupNotify=true
EOF

cat > "$SHARE_DIR/applications/carrot-terminal.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Version=1.0
Name=Carrot Terminal
Comment=Terminal Emulator
Exec=carrot-terminal
Icon=utilities-terminal
Categories=System;
EOF

cat > "$SHARE_DIR/applications/carrot-browser.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Version=1.0
Name=Carrot Browser
Comment=Web Browser
Exec=carrot-browser %U
Icon=web-browser
Categories=Internet;
EOF

cat > "$SHARE_DIR/applications/carrot-settings.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Version=1.0
Name=Carrot Settings
Comment=System Settings
Exec=carrot-settings
Icon=preferences-system
Categories=System;
EOF

# Create wrapper script for easier running
cat > "$BIN_DIR/carrot-app" <<'EOF'
#!/bin/bash
# Generic application launcher

APP=$(basename "$0")
if [ "$#" -gt 0 ]; then
    exec "$APP" "$@"
else
    exec "$APP"
fi
EOF
chmod +x "$BIN_DIR/carrot-app"

# Update XDG data
echo "[+] Updating XDG database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$SHARE_DIR/applications" 2>/dev/null || true
fi

echo ""
echo "[✓] Installation Complete!"
echo ""
echo "Installed Applications:"
echo "  • carrot-files    - File Manager"
echo "  • carrot-editor   - Text Editor"
echo "  • carrot-terminal - Terminal Emulator"
echo "  • carrot-browser  - Web Browser"
echo "  • carrot-settings - System Settings"
echo "  • carrot-shell    - Desktop Shell"
echo "  • carrot-dm       - Display Manager"
echo ""
echo "Run any application from terminal:"
echo "  $ carrot-files"
echo "  $ carrot-editor /path/to/file"
echo "  $ carrot-terminal"
echo ""
