#!/bin/bash

echo "=== Préparation de la VM 2 : CLIENT (Interface PyQt5) ==="

sudo apt update
sudo apt install -y python3 python3-pip python3-venv unzip
sudo apt install -y libxcb-xinerama0 libqt5gui5 libqt5core5a libqt5widgets5

echo "Décompression du projet..."
unzip -o projet.zip -d projet_carrefour
cd projet_carrefour

echo "Création de l'environnement virtuel..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installation de PyQt5 et Requests..."
pip install PyQt5 requests

echo "====================================================="
echo " INSTALLATION TERMINÉE !"
echo " Pour lancer la simulation :"
echo " 1. cd projet_carrefour"
echo " 2. source .venv/bin/activate"
echo " 3. python3 main.py"
echo "====================================================="