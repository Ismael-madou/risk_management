import io
import pandas as pd


def results_to_excel_bytes(
    results: pd.DataFrame, backtest_var_df: pd.DataFrame, backtest_es_df: pd.DataFrame
) -> bytes:
    """
    Génère un Excel (3 feuilles) en mémoire et retourne les bytes.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        results.to_excel(writer, sheet_name="daily_results", index=False)
        backtest_var_df.to_excel(writer, sheet_name="backtest_VaR", index=False)
        backtest_es_df.to_excel(writer, sheet_name="backtest_ES", index=False)
    return output.getvalue()
