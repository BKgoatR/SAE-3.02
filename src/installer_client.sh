#!/bin/bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv unzip libxcb-xinerama0 libqt5gui5 libqt5core5a libqt5widgets5
unzip -o projet.zip -d projet_carrefour
cd projet_carrefour
python3 -m venv .venv
source .venv/bin/activate
pip install PyQt5 requests