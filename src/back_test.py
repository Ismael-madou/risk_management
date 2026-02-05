import numpy as np
import pandas as pd
from scipy.stats import chi2


def kupiec_uc_test(exceed: np.ndarray, alpha: float) -> dict:
    """
    Test de Kupiec (Unconditional Coverage) pour VaR:
    H0: P(exceed)=alpha
    """
    exceed = exceed.astype(bool)
    x = int(exceed.sum())
    n = int(exceed.size)
    phat = x / n if n else np.nan

    eps = 1e-12
    a = min(max(alpha, eps), 1 - eps)
    p = min(max(phat, eps), 1 - eps)

    lr = -2 * (
        (n - x) * np.log(1 - a)
        + x * np.log(a)
        - ((n - x) * np.log(1 - p) + x * np.log(p))
    )
    pval = 1 - chi2.cdf(lr, df=1)
    return {
        "n": n,
        "exceptions": x,
        "exception_rate": phat,
        "LR_uc": float(lr),
        "p_value": float(pval),
    }


def backtest_var(
    df_results: pd.DataFrame, var_col: str, alpha: float = 0.01
) -> pd.DataFrame:
    exceed = df_results["loss_real"].to_numpy() > df_results[var_col].to_numpy()
    res = kupiec_uc_test(exceed, alpha)
    return pd.DataFrame([{"method": var_col, **res}])


def backtest_es_simple(
    df_results: pd.DataFrame, es_col: str, alpha_es: float = 0.025
) -> pd.DataFrame:
    """
    Backtest ES simple:
    compare moyenne des pires pertes (top alpha_es) avec la moyenne ES.
    À expliquer dans le rapport.
    """
    loss = df_results["loss_real"].to_numpy()
    ES = df_results[es_col].to_numpy()

    thr = np.quantile(loss, 1 - alpha_es)
    worst = loss[loss >= thr]

    return pd.DataFrame(
        [
            {
                "method": es_col,
                "mean_loss": float(loss.mean()),
                "mean_loss_worst_(top_2.5%)": float(worst.mean())
                if len(worst)
                else np.nan,
                "mean_ES": float(ES.mean()),
                "note": "Backtest ES simple (à détailler dans le rapport).",
            }
        ]
    )
