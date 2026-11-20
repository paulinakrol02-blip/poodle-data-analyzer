import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# Konfiguracja strony (tytuł w zakładce przeglądarki i szeroki układ)
st.set_page_config(page_title="Analizator Rynku Pudli", page_icon="🐩", layout="wide")

# Funkcja wczytująca dane z bazy SQLite
@st.cache_data
def wczytaj_dane():
    conn = sqlite3.connect("poodle_market.db")
    df = pd.read_sql_query("SELECT * FROM ogloszenia", conn)
    conn.close()
    return df

df = wczytaj_dane()

# Nagłówek aplikacji
st.title("🐩 Analizator Rynku Kynologicznego — Rasa Pudel")
st.markdown("Interaktywny dashboard analityczny oparty na danych z portalu OLX.")

# --- PANEL BOCZNY (FILTRY) ---
st.sidebar.header("Filtry danych")

# Filtr: pomiń ogłoszenia za 0 zł ("Za darmo" / "Zamienię")
tylko_platne = st.sidebar.checkbox("Ukryj oferty za 0 zł (Za darmo)", value=True)
if tylko_platne:
    df = df[df["cena_pln"] > 0]

# Filtr: Odmiana wielkościowa
dostepne_odmiany = sorted(df["odmiana"].dropna().unique())
wybrane_odmiany = st.sidebar.multiselect("Odmiana wielkościowa:", dostepne_odmiany, default=dostepne_odmiany)

# Filtr: Umaszczenie
dostepne_kolory = sorted(df["umaszczenie"].dropna().unique())
wybrane_kolory = st.sidebar.multiselect("Umaszczenie:", dostepne_kolory, default=dostepne_kolory)

# Filtr: Tylko ZKwP / FCI
tylko_zkwp = st.sidebar.checkbox("Tylko ogłoszenia z ZKwP / FCI w tytule", value=False)

# Aplikowanie filtrów
df_filtered = df[
    (df["odmiana"].isin(wybrane_odmiany)) &
    (df["umaszczenie"].isin(wybrane_kolory))
]
if tylko_zkwp:
    df_filtered = df_filtered[df_filtered["zkwp_fci"] == 1]

# --- GŁÓWNE WSKAŹNIKI (KPI) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Liczba ogłoszeń", len(df_filtered))
col2.metric("Średnia cena", f"{df_filtered['cena_pln'].mean():,.0f} zł" if len(df_filtered) > 0 else "Brak")
col3.metric("Mediana ceny", f"{df_filtered['cena_pln'].median():,.0f} zł" if len(df_filtered) > 0 else "Brak")
udzial_zkwp = (df_filtered["zkwp_fci"].mean() * 100) if len(df_filtered) > 0 else 0
col4.metric("Udział ofert ZKwP/FCI", f"{udzial_zkwp:.1f}%")

st.divider()

# --- WYKRESY ---
if len(df_filtered) > 0:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Rozkład cen wg odmiany wielkościowej")
        fig_box = px.box(
            df_filtered,
            x="odmiana",
            y="cena_pln",
            color="odmiana",
            labels={"odmiana": "Odmiana", "cena_pln": "Cena (PLN)"},
            points="all"
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with c2:
        st.subheader("Liczba ogłoszeń wg umaszczenia")
        kolory_count = df_filtered["umaszczenie"].value_counts().reset_index()
        kolory_count.columns = ["umaszczenie", "liczba"]
        fig_bar = px.bar(
            kolory_count,
            x="umaszczenie",
            y="liczba",
            color="umaszczenie",
            labels={"umaszczenie": "Umaszczenie", "liczba": "Liczba ofert"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABELA Z DANYMI ---
    st.subheader("Przegląd ogłoszeń")
    st.dataframe(
        df_filtered[["tytul", "cena_pln", "odmiana", "umaszczenie", "miasto", "zkwp_fci", "badania_genetyczne", "link"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Brak ogłoszeń spełniających wybrane kryteria.")