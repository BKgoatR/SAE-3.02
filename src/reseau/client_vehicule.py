import socket

def envoyer_urgence(axe="NS"):
    """Envoie un signal UDP en précisant l'axe ('NS' ou 'EO')"""
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # On envoie par exemple le texte "URGENCE_NS" ou "URGENCE_EO"
    message = f"URGENCE_{axe}".encode('utf-8')
    client.sendto(message, ("127.0.0.1", 5000))
    client.close()