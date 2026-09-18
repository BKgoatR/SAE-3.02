import socket

def envoyer_urgence():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b"URGENCE", ("127.0.0.1", 5000))
    except Exception as e:
        pass