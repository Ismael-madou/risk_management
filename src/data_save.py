import numpy as np
import pandas as pd
import yfinance as yf


def load_prices(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Télécharge des prix journaliers via Yahoo Finance (auto_adjust=True).
    Retour: DataFrame avec colonnes: date, close
    """
    data = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if data.empty:
        raise ValueError(f"Aucune donnée pour {ticker}. Vérifie le ticker.")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0] for c in data.columns]

    if "Close" not in data.columns:
        raise ValueError(
            f"Colonne 'Close' introuvable. Colonnes disponibles: {list(data.columns)}"
        )

    out = data[["Close"]].rename(columns={"Close": "close"}).copy()
    out.index = pd.to_datetime(out.index)
    out = out.reset_index().rename(columns={"Date": "date"})
    out["date"] = pd.to_datetime(out["date"]).dt.date

    # On force close en float
    out["close"] = pd.to_numeric(out["close"], errors="coerce")

    return out.dropna(subset=["close"]).reset_index(drop=True)


def compute_log_returns(data_prices: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute rendements log r et pertes loss=-r.
    Retour: date, close, r, loss
    """
    data = data_prices.copy()

    # Sécurité colonnes
    expected = {"date", "close"}
    missing = expected - set(data.columns)
    if missing:
        raise ValueError(
            f"Colonnes manquantes dans data_prices: {missing}. Colonnes: {list(data.columns)}"
        )

    data = data.sort_values("date").reset_index(drop=True)

    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data = data.dropna(subset=["close"]).reset_index(drop=True)

    # Calcul rendements
    data["r"] = np.log(data["close"] / data["close"].shift(1))

    # dropna sur r (après création seulement)
    data = data.dropna(subset=["r"]).reset_index(drop=True)

    data["loss"] = -data["r"]
    return data[["date", "close", "r", "loss"]]
