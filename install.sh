#!/bin/bash
set -e

APP_NAME="pc-unlock-agent"
INSTALL_DIR="/opt/$APP_NAME"
USER_SERVICE="$HOME/.config/systemd/user/$APP_NAME.service"

echo "Installing $APP_NAME..."

# 1. Create installation directory
sudo mkdir -p "$INSTALL_DIR"
sudo chown "$USER":"$USER" "$INSTALL_DIR"

# 2. Copy files (assuming run from repo root)
sudo cp -r ./* "$INSTALL_DIR"

# 3. Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-gi gir1.2-gtk-3.0 dbus-user-session

# 4. Install Python dependencies
pip install --user -r "$INSTALL_DIR/requirements.txt"

# 5. Create systemd user service
mkdir -p "$HOME/.config/systemd/user"

cat > "$USER_SERVICE" <<EOL
[Unit]
Description=PC Unlock Agent
After=graphical.target

[Service]
Type=simple
ExecStart=/usr/bin/env python3 $INSTALL_DIR/main.py
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
EOL

# 6. Reload systemd and enable service
systemctl --user daemon-reload
systemctl --user enable --now "$APP_NAME.service"

echo "$APP_NAME installed and running!"
echo "Check logs with: journalctl --user -u $APP_NAME.service -f"
