from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor

class ZoneSimulation(QWidget):
    def __init__(self, vehicules):
        super().__init__()
        self.vehicules = vehicules
        self.feu_vert = False

    def passer_vert(self):
        self.feu_vert = True

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(100, 200, 100)) # Herbe
        p.fillRect(350, 0, 100, 800, QColor(50, 50, 50)) # Route

        # Feu tricolore
        p.setBrush(QColor(0, 255, 0) if self.feu_vert else QColor(255, 0, 0))
        p.drawEllipse(460, 250, 30, 30)

        # Véhicules
        for v in self.vehicules:
            p.setBrush(QColor(0, 0, 255) if v.prioritaire else QColor(200, 0, 0))
            p.drawRect(375, int(v.y), 50, 80)