"""
═══════════════════════════════════════════════════════════════════════
  CANADA PERMANENT RESIDENCY — ECONOMIC IMPACT DASHBOARD  v2.0
  A research-grade analysis of PR admissions and macroeconomic outcomes
  Data: IRCC & Statistics Canada | 2015–2025 | Monthly frequency

  Capstone Group 4 — DAMO-699-1, Spring 2026
  University of Niagara Falls Canada
═══════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import statsmodels.api as sm
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Canada PR · Economic Impact Dashboard",
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
ROSE     = "#DB2777"
CYAN     = "#0891B2"

SERIES = [INK, MAPLE, TEAL, AMBER, INDIGO, VIOLET, EMERALD, MIST, ROSE, CYAN]

FONT = "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

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
    hoverlabel=dict(font_size=12, font_family=FONT, bgcolor=INK),
)

def style_fig(fig, height=360, legend_bottom=True):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    if legend_bottom:
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.22,
                                      xanchor="center", x=0.5, font=dict(size=11)))
    return fig

def covid_shade(fig, row=None, col=None):
    kw = {}
    if row is not None: kw = dict(row=row, col=col)
    fig.add_vrect(x0="2020-03-01", x1="2021-06-30",
                  fillcolor=AMBER, opacity=0.07, line_width=0, **kw)

# ═══════════════════════════════════════════════════════════════════════
#  GLOBAL CSS — Premium Design
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {{ font-family: {FONT}; }}
[data-testid="stAppViewContainer"] {{ background: linear-gradient(180deg, {CANVAS} 0%, #EFF6FF 100%); }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1520px; }}

/* ─── Dark sidebar ─── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {INK} 0%, #1E293B 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}}
[data-testid="stSidebar"] * {{ color: #CBD5E1 !important; }}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{ color: #F1F5F9 !important; }}
[data-testid="stSidebar"] .stSlider label, [data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stRadio label {{
    color: #94A3B8 !important; font-size: .72rem; font-weight: 600;
    letter-spacing: .08em; text-transform: uppercase;
}}

/* ─── Glassmorphism metric cards ─── */
div[data-testid="stMetric"] {{
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(226,232,240,0.6);
    border-radius: 16px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(15,27,45,0.04), 0 8px 32px rgba(15,27,45,0.04);
    transition: all .2s cubic-bezier(.4,0,.2,1);
}}
div[data-testid="stMetric"]:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(15,27,45,0.1);
    border-color: {MAPLE_LT};
}}
div[data-testid="stMetric"] label {{
    color: {MUTED} !important; font-size: .7rem !important; font-weight: 600;
    letter-spacing: .08em; text-transform: uppercase;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {INK}; font-weight: 800; font-size: 1.8rem; letter-spacing: -.02em;
}}

/* ─── Tab styling ─── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{ gap: 2px; border-bottom: 2px solid {LINE}; }}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    font-weight: 600; font-size: .78rem; color: {MUTED}; padding: 10px 14px;
    border-radius: 10px 10px 0 0; transition: all .15s ease;
}}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {{ color: {SLATE}; background: rgba(185,28,28,0.04); }}
[data-testid="stTabs"] [aria-selected="true"] {{ color: {MAPLE} !important; font-weight: 700; }}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ background-color: {MAPLE}; height: 3px; }}

/* ─── Hypothesis card ─── */
.hyp {{
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(8px);
    border: 1px solid {LINE};
    border-left: 4px solid {MAPLE};
    border-radius: 14px; padding: 20px 24px; margin-bottom: 18px;
    box-shadow: 0 2px 8px rgba(15,27,45,0.04);
}}
.hyp .eyebrow {{ font-size: .68rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: {MAPLE}; }}
.hyp h3 {{ margin: 4px 0 12px 0; color: {INK}; font-size: 1.15rem; font-weight: 700; }}
.hyp .row {{ display:flex; gap:10px; margin: 5px 0; font-size: .87rem; align-items:baseline; }}
.hyp .tag {{ font-weight: 700; color: {SLATE}; min-width: 42px; }}
.hyp .rationale {{ margin-top: 10px; padding-top: 10px; border-top: 1px dashed {LINE};
    font-size: .82rem; color: {MUTED}; font-style: italic; }}

/* ─── Section header ─── */
.sec {{ font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
    color: {SLATE}; margin: 24px 0 12px 0; display:flex; align-items:center; gap:8px; }}
.sec::before {{ content:''; width:20px; height:3px; background: linear-gradient(90deg, {MAPLE}, {MAPLE_LT});
    display:inline-block; border-radius: 2px; }}

/* ─── Verdict badges ─── */
.verdict {{ border-radius: 14px; padding: 16px 22px; margin: 4px 0 14px 0;
    font-size: .9rem; line-height: 1.6; border: 1px solid; }}
.v-support {{ background: linear-gradient(135deg, #ECFDF5, #D1FAE5); border-color:#A7F3D0; color:#065F46; }}
.v-reject  {{ background: linear-gradient(135deg, #FEF2F2, #FECACA); border-color:#FECACA; color:#991B1B; }}
.v-mixed   {{ background: linear-gradient(135deg, #FFFBEB, #FEF3C7); border-color:#FDE68A; color:#92400E; }}
.v-neutral {{ background: linear-gradient(135deg, #F1F5F9, #E2E8F0); border-color:#CBD5E1; color:#334155; }}
.verdict b {{ font-weight: 800; }}

/* ─── Hero ─── */
.hero {{ display:flex; align-items:center; gap:18px; margin-bottom:8px;
    padding: 12px 0; }}
.hero .mark {{ font-size:2.4rem; filter: drop-shadow(0 2px 4px rgba(185,28,28,0.2)); }}
.hero h1 {{ margin:0; font-size:1.6rem; font-weight:900; color:{INK}; letter-spacing:-.03em; }}
.hero p {{ margin:2px 0 0 0; color:{MUTED}; font-size:.85rem; font-weight:400; }}

/* ─── Report finding card ─── */
.report-card {{
    background: linear-gradient(135deg, #FFF7ED, #FFFBEB);
    border: 1px solid #FDE68A;
    border-left: 4px solid {AMBER};
    border-radius: 12px; padding: 16px 20px; margin: 12px 0;
    font-size: .88rem; color: #92400E; line-height: 1.6;
}}
.report-card b {{ color: #78350F; }}
.report-card .label {{ font-size: .68rem; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: {AMBER}; margin-bottom: 6px; }}

/* ─── Data frames ─── */
[data-testid="stDataFrame"] {{ border:1px solid {LINE}; border-radius:14px;
    box-shadow: 0 1px 3px rgba(15,27,45,0.03); }}

/* ─── Footer ─── */
.foot {{ text-align:center; color:{MIST}; font-size:.78rem; padding:20px 0 6px 0;
    border-top:1px solid {LINE}; margin-top:32px; }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  DATA LOADING
# ═══════════════════════════════════════════════════════════════════════
BASE = Path(__file__).resolve().parent / "data"
TABLES = BASE / "tables"
FIGURES = BASE / "figures"

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

@st.cache_data(show_spinner=False)
def load_table(name):
    try:
        return pd.read_csv(TABLES / name)
    except Exception:
        return None

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
CONTROLS = ["time_trend", "covid_dummy", "prime_rate", "cpi_all_items"]
CONTROL_LABELS = {
    "time_trend": "Time trend", "covid_dummy": "COVID-19 dummy",
    "prime_rate": "Prime interest rate", "cpi_all_items": "CPI (all items)",
    "const": "Intercept", "pr_admissions_national": "PR admissions",
    "pr_lag3": "PR admissions (lag 3m)", "pr_lag6": "PR admissions (lag 6m)",
    "pr_lag12": "PR admissions (lag 12m)",
}

def run_ols(df, y_col, x_cols, hac_lags=6):
    d = df.dropna(subset=[y_col] + x_cols).copy()
    usable = [x_cols[0]] + [c for c in x_cols[1:] if d[c].nunique() > 1]
    if len(d) < len(usable) + 3:
        return None, len(d)
    X = sm.add_constant(d[usable])
    lags = min(hac_lags, max(1, len(d) // 4))
    try:
        model = sm.OLS(d[y_col], X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    except Exception:
        return None, len(d)
    return model, len(d)

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
    st.markdown(f"<p style='color:{MIST};font-size:.78rem;margin-top:0;'>Economic Research Dashboard · v2.0</p>",
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
<b style='color:#CBD5E1;'>Sources</b><br>IRCC · Statistics Canada<br>2015–2025<br><br>
<b style='color:#CBD5E1;'>Team</b><br>Group 4 · DAMO-699-1<br>University of Niagara Falls
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
    <p>Do PR admissions move GDP, jobs, unemployment, and labour input? A multi-method econometric analysis · {yr_range[0]}–{yr_range[1]}</p>
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
#  REUSABLE RQ BLOCK
# ═══════════════════════════════════════════════════════════════════════
def rq_block(y_col, y_label, y_units, accent, alt_direction="positive",
             monthly_y_transform=None, monthly_label=None, report_finding=None):
    model, n = run_ols(nat_f, y_col, x_cols)
    if model is None:
        st.warning(f"Not enough data ({n} months). Widen the **Analysis Period** in the sidebar.")
        return
    beta = model.params[pr_var]; p = model.pvalues[pr_var]; r2 = model.rsquared_adj
    sig = p < 0.05; pos = beta > 0

    if alt_direction == "positive":
        if sig and pos:
            cls, txt = "v-support", f"<b>H₁ supported.</b> Statistically significant <b>positive</b> association (p {fmt_p(p)}). β = {beta:+.4g} {y_units} per PR admission."
        elif sig and not pos:
            cls, txt = "v-reject", f"<b>H₁ rejected.</b> Significant but <b>negative</b> (p {fmt_p(p)}), opposite to hypothesis."
        else:
            cls, txt = "v-neutral", f"<b>H₀ not rejected.</b> No significant association at α=0.05 (p {fmt_p(p)})."
    else:
        if sig and not pos:
            cls, txt = "v-support", f"<b>H₁a supported.</b> PR admissions significantly associated with <b>lower</b> {y_label.lower()} (β={beta:+.4g}, p {fmt_p(p)})."
        elif sig and pos:
            cls, txt = "v-mixed", f"<b>H₁b supported.</b> PR admissions associated with <b>higher</b> {y_label.lower()} (β={beta:+.4g}, p {fmt_p(p)})."
        else:
            cls, txt = "v-neutral", f"<b>H₀ not rejected.</b> No significant relationship at α=0.05 (p {fmt_p(p)})."

    st.markdown(f"<div class='verdict {cls}'>{txt}</div>", unsafe_allow_html=True)

    s1,s2,s3,s4 = st.columns(4)
    s1.metric("PR Coefficient (β)", f"{beta:+.4g}")
    s2.metric("p-value", f"{fmt_p(p)} {sig_stars(p)}")
    s3.metric("Adj. R²", f"{r2:.3f}")
    s4.metric("Observations", f"{n} months")

    # Report finding card
    if report_finding:
        st.markdown(f"""<div class='report-card'>
            <div class='label'>📄 Final Report Finding (M2 Specification)</div>
            {report_finding}
        </div>""", unsafe_allow_html=True)

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
        st.plotly_chart(fig, theme=None, use_container_width=True)
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
        st.plotly_chart(fig2, theme=None, use_container_width=True)

    st.markdown("<div class='sec'>Full regression output</div>", unsafe_allow_html=True)
    ct = coef_table(model)
    styled = ct.style.format({
        "Coefficient":"{:+.4g}", "Std. Error":"{:.4g}", "t-stat":"{:+.2f}",
        "p-value":"{:.3f}", "CI Low (95%)":"{:+.4g}", "CI High (95%)":"{:+.4g}"
    }).background_gradient(subset=["p-value"], cmap="RdYlGn_r", vmin=0, vmax=0.2)
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.caption(f"OLS with HAC (Newey–West) std. errors · "
               f"Spec: {'controlled' if use_controls else 'bivariate'}, {lag_choice.lower()} · "
               f"*** p<0.001, ** p<0.01, * p<0.05, † p<0.10")


# ═══════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    " 🏠 Executive Summary ", " 📈 RQ1 · GDP ", " 👥 RQ2 · Employment ",
    " 📉 RQ3 · Unemployment ", " ⏱️ RQ4 · Hours ", " 🗺️ RQ5 · Provincial ",
    " 🤖 ML & Analytics ", " 📊 Categories ", " 🌍 Country-of-Origin ",
    " 🔬 Bartik IV ", " 📚 Literature ", " 📋 Methodology "
])

# ════════════════════════════════════════════════════════════════════
#  TAB 0 — EXECUTIVE SUMMARY
# ════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("<div class='sec'>National indicators at a glance</div>", unsafe_allow_html=True)
    fig = make_subplots(rows=2, cols=2, vertical_spacing=0.14, horizontal_spacing=0.08,
        subplot_titles=("PR admissions (monthly)", "Real GDP ($M)",
                        "Unemployment rate (%)", "Hours worked (M/mo)"))
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
    st.plotly_chart(fig, theme=None, use_container_width=True)

    # Hypothesis Scorecard from report
    st.markdown("<div class='sec'>Hypothesis verdicts — Final Report</div>", unsafe_allow_html=True)
    hyp_df = load_table("5m_10_hypothesis_summary.csv")
    if hyp_df is not None:
        def color_supported(v):
            if v == "Yes": return "background-color:#ECFDF5;color:#065F46;font-weight:700"
            return "background-color:#FEF2F2;color:#991B1B;font-weight:700"
        styled = hyp_df.style.map(color_supported, subset=["Supported"])
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        # Fallback: live scorecard
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
                             "Adj. R²":np.nan, "Verdict":"Insufficient data"})
                continue
            b, p, r2 = m.params[pr_var], m.pvalues[pr_var], m.rsquared_adj
            sig = p < 0.05
            if direction == "positive":
                verdict = "SUPPORTED" if (sig and b>0) else ("Rejected" if (sig and b<0) else "Not Rejected")
            else:
                verdict = "SUPPORTED" if (sig and b<0) else ("SUPPORTED (pos)" if (sig and b>0) else "Not Rejected")
            rows.append({"RQ":tag, "Outcome":lbl, "β (PR)":b, "p-value":p, "Adj. R²":r2, "Verdict":verdict})
        sc = pd.DataFrame(rows)
        st.dataframe(sc, use_container_width=True, hide_index=True)

    # Correlation heatmap
    st.markdown("<div class='sec'>Correlation structure</div>", unsafe_allow_html=True)
    corr_cols = ["pr_admissions_national","gdp_real_millions","employment_thousands",
                 "unemployment_rate","hours_worked_millions","prime_rate","cpi_all_items"]
    nice = {"pr_admissions_national":"PR","gdp_real_millions":"GDP","employment_thousands":"Employ.",
            "unemployment_rate":"Unemp.","hours_worked_millions":"Hours","prime_rate":"Prime",
            "cpi_all_items":"CPI"}
    avail = [c for c in corr_cols if c in nat_f.columns]
    cm = nat_f[avail].corr()
    cm.index = [nice.get(c,c) for c in cm.index]; cm.columns = [nice.get(c,c) for c in cm.columns]
    fig_c = px.imshow(cm, text_auto=".2f", color_continuous_scale=[MAPLE,"#FFFFFF",TEAL],
                      zmin=-1, zmax=1, aspect="auto")
    fig_c.update_layout(**{k:v for k,v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis")},
                        height=420, coloraxis_colorbar=dict(title="r", thickness=12))
    fig_c.update_traces(textfont_size=10)
    st.plotly_chart(fig_c, theme=None, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
#  TAB 1 — RQ1 GDP
# ════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("""
    <div class="hyp"><div class="eyebrow">Research Question 1</div>
      <h3>PR Admissions &amp; Real GDP</h3>
      <div class="row"><span class="tag">H₀</span><span>PR admissions have no significant effect on Real GDP.</span></div>
      <div class="row"><span class="tag">H₁</span><span>Higher PR admissions are associated with increased Real GDP.</span></div>
      <div class="rationale">Immigration expands labour supply, consumption demand, and investment.</div>
    </div>""", unsafe_allow_html=True)
    rq_block("gdp_real_millions", "Real GDP ($M)", "millions CAD", INDIGO,
             report_finding="<b>OLS M2:</b> β = +0.182, p < 0.001 · <b>Elasticity:</b> +0.044% per 1% ↑ PR · "
                           "<b>Cointegration:</b> Not found (EG p = 0.805) · <b>First-diff:</b> Marginal (p ≈ 0.06)")

# ════════════════════════════════════════════════════════════════════
#  TAB 2 — RQ2 EMPLOYMENT
# ════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("""
    <div class="hyp"><div class="eyebrow">Research Question 2</div>
      <h3>PR Admissions &amp; Employment Levels</h3>
      <div class="row"><span class="tag">H₀</span><span>PR admissions do not significantly affect employment levels.</span></div>
      <div class="row"><span class="tag">H₁</span><span>Increased PR admissions lead to higher employment levels.</span></div>
      <div class="rationale">A growing population raises both labour supply and demand for goods and services.</div>
    </div>""", unsafe_allow_html=True)
    rq_block("employment_thousands", "Employment (000s)", "thousand jobs", EMERALD,
             report_finding="<b>OLS M2:</b> β = +0.016, p = 0.009 · <b>Panel FE:</b> β = +0.000188, p < 0.001 · "
                           "<b>Bartik IV (2SLS):</b> β = +0.000064, p = 0.003 (attenuated → OLS not purely endogenous)")

# ════════════════════════════════════════════════════════════════════
#  TAB 3 — RQ3 UNEMPLOYMENT
# ════════════════════════════════════════════════════════════════════
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
             alt_direction="bidirectional",
             report_finding="<b>OLS M2:</b> β = −0.000081, p < 0.001 · <b>Cointegrated:</b> ✓ (EG p = 0.003) · "
                           "<b>ECM:</b> ECT = −0.131, correction speed 13%/month · <b>Panel FE:</b> p = 0.002")

# ════════════════════════════════════════════════════════════════════
#  TAB 4 — RQ4 HOURS WORKED
# ════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("""
    <div class="hyp"><div class="eyebrow">Research Question 4</div>
      <h3>PR Admissions &amp; Total Hours Worked</h3>
      <div class="row"><span class="tag">H₀</span><span>PR admissions do not affect total hours worked.</span></div>
      <div class="row"><span class="tag">H₁</span><span>Higher PR admissions increase total hours worked.</span></div>
      <div class="rationale">A larger workforce directly raises aggregate labour input.</div>
    </div>""", unsafe_allow_html=True)
    rq_block("hours_worked_millions", "Hours worked (M)", "million hours", VIOLET,
             monthly_y_transform=lambda s: s/1e6, monthly_label="Hours worked (B/mo)",
             report_finding="<b>OLS M2:</b> β = +3.296, p = 0.012 · <b>Elasticity:</b> +0.061% · "
                           "<b>Cointegrated:</b> ✓ (EG p = 0.020) · <b>ECM:</b> ECT = −0.113")


# ════════════════════════════════════════════════════════════════════
#  TAB 5 — RQ5 PROVINCIAL
# ════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("""
    <div class="hyp"><div class="eyebrow">Research Question 5</div>
      <h3>Regional Distribution &amp; Provincial Performance</h3>
      <div class="row"><span class="tag">H₀</span><span>PR distribution across provinces has no impact on regional economic performance.</span></div>
      <div class="row"><span class="tag">H₁</span><span>Provinces with higher PR inflows experience stronger economic performance.</span></div>
      <div class="rationale">Regional labour supply and demand respond to where immigrants settle.</div>
    </div>""", unsafe_allow_html=True)

    # Panel FE results from report
    panel_fe = load_table("5m_07_panel_fe.csv")
    if panel_fe is not None:
        st.markdown("<div class='sec'>Panel Fixed Effects results (n = 1,319 province-months)</div>", unsafe_allow_html=True)
        st.dataframe(panel_fe, use_container_width=True, hide_index=True)
        st.markdown("""<div class='report-card'>
            <div class='label'>📄 Panel FE Key Finding</div>
            <b>Employment rate:</b> β = +1.88×10⁻⁴, p < 0.001 · <b>Unemployment rate:</b> β = −8.3×10⁻⁵, p = 0.003 ·
            <b>Participation rate:</b> β = +1.43×10⁻⁴, p < 0.001 — all within-province effects significant.
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
                            text=[f"{v/1e3:.0f}K" for v in pt.pr], textposition="outside"))
            style_fig(fig, height=400, legend_bottom=False)
            fig.update_xaxes(title_text="Total PR admissions")
            st.plotly_chart(fig, theme=None, use_container_width=True)
        with c2:
            st.markdown("<div class='sec'>PR intake vs employment rate</div>", unsafe_allow_html=True)
            fig = px.scatter(prov_tot, x="pr", y="emp_rate", size="emp", text="Province",
                             color="Province", color_discrete_sequence=SERIES, trendline="ols",
                             trendline_scope="overall", size_max=40)
            fig.update_traces(textposition="top center", textfont_size=9)
            for tr in fig.data:
                if tr.mode == "lines": tr.line.color = INK; tr.line.dash="dot"
            style_fig(fig, height=400, legend_bottom=False)
            fig.update_layout(showlegend=False)
            fig.update_xaxes(title_text="Total PR admissions")
            fig.update_yaxes(title_text="Avg employment rate (%)")
            st.plotly_chart(fig, theme=None, use_container_width=True)

        st.markdown("<div class='sec'>PR admissions over time · selected provinces</div>", unsafe_allow_html=True)
        psel = prov_f[prov_f.Province.isin(sel_provinces)].groupby(["Year","Province"])["pr_admissions"].sum().reset_index()
        fig = px.area(psel, x="Year", y="pr_admissions", color="Province", color_discrete_sequence=SERIES)
        fig.update_traces(line=dict(width=0.5))
        style_fig(fig, height=340)
        fig.update_yaxes(title_text="PR admissions")
        st.plotly_chart(fig, theme=None, use_container_width=True)

    # Province clustering figure
    fig_path = FIGURES / "6a_03b_province_clusters_pca.png"
    if fig_path.exists():
        st.markdown("<div class='sec'>K-Means province clustering (k=3)</div>", unsafe_allow_html=True)
        st.image(str(fig_path), use_container_width=True)


# ════════════════════════════════════════════════════════════════════
#  TAB 6 — ML & ANALYTICS
# ════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("<div class='sec'>Machine Learning & Advanced Analytics</div>", unsafe_allow_html=True)
    st.markdown("""
    This section presents results from the analytics applications tier: Random Forest, XGBoost,
    Support Vector Machines, PCA, K-Means clustering, and walk-forward cross-validation.
    These methods **validate and extend** the statistical findings from OLS.
    """)

    ml_figures = [
        ("6a_02_rf_importance.png", "Random Forest Feature Importance", "PR admissions consistently appears as a non-trivial contributor alongside time trend and COVID dummy."),
        ("6a_xgb_importance.png", "XGBoost Feature Importance", "Gradient boosting confirms PR admissions as a significant predictor."),
        ("6a_05_pca.png", "PCA Scree Plot & Loadings", "PC1 (economic scale) explains 78.3% of variance. PR loads positively on the growth dimension."),
        ("6a_04_walkforward_cv_expanded.png", "Walk-Forward CV Model Comparison", "Ridge regression achieves the least-negative CV R², confirming it as the most stable level-forecasting approach."),
        ("6a_01_regularized_r2.png", "Regularized Regression R² Comparison", "Ridge, Lasso, and ElasticNet all retain PR admissions as a non-zero predictor."),
        ("6a_svm_fit.png", "SVM (RBF Kernel) Fit", "Support Vector Machine with RBF kernel captures non-linear patterns in the PR-economy relationship."),
    ]

    for i in range(0, len(ml_figures), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j < len(ml_figures):
                fname, title, desc = ml_figures[i+j]
                fpath = FIGURES / fname
                with col:
                    if fpath.exists():
                        st.markdown(f"**{title}**")
                        st.image(str(fpath), use_container_width=True)
                        st.caption(desc)
                    else:
                        st.info(f"Figure not found: {fname}")

    # Walk-forward CV table
    cv_table = load_table("6a_04_walkforward_cv.csv")
    if cv_table is not None:
        st.markdown("<div class='sec'>Walk-Forward CV detailed results</div>", unsafe_allow_html=True)
        st.dataframe(cv_table, use_container_width=True, hide_index=True)
        st.caption("All CV R² values are negative — expected for non-stationary level series forecasted out-of-sample.")


# ════════════════════════════════════════════════════════════════════
#  TAB 7 — CATEGORIES
# ════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown("<div class='sec'>Composition of permanent residency by program</div>", unsafe_allow_html=True)
    econ = ["Skilled Worker","Skilled Trade","Canadian Experience","Provincial Nominee Program",
            "Agri-Food Pilot","Rural and Northern Immigration","Start-up Business","Entrepreneur",
            "Self-Employed","Investor","Atlantic Immigration Pilot Programs","Atlantic Immigration Programs",
            "Federal Economic Mobility Pathways Pilot","Temporary Resident to Permanent Resident Pathway"]
    family = ["Sponsored Spouse or Partner","Sponsored Children","Sponsored Parent or Grandparent",
              "Sponsored Extended Family Member"]
    refugee = ["Government-Assisted Refugee","Privately Sponsored Refugee","Blended Sponsorship Refugee"]
    def broad(c):
        if c in econ: return "Economic"
        if c in family: return "Family"
        if c in refugee: return "Refugee"
        return "Caregiver / Other"
    ircc["Broad"] = ircc["ImmCategory"].apply(broad)
    nat_ircc = ircc[ircc.Geo_Level=="Unknown"].copy()
    nat_ircc = nat_ircc[(nat_ircc.Year>=yr_range[0])&(nat_ircc.Year<=yr_range[1])]
    agg = nat_ircc.groupby(["Year","Broad"])["Admissions"].sum().reset_index()
    cmap = {"Economic":INDIGO,"Family":EMERALD,"Refugee":AMBER,"Caregiver / Other":MIST}

    c1,c2 = st.columns([1.4,1])
    with c1:
        fig = px.bar(agg, x="Year", y="Admissions", color="Broad", color_discrete_map=cmap)
        fig.update_traces(marker_line_width=0)
        style_fig(fig, height=380)
        fig.update_yaxes(title_text="PR admissions")
        st.plotly_chart(fig, theme=None, use_container_width=True)
    with c2:
        tot = agg.groupby("Broad")["Admissions"].sum().reset_index()
        fig = go.Figure(go.Pie(labels=tot.Broad, values=tot.Admissions, hole=0.55,
                        marker=dict(colors=[cmap[b] for b in tot.Broad]),
                        textinfo="percent", textfont_size=12))
        fig.update_layout(**{k:v for k,v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis","legend")},
                          height=380, showlegend=True,
                          legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
        st.plotly_chart(fig, theme=None, use_container_width=True)

    # Class OLS results
    class_ols = load_table("23_class_ols.csv")
    if class_ols is not None:
        st.markdown("<div class='sec'>OLS coefficients by immigration class</div>", unsafe_allow_html=True)
        st.dataframe(class_ols, use_container_width=True, hide_index=True)
        st.markdown("""<div class='report-card'>
            <div class='label'>📄 Class Segmentation Finding</div>
            <b>Economic-class admissions</b> produced the largest employment and GDP coefficients,
            followed by family class, then refugee class — consistent with the human capital channel (Erkisi, 2023).
        </div>""", unsafe_allow_html=True)

    # Class figures
    class_figs = [("23_class_composition.png", "Immigration Class Composition"),
                  ("23_class_coefficients.png", "OLS Coefficients by Class"),
                  ("23_province_class_heatmap.png", "Province-Class Heatmap")]
    cols = st.columns(3)
    for i, (fname, title) in enumerate(class_figs):
        fpath = FIGURES / fname
        with cols[i]:
            if fpath.exists():
                st.markdown(f"**{title}**")
                st.image(str(fpath), use_container_width=True)


# ════════════════════════════════════════════════════════════════════
#  TAB 8 — COUNTRY-OF-ORIGIN
# ════════════════════════════════════════════════════════════════════
with tabs[8]:
    st.markdown("<div class='sec'>Country-of-Origin analysis</div>", unsafe_allow_html=True)
    st.markdown("This analysis examines whether the source-country composition of PR admissions "
                "is associated with differential economic outcomes.")

    origin_figs = [
        ("24_top15_countries.png", "Top 15 Source Countries"),
        ("24_country_outcome_heatmap.png", "Country-Outcome Correlation Heatmap"),
    ]
    cols = st.columns(2)
    for i, (fname, title) in enumerate(origin_figs):
        fpath = FIGURES / fname
        with cols[i]:
            if fpath.exists():
                st.markdown(f"**{title}**")
                st.image(str(fpath), use_container_width=True)

    country_corr = load_table("24_country_outcome_corr.csv")
    if country_corr is not None:
        st.markdown("<div class='sec'>Country-outcome correlation table</div>", unsafe_allow_html=True)
        st.dataframe(country_corr, use_container_width=True, hide_index=True)

    top5_path = FIGURES / "24_top5_timeseries.png"
    if top5_path.exists():
        st.markdown("<div class='sec'>Top 5 source countries — time series</div>", unsafe_allow_html=True)
        st.image(str(top5_path), use_container_width=True)


# ════════════════════════════════════════════════════════════════════
#  TAB 9 — BARTIK IV
# ════════════════════════════════════════════════════════════════════
with tabs[9]:
    st.markdown("<div class='sec'>Bartik Shift-Share Instrumental Variables</div>", unsafe_allow_html=True)
    st.markdown("""
    To address endogeneity — provinces with stronger economies may attract more immigrants —
    a **Bartik Shift-Share IV** strategy was implemented following Card (2001) and Goldsmith-Pinkham et al. (2020).
    """)

    bartik_iv = load_table("25_bartik_iv_results.csv")
    if bartik_iv is not None:
        st.dataframe(bartik_iv, use_container_width=True, hide_index=True)

    st.markdown("""<div class='report-card'>
        <div class='label'>📄 Bartik IV Key Finding</div>
        <b>First-stage F-statistic:</b> 316.21 (>> 10 threshold for strong instrument) ·
        <b>2SLS employment rate β:</b> +0.000064, p = 0.003 (smaller than OLS β = +0.000107) ·
        <b>Interpretation:</b> Attenuation under IV suggests OLS modestly overstates the causal effect,
        but the relationship remains significant — ruling out pure reverse causality.
    </div>""", unsafe_allow_html=True)

    bartik_figs = [
        ("25_bartik_shares.png", "Bartik Baseline Settlement Shares"),
        ("25_ols_vs_2sls.png", "OLS vs. 2SLS Coefficient Comparison"),
    ]
    cols = st.columns(2)
    for i, (fname, title) in enumerate(bartik_figs):
        fpath = FIGURES / fname
        with cols[i]:
            if fpath.exists():
                st.markdown(f"**{title}**")
                st.image(str(fpath), use_container_width=True)

    # Secondary migration
    st.markdown("<div class='sec'>Secondary migration analysis</div>", unsafe_allow_html=True)
    sec_figs = [
        ("26_net_migration.png", "Interprovincial Net Migration"),
        ("26_pr_outflow_analysis.png", "PR vs. Outflow Scatter"),
        ("26_od_heatmap.png", "Origin-Destination Flow Heatmap"),
    ]
    cols = st.columns(3)
    for i, (fname, title) in enumerate(sec_figs):
        fpath = FIGURES / fname
        with cols[i]:
            if fpath.exists():
                st.markdown(f"**{title}**")
                st.image(str(fpath), use_container_width=True)


# ════════════════════════════════════════════════════════════════════
#  TAB 10 — LITERATURE ALIGNMENT
# ════════════════════════════════════════════════════════════════════
with tabs[10]:
    st.markdown("<div class='sec'>Literature alignment analysis</div>", unsafe_allow_html=True)
    st.markdown("The confirmatory analysis compared our findings against 7 peer-reviewed studies, "
                "achieving a **92.3% alignment rate** across 13 directional predictions.")

    lit_table = load_table("26_confirmatory_alignment.csv")
    if lit_table is not None:
        st.dataframe(lit_table, use_container_width=True, hide_index=True)

    align_path = FIGURES / "6a_confirmatory_alignment.png"
    if align_path.exists():
        st.image(str(align_path), use_container_width=True,
                 caption="Literature Alignment Heatmap — 92.3% agreement rate")

    verdict_path = FIGURES / "fig10_hypothesis_verdicts.png"
    if verdict_path.exists():
        st.markdown("<div class='sec'>Hypothesis verdict scorecard</div>", unsafe_allow_html=True)
        st.image(str(verdict_path), use_container_width=True,
                 caption="Visual scorecard of all evaluated hypotheses")


# ════════════════════════════════════════════════════════════════════
#  TAB 11 — METHODOLOGY
# ════════════════════════════════════════════════════════════════════
with tabs[11]:
    st.markdown("<div class='sec'>Analytical approach</div>", unsafe_allow_html=True)
    st.markdown("""
This dashboard tests five research questions using **monthly time-series data** (2015–2025, n = 132)
rather than annual aggregates, preserving statistical power. The analytical framework spans three tiers:

**Tier 1 — Econometric Core:**
- OLS with HC1 robust standard errors (4 specifications: bivariate, controlled, log-linear, first-difference)
- Engle-Granger cointegration testing + Error Correction Models (ECM)
- Vector Autoregression (VAR) with Impulse Response Functions and FEVD
- Panel Fixed Effects (10 provinces × 132 months = 1,319 obs.)
- Bartik Shift-Share Instrumental Variables (2SLS)

**Tier 2 — Machine Learning Validation:**
- Random Forest (300 trees, OOB evaluation)
- XGBoost (gradient boosting)
- Support Vector Machine (RBF kernel)
- Ridge / Lasso / ElasticNet regularized regression
- Walk-forward cross-validation (TimeSeriesSplit, 5 folds)

**Tier 3 — Exploratory Analytics:**
- PCA (variance decomposition)
- K-Means provincial clustering (k=3)
- Immigration class segmentation
- Country-of-origin analysis
- Secondary interprovincial migration analysis
""")

    st.markdown("<div class='sec'>Why controls change the story</div>", unsafe_allow_html=True)
    st.markdown("""
PR admissions, GDP, employment, and hours worked all rose over the sample period. A bivariate
regression shows strong positive associations — but much of that is a shared upward **trend**,
not a causal immigration effect. Once the time trend and macro controls are added, several coefficients
shrink. **This is the expected, honest result**: it shows the raw correlations are
partly spurious, which is why the controlled specification is the default.
""")

    st.markdown("<div class='sec'>Variable definitions</div>", unsafe_allow_html=True)
    defs = pd.DataFrame({
        "Variable": ["PR admissions","Real GDP","Employment","Unemployment rate",
                     "Hours worked","GDP per worker","Time trend","COVID-19 dummy","Prime rate","CPI"],
        "Definition": [
            "Monthly permanent-resident landings (IRCC)",
            "Real GDP at basic prices, seasonally adjusted (millions of chained 2017 CAD)",
            "Total employed persons (thousands, LFS)",
            "Unemployment rate (%, LFS)",
            "Aggregate actual hours worked (millions/month)",
            "Real GDP per employed person (productivity proxy)",
            "Sequential month index (1–132) capturing secular growth",
            "1 for Mar 2020–Sep 2021, else 0",
            "Bank prime lending rate (%)",
            "Consumer Price Index, all items (2002=100)"],
        "Source": ["IRCC","Statistics Canada","Statistics Canada","Statistics Canada",
                   "Statistics Canada","Statistics Canada","Constructed","Constructed",
                   "Bank of Canada","Statistics Canada"]
    })
    st.dataframe(defs, use_container_width=True, hide_index=True)

    # Stationarity results
    stationarity = load_table("5m_01_stationarity.csv")
    if stationarity is not None:
        st.markdown("<div class='sec'>Stationarity test results</div>", unsafe_allow_html=True)
        st.dataframe(stationarity, use_container_width=True, hide_index=True)
        st.caption("All variables are I(1): non-stationary in levels, stationary after first differencing.")

    # Cointegration results
    coint = load_table("5m_12b_cointegration.csv")
    if coint is not None:
        st.markdown("<div class='sec'>Engle-Granger cointegration results</div>", unsafe_allow_html=True)
        st.dataframe(coint, use_container_width=True, hide_index=True)

    st.markdown("<div class='sec'>Limitations</div>", unsafe_allow_html=True)
    st.markdown("""
- **Association, not causation.** Controls reduce confounding but OLS does not establish causality.
  The Bartik IV analysis addresses this partially.
- **Aggregate masking.** National models can hide heterogeneous regional/sectoral effects (see RQ5).
- **COVID-19 structural break.** The pandemic produced extreme outliers; the dummy mitigates but does not fully neutralise this.
- **Short sample.** Eleven years of monthly data limits the precision of long-lag estimates.
- **Non-stationarity.** Several series are I(1); first-difference results should be given weight for non-cointegrated pairs.
""")

# ════════════════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="foot">
🍁 &nbsp;Canada PR Economic Impact Dashboard v2.0&nbsp; · &nbsp;
Group 4 — DAMO-699-1, Spring 2026&nbsp; · &nbsp;University of Niagara Falls Canada&nbsp; · &nbsp;
Data: IRCC &amp; Statistics Canada&nbsp; · &nbsp;2015–2025&nbsp; · &nbsp;
<i>Estimates are associational unless stated otherwise (Bartik IV).</i>
</div>""", unsafe_allow_html=True)
