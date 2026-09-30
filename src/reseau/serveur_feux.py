import socket
from PyQt5.QtCore import QThread, pyqtSignal


class ServeurEcoute(QThread):
    # On émet un signal avec une chaîne de caractères (ex: "NS" ou "EO")
    urgence = pyqtSignal(str)

    def run(self):
        serveur = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serveur.bind(("127.0.0.1", 5000))

        while True:
            data, addr = serveur.recvfrom(1024)
            message = data.decode('utf-8')

            if "URGENCE" in message:
                if "EO" in message:
                    self.urgence.emit("EO")
                else:
                    self.urgence.emit("NS")