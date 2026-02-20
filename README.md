# Fashion Price Comparator (Terranova, H&M, OVS, Zara)

Mini app in **Streamlit** per confrontare prezzi di capi simili tra brand fast fashion in una specifica città, filtrando per fascia di prezzo.

## Cosa fa

- Filtra per:
  - città
  - categoria (es. t-shirt, jeans, blazer)
  - fascia di prezzo
  - brand
- Cerca capi "simili" in base al nome del prodotto usando fuzzy matching.
- Mostra:
  - tabella comparativa
  - prezzo medio/min/max per brand
  - differenza di prezzo rispetto al miglior match

## Avvio rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Dataset

Il file `data/sample_items.csv` contiene un dataset demo con città italiane e brand:

- Terranova
- H&M
- OVS
- Zara
- Mango
- Uniqlo

Puoi sostituire il CSV con dati reali mantenendo queste colonne:

- `city`
- `brand`
- `category`
- `item_name`
- `price_eur`
- `url`

## Note

- La similarità è calcolata con `rapidfuzz.fuzz.token_set_ratio` su una stringa normalizzata.
- Non usa scraping automatico: il dataset è di esempio.
