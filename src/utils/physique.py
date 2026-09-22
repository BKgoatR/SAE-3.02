import time
from PyQt5.QtCore import QThread, pyqtSignal
from reseau.client_vehicule import envoyer_urgence


class MoteurPhysique(QThread):
    maj_ui = pyqtSignal()

    def __init__(self, vehicules, ui):
        super().__init__()
        self.vehicules = vehicules
        self.ui = ui

    def run(self):
        while True:
            time.sleep(0.03)

            for v in self.vehicules:
                v.vitesse_actuelle = v.vitesse_max

                # --- Système Anti-collision ---
                for autre in self.vehicules:
                    if v != autre and v.direction == autre.direction:
                        if v.direction == "haut" and 0 < (v.y - autre.y) < 100:
                            v.vitesse_actuelle = 0
                        elif v.direction == "bas" and 0 < (autre.y - v.y) < 100:
                            v.vitesse_actuelle = 0
                        elif v.direction == "droite" and 0 < (autre.x - v.x) < 100:
                            v.vitesse_actuelle = 0
                        elif v.direction == "gauche" and 0 < (v.x - autre.x) < 100:
                            v.vitesse_actuelle = 0

                # --- Logique des feux basée sur le pare-chocs avant ---
                if not v.prioritaire:
                    # 1. Voitures Nord / Sud
                    if v.direction == "haut" and self.ui.etat_feu_NS != "vert":
                        # Si le nez (v.y) a dépassé 450, il est déjà dans l'intersection -> on trace !
                        # Sinon, s'il approche entre 450 et 520, on s'arrête.
                        if 450 <= v.y <= 520:
                            v.vitesse_actuelle = 0

                    elif v.direction == "bas" and self.ui.etat_feu_NS != "vert":
                        # Le nez pour 'bas' est à l'avant (v.y + 80). Ligne d'effet à 350.
                        nez_y = v.y + 80
                        if 280 <= nez_y <= 350:
                            v.vitesse_actuelle = 0

                    # 2. Voitures Est / Ouest
                    elif v.direction == "droite" and self.ui.etat_feu_EO != "vert":
                        # Le nez pour 'droite' est à v.x + 80. Ligne d'effet à 350.
                        nez_x = v.x + 80
                        if 280 <= nez_x <= 350:
                            v.vitesse_actuelle = 0

                    elif v.direction == "gauche" and self.ui.etat_feu_EO != "vert":
                        # Le nez pour 'gauche' est à v.x. Ligne d'effet à 450.
                        if 450 <= v.x <= 520:
                            v.vitesse_actuelle = 0

                # --- Gestion de l'Ambulance ---
                if v.prioritaire and not v.signal_envoye:
                    if (v.direction == "haut" and 500 < v.y < 600) or \
                            (v.direction == "bas" and 200 < v.y < 300) or \
                            (v.direction == "droite" and 200 < v.x < 300) or \
                            (v.direction == "gauche" and 500 < v.x < 600):
                        envoyer_urgence()
                        v.signal_envoye = True

                v.avancer()

            self.maj_ui.emit()