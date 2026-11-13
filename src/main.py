import sys, socket, json, threading
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
    try:
        # Création du socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((ip, 5000))

        # Envoi des données
        donnees = {"type": "Ambulance" if v.prioritaire else "Voiture", "direction": v.direction}
        sock.send(json.dumps(donnees).encode('utf-8'))
        sock.close()
    except:
        pass


class FenetrePrincipale(QMainWindow):
    def __init__(self, ip):
        super().__init__()
        self.ip = ip
        self.setGeometry(100, 100, 800, 800)
        self.setFixedSize(800, 800)
        self.zone_dessin = ZoneDessin()
        self.setCentralWidget(self.zone_dessin)

        self.compteur_feux = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.boucle)
        self.timer.start(50)

    def boucle(self):
        self.compteur_feux += 1
        if self.compteur_feux >= 100:
            self.compteur_feux = 0
            for f in self.zone_dessin.liste_feux:
                f.etat = "vert" if f.etat == "rouge" else "rouge"

        for v in self.zone_dessin.liste_vehicules:
            v.vitesse_actuelle = v.vitesse_max

            if not v.prioritaire:
                for f in self.zone_dessin.liste_feux:
                    if f.etat == "rouge":
                        if v.direction == "haut" and 500 <= v.y <= 510:
                            v.vitesse_actuelle = 0
                        elif v.direction == "bas" and 210 <= v.y <= 220:
                            v.vitesse_actuelle = 0
                        elif v.direction == "droite" and 210 <= v.x <= 220:
                            v.vitesse_actuelle = 0
                        elif v.direction == "gauche" and 500 <= v.x <= 510:
                            v.vitesse_actuelle = 0

            v.avancer()

            if (v.direction in ["haut", "bas"] and 390 <= v.y <= 410) or (
                    v.direction in ["gauche", "droite"] and 390 <= v.x <= 410):
                if not v.signal_envoye:
                    v.signal_envoye = True
                    threading.Thread(target=envoyer_log, args=(self.ip, v)).start()

            if v.y < -100:
                v.y, v.signal_envoye = 800, False
            elif v.y > 900:
                v.y, v.signal_envoye = -80, False
            elif v.x > 900:
                v.x, v.signal_envoye = -80, False
            elif v.x < -100:
                v.x, v.signal_envoye = 800, False

        self.zone_dessin.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ip = trouver_serveur()
    fenetre = FenetrePrincipale(ip)
    fenetre.show()
    sys.exit(app.exec_())