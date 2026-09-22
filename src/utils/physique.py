import time
from PyQt5.QtCore import QThread, pyqtSignal


class MoteurPhysique(QThread):
    maj_ui = pyqtSignal()
    relancer_feux = pyqtSignal()  # 👈 Nouveau signal pour prévenir l'interface

    def __init__(self, vehicules, ui):
        super().__init__()
        self.vehicules = vehicules
        self.ui = ui
        self.ambulance_etait_la = False

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

                # --- Logique des feux ---
                if not v.prioritaire:
                    if v.direction == "haut" and self.ui.etat_feu_NS != "vert":
                        if 450 <= v.y <= 520:
                            v.vitesse_actuelle = 0

                    elif v.direction == "bas" and self.ui.etat_feu_NS != "vert":
                        nez_y = v.y + 80
                        if 280 <= nez_y <= 350:
                            v.vitesse_actuelle = 0

                    elif v.direction == "droite" and self.ui.etat_feu_EO != "vert":
                        nez_x = v.x + 80
                        if 280 <= nez_x <= 350:
                            v.vitesse_actuelle = 0

                    elif v.direction == "gauche" and self.ui.etat_feu_EO != "vert":
                        if 450 <= v.x <= 520:
                            v.vitesse_actuelle = 0

                v.avancer()

            # --- Nettoyage et gestion du retour à la normale ---
            ambulance_presente = False
            vehicules_a_garder = []

            for v in self.vehicules:
                hors_champ = (v.y < -150 or v.y > 950 or v.x < -150 or v.x > 950)
                if not hors_champ:
                    vehicules_a_garder.append(v)
                    if v.prioritaire:
                        ambulance_presente = True

            self.vehicules.clear()
            self.vehicules.extend(vehicules_a_garder)

            # Détection de la sortie de l'ambulance
            if ambulance_presente:
                self.ambulance_etait_la = True
            else:
                if self.ambulance_etait_la:
                    # L'ambulance vient de partir -> on émet le signal vers le thread principal
                    self.relancer_feux.emit()
                    self.ambulance_etait_la = False

            self.maj_ui.emit()

