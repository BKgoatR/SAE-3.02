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

                # Logique des feux tricolores (pour les civils)
                if not v.prioritaire:
                    # 1. Voitures Nord/Sud regardent le feu NS
                    if v.direction in ["haut", "bas"] and not self.ui.feu_NS_vert:
                        if (v.direction == "haut" and 460 < v.y < 500) or \
                                (v.direction == "bas" and 250 < v.y < 300):
                            v.vitesse_actuelle = 0

                    # 2. Voitures Est/Ouest regardent le feu EO
                    elif v.direction in ["gauche", "droite"] and not self.ui.feu_EO_vert:
                        if (v.direction == "droite" and 250 < v.x < 300):
                            v.vitesse_actuelle = 0

                # L'ambulance envoie le signal à l'approche du feu
                if v.prioritaire and 550 < v.y < 600 and not v.signal_envoye:
                    envoyer_urgence()
                    v.signal_envoye = True

                v.avancer()

            self.maj_ui.emit()