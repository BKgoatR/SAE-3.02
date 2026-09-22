from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor


class ZoneSimulation(QWidget):
    def __init__(self, vehicules):
        super().__init__()
        self.vehicules = vehicules
        # Par défaut, on laisse passer les voitures horizontales
        self.feu_NS_vert = False  # Nord/Sud est ROUGE
        self.feu_EO_vert = True  # Est/Ouest est VERT

    def passer_vert(self):
        """L'ambulance approche : elle force son axe au vert et bloque l'autre !"""
        self.feu_NS_vert = True
        self.feu_EO_vert = False
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(100, 200, 100))  # Herbe

        # Routes
        p.fillRect(350, 0, 100, 800, QColor(50, 50, 50))
        p.fillRect(0, 350, 800, 100, QColor(50, 50, 50))

        # Couleurs des feux selon leur axe
        couleur_NS = QColor(0, 255, 0) if self.feu_NS_vert else QColor(255, 0, 0)
        couleur_EO = QColor(0, 255, 0) if self.feu_EO_vert else QColor(255, 0, 0)

        # Dessin des 4 feux aux 4 coins du croisement
        p.setBrush(couleur_NS)
        p.drawEllipse(310, 220, 30, 30)  # Feu Haut (Nord)
        p.drawEllipse(460, 550, 30, 30)  # Feu Bas (Sud)

        p.setBrush(couleur_EO)
        p.drawEllipse(220, 460, 30, 30)  # Feu Gauche (Ouest)
        p.drawEllipse(550, 310, 30, 30)  # Feu Droite (Est)

        # Véhicules
        for v in self.vehicules:
            p.setBrush(QColor(0, 0, 255) if v.prioritaire else QColor(200, 0, 0))
            if v.direction in ["haut", "bas"]:
                p.drawRect(int(v.x), int(v.y), 50, 80)
            else:
                p.drawRect(int(v.x), int(v.y), 80, 50)