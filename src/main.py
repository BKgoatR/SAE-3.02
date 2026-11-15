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
    # Initialisation d'un socket UDP avec réutilisation d'adresse autorisée
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 5005))

    # Attente bloquante de la trame d'annonce émise par le serveur
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
        # Ouverture d'une connexion TCP éphémère avec un timeout court (1s)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((ip, 5000))

        # Sérialisation des métadonnées du véhicule au format JSON
        donnees = {"type": "Ambulance" if v.prioritaire else "Voiture", "direction": v.direction}
        sock.send(json.dumps(donnees).encode('utf-8'))
        sock.close()
    except:
        # Ignorer silencieusement les erreurs réseau ponctuelles pour préserver la fluidité
        pass


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

        # Configuration géométrique fixe de la fenêtre (800x800 pixels)
        self.setGeometry(100, 100, 800, 800)
        self.setFixedSize(800, 800)

        # Intégration du widget personnalisé responsable du rendu graphique
        self.zone_dessin = ZoneDessin()
        self.setCentralWidget(self.zone_dessin)

        # Initialisation de l'horloge de simulation (rafraîchissement toutes les 50 ms, soit 20 FPS)
        self.compteur_feux = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.boucle)
        self.timer.start(50)

    def boucle(self):
        """
        Exécute une itération complète de la logique métier et déclenche le rafraîchissement visuel.
        """
        # 1. Cycle des feux allongé (240 temps au total, soit 12 secondes par cycle complet)
        self.compteur_feux = (self.compteur_feux + 1) % 240

        if self.compteur_feux < 90:
            etat_v, etat_h = "vert", "rouge"
        elif self.compteur_feux < 130:
            etat_v, etat_h = "orange", "rouge"
        elif self.compteur_feux < 220:
            etat_v, etat_h = "rouge", "vert"
        else:
            etat_v, etat_h = "rouge", "orange"

        # Application des états calculés aux feux verticaux (0, 2) et horizontaux (1, 3)
        self.zone_dessin.liste_feux[0].etat = etat_v
        self.zone_dessin.liste_feux[2].etat = etat_v
        self.zone_dessin.liste_feux[1].etat = etat_h
        self.zone_dessin.liste_feux[3].etat = etat_h

        # 2. Détection globale de l'état de l'intersection (urgence et congestion)
        alerte_ambulance = False
        carrefour_occupe = False

        for v in self.zone_dessin.liste_vehicules:
            # Vérification de la présence d'un véhicule prioritaire dans le périmètre élargi du carrefour
            if v.prioritaire and 200 < v.x < 600 and 200 < v.y < 600:
                alerte_ambulance = True
            # Vérification de l'occupation du cœur de l'intersection pour éviter le blocage
            if 310 < v.x < 490 and 310 < v.y < 490:
                carrefour_occupe = True

        # 3. Calcul des mouvements, priorités et évitements pour chaque véhicule
        for v in self.zone_dessin.liste_vehicules:
            v.vitesse_actuelle = v.vitesse_max
            v.se_range = False

            # --- A. DÉTECTION POUR SE RANGER ---
            # Si un véhicule standard partage la même voie qu'une ambulance proche, il libère le passage
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
            # Ajustement latéral sur la chaussée (rabattement à droite pour les usagers, dépassement au centre pour l'ambulance)
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
                # Vérifie si au moins un véhicule s'est rangé sur sa voie pour engager un dépassement sécurisé
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
            # Les véhicules non prioritaires s'arrêtent à la ligne d'effet si le feu n'est pas vert,
            # si une ambulance approche ou si le carrefour est encombré
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
            # Maintien d'une distance de sécurité de 90 pixels avec le véhicule précédent sur la même voie
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
            # Réalignement orthogonal du véhicule lorsqu'il atteint l'axe de sa voie de destination
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

            # Mise à jour des coordonnées selon la vitesse calculée
            v.avancer()

            # 4. Envoi des logs (Simplifié : quand le véhicule est au cœur du carrefour)
            if 350 <= v.x <= 450 and 350 <= v.y <= 450:
                if not getattr(v, 'signal_envoye', False):
                    v.signal_envoye = True
                    threading.Thread(target=envoyer_log, args=(self.ip, v)).start()

            # 5. Réapparition aléatoire (Tirage au sort de la destination)
            # Dès qu'un véhicule sort de la zone visible, il est réinitialisé sur un nouvel axe d'entrée
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

        # Demande de redessin du widget graphique
        self.zone_dessin.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Découverte réseau préalable avant l'ouverture de l'interface graphique
    ip = trouver_serveur()
    fenetre = FenetrePrincipale(ip)
    fenetre.show()
    sys.exit(app.exec_())