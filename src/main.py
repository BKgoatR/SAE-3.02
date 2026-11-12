import sys
import socket
import requests
import threading
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from zone_dessin import ZoneDessin


def trouver_serveur():
    print("Recherche automatique du serveur en cours (patiente 5 secondes max)...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 5005))
    sock.settimeout(5.0)

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if data == b"SERVEUR_CARREFOUR":
                print(f"Serveur trouvé automatiquement à l'adresse : {addr[0]}")
                return addr[0]
    except socket.timeout:
        return None


def envoyer_log_serveur(ip_serveur, vehicule):
    try:
        url = f"http://{ip_serveur}:5000/log_passage"
        donnees = {
            "type_vehicule": "Ambulance" if getattr(vehicule, 'prioritaire', False) else "Voiture",
            "direction": vehicule.direction
        }
        requests.post(url, json=donnees, timeout=1)
    except:
        pass


class FenetrePrincipale(QMainWindow):
    def __init__(self, ip_serveur):
        super().__init__()
        self.ip_serveur = ip_serveur  # On sauvegarde l'IP de la VM 1

        self.setWindowTitle("SAE 3.02 - Maquette Client")
        self.setGeometry(100, 100, 800, 800)
        self.setFixedSize(800, 800)
        self.setWindowIcon(QIcon('feu1.png'))

        self.zone_dessin = ZoneDessin()
        self.setCentralWidget(self.zone_dessin)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.boucle)
        self.timer.start(50)

    def boucle(self):
        for voiture in self.zone_dessin.liste_vehicules:
            voiture.avancer()

            if (voiture.direction in ["haut", "bas"] and voiture.y == 400) or \
                    (voiture.direction in ["gauche", "droite"] and voiture.x == 400):

                if not getattr(voiture, 'signal_envoye', False):
                    voiture.signal_envoye = True
                    threading.Thread(target=envoyer_log_serveur, args=(self.ip_serveur, voiture)).start()

        self.zone_dessin.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ip = trouver_serveur()

    if not ip:
        ip, ok = QInputDialog.getText(None, "Échec Auto", "Serveur non trouvé.\nEntrez l'IP manuellement :",
                                      text="192.168.")
        if not ok or not ip:
            sys.exit()

    fenetre = FenetrePrincipale(ip)
    fenetre.show()
    sys.exit(app.exec_())