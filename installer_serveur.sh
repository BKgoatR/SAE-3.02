#!/bin/bash
su
toto
apt update
apt install -y python3 python3-venv
cd Downloads/SAE-3.02-main/SAE-3.02-main/
python3 serveur.py
