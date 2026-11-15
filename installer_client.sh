#!/bin/bash
sudo sed -i 's|http://deb.debian.org/debian|http://ftp.fr.debian.org/debian|g' /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null
sudo systemctl stop packagekit
sudo apt update
sudo apt install -y python3 python3-pip python3-venv libxcb-xinerama0 libqt5gui5 libqt5core5a libqt5widgets5 qtwayland5

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

./venv/bin/pip install PyQt5

cd src/
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export WAYLAND_DISPLAY=wayland-0
export QT_QPA_PLATFORM=wayland
../venv/bin/python3 main.py