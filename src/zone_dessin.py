from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt
from modeles.vehicules import Vehicule

class ZoneDessin(QWidget):
    def __init__(self):
        super().__init__()
        self.liste_vehicules = [

            Vehicule(430, 700, "haut", prioritaire=False),
            Vehicule(0, 430, "droite", prioritaire=True),

        ]

    def paintEvent(self, event):
        painter = QPainter(self)

        largeur = self.width()
        hauteur = self.height()
        cx = largeur // 2
        cy = hauteur // 2
        largeur_route = 200

        #Fond

        painter.fillRect(0, 0, largeur, hauteur, Qt.darkGreen)

        # Route

        painter.fillRect(cx - largeur_route // 2, 0, largeur_route, hauteur, Qt.darkGray)

        painter.fillRect(0, cy - largeur_route // 2, largeur, largeur_route, Qt.darkGray)

        # Ligne pointillé

        stylo_pointille = QPen(Qt.white, 4, Qt.DashLine)
        painter.setPen(stylo_pointille)

        painter.drawLine(cx, 0, cx, cy - largeur_route // 2) # Voie du haut
        painter.drawLine(cx, cy + largeur_route // 2, cx, hauteur) # Voie du bas

        painter.drawLine(0, cy, cy - largeur_route // 2, cy) # Voie gauche
        painter.drawLine(cx + largeur_route // 2, cy, largeur, cy) # Voie droite

        # DESSIN VEHICULES

        for v in self.liste_vehicules:

            if v.prioritaire :
                painter.setBrush(QBrush(QColor(255, 0, 0)))
            else:
                painter.setBrush(QBrush(QColor(0, 0, 255)))

            painter.setPen(Qt.NoPen)

            longueur = 80
            largeur = 40

            if v.direction in ["haut", "bas"]:
                painter.drawRect(v.x, v.y, largeur, longueur)
            else :
                painter.drawRect(v.x, v.y, longueur, largeur)






