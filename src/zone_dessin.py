from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt


class ZoneDessin(QWidget):
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        painter = QPainter(self)

        # On récupère la taille de la fenêtre
        largeur = self.width()
        hauteur = self.height()

        # On peint le fond tout en vert
        painter.fillRect(0, 0, largeur, hauteur, QColor(60, 150, 60))