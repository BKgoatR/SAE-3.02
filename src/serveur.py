import socket
import threading
import time
import json


def annoncer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        sock.sendto(b"SERVEUR", ("255.255.255.255", 5005))
        time.sleep(2)


def gerer_client(connexion):
    try:
        data = connexion.recv(1024).decode('utf-8')
        if data:
            infos = json.loads(data)
            with open("logs.txt", "a") as f:
                f.write(f"Passage: {infos['type']} vers {infos['direction']}\n")
    except:
        pass
    finally:
        connexion.close()


if __name__ == '__main__':
    # Thread 1 : L'annonceur UDP
    threading.Thread(target=annoncer, daemon=True).start()

    # Le serveur TCP principal
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.bind(('0.0.0.0', 5000))
    serveur.listen(5)

    print("Serveur TCP prêt. En attente des véhicules...")

    while True:
        connexion, adresse = serveur.accept()
        # Thread 2 : Gestion de la réception du message
        threading.Thread(target=gerer_client, args=(connexion,)).start()