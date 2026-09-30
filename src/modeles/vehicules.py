class Vehicule:
    def __init__(self, x, y, direction="haut", prioritaire=False):
        self.x = x
        self.y = y
        self.direction = direction
        self.prioritaire = prioritaire
        self.vitesse_max = 4 if prioritaire else 2
        self.vitesse_actuelle = self.vitesse_max
        self.signal_envoye = False

    def avancer(self):
        if self.direction == "haut":
            self.y -= self.vitesse_actuelle
        elif self.direction == "bas":
            self.y += self.vitesse_actuelle
        elif self.direction == "gauche":
            self.x -= self.vitesse_actuelle
        elif self.direction == "droite":
            self.x += self.vitesse_actuelle