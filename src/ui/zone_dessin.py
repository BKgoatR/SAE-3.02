from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer


class ZoneSimulation(QWidget):
    def __init__(self, vehicules):
        super().__init__()
        self.vehicules = vehicules

        self.etat_feu_NS = "rouge"
        self.etat_feu_EO = "vert"

        self.timer_feux = QTimer()
        self.timer_feux.timeout.connect(self.gerer_cycle_feux)
        self.timer_feux.start(5000)

    def gerer_cycle_feux(self):
        if self.etat_feu_EO == "vert":
            self.etat_feu_EO = "orange"
            self.timer_feux.start(2000)
        elif self.etat_feu_EO == "orange":
            self.etat_feu_EO = "rouge"
            self.etat_feu_NS = "vert"
            self.timer_feux.start(5000)
        elif self.etat_feu_NS == "vert":
            self.etat_feu_NS = "orange"
            self.timer_feux.start(2000)
        elif self.etat_feu_NS == "orange":
            self.etat_feu_NS = "rouge"
            self.etat_feu_EO = "vert"
            self.timer_feux.start(5000)
        self.update()

    def passer_vert(self, axe):
        """L'ambulance force son propre axe au vert et bloque l'autre"""
        self.timer_feux.stop()
        if axe == "NS":
            self.etat_feu_NS = "vert"
            self.etat_feu_EO = "rouge"
            print("🚨 Priorité absolue accordée à l'axe Nord / Sud !")
        else:
            self.etat_feu_EO = "vert"
            self.etat_feu_NS = "rouge"
            print("🚨 Priorité absolue accordée à l'axe Est / Ouest !")
        self.update()

    def obtenir_couleur(self, etat):
        if etat == "vert": return QColor(0, 255, 0)
        if etat == "orange": return QColor(255, 165, 0)
        return QColor(255, 0, 0)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(100, 200, 100))  # Herbe

        # Routes
        p.fillRect(350, 0, 100, 800, QColor(50, 50, 50))
        p.fillRect(0, 350, 800, 100, QColor(50, 50, 50))

        # --- Feux rapprochés des coins de l'intersection (350 et 450) ---
        p.setBrush(self.obtenir_couleur(self.etat_feu_NS))
        p.drawEllipse(310, 310, 25, 25)  # Feu Nord (au-dessus du carrefour)
        p.drawEllipse(465, 465, 25, 25)  # Feu Sud (en dessous du carrefour)

        p.setBrush(self.obtenir_couleur(self.etat_feu_EO))
        p.drawEllipse(465, 310, 25, 25)  # Feu Est (à droite)
        p.drawEllipse(310, 465, 25, 25)  # Feu Ouest (à gauche)

        # Véhicules
        for v in self.vehicules:
            p.setBrush(QColor(0, 0, 255) if v.prioritaire else QColor(200, 0, 0))
            if v.direction in ["haut", "bas"]:
                p.drawRect(int(v.x), int(v.y), 50, 80)
            else:
                p.drawRect(int(v.x), int(v.y), 80, 50)

    def reprendre_cycle(self):
        """Relance le timer des feux depuis le thread principal"""
        if not self.timer_feux.isActive():
            self.timer_feux.start(5000)
            print("🔄 L'ambulance est passée : reprise automatique du cycle normal des feux !")