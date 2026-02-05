import numpy as np
import pandas as pd
from src.back_test import kupiec_uc_test, backtest_var, backtest_es_simple


def test_kupiec_uc_test_basic_counts_and_keys():
    exceed = np.array([True, False, True, False, False], dtype=bool)  # x=2, n=5
    alpha = 0.01

    res = kupiec_uc_test(exceed, alpha)

    assert set(res.keys()) == {"n", "exceptions", "exception_rate", "LR_uc", "p_value"}

    assert res["n"] == 5
    assert res["exceptions"] == 2
    assert np.isclose(res["exception_rate"], 2 / 5)

    assert res["LR_uc"] >= 0.0
    assert 0.0 <= res["p_value"] <= 1.0


def test_backtest_var_builds_expected_dataframe():
    df = pd.DataFrame(
        {
            "loss_real": [0.10, 0.05, 0.20, 0.02],
            "VaR_model": [0.08, 0.08, 0.08, 0.08],
        }
    )

    out = backtest_var(df, var_col="VaR_model", alpha=0.01)

    assert isinstance(out, pd.DataFrame)
    assert list(out.columns) == [
        "method",
        "n",
        "exceptions",
        "exception_rate",
        "LR_uc",
        "p_value",
    ]
    assert len(out) == 1
    assert out.loc[0, "method"] == "VaR_model"
    assert out.loc[0, "n"] == 4
    assert out.loc[0, "exceptions"] == 2
    assert np.isclose(out.loc[0, "exception_rate"], 2 / 4)
    assert out.loc[0, "LR_uc"] >= 0.0
    assert 0.0 <= out.loc[0, "p_value"] <= 1.0


def test_backtest_es_simple_computes_worst_mean_and_es_mean():
    df = pd.DataFrame(
        {
            "loss_real": [0.01, 0.03, 0.10, 0.20],
            "ES_model": [0.15, 0.15, 0.15, 0.15],
        }
    )

    alpha_es = 0.25
    out = backtest_es_simple(df, es_col="ES_model", alpha_es=alpha_es)

    assert len(out) == 1
    assert out.loc[0, "method"] == "ES_model"
    assert np.isclose(out.loc[0, "mean_loss"], np.mean([0.01, 0.03, 0.10, 0.20]))
    assert np.isclose(out.loc[0, "mean_ES"], 0.15)

    loss = np.array([0.01, 0.03, 0.10, 0.20])
    thr = np.quantile(loss, 1 - alpha_es)
    worst = loss[loss >= thr]
    assert np.isclose(out.loc[0, "mean_loss_worst_(top_2.5%)"], worst.mean())
