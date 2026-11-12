#!/bin/bash

echo "=== Préparation de la VM 1 : SERVEUR (API & Logs) ==="

sudo apt update
sudo apt install -y python3 python3-pip python3-venv unzip net-tools

echo "Décompression du projet..."
unzip -o projet.zip -d projet_carrefour
cd projet_carrefour

echo "Création de l'environnement virtuel..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installation de Flask..."
pip install flask

echo "====================================================="
echo " INSTALLATION TERMINÉE !"
echo " Pour lancer le serveur :"
echo " 1. cd projet_carrefour"
echo " 2. source .venv/bin/activate"
echo " 3. python3 serveur.py"
echo "====================================================="
echo "Rappel : L'adresse IP de cette machine est :"
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1'