#!/bin/bash
# Desinstala el driver Maschine MK1. Uso: sudo ./uninstall.sh
set -e
LABEL="io.github.carlos-ssh.maschine-mk1"
USER_NAME=$(stat -f%Su /dev/console)
[ -n "$USER_NAME" ] && launchctl bootout "gui/$(id -u "$USER_NAME")/$LABEL" 2>/dev/null || true
rm -f "/Library/LaunchAgents/$LABEL.plist"
rm -rf /usr/local/libexec/maschine-mk1
pkgutil --forget "$LABEL" 2>/dev/null || true
echo "Maschine MK1 driver desinstalado."
