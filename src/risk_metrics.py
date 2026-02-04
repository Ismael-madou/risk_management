import numpy as np
import pandas as pd
from scipy.stats import norm


def compute_rolling_metrics(
    df_ret: pd.DataFrame,
    window_days: int = 504,      # ~ 2 ans bourse
    test_days: int = 252,        # ~ 1 an
    alpha_var: float = 0.01,     # VaR 99% => quantile 1%
    alpha_es: float = 0.025      # ES 97.5% => quantile 2.5%
) -> pd.DataFrame:
    """
    Pour chaque jour t de la période de test (dernière année):
    - VaR99 normale (sur fenêtre 2 ans précédant t)
    - VaR99 historique
    - ES97.5 historique
    Résultats en "loss" positive; compare à loss_real = -r_real.
    """
    df = df_ret.sort_values("date").reset_index(drop=True).copy()
    r = df["r"].to_numpy()

    if len(df) <= window_days + test_days:
        raise ValueError(
            f"Pas assez de données: {len(df)} lignes. "
            f"Il faut > window({window_days}) + test({test_days})."
        )

    rows = []
    for i in range(window_days, len(df)):
        w = r[i - window_days:i]
        mu = w.mean()
        sig = w.std(ddof=1)

        # VaR sur rendements
        var_norm_r = mu + sig * norm.ppf(alpha_var)
        var_hist_r = np.quantile(w, alpha_var)

        # ES historique: moyenne des rendements sous quantile alpha_es
        q_es = np.quantile(w, alpha_es)
        es_hist_r = w[w <= q_es].mean()

        rows.append({
            "date": df.loc[i, "date"],
            "r_real": float(r[i]),
            "loss_real": float(-r[i]),
            "VaR99_norm_loss": float(-var_norm_r),
            "VaR99_hist_loss": float(-var_hist_r),
            "ES97_5_hist_loss": float(-es_hist_r),
        })

    out = pd.DataFrame(rows).tail(test_days).reset_index(drop=True)
    return out
