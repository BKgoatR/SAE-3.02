import sqlite3
import datetime


def enregistrer_passage():
    # Se connecte à la base (ou crée le fichier statistiques.db s'il n'existe pas)
    conn = sqlite3.connect("statistiques.db")
    cursor = conn.cursor()

    # Crée la table la première fois
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_urgence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            heure TEXT,
            evenement TEXT
        )
    """)

    # Enregistre le passage
    heure_actuelle = datetime.datetime.now().strftime("%H:%M:%S")
    cursor.execute("INSERT INTO logs_urgence (heure, evenement) VALUES (?, ?)",
                   (heure_actuelle, "Feu vert forcé par ambulance"))

    conn.commit()
    conn.close()

    print("💾 [BDD] Statistiques mises à jour !")