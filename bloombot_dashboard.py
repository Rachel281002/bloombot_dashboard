"""
BloomBot — Live Sensor Dashboard
Fixed: plotly fillcolor rgba, button logic, alignment, spacing
Run:   streamlit run bloombot_dashboard.py
"""

import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(
    page_title="BloomBot · Live Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SUPABASE_URL = "https://gmyacsgpdnhvbtrdtthe.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdteWFjc2dwZG5odmJ0cmR0dGhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI1MzM5NzIsImV4cCI6MjA4ODEwOTk3Mn0"
    ".GixrDxtFD5VXTQw57ts95yUWs1IBZAS5iV3_8gL4x2A"
)
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("auto_refresh", True), ("refresh_count", 0), ("hist_limit", 20)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Palette ───────────────────────────────────────────────────────────────────
P = {
    "dark":   "#0D1F0D", "forest": "#1B4332", "green":  "#2D6A4F",
    "sage":   "#74C69D", "mint":   "#B7E4C7", "cream":  "#F8F5F0",
    "sand":   "#EDE8DC", "white":  "#FFFFFF", "gray":   "#7B8794",
    "red":    "#C0392B", "amber":  "#D97706", "blue":   "#2563EB",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {{
    background: {P['cream']} !important;
    font-family: 'Inter', sans-serif !important;
    color: {P['dark']} !important;
}}

.block-container {{ padding: 0 !important; max-width: 100% !important; }}
[data-testid="stMain"] > div {{ padding: 0 !important; }}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="collapsedControl"] {{
    display: none !important; visibility: hidden !important;
}}

/* ── Buttons ── */
[data-testid="stButton"] > button {{
    background: {P['forest']} !important;
    color: {P['mint']} !important;
    border: 1px solid {P['green']} !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 9px 20px !important;
    width: 100% !important;
    transition: all 0.18s ease !important;
    letter-spacing: 0.02em !important;
    cursor: pointer !important;
}}
[data-testid="stButton"] > button:hover {{
    background: {P['green']} !important;
    border-color: {P['sage']} !important;
    color: {P['white']} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(45,106,79,0.28) !important;
}}

/* ── Toggle ── */
[data-testid="stToggle"] label {{
    font-size: 13px !important;
    color: {P['gray']} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > label {{
    font-size: 12px !important;
    color: {P['gray']} !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    background: {P['white']} !important;
    border: 1px solid {P['sand']} !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    color: {P['dark']} !important;
    font-family: 'Inter', sans-serif !important;
}}

/* ── Metric card ── */
.bb-card {{
    background: {P['white']};
    border: 1px solid {P['sand']};
    border-radius: 16px;
    padding: 24px 22px 20px;
    height: 168px;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.2s, border-color 0.2s;
}}
.bb-card:hover {{
    box-shadow: 0 6px 24px rgba(27,67,50,0.09);
    border-color: {P['mint']};
}}
.bb-card-accent {{
    position: absolute; top: 0; left: 0; right: 0;
    height: 3px; border-radius: 16px 16px 0 0;
}}
.bb-card-label {{
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: {P['gray']}; margin-bottom: 10px; margin-top: 8px;
}}
.bb-card-value {{
    font-size: 48px; font-weight: 700;
    line-height: 1; letter-spacing: -0.04em; color: {P['dark']};
}}
.bb-card-unit {{
    font-size: 18px; font-weight: 300;
    color: {P['gray']}; margin-left: 2px;
}}
.bb-card-sub {{
    font-size: 11px; color: {P['gray']};
    margin-top: 8px; line-height: 1.5;
}}
.bb-card-bar {{
    height: 4px; background: {P['sand']};
    border-radius: 2px; margin-top: 14px; overflow: hidden;
}}
.bb-card-bar-fill {{
    height: 100%; border-radius: 2px;
    transition: width 0.8s ease;
}}

/* ── Badges ── */
.bb-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 20px;
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.07em; text-transform: uppercase;
    white-space: nowrap;
}}
.bb-badge-live  {{ background: rgba(116,198,157,0.15); color: {P['forest']};
                   border: 1px solid rgba(116,198,157,0.4); }}
.bb-badge-dry   {{ background: rgba(192,57,43,0.1);   color: {P['red']};
                   border: 1px solid rgba(192,57,43,0.25); }}
.bb-badge-good  {{ background: rgba(116,198,157,0.15); color: {P['green']};
                   border: 1px solid rgba(116,198,157,0.35); }}
.bb-badge-warn  {{ background: rgba(217,119,6,0.1);   color: {P['amber']};
                   border: 1px solid rgba(217,119,6,0.25); }}

/* ── Header ── */
.bb-header {{
    background: {P['dark']};
    padding: 0 36px; height: 64px;
    display: flex; align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid {P['forest']};
}}
.bb-logo-dot {{
    width: 10px; height: 10px; border-radius: 50%;
    background: {P['sage']};
    box-shadow: 0 0 8px rgba(116,198,157,0.6);
    display: inline-block; margin-right: 10px;
}}
.bb-logo-name {{
    font-size: 16px; font-weight: 700;
    color: {P['white']}; letter-spacing: -0.02em;
}}
.bb-logo-tag {{
    font-size: 10px; font-weight: 500; color: {P['sage']};
    letter-spacing: 0.06em; text-transform: uppercase; margin-left: 6px;
}}
.bb-header-right {{
    display: flex; align-items: center; gap: 20px;
    font-size: 12px; color: {P['gray']};
}}
.bb-hl {{ color: {P['sage']}; font-weight: 500; }}

/* ── Section labels ── */
.bb-eye {{
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: {P['green']}; margin-bottom: 4px;
}}
.bb-title {{
    font-size: 22px; font-weight: 700;
    color: {P['dark']}; letter-spacing: -0.02em; margin-bottom: 4px;
}}
.bb-sub {{ font-size: 13px; color: {P['gray']}; line-height: 1.6; }}

/* ── Pump card ── */
.pump-wrap {{
    background: {P['dark']};
    border: 1px solid {P['forest']};
    border-radius: 16px;
    padding: 24px 22px 20px;
    height: 168px;
    position: relative; overflow: hidden;
}}
.pump-wrap::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, {P['sage']}, {P['mint']});
    border-radius: 16px 16px 0 0;
}}
.pump-label {{
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: {P['gray']}; margin-bottom: 8px; margin-top: 8px;
}}
.pump-orb {{
    width: 36px; height: 36px; border-radius: 50%;
    display: inline-flex; align-items: center;
    justify-content: center; font-size: 16px; margin-bottom: 8px;
}}
.pump-orb-on  {{
    background: rgba(116,198,157,0.15);
    box-shadow: 0 0 20px rgba(116,198,157,0.4), 0 0 0 1px rgba(116,198,157,0.25);
}}
.pump-orb-off {{ background: {P['forest']}; }}
.pump-on  {{ font-size: 16px; font-weight: 700; color: {P['sage']}; }}
.pump-off {{ font-size: 16px; font-weight: 700; color: {P['gray']}; }}
.pump-detail {{ font-size: 11px; color: {P['gray']}; margin-top: 3px; line-height: 1.4; }}

/* ── Control panel ── */
.ctrl-panel {{
    background: {P['white']};
    border: 1px solid {P['sand']};
    border-radius: 16px;
    padding: 20px 20px 16px;
}}
.ctrl-title {{
    font-size: 12px; font-weight: 600;
    color: {P['dark']}; margin-bottom: 14px; letter-spacing: 0.02em;
}}

/* ── Chart card ── */
.chart-card {{
    background: {P['white']};
    border: 1px solid {P['sand']};
    border-radius: 16px;
    padding: 20px 16px 4px;
    overflow: hidden;
}}

/* ── Table ── */
.tbl-card {{
    background: {P['white']};
    border: 1px solid {P['sand']};
    border-radius: 16px;
    overflow: hidden;
}}
.tbl {{
    width: 100%; border-collapse: collapse;
    font-family: 'Inter', sans-serif; font-size: 12px;
}}
.tbl th {{
    text-align: left; padding: 10px 16px;
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: {P['gray']}; background: {P['cream']};
    border-bottom: 1px solid {P['sand']};
}}
.tbl td {{
    padding: 9px 16px; color: {P['gray']};
    border-bottom: 1px solid rgba(237,232,220,0.6);
    font-variant-numeric: tabular-nums;
}}
.tbl tr:last-child td {{ border-bottom: none; }}
.tbl tr:hover td {{ background: {P['cream']}; }}
.tbl td.hi {{ color: {P['dark']}; font-weight: 500; }}

/* ── Misc ── */
.bb-hr {{ height: 1px; background: {P['sand']}; border: none; margin: 0; }}
.gap8  {{ height: 8px; }}
.gap16 {{ height: 16px; }}
.gap24 {{ height: 24px; }}
.gap32 {{ height: 32px; }}

::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {P['sand']}; border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)


# ── Data helpers ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def fetch_latest():
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/sensor_data", headers=HEADERS,
            params={"select": "*", "order": "created_at.desc", "limit": "1"},
            timeout=6,
        )
        if r.status_code == 200 and r.json():
            return r.json()[0]
    except Exception:
        pass
    return None


@st.cache_data(ttl=5)
def fetch_history(n=20):
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/sensor_data", headers=HEADERS,
            params={"select": "*", "order": "created_at.desc", "limit": str(n)},
            timeout=6,
        )
        if r.status_code == 200 and r.json():
            rows = r.json()
            rows.reverse()
            return rows
    except Exception:
        pass
    return []


def fmt(iso):
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except Exception:
        return str(iso)[:19]


def classify(sp, tp, hp):
    if sp < 30:
        return "dry",  "DRY — Irrigating",  P["red"]
    if tp > 35 and hp < 40:
        return "warn", "Harsh Conditions",  P["amber"]
    return "good", "Healthy", P["sage"]


def pbar(val, lo, hi, color):
    pct = max(0.0, min(100.0, (val - lo) / (hi - lo) * 100))
    return (
        f'<div class="bb-card-bar">'
        f'<div class="bb-card-bar-fill" style="width:{pct:.1f}%;background:{color}"></div>'
        f'</div>'
    )


def hex_to_rgba(hex_color, alpha=0.08):
    """Convert #RRGGBB to rgba(r,g,b,alpha) — fixes Plotly fillcolor error."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── Fetch data ────────────────────────────────────────────────────────────────
latest  = fetch_latest()
history = fetch_history(st.session_state.hist_limit)

sp  = float(latest["soilpercent"])  if latest else 0.0
raw = int(latest["soilmoist"])      if latest else 0
tp  = float(latest["temperature"])  if latest else 0.0
hp  = float(latest["humidity"])     if latest else 0.0
led = bool(latest["led"])           if latest else False
ts  = latest["created_at"]          if latest else None

cls, status_lbl, _ = classify(sp, tp, hp)
sc = P["red"]   if sp < 30 else (P["amber"] if sp < 50 else P["sage"])
tc = P["red"]   if tp > 35 else P["amber"]
hc = P["blue"]  if hp >= 40 else P["amber"]


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="bb-header">
  <div style="display:flex;align-items:center;">
    <span class="bb-logo-dot"></span>
    <span class="bb-logo-name">BloomBot</span>
    <span class="bb-logo-tag">· Smart Irrigation</span>
  </div>
  <div class="bb-header-right">
    <span>Node: <span class="bb-hl">MCC-MRF</span></span>
    <span>Last: <span class="bb-hl">{fmt(ts)}</span></span>
    <span>Refreshes: <span class="bb-hl">{st.session_state.refresh_count}</span></span>
    <span class="bb-badge bb-badge-live">● LIVE</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Body ──────────────────────────────────────────────────────────────────────
st.markdown('<div style="padding:32px 36px 56px;">', unsafe_allow_html=True)


# ── Hero + controls ───────────────────────────────────────────────────────────
col_hero, col_ctrl = st.columns([3, 2], gap="large")

with col_hero:
    st.markdown(f"""
    <div class="bb-eye">Live Sensor Feed · Team Agriii</div>
    <div class="bb-title">Campus Irrigation Monitor</div>
    <div class="bb-sub">
      Real-time soil moisture, temperature and humidity from the
      MCC-MRF sensor node — with automatic pump control.
    </div>
    """, unsafe_allow_html=True)

with col_ctrl:
    st.markdown('<div class="ctrl-panel">', unsafe_allow_html=True)
    st.markdown('<div class="ctrl-title">⚙ &nbsp;Dashboard Controls</div>',
                unsafe_allow_html=True)

    # ── Button 1: Refresh Now ─────────────────────────────────────────────────
    if st.button("↻  Refresh Now", key="btn_refresh", use_container_width=True):
        st.cache_data.clear()
        st.session_state.refresh_count += 1
        st.rerun()

    st.markdown('<div class="gap8"></div>', unsafe_allow_html=True)

    # ── Toggle: Auto-refresh ──────────────────────────────────────────────────
    st.session_state.auto_refresh = st.toggle(
        "Auto-refresh every 5s",
        value=st.session_state.auto_refresh,
        key="toggle_auto",
    )

    st.markdown('<div class="gap8"></div>', unsafe_allow_html=True)

    # ── Selectbox: History depth ──────────────────────────────────────────────
    opts   = {"Last 10 readings": 10, "Last 20 readings": 20,
              "Last 30 readings": 30, "Last 50 readings": 50}
    chosen = st.selectbox(
        "History depth", list(opts.keys()), index=1,
        key="sel_limit", label_visibility="visible",
    )
    if opts[chosen] != st.session_state.hist_limit:
        st.session_state.hist_limit = opts[chosen]
        st.cache_data.clear()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="gap32"></div>', unsafe_allow_html=True)
st.markdown('<hr class="bb-hr">', unsafe_allow_html=True)
st.markdown('<div class="gap24"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# METRIC CARDS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="bb-eye">Sensor Readings</div>',
            unsafe_allow_html=True)
st.markdown('<div class="gap16"></div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4, gap="medium")

with m1:
    st.markdown(f"""
    <div class="bb-card">
      <div class="bb-card-accent" style="background:{sc};"></div>
      <div class="bb-card-label">Soil Moisture</div>
      <div class="bb-card-value">{sp:.0f}<span class="bb-card-unit">%</span></div>
      <div class="bb-card-sub">
        Raw: {raw} &nbsp;·&nbsp;
        <span class="bb-badge bb-badge-{cls}"
              style="font-size:9px;padding:2px 8px;">{status_lbl}</span>
      </div>
      {pbar(sp, 0, 100, sc)}
    </div>
    """, unsafe_allow_html=True)

with m2:
    tn = "⚠ High temperature" if tp > 35 else "Normal range"
    st.markdown(f"""
    <div class="bb-card">
      <div class="bb-card-accent" style="background:{tc};"></div>
      <div class="bb-card-label">Temperature</div>
      <div class="bb-card-value">{tp:.1f}<span class="bb-card-unit">°C</span></div>
      <div class="bb-card-sub">{tn} &nbsp;·&nbsp; Limit 35°C</div>
      {pbar(tp, 0, 50, tc)}
    </div>
    """, unsafe_allow_html=True)

with m3:
    hn = "⚠ Dry air" if hp < 40 else "Normal range"
    st.markdown(f"""
    <div class="bb-card">
      <div class="bb-card-accent" style="background:{hc};"></div>
      <div class="bb-card-label">Air Humidity</div>
      <div class="bb-card-value">{hp:.1f}<span class="bb-card-unit">%</span></div>
      <div class="bb-card-sub">{hn} &nbsp;·&nbsp; Min 40%</div>
      {pbar(hp, 0, 100, hc)}
    </div>
    """, unsafe_allow_html=True)

with m4:
    orb_c  = "pump-orb-on"  if led else "pump-orb-off"
    st_c   = "pump-on"      if led else "pump-off"
    p_lbl  = "IRRIGATING"   if led else "STANDBY"
    p_icon = "💧"            if led else "🌿"
    p_info = (f"Soil {sp:.0f}% — below threshold"
              if led else f"Soil {sp:.0f}% — above threshold")
    st.markdown(f"""
    <div class="pump-wrap">
      <div class="pump-label">Irrigation Pump</div>
      <div class="pump-orb {orb_c}">{p_icon}</div>
      <div class="{st_c}">{p_lbl}</div>
      <div class="pump-detail">{p_info}</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown('<div class="gap32"></div>', unsafe_allow_html=True)
st.markdown('<hr class="bb-hr">', unsafe_allow_html=True)
st.markdown('<div class="gap24"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CHARTS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="bb-eye">Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="gap16"></div>', unsafe_allow_html=True)

BG   = P["white"]
GRID = "#F0EDE8"
TICK = "#C8C4BE"
FONT = "#A09C98"


def make_fig(h=260):
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor=BG, paper_bgcolor=BG, height=h,
        font=dict(family="Inter", color=FONT, size=11),
        margin=dict(l=4, r=4, t=12, b=8),
        xaxis=dict(
            showgrid=False, zeroline=False, showline=False,
            tickfont=dict(size=10, color=TICK), tickcolor=TICK,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=GRID, gridwidth=1,
            zeroline=False, showline=False,
            tickfont=dict(size=10, color=TICK),
        ),
        legend=dict(
            orientation="h", x=1, xanchor="right", y=1.16,
            font=dict(size=10, color=FONT),
            bgcolor="rgba(0,0,0,0)", itemsizing="constant",
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=P["white"], bordercolor=P["sand"],
            font=dict(color=P["dark"], size=11, family="Inter"),
        ),
    )
    return fig


if history:
    times  = [fmt(r["created_at"])       for r in history]
    soils  = [float(r["soilpercent"])    for r in history]
    temps  = [float(r["temperature"])    for r in history]
    humids = [float(r["humidity"])       for r in history]
    leds   = [1 if r["led"] else 0       for r in history]

    ch1, ch2 = st.columns([3, 2], gap="medium")

    with ch1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = make_fig(270)

        # ── FIX: use rgba() not hex+alpha ─────────────────────────────────────
        fig.add_trace(go.Scatter(
            x=times, y=soils, name="Soil %",
            line=dict(color=P["sage"], width=2.5, shape="spline", smoothing=0.7),
            fill="tozeroy",
            fillcolor=hex_to_rgba(P["sage"], 0.08),  # rgba — fixed
            hovertemplate="<b>%{y:.1f}%</b>",
            mode="lines",
        ))
        fig.add_trace(go.Scatter(
            x=times, y=humids, name="Humidity %",
            line=dict(color=P["blue"], width=2, shape="spline", smoothing=0.7),
            hovertemplate="<b>%{y:.1f}%</b>",
            mode="lines",
        ))
        fig.add_trace(go.Scatter(
            x=times, y=temps, name="Temp °C",
            line=dict(color=P["amber"], width=1.5, shape="spline",
                      smoothing=0.7, dash="dot"),
            hovertemplate="<b>%{y:.1f}°C</b>",
            mode="lines", yaxis="y2",
        ))
        fig.add_hline(
            y=30,
            line=dict(color=P["red"], width=1, dash="dash"),
            opacity=0.4,
            annotation_text="dry threshold 30%",
            annotation_font_size=9,
            annotation_font_color=P["red"],
        )
        fig.update_layout(
            yaxis=dict(range=[0, 105]),
            yaxis2=dict(
                overlaying="y", side="right", range=[0, 55],
                showgrid=False, zeroline=False, showline=False,
                tickfont=dict(size=10, color=TICK),
            ),
        )
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with ch2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig2 = make_fig(270)
        bar_colors = [hex_to_rgba(P["sage"], 0.8) if v else P["sand"]
                      for v in leds]
        fig2.add_trace(go.Bar(
            x=times, y=leds, name="Pump",
            marker=dict(color=bar_colors, line=dict(width=0)),
            hovertemplate="Pump: <b>%{customdata}</b>",
            customdata=["ON" if v else "OFF" for v in leds],
        ))
        fig2.update_layout(
            yaxis=dict(
                tickvals=[0, 1], ticktext=["Off", "On"],
                range=[-0.15, 1.7], showgrid=False,
                tickfont=dict(size=10, color=TICK),
            ),
            bargap=0.4, showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div style="background:{P['white']};border:1px solid {P['sand']};
                border-radius:16px;padding:60px;text-align:center;
                color:{P['gray']};font-size:13px;">
      🌱 &nbsp; Waiting for sensor data from Supabase…
    </div>
    """, unsafe_allow_html=True)


st.markdown('<div class="gap32"></div>', unsafe_allow_html=True)
st.markdown('<hr class="bb-hr">', unsafe_allow_html=True)
st.markdown('<div class="gap24"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA TABLE
# ═══════════════════════════════════════════════════════════════════════════════
t_col, b_col = st.columns([4, 1], gap="medium")

with t_col:
    st.markdown('<div class="bb-eye">Data Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="gap16"></div>', unsafe_allow_html=True)

with b_col:
    st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)
    if st.button("⟳  Hard Reload", key="btn_hard", use_container_width=True):
        st.cache_data.clear()
        st.session_state.refresh_count += 1
        st.rerun()

if history:
    rows = ""
    for row in reversed(history[-12:]):
        sp_r  = float(row["soilpercent"])
        tp_r  = float(row["temperature"])
        hp_r  = float(row["humidity"])
        ts_r  = fmt(row["created_at"])
        led_r = bool(row["led"])
        cl_r, lb_r, _ = classify(sp_r, tp_r, hp_r)
        pb = (
            f'<span class="bb-badge bb-badge-dry" '
            f'style="font-size:9px;padding:2px 8px;">ON</span>'
            if led_r else
            f'<span class="bb-badge bb-badge-good" '
            f'style="font-size:9px;padding:2px 8px;">OFF</span>'
        )
        rows += f"""<tr>
          <td class="hi">{ts_r}</td>
          <td class="hi">{sp_r:.0f}%</td>
          <td>{int(row['soilmoist'])}</td>
          <td>{tp_r:.1f} °C</td>
          <td>{hp_r:.1f}%</td>
          <td><span class="bb-badge bb-badge-{cl_r}"
                style="font-size:9px;padding:2px 8px;">{lb_r}</span></td>
          <td>{pb}</td>
        </tr>"""

    st.markdown(f"""
    <div class="tbl-card">
      <table class="tbl">
        <thead>
          <tr>
            <th>Time</th><th>Soil %</th><th>Raw ADC</th>
            <th>Temp</th><th>Humidity</th><th>Status</th><th>Pump</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="gap32"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            flex-wrap:wrap;gap:8px;padding-top:20px;
            border-top:1px solid {P['sand']};">
  <div style="display:flex;align-items:center;gap:8px;">
    <div style="width:24px;height:24px;border-radius:6px;
                background:{P['dark']};display:flex;
                align-items:center;justify-content:center;font-size:12px;">🌱</div>
    <span style="font-size:11px;color:{P['gray']};">
      BloomBot &nbsp;·&nbsp; Smart Irrigation &nbsp;·&nbsp;
      Team Agriii &nbsp;·&nbsp; MCC Campus
    </span>
  </div>
  <span style="font-size:11px;color:{P['sand']};">
    ESP8266 &nbsp;·&nbsp; DHT11 &nbsp;·&nbsp;
    Supabase &nbsp;·&nbsp; Streamlit
  </span>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Auto-refresh ──────────────────────────────────────────────────────────────
if st.session_state.auto_refresh:
    time.sleep(5)
    st.session_state.refresh_count += 1
    st.rerun()
