class Vehicule:
    def __init__(self, x, y, prioritaire=False):
        self.x = x
        self.y = y
        self.prioritaire = prioritaire
        self.vitesse = 2
        self.signal_envoye = False

    def avancer(self):
        self.y -= self.vitesse
class Vehicules:
    def __init__(self, x, y, prioritaire=False):
        self.x = x
        self.y = y
        self.prioritaire = prioritaire
        self.vitesse_max = 4 if prioritaire else 2
        self.vitesse_actuelle = self.vitesse_max
        self.signal_envoye = False

    def avancer2(self):
        self.y -= self.vitesse_actuelle
