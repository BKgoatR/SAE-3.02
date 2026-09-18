import socket
from PyQt5.QtCore import QThread, pyqtSignal


class ServeurEcoute(QThread):
    urgence = pyqtSignal()

    def run(self):
        serveur = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serveur.bind(("127.0.0.1", 5000))

        while True:
            donnees, _ = serveur.recvfrom(1024)
            if donnees.decode() == "URGENCE":
                self.urgence.emit()