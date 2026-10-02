from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt
from modeles.vehicules import Vehicule
from modeles.feu import Feu

class ZoneDessin(QWidget):
    def __init__(self):
        super().__init__()
        self.liste_vehicules = [
            Vehicule(430, 700, "haut", prioritaire=False),
            Vehicule(0, 430, "droite", prioritaire=True),
        ]

        self.liste_feux = [
            Feu(x=510, y=510, etat="vert"),
            Feu(x=270, y=510, etat="rouge"),
            Feu(x=270, y=270, etat="vert"),
            Feu(x=510, y=270, etat="rouge")
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


        for feu in self.liste_feux:

            if feu.etat == "rouge":
                painter.setBrush(QBrush(QColor(255, 0, 0)))
            elif feu.etat == "vert":
                painter.setBrush(QBrush(QColor(0, 255, 0)))

            painter.setPen(Qt.black)
            painter.drawEllipse(feu.x, feu.y, 20, 20)

