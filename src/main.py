"""
Module principal du client de simulation de trafic routier.

Ce module gère la découverte automatique du serveur central via UDP, l'interface
graphique principale sous PyQt5, la boucle de simulation temps réel (feux tricolores,
priorité aux véhicules d'urgence, gestion des collisions et trajectoires) ainsi que
la transmission asynchrone des événements de passage via TCP.
"""

import sys, socket, json, threading, random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from zone_dessin import ZoneDessin


def trouver_serveur():
    """
    Écoute le réseau local en broadcast UDP pour découvrir l'adresse IP du serveur.

    Returns:
        str: L'adresse IPv4 du serveur détecté sur le port 5005.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 5005))

    data, addr = sock.recvfrom(1024)
    return addr[0]


def envoyer_log(ip, v):
    """
    Transmet au serveur central les informations d'un véhicule franchissant le carrefour.

    Exécutée dans un thread dédié afin de ne pas bloquer le rafraîchissement de l'interface.

    Args:
        ip (str): Adresse IP du serveur TCP cible.
        v (Vehicule): Instance du véhicule concerné par l'événement.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((ip, 5000))

        donnees = {"type": "Ambulance" if v.prioritaire else "Voiture", "direction": v.direction}
        sock.send(json.dumps(donnees).encode('utf-8'))
        sock.close()
    except:
        pass


def obtenir_rectangle(v):
    """
    Calcule la boîte englobante (x1, y1, x2, y2) d'un véhicule selon son orientation.
    """
    if v.direction in ["haut", "bas"]:
        return (v.x, v.y, v.x + 40, v.y + 80)
    return (v.x, v.y, v.x + 80, v.y + 40)


def collision_prevue(v, autre_v):
    """
    Vérifie si le prochain déplacement de `v` entre en collision avec `autre_v`.
    """
    nx, ny = v.x, v.y
    if v.direction == "haut":
        ny -= v.vitesse_actuelle
    elif v.direction == "bas":
        ny += v.vitesse_actuelle
    elif v.direction == "gauche":
        nx -= v.vitesse_actuelle
    elif v.direction == "droite":
        nx += v.vitesse_actuelle

    if v.direction in ["haut", "bas"]:
        x1, y1, x2, y2 = nx, ny, nx + 40, ny + 80
    else:
        x1, y1, x2, y2 = nx, ny, nx + 80, ny + 40

    # Ajout d'une marge de sécurité de 12 pixels autour de l'autre véhicule
    ox1, oy1, ox2, oy2 = obtenir_rectangle(autre_v)
    ox1 -= 12
    oy1 -= 12
    ox2 += 12
    oy2 += 12

    return not (x2 <= ox1 or x1 >= ox2 or y2 <= oy1 or y1 >= oy2)


class FenetrePrincipale(QMainWindow):
    """
    Fenêtre principale hébergeant le canevas de simulation et l'ordonnanceur temps réel.
    """

    def __init__(self, ip):
        """
        Initialise la fenêtre graphique et démarre la boucle de simulation.

        Args:
            ip (str): Adresse IP du serveur central pour l'envoi des logs.
        """
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
        """
        Exécute une itération complète de la logique métier et déclenche le rafraîchissement visuel.
        """
        # 1. Cycle des feux (240 temps au total, soit 12 secondes par cycle complet)
        self.compteur_feux = (self.compteur_feux + 1) % 240

        if self.compteur_feux < 90:
            etat_v, etat_h = "vert", "rouge"
        elif self.compteur_feux < 130:
            etat_v, etat_h = "orange", "rouge"
        elif self.compteur_feux < 220:
            etat_v, etat_h = "rouge", "vert"
        else:
            etat_v, etat_h = "rouge", "orange"

        # Feux 0 (bas-droite) et 2 (haut-gauche) contrôlent l'axe vertical
        # Feux 1 (bas-gauche) et 3 (haut-droite) contrôlent l'axe horizontal
        self.zone_dessin.liste_feux[0].etat = etat_v
        self.zone_dessin.liste_feux[2].etat = etat_v
        self.zone_dessin.liste_feux[1].etat = etat_h
        self.zone_dessin.liste_feux[3].etat = etat_h

        # 2. Détection globale de l'état de l'intersection (urgence et congestion)
        alerte_ambulance = False
        carrefour_occupe = False

        for v in self.zone_dessin.liste_vehicules:
            if v.prioritaire and 150 < v.x < 650 and 150 < v.y < 650:
                alerte_ambulance = True
            # Vérifie si un véhicule se trouve déjà à l'intérieur du carré central [300..500]
            x1, y1, x2, y2 = obtenir_rectangle(v)
            if x2 > 305 and x1 < 495 and y2 > 305 and y1 < 495:
                carrefour_occupe = True

        # 3. Calcul des mouvements, priorités et évitements pour chaque véhicule
        for v in self.zone_dessin.liste_vehicules:
            v.vitesse_actuelle = v.vitesse_max
            v.se_range = False

            # --- A. DÉTECTION POUR SE RANGER ---
            if not v.prioritaire:
                for autre_v in self.zone_dessin.liste_vehicules:
                    if autre_v.prioritaire and v.direction == autre_v.direction:
                        dx = autre_v.x - v.x
                        dy = autre_v.y - v.y
                        if v.direction == "haut" and -100 < dy < 180:
                            v.se_range = True
                        elif v.direction == "bas" and -180 < dy < 100:
                            v.se_range = True
                        elif v.direction == "gauche" and -100 < dx < 180:
                            v.se_range = True
                        elif v.direction == "droite" and -180 < dx < 100:
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
                    if not autre_v.prioritaire and getattr(autre_v, 'se_range', False) and v.direction == autre_v.direction:
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

            # --- C. ARRÊT AU FEU (Lignes d'arrêt calibrées sur la bordure du carrefour [300..500]) ---
            if not v.prioritaire:
                # Arrêt voie montante (avant y = 500)
                if v.direction == "haut" and 500 <= v.y <= 512:
                    if etat_v in ["rouge", "orange"] or alerte_ambulance or carrefour_occupe:
                        v.vitesse_actuelle = 0
                # Arrêt voie descendante (avant y + 80 = 300 -> y = 220)
                elif v.direction == "bas" and 208 <= v.y <= 220:
                    if etat_v in ["rouge", "orange"] or alerte_ambulance or carrefour_occupe:
                        v.vitesse_actuelle = 0
                # Arrêt voie vers la droite (avant x + 80 = 300 -> x = 220)
                elif v.direction == "droite" and 208 <= v.x <= 220:
                    if etat_h in ["rouge", "orange"] or alerte_ambulance or carrefour_occupe:
                        v.vitesse_actuelle = 0
                # Arrêt voie vers la gauche (avant x = 500)
                elif v.direction == "gauche" and 500 <= v.x <= 512:
                    if etat_h in ["rouge", "orange"] or alerte_ambulance or carrefour_occupe:
                        v.vitesse_actuelle = 0

            # --- D. ANTI-COLLISION 2D (Avant, arrière et intersections) ---
            if v.vitesse_actuelle > 0:
                for autre_v in self.zone_dessin.liste_vehicules:
                    if v != autre_v and collision_prevue(v, autre_v):
                        # L'ambulance conserve la priorité sauf si un véhicule est juste devant elle sur sa trajectoire
                        if not v.prioritaire or (v.direction == autre_v.direction and not getattr(autre_v, 'se_range', False)):
                            v.vitesse_actuelle = 0
                            break

            # --- E. GESTION DES VIRAGES ---
            if not hasattr(v, 'direction_finale'):
                v.direction_finale = v.direction

            if v.direction != v.direction_finale and v.vitesse_actuelle > 0:
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

            # Mise à jour des coordonnées selon la vitesse calculée
            v.avancer()

            # 4. Envoi des logs (quand le véhicule est au cœur du carrefour)
            if 350 <= v.x <= 450 and 350 <= v.y <= 450:
                if not getattr(v, 'signal_envoye', False):
                    v.signal_envoye = True
                    threading.Thread(target=envoyer_log, args=(self.ip, v)).start()

            # 5. Réapparition aléatoire (Tirage au sort de la destination)
            if v.y < -100 or v.y > 900 or v.x > 900 or v.x < -100:
                v.signal_envoye = False

                v.direction = random.choice(["haut", "bas", "gauche", "droite"])

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