import numpy as np
import pandas as pd
import pytest
from src.risk_metrics import compute_rolling_metrics


def _make_df_ret(r_values, start="2024-01-01"):
    dates = pd.date_range(start, periods=len(r_values), freq="D")
    return pd.DataFrame({"date": dates.date, "r": np.array(r_values, dtype=float)})


def test_compute_rolling_metrics_raises_if_not_enough_data():
    window_days = 5
    test_days = 3
    df = _make_df_ret([0.01] * (window_days + test_days))  # égal => erreur

    with pytest.raises(ValueError, match="Pas assez de données"):
        compute_rolling_metrics(df, window_days=window_days, test_days=test_days)


def test_compute_rolling_metrics_shape_and_basic_consistency():
    window_days = 10
    test_days = 5
    rng = np.random.default_rng(42)
    r = rng.normal(loc=0.0005, scale=0.01, size=window_days + test_days + 5)
    df = _make_df_ret(r)

    out = compute_rolling_metrics(
        df, window_days=window_days, test_days=test_days, alpha_var=0.01, alpha_es=0.025
    )

    expected_cols = [
        "date",
        "r_real",
        "loss_real",
        "VaR99_norm_loss",
        "VaR99_hist_loss",
        "ES97_5_hist_loss",
    ]
    assert list(out.columns) == expected_cols
    assert len(out) == test_days
    assert np.allclose(
        out["loss_real"].to_numpy(), -out["r_real"].to_numpy(), rtol=0, atol=1e-15
    )
    for c in ["VaR99_norm_loss", "VaR99_hist_loss", "ES97_5_hist_loss"]:
        assert np.isfinite(out[c].to_numpy()).all()


def test_compute_rolling_metrics_constant_returns_deterministic():
    """
    Si tous les rendements = c, alors:
    - mu = c
    - sig = 0
    - quantiles = c
    - ES = c
    Donc toutes les mesures loss = -c, et loss_real = -c.
    """
    window_days = 6
    test_days = 4
    c = 0.01

    df = _make_df_ret([c] * (window_days + test_days + 2))

    out = compute_rolling_metrics(
        df,
        window_days=window_days,
        test_days=test_days,
        alpha_var=0.01,
        alpha_es=0.025,
    )

    assert len(out) == test_days
    for col in ["loss_real", "VaR99_norm_loss", "VaR99_hist_loss", "ES97_5_hist_loss"]:
        assert np.allclose(out[col].to_numpy(), -c, rtol=0, atol=1e-15)
