from flask import Flask, request
from datetime import datetime
import socket
import threading
import time

app = Flask(__name__)


def annoncer_presence():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        try:
            sock.sendto(b"SERVEUR_CARREFOUR", ("255.255.255.255", 5005))
        except:
            pass
        time.sleep(2)


@app.route('/log_passage', methods=['POST'])
def log_passage():
    data = request.json
    heure = datetime.now().strftime("%H:%M:%S")
    ligne = f"[{heure}] Passage d'un(e) {data['type_vehicule']} vers la {data['direction']}.\n"

    print(ligne.strip())
    with open("logs_carrefour.txt", "a", encoding="utf-8") as f:
        f.write(ligne)

    return {"statut": "ok"}


if __name__ == '__main__':
    print("=== Démarrage du Serveur du Carrefour ===")

    threading.Thread(target=annoncer_presence, daemon=True).start()

    print("Diffusion de l'IP en cours... En attente des véhicules.")
    app.run(host='0.0.0.0', port=5000)