"""
Serveur central de supervision et de journalisation du trafic.

Ce module assure deux responsabilités en parallèle :
1. Diffusion périodique de sa présence sur le réseau local via broadcast UDP (port 5005).
2. Réception multi-threadée des événements de passage envoyés par les clients via TCP (port 5000)
   et écriture persistante dans le fichier de journalisation `logs.txt`.
"""

import socket
import threading
import time
import json


def annoncer():
    """
    Diffuse en boucle un message de découverte UDP sur l'adresse de broadcast du réseau.
    Permet aux clients de localiser automatiquement le serveur sans configuration manuelle d'IP.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        sock.sendto(b"SERVEUR", ("255.255.255.255", 5005))
        time.sleep(2)


def gerer_client(connexion):
    """
    Traite la requête entrante d'un client TCP, enregistre l'événement et ferme le socket.

    Args:
        connexion (socket.socket): Socket client accepté par le serveur principal.
    """
    try:
        # Lecture et décodage de la charge utile JSON transmise par le client
        data = connexion.recv(1024).decode('utf-8')
        if data:
            infos = json.loads(data)
            message = f"Passage: {infos['type']} vers {infos['direction']}"
            print(message)

            # Écriture en mode ajout (append) dans le journal des passages
            with open("logs.txt", "a") as f:
                f.write(message + "\n")
    except:
        # Protection contre les paquets malformés ou déconnexions brutales
        pass
    finally:
        # Libération systématique des ressources réseau
        connexion.close()


if __name__ == '__main__':
    # Thread 1 : L'annonceur UDP (exécuté en démon pour s'arrêter avec le programme principal)
    threading.Thread(target=annoncer, daemon=True).start()

    # Le serveur TCP principal à l'écoute sur toutes les interfaces réseau (port 5000)
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.bind(('0.0.0.0', 5000))
    serveur.listen(5)

    print("Serveur TCP prêt. En attente des véhicules...")

    # Boucle principale d'acceptation des connexions entrantes
    while True:
        connexion, adresse = serveur.accept()
        # Thread 2 : Gestion concurrente de chaque événement client sans bloquer les suivants
        threading.Thread(target=gerer_client, args=(connexion,)).start()