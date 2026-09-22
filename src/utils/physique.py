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
                        if v.direction == "haut" and 0 < (v.y - autre.y) < 90:
                            v.vitesse_actuelle = 0
                        elif v.direction == "bas" and 0 < (autre.y - v.y) < 90:
                            v.vitesse_actuelle = 0
                        elif v.direction == "droite" and 0 < (autre.x - v.x) < 90:
                            v.vitesse_actuelle = 0
                        elif v.direction == "gauche" and 0 < (v.x - autre.x) < 90:
                            v.vitesse_actuelle = 0

                # Logique des feux : S'arrête si le feu n'est pas "vert" (donc rouge OU orange)
                if not v.prioritaire:
                    if v.direction in ["haut", "bas"] and self.ui.etat_feu_NS != "vert":
                        if (v.direction == "haut" and 460 < v.y < 500) or (v.direction == "bas" and 250 < v.y < 300):
                            v.vitesse_actuelle = 0

                    elif v.direction in ["gauche", "droite"] and self.ui.etat_feu_EO != "vert":
                        if (v.direction == "droite" and 250 < v.x < 300) or (
                                v.direction == "gauche" and 460 < v.x < 500):
                            v.vitesse_actuelle = 0

                # L'ambulance envoie le signal à l'approche du feu
                if v.prioritaire and 550 < v.y < 600 and not v.signal_envoye:
                    envoyer_urgence()
                    v.signal_envoye = True

                v.avancer()

            self.maj_ui.emit()