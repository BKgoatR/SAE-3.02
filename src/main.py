import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

from modeles.vehicules import Vehicule
from ui.zone_dessin import ZoneSimulation
from reseau.serveur_feux import ServeurEcoute
from moteur.physique import MoteurPhysique


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 800)

        self.vehicules = [Vehicule(375, 800, prioritaire=True)]

        self.ui = ZoneSimulation(self.vehicules)
        self.setCentralWidget(self.ui)

        self.serveur = ServeurEcoute()
        self.serveur.urgence.connect(self.ui.passer_vert)
        self.serveur.start()

        self.physique = MoteurPhysique(self.vehicules)
        self.physique.maj_ui.connect(self.ui.update)
        self.physique.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = App()
    fenetre.show()
    sys.exit(app.exec_())