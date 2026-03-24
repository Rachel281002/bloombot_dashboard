"""
BloomBot — Live Sensor Dashboard
Aesthetic: solar.tremor.so — cream background, dark farm-management section,
           orange F97316 accent, Inter font, minimal spline charts
Install:   pip install streamlit requests plotly
Run:       streamlit run bloombot_dashboard.py
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

# ── Design tokens (extracted from solar.tremor.so) ────────────────────────────
C = {
    "page_bg":    "#F5F4F0",   # warm cream — page background
    "section_bg": "#FFFFFF",   # pure white cards / light sections
    "dark_bg":    "#0D0D0D",   # near-black "Farm Management" section
    "dark_card":  "#151515",   # slightly lighter dark card
    "orange":     "#F97316",   # Solar brand orange — primary accent
    "orange_dim": "#F9731620", # orange at 12% opacity
    "teal":       "#14B8A6",   # chart line 2 / accents
    "amber":      "#EAB308",   # chart line 3 / warning
    "red":        "#EF4444",   # danger
    "green":      "#22C55E",   # good status
    "border":     "#E8E6E1",   # light card border
    "dark_border":"#222222",   # dark section border
    "text_h":     "#111111",   # headings
    "text_b":     "#6B6660",   # body
    "text_dim":   "#A09C98",   # dimmed labels
    "text_dark":  "#FFFFFF",   # text on dark bg
    "text_dark2": "#888888",   # muted text on dark bg
}

# ── Master CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

/* Reset & globals */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, .block-container {{
    background-color: {C['page_bg']} !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: {C['text_h']} !important;
}}

/* Hide Streamlit chrome completely */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="collapsedControl"] {{ display: none !important; visibility: hidden !important; }}

/* Block container full-width */
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
[data-testid="stMain"] > div {{ padding: 0 !important; }}
section[data-testid="stMain"] {{ background: {C['page_bg']} !important; }}

/* Plotly chart bg transparency */
.js-plotly-plot .plotly, .js-plotly-plot .plotly .bg {{
    background: transparent !important;
}}
.modebar-container {{ display: none !important; }}

/* ── Navbar ── */
.bb-nav {{
    background: {C['section_bg']};
    border-bottom: 1px solid {C['border']};
    padding: 0 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
    gap: 16px;
    flex-wrap: wrap;
}}
.bb-logo {{
    display: flex; align-items: center; gap: 8px;
    text-decoration: none;
}}
.bb-logo-icon {{
    width: 28px; height: 28px; border-radius: 6px;
    background: {C['orange']};
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
}}
.bb-logo-text {{
    font-size: 15px; font-weight: 700;
    color: {C['text_h']}; letter-spacing: -0.02em;
}}
.bb-nav-links {{
    display: flex; align-items: center; gap: 28px;
    font-size: 13px; color: {C['text_dim']};
}}
.bb-nav-links .active {{ color: {C['text_h']}; font-weight: 500; }}
.bb-nav-right {{
    display: flex; align-items: center; gap: 10px;
}}

/* ── Eyebrow label ── */
.eyebrow {{
    display: inline-block;
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: {C['orange']};
    margin-bottom: 7px;
}}
.eyebrow-bracket::before {{ content: '['; margin-right: 2px; }}
.eyebrow-bracket::after  {{ content: ']'; margin-left: 2px; }}

/* ── Section headings ── */
.section-h {{
    font-size: 26px; font-weight: 700;
    color: {C['text_h']}; letter-spacing: -0.03em;
    line-height: 1.2; margin-bottom: 5px;
}}
.section-p {{
    font-size: 13px; color: {C['text_b']};
    line-height: 1.6; margin-bottom: 0;
}}
.section-h-dark {{
    font-size: 26px; font-weight: 700;
    color: #FFFFFF; letter-spacing: -0.03em;
    line-height: 1.2; margin-bottom: 5px;
    text-align: center;
}}
.section-p-dark {{
    font-size: 13px; color: {C['text_dark2']};
    line-height: 1.6; text-align: center;
}}

/* ── Metric card (light) ── */
.mc {{
    background: {C['section_bg']};
    border: 1px solid {C['border']};
    border-radius: 14px;
    padding: 22px 20px 18px;
    height: 100%;
    position: relative;
    transition: box-shadow 0.2s;
}}
.mc:hover {{ box-shadow: 0 4px 24px rgba(0,0,0,0.06); }}
.mc-label {{
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: {C['text_dim']}; margin-bottom: 12px;
}}
.mc-val {{
    font-size: 48px; font-weight: 700;
    line-height: 1; letter-spacing: -0.04em;
    color: {C['text_h']};
}}
.mc-unit {{
    font-size: 20px; font-weight: 300;
    color: {C['text_dim']}; margin-left: 2px;
}}
.mc-sub {{
    font-size: 12px; color: {C['text_dim']};
    margin-top: 10px; line-height: 1.4;
}}
.mc-bar {{
    height: 3px; background: {C['border']};
    border-radius: 2px; margin-top: 16px; overflow: hidden;
}}
.mc-bar-fill {{ height: 100%; border-radius: 2px; }}
.mc-accent-dot {{
    position: absolute; top: 18px; right: 18px;
    width: 8px; height: 8px; border-radius: 50%;
}}

/* ── Status badges ── */
.badge {{
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 20px;
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.06em; text-transform: uppercase;
    white-space: nowrap;
}}
.badge-live   {{ background: {C['orange_dim']}; color: {C['orange']};
                 border: 1px solid {C['orange']}30; }}
.badge-dry    {{ background: #EF444418; color: #EF4444;
                 border: 1px solid #EF444432; }}
.badge-good   {{ background: #22C55E18; color: #16A34A;
                 border: 1px solid #22C55E32; }}
.badge-warn   {{ background: #EAB30818; color: #CA8A04;
                 border: 1px solid #EAB30832; }}

/* ── Dark section (Farm Management) ── */
.dark-section {{
    background: {C['dark_bg']};
    padding: 48px 40px 52px;
    margin: 0 -100vw;
    padding-left: calc(40px + 100vw - 100%);
    padding-right: calc(40px + 100vw - 100%);
}}
.dark-card {{
    background: {C['dark_card']};
    border: 1px solid {C['dark_border']};
    border-radius: 16px;
    padding: 28px 24px;
    height: 100%;
    position: relative;
    overflow: hidden;
}}
.dark-card::after {{
    content: '';
    position: absolute;
    top: 0; left: 24px; right: 24px; height: 1px;
    background: linear-gradient(90deg, transparent, {C['orange']}30, transparent);
}}
.dc-label {{
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: {C['text_dark2']}; margin-bottom: 14px;
}}
.dc-val {{
    font-size: 44px; font-weight: 700;
    line-height: 1; letter-spacing: -0.04em;
    color: #FFFFFF;
}}
.dc-unit {{
    font-size: 18px; font-weight: 300;
    color: {C['text_dark2']}; margin-left: 2px;
}}
.dc-sub {{
    font-size: 12px; color: {C['text_dark2']};
    margin-top: 10px;
}}
.dc-bar {{
    height: 2px; background: #222;
    border-radius: 2px; margin-top: 18px; overflow: hidden;
}}
.dc-bar-fill {{ height: 100%; border-radius: 2px; }}

/* Pump status card */
.pump-card {{
    background: {C['dark_card']};
    border: 1px solid {C['dark_border']};
    border-radius: 16px;
    padding: 28px 24px;
    height: 100%;
    position: relative;
    overflow: hidden;
}}
.pump-card::after {{
    content: '';
    position: absolute;
    top: 0; left: 24px; right: 24px; height: 1px;
    background: linear-gradient(90deg, transparent, {C['orange']}40, transparent);
}}
.pump-orb {{
    width: 64px; height: 64px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; margin-bottom: 14px;
}}
.pump-orb-on  {{
    background: {C['orange']}20;
    box-shadow: 0 0 32px {C['orange']}35, 0 0 0 1px {C['orange']}25;
}}
.pump-orb-off {{
    background: #1E1E1E;
    box-shadow: none;
}}
.pump-state {{
    font-size: 20px; font-weight: 700; line-height: 1;
    margin-bottom: 6px;
}}
.pump-state-on  {{ color: {C['orange']}; }}
.pump-state-off {{ color: #444444; }}
.pump-detail {{ font-size: 12px; color: {C['text_dark2']}; line-height: 1.5; }}

/* ── Data table ── */
.tbl-wrap {{
    background: {C['section_bg']};
    border: 1px solid {C['border']};
    border-radius: 14px;
    overflow: hidden;
}}
.tbl {{
    width: 100%; border-collapse: collapse;
    font-size: 12.5px; font-family: 'Inter', sans-serif;
}}
.tbl th {{
    text-align: left; padding: 11px 16px;
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: {C['text_dim']};
    border-bottom: 1px solid {C['border']};
    background: {C['page_bg']};
}}
.tbl td {{
    padding: 10px 16px; color: {C['text_b']};
    border-bottom: 1px solid #F0EDE8;
    font-variant-numeric: tabular-nums;
}}
.tbl tr:last-child td {{ border-bottom: none; }}
.tbl tr:hover td {{ background: #FAF9F6; }}
.tbl td.bright {{ color: {C['text_h']}; font-weight: 500; }}

/* ── Spacing ── */
.bb-divider {{ height: 1px; background: {C['border']}; margin: 0; border: none; }}
.gap-sm  {{ height: 16px; }}
.gap-md  {{ height: 28px; }}
.gap-lg  {{ height: 48px; }}

.timestrip {{
    display: flex; align-items: center; gap: 20px;
    flex-wrap: wrap; font-size: 11.5px; color: {C['text_dim']};
    padding: 12px 0 0;
}}
.timestrip strong {{ color: {C['text_h']}; font-weight: 500; }}

::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {C['border']}; border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)

# ── Data helpers ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=REFRESH_SEC)
def fetch_latest():
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/sensor_data",
            headers=HEADERS,
            params={"select": "*", "order": "created_at.desc", "limit": "1"},
            timeout=5,
        )
        if r.status_code == 200 and r.json():
            return r.json()[0]
    except:
        pass
    return None

@st.cache_data(ttl=REFRESH_SEC)
def fetch_history(n=40):
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/sensor_data",
            headers=HEADERS,
            params={"select": "*", "order": "created_at.desc", "limit": str(n)},
            timeout=5,
        )
        if r.status_code == 200 and r.json():
            rows = r.json(); rows.reverse(); return rows
    except:
        pass
    return []

def fmt_time(iso):
    if not iso: return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except:
        return str(iso)[:19]

def classify(sp, tp, hp):
    if sp < 30:              return "dry",  "Irrigating",        C["red"]
    if tp > 35 and hp < 40: return "warn", "Harsh conditions",  C["amber"]
    return "good", "Healthy", C["green"]

def last_irrigated(history):
    """Find most recent row where pump was ON."""
    for row in reversed(history):
        if bool(row["led"]):
            return fmt_time(row["created_at"])
    return "No record yet"

def pct_bar(val, mn, mx, color, dark=False):
    p = max(0, min(100, (val - mn) / (mx - mn) * 100))
    cls = "dc-bar" if dark else "mc-bar"
    fill_cls = "dc-bar-fill" if dark else "mc-bar-fill"
    return (f'<div class="{cls}"><div class="{fill_cls}" '
            f'style="width:{p:.1f}%;background:{color}"></div></div>')

# ── Pull data ─────────────────────────────────────────────────────────────────
latest  = fetch_latest()
history = fetch_history(40)

sp   = float(latest["soilpercent"])  if latest else 0.0
raw  = int(latest["soilmoist"])      if latest else 0
tp   = float(latest["temperature"])  if latest else 0.0
hp   = float(latest["humidity"])     if latest else 0.0
led  = bool(latest["led"])           if latest else False
ts   = latest["created_at"]          if latest else None
cls, status_label, status_color = classify(sp, tp, hp)

# ═══════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ═══════════════════════════════════════════════════════════════════════════════
live_dot = f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{C["orange"]};margin-right:5px;box-shadow:0 0 6px {C["orange"]}80;"></span>'

st.markdown(f"""
<div class="bb-nav">
  <div class="bb-logo">
    <div class="bb-logo-icon">🌱</div>
    <div class="bb-logo-text">BloomBot</div>
  </div>
  <div class="bb-nav-links">
    <span class="active">Live Monitor</span>
    <span>Farm Map</span>
    <span>Analytics</span>
  </div>
  <div class="bb-nav-right">
    <span class="badge badge-live">{live_dot}Live</span>
    <span style="font-size:11px;color:{C['text_dim']};margin-left:4px;">
      {fmt_time(ts)}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BODY WRAPPER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="padding: 36px 40px 60px;">', unsafe_allow_html=True)

# ── Hero heading ──────────────────────────────────────────────────────────────
col_hero, col_status = st.columns([2, 1], gap="large")
with col_hero:
    n_readings = len(history)
    st.markdown(f"""
    <div class="eyebrow eyebrow-bracket">Live Sensor Feed</div>
    <div class="section-h">Monitoring &amp; Control<br>for Precision Agriculture</div>
    <div class="section-p" style="margin-top:8px;">
      Complete oversight of your campus garden — soil, climate, and irrigation
      status delivered in real time from the MCC-MRF sensor node.
    </div>
    """, unsafe_allow_html=True)

with col_status:
    st.markdown(f"""
    <div style="padding-top:10px;display:flex;flex-direction:column;gap:8px;align-items:flex-end;">
      <span class="badge badge-{cls}" style="font-size:11px;padding:5px 14px;">
        ● {status_label}
      </span>
      <div class="timestrip" style="justify-content:flex-end;">
        <span>Readings: <strong>{n_readings}</strong></span>
        <span>Node: <strong>MCC-MRF</strong></span>
        <span>Refresh: <strong>{REFRESH_SEC}s</strong></span>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="gap-lg"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# METRIC CARDS — light bg section
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="eyebrow">Sensor Readings</div>
<div style="height:10px"></div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    sc  = C["red"] if sp < 30 else (C["amber"] if sp < 50 else C["green"])
    dot = f'<div class="mc-accent-dot" style="background:{sc};{"box-shadow:0 0 8px "+sc+"60" if sp<30 else ""}"></div>'
    st.markdown(f"""
    <div class="mc">
      {dot}
      <div class="mc-label">Soil Moisture</div>
      <div class="mc-val">{sp:.0f}<span class="mc-unit">%</span></div>
      <div class="mc-sub">Raw ADC {raw} &nbsp;·&nbsp; Dry below 30%</div>
      {pct_bar(sp, 0, 100, sc)}
    </div>
    """, unsafe_allow_html=True)

with c2:
    tc  = C["red"] if tp > 35 else C["orange"]
    tn  = "High — watch roots" if tp > 35 else "Normal range"
    st.markdown(f"""
    <div class="mc">
      <div class="mc-accent-dot" style="background:{tc}"></div>
      <div class="mc-label">Temperature</div>
      <div class="mc-val">{tp:.1f}<span class="mc-unit">°C</span></div>
      <div class="mc-sub">{tn} &nbsp;·&nbsp; Threshold 35°C</div>
      {pct_bar(tp, 0, 50, tc)}
    </div>
    """, unsafe_allow_html=True)

with c3:
    hc  = C["teal"] if hp >= 40 else C["amber"]
    hn  = "Dry air — monitor closely" if hp < 40 else "Good humidity"
    st.markdown(f"""
    <div class="mc">
      <div class="mc-accent-dot" style="background:{hc}"></div>
      <div class="mc-label">Air Humidity</div>
      <div class="mc-val">{hp:.1f}<span class="mc-unit">%</span></div>
      <div class="mc-sub">{hn} &nbsp;·&nbsp; Threshold 40%</div>
      {pct_bar(hp, 0, 100, hc)}
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="gap-lg"></div>', unsafe_allow_html=True)
st.markdown('<hr class="bb-divider">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DARK SECTION — Farm Management (Monitoring & Control)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('</div>', unsafe_allow_html=True)  # close light padding

st.markdown(f"""
<div style="background:{C['dark_bg']};padding:52px 40px 56px;">
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align:center;margin-bottom:36px;">
  <div class="eyebrow">Farm Management</div>
  <div class="section-h-dark">System Status &amp; Control</div>
  <div class="section-p-dark">
    Real-time irrigation control &mdash; sensor-triggered, zero manual input required.
  </div>
</div>
""", unsafe_allow_html=True)

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
      <div class="dc-sub">{"⚠ High — above 35°C" if tp > 35 else "Normal range"}</div>
      {pct_bar(tp, 0, 50, dtc, dark=True)}
    </div>
    """, unsafe_allow_html=True)

with d3:
    dhc = C["teal"] if hp >= 40 else C["amber"]
    st.markdown(f"""
    <div class="dark-card">
      <div class="dc-label">Air Humidity</div>
      <div class="dc-val">{hp:.1f}<span class="dc-unit">%</span></div>
      <div class="dc-sub">{"⚠ Dry air" if hp < 40 else "Normal range"}</div>
      {pct_bar(hp, 0, 100, dhc, dark=True)}
    </div>
    """, unsafe_allow_html=True)

with d4:
    orb_cls    = "pump-orb-on"  if led else "pump-orb-off"
    state_cls  = "pump-state-on" if led else "pump-state-off"
    pump_icon  = "💧" if led else "🌿"
    pump_lbl   = "IRRIGATING" if led else "STANDBY"
    pump_info  = f"Soil at {sp:.0f}% — below 30%" if led else f"Soil at {sp:.0f}% — above threshold"
    st.markdown(f"""
    <div class="pump-card">
      <div class="dc-label">Irrigation Pump</div>
      <div class="pump-orb {orb_cls}">{pump_icon}</div>
      <div class="pump-state {state_cls}">{pump_lbl}</div>
      <div class="pump-detail" style="margin-top:6px;">{pump_info}</div>
    </div>
    """, unsafe_allow_html=True)

with d5:
    last_time = last_irrigated(history)
    # Adapted custom widget to seamlessly blend into the dark UI card styling
    st.markdown(f"""
    <div class="dark-card">
      <div class="dc-label">Last Irrigated</div>
      <div class="dc-val" style="font-size:32px; margin-top:8px;">
        {last_time}
      </div>
      <div class="dc-sub">Most recent pump ON event</div>
      <div class="dc-bar">
        <div class="dc-bar-fill" style="width:100%;background:{C['teal']};"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close dark section

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS SECTION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f'<div style="padding: 52px 40px 60px;background:{C["page_bg"]};">', unsafe_allow_html=True)

st.markdown(f"""
<div class="eyebrow">Solar Analytics</div>
<div class="section-h">Turn field data into insights</div>
<div class="section-p" style="margin-top:4px;margin-bottom:28px;">
  Historical sensor readings — moisture, temperature and humidity trends over time.
</div>
""", unsafe_allow_html=True)

PLOT_BG    = C["section_bg"]
GRID_CLR   = "#F0EDE8"
TICK_CLR   = "#C8C4BE"
FONT_CLR   = "#A09C98"
HOVER_BG   = "#FFFFFF"
HOVER_FONT = "#111111"

def base_fig(height=260):
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, height=height,
        font=dict(family="Inter", color=FONT_CLR, size=11),
        margin=dict(l=4, r=4, t=8, b=8),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, tickfont=dict(size=10, color=TICK_CLR), tickcolor=TICK_CLR, linecolor=GRID_CLR),
        yaxis=dict(showgrid=True, gridcolor=GRID_CLR, gridwidth=1, zeroline=False, showline=False, tickfont=dict(size=10, color=TICK_CLR)),
        legend=dict(orientation="h", x=1, xanchor="right", y=1.12, font=dict(size=10, color=FONT_CLR), bgcolor="rgba(0,0,0,0)", itemsizing="constant"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=HOVER_BG, bordercolor=C["border"], font=dict(color=HOVER_FONT, size=11, family="Inter")),
    )
    return fig

if history:
    times  = [fmt_time(r["created_at"])  for r in history]
    soils  = [float(r["soilpercent"])    for r in history]
    temps  = [float(r["temperature"])    for r in history]
    humids = [float(r["humidity"])       for r in history]
    leds   = [1 if r["led"] else 0       for r in history]

    fig_main = base_fig(height=280)
    fig_main.add_trace(go.Scatter(x=times, y=soils, name="Soil Moisture %", line=dict(color=C["orange"], width=2.5, shape="spline", smoothing=0.6), fill="tozeroy", fillcolor=f"{C['orange']}0D", hovertemplate="<b>%{y:.1f}%</b>", mode="lines"))
    fig_main.add_trace(go.Scatter(x=times, y=humids, name="Humidity %", line=dict(color=C["teal"], width=2, shape="spline", smoothing=0.6), hovertemplate="<b>%{y:.1f}%</b>", mode="lines"))
    fig_main.add_trace(go.Scatter(x=times, y=temps, name="Temperature °C", line=dict(color=C["amber"], width=1.5, shape="spline", smoothing=0.6, dash="dot"), hovertemplate="<b>%{y:.1f}°C</b>", mode="lines", yaxis="y2"))
    fig_main.add_hline(y=30, line=dict(color=C["red"], width=1, dash="dash"), opacity=0.35, annotation_text="dry threshold", annotation_font_size=9, annotation_font_color=C["red"])
    fig_main.update_layout(
        yaxis=dict(range=[0, 105], showgrid=True, gridcolor=GRID_CLR, tickfont=dict(size=10, color=TICK_CLR)),
        yaxis2=dict(overlaying="y", side="right", range=[0, 55], showgrid=False, zeroline=False, showline=False, tickfont=dict(size=10, color=TICK_CLR)),
    )
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig_main, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    cc1, cc2 = st.columns(2, gap="medium")
    with cc1:
        st.markdown('<div class="eyebrow" style="font-size:10px;margin-bottom:10px;">Irrigation Events</div>', unsafe_allow_html=True)
        fig_pump = base_fig(height=200)
        bar_colors = [f"{C['orange']}90" if v else "#EBEBEB" for v in leds]
        fig_pump.add_trace(go.Bar(x=times, y=leds, name="Pump", marker=dict(color=bar_colors, line=dict(width=0), cornerradius=3), hovertemplate="Pump: <b>%{customdata}</b>", customdata=["ON" if v else "OFF" for v in leds]))
        fig_pump.update_layout(yaxis=dict(tickvals=[0, 1], ticktext=["Off", "On"], range=[-0.15, 1.6], showgrid=False, tickfont=dict(size=10, color=TICK_CLR)), bargap=0.35, showlegend=False)
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_pump, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with cc2:
        st.markdown('<div class="eyebrow" style="font-size:10px;margin-bottom:10px;">Soil vs Humidity Scatter</div>', unsafe_allow_html=True)
        fig_sc = base_fig(height=200)
        fig_sc.add_trace(go.Scatter(x=soils, y=humids, mode="markers+lines", name="", marker=dict(color=C["orange"], size=6, line=dict(width=1, color="#FFFFFF")), line=dict(color=C["orange"], width=1, dash="dot"), hovertemplate="Soil: <b>%{x:.0f}%</b> · Humidity: <b>%{y:.1f}%</b>"))
        fig_sc.update_layout(
            xaxis=dict(title=dict(text="Soil %", font=dict(size=10, color=FONT_CLR)), tickfont=dict(size=10, color=TICK_CLR), showgrid=False),
            yaxis=dict(title=dict(text="Humidity %", font=dict(size=10, color=FONT_CLR)), gridcolor=GRID_CLR, tickfont=dict(size=10, color=TICK_CLR)),
            showlegend=False,
        )
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_sc, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="background:{C["section_bg"]};border:1px solid {C["border"]}; border-radius:14px;padding:48px;text-align:center; color:{C["text_dim"]};font-size:13px;">Waiting for sensor data from Supabase…</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOG TABLE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="gap-lg"></div><hr class="bb-divider"><div class="gap-md"></div>', unsafe_allow_html=True)
st.markdown('<div class="eyebrow">Data Log</div><div class="section-h" style="font-size:22px;">Recent readings</div><div style="height:16px"></div>', unsafe_allow_html=True)

if history:
    rows_html = ""
    for row in reversed(history[-12:]):
        sp_r, tp_r, hp_r = float(row["soilpercent"]), float(row["temperature"]), float(row["humidity"])
        ts_r, led_r = fmt_time(row["created_at"]), bool(row["led"])
        cl_r, lb_r, _ = classify(sp_r, tp_r, hp_r)
        pump_badge = f'<span class="badge badge-live">On</span>' if led_r else f'<span class="badge badge-good">Off</span>'
        rows_html += f'<tr><td class="bright">{ts_r}</td><td class="bright">{sp_r:.0f}%</td><td>{int(row["soilmoist"])}</td><td>{tp_r:.1f} °C</td><td>{hp_r:.1f}%</td><td><span class="badge badge-{cl_r}">{lb_r}</span></td><td>{pump_badge}</td></tr>'

    st.markdown(f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Time</th><th>Soil %</th><th>Raw ADC</th><th>Temp</th><th>Humidity</th><th>Status</th><th>Pump</th></tr></thead><tbody>{rows_html}</tbody></table></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="tbl-wrap" style="padding:32px;text-align:center;color:{C["text_dim"]};font-size:13px;">No readings yet.</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close main wrapper
# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-REFRESH LOOP
# ═══════════════════════════════════════════════════════════════════════════════
time.sleep(REFRESH_SEC)
st.rerun()
