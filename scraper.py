import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.olx.pl/zwierzeta/psy/q-pudel/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("div", attrs={"data-testid": "l-card"})
    
    # Pusta lista, do której będziemy wrzucać kolejne ogłoszenia jako słowniki
    dane = []
    
    for card in cards:
        title_tag = card.find("a", attrs={"data-testid": "card-title-link"})
        title = title_tag.text.strip() if title_tag else None
        
        # Wyciągamy link i od razu ucinamy końcówkę po znaku "?"
        raw_link = title_tag["href"] if title_tag and title_tag.has_attr("href") else None
        link = "https://www.olx.pl" + raw_link.split("?")[0] if raw_link else None
        
        price_tag = card.find("p", attrs={"data-testid": "ad-price"})
        price = price_tag.text.strip() if price_tag else None
        
        # Wyciągamy lokalizację i datę
        loc_tag = card.find("p", attrs={"data-testid": "location-date"})
        location_date = loc_tag.text.strip() if loc_tag else None
        
        dane.append({
            "tytul": title,
            "cena_surowa": price,
            "lokalizacja_data": location_date,
            "link": link
        })
    
    # Zamieniamy listę na tabelę (DataFrame) i zapisujemy do pliku CSV
    df = pd.DataFrame(dane)
    df.to_csv("surowe_dane.csv", index=False, encoding="utf-8-sig")
    print(f"Sukces! Zapisano {len(df)} ogłoszeń do pliku surowe_dane.csv")
    print(df.head()) # Pokazuje pierwsze 5 wierszy w terminalu
else:
    print("Błąd połączenia:", response.status_code)