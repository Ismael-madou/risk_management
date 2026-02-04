from datetime import date
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.data_save import load_prices, compute_log_returns
from src.risk_metrics import compute_rolling_metrics
from src.back_test import backtest_var, backtest_es_simple
from src.export_excel import results_to_excel_bytes


st.set_page_config(page_title="VaR / ES Backtesting", layout="wide")
st.title("Mini-projet : VaR 99% + ES 97.5% (Backtesting)")

tab_params, tab_results = st.tabs(["⚙️ Paramètres", "📊 Résultats"])

# État
if "computed" not in st.session_state:
    st.session_state.computed = False
    st.session_state.results = None
    st.session_state.bt_var = None
    st.session_state.bt_es = None
    st.session_state.ticker_used = None


# -----------------------
# Onglet Paramètres
# -----------------------
with tab_params:
    st.subheader("Choix de l'actif et de la période")

    presets = {
        "CAC 40": "^FCHI",
        "LVMH": "MC.PA",
        "TotalEnergies": "TTE.PA",
        "Air Liquide": "AI.PA",
        "BNP Paribas": "BNP.PA",
    }

    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        preset_name = st.selectbox("Preset (optionnel)", list(presets.keys()), index=0)
        ticker = st.text_input("Ticker (Yahoo Finance)", value=presets[preset_name])

    with c2:
        start_date = st.date_input("Date début", value=date(2023, 1, 1))
        end_date = st.date_input("Date fin", value=date.today())

    st.divider()
    st.subheader("Paramètres de calcul")

    c3, c4, c5 = st.columns(3)
    with c3:
        window_days = st.slider("Fenêtre estimation (jours bourse ~ 2 ans)", 252, 800, 504, step=21)
    with c4:
        test_days = st.slider("Période backtesting (jours ~ 1 an)", 200, 300, 252)
    with c5:
        alpha_var = st.number_input("Alpha VaR (VaR 99% => 0.01)", 0.001, 0.1, 0.01, 0.001, format="%.3f")

    alpha_es = st.number_input("Alpha ES (ES 97.5% => 0.025)", 0.001, 0.2, 0.025, 0.001, format="%.3f")

    st.divider()
    debug = st.checkbox("🔎 Mode debug", value=True)

    run = st.button("🚀 Lancer le calcul", type="primary")

    if run:
        if start_date >= end_date:
            st.error("La date début doit être strictement avant la date fin.")
            st.stop()

        try:
            if debug:
                st.write("DEBUG cwd:", os.getcwd())
                st.write("DEBUG sys.path[0:6]:", sys.path[:6])
                st.write("DEBUG data_save module:", load_prices.__module__)

            with st.spinner("Téléchargement des données..."):
                prices = load_prices(ticker, start_date.isoformat(), end_date.isoformat())

            if debug:
                st.write("DEBUG prices columns:", prices.columns.tolist())
                st.write("DEBUG prices head:", prices.head(5))

            with st.spinner("Calcul des rendements..."):
                rets = compute_log_returns(prices)

            if debug:
                st.write("DEBUG rets columns:", rets.columns.tolist())
                st.write("DEBUG rets head:", rets.head(5))

            with st.spinner("Calcul VaR / ES en rolling + backtesting..."):
                results = compute_rolling_metrics(
                    rets,
                    window_days=window_days,
                    test_days=test_days,
                    alpha_var=alpha_var,
                    alpha_es=alpha_es
                )

                bt_var = pd.concat([
                    backtest_var(results, "VaR99_norm_loss", alpha=alpha_var),
                    backtest_var(results, "VaR99_hist_loss", alpha=alpha_var),
                ], ignore_index=True)

                bt_es = backtest_es_simple(results, "ES97_5_hist_loss", alpha_es=alpha_es)

            st.session_state.computed = True
            st.session_state.results = results
            st.session_state.bt_var = bt_var
            st.session_state.bt_es = bt_es
            st.session_state.ticker_used = ticker

            st.success("Calcul terminé ✅ Va dans l'onglet 📊 Résultats.")

        except Exception as e:
            # Trace complète, indispensable pour diagnostiquer
            st.exception(e)


# -----------------------
# Onglet Résultats
# -----------------------
with tab_results:
    if not st.session_state.computed:
        st.info("Lance d'abord le calcul dans l'onglet ⚙️ Paramètres.")
        st.stop()

    results = st.session_state.results
    bt_var = st.session_state.bt_var
    bt_es = st.session_state.bt_es
    ticker_used = st.session_state.ticker_used

    st.subheader(f"Résultats — {ticker_used}")

    left, right = st.columns([2, 1], gap="large")

    with left:
        st.markdown("### Pertes vs VaR (99%)")

        fig = plt.figure()
        plt.plot(pd.to_datetime(results["date"]), results["loss_real"], label="Pertes (L)")
        plt.plot(pd.to_datetime(results["date"]), results["VaR99_norm_loss"], label="VaR99 Normale")
        plt.plot(pd.to_datetime(results["date"]), results["VaR99_hist_loss"], label="VaR99 Historique")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("### Tableau (dernière année)")
        st.dataframe(results, use_container_width=True)

    with right:
        st.markdown("### Backtesting VaR (Kupiec)")
        st.dataframe(bt_var, use_container_width=True)

        st.markdown("### Backtesting ES (simple)")
        st.dataframe(bt_es, use_container_width=True)

        ex_norm = (results["loss_real"] > results["VaR99_norm_loss"]).mean()
        ex_hist = (results["loss_real"] > results["VaR99_hist_loss"]).mean()
        st.metric("Taux exceptions VaR normale", f"{ex_norm*100:.2f}%")
        st.metric("Taux exceptions VaR historique", f"{ex_hist*100:.2f}%")

        st.divider()
        st.markdown("### Export")

        excel_bytes = results_to_excel_bytes(results, bt_var, bt_es)
        st.download_button(
            "📥 Télécharger Excel (résultats + backtests)",
            data=excel_bytes,
            file_name="results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
