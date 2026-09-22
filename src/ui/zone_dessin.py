from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer


class ZoneSimulation(QWidget):
    def __init__(self, vehicules):
        super().__init__()
        self.vehicules = vehicules

        # On utilise des mots pour intégrer l'état "orange"
        self.etat_feu_NS = "rouge"
        self.etat_feu_EO = "vert"

        self.timer_feux = QTimer()
        self.timer_feux.timeout.connect(self.gerer_cycle_feux)
        self.timer_feux.start(5000)  # Commence avec 5 secondes de vert

    def gerer_cycle_feux(self):
        """Cycle : Vert (5s) -> Orange (2s) -> Rouge"""
        if self.etat_feu_EO == "vert":
            self.etat_feu_EO = "orange"
            self.timer_feux.start(2000)  # L'orange dure 2 secondes

        elif self.etat_feu_EO == "orange":
            self.etat_feu_EO = "rouge"
            self.etat_feu_NS = "vert"
            self.timer_feux.start(5000)  # Le vert dure 5 secondes

        elif self.etat_feu_NS == "vert":
            self.etat_feu_NS = "orange"
            self.timer_feux.start(2000)

        elif self.etat_feu_NS == "orange":
            self.etat_feu_NS = "rouge"
            self.etat_feu_EO = "vert"
            self.timer_feux.start(5000)

        self.update()

    def passer_vert(self):
        """L'ambulance force le feu de sa voie au vert instantanément"""
        self.timer_feux.stop()
        self.etat_feu_NS = "vert"
        self.etat_feu_EO = "rouge"
        self.update()

    def obtenir_couleur(self, etat):
        if etat == "vert": return QColor(0, 255, 0)
        if etat == "orange": return QColor(255, 165, 0)  # Code couleur Orange
        return QColor(255, 0, 0)  # Rouge par défaut

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(100, 200, 100))  # Herbe

        # Routes
        p.fillRect(350, 0, 100, 800, QColor(50, 50, 50))
        p.fillRect(0, 350, 800, 100, QColor(50, 50, 50))

        # Dessin des 4 feux avec la nouvelle fonction de couleur
        p.setBrush(self.obtenir_couleur(self.etat_feu_NS))
        p.drawEllipse(310, 220, 30, 30)  # Haut
        p.drawEllipse(460, 550, 30, 30)  # Bas

        p.setBrush(self.obtenir_couleur(self.etat_feu_EO))
        p.drawEllipse(220, 460, 30, 30)  # Gauche
        p.drawEllipse(550, 310, 30, 30)  # Droite

        # Véhicules
        for v in self.vehicules:
            p.setBrush(QColor(0, 0, 255) if v.prioritaire else QColor(200, 0, 0))
            if v.direction in ["haut", "bas"]:
                p.drawRect(int(v.x), int(v.y), 50, 80)
            else:
                p.drawRect(int(v.x), int(v.y), 80, 50)