# 📊 Financial Risk Management — VaR & Expected Shortfall (ES)

An interactive web application to **compute**, **visualize**, and **backtest** the **Value at Risk (VaR)** and the **Expected Shortfall (ES)** using real financial market data.

🔗 **Live application:**  
https://financial-risk-var-es.streamlit.app/

---

## 🎯 Project Objective

This academic project (Master SEP — University of Reims, 2025–2026) aims to:

1. Compute the **99% VaR** using two approaches:
   - Parametric (Normal distribution)
   - Historical (Empirical)
2. Compute the **97.5% Expected Shortfall**
3. Perform **backtesting** over the last year of data:
   - Kupiec test for VaR
   - Empirical comparison for ES
4. Provide a fully **interactive web interface** to explore these risk measures.

---

## 🧠 Theoretical Background

Logarithmic return:

rₜ = ln(Pₜ / Pₜ₋₁)  
Lₜ = −rₜ

### Parametric VaR (Normal)

VaR₉₉% = −(μ + σ Φ⁻¹(0.01))

### Historical VaR

VaR₉₉% = −Q₁%(r)

### Expected Shortfall (ES)

ES₉₇.₅% = − E[r | r ≤ Q₂.₅%(r)]

### Backtesting — Kupiec Test

LR_uc = −2 ln( ((1−α)^(n−x) α^x) / ((1−p̂)^(n−x) p̂^x) )

---

## 🖥️ Application Overview

The application is divided into two main tabs.

### ⚙️ Parameters Tab

Allows full configuration of the analysis:

- Asset selection (CAC40, LVMH, TotalEnergies, BNP… or custom Yahoo ticker)
- Date range selection
- Estimation window (≈2 years by default)
- Backtesting period (≈1 year)
- VaR confidence level
- ES confidence level

### 📊 Results Tab

Displays:

- Losses vs VaR graph
- Detailed daily results table
- VaR backtesting (Kupiec test)
- ES backtesting
- Exception rates
- Excel export

---

## 🗂️ Project Structure

