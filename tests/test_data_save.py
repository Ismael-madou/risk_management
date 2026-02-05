import numpy as np
import pandas as pd
from src.data_save import compute_log_returns


def test_compute_log_returns_ok():
    df = pd.DataFrame(
        {
            "date": [
                pd.to_datetime("2024-01-01").date(),
                pd.to_datetime("2024-01-02").date(),
                pd.to_datetime("2024-01-03").date(),
            ],
            "close": [100, 101, 102],
        }
    )

    out = compute_log_returns(df)

    assert list(out.columns) == ["date", "close", "r", "loss"]
    assert len(out) == 2

    r_expected = [np.log(101 / 100), np.log(102 / 101)]
    assert np.allclose(
        out["r"].to_numpy(), np.array(r_expected), rtol=1e-12, atol=1e-12
    )
    assert np.allclose(
        out["loss"].to_numpy(), -out["r"].to_numpy(), rtol=1e-12, atol=1e-12
    )
