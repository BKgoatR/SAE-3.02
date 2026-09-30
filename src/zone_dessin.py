from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt


class ZoneDessin(QWidget):
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        painter = QPainter(self)

        largeur = self.width()
        hauteur = self.height()
        cx = largeur // 2
        cy = hauteur // 2
        largeur_route = 200

        painter.fillRect(0, 0, largeur, hauteur, QColor(60, 150, 60))

        painter.fillRect(cx - largeur_route // 2, 0, largeur_route, hauteur, Qt.black)

        painter.fillRect(0, cy - largeur_route // 2, largeur, largeur_route, Qt.black)