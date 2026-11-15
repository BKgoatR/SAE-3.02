"""
Composant graphique de rendu 2D de l'intersection routière.

Gère l'état initial des entités de la scène (véhicules et feux tricolores) ainsi que
leur dessin vectoriel via QPainter à chaque cycle de rafraîchissement.
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt
from modeles.vehicule import Vehicule
from modeles.feu import Feu


class ZoneDessin(QWidget):
    """
    Widget Qt personnalisé assurant le rendu visuel du carrefour, des véhicules et des feux.
    """

    def __init__(self):
        """
        Initialise le parc de véhicules et positionne les quatre feux tricolores autour du carrefour.
        """
        super().__init__()

        # Initialisation des véhicules actifs sur chacune des 4 voies d'accès
        self.liste_vehicules = [
            Vehicule(430, 700, "haut", prioritaire=False),
            Vehicule(0, 430, "droite", prioritaire=True),
            # --- AJOUT DES 2 VEHICULES MANQUANTS ---
            Vehicule(330, -80, "bas", prioritaire=False),
            Vehicule(800, 330, "gauche", prioritaire=False)
        ]

        # Positionnement des 4 feux de signalisation aux angles de l'intersection
        self.liste_feux = [
            Feu(x=510, y=510, etat="vert"),
            Feu(x=270, y=510, etat="rouge"),
            Feu(x=270, y=270, etat="vert"),
            Feu(x=510, y=270, etat="rouge")
        ]

    def paintEvent(self, event):
        """
        Callback Qt déclenché automatiquement lors d'un appel à `update()` ou d'un redimensionnement.

        Args:
            event (QPaintEvent): Événement de peinture fourni par le moteur graphique Qt.
        """
        painter = QPainter(self)

        # Calcul des repères géométriques centraux du canevas
        largeur = self.width()
        hauteur = self.height()
        cx = largeur // 2
        cy = hauteur // 2
        largeur_route = 200

        # Fond (espaces verts autour de l'intersection)
        painter.fillRect(0, 0, largeur, hauteur, Qt.darkGreen)

        # Route (chaussées verticale et horizontale formant le carrefour en croix)
        painter.fillRect(cx - largeur_route // 2, 0, largeur_route, hauteur, Qt.darkGray)
        painter.fillRect(0, cy - largeur_route // 2, largeur, largeur_route, Qt.darkGray)

        # Ligne pointillé (marquage axial séparant les sens de circulation)
        stylo_pointille = QPen(Qt.white, 4, Qt.DashLine)
        painter.setPen(stylo_pointille)

        painter.drawLine(cx, 0, cx, cy - largeur_route // 2) # Voie du haut
        painter.drawLine(cx, cy + largeur_route // 2, cx, hauteur) # Voie du bas

        painter.drawLine(0, cy, cx - largeur_route // 2, cy) # Voie gauche
        painter.drawLine(cx + largeur_route // 2, cy, largeur, cy) # Voie droite

        # DESSIN VEHICULES
        for v in self.liste_vehicules:
            # Code couleur : rouge pour les véhicules prioritaires (ambulances), bleu pour les usagers standards
            if v.prioritaire:
                painter.setBrush(QBrush(QColor(255, 0, 0)))
            else:
                painter.setBrush(QBrush(QColor(0, 0, 255)))

            painter.setPen(Qt.NoPen)

            longueur = 80
            larg_vehicule = 40

            # Adaptation de l'orientation du rectangle selon l'axe de déplacement
            if v.direction in ["haut", "bas"]:
                painter.drawRect(v.x, v.y, larg_vehicule, longueur)
            else:
                painter.drawRect(v.x, v.y, longueur, larg_vehicule)

        # DESSIN DES FEUX TRICOLORES
        for feu in self.liste_feux:
            if feu.etat == "rouge":
                painter.setBrush(QBrush(QColor(255, 0, 0)))
            elif feu.etat == "vert":
                painter.setBrush(QBrush(QColor(0, 255, 0)))
            # --- AJOUT DU FEU ORANGE ---
            elif feu.etat == "orange":
                painter.setBrush(QBrush(QColor(255, 165, 0)))

            painter.setPen(Qt.black)
            painter.drawEllipse(feu.x, feu.y, 20, 20)