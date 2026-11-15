"""
Modèle de données représentant un feu de signalisation tricolore.
"""


class Feu:
    """
    Représente un feu tricolore positionné sur la scène avec un état courant.
    """

    def __init__(self, x, y, etat="rouge"):
        self.x = x
        self.y = y
        self.etat = etat