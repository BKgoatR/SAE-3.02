import sys
from reseau.client_vehicule import envoyer_urgence
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
        self.physique.relancer_feux.connect(self.ui.reprendre_cycle)  # 👈 Connexion du signal ici
        self.physique.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            # On définit les 4 issues possibles avec leur axe associé ("NS" ou "EO")
            voies_urgences = [
                (400, 750, "haut", "NS"),
                (350, -50, "bas", "NS"),
                (-50, 400, "droite", "EO"),
                (800, 350, "gauche", "EO")
            ]

            x, y, direction, axe = random.choice(voies_urgences)

            # Création de l'ambulance
            self.vehicules.append(Vehicule(x, y, direction=direction, prioritaire=True))

            # 🚨 ON FORCE LE FEU AU VERT INSTANTANÉMENT À L'APPARITION
            envoyer_urgence(axe)
            self.ui.passer_vert(axe)

            print(f"🚑 Ambulance générée ({direction}) -> Feu mis au vert immédiatement !")

        elif event.key() == Qt.Key_C:
            voies_civiles = [
                (400, 750, "haut"),
                (350, -50, "bas"),
                (-50, 400, "droite"),
                (800, 350, "gauche")
            ]
            x, y, direction = random.choice(voies_civiles)
            self.vehicules.append(Vehicule(x, y, direction=direction, prioritaire=False))
            print(f"🚗 Voiture civile générée ({direction})")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = App()
    fenetre.show()
    sys.exit(app.exec_())