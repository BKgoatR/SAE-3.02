#!/bin/bash
sudo apt update
sudo apt install -y python3 python3-venv unzip
cd Downloads/
unzip -o SAE-3.02-main.zip -d SAE-3.02
cd projet_carrefour
python3 -m venv .venv