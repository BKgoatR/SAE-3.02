#!/bin/bash
su
toto
apt update
apt install -y python3 python3-pip python3-venv libxcb-xinerama0 libqt5gui5 libqt5core5a libqt5widgets5
cd /Downloads/SAE-3.02/
python3 -m venv .venv
source venv/bin/activate
pip install PyQt5
cd /SAE-3.02-main/src/
python3 main.py