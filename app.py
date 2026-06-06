"""
═══════════════════════════════════════════════════════════════════════
  CANADA PERMANENT RESIDENCY — ECONOMIC IMPACT DASHBOARD
  A research-grade analysis of PR admissions and macroeconomic outcomes
  Data: IRCC & Statistics Canada | 2015–2025 | Monthly frequency
═══════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import statsmodels.api as sm
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Canada PR · Economic Impact",
    page_icon="🍁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════════════════
INK      = "#0F1B2D"
SLATE    = "#334155"
MUTED    = "#64748B"
MIST     = "#94A3B8"
LINE     = "#E2E8F0"
PAPER    = "#FFFFFF"
CANVAS   = "#F8FAFC"

MAPLE    = "#B91C1C"
MAPLE_LT = "#FCA5A5"
TEAL     = "#0D9488"
AMBER    = "#D97706"
INDIGO   = "#4F46E5"
VIOLET   = "#7C3AED"
EMERALD  = "#059669"

_BASE_SERIES = [INK, MAPLE, TEAL, AMBER, INDIGO, VIOLET, EMERALD, MIST, "#DB2777", "#0891B2",
                "#0E7490", "#B45309", "#6D28D9"]

def make_series(n):
    """Return n colours, cycling the palette if needed."""
    return [_BASE_SERIES[i % len(_BASE_SERIES)] for i in range(max(n, 1))]

SERIES = _BASE_SERIES

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

PLOTLY_LAYOUT = dict(
    font=dict(family=FONT, size=12, color=SLATE),
    plot_bgcolor=PAPER,
    paper_bgcolor=PAPER,
    margin=dict(t=48, b=36, l=56, r=24),
    xaxis=dict(showgrid=False, linecolor=LINE, ticks="outside", tickcolor=LINE,
               title_font=dict(size=11, color=MUTED)),
    yaxis=dict(showgrid=True, gridcolor=LINE, zeroline=False,
               title_font=dict(size=11, color=MUTED)),
    legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
    title=dict(text="", font=dict(size=14.5, color=INK, family=FONT)),
    hoverlabel=dict(font_size=12, font_family=FONT, bgcolor=INK),
)

def style_fig(fig, height=360, legend_bottom=True):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    if legend_bottom:
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.22,
                                      xanchor="center", x=0.5, font=dict(size=11)))
    return fig

COVID_START = "2020-03-01"
COVID_END   = "2021-06-30"

def covid_shade(fig, row=None, col=None):
    kw = {}
    if row is not None: kw = dict(row=row, col=col)
    fig.add_vrect(x0=COVID_START, x1=COVID_END,
                  fillcolor=AMBER, opacity=0.07, line_width=0, **kw)

# ═══════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', {FONT}; }}
[data-testid="stAppViewContainer"] {{ background: {CANVAS}; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1500px; }}

[data-testid="stSidebar"] {{ background: {INK}; border-right: 1px solid #1E293B; }}
[data-testid="stSidebar"] * {{ color: #CBD5E1 !important; }}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{ color: #F1F5F9 !important; }}
[data-testid="stSidebar"] .stSlider label, [data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stRadio label {{
    color: #94A3B8 !important; font-size: .72rem; font-weight: 600;
    letter-spacing: .08em; text-transform: uppercase;
}}

div[data-testid="stMetric"] {{
    background: {PAPER}; border: 1px solid {LINE}; border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(15,27,45,0.04), 0 8px 24px rgba(15,27,45,0.03);
    transition: transform .15s ease, box-shadow .15s ease;
}}
div[data-testid="stMetric"]:hover {{ transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(15,27,45,0.08); }}
div[data-testid="stMetric"] label {{
    color: {MUTED} !important; font-size: .7rem !important; font-weight: 600;
    letter-spacing: .07em; text-transform: uppercase; }}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {INK}; font-weight: 700; font-size: 1.7rem; }}

[data-testid="stTabs"] [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {LINE}; }}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    font-weight: 600; font-size: .82rem; color: {MUTED}; padding: 10px 16px;
    border-radius: 8px 8px 0 0; }}
[data-testid="stTabs"] [aria-selected="true"] {{ color: {MAPLE} !important; }}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ background-color: {MAPLE}; }}

.hyp {{ background: {PAPER}; border: 1px solid {LINE}; border-left: 4px solid {MAPLE};
    border-radius: 12px; padding: 18px 22px; margin-bottom: 18px;
    box-shadow: 0 1px 3px rgba(15,27,45,0.04); }}
.hyp .eyebrow {{ font-size: .68rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: {MAPLE}; }}
.hyp h3 {{ margin: 4px 0 12px 0; color: {INK}; font-size: 1.15rem; font-weight: 700; }}
.hyp .row {{ display:flex; gap:10px; margin: 5px 0; font-size: .87rem; align-items:baseline; }}
.hyp .tag {{ font-weight: 700; color: {SLATE}; min-width: 42px; }}
.hyp .rationale {{ margin-top: 10px; padding-top: 10px; border-top: 1px dashed {LINE};
    font-size: .82rem; color: {MUTED}; font-style: italic; }}

.sec {{ font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
    color: {SLATE}; margin: 22px 0 10px 0; display:flex; align-items:center; gap:8px; }}
.sec::before {{ content:''; width:18px; height:2px; background:{MAPLE}; display:inline-block; }}

.verdict {{ border-radius: 12px; padding: 16px 20px; margin: 4px 0 14px 0;
    font-size: .9rem; line-height: 1.5; border:1px solid; }}
.v-support {{ background:#ECFDF5; border-color:#A7F3D0; color:#065F46; }}
.v-reject  {{ background:#FEF2F2; border-color:#FECACA; color:#991B1B; }}
.v-mixed   {{ background:#FFFBEB; border-color:#FDE68A; color:#92400E; }}
.v-neutral {{ background:#F1F5F9; border-color:#E2E8F0; color:#334155; }}
.verdict b {{ font-weight: 800; }}

.hero {{ display:flex; align-items:center; gap:16px; margin-bottom:6px; }}
.hero .mark {{ font-size:2.1rem; }}
.hero h1 {{ margin:0; font-size:1.55rem; font-weight:800; color:{INK}; letter-spacing:-.02em; }}
.hero p {{ margin:2px 0 0 0; color:{MUTED}; font-size:.85rem; }}

[data-testid="stDataFrame"] {{ border:1px solid {LINE}; border-radius:12px; }}
.foot {{ text-align:center; color:{MIST}; font-size:.78rem; padding:18px 0 4px 0;
    border-top:1px solid {LINE}; margin-top:28px; }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════════════════════════
from pathlib import Path

# Resolve data relative to THIS file so the app works regardless of the
# directory it is launched from (critical for Streamlit Cloud / Render).
BASE = Path(__file__).resolve().parent / "data"

@st.cache_data(show_spinner="Loading data…")
def load_data():
    nat  = pd.read_csv(BASE / "processed" / "master_national_monthly.csv", parse_dates=["YearMonth"])
    prov = pd.read_csv(BASE / "processed" / "master_provincial_monthly.csv", parse_dates=["YearMonth"])
    ircc = pd.read_csv(BASE / "interim" / "ircc_pr_monthly_by_province_category.csv")

    nat = nat.sort_values("YearMonth").reset_index(drop=True)
    nat["Year"] = nat["YearMonth"].dt.year
    nat["gdp_growth_yoy"] = nat["gdp_real_millions"].pct_change(12) * 100
    nat["pr_lag3"]  = nat["pr_admissions_national"].shift(3)
    nat["pr_lag6"]  = nat["pr_admissions_national"].shift(6)
    nat["pr_lag12"] = nat["pr_admissions_national"].shift(12)

    prov["Year"] = prov["YearMonth"].dt.year
    ircc["Province"] = ircc["Province_Raw"].str.replace(r"\s*-\s*Total$", "", regex=True).str.strip()
    return nat, prov, ircc

try:
    nat, prov, ircc = load_data()
except FileNotFoundError as e:
    st.error(
        "**Data files not found.** Expected CSVs under a `data/` folder next to `app.py`:\n\n"
        "```\ndata/processed/master_national_monthly.csv\n"
        "data/processed/master_provincial_monthly.csv\n"
        "data/interim/ircc_pr_monthly_by_province_category.csv\n```\n\n"
        "If you deployed to a cloud host, make sure the `data/` folder was committed to the repo."
    )
    st.caption(f"Details: {e}")
    st.stop()

provinces = sorted(prov["Province"].unique())
all_years = sorted(nat["Year"].unique())


# ═══════════════════════════════════════════════════════════════════════
#  ECONOMETRIC ENGINE
# ═══════════════════════════════════════════════════════════════════════
_CONTROL_DEFS = [
    ("time_trend",   "Time trend"),
    ("covid_dummy",  "COVID-19 dummy"),
    ("prime_rate",   "Prime interest rate"),
    ("cpi_all_items","CPI (all items)"),
]
CONTROLS = [k for k, _ in _CONTROL_DEFS]
CONTROL_LABELS = {k: v for k, v in _CONTROL_DEFS}
CONTROL_LABELS.update({
    "const": "Intercept",
    "pr_admissions_national": "PR admissions",
    "pr_lag3":  "PR admissions (lag 3m)",
    "pr_lag6":  "PR admissions (lag 6m)",
    "pr_lag12": "PR admissions (lag 12m)",
})

def _run_ols_impl(df, y_col, x_cols, hac_lags=6):
    """Multivariate OLS with HAC errors. Returns (model, n) or (None, n) if
    there is not enough usable data to estimate the model."""
    d = df.dropna(subset=[y_col] + x_cols).copy()

    # Drop control columns that are constant within this window (e.g. the
    # COVID dummy is all-zero in a pre-2020 window) — they cause singular
    # matrices or NaN coefficients. Never drop the primary PR regressor.
    usable = [x_cols[0]] + [c for c in x_cols[1:] if d[c].nunique() > 1]

    # Need at least a few more observations than parameters to estimate.
    if len(d) < len(usable) + 3:
        return None, len(d)

    X = sm.add_constant(d[usable])
    lags = min(hac_lags, max(1, len(d) // 4))
    try:
        model = sm.OLS(d[y_col], X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    except Exception:
        return None, len(d)
    return model, len(d)

@st.cache_data(show_spinner=False)
def _cached_ols(min_date: str, max_date: str, n_rows: int,
                y_col: str, x_cols_tuple: tuple, hac_lags: int, _df):
    return _run_ols_impl(_df, y_col, list(x_cols_tuple), hac_lags)

def run_ols(df, y_col, x_cols, hac_lags=6):
    min_d = df["YearMonth"].min().isoformat()
    max_d = df["YearMonth"].max().isoformat()
    return _cached_ols(min_d, max_d, len(df), y_col, tuple(x_cols), hac_lags, df)

def coef_table(model):
    rows = []
    ci = model.conf_int()
    for name in model.params.index:
        rows.append({
            "Variable": CONTROL_LABELS.get(name, name),
            "Coefficient": model.params[name], "Std. Error": model.bse[name],
            "t-stat": model.tvalues[name], "p-value": model.pvalues[name],
            "CI Low (95%)": ci.loc[name, 0], "CI High (95%)": ci.loc[name, 1],
        })
    return pd.DataFrame(rows)

def sig_stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.10:  return "†"
    return ""

def fmt_p(p):
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


# ═══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:2px;'>🍁 PR Impact</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MIST};font-size:.78rem;margin-top:0;'>Economic Research Dashboard</p>",
                unsafe_allow_html=True)
    st.divider()

    yr_range = st.slider("Analysis Period", int(min(all_years)), int(max(all_years)), (2015, 2025))

    model_spec = st.radio("Regression Specification",
        ["Controlled (multivariate)", "Naive (bivariate)"],
        help="Controlled models add time trend, COVID dummy, prime rate, and CPI to isolate the PR effect.")
    use_controls = model_spec.startswith("Controlled")

    lag_choice = st.selectbox("PR Effect Timing",
        ["Contemporaneous", "Lag 3 months", "Lag 6 months", "Lag 12 months"],
        help="Immigration effects may materialise with a delay.")
    lag_map = {"Contemporaneous":"pr_admissions_national","Lag 3 months":"pr_lag3",
               "Lag 6 months":"pr_lag6","Lag 12 months":"pr_lag12"}
    pr_var = lag_map[lag_choice]

    st.divider()
    sel_provinces = st.multiselect("Provinces (RQ5)", provinces,
        default=["Ontario", "British Columbia", "Alberta", "Quebec"])

    st.divider()
    st.markdown(f"""
<div style='font-size:.74rem;color:{MIST};line-height:1.6;'>
<b style='color:#CBD5E1;'>Method</b><br>
Monthly OLS, n≈132<br>HAC (Newey–West) std. errors<br>α = 0.05 significance<br><br>
<b style='color:#CBD5E1;'>Sources</b><br>IRCC · Statistics Canada<br>2015–2025
</div>""", unsafe_allow_html=True)

nat_f  = nat[(nat.Year >= yr_range[0]) & (nat.Year <= yr_range[1])].copy()
prov_f = prov[(prov.Year >= yr_range[0]) & (prov.Year <= yr_range[1])].copy()
x_cols = [pr_var] + (CONTROLS if use_controls else [])


# ═══════════════════════════════════════════════════════════════════════
#  HERO + KPIs
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <span class="mark">🍁</span>
  <div>
    <h1>Permanent Residency &amp; the Canadian Economy</h1>
    <p>Do PR admissions move GDP, jobs, unemployment, and labour input? A controlled econometric analysis · {yr_range[0]}–{yr_range[1]}</p>
  </div>
</div>""", unsafe_allow_html=True)
st.write("")

if nat_f.empty:
    st.warning("No data in the selected period. Widen the **Analysis Period** in the sidebar.")
    st.stop()

total_pr   = nat_f["pr_admissions_national"].sum()
avg_growth = nat_f["gdp_growth_yoy"].mean()
avg_unemp  = nat_f["unemployment_rate"].mean()
avg_emp    = nat_f["employment_thousands"].mean()
peak_month = nat_f.loc[nat_f["pr_admissions_national"].idxmax(), "YearMonth"].strftime("%b %Y")

def _fmt(v, suffix="", scale=1.0, dp=1):
    return "—" if pd.isna(v) else f"{v/scale:.{dp}f}{suffix}"

k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Total PR Admissions", _fmt(total_pr, "M", 1e6, 2))
k2.metric("Avg GDP Growth (YoY)", _fmt(avg_growth, "%"))
k3.metric("Avg Unemployment", _fmt(avg_unemp, "%"))
k4.metric("Avg Employment", _fmt(avg_emp, "M", 1e3, 2))
k5.metric("Peak Intake Month", peak_month)


# ═══════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "  Overview  ", "  RQ1 · GDP  ", "  RQ2 · Employment  ",
    "  RQ3 · Unemployment  ", "  RQ4 · Hours  ", "  RQ5 · Regional  ",
    "  Categories  ", "  Methodology  "
])

def rq_block(y_col, y_label, y_units, accent, alt_direction="positive",
             monthly_y_transform=None, monthly_label=None):
    model, n = run_ols(nat_f, y_col, x_cols)
    if model is None:
        st.warning(
            f"Not enough data to estimate this model for the selected window "
            f"({n} usable month{'s' if n != 1 else ''}). "
            "Widen the **Analysis Period** in the sidebar — year-over-year GDP growth "
            "needs at least 12 months of prior data, so a window spanning two or more "
            "years is required."
        )
        return
    beta = model.params[pr_var]; p = model.pvalues[pr_var]; r2 = model.rsquared_adj
    sig = p < 0.05; pos = beta > 0

    if alt_direction == "positive":
        if sig and pos:
            cls, txt = "v-support", f"<b>H₁ supported.</b> A statistically significant <b>positive</b> association between PR admissions and {y_label.lower()} (p {fmt_p(p)}). Each additional PR admission is associated with a {beta:+.4g} change in {y_units}."
        elif sig and not pos:
            cls, txt = "v-reject", f"<b>H₁ rejected.</b> The effect is significant but <b>negative</b> (p {fmt_p(p)}), opposite to the hypothesised direction."
        else:
            cls, txt = "v-neutral", f"<b>H₀ not rejected.</b> No statistically significant association at α=0.05 (p {fmt_p(p)}) once {'controls are applied' if use_controls else 'examined bivariately'}."
    else:
        if sig and not pos:
            cls, txt = "v-support", f"<b>H₁a supported.</b> PR admissions are significantly associated with <b>lower</b> {y_label.lower()} (β={beta:+.4g}, p {fmt_p(p)})."
        elif sig and pos:
            cls, txt = "v-mixed", f"<b>H₁b supported.</b> PR admissions are significantly associated with <b>higher</b> {y_label.lower()} (β={beta:+.4g}, p {fmt_p(p)}) — consistent with short-run labour-market competition."
        else:
            cls, txt = "v-neutral", f"<b>H₀ not rejected.</b> No significant relationship at α=0.05 (p {fmt_p(p)})."

    st.markdown(f"<div class='verdict {cls}'>{txt}</div>", unsafe_allow_html=True)

    s1,s2,s3,s4 = st.columns(4)
    s1.metric("PR Coefficient (β)", f"{beta:+.4g}", help="Marginal effect of one PR admission")
    s2.metric("p-value", f"{fmt_p(p)} {sig_stars(p)}")
    s3.metric("Adj. R²", f"{r2:.3f}")
    s4.metric("Observations", f"{n} months")

    c1, c2 = st.columns([1.45, 1])
    with c1:
        st.markdown("<div class='sec'>Co-movement over time</div>", unsafe_allow_html=True)
        yvals = nat_f[y_col] if monthly_y_transform is None else monthly_y_transform(nat_f[y_col])
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=nat_f.YearMonth, y=nat_f.pr_admissions_national,
                             name="PR admissions", marker_color=MAPLE_LT,
                             marker_line_width=0, opacity=0.75), secondary_y=False)
        fig.add_trace(go.Scatter(x=nat_f.YearMonth, y=yvals, name=monthly_label or y_label,
                                 mode="lines", line=dict(color=accent, width=2.4)), secondary_y=True)
        covid_shade(fig)
        style_fig(fig, height=340)
        fig.update_yaxes(title_text="PR admissions / mo", secondary_y=False)
        fig.update_yaxes(title_text=monthly_label or y_label, secondary_y=True, showgrid=False)
        st.plotly_chart(fig, width='stretch')
    with c2:
        st.markdown("<div class='sec'>Partial relationship</div>", unsafe_allow_html=True)
        d = nat_f.dropna(subset=[y_col, pr_var])
        fig2 = px.scatter(d, x=pr_var, y=y_col, trendline="ols", color_discrete_sequence=[accent])
        fig2.update_traces(marker=dict(size=7, opacity=0.55, line=dict(width=0.5, color=PAPER)))
        for tr in fig2.data:
            if tr.mode == "lines": tr.line.color = INK; tr.line.width = 2
        style_fig(fig2, height=340, legend_bottom=False)
        fig2.update_xaxes(title_text=f"PR admissions ({lag_choice.lower()})")
        fig2.update_yaxes(title_text=y_label)
        st.plotly_chart(fig2, width='stretch')

    st.markdown("<div class='sec'>Full regression output</div>", unsafe_allow_html=True)
    ct = coef_table(model)
    styled = ct.style.format({
        "Coefficient":"{:+.4g}", "Std. Error":"{:.4g}", "t-stat":"{:+.2f}",
        "p-value":"{:.3f}", "CI Low (95%)":"{:+.4g}", "CI High (95%)":"{:+.4g}"
    }, na_rep="—").background_gradient(subset=["p-value"], cmap="RdYlGn_r", vmin=0, vmax=0.2)
    st.dataframe(styled, width='stretch', hide_index=True)
    st.caption(f"Dependent variable: **{y_label}** · OLS with HAC (Newey–West, 6 lags) standard errors · "
               f"Significance: *** p<0.001, ** p<0.01, * p<0.05, † p<0.10 · "
               f"Specification: {'controlled' if use_controls else 'bivariate'}, {lag_choice.lower()}.")


# ════════════ OVERVIEW
with tabs[0]:
    st.markdown("<div class='sec'>National indicators at a glance</div>", unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=2, vertical_spacing=0.14, horizontal_spacing=0.08,
        subplot_titles=("PR admissions (monthly)", "Real GDP ($M)",
                        "Unemployment rate (%)", "Hours worked (B/mo)"))
    fig.add_trace(go.Scatter(x=nat_f.YearMonth, y=nat_f.pr_admissions_national, mode="lines",
                  name="PR admissions", line=dict(color=MAPLE, width=2), fill="tozeroy",
                  fillcolor="rgba(185,28,28,0.08)"), 1, 1)
    fig.add_trace(go.Scatter(x=nat_f.YearMonth, y=nat_f.gdp_real_millions, mode="lines",
                  name="Real GDP", line=dict(color=INDIGO, width=2)), 1, 2)
    fig.add_trace(go.Scatter(x=nat_f.YearMonth, y=nat_f.unemployment_rate, mode="lines",
                  name="Unemployment rate", line=dict(color=AMBER, width=2)), 2, 1)
    fig.add_trace(go.Scatter(x=nat_f.YearMonth, y=nat_f.hours_worked_millions/1e6, mode="lines",
                  name="Hours worked", line=dict(color=VIOLET, width=2)), 2, 2)
    for r in (1,2):
        for c in (1,2): covid_shade(fig, row=r, col=c)
    fig.update_layout(**{k:v for k,v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis")},
                      height=520, showlegend=False)
    fig.update_xaxes(showgrid=False, linecolor=LINE)
    fig.update_yaxes(showgrid=True, gridcolor=LINE)
    fig.update_annotations(font_size=12.5, font_color=INK)
    st.plotly_chart(fig, width='stretch')

    st.markdown("<div class='sec'>Hypothesis scorecard · current specification</div>", unsafe_allow_html=True)
    st.caption(f"Spec: **{model_spec}** · Timing: **{lag_choice}** · Adjust in the sidebar to compare.")
    rq_defs = [
        ("RQ1", "GDP growth (YoY)", "gdp_growth_yoy", "positive"),
        ("RQ2", "Employment (000s)", "employment_thousands", "positive"),
        ("RQ3", "Unemployment rate", "unemployment_rate", "bidirectional"),
        ("RQ4", "Hours worked", "hours_worked_millions", "positive"),
    ]
    rows = []
    for tag, lbl, col, direction in rq_defs:
        m, n = run_ols(nat_f, col, x_cols)
        if m is None:
            rows.append({"RQ":tag, "Outcome":lbl, "β (PR)":np.nan, "p-value":np.nan,
                         "Adj. R²":np.nan, "Direction":"—", "Verdict":"Insufficient data"})
            continue
        b, p, r2 = m.params[pr_var], m.pvalues[pr_var], m.rsquared_adj
        sig = p < 0.05
        if direction == "positive":
            verdict = "H₁ supported" if (sig and b>0) else ("H₁ rejected (neg.)" if (sig and b<0) else "H₀ not rejected")
        else:
            verdict = "H₁a supported" if (sig and b<0) else ("H₁b supported" if (sig and b>0) else "H₀ not rejected")
        rows.append({"RQ":tag, "Outcome":lbl, "β (PR)":b, "p-value":p,
                     "Adj. R²":r2, "Direction":"↑" if b>0 else "↓", "Verdict":verdict})
    sc = pd.DataFrame(rows)
    def color_verdict(v):
        if "Insufficient" in v: return "background-color:#FEF9C3;color:#854D0E;font-weight:600"
        if "H₁a" in v: return "background-color:#ECFDF5;color:#065F46;font-weight:700"
        if "H₁b" in v: return "background-color:#FFFBEB;color:#92400E;font-weight:700"
        if "supported" in v: return "background-color:#ECFDF5;color:#065F46;font-weight:700"
        if "rejected" in v: return "background-color:#FEF2F2;color:#991B1B;font-weight:700"
        return "background-color:#F1F5F9;color:#334155;font-weight:600"
    styled = sc.style.format({"β (PR)":"{:+.4g}","p-value":"{:.3f}","Adj. R²":"{:.3f}"}, na_rep="—") \
                     .map(color_verdict, subset=["Verdict"]) \
                     .background_gradient(subset=["p-value"], cmap="RdYlGn_r", vmin=0, vmax=0.2)
    st.dataframe(styled, width='stretch', hide_index=True)

    st.markdown("<div class='sec'>Correlation structure</div>", unsafe_allow_html=True)
    corr_cols = ["pr_admissions_national","gdp_real_millions","employment_thousands",
                 "unemployment_rate","hours_worked_millions","prime_rate","cpi_all_items",
                 "job_vacancies","labour_productivity_index"]
    nice = {"pr_admissions_national":"PR","gdp_real_millions":"GDP","employment_thousands":"Employ.",
            "unemployment_rate":"Unemp.","hours_worked_millions":"Hours","prime_rate":"Prime",
            "cpi_all_items":"CPI","job_vacancies":"Vacancies","labour_productivity_index":"Productiv."}
    avail = [c for c in corr_cols if c in nat_f.columns and nat_f[c].notna().sum() > 1]
    cm = nat_f[avail].corr()
    cm.index = [nice.get(c, c) for c in cm.index]
    cm.columns = [nice.get(c, c) for c in cm.columns]
    fig_c = px.imshow(cm, text_auto=".2f", color_continuous_scale=["#B91C1C","#FFFFFF","#0D9488"],
                      zmin=-1, zmax=1, aspect="auto")
    fig_c.update_layout(**{k:v for k,v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis")},
                        height=440, coloraxis_colorbar=dict(title="r", thickness=12))
    fig_c.update_traces(textfont_size=10)
    st.plotly_chart(fig_c, width='stretch')

# ════════════ RQ1
with tabs[1]:
    st.markdown("""
    <div class="hyp"><div class="eyebrow">Research Question 1</div>
      <h3>PR Admissions &amp; GDP Growth</h3>
      <div class="row"><span class="tag">H₀</span><span>PR admissions have no significant effect on GDP growth.</span></div>
      <div class="row"><span class="tag">H₁</span><span>Higher PR admissions are associated with increased GDP growth.</span></div>
      <div class="rationale">Immigration expands labour supply, consumption, and investment demand.</div>
    </div>""", unsafe_allow_html=True)
    rq_block("gdp_growth_yoy", "GDP growth (YoY %)", "percentage points", INDIGO,
             monthly_label="GDP growth YoY (%)")

# ════════════ RQ2
with tabs[2]:
    st.markdown("""
    <div class="hyp"><div class="eyebrow">Research Question 2</div>
      <h3>PR Admissions &amp; Employment Levels</h3>
      <div class="row"><span class="tag">H₀</span><span>PR admissions do not significantly affect employment levels.</span></div>
      <div class="row"><span class="tag">H₁</span><span>Increased PR admissions lead to higher employment levels.</span></div>
      <div class="rationale">A growing population raises both labour supply and demand for goods and services.</div>
    </div>""", unsafe_allow_html=True)
    rq_block("employment_thousands", "Employment (000s)", "thousand jobs", EMERALD,
             monthly_label="Employment (000s)")

# ════════════ RQ3
with tabs[3]:
    st.markdown("""
    <div class="hyp"><div class="eyebrow">Research Question 3</div>
      <h3>PR Admissions &amp; Unemployment Rate</h3>
      <div class="row"><span class="tag">H₀</span><span>PR admissions have no significant impact on unemployment rates.</span></div>
      <div class="row"><span class="tag">H₁a</span><span>Increased PR admissions reduce unemployment rates.</span></div>
      <div class="row"><span class="tag">H₁b</span><span>Increased PR admissions increase unemployment rates.</span></div>
      <div class="rationale">Short-run labour-market competition may raise unemployment; long-run expansion may lower it.</div>
    </div>""", unsafe_allow_html=True)
    rq_block("unemployment_rate", "Unemployment rate (%)", "percentage points", AMBER,
             alt_direction="bidirectional", monthly_label="Unemployment rate (%)")

# ════════════ RQ4
with tabs[4]:
    st.markdown("""
    <div class="hyp"><div class="eyebrow">Research Question 4</div>
      <h3>PR Admissions &amp; Total Hours Worked</h3>
      <div class="row"><span class="tag">H₀</span><span>PR admissions do not affect total hours worked.</span></div>
      <div class="row"><span class="tag">H₁</span><span>Higher PR admissions increase total hours worked.</span></div>
      <div class="rationale">A larger workforce directly raises aggregate labour input.</div>
    </div>""", unsafe_allow_html=True)
    rq_block("hours_worked_millions", "Hours worked (M)", "million hours", VIOLET,
             monthly_y_transform=lambda s: s/1e6, monthly_label="Hours worked (B/mo)")

# ════════════ RQ5
with tabs[5]:
    st.markdown("""
    <div class="hyp"><div class="eyebrow">Research Question 5</div>
      <h3>Regional Distribution &amp; Provincial Performance</h3>
      <div class="row"><span class="tag">H₀</span><span>PR distribution across provinces has no impact on regional economic performance.</span></div>
      <div class="row"><span class="tag">H₁</span><span>Provinces with higher PR inflows experience stronger economic performance.</span></div>
      <div class="rationale">Regional labour supply and demand respond to where immigrants settle.</div>
    </div>""", unsafe_allow_html=True)

    if not sel_provinces:
        st.warning("Select at least one province in the sidebar.")
    else:
        prov_tot = prov_f.groupby("Province").agg(
            pr=("pr_admissions","sum"), emp_rate=("employment_rate","mean"),
            unemp=("unemployment_rate","mean"), emp=("employment_thousands","mean")).reset_index()

        c1, c2 = st.columns([1,1.3])
        with c1:
            st.markdown("<div class='sec'>Share of national PR intake</div>", unsafe_allow_html=True)
            pt = prov_tot.sort_values("pr", ascending=True)
            fig = go.Figure(go.Bar(x=pt.pr, y=pt.Province, orientation="h",
                            marker=dict(color=pt.pr, colorscale=[[0,MAPLE_LT],[1,MAPLE]]),
                            text=[f"{v/1e3:.0f}K" if pd.notna(v) else "—" for v in pt.pr], textposition="outside"))
            style_fig(fig, height=400, legend_bottom=False)
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title_text="Total PR admissions")
            st.plotly_chart(fig, width='stretch')
        with c2:
            st.markdown("<div class='sec'>PR intake vs employment rate</div>", unsafe_allow_html=True)
            fig = px.scatter(prov_tot, x="pr", y="emp_rate", size="emp",
                             hover_name="Province",
                             hover_data={"pr": ":,.0f", "emp_rate": ":.1f", "emp": ":.0f"},
                             color="Province", color_discrete_sequence=make_series(len(prov_tot)),
                             trendline="ols", trendline_scope="overall", size_max=40)
            fig.update_traces(selector=dict(mode="markers"), textfont_size=9)
            for tr in fig.data:
                if tr.mode == "lines": tr.line.color = INK; tr.line.dash="dot"
            style_fig(fig, height=400, legend_bottom=False)
            fig.update_layout(showlegend=False)
            fig.update_xaxes(title_text="Total PR admissions")
            fig.update_yaxes(title_text="Avg employment rate (%)")
            st.plotly_chart(fig, width='stretch')

        st.markdown("<div class='sec'>PR admissions over time · selected provinces</div>", unsafe_allow_html=True)
        psel = prov_f[prov_f.Province.isin(sel_provinces)].groupby(["Year","Province"])["pr_admissions"].sum().reset_index()
        fig = px.area(psel, x="Year", y="pr_admissions", color="Province",
                      color_discrete_sequence=make_series(len(sel_provinces)))
        fig.update_traces(line=dict(width=0.5))
        style_fig(fig, height=340)
        fig.update_yaxes(title_text="PR admissions")
        st.plotly_chart(fig, width='stretch')

        st.markdown("<div class='sec'>Province-level effect · PR → employment rate</div>", unsafe_allow_html=True)
        reg_rows = []
        for pv in provinces:
            sub = prov_f[prov_f.Province==pv].dropna(subset=["pr_admissions","employment_rate"])
            if len(sub) > 15 and sub["pr_admissions"].nunique() > 1:
                try:
                    X = sm.add_constant(sub[["pr_admissions"]])
                    lags = min(6, max(1, len(sub)//4))
                    m = sm.OLS(sub["employment_rate"], X).fit(cov_type="HAC", cov_kwds={"maxlags":lags})
                except Exception:
                    continue
                reg_rows.append({"Province":pv, "β (PR)":m.params["pr_admissions"],
                                 "p-value":m.pvalues["pr_admissions"], "Adj. R²":m.rsquared_adj,
                                 "n":int(len(sub)),
                                 "Significant":"Yes" if m.pvalues["pr_admissions"]<0.05 else "No"})
        if reg_rows:
            rdf = pd.DataFrame(reg_rows).sort_values("β (PR)", ascending=False)
            styled = rdf.style.format({"β (PR)":"{:+.4g}","p-value":"{:.3f}","Adj. R²":"{:.3f}"}, na_rep="—") \
                              .background_gradient(subset=["p-value"], cmap="RdYlGn_r", vmin=0, vmax=0.2)
            st.dataframe(styled, width='stretch', hide_index=True)
            st.caption("Bivariate OLS per province, HAC standard errors. Positive β = higher PR intake associated with higher employment rate.")
        else:
            st.info("Not enough data in the selected window to fit province-level models. Widen the Analysis Period.")

# ════════════ CATEGORIES
with tabs[6]:
    st.markdown("<div class='sec'>Composition of permanent residency by program</div>", unsafe_allow_html=True)
    _ECON = frozenset(["Skilled Worker","Skilled Trade","Canadian Experience","Provincial Nominee Program",
            "Agri-Food Pilot","Rural and Northern Immigration","Start-up Business","Entrepreneur",
            "Self-Employed","Investor","Atlantic Immigration Pilot Programs","Atlantic Immigration Programs",
            "Federal Economic Mobility Pathways Pilot","Temporary Resident to Permanent Resident Pathway"])
    _FAMILY = frozenset(["Sponsored Spouse or Partner","Sponsored Children","Sponsored Parent or Grandparent",
              "Sponsored Extended Family Member"])
    _REFUGEE = frozenset(["Government-Assisted Refugee","Privately Sponsored Refugee","Blended Sponsorship Refugee"])
    def broad(c):
        if c in _ECON: return "Economic"
        if c in _FAMILY: return "Family"
        if c in _REFUGEE: return "Refugee"
        return "Caregiver / Other"
    nat_levels = set(ircc["Geo_Level"].unique())
    if "Unknown" not in nat_levels:
        st.warning("Expected Geo_Level='Unknown' for national IRCC totals — category charts may be inaccurate.")
    nat_ircc = ircc[ircc.Geo_Level == "Unknown"].copy()
    nat_ircc = nat_ircc.assign(Broad=nat_ircc["ImmCategory"].apply(broad))
    nat_ircc = nat_ircc[(nat_ircc.Year>=yr_range[0])&(nat_ircc.Year<=yr_range[1])]
    agg = nat_ircc.groupby(["Year","Broad"])["Admissions"].sum().reset_index()
    cmap = {"Economic":INDIGO,"Family":EMERALD,"Refugee":AMBER,"Caregiver / Other":MIST}

    c1,c2 = st.columns([1.4,1])
    with c1:
        fig = px.bar(agg, x="Year", y="Admissions", color="Broad", color_discrete_map=cmap)
        fig.update_traces(marker_line_width=0)
        style_fig(fig, height=380)
        fig.update_yaxes(title_text="PR admissions")
        st.plotly_chart(fig, width='stretch')
    with c2:
        tot = agg.groupby("Broad")["Admissions"].sum().reset_index()
        fig = go.Figure(go.Pie(labels=tot.Broad, values=tot.Admissions, hole=0.55,
                        marker=dict(colors=[cmap[b] for b in tot.Broad]),
                        textinfo="percent+label", textfont_size=11,
                        hovertemplate="%{label}: %{value:,.0f} (%{percent})<extra></extra>"))
        fig.update_layout(**{k:v for k,v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis","legend")},
                          height=380, showlegend=True,
                          legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
        st.plotly_chart(fig, width='stretch')

    st.markdown("<div class='sec'>Top programs by total admissions</div>", unsafe_allow_html=True)
    _all_cat = nat_ircc.groupby("ImmCategory")["Admissions"].sum().reset_index().sort_values("Admissions")
    _top_n = min(10, len(_all_cat))
    if _top_n < 3:
        st.warning("Fewer than 3 program categories in this period — broaden the date range for a meaningful chart.")
    cat_tot = _all_cat.tail(_top_n)
    fig = go.Figure(go.Bar(x=cat_tot.Admissions, y=cat_tot.ImmCategory, orientation="h",
                    marker=dict(color=cat_tot.Admissions, colorscale=[[0,"#E0E7FF"],[1,INDIGO]]),
                    text=[f"{v/1e3:.0f}K" if pd.notna(v) else "—" for v in cat_tot.Admissions], textposition="outside"))
    style_fig(fig, height=420, legend_bottom=False)
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(title_text="Total admissions")
    st.plotly_chart(fig, width='stretch')

    st.markdown("<div class='sec'>Program intensity by province</div>", unsafe_allow_html=True)
    pv = ircc[ircc.Geo_Level=="Provincial"].copy()
    pv["P"] = pv["Province_Raw"].str.replace(r"\s*-\s*Total$","",regex=True).str.strip()
    hm = pv.groupby(["P","ImmCategory"])["Admissions"].sum().reset_index()
    pivot = hm.pivot(index="P", columns="ImmCategory", values="Admissions").fillna(0)
    fig = px.imshow(pivot, color_continuous_scale=["#FFFFFF","#FCA5A5",MAPLE], aspect="auto")
    fig.update_layout(**{k:v for k,v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis")},
                      height=460, coloraxis_colorbar=dict(title="Admissions", thickness=12))
    fig.update_xaxes(tickangle=-40, tickfont_size=9)
    st.plotly_chart(fig, width='stretch')

# ════════════ METHODOLOGY
with tabs[7]:
    st.markdown("<div class='sec'>Approach</div>", unsafe_allow_html=True)
    st.markdown("""
This dashboard tests five research questions using **monthly time-series data** (2015–2025, n ≈ 132)
rather than annual aggregates, preserving statistical power. Each outcome is modelled with
**Ordinary Least Squares** using **Newey–West (HAC) standard errors** robust to the
autocorrelation and heteroskedasticity typical of macroeconomic series.

**Two specifications** are available (sidebar):

- **Naive (bivariate):** outcome regressed on PR admissions alone. Reproduces the headline
  correlation but is vulnerable to confounding — both immigration and the economy trend upward together.
- **Controlled (multivariate):** adds a **time trend**, **COVID-19 dummy**, **prime interest rate**,
  and **CPI**, isolating the PR effect from the broader macro environment. This is the more credible estimate.

**Lag structure:** immigration effects can take time to appear, so PR admissions may be entered
contemporaneously or lagged 3, 6, or 12 months.
""")
    st.markdown("<div class='sec'>Why controls change the story</div>", unsafe_allow_html=True)
    st.markdown("""
PR admissions, GDP, employment, and hours worked all rose over the sample period. A bivariate
regression therefore shows strong positive associations — but much of that is a shared upward **trend**,
not a causal immigration effect. Once the time trend and macro controls are added, several coefficients
shrink and lose significance. **This is the expected, honest result**: it shows the raw correlations are
partly spurious, which is why the controlled specification is the default for interpretation.
""")
    st.markdown("<div class='sec'>Variable definitions</div>", unsafe_allow_html=True)
    defs = pd.DataFrame({
        "Variable": ["PR admissions","GDP growth (YoY)","Employment","Unemployment rate",
                     "Hours worked","Time trend","COVID-19 dummy","Prime rate","CPI"],
        "Definition": [
            "Monthly permanent-resident landings (IRCC)",
            "12-month % change in real GDP ($M, chained)",
            "Total employed persons (thousands, LFS)",
            "Unemployment rate (%, LFS)",
            "Aggregate actual hours worked (millions/month)",
            "Sequential month index capturing secular growth",
            "1 for Mar 2020–Jun 2021, else 0",
            "Bank prime lending rate (%)",
            "Consumer Price Index, all items (2002=100)"],
        "Source": ["IRCC","Statistics Canada","Statistics Canada","Statistics Canada",
                   "Statistics Canada","Constructed","Constructed","Bank of Canada","Statistics Canada"]
    })
    st.dataframe(defs, width='stretch', hide_index=True)
    st.markdown("<div class='sec'>Limitations</div>", unsafe_allow_html=True)
    st.markdown("""
- **Association, not causation.** Controls reduce confounding but do not establish causality;
  reverse causality (a strong economy attracting immigrants) remains possible.
- **Aggregate masking.** National models can hide heterogeneous regional/sectoral effects (see RQ5).
- **COVID-19 structural break.** The pandemic produced extreme outliers; the dummy mitigates but does not fully neutralise this.
- **Short sample.** Eleven years of monthly data limits the precision of long-lag estimates.
""")
    st.info("For inference beyond this dashboard, consider VAR / impulse-response analysis, "
            "instrumental variables, or a fixed-effects panel across provinces.")


st.markdown("""
<div class="foot">
🍁 &nbsp;Canada PR Economic Impact Dashboard&nbsp; · &nbsp;Data: IRCC &amp; Statistics Canada&nbsp; · &nbsp;
2015–2025&nbsp; · &nbsp;OLS with HAC standard errors&nbsp; · &nbsp;
<i>Estimates are associational, not causal.</i>
</div>""", unsafe_allow_html=True)
