import sqlite3
import datetime


def enregistrer_passage():
    conn = sqlite3.connect("statistiques.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_urgence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            heure TEXT,
            evenement TEXT
        )
    """)

    heure_actuelle = datetime.datetime.now().strftime("%H:%M:%S")
    cursor.execute("INSERT INTO logs_urgence (heure, evenement) VALUES (?, ?)",
                   (heure_actuelle, "Feu vert forcé par ambulance"))

    conn.commit()
    conn.close()

    print("💾 [BDD] Statistiques mises à jour !")