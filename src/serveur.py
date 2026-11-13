from flask import Flask, request
import socket, threading, time

app = Flask(__name__)

def annoncer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        sock.sendto(b"SERVEUR", ("255.255.255.255", 5005))
        time.sleep(2)

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    with open("logs.txt", "a") as f:
        f.write(f"Passage: {data['type']} vers {data['direction']}\n")
    return {"ok": True}

if __name__ == '__main__':
    threading.Thread(target=annoncer, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)