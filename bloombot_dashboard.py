"""
BloomBot — Live Sensor Dashboard
Aesthetic: Professional, minimal, dark/light contrast cards, uniform heights.
"""

import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BloomBot · Farm Monitor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = "https://gmyacsgpdnhvbtrdtthe.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdteWFjc2dwZG5odmJ0cmR0dGhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI1MzM5NzIsImV4cCI6MjA4ODEwOTk3Mn0"
    ".GixrDxtFD5VXTQw57ts95yUWs1IBZAS5iV3_8gL4x2A"
)
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}
REFRESH_SEC = 5

# ── Design tokens ─────────────────────────────────────────────────────────────
C = {
    "page_bg":    "#F5F4F0",
    "section_bg": "#FFFFFF",
    "dark_card":  "#151515",
    "orange":     "#F97316",
    "orange_dim": "#F9731620",
    "teal":       "#14B8A6",
    "amber":      "#EAB308",
    "red":        "#EF4444",
    "green":      "#22C55E",
    "border":     "#E8E6E1",
    "dark_border":"#2A2A2A",
    "text_h":     "#111111",
    "text_b":     "#6B6660",
    "text_dim":   "#A09C98",
    "text_dark":  "#FFFFFF",
    "text_dark2": "#888888",
}

# ── Master CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset & globals */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .block-container {{
    background-color: {C['page_bg']} !important;
    font-family: 'Inter', sans-serif !important;
    color: {C['text_h']} !important;
}}

/* Hide Streamlit chrome completely */
#MainMenu, footer, header, [data-testid="stToolbar"] {{ display: none !important; }}

.block-container {{ padding: 0 !important; max-width: 100% !important; }}

/* Plotly chart bg transparency */
.js-plotly-plot .plotly, .js-plotly-plot .plotly .bg {{ background: transparent !important; }}

/* ── Navbar ── */
.bb-nav {{
    background: {C['section_bg']};
    border-bottom: 1px solid {C['border']};
    padding: 0 40px; display: flex; align-items: center; justify-content: space-between;
    height: 60px;
}}
.bb-logo {{ display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 15px; }}
.bb-logo-icon {{
    width: 28px; height: 28px; border-radius: 6px; background: {C['orange']};
    display: flex; align-items: center; justify-content: center; font-size: 14px;
}}

/* Typography */
.eyebrow {{ font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: {C['orange']}; margin-bottom: 7px; display: inline-block; }}
.section-h {{ font-size: 26px; font-weight: 700; letter-spacing: -0.03em; line-height: 1.2; margin-bottom: 5px; }}
.section-p {{ font-size: 13px; color: {C['text_b']}; line-height: 1.6; }}

/* ── Uniform Cards (Light & Dark) ── */
.mc, .dark-card, .pump-card {{
    border-radius: 14px; padding: 22px 20px 18px; 
    position: relative; overflow: hidden;
    min-height: 180px; /* Forces all cards to exactly the same height */
    display: flex; flex-direction: column;
}}
.mc {{ background: {C['section_bg']}; border: 1px solid {C['border']}; }}
.dark-card, .pump-card {{ background: {C['dark_card']}; border: 1px solid {C['dark_border']}; }}

/* Top Gradient Line for dark cards */
.dark-card::after, .pump-card::after {{
    content: ''; position: absolute; top: 0; left: 20px; right: 20px; height: 1px;
    background: linear-gradient(90deg, transparent, {C['orange']}40, transparent);
}}

/* Card Elements */
.mc-label {{ font-size: 10px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: {C['text_dim']}; margin-bottom: 8px; }}
.dc-label {{ font-size: 10px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: {C['text_dark2']}; margin-bottom: 8px; }}

.mc-val {{ font-size: 42px; font-weight: 700; line-height: 1; letter-spacing: -0.04em; color: {C['text_h']}; }}
.dc-val {{ font-size: 42px; font-weight: 700; line-height: 1; letter-spacing: -0.04em; color: #FFFFFF; }}

.mc-unit, .dc-unit {{ font-size: 18px; font-weight: 300; margin-left: 2px; }}
.mc-unit {{ color: {C['text_dim']}; }}
.dc-unit {{ color: {C['text_dark2']}; }}

.mc-sub {{ font-size: 12px; color: {C['text_dim']}; margin-top: 8px; line-height: 1.4; }}
.dc-sub {{ font-size: 12px; color: {C['text_dark2']}; margin-top: 8px; line-height: 1.4; }}

/* Progress Bars pushed to bottom via margin-top: auto */
.mc-bar, .dc-bar {{ height: 3px; border-radius: 2px; margin-top: auto; overflow: hidden; }}
.mc-bar {{ background: {C['border']}; }}
.dc-bar {{ background: #2A2A2A; }}
.mc-bar-fill, .dc-bar-fill {{ height: 100%; border-radius: 2px; }}

.mc-accent-dot {{ position: absolute; top: 18px; right: 18px; width: 8px; height: 8px; border-radius: 50%; }}

/* Pump specific */
.pump-orb {{ width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; margin-bottom: 12px; }}
.pump-orb-on {{ background: {C['orange']}20; box-shadow: 0 0 20px {C['orange']}35, 0 0 0 1px {C['orange']}25; }}
.pump-orb-off {{ background: #1E1E1E; }}
.pump-state {{ font-size: 18px; font-weight: 700; line-height: 1; margin-bottom: 4px; }}
.pump-state-on {{ color: {C['orange']}; }}
.pump-state-off {{ color: #555555; }}

/* Badges & Tables */
.badge {{ display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; }}
.badge-live {{ background: {C['orange_dim']}; color: {C['orange']}; border: 1px solid {C['orange']}30; }}
.badge-good {{ background: #22C55E18; color: #16A34A; border: 1px solid #22C55E32; }}
.badge-warn {{ background: #EAB30818; color: #CA8A04; border: 1px solid #EAB30832; }}
.badge-dry {{ background: #EF444418; color: #EF4444; border: 1px solid #EF444432; }}

.tbl-wrap {{ background: {C['section_bg']}; border: 1px solid {C['border']}; border-radius: 14px; overflow: hidden; }}
.tbl {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
.tbl th {{ text-align: left; padding: 11px 16px; font-size: 10px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: {C['text_dim']}; border-bottom: 1px solid {C['border']}; }}
.tbl td {{ padding: 10px 16px; border-bottom: 1px solid #F0EDE8; }}

.gap-lg {{ height: 48px; }}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=REFRESH_SEC)
def fetch_latest():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/sensor_data", headers=HEADERS, params={"select": "*", "order": "created_at.desc", "limit": "1"}, timeout=5)
        if r.status_code == 200 and r.json(): return r.json()[0]
    except: pass
    return None

@st.cache_data(ttl=REFRESH_SEC)
def fetch_history(n=40):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/sensor_data", headers=HEADERS, params={"select": "*", "order": "created_at.desc", "limit": str(n)}, timeout=5)
        if r.status_code == 200 and r.json():
            rows = r.json(); rows.reverse(); return rows
    except: pass
    return []

def fmt_time(iso):
    if not iso: return "—"
    try: return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%H:%M:%S")
    except: return str(iso)[:19]

def classify(sp, tp, hp):
    if sp < 30: return "dry", "Irrigating", C["red"]
    if tp > 35 and hp < 40: return "warn", "Harsh conditions", C["amber"]
    return "good", "Healthy", C["green"]

def last_irrigated(history):
    for row in reversed(history):
        if bool(row["led"]): return fmt_time(row["created_at"])
    return "No record"

def pct_bar(val, mn, mx, color, dark=False):
    p = max(0, min(100, (val - mn) / (mx - mn) * 100))
    cls, fill_cls = ("dc-bar", "dc-bar-fill") if dark else ("mc-bar", "mc-bar-fill")
    return f'<div class="{cls}"><div class="{fill_cls}" style="width:{p:.1f}%;background:{color}"></div></div>'

# ── Data Pull ─────────────────────────────────────────────────────────────────
latest = fetch_latest()
history = fetch_history(40)

sp  = float(latest["soilpercent"]) if latest else 0.0
raw = int(latest["soilmoist"]) if latest else 0
tp  = float(latest["temperature"]) if latest else 0.0
hp  = float(latest["humidity"]) if latest else 0.0
led = bool(latest["led"]) if latest else False
ts  = latest["created_at"] if latest else None
cls, status_label, status_color = classify(sp, tp, hp)

# ── Navbar & Header ───────────────────────────────────────────────────────────
st.markdown(f"""
<div class="bb-nav">
  <div class="bb-logo"><div class="bb-logo-icon">🌱</div>BloomBot</div>
  <div><span class="badge badge-live">● Live Updating</span></div>
</div>
<div style="padding: 36px 40px 10px;">
  <div class="eyebrow">[ Live Sensor Feed ]</div>
  <div class="section-h">Monitoring & Control</div>
  <div class="section-p">Precision agriculture oversight from the MCC-MRF sensor node.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="padding: 0 40px;">', unsafe_allow_html=True)

# ── Sensor Readings (Light Cards) ─────────────────────────────────────────────
st.markdown('<div class="eyebrow" style="margin-top:20px;">Sensor Readings</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    sc = C["red"] if sp < 30 else (C["amber"] if sp < 50 else C["green"])
    st.markdown(f"""
    <div class="mc">
      <div class="mc-accent-dot" style="background:{sc}"></div>
      <div class="mc-label">Soil Moisture</div>
      <div class="mc-val">{sp:.0f}<span class="mc-unit">%</span></div>
      <div class="mc-sub">Raw ADC {raw} · Dry below 30%</div>
      {pct_bar(sp, 0, 100, sc)}
    </div>
    """, unsafe_allow_html=True)

with c2:
    tc = C["red"] if tp > 35 else C["orange"]
    st.markdown(f"""
    <div class="mc">
      <div class="mc-accent-dot" style="background:{tc}"></div>
      <div class="mc-label">Temperature</div>
      <div class="mc-val">{tp:.1f}<span class="mc-unit">°C</span></div>
      <div class="mc-sub">{"High — watch roots" if tp > 35 else "Normal range"}</div>
      {pct_bar(tp, 0, 50, tc)}
    </div>
    """, unsafe_allow_html=True)

with c3:
    hc = C["teal"] if hp >= 40 else C["amber"]
    st.markdown(f"""
    <div class="mc">
      <div class="mc-accent-dot" style="background:{hc}"></div>
      <div class="mc-label">Air Humidity</div>
      <div class="mc-val">{hp:.1f}<span class="mc-unit">%</span></div>
      <div class="mc-sub">{"Dry air — monitor closely" if hp < 40 else "Good humidity"}</div>
      {pct_bar(hp, 0, 100, hc)}
    </div>
    """, unsafe_allow_html=True)

# ── Farm Management (Dark Cards) ──────────────────────────────────────────────
st.markdown('<div class="eyebrow" style="margin-top:40px;">Farm Management</div>', unsafe_allow_html=True)
d1, d2, d3, d4, d5 = st.columns(5, gap="medium")

with d1:
    dsc = C["red"] if sp < 30 else (C["amber"] if sp < 50 else C["green"])
    st.markdown(f"""
    <div class="dark-card">
      <div class="dc-label">Soil Moisture</div>
      <div class="dc-val">{sp:.0f}<span class="dc-unit">%</span></div>
      <div class="dc-sub">Raw ADC: {raw}</div>
      {pct_bar(sp, 0, 100, dsc, dark=True)}
    </div>
    """, unsafe_allow_html=True)

with d2:
    dtc = C["red"] if tp > 35 else C["orange"]
    st.markdown(f"""
    <div class="dark-card">
      <div class="dc-label">Temperature</div>
      <div class="dc-val">{tp:.1f}<span class="dc-unit">°C</span></div>
      <div class="dc-sub">{"⚠ High" if tp > 35 else "Normal"}</div>
      {pct_bar(tp, 0, 50, dtc, dark=True)}
    </div>
    """, unsafe_allow_html=True)

with d3:
    dhc = C["teal"] if hp >= 40 else C["amber"]
    st.markdown(f"""
    <div class="dark-card">
      <div class="dc-label">Air Humidity</div>
      <div class="dc-val">{hp:.1f}<span class="dc-unit">%</span></div>
      <div class="dc-sub">{"⚠ Dry" if hp < 40 else "Normal"}</div>
      {pct_bar(hp, 0, 100, dhc, dark=True)}
    </div>
    """, unsafe_allow_html=True)

with d4:
    orb_cls, state_cls, p_icon, p_lbl = ("pump-orb-on", "pump-state-on", "💧", "ON") if led else ("pump-orb-off", "pump-state-off", "🌿", "STANDBY")
    st.markdown(f"""
    <div class="pump-card">
      <div class="dc-label">Pump Status</div>
      <div class="pump-orb {orb_cls}">{p_icon}</div>
      <div class="pump-state {state_cls}">{p_lbl}</div>
      <div class="dc-sub" style="margin-top:auto;">Auto-controlled</div>
    </div>
    """, unsafe_allow_html=True)

with d5:
    last_time = last_irrigated(history)
    st.markdown(f"""
    <div class="dark-card">
      <div class="dc-label">Last Irrigated</div>
      <div class="dc-val" style="font-size:32px; padding-top:6px;">{last_time}</div>
      <div class="dc-sub">Most recent ON event</div>
      <div class="dc-bar"><div class="dc-bar-fill" style="width:100%;background:{C['teal']};"></div></div>
    </div>
    """, unsafe_allow_html=True)

# ── Analytics ─────────────────────────────────────────────────────────────────
st.markdown('<div class="gap-lg"></div><div class="eyebrow">Analytics</div>', unsafe_allow_html=True)

if history:
    times = [fmt_time(r["created_at"]) for r in history]
    soils = [float(r["soilpercent"]) for r in history]
    temps = [float(r["temperature"]) for r in history]
    humids = [float(r["humidity"]) for r in history]

    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor="#FFF", paper_bgcolor="#FFF", height=280,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color=C["text_dim"])),
        yaxis=dict(showgrid=True, gridcolor="#F0EDE8", tickfont=dict(size=10, color=C["text_dim"])),
        legend=dict(orientation="h", y=1.15), hovermode="x unified"
    )
    
    # Bug Fix applied here: valid rgba string instead of hex formatting error
    fig.add_trace(go.Scatter(x=times, y=soils, name="Soil %", line=dict(color=C["orange"], width=2), fill="tozeroy", fillcolor="rgba(249, 115, 22, 0.08)"))
    fig.add_trace(go.Scatter(x=times, y=humids, name="Humidity %", line=dict(color=C["teal"], width=2)))
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown('</div>', unsafe_allow_html=True)

# ── Auto-Refresh Loop ──
time.sleep(REFRESH_SEC)
st.rerun()
