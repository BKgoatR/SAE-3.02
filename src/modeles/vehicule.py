"""
Modèle de données représentant un véhicule circulant dans la simulation.
"""


class Vehicule:
    """
    Encapsule la position, la direction, la priorité et la cinématique d'un véhicule.
    """

    def __init__(self, x, y, direction="haut", prioritaire=False):
        """
        Initialise une instance de véhicule avec ses paramètres de déplacement.

        Args:
            x (int): Position initiale sur l'axe X en pixels.
            y (int): Position initiale sur l'axe Y en pixels.
            direction (str, optional): Sens de déplacement ("haut", "bas", "gauche", "droite"). Défaut à "haut".
            prioritaire (bool, optional): Indique s'il s'agit d'un véhicule d'urgence. Défaut à False.
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.prioritaire = prioritaire

        # Définition de la vitesse nominale (double pour les véhicules prioritaires)
        self.vitesse_max = 8 if prioritaire else 4
        self.vitesse_actuelle = self.vitesse_max
        self.signal_envoye = False

    def avancer(self):
        """
        Met à jour les coordonnées (x, y) du véhicule en fonction de sa direction
        et de sa vitesse actuelle pour le pas de temps courant.
        """
        if self.direction == "haut":
            self.y -= self.vitesse_actuelle
        elif self.direction == "bas":
            self.y += self.vitesse_actuelle
        elif self.direction == "gauche":
            self.x -= self.vitesse_actuelle
        elif self.direction == "droite":
            self.x += self.vitesse_actuelle