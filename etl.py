import re
import pandas as pd

# 1. EXTRACT: Wczytujemy surowe dane z pliku CSV
df = pd.read_csv("surowe_dane.csv")
print(f"Wczytano surowych ogłoszeń: {len(df)}")

# 2. TRANSFORM: Czyszczenie i wyciąganie cech

# A. Usuwamy mieszańce i hybrydy (np. maltipoo, cockapoo, mix)
slowa_wykluczone = [
    "maltipoo", "cavapoo", "cockapoo", "shihpoo", "bichpoo",
    "labradoodle", "goldendoodle", "aussiedoodle", "bernedoodle",
    "maltidoodle", "mix", "mieszaniec", "krzyżówka"
]
wzorzec_wykluczony = "|".join(slowa_wykluczone)
df = df[~df["tytul"].str.lower().str.contains(wzorzec_wykluczony, na=False)].copy()
print(f"Po odfiltrowaniu mieszańców (np. maltipoo, mix): {len(df)}")

# B. Czyszczenie ceny (wyciągamy samą liczbę)
def wyczysc_cene(cena):
    if pd.isna(cena):
        return None
    tekst = str(cena).lower()
    if "za darmo" in tekst or "zamienię" in tekst:
        return 0.0
    # Usuwamy spacje i szukamy cyfr za pomocą wyrażenia regularnego (regex)
    tekst_bez_spacji = tekst.replace(" ", "")
    dopasowanie = re.search(r"(\d+(?:[.,]\d+)?)", tekst_bez_spacji)
    if dopasowanie:
        return float(dopasowanie.group(1).replace(",", "."))
    return None

df["cena_pln"] = df["cena_surowa"].apply(wyczysc_cene)

# C. Wyciąganie miasta z kolumny 'lokalizacja_data'
def wyciagnij_miasto(tekst):
    if pd.isna(tekst):
        return "Nieznane"
    lokalizacja = str(tekst).split(" - ")[0]
    miasto = lokalizacja.split(",")[0].strip()
    return miasto

df["miasto"] = df["lokalizacja_data"].apply(wyciagnij_miasto)

# D. Rozpoznawanie odmiany wielkościowej pudla na podstawie tytułu
def rozpoznaj_odmiane(tytul):
    if pd.isna(tytul):
        return "Nieokreślona"
    t = str(tytul).lower()
    if "toy" in t or "teacup" in t or "mikro" in t:
        return "Toy"
    elif "miniatu" in t or "mini" in t:
        return "Miniatura"
    elif "średni" in t or "sredni" in t:
        return "Średni"
    elif "duży" in t or "duzy" in t or "królewski" in t or "krolewski" in t or "standard" in t:
        return "Duży"
    return "Nieokreślona"

df["odmiana"] = df["tytul"].apply(rozpoznaj_odmiane)

# E. Rozpoznawanie umaszczenia
def rozpoznaj_kolor(tytul):
    if pd.isna(tytul):
        return "Nieokreślone"
    t = str(tytul).lower()
    if any(k in t for k in ["red", "czerw", "apricot", "morel", "rudy", "rude", "fawn"]):
        return "Red / Apricot"
    elif any(k in t for k in ["czarn", "black"]):
        return "Czarny"
    elif any(k in t for k in ["biał", "bial", "white"]):
        return "Biały"
    elif any(k in t for k in ["brąz", "braz", "brown", "czekolad"]):
        return "Brązowy"
    elif any(k in t for k in ["srebr", "srebny", "silver", "szary"]):
        return "Srebrny"
    elif any(k in t for k in ["phantom", "arlekin", "harlekin"]):
        return "Phantom / Harlekin"
    return "Nieokreślone"

df["umaszczenie"] = df["tytul"].apply(rozpoznaj_kolor)

# F. Dodatkowe cechy kynologiczne (ZKwP/FCI oraz badania genetyczne)
df["zkwp_fci"] = df["tytul"].str.lower().str.contains(r"zkwp|fci", na=False)
df["badania_genetyczne"] = df["tytul"].str.lower().str.contains(r"badani|genetycz", na=False)

# 3. LOAD: Zapisujemy wyczyszczone dane do nowego pliku CSV
df.to_csv("czyste_dane.csv", index=False, encoding="utf-8-sig")

print("\nSukces! Zapisano wyczyszczone dane do pliku czyste_dane.csv")
print("\n--- Podsumowanie odmian ---")
print(df["odmiana"].value_counts())
print("\n--- Średnia cena (bez ofert za 0 zł) wg odmiany ---")
print(df[df["cena_pln"] > 0].groupby("odmiana")["cena_pln"].mean().round(2))