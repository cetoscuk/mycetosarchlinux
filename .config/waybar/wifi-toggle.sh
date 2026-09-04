#!/usr/bin/env bash

PID=$(pgrep -f "wifi-popup.py")

if [ -n "$PID" ]; then
    kill -9 $PID
else
    GDK_BACKEND=x11 python3 "$HOME/.config/waybar/wifi-popup.py" &
fi
