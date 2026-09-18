import time
from PyQt5.QtCore import QThread, pyqtSignal
from reseau.client_vehicule import envoyer_urgence


class MoteurPhysique(QThread):
    maj_ui = pyqtSignal()

    def __init__(self, vehicules):
        super().__init__()
        self.vehicules = vehicules

    def run(self):
        while True:
            time.sleep(0.03)
            for v in self.vehicules:
                v.avancer()
                if v.prioritaire and 300 < v.y < 350 and not v.signal_envoye:
                    envoyer_urgence()
                    v.signal_envoye = True

            self.maj_ui.emit()