#!/bin/bash
# =============================================================================
# Startup script for ROS 2 Jazzy Desktop Environment
# This script configures VNC and launches supervisord
# =============================================================================

set -e

# ---- Read environment variables with defaults ----
export VNC_RESOLUTION=${VNC_RESOLUTION:-1920x1080}
export VNC_PASSWORD=${VNC_PASSWORD:-student}
export VNC_DEPTH=${VNC_DEPTH:-24}

# ---- Update VNC password if changed via environment ----
mkdir -p /home/student/.vnc
echo "$VNC_PASSWORD" | vncpasswd -f > /home/student/.vnc/passwd
chmod 600 /home/student/.vnc/passwd
chown -R student:student /home/student/.vnc

# ---- Ensure /tmp/.X11-unix exists ----
mkdir -p /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix

# ---- Ensure log directory exists ----
mkdir -p /var/log/supervisor

# ---- Start everything via supervisor ----
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
