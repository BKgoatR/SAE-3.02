import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

from modeles.vehicules import Vehicule
from ui.zone_dessin import ZoneSimulation
from reseau.serveur_feux import ServeurEcoute
from utils.physique import MoteurPhysique

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 800)

        self.vehicules = [
            Vehicule(400, 500, direction="haut", prioritaire=False),
            Vehicule(400, 800, direction="haut", prioritaire=True),  # Ambulance

            Vehicule(100, 400, direction="droite", prioritaire=False),

            Vehicule(350, 100, direction="bas", prioritaire=False)
        ]

        self.ui = ZoneSimulation(self.vehicules)
        self.setCentralWidget(self.ui)

        self.serveur = ServeurEcoute()
        self.serveur.urgence.connect(self.ui.passer_vert)
        self.serveur.start()

        # 2. On passe l'UI au moteur pour qu'il connaisse la couleur du feu
        self.physique = MoteurPhysique(self.vehicules, self.ui)
        self.physique.maj_ui.connect(self.ui.update)
        self.physique.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = App()
    fenetre.show()
    sys.exit(app.exec_())