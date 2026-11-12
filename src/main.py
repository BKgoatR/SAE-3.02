import sys
import requests
import threading
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from zone_dessin import ZoneDessin


# --- FONCTION RÉSEAU (S'exécute en arrière-plan) ---
def envoyer_log_serveur(ip_serveur, vehicule):
    """Envoie les infos de la voiture au serveur via Flask"""
    try:
        url = f"http://{ip_serveur}:5000/log_passage"
        donnees = {
            "type_vehicule": "Ambulance" if getattr(vehicule, 'prioritaire', False) else "Voiture",
            "direction": vehicule.direction
        }
        # timeout=1 permet de ne pas faire laguer la fenêtre si le serveur est éteint
        requests.post(url, json=donnees, timeout=1)
    except:
        pass  # Si le serveur n'est pas lancé, on ignore l'erreur pour ne pas bloquer la simulation


class FenetrePrincipale(QMainWindow):
    def __init__(self, ip_serveur):
        super().__init__()
        self.ip_serveur = ip_serveur  # On stocke l'IP de la VM serveur

        self.setWindowTitle("SAE 3.02 - Maquette Client")
        self.setGeometry(100, 100, 800, 800)
        self.setFixedSize(800, 800)
        self.setWindowIcon(QIcon('feu1.png'))

        self.zone_dessin = ZoneDessin()
        self.setCentralWidget(self.zone_dessin)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.boucle)
        self.timer.start(50)

    def boucle(self):
        for voiture in self.zone_dessin.liste_vehicules:
            voiture.avancer()

            # --- DÉTECTION DU PASSAGE AU MILIEU DU CARREFOUR ---
            if (voiture.direction in ["haut", "bas"] and voiture.y == 400) or \
                    (voiture.direction in ["gauche", "droite"] and voiture.x == 400):

                # On vérifie si on n'a pas déjà envoyé le signal pour cette voiture
                if not getattr(voiture, 'signal_envoye', False):
                    voiture.signal_envoye = True
                    # On envoie le message au serveur dans un processus parallèle pour éviter les saccades
                    threading.Thread(target=envoyer_log_serveur, args=(self.ip_serveur, voiture)).start()

        self.zone_dessin.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Petite boîte de dialogue pour demander l'IP de la VM Serveur au lancement
    ip, ok = QInputDialog.getText(None, "Connexion", "Entrez l'IP du Serveur (VM 1) :", text="192.168.")

    # Si on clique sur OK, on lance la fenêtre avec cette IP
    if ok and ip:
        fenetre = FenetrePrincipale(ip)
        fenetre.show()
        sys.exit(app.exec_())