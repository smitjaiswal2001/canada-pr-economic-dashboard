# 🍁 Canada PR Admissions — Economic Impact Dashboard

A research-grade Streamlit dashboard analysing the economic effects of Canada's
Permanent Residency admissions (2015–2025), testing five research questions with
proper econometric methods.

## Run it

```bash
cd pr_dashboard
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Opens at http://localhost:8501 . On Windows use `python -m streamlit run app.py`
(not bare `streamlit run`) if the command isn't on your PATH.

## What's new in this version

- **Monthly analysis (n≈132)** instead of annual aggregates (n≈10) — far more statistical power.
- **Multivariate OLS** with controls: time trend, COVID-19 dummy, prime rate, CPI.
- **HAC (Newey–West) standard errors** robust to autocorrelation in time series.
- **Toggle naive vs. controlled** specifications to see how confounding changes results.
- **Lag analysis** (contemporaneous, 3/6/12-month) for delayed immigration effects.
- **Full regression output** tables with SE, t-stats, p-values, 95% CIs.
- **Correlation matrix**, hypothesis scorecard, per-province regressions.
- Cohesive professional design system, consistent chart theme.

## Research Questions

| Tab | Outcome | Hypothesis |
|-----|---------|-----------|
| RQ1 | GDP growth (YoY) | PR → higher GDP growth |
| RQ2 | Employment level | PR → higher employment |
| RQ3 | Unemployment rate | PR → lower (H₁a) or higher (H₁b) |
| RQ4 | Hours worked | PR → more aggregate hours |
| RQ5 | Provincial performance | Higher-intake provinces perform better |

## Key finding

Bivariate models show strong positive PR associations, but once the time trend and
macro controls are added, most shrink toward zero — the raw correlations are largely a
**shared upward trend**. GDP growth and unemployment retain significance under controls;
employment and hours do not. The **Methodology** tab explains this in full.

## Data layout

```
data/
  processed/  master_national_monthly.csv, master_provincial_monthly.csv
  interim/    ircc_pr_monthly_by_province_category.csv
  raw/        IRCC country-of-citizenship..., Interprovincial migration 17100022.csv
```

*Estimates are associational, not causal.*
