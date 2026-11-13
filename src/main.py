import sys, socket, json, threading, random
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((ip, 5000))
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
        # 1. Cycle des feux allongé (240 temps au total)
        self.compteur_feux = (self.compteur_feux + 1) % 240

        if self.compteur_feux < 90:
            etat_v, etat_h = "vert", "rouge"
        elif self.compteur_feux < 130:
            etat_v, etat_h = "orange", "rouge"
        elif self.compteur_feux < 220:
            etat_v, etat_h = "rouge", "vert"
        else:
            etat_v, etat_h = "rouge", "orange"

        self.zone_dessin.liste_feux[0].etat = etat_v
        self.zone_dessin.liste_feux[2].etat = etat_v
        self.zone_dessin.liste_feux[1].etat = etat_h
        self.zone_dessin.liste_feux[3].etat = etat_h

        # 2. Détection globale
        alerte_ambulance = False
        carrefour_occupe = False

        for v in self.zone_dessin.liste_vehicules:
            if v.prioritaire and 200 < v.x < 600 and 200 < v.y < 600:
                alerte_ambulance = True
            if 310 < v.x < 490 and 310 < v.y < 490:
                carrefour_occupe = True

        # 3. Mouvement et Arrêts
        for v in self.zone_dessin.liste_vehicules:
            v.vitesse_actuelle = v.vitesse_max
            v.se_range = False

            # --- A. DÉTECTION POUR SE RANGER ---
            if not v.prioritaire:
                for autre_v in self.zone_dessin.liste_vehicules:
                    if autre_v.prioritaire and v.direction == autre_v.direction:
                        dx = autre_v.x - v.x
                        dy = autre_v.y - v.y
                        if v.direction == "haut" and -80 < dy < 150:
                            v.se_range = True
                        elif v.direction == "bas" and -150 < dy < 80:
                            v.se_range = True
                        elif v.direction == "gauche" and -80 < dx < 150:
                            v.se_range = True
                        elif v.direction == "droite" and -150 < dx < 80:
                            v.se_range = True

            # --- B. DÉCALAGE VISUEL OPTIMISÉ ---
            if not v.prioritaire:
                if getattr(v, 'se_range', False):
                    if v.direction == "haut":
                        v.x = 460
                    elif v.direction == "bas":
                        v.x = 300
                    elif v.direction == "gauche":
                        v.y = 300
                    elif v.direction == "droite":
                        v.y = 460
                else:
                    if v.direction == "haut":
                        v.x = 430
                    elif v.direction == "bas":
                        v.x = 330
                    elif v.direction == "gauche":
                        v.y = 330
                    elif v.direction == "droite":
                        v.y = 430
            else:
                ambulance_doublage = False
                for autre_v in self.zone_dessin.liste_vehicules:
                    if not autre_v.prioritaire and getattr(autre_v, 'se_range',
                                                           False) and v.direction == autre_v.direction:
                        ambulance_doublage = True

                if ambulance_doublage:
                    if v.direction == "haut":
                        v.x = 400
                    elif v.direction == "bas":
                        v.x = 360
                    elif v.direction == "gauche":
                        v.y = 360
                    elif v.direction == "droite":
                        v.y = 400
                else:
                    if v.direction == "haut":
                        v.x = 430
                    elif v.direction == "bas":
                        v.x = 330
                    elif v.direction == "gauche":
                        v.y = 330
                    elif v.direction == "droite":
                        v.y = 430

            # --- C. ARRÊT AU FEU ---
            if not v.prioritaire:
                for f in self.zone_dessin.liste_feux:
                    if f.etat in ["rouge", "orange"] or alerte_ambulance or carrefour_occupe:
                        if v.direction == "haut" and f.x == 510 and f.y == 510 and 500 <= v.y <= 510:
                            v.vitesse_actuelle = 0
                        elif v.direction == "bas" and f.x == 270 and f.y == 270 and 210 <= v.y <= 220:
                            v.vitesse_actuelle = 0
                        elif v.direction == "droite" and f.x == 270 and f.y == 510 and 210 <= v.x <= 220:
                            v.vitesse_actuelle = 0
                        elif v.direction == "gauche" and f.x == 510 and f.y == 270 and 500 <= v.x <= 510:
                            v.vitesse_actuelle = 0

            # --- D. ANTI-COLLISION ARRIÈRE ---
            for autre_v in self.zone_dessin.liste_vehicules:
                if v != autre_v and v.direction == autre_v.direction:
                    if not getattr(autre_v, 'se_range', False):
                        dx = autre_v.x - v.x
                        dy = autre_v.y - v.y
                        if v.direction == "haut" and -90 < dy < 0:
                            v.vitesse_actuelle = 0
                        elif v.direction == "bas" and 0 < dy < 90:
                            v.vitesse_actuelle = 0
                        elif v.direction == "gauche" and -90 < dx < 0:
                            v.vitesse_actuelle = 0
                        elif v.direction == "droite" and 0 < dx < 90:
                            v.vitesse_actuelle = 0

            # --- E. GESTION DES VIRAGES (NOUVEAU) ---
            if not hasattr(v, 'direction_finale'):
                v.direction_finale = v.direction

            if v.direction != v.direction_finale:
                if v.direction == "haut":
                    if v.direction_finale == "droite" and v.y <= 430:
                        v.direction = "droite"; v.y = 430
                    elif v.direction_finale == "gauche" and v.y <= 330:
                        v.direction = "gauche"; v.y = 330
                elif v.direction == "bas":
                    if v.direction_finale == "droite" and v.y >= 430:
                        v.direction = "droite"; v.y = 430
                    elif v.direction_finale == "gauche" and v.y >= 330:
                        v.direction = "gauche"; v.y = 330
                elif v.direction == "droite":
                    if v.direction_finale == "haut" and v.x >= 430:
                        v.direction = "haut"; v.x = 430
                    elif v.direction_finale == "bas" and v.x >= 330:
                        v.direction = "bas"; v.x = 330
                elif v.direction == "gauche":
                    if v.direction_finale == "haut" and v.x <= 430:
                        v.direction = "haut"; v.x = 430
                    elif v.direction_finale == "bas" and v.x <= 330:
                        v.direction = "bas"; v.x = 330

            v.avancer()

            # 4. Envoi des logs (Simplifié : quand le véhicule est au cœur du carrefour)
            if 350 <= v.x <= 450 and 350 <= v.y <= 450:
                if not getattr(v, 'signal_envoye', False):
                    v.signal_envoye = True
                    threading.Thread(target=envoyer_log, args=(self.ip, v)).start()

            # 5. Réapparition aléatoire (Tirage au sort de la destination)
            if v.y < -100 or v.y > 900 or v.x > 900 or v.x < -100:
                v.signal_envoye = False

                # On choisit d'où la voiture arrive
                v.direction = random.choice(["haut", "bas", "gauche", "droite"])

                # On choisit où elle veut aller (en interdisant de repartir par où elle est arrivée)
                choix_possibles = ["haut", "bas", "gauche", "droite"]
                if v.direction == "haut":
                    choix_possibles.remove("bas")
                elif v.direction == "bas":
                    choix_possibles.remove("haut")
                elif v.direction == "gauche":
                    choix_possibles.remove("droite")
                elif v.direction == "droite":
                    choix_possibles.remove("gauche")

                v.direction_finale = random.choice(choix_possibles)

                # On replace la voiture à son point de départ
                if v.direction == "haut":
                    v.x, v.y = 430, 800
                elif v.direction == "bas":
                    v.x, v.y = 330, -80
                elif v.direction == "droite":
                    v.x, v.y = -80, 430
                elif v.direction == "gauche":
                    v.x, v.y = 800, 330

        self.zone_dessin.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ip = trouver_serveur()
    fenetre = FenetrePrincipale(ip)
    fenetre.show()
    sys.exit(app.exec_())