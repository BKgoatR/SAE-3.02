import sys, socket, requests, threading
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from zone_dessin import ZoneDessin


def trouver_serveur():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 5005))
    data, addr = sock.recvfrom(1024)
    return addr[0]


def envoyer_log(ip, v):
    requests.post(f"http://{ip}:5000/log",
                  json={"type": "Ambulance" if v.prioritaire else "Voiture", "direction": v.direction})


class FenetrePrincipale(QMainWindow):
    def __init__(self, ip):
        super().__init__()
        self.ip = ip
        self.setGeometry(100, 100, 800, 800)
        self.setFixedSize(800, 800)
        self.zone_dessin = ZoneDessin()
        self.setCentralWidget(self.zone_dessin)

        self.compteur_feux = 0  # Compteur pour le timer des feux

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.boucle)
        self.timer.start(50)

    def boucle(self):
        # 1. Gestion des feux (changement toutes les 100 boucles = 5 secondes)
        self.compteur_feux += 1
        if self.compteur_feux >= 100:
            self.compteur_feux = 0
            for f in self.zone_dessin.liste_feux:
                f.etat = "vert" if f.etat == "rouge" else "rouge"

        # 2. Gestion des véhicules
        for v in self.zone_dessin.liste_vehicules:
            v.vitesse_actuelle = v.vitesse_max

            if not v.prioritaire:
                for f in self.zone_dessin.liste_feux:
                    if f.etat == "rouge":
                        if v.direction == "haut" and 500 <= v.y <= 510:
                            v.vitesse_actuelle = 0
                        elif v.direction == "droite" and 210 <= v.x <= 220:
                            v.vitesse_actuelle = 0

            v.avancer()

            # Envoi des logs au milieu
            if (v.direction in ["haut", "bas"] and 390 <= v.y <= 410) or (
                    v.direction in ["gauche", "droite"] and 390 <= v.x <= 410):
                if not v.signal_envoye:
                    v.signal_envoye = True
                    threading.Thread(target=envoyer_log, args=(self.ip, v)).start()

            # Réapparition si sortie d'écran
            if v.y < -100 or v.x > 900:
                if v.direction == "haut":
                    v.y = 800
                elif v.direction == "droite":
                    v.x = -80
                v.signal_envoye = False

        self.zone_dessin.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ip = trouver_serveur()
    fenetre = FenetrePrincipale(ip)
    fenetre.show()
    sys.exit(app.exec_())