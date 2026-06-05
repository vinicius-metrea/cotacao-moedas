# pip install streamlit yfinance pandas plotly

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Cotação de Moedas",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Constants ────────────────────────────────────────────────────────────────

CURRENCIES = {
    "USD": {"name": "Dólar Americano",    "flag": "🇺🇸", "region": "Américas"},
    "EUR": {"name": "Euro",               "flag": "🇪🇺", "region": "Europa"},
    "GBP": {"name": "Libra Esterlina",    "flag": "🇬🇧", "region": "Europa"},
    "JPY": {"name": "Iene Japonês",       "flag": "🇯🇵", "region": "Ásia"},
    "CHF": {"name": "Franco Suíço",       "flag": "🇨🇭", "region": "Europa"},
    "CAD": {"name": "Dólar Canadense",    "flag": "🇨🇦", "region": "Américas"},
    "AUD": {"name": "Dólar Australiano",  "flag": "🇦🇺", "region": "Oceania"},
    "CNY": {"name": "Yuan Chinês",        "flag": "🇨🇳", "region": "Ásia"},
    "BRL": {"name": "Real Brasileiro",    "flag": "🇧🇷", "region": "Américas"},
    "MXN": {"name": "Peso Mexicano",      "flag": "🇲🇽", "region": "Américas"},
    "INR": {"name": "Rúpia Indiana",      "flag": "🇮🇳", "region": "Ásia"},
    "KRW": {"name": "Won Sul-coreano",    "flag": "🇰🇷", "region": "Ásia"},
    "SGD": {"name": "Dólar de Singapura", "flag": "🇸🇬", "region": "Ásia"},
    "NOK": {"name": "Coroa Norueguesa",   "flag": "🇳🇴", "region": "Europa"},
    "SEK": {"name": "Coroa Sueca",        "flag": "🇸🇪", "region": "Europa"},
    "NZD": {"name": "Dólar Neozelandês",  "flag": "🇳🇿", "region": "Oceania"},
    "ZAR": {"name": "Rand Sul-africano",  "flag": "🇿🇦", "region": "África"},
    "HKD": {"name": "Dólar de Hong Kong", "flag": "🇭🇰", "region": "Ásia"},
    "DKK": {"name": "Coroa Dinamarquesa", "flag": "🇩🇰", "region": "Europa"},
    "ARS": {"name": "Peso Argentino",     "flag": "🇦🇷", "region": "Américas"},
}

BASE_OPTIONS  = ["USD", "EUR", "BRL", "GBP", "JPY"]
LINE_CODES    = ["EUR", "GBP", "BRL", "JPY", "CHF", "CNY"]
LINE_COLORS   = ["#6c63ff", "#00d4aa", "#ff9f43", "#ff5c7a", "#54a0ff", "#feca57"]
BAR_CODES     = ["EUR", "GBP", "CHF", "CAD", "AUD", "NZD", "SGD", "HKD", "BRL", "MXN", "ZAR"]
DONUT_COLORS  = ["#6c63ff", "#00d4aa", "#ff9f43", "#ff5c7a", "#54a0ff", "#feca57"]

BG      = "#0f1117"
CARD_BG = "#1a1d27"
GRID    = "#2a2d3a"
TEXT    = "#e2e8f0"
MUTED   = "#8892a4"

# ── Data ─────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(base: str):
    targets = [c for c in CURRENCIES if c != base]
    tickers = [f"{base}{t}=X" for t in targets]

    raw = yf.download(tickers, start="2025-01-01", progress=False, auto_adjust=True)

    if raw.empty:
        return pd.DataFrame(), {}, {}, None

    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"].copy()
    else:
        close = raw[["Close"]].copy()
        close.columns = tickers

    # "USDBRL=X" → "BRL"
    close.columns = [col.replace(base, "", 1).replace("=X", "") for col in close.columns]
    close = close.sort_index()

    year_start = close.apply(lambda s: s.dropna().iloc[0] if not s.dropna().empty else float("nan"))
    current    = close.iloc[-1]
    last_date  = close.index[-1].date()

    return close, current.to_dict(), year_start.to_dict(), last_date


# ── Helpers ──────────────────────────────────────────────────────────────────

def fmt(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    if val >= 100:
        return f"{val:,.2f}"
    if val >= 0.01:
        return f"{val:.4f}"
    return f"{val:.6f}"


def pct_change(cur, start):
    try:
        if pd.isna(cur) or pd.isna(start) or start == 0:
            return None
        return (cur - start) / start * 100
    except Exception:
        return None


def badge(pct) -> str:
    base_style = "font-size:0.72rem;padding:2px 8px;border-radius:20px;font-weight:600;"
    if pct is None:
        return f'<span style="{base_style}background:rgba(136,146,164,.15);color:{MUTED}">— s/d</span>'
    if pct > 0.5:
        return f'<span style="{base_style}background:rgba(0,212,170,.15);color:#00d4aa">▲ {abs(pct):.2f}% no ano</span>'
    if pct < -0.5:
        return f'<span style="{base_style}background:rgba(255,92,122,.15);color:#ff5c7a">▼ {abs(pct):.2f}% no ano</span>'
    return f'<span style="{base_style}background:rgba(136,146,164,.15);color:{MUTED}">— {abs(pct):.2f}% no ano</span>'


def chart_layout(title: str, height: int = 400, **kwargs):
    return dict(
        title=dict(text=title, font_color=TEXT),
        plot_bgcolor=CARD_BG,
        paper_bgcolor=CARD_BG,
        font_color=TEXT,
        height=height,
        margin=dict(t=52, b=20, l=48, r=20),
        xaxis=dict(gridcolor=GRID, tickfont_color=MUTED, zeroline=False),
        yaxis=dict(gridcolor=GRID, tickfont_color=MUTED, zeroline=False),
        legend=dict(font_color=TEXT, bgcolor="rgba(0,0,0,0)"),
        **kwargs,
    )


# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown(f"""
<style>
  .block-container {{ padding-top:1.5rem; padding-bottom:1rem; max-width:1400px; }}
  .currency-card {{
    background:{CARD_BG}; border:1px solid {GRID}; border-radius:12px;
    padding:14px 16px; margin-bottom:8px;
  }}
  .currency-card:hover {{ border-color:#6c63ff; }}
  .card-flag  {{ font-size:1.5rem; line-height:1; margin-bottom:5px; }}
  .card-code  {{ font-size:.72rem; font-weight:700; color:{MUTED}; letter-spacing:.05em; }}
  .card-name  {{ font-size:.78rem; color:{MUTED}; white-space:nowrap; overflow:hidden;
                 text-overflow:ellipsis; margin-bottom:7px; }}
  .card-rate  {{ font-size:1.18rem; font-weight:700; color:{TEXT}; margin-bottom:4px; }}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

col_title, col_base, col_refresh = st.columns([3, 1.4, 0.6])

with col_title:
    st.markdown("## 🌐 Cotação de Moedas")

with col_base:
    base = st.selectbox(
        "Moeda base",
        BASE_OPTIONS,
        format_func=lambda c: f"{CURRENCIES[c]['flag']} {c} — {CURRENCIES[c]['name']}",
        label_visibility="collapsed",
    )

with col_refresh:
    if st.button("↺ Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Fetch ─────────────────────────────────────────────────────────────────────

with st.spinner("Buscando cotações no Yahoo Finance..."):
    close_df, current, year_start, last_date = fetch_data(base)

if not current:
    st.error("Não foi possível carregar os dados. Verifique a conexão e clique em ↺ Atualizar.")
    st.stop()

st.caption(
    f"Última atualização: **{last_date.strftime('%d/%m/%Y')}** · "
    "Fonte: Yahoo Finance · Cache: 1 hora"
)

st.divider()

# ── Cards ─────────────────────────────────────────────────────────────────────

st.markdown("**Cotações atuais**")

cards = [
    (code, info)
    for code, info in CURRENCIES.items()
    if code != base
    and code in current
    and not pd.isna(current.get(code, float("nan")))
]

COLS = 5
for row_start in range(0, len(cards), COLS):
    row = cards[row_start : row_start + COLS]
    cols = st.columns(COLS)
    for i, (code, info) in enumerate(row):
        rate = current[code]
        pct  = pct_change(rate, year_start.get(code))
        with cols[i]:
            st.markdown(f"""
            <div class="currency-card">
              <div class="card-flag">{info['flag']}</div>
              <div class="card-code">{code}</div>
              <div class="card-name">{info['name']}</div>
              <div class="card-rate">{fmt(rate)}</div>
              {badge(pct)}
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────

st.markdown("**Gráficos**")

col_bar, col_donut = st.columns(2)

# Bar
with col_bar:
    bc = [c for c in BAR_CODES if c != base and c in current and not pd.isna(current.get(c, float("nan")))]
    bv = [current[c] for c in bc]
    bc_colors = [f"hsl({(i * 37 + 200) % 360},70%,60%)" for i in range(len(bc))]

    fig_bar = go.Figure(go.Bar(
        x=bc, y=bv,
        marker_color=bc_colors,
        text=[fmt(v) for v in bv],
        textposition="outside",
        textfont_color=MUTED,
    ))
    fig_bar.update_layout(**chart_layout(f"Comparativo vs {base}", height=380, showlegend=False))
    st.plotly_chart(fig_bar, use_container_width=True)

# Donut
with col_donut:
    regions: dict = {}
    for code, info in CURRENCIES.items():
        if code != base and code in current and not pd.isna(current.get(code, float("nan"))):
            r = info["region"]
            regions[r] = regions.get(r, 0) + 1

    fig_donut = go.Figure(go.Pie(
        labels=list(regions.keys()),
        values=list(regions.values()),
        hole=0.55,
        marker_colors=DONUT_COLORS,
        textfont_color=TEXT,
    ))
    fig_donut.update_layout(**chart_layout("Distribuição por Região", height=380))
    st.plotly_chart(fig_donut, use_container_width=True)

# Line — normalized to 100 at start of year
line_codes = [
    c for c in LINE_CODES
    if c != base and not close_df.empty and c in close_df.columns
]

if line_codes and not close_df.empty:
    fig_line = go.Figure()
    for i, code in enumerate(line_codes):
        series = close_df[code].dropna()
        if series.empty or series.iloc[0] == 0:
            continue
        normalized = (series / series.iloc[0]) * 100
        fig_line.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized.values,
            name=f"{CURRENCIES[code]['flag']} {code}",
            line=dict(color=LINE_COLORS[i % len(LINE_COLORS)], width=2),
            mode="lines",
            hovertemplate=f"<b>{code}</b>: %{{y:.2f}}<extra></extra>",
        ))

    layout = chart_layout("Evolução em 2025 (Jan 2025 = 100)", height=420, hovermode="x unified")
    layout["yaxis"]["title"] = dict(text="Índice (base 100)", font_color=MUTED)
    fig_line.update_layout(**layout)
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# ── Table ─────────────────────────────────────────────────────────────────────

st.markdown("**Tabela completa**")

rows = []
for code, info in CURRENCIES.items():
    if code == base:
        continue
    rate = current.get(code)
    if rate is None or pd.isna(rate):
        continue
    pct = pct_change(rate, year_start.get(code))
    sign = "+" if pct and pct > 0 else ""
    rows.append({
        " ": info["flag"],
        "Código": code,
        "Moeda": info["name"],
        "Região": info["region"],
        f"1 {base} =": fmt(rate),
        f"1 {code} → {base}": fmt(1 / rate),
        "Var. no ano": f"{sign}{pct:.2f}%" if pct is not None else "—",
    })

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=580)

st.markdown("---")
st.caption("Dados: Yahoo Finance · Atualizados diariamente em dias úteis")
