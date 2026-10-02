import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
from zone_dessin import ZoneDessin


class FenetrePrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAE 3.02 - Maquette")
        self.setGeometry(100, 100, 800, 800)
        self.setFixedSize(800, 800)
        self.setWindowIcon(QIcon('croix.png'))


        self.zone_dessin = ZoneDessin()
        self.setCentralWidget(self.zone_dessin)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.boucle)
        self.timer.start(50)

    def boucle(self):

        for voiture in self.zone_dessin.liste_vehicules:
            voiture.avancer()

        self.zone_dessin.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    fenetre = FenetrePrincipale()
    fenetre.show()
    sys.exit(app.exec_())