import re
import unicodedata

import pandas as pd
import streamlit as st
from rapidfuzz import fuzz

st.set_page_config(page_title="Confronto Prezzi Fast Fashion", layout="wide")


@st.cache_data
def load_data(path: str = "data/sample_items.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    expected_cols = {"city", "brand", "category", "item_name", "price_eur", "url"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Colonne mancanti nel CSV: {sorted(missing)}")
    df["price_eur"] = pd.to_numeric(df["price_eur"], errors="coerce")
    df = df.dropna(subset=["price_eur"]).copy()
    return df


def normalize_text(value: str) -> str:
    value = str(value).lower().strip()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def compute_similarity(reference: str, candidate: str) -> int:
    return int(fuzz.token_set_ratio(normalize_text(reference), normalize_text(candidate)))


def best_matches(df: pd.DataFrame, reference_item: str, min_similarity: int) -> pd.DataFrame:
    out = df.copy()
    out["similarity"] = out["item_name"].apply(lambda item: compute_similarity(reference_item, item))
    out = out[out["similarity"] >= min_similarity].copy()
    out = out.sort_values(["similarity", "price_eur"], ascending=[False, True])
    return out


def main() -> None:
    st.title("👕 Comparatore Prezzi Abbigliamento Fast Fashion")
    st.caption("Confronta capi simili per città, fascia prezzo e brand (Terranova, H&M, OVS, Zara e competitor).")

    df = load_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.selectbox("Città", sorted(df["city"].unique()))
    with col2:
        category = st.selectbox("Categoria", sorted(df["category"].unique()))
    with col3:
        selected_brands = st.multiselect(
            "Brand",
            sorted(df["brand"].unique()),
            default=["Terranova", "H&M", "OVS", "Zara"],
        )

    filtered = df[(df["city"] == city) & (df["category"] == category)].copy()
    if selected_brands:
        filtered = filtered[filtered["brand"].isin(selected_brands)]

    if filtered.empty:
        st.warning("Nessun prodotto disponibile per i filtri scelti.")
        return

    min_price = float(filtered["price_eur"].min())
    max_price = float(filtered["price_eur"].max())
    price_range = st.slider(
        "Fascia di prezzo (€)",
        min_value=float(min_price),
        max_value=float(max_price),
        value=(float(min_price), float(max_price)),
        step=1.0,
    )

    filtered = filtered[(filtered["price_eur"] >= price_range[0]) & (filtered["price_eur"] <= price_range[1])]
    if filtered.empty:
        st.warning("Nessun prodotto nella fascia di prezzo selezionata.")
        return

    reference_item = st.selectbox("Capo di riferimento", filtered["item_name"].tolist())
    min_similarity = st.slider("Similarità minima (%)", min_value=0, max_value=100, value=60, step=5)

    result = best_matches(filtered, reference_item, min_similarity)
    if result.empty:
        st.info("Nessun capo supera la soglia di similarità.")
        return

    cheapest_price = result["price_eur"].min()
    result["delta_vs_best"] = (result["price_eur"] - cheapest_price).round(2)

    st.subheader("Confronto capi simili")
    st.dataframe(
        result[["brand", "item_name", "price_eur", "similarity", "delta_vs_best", "url"]]
        .rename(
            columns={
                "brand": "Brand",
                "item_name": "Prodotto",
                "price_eur": "Prezzo (€)",
                "similarity": "Similarità (%)",
                "delta_vs_best": "Differenza dal migliore (€)",
                "url": "Link",
            }
        )
        .reset_index(drop=True),
        use_container_width=True,
    )

    summary = (
        result.groupby("brand", as_index=False)
        .agg(prezzo_medio=("price_eur", "mean"), prezzo_min=("price_eur", "min"), prezzo_max=("price_eur", "max"))
        .sort_values("prezzo_medio")
    )

    st.subheader("Statistiche per brand")
    st.dataframe(summary.round(2), use_container_width=True)


if __name__ == "__main__":
    main()
