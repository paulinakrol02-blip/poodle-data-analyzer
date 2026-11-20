import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://www.olx.pl/zwierzeta/psy/q-pudel/?page="
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

dane = []
liczba_stron = 5

for page in range(1, liczba_stron + 1):
    url = f"{base_url}{page}"
    print(f"Pobieram stronę {page} z {liczba_stron}...")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Błąd na stronie {page}: kod {response.status_code}")
        break
        
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all("div", attrs={"data-testid": "l-card"})
    
    for card in cards:
        title_tag = card.find("a", attrs={"data-testid": "card-title-link"})
        title = title_tag.text.strip() if title_tag else None
        
        raw_link = title_tag["href"] if title_tag and title_tag.has_attr("href") else None
        link = "https://www.olx.pl" + raw_link.split("?")[0] if raw_link else None
        
        price_tag = card.find("p", attrs={"data-testid": "ad-price"})
        price = price_tag.text.strip() if price_tag else None
        
        loc_tag = card.find("p", attrs={"data-testid": "location-date"})
        location_date = loc_tag.text.strip() if loc_tag else None
        
        dane.append({
            "tytul": title,
            "cena_surowa": price,
            "lokalizacja_data": location_date,
            "link": link
        })
    
    time.sleep(2)

df = pd.DataFrame(dane)
przed_czyszczeniem = len(df)
df = df.drop_duplicates(subset=["link"])
po_czyszczeniu = len(df)

df.to_csv("surowe_dane.csv", index=False, encoding="utf-8-sig")
print(f"\nGotowe! Pobrano {przed_czyszczeniem} wpisów, po usunięciu duplikatów zostało {po_czyszczeniu} unikalnych ogłoszeń.")