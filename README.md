SAE-3.02 — Simulation de Trafic Routier

Projet SAE 3.02 / R3.09

Équipe : TCP&IP (BAKIR Evan & HODZIC Armin)

Groupe : ROM-FA

📋 Présentation du projet

Ce projet est une maquette logicielle simulant un carrefour dans une ville moyenne. L'objectif principal est de permettre à un véhicule d'urgence (prioritaire) de se rendre d'un point A à un point B de manière efficace, tout en réduisant le temps de prise en charge et en diminuant le taux d'accidents routiers.

Le système interagit dynamiquement avec le trafic (feux de circulation, densité, etc.).

Spécifications techniques

Langage : Python 3.10+

Interface Graphique : PyQt5 (Qt)

Communication Réseau : Sockets (Architecture Client/Serveur)

Multitâche : Threads (Gestion asynchrone des entités)

Installation et Lancement

Plusieurs méthodes sont mises à votre disposition pour déployer et lancer le projet selon vos préférences :

(TOUJOURS COMMENCER PAR INSTALLER LE SERVEUR)d

COMMENCER PAR METTRE TOTO EN SUDO :

su -
toto
usermod -aG sudo toto
exit
su - toto
toto

1. Par Tutoriel Vidéo (le plus simple)

Une vidéo disponible sur YouTube explique pas à pas comment déployer le projet de A à Z :

Installation serveur : https://www.youtube.com/watch?v=kVbtVVq9oY0

Installation client : https://www.youtube.com/watch?v=5rNuoh7VzUg

2. Par Guide Textuel

Si vous préférez un tutoriel écrit, deux fichiers de documentation détaillée sont présents à la racine du projet :

installer-serveur.txt (guide d'installation et de configuration de la partie serveur)

installer-client.txt (guide d'installation et de configuration de la partie cliente)

Vous devrez dans tout les cas éxécuter les Scripts Exécutables (ne pas oublier de cocher la case dans les propriétés du fichier)

à éxecuter dans /home/toto/Downloads/SAE-3.02-main

Côté Serveur : ./installer_serveur.sh

Côté Client : ./installer_client.sh
