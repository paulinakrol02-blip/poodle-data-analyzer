import sqlite3
import pandas as pd

def zaladuj_do_bazy():
    # Wczytujemy wyczyszczone dane
    df = pd.read_csv("czyste_dane.csv")
    
    # Łączymy się z bazą danych (plik utworzy się sam, jeśli go nie ma)
    conn = sqlite3.connect("poodle_market.db")
    cursor = conn.cursor()
    
    # Tworzymy tabelę SQL (schemat bazy danych - opiszemy go w Rozdziale 4!)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ogloszenia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tytul TEXT,
            cena_surowa TEXT,
            cena_pln REAL,
            lokalizacja_data TEXT,
            miasto TEXT,
            odmiana TEXT,
            umaszczenie TEXT,
            zkwp_fci BOOLEAN,
            badania_genetyczne BOOLEAN,
            link TEXT UNIQUE
        )
    """)
    
    # Zapisujemy wiersze do bazy (INSERT OR IGNORE zapobiega duplikatom po linku)
    dodane = 0
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO ogloszenia 
            (tytul, cena_surowa, cena_pln, lokalizacja_data, miasto, odmiana, umaszczenie, zkwp_fci, badania_genetyczne, link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["tytul"],
            row["cena_surowa"],
            row["cena_pln"] if pd.notna(row["cena_pln"]) else None,
            row["lokalizacja_data"],
            row["miasto"],
            row["odmiana"],
            row["umaszczenie"],
            bool(row["zkwp_fci"]),
            bool(row["badania_genetyczne"]),
            row["link"]
        ))
        if cursor.rowcount > 0:
            dodane += 1

    conn.commit()
    
    # Sprawdzamy łączną liczbę rekordów w bazie
    cursor.execute("SELECT COUNT(*) FROM ogloszenia")
    lacznie = cursor.fetchone()[0]
    
    conn.close()
    print(f"Sukces! Dodano {dodane} nowych ogłoszeń. Łącznie w bazie: {lacznie} rekordów.")

if __name__ == "__main__":
    zaladuj_do_bazy()