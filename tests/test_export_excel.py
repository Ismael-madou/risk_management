import io
import pandas as pd
from src.export_excel import results_to_excel_bytes


def test_results_to_excel_bytes_returns_valid_xlsx_with_3_sheets_and_content():
    results = pd.DataFrame(
        {
            "date": [
                pd.to_datetime("2024-01-01").date(),
                pd.to_datetime("2024-01-02").date(),
            ],
            "loss_real": [0.1, 0.2],
            "VaR99_hist_loss": [0.15, 0.16],
        }
    )
    backtest_var_df = pd.DataFrame(
        {
            "method": ["VaR99_hist_loss"],
            "n": [2],
            "exceptions": [1],
            "exception_rate": [0.5],
            "LR_uc": [0.12],
            "p_value": [0.73],
        }
    )
    backtest_es_df = pd.DataFrame(
        {
            "method": ["ES97_5_hist_loss"],
            "mean_loss": [0.15],
            "mean_loss_worst_(top_2.5%)": [0.2],
            "mean_ES": [0.18],
            "note": ["Backtest ES simple (à détailler dans le rapport)."],
        }
    )

    b = results_to_excel_bytes(results, backtest_var_df, backtest_es_df)
    assert isinstance(b, (bytes, bytearray))
    assert len(b) > 0

    bio = io.BytesIO(b)
    xls = pd.ExcelFile(bio, engine="openpyxl")

    assert set(xls.sheet_names) == {"daily_results", "backtest_VaR", "backtest_ES"}

    got_results = pd.read_excel(xls, sheet_name="daily_results", engine="openpyxl")
    got_var = pd.read_excel(xls, sheet_name="backtest_VaR", engine="openpyxl")
    got_es = pd.read_excel(xls, sheet_name="backtest_ES", engine="openpyxl")

    assert list(got_results.columns) == list(results.columns)
    assert len(got_results) == len(results)
    assert got_results["loss_real"].tolist() == results["loss_real"].tolist()
    assert (
        got_results["VaR99_hist_loss"].tolist() == results["VaR99_hist_loss"].tolist()
    )

    assert got_var.to_dict(orient="list") == backtest_var_df.to_dict(orient="list")
    assert got_es.to_dict(orient="list") == backtest_es_df.to_dict(orient="list")
