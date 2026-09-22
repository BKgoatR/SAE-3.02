import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt  # <-- AJOUT pour détecter le clavier

from modeles.vehicules import Vehicule
from ui.zone_dessin import ZoneSimulation
from reseau.serveur_feux import ServeurEcoute
from utils.physique import MoteurPhysique


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 800)

        # 1. On retire l'ambulance de la liste de départ
        self.vehicules = [
            Vehicule(400, 500, direction="haut", prioritaire=False),
            Vehicule(100, 400, direction="droite", prioritaire=False),
            Vehicule(350, 100, direction="bas", prioritaire=False)
        ]

        self.ui = ZoneSimulation(self.vehicules)
        self.setCentralWidget(self.ui)

        self.serveur = ServeurEcoute()
        self.serveur.urgence.connect(self.ui.passer_vert)
        self.serveur.start()

        self.physique = MoteurPhysique(self.vehicules, self.ui)
        self.physique.maj_ui.connect(self.ui.update)
        self.physique.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            # Liste des 4 points de départ possibles pour l'ambulance
            voies_urgences = [
                (400, 750, "haut"),  # Vient du Sud (monte)
                (350, -50, "bas"),  # Vient du Nord (descend)
                (-50, 400, "droite"),  # Vient de l'Ouest (va à droite)
                (800, 350, "gauche")  # Vient de l'Est (va à gauche)
            ]

            # On choisit une voie au hasard
            x, y, direction = random.choice(voies_urgences)

            # On crée l'ambulance avec prioritaire=True
            self.vehicules.append(Vehicule(x, y, direction=direction, prioritaire=True))
            print(f"🚑 Ambulance générée en urgence (Direction : {direction}) !")

        elif event.key() == Qt.Key_C:
            # Liste des 4 points de départ pour les civils
            voies_civiles = [
                (400, 750, "haut"),
                (350, -50, "bas"),
                (-50, 400, "droite"),
                (800, 350, "gauche")
            ]

            x, y, direction = random.choice(voies_civiles)
            self.vehicules.append(Vehicule(x, y, direction=direction, prioritaire=False))
            print(f"🚗 Voiture civile générée (Direction : {direction})")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = App()
    fenetre.show()
    sys.exit(app.exec_())