"""
===============================================
ESTATE 2026 - DASHBOARD ANALYTICS
===============================================
Developed by Samuele Felici
© 2026 — All rights reserved
===============================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from datetime import datetime
from io import BytesIO
import base64, os

# --------------------------------------------------
# CONFIGURAZIONE PAGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Estate 2026 - Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚍"
)

# --------------------------------------------------
# MAPPA COLORI DEPOSITI
# --------------------------------------------------
COLORI_DEPOSITI = {
    "ancona":                   "#22c55e",
    "polverigi":                "#166534",
    "marina":                   "#ec4899",
    "marina di montemarciano":  "#ec4899",
    "filottrano":               "#a855f7",
    "jesi":                     "#f97316",
    "osimo":                    "#eab308",
    "castelfidardo":            "#38bdf8",
    "castelfdardo":             "#38bdf8",
    "ostra":                    "#ef4444",
    "belvedere ostrense":       "#94a3b8",
    "belvedereostrense":        "#94a3b8",
    "depbelvede":               "#94a3b8",
    "moie":                     "#a78bfa",
}

def get_colore_deposito(dep: str) -> str:
    return COLORI_DEPOSITI.get(str(dep).strip().lower(), "#64748b")

def hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# --------------------------------------------------
# LOGIN
# --------------------------------------------------
def check_password():
    if st.session_state.get("password_correct"):
        return True

    logo_b64 = ""
    try:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logoanalytic.png")
        with open(p, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
    except Exception:
        pass

    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stHeader"]  { display: none !important; }
    footer { display: none !important; }
    .block-container { padding-top: 0 !important; max-width: 100% !important; }
    .stApp { background: #0d1117 !important; }

    @keyframes gridPulse { 0%, 100% { opacity: 0.05; } 50% { opacity: 0.12; } }
    @keyframes warmGlow {
        0%, 100% { transform: translate(-50%, -50%) scale(1);   opacity: 0.35; }
        50%       { transform: translate(-50%, -50%) scale(1.08); opacity: 0.55; }
    }
    @keyframes rise {
        0%   { transform: translateY(0); opacity: 0; }
        10%  { opacity: 0.7; }
        90%  { opacity: 0.4; }
        100% { transform: translateY(-100vh); opacity: 0; }
    }
    @keyframes twinkle { 0%, 100% { opacity: 0.15; } 50% { opacity: 0.8; } }

    .ca-bg-grid {
        position: fixed; inset: 0; z-index: 0; pointer-events: none;
        background-image:
            linear-gradient(rgba(245,166,35,0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(245,166,35,0.04) 1px, transparent 1px);
        background-size: 56px 56px;
        animation: gridPulse 6s ease-in-out infinite;
    }
    .ca-bg-glow {
        position: fixed; top: 50%; left: 50%;
        width: 700px; height: 500px;
        background: radial-gradient(ellipse,
            rgba(245,166,35,0.12) 0%, rgba(13,17,23,0.4) 50%, transparent 70%);
        animation: warmGlow 8s ease-in-out infinite;
        pointer-events: none; z-index: 0;
    }
    .ca-particle { position: fixed; border-radius: 50%; animation: rise linear infinite; pointer-events: none; z-index: 0; }
    .ca-star { position: fixed; width: 2px; height: 2px; background: rgba(245,166,35,0.6); border-radius: 50%; animation: twinkle ease-in-out infinite; pointer-events: none; z-index: 0; }

    div[data-testid="stTextInput"] > div > div {
        background: rgba(13, 17, 23, 0.95) !important;
        border: 1px solid rgba(245,166,35,0.3) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stTextInput"] > div > div:focus-within {
        border-color: rgba(245,166,35,0.7) !important;
        box-shadow: 0 0 0 3px rgba(245,166,35,0.1) !important;
    }
    div[data-testid="stTextInput"] input {
        color: #ECF0F1 !important; font-size: 1rem !important; letter-spacing: 2px !important;
    }
    div[data-testid="stTextInput"] label { display: none !important; }

    .ca-logo-img { transition: filter 0.3s ease; cursor: default; }
    .ca-logo-img:hover {
        filter: drop-shadow(0 0 20px rgba(245,166,35,0.4)) brightness(1.05);
    }

    .ca-security {
        position: fixed; bottom: 0; left: 0; right: 0;
        padding: 10px 20px;
        background: rgba(13,17,23,0.95);
        border-top: 1px solid rgba(245,166,35,0.15);
        backdrop-filter: blur(10px);
        z-index: 9999;
    }
    .ca-security-row { display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap; }
    .ca-security-item {
        color: rgba(176,190,197,0.85); font-size: 0.7rem; letter-spacing: 1.5px;
        text-transform: uppercase; display: flex; align-items: center; gap: 6px;
    }
    .ca-security-item svg { color: rgba(245,166,35,0.6); }
    .ca-sep { color: rgba(245,166,35,0.3); font-size: 0.8rem; }
    </style>

    <div class="ca-bg-grid"></div>
    <div class="ca-bg-glow"></div>
    <div class="ca-star" style="top:8%;left:15%;animation-duration:3s;animation-delay:0s;"></div>
    <div class="ca-star" style="top:22%;left:78%;animation-duration:4s;animation-delay:1s;"></div>
    <div class="ca-star" style="top:55%;left:92%;animation-duration:2.5s;animation-delay:0.5s;"></div>
    <div class="ca-star" style="top:72%;left:5%;animation-duration:5s;animation-delay:2s;"></div>
    <div class="ca-star" style="top:35%;left:32%;animation-duration:4.5s;animation-delay:0.8s;"></div>
    <div class="ca-star" style="top:15%;left:62%;animation-duration:2.8s;animation-delay:2.5s;"></div>
    <div class="ca-particle" style="width:3px;height:3px;background:#F5A623;left:10%;bottom:0;animation-duration:9s;animation-delay:0s;"></div>
    <div class="ca-particle" style="width:2px;height:2px;background:#FFB74D;left:30%;bottom:0;animation-duration:12s;animation-delay:2s;"></div>
    <div class="ca-particle" style="width:3px;height:3px;background:#4FC3F7;left:55%;bottom:0;animation-duration:10s;animation-delay:1s;"></div>
    <div class="ca-particle" style="width:2px;height:2px;background:#F5A623;left:75%;bottom:0;animation-duration:11s;animation-delay:3s;"></div>
    <div class="ca-particle" style="width:2px;height:2px;background:#FFB74D;left:90%;bottom:0;animation-duration:13s;animation-delay:1.5s;"></div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<div style='height:18vh'></div>", unsafe_allow_html=True)

        def _entered():
            if st.session_state["_pwd"] == st.secrets["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
            else:
                st.session_state["password_correct"] = False

        st.text_input(
            "Password", type="password", on_change=_entered, key="_pwd",
            placeholder="🔒  Inserisci password", label_visibility="collapsed"
        )

        if st.session_state.get("password_correct") is False:
            st.error("❌ Password errata")

        if logo_b64:
            st.markdown(
                f"<div style='text-align:center; margin-top:28px;'>"
                f"<img class='ca-logo-img' src='data:image/png;base64,{logo_b64}' "
                f"style='height:420px; width:auto; opacity:0.93;'/>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("""
    <div class='ca-security'>
        <div class='ca-security-row'>
            <span class='ca-security-item'>
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                    <rect x="3" y="11" width="18" height="11" rx="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>Connessione cifrata
            </span>
            <span class='ca-sep'>·</span>
            <span class='ca-security-item'>
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>Sistema protetto
            </span>
            <span class='ca-sep'>·</span>
            <span class='ca-security-item'>
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M12 8v4l3 3"/>
                </svg>Estate 2026
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    return False


if not check_password():
    st.stop()


# --------------------------------------------------
# SPLASH SCREEN
# --------------------------------------------------
if not st.session_state.get("splash_done"):
    st.session_state["splash_done"] = True
    st.markdown("""
<style>
[data-testid="stSidebar"]{display:none!important}
[data-testid="stHeader"]{display:none!important}
footer{display:none!important}
.block-container{padding:0!important;max-width:100%!important}
.stApp{background:#0d1117!important;overflow:hidden}

@keyframes fadeOutSplash{0%,75%{opacity:1}100%{opacity:0}}
@keyframes progressFill{from{width:0%}to{width:100%}}
@keyframes pulseCore{
  0%,100%{transform:translate(-50%,-50%) scale(1);box-shadow:0 0 25px 6px rgba(245,166,35,0.6),0 0 60px 20px rgba(245,166,35,0.2)}
  50%{transform:translate(-50%,-50%) scale(1.1);box-shadow:0 0 40px 12px rgba(245,166,35,0.8),0 0 90px 35px rgba(245,166,35,0.3)}}
@keyframes spinR{from{transform:translate(-50%,-50%) rotate(0deg)}to{transform:translate(-50%,-50%) rotate(360deg)}}
@keyframes spinL{from{transform:translate(-50%,-50%) rotate(0deg)}to{transform:translate(-50%,-50%) rotate(-360deg)}}
@keyframes textPulse{0%,100%{opacity:0.4}50%{opacity:1}}

.sp-wrap{position:fixed;inset:0;z-index:99999;background:#0d1117;display:flex;flex-direction:column;align-items:center;justify-content:center;animation:fadeOutSplash 3.2s ease forwards}
.sp-arena{position:relative;width:300px;height:300px;margin-bottom:30px}
.sp-core{position:absolute;top:50%;left:50%;width:36px;height:36px;margin:-18px 0 0 -18px;border-radius:50%;background:radial-gradient(circle,#fff 0%,#FFE0B2 30%,#F5A623 65%,#E65100 100%);animation:pulseCore 2s ease-in-out infinite;z-index:10}
.sp-ring{position:absolute;top:50%;left:50%;border-radius:50%;border:1.5px solid transparent}
.sp-ring-1{width:180px;height:180px;margin:-90px 0 0 -90px;border-top-color:rgba(245,166,35,0.6);animation:spinR 2.5s linear infinite}
.sp-ring-2{width:250px;height:250px;margin:-125px 0 0 -125px;border-right-color:rgba(79,195,247,0.4);animation:spinL 3.5s linear infinite}
.sp-label{color:#B0BEC5;font-size:0.7rem;letter-spacing:3px;text-transform:uppercase;margin:0 0 14px;animation:textPulse 2s ease-in-out infinite}
.sp-bar-wrap{width:200px;height:2px;background:rgba(245,166,35,0.1);border-radius:2px;overflow:hidden}
.sp-bar{height:100%;background:linear-gradient(90deg,#E65100,#F5A623,#E65100);background-size:200% 100%;animation:progressFill 2.8s cubic-bezier(.4,0,.2,1) forwards}
</style>
<div class="sp-wrap">
  <div class="sp-arena">
    <div class="sp-ring sp-ring-1"></div>
    <div class="sp-ring sp-ring-2"></div>
    <div class="sp-core"></div>
  </div>
  <p class="sp-label">Inizializzazione sistema</p>
  <div class="sp-bar-wrap"><div class="sp-bar"></div></div>
</div>
""", unsafe_allow_html=True)
    import time
    time.sleep(3.0)
    st.rerun()


# --------------------------------------------------
# CSS DASHBOARD — TEMA CHIARO
# --------------------------------------------------
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
""", unsafe_allow_html=True)

st.markdown("""<style>
    /* ─── BASE ─── */
    .stApp {
        background: linear-gradient(160deg, #f8f9fc 0%, #eef1f8 50%, #f0f2f7 100%) !important;
        background-attachment: fixed;
    }

    /* ─── TITOLI ─── */
    h1 {
        color: #d4850a !important;
        font-weight: 800 !important;
        letter-spacing: 1px;
        font-size: 2.6rem !important;
    }
    h2 {
        color: #1e293b !important;
        font-weight: 700 !important;
        margin-top: 24px !important;
        font-size: 1.4rem !important;
    }
    h3 {
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    p, span, label {
        color: #475569 !important;
    }

    /* ─── KPI CARDS ─── */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.92) !important;
        padding: 22px 20px;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06), inset 0 1px 0 rgba(255,255,255,0.8);
        border: 1px solid rgba(0, 0, 0, 0.06);
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #F5A623, #4FC3F7);
        opacity: 0;
        transition: opacity 0.25s;
    }
    [data-testid="metric-container"]:hover::before { opacity: 1; }
    [data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(245,166,35,0.12);
        border-color: rgba(245, 166, 35, 0.2);
    }
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #d4850a !important;
        line-height: 1.1 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
    }

    /* ─── TABS ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255, 255, 255, 0.6);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.06);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #64748b !important;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 10px 20px;
        border: 1px solid transparent;
        transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(245,166,35,0.08);
        border-color: rgba(245, 166, 35, 0.2);
        color: #d4850a !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(245,166,35,0.12) !important;
        color: #d4850a !important;
        border-color: rgba(245, 166, 35, 0.25) !important;
    }

    /* ─── SIDEBAR ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        border-right: 1px solid rgba(245, 166, 35, 0.25);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    /* ─── ALERT / BANNER ─── */
    .alert-critical { background: rgba(239,83,80,0.08); padding: 16px 20px; border-radius: 12px; color: #b91c1c; font-size: 0.95rem; margin: 16px 0; border: 1px solid rgba(239,83,80,0.2); border-left: 4px solid #EF5350; }
    .alert-warning  { background: rgba(245,166,35,0.08); padding: 16px 20px; border-radius: 12px; color: #92400e; font-size: 0.95rem; margin: 16px 0; border: 1px solid rgba(245,166,35,0.2); border-left: 4px solid #F5A623; }
    .alert-success  { background: rgba(34,197,94,0.08); padding: 16px 20px; border-radius: 12px; color: #166534; font-size: 0.95rem; margin: 16px 0; border: 1px solid rgba(34,197,94,0.2); border-left: 4px solid #22c55e; }
    .alert-info     { background: rgba(59,130,246,0.08); padding: 16px 20px; border-radius: 12px; color: #1e40af; font-size: 0.95rem; margin: 16px 0; border: 1px solid rgba(59,130,246,0.2); border-left: 4px solid #3b82f6; }

    /* ─── GRAFICI ─── */
    .js-plotly-plot { border-radius: 16px; border: 1px solid rgba(0, 0, 0, 0.06); }

    /* ─── DATAFRAME ─── */
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid rgba(0, 0, 0, 0.06); }

    /* ─── EXPANDER ─── */
    [data-testid="stExpander"] { background: rgba(255, 255, 255, 0.7); border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 12px; }

    /* ─── BOTTONI ─── */
    button {
        background: linear-gradient(135deg, #F5A623 0%, #E65100 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }
    button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(245,166,35,0.3) !important;
    }
    .stDownloadButton button {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: #fff !important;
    }

    /* ─── INPUT ─── */
    input, select, textarea {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #1e293b !important;
        border: 1px solid rgba(0, 0, 0, 0.12) !important;
        border-radius: 8px !important;
    }

    /* ─── INSIGHT CARD ─── */
    .insight-card {
        background: rgba(255, 255, 255, 0.85);
        padding: 18px;
        border-radius: 14px;
        border: 1px solid rgba(245, 166, 35, 0.2);
        margin: 12px 0;
        transition: all 0.2s;
    }
    .insight-card:hover {
        border-color: rgba(245, 166, 35, 0.5);
        box-shadow: 0 4px 16px rgba(245,166,35,0.1);
    }
    .insight-card h4 {
        color: #d4850a !important;
        margin-bottom: 8px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
    }

    /* ─── SEPARATOR ─── */
    hr { border-color: rgba(0, 0, 0, 0.08) !important; margin: 24px 0 !important; }

    /* ─── SECTION HEADER ─── */
    .section-header {
        display: flex; align-items: center; gap: 10px;
        margin: 20px 0 12px; padding-bottom: 8px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    }
    .section-header span {
        font-size: 1.05rem !important; font-weight: 700 !important;
        color: #1e293b !important; letter-spacing: 0.4px;
    }
    .section-icon {
        width: 30px; height: 30px;
        background: rgba(245,166,35,0.1);
        border: 1px solid rgba(245, 166, 35, 0.2);
        border-radius: 8px; display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem;
    }

    /* ─── LEGEND BOX ─── */
    .legend-box {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 10px; padding: 12px 16px;
        font-size: 0.82rem; color: #64748b;
        display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
        margin: 8px 0 16px;
    }
    .legend-item { display: flex; align-items: center; gap: 6px; color: #64748b; }
    .legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

    /* ─── GLOSSARIO TOOLTIP ─── */
    .glossario {
        background: rgba(255,255,255,0.95);
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 10px; padding: 12px 16px;
        font-size: 0.82rem; color: #64748b; line-height: 1.6; margin-top: 6px;
    }
    .term { color: #d4850a; font-weight: 700; }
</style>""", unsafe_allow_html=True)

# --------------------------------------------------
# TEMPLATE PLOTLY GLOBALE — TEMA CHIARO
# --------------------------------------------------
PLOTLY_TEMPLATE = {
    'plot_bgcolor':  'rgba(255, 255, 255, 0.6)',
    'paper_bgcolor': 'rgba(255, 255, 255, 0.0)',
    'font': {'color': '#475569', 'family': 'Inter, -apple-system, sans-serif', 'size': 12},
    'xaxis': {'gridcolor': 'rgba(0,0,0,0.06)', 'linecolor': 'rgba(0,0,0,0.10)', 'zerolinecolor': 'rgba(0,0,0,0.10)'},
    'yaxis': {'gridcolor': 'rgba(0,0,0,0.06)', 'linecolor': 'rgba(0,0,0,0.10)', 'zerolinecolor': 'rgba(0,0,0,0.10)'},
}

# --------------------------------------------------
# CONNESSIONE DATABASE
# --------------------------------------------------
def get_conn():
    if "db_conn" not in st.session_state or st.session_state["db_conn"].closed:
        st.session_state["db_conn"] = psycopg2.connect(
            st.secrets["DATABASE_URL"], sslmode="require"
        )
    else:
        try:
            c = st.session_state["db_conn"].cursor()
            c.execute("SELECT 1;")
            c.close()
        except Exception:
            st.session_state["db_conn"] = psycopg2.connect(
                st.secrets["DATABASE_URL"], sslmode="require"
            )
    return st.session_state["db_conn"]

conn = get_conn()

try:
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    db_time = cur.fetchone()[0]
    cur.close()
    st.sidebar.success(f"✅ DB connesso — {db_time.strftime('%d/%m/%Y %H:%M')}")
except Exception as e:
    st.sidebar.error(f"❌ Errore DB: {e}")
    st.stop()

# --------------------------------------------------
# CARICAMENTO DATI
# --------------------------------------------------
@st.cache_data(ttl=600)
def load_staffing() -> pd.DataFrame:
    return pd.read_sql("""
        SELECT giorno, tipo_giorno, deposito, totale_autisti,
               assenze_programmate, assenze_previste, infortuni, malattie,
               legge_104, altre_assenze, congedo_parentale, permessi_vari,
               turni_richiesti, disponibili_netti, gap
        FROM v_staffing ORDER BY giorno, deposito;
    """, get_conn())

@st.cache_data(ttl=600)
def load_depositi_stats() -> pd.DataFrame:
    return pd.read_sql("""
        SELECT deposito, giorni_attivi, dipendenti_medi_giorno
        FROM v_depositi_organico_medio ORDER BY deposito;
    """, get_conn())

@st.cache_data(ttl=600)
def load_turni_calendario() -> pd.DataFrame:
    return pd.read_sql("""
        SELECT tg.data AS giorno, tg.deposito, COUNT(tg.id) AS turni
        FROM turni_giornalieri tg
        GROUP BY tg.data, tg.deposito ORDER BY tg.data, tg.deposito;
    """, get_conn())

@st.cache_data(ttl=600)
def load_copertura() -> pd.DataFrame:
    return pd.read_sql("""
        WITH
        forza AS (
            SELECT r.data AS giorno, r.deposito,
                   COUNT(DISTINCT r.matricola) AS persone_in_forza,
                   COUNT(*) FILTER (WHERE r.turno IS NOT NULL AND TRIM(r.turno)<>'') AS assenze_nominali
            FROM roster r GROUP BY r.data, r.deposito
        ),
        turni AS (
            SELECT data AS giorno, deposito, COUNT(*) AS turni_richiesti
            FROM turni_giornalieri GROUP BY data, deposito
        ),
        ass AS (
            SELECT c.data AS giorno, a.deposito,
                   ROUND(COALESCE(a.infortuni,0)+COALESCE(a.malattie,0)+COALESCE(a.legge_104,0)+
                         COALESCE(a.altre_assenze,0)+COALESCE(a.congedo_parentale,0)+COALESCE(a.permessi_vari,0))::int AS assenze_statistiche
            FROM assenze a JOIN calendar c ON c.daytype=a.daytype
        )
        SELECT f.giorno, f.deposito, f.persone_in_forza,
               COALESCE(t.turni_richiesti,0) AS turni_richiesti,
               f.assenze_nominali,
               COALESCE(a.assenze_statistiche,0) AS assenze_statistiche,
               f.persone_in_forza-COALESCE(t.turni_richiesti,0)
               -f.assenze_nominali-COALESCE(a.assenze_statistiche,0) AS gap
        FROM forza f
        LEFT JOIN turni t USING (giorno,deposito)
        LEFT JOIN ass   a USING (giorno,deposito)
        ORDER BY f.giorno, f.deposito;
    """, get_conn())

try:
    df_raw      = load_staffing()
    df_raw["giorno"] = pd.to_datetime(df_raw["giorno"])
    df_depositi = load_depositi_stats()
    df_raw      = df_raw[df_raw["deposito"] != "depbelvede"].copy()
    df_depositi = df_depositi[df_depositi["deposito"] != "depbelvede"].copy()
except Exception as e:
    st.error(f"❌ Errore caricamento staffing: {e}"); st.stop()

try:
    df_turni_cal = load_turni_calendario()
    df_turni_cal["giorno"] = pd.to_datetime(df_turni_cal["giorno"])
    turni_cal_ok = len(df_turni_cal) > 0
    if not turni_cal_ok:
        st.sidebar.warning("⚠️ Turni: 0 righe")
except Exception as e:
    st.sidebar.error(f"❌ Errore turni: {e}")
    df_turni_cal = pd.DataFrame(); turni_cal_ok = False

try:
    df_copertura = load_copertura()
    df_copertura["giorno"] = pd.to_datetime(df_copertura["giorno"])
except Exception as e:
    st.sidebar.warning(f"⚠️ Copertura non disponibile: {e}")
    df_copertura = pd.DataFrame()

# --------------------------------------------------
# UTILITY
# --------------------------------------------------
def categorizza_tipo_giorno(tipo: str) -> str:
    t = (tipo or "").strip().lower()
    if t in ['lunedi','martedi','mercoledi','giovedi','venerdi']: return 'Lu-Ve'
    elif t == 'sabato':   return 'Sabato'
    elif t == 'domenica': return 'Domenica'
    return tipo

def applica_ferie_10gg(df_in: pd.DataFrame) -> pd.DataFrame:
    df = df_in.copy()
    df["deposito_norm"] = df["deposito"].astype(str).str.strip().str.lower()
    df["ferie_extra"]   = 0.0
    df.loc[df["deposito_norm"]=="ancona", "ferie_extra"] += 5.0
    mask_eligible = ~df["deposito_norm"].isin(["ancona","moie"])
    eligible = df[mask_eligible].copy()
    if not eligible.empty:
        eligible["peso"]  = eligible["totale_autisti"].clip(lower=0)
        sum_pesi          = eligible.groupby("giorno")["peso"].transform("sum")
        eligible["quota"] = np.where(sum_pesi>0, 5.0*eligible["peso"]/sum_pesi, 0.0)
        df.loc[eligible.index, "ferie_extra"] += eligible["quota"].values
    df["assenze_previste_adj"]  = df["assenze_previste"] + df["ferie_extra"]
    df["disponibili_netti_adj"] = (df["disponibili_netti"]-df["ferie_extra"]).clip(lower=0)
    df["gap_adj"]               = df["gap"]-df["ferie_extra"]
    df.drop(columns=["deposito_norm"], inplace=True)
    return df

df_raw["categoria_giorno"] = df_raw["tipo_giorno"].apply(categorizza_tipo_giorno)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.markdown("## Controlli", unsafe_allow_html=True)
st.sidebar.markdown("---")
modalita = st.sidebar.radio("📊 Modalità Vista",
    ["Dashboard Completa","Analisi Comparativa","Report Esportabile"])
st.sidebar.markdown("---")

depositi_lista = sorted(df_raw["deposito"].unique())
deposito_sel   = st.sidebar.multiselect("📍 Depositi", depositi_lista, default=depositi_lista)

min_date   = df_raw["giorno"].min().date()
max_date   = df_raw["giorno"].max().date()
date_range = st.sidebar.date_input("📅 Periodo", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)
st.sidebar.markdown("---")
soglia_gap = st.sidebar.slider("⚠️ Soglia Critica", min_value=-50, max_value=0, value=-10)
ferie_10   = st.sidebar.checkbox("✅ Con 10 giornate di ferie (5 Ancona + 5 altri)", value=False)

with st.sidebar.expander("🔧 Filtri Avanzati"):
    show_forecast  = st.sidebar.checkbox("📈 Mostra Previsioni",  value=True)
    show_insights  = st.sidebar.checkbox("💡 Mostra Insights",    value=True)
    min_gap_filter = st.sidebar.number_input("Gap Minimo", value=-100)
    max_gap_filter = st.sidebar.number_input("Gap Massimo", value=100)
st.sidebar.markdown("---")

# --- filtro staffing ---
if len(date_range)==2:
    df_filtered = df_raw[
        (df_raw["deposito"].isin(deposito_sel)) &
        (df_raw["giorno"]>=pd.to_datetime(date_range[0])) &
        (df_raw["giorno"]<=pd.to_datetime(date_range[1]))
    ].copy()
else:
    df_filtered = df_raw[df_raw["deposito"].isin(deposito_sel)].copy()

if ferie_10:
    try:
        df_filtered = applica_ferie_10gg(df_filtered)
        df_filtered["assenze_previste"]  = df_filtered["assenze_previste_adj"]
        df_filtered["disponibili_netti"] = df_filtered["disponibili_netti_adj"]
        df_filtered["gap"]               = df_filtered["gap_adj"]
    except Exception as e:
        st.error(f"❌ Errore ferie: {e}"); st.stop()

df_filtered = df_filtered[
    (df_filtered["gap"]>=min_gap_filter) & (df_filtered["gap"]<=max_gap_filter)
].copy()

# --- filtro copertura ---
if len(df_copertura)>0:
    if ferie_10:
        df_cop = df_copertura.copy()
        df_cop["deposito_norm"] = df_cop["deposito"].str.strip().str.lower()
        df_cop["ferie_extra"]   = 0.0
        df_cop.loc[df_cop["deposito_norm"]=="ancona","ferie_extra"] += 5.0
        mask_elig = ~df_cop["deposito_norm"].isin(["ancona","moie"])
        elig = df_cop[mask_elig].copy()
        if not elig.empty:
            elig["peso"] = elig["persone_in_forza"].clip(lower=0)
            sum_p = elig.groupby("giorno")["peso"].transform("sum")
            elig["quota"] = np.where(sum_p>0, 5.0*elig["peso"]/sum_p, 0.0)
            df_cop.loc[elig.index,"ferie_extra"] += elig["quota"].values
        df_cop["assenze_nominali"] = df_cop["assenze_nominali"]+df_cop["ferie_extra"]
        df_cop["gap"] = df_cop["persone_in_forza"]-df_cop["turni_richiesti"]-df_cop["assenze_nominali"]-df_cop["assenze_statistiche"]
        df_cop.drop(columns=["deposito_norm","ferie_extra"], inplace=True)
        df_copertura_filtered = df_cop
    else:
        df_copertura_filtered = df_copertura.copy()
    if len(date_range)==2:
        df_copertura_filtered = df_copertura_filtered[
            (df_copertura_filtered["giorno"]>=pd.to_datetime(date_range[0])) &
            (df_copertura_filtered["giorno"]<=pd.to_datetime(date_range[1])) &
            (df_copertura_filtered["deposito"].isin(deposito_sel))
        ]
    else:
        df_copertura_filtered = df_copertura_filtered[df_copertura_filtered["deposito"].isin(deposito_sel)]
else:
    df_copertura_filtered = pd.DataFrame()

if turni_cal_ok and len(df_turni_cal)>0:
    if len(date_range)==2:
        df_tc_filtered = df_turni_cal[
            (df_turni_cal["giorno"]>=pd.to_datetime(date_range[0])) &
            (df_turni_cal["giorno"]<=pd.to_datetime(date_range[1])) &
            (df_turni_cal["deposito"].isin(deposito_sel))
        ].copy()
    else:
        df_tc_filtered = df_turni_cal[df_turni_cal["deposito"].isin(deposito_sel)].copy()
else:
    df_tc_filtered = pd.DataFrame()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div style='margin-bottom:1.5rem;'>
    <h1 style='margin-bottom:0 !important;'>Estate 2026</h1>
    <p style='color:#64748b !important;font-size:1rem;font-weight:500;letter-spacing:0.5px;margin:4px 0 0;'>
        Analytics Dashboard · Conerobus S.p.A.</p>
</div>
""", unsafe_allow_html=True)

if len(date_range)==2:
    ferie_badge = " · 🏖️ Simulazione Ferie" if ferie_10 else ""
    st.markdown(
        f"<p style='font-size:0.9rem;font-weight:500;margin-top:-8px;color:#64748b !important;'>"
        f"{date_range[0].strftime('%d/%m/%Y')} → {date_range[1].strftime('%d/%m/%Y')} · "
        f"{len(deposito_sel)} Depositi · {len(df_filtered):,} Records{ferie_badge}</p>",
        unsafe_allow_html=True)
st.markdown("---")

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------
st.markdown("### Key Performance Indicators", unsafe_allow_html=True)
if len(df_filtered)>0:
    totale_dipendenti  = df_depositi[df_depositi["deposito"].isin(deposito_sel)]["dipendenti_medi_giorno"].sum()
    gap_per_giorno     = df_filtered.groupby("giorno")["gap"].sum()
    gap_medio_giorno   = gap_per_giorno.mean()
    media_turni_giorno = df_filtered.groupby("giorno")["turni_richiesti"].sum().mean()
    gap_pct_medio      = (gap_medio_giorno/media_turni_giorno*100) if media_turni_giorno>0 else 0
    giorni_analizzati  = df_filtered["giorno"].nunique()
    giorni_critici_count = (gap_per_giorno<soglia_gap).sum()
    pct_critici        = (giorni_critici_count/giorni_analizzati*100) if giorni_analizzati>0 else 0
    turni_luv = df_filtered[
        df_filtered["tipo_giorno"].str.lower().isin(['lunedi','martedi','mercoledi','giovedi','venerdi'])
    ].groupby("giorno")["turni_richiesti"].sum().mean()
    turni_luv = int(turni_luv) if not np.isnan(turni_luv) else 0

    kpi1,kpi2,kpi3,kpi4 = st.columns(4)
    with kpi1: st.metric("👤 Autisti", f"{int(totale_dipendenti):,}")
    with kpi2: st.metric("🚌 Turni/giorno Lu-Ve", f"{turni_luv:,}")
    with kpi3: st.metric("⚖️ Gap Medio/giorno", f"{int(gap_medio_giorno):,}",
                         delta=f"{gap_pct_medio:.1f}%",
                         delta_color="normal" if gap_medio_giorno>=0 else "inverse")
    with kpi4: st.metric("🚨 Giorni Critici", f"{giorni_critici_count}/{giorni_analizzati}",
                         delta=f"{pct_critici:.0f}%", delta_color="inverse")
st.markdown("---")

# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------
if show_insights and len(df_filtered)>0:
    st.markdown("### Insights", unsafe_allow_html=True)
    ic1,ic2,ic3 = st.columns(3)
    with ic1:
        by_dep    = df_filtered.groupby("deposito")["gap"].mean()
        worst_dep = by_dep.idxmin()
        st.markdown(f"""<div class='insight-card'>
            <h4>⚠ Deposito Critico</h4>
            <p style='font-size:1rem;margin:0;color:#1e293b !important;'><b>{worst_dep}</b> — gap medio: <b>{by_dep.min():.1f}</b></p>
            <p style='font-size:0.85rem;margin-top:8px;color:#64748b !important;'>Considera redistribuzione turni</p>
        </div>""", unsafe_allow_html=True)
    with ic2:
        by_cat    = df_filtered.groupby("categoria_giorno")["gap"].mean()
        worst_cat = by_cat.idxmin()
        st.markdown(f"""<div class='insight-card'>
            <h4>📅 Giorno Critico</h4>
            <p style='font-size:1rem;margin:0;color:#1e293b !important;'><b>{worst_cat}</b> — gap medio: <b>{by_cat.min():.1f}</b></p>
            <p style='font-size:0.85rem;margin-top:8px;color:#64748b !important;'>Pianifica turni extra</p>
        </div>""", unsafe_allow_html=True)
    with ic3:
        assenze_trend = df_filtered.groupby("giorno")["assenze_previste"].sum()
        if len(assenze_trend)>1:
            crescente  = assenze_trend.iloc[-1]>assenze_trend.iloc[0]
            trend_txt  = "crescente" if crescente else "decrescente"
            trend_icon = "📈" if crescente else "📉"
        else:
            trend_txt, trend_icon = "stabile", "➡️"
        st.markdown(f"""<div class='insight-card'>
            <h4>📊 Trend Assenze</h4>
            <p style='font-size:1rem;margin:0;color:#1e293b !important;'>{trend_icon} Trend <b>{trend_txt}</b></p>
            <p style='font-size:0.85rem;margin-top:8px;color:#64748b !important;'>Monitora evoluzione settimanale</p>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")

# --------------------------------------------------
# AGGREGATI PER DEPOSITO
# --------------------------------------------------
if len(df_filtered)>0:
    by_deposito = df_filtered.groupby("deposito").agg(
        turni_richiesti=("turni_richiesti","sum"),
        disponibili_netti=("disponibili_netti","sum"),
        gap=("gap","sum"),
        assenze_previste=("assenze_previste","sum"),
    ).reset_index()
    by_deposito = by_deposito.merge(df_depositi, on="deposito", how="left")
    giorni_per_dep = df_filtered.groupby("deposito")["giorno"].nunique().rename("giorni_periodo")
    by_deposito    = by_deposito.merge(giorni_per_dep, left_on="deposito", right_index=True)
    by_deposito["media_gap_giorno"]  = (by_deposito["gap"]/by_deposito["giorni_periodo"]).round(1)
    by_deposito["tasso_copertura_%"] = (by_deposito["disponibili_netti"]/by_deposito["turni_richiesti"]*100).fillna(0).round(1)
    by_deposito = by_deposito.sort_values("media_gap_giorno")
else:
    by_deposito = pd.DataFrame()

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1,tab2,tab3,tab4,tab5 = st.tabs(["📊 Overview","📈 Analisi & Assenze","🚌 Turni Calendario","🎯 Depositi","📥 Export"])

# ══════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════
with tab1:
    if len(df_filtered)==0:
        st.info("Nessun dato per i filtri selezionati.")
    else:
        st.markdown("#### Copertura del Servizio — Persone per Giorno", unsafe_allow_html=True)
        st.markdown(
            "<p style='font-size:0.85rem;'>"
            "Ogni barra mostra come vengono distribuite le <b style='color:#1e293b;'>persone in forza</b> quel giorno. "
            "<span style='color:#22c55e;'>Verde</span> = buffer · "
            "<span style='color:#ef4444;'>Rosso</span> = deficit.</p>",
            unsafe_allow_html=True)

        if len(df_copertura_filtered)>0:
            cop = df_copertura_filtered.groupby("giorno").agg(
                persone_in_forza=("persone_in_forza","sum"),
                turni_richiesti=("turni_richiesti","sum"),
                assenze_nominali=("assenze_nominali","sum"),
                assenze_statistiche=("assenze_statistiche","sum"),
                gap=("gap","sum"),
            ).reset_index()

            giorni_ok      = int((cop["gap"]>=0).sum())
            giorni_allarme = int((cop["gap"]<0).sum())
            gap_medio_cop  = cop["gap"].mean()
            gap_min_cop    = cop["gap"].min()

            kc1,kc2,kc3,kc4 = st.columns(4)
            with kc1: st.metric("👥 Persone in forza (media/gg)", f"{cop['persone_in_forza'].mean():.0f}")
            with kc2: st.metric("✅ Giorni in copertura", f"{giorni_ok}")
            with kc3: st.metric("🚨 Giorni in deficit", f"{giorni_allarme}")
            with kc4: st.metric("📉 Gap medio/giorno", f"{gap_medio_cop:.1f}", delta=f"min: {gap_min_cop:.0f}")

            fig_cop = make_subplots(rows=2,cols=1,row_heights=[0.70,0.30],
                shared_xaxes=True,vertical_spacing=0.05,
                subplot_titles=("Distribuzione persone in forza","Buffer / Deficit"))

            fig_cop.add_trace(go.Bar(x=cop["giorno"],y=cop["turni_richiesti"],name="Turni da coprire",
                marker_color="rgba(100,116,139,0.75)",
                hovertemplate="<b>Turni da coprire</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"), row=1,col=1)
            fig_cop.add_trace(go.Bar(x=cop["giorno"],y=cop["assenze_nominali"],name="Assenze roster",
                marker_color="rgba(148,163,184,0.75)",
                hovertemplate="<b>Assenze roster</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"), row=1,col=1)
            fig_cop.add_trace(go.Bar(x=cop["giorno"],y=cop["assenze_statistiche"],name="Assenze storiche",
                marker_color="rgba(203,213,225,0.80)",
                hovertemplate="<b>Assenze storiche</b><br>%{x|%d/%m/%Y}: <b>%{y:.0f}</b><extra></extra>"), row=1,col=1)

            buf_colors = ["rgba(34,197,94,0.80)" if g>=0 else "rgba(239,68,68,0.85)" for g in cop["gap"]]
            fig_cop.add_trace(go.Bar(x=cop["giorno"],y=cop["gap"],name="Buffer / Deficit",
                marker=dict(color=buf_colors,line=dict(width=0.8,color="rgba(255,255,255,0.3)")),
                text=[f"<b>{int(g)}</b>" if g<0 else "" for g in cop["gap"]],
                textposition="outside",textfont=dict(size=11,color="#ef4444"),
                hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Buffer/Deficit: <b>%{y}</b><extra></extra>"), row=1,col=1)
            fig_cop.add_trace(go.Scatter(x=cop["giorno"],y=cop["persone_in_forza"],name="Persone in forza",
                mode="lines",line=dict(color="#64748b",width=2,dash="dot"),
                hovertemplate="<b>Persone in forza</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"), row=1,col=1)

            gap_colors2 = ["rgba(34,197,94,0.80)" if g>=0 else "rgba(239,68,68,0.85)" for g in cop["gap"]]
            fig_cop.add_trace(go.Bar(x=cop["giorno"],y=cop["gap"],name="Gap",
                marker=dict(color=gap_colors2,line=dict(width=0.5,color="rgba(255,255,255,0.2)")),
                text=[f"<b>{int(g)}</b>" for g in cop["gap"]],
                textposition="outside",textfont=dict(size=9,color="#475569"),
                showlegend=False,
                hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Gap: <b>%{y}</b><extra></extra>"), row=2,col=1)

            fig_cop.add_hline(y=0,line_dash="solid",line_color="rgba(0,0,0,0.3)",line_width=1.5,row=2,col=1)
            if soglia_gap<0:
                fig_cop.add_hline(y=soglia_gap,line_dash="dash",line_color="#ef4444",line_width=2,
                    annotation_text=f"Soglia ({soglia_gap})",
                    annotation_font=dict(color="#ef4444",size=10),
                    annotation_position="top left",row=2,col=1)

            fig_cop.update_layout(
                barmode="stack",height=700,hovermode="x unified",
                legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,
                    font=dict(size=11),bgcolor="rgba(255,255,255,0.5)"),
                plot_bgcolor="rgba(255,255,255,0.6)",paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#475569",family="Inter, sans-serif"),
                margin=dict(t=60,b=20,l=10,r=10))
            fig_cop.update_xaxes(tickformat="%d/%m",tickangle=-45,
                gridcolor="rgba(0,0,0,0.06)",linecolor="rgba(0,0,0,0.10)")
            fig_cop.update_yaxes(gridcolor="rgba(0,0,0,0.06)",linecolor="rgba(0,0,0,0.10)",zeroline=False)
            fig_cop.update_yaxes(title_text="Persone",row=1,col=1)
            fig_cop.update_yaxes(title_text="Gap",row=2,col=1)
            st.plotly_chart(fig_cop,use_container_width=True,key="pc_main_cop")

            st.markdown("""
            <div class='legend-box'>
                <div class='legend-item'><div class='legend-dot' style='background:#64748b;'></div> Turni da coprire</div>
                <div class='legend-item'><div class='legend-dot' style='background:#94a3b8;'></div> Assenze roster (FP, R, PS…)</div>
                <div class='legend-item'><div class='legend-dot' style='background:#cbd5e1;'></div> Assenze storiche</div>
                <div class='legend-item'><div class='legend-dot' style='background:#22c55e;'></div> Buffer</div>
                <div class='legend-item'><div class='legend-dot' style='background:#ef4444;'></div> Deficit</div>
                <div class='legend-item'><div style='width:20px;height:2px;border-top:2px dotted #64748b;'></div> Persone in forza</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Dati copertura non disponibili per i filtri selezionati.")

        with st.expander("📊 Statistiche aggiuntive"):
            eg1,eg2 = st.columns(2)
            with eg1:
                st.markdown("##### Stato Copertura (Gap %)")
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",value=gap_pct_medio,
                    title={'text':"Gap % Medio",'font':{'size':14,'color':'#64748b'}},
                    delta={'reference':0,'suffix':'%'},
                    number={'suffix':'%','font':{'size':28,'color':'#d4850a'}},
                    gauge={'axis':{'range':[-20,20],'tickcolor':"#64748b"},
                        'bar':{'color':"#F5A623",'thickness':0.7},
                        'bgcolor':"rgba(255,255,255,0.6)",'borderwidth':2,'bordercolor':"#e2e8f0",
                        'steps':[
                            {'range':[-20,-10],'color':'rgba(239,68,68,0.15)'},
                            {'range':[-10,0],'color':'rgba(245,166,35,0.12)'},
                            {'range':[0,10],'color':'rgba(34,197,94,0.12)'},
                            {'range':[10,20],'color':'rgba(22,163,74,0.15)'}],
                        'threshold':{'line':{'color':"#ef4444",'width':3},'thickness':0.75,
                            'value':(soglia_gap/media_turni_giorno*100) if media_turni_giorno>0 else 0}}))
                fig_gauge.update_layout(height=280,paper_bgcolor='rgba(0,0,0,0)',margin=dict(l=20,r=20,t=40,b=20))
                st.plotly_chart(fig_gauge,use_container_width=True,key="pc_2")
            with eg2:
                st.markdown("##### Distribuzione Assenze Storiche")
                ab = pd.DataFrame({
                    'Tipo':['Infortuni','Malattie','L.104','Congedi','Permessi','Altro'],
                    'Totale':[int(df_filtered[c].sum()) for c in
                        ['infortuni','malattie','legge_104','congedo_parentale','permessi_vari','altre_assenze']]})
                ab = ab[ab['Totale']>0]
                if len(ab)>0:
                    fig_pie = go.Figure(go.Pie(labels=ab['Tipo'],values=ab['Totale'],hole=.5,
                        marker=dict(colors=['#ef4444','#f97316','#eab308','#3b82f6','#22c55e','#94a3b8']),
                        textinfo='label+percent',textfont=dict(size=11)))
                    fig_pie.update_layout(height=280,showlegend=False,paper_bgcolor='rgba(0,0,0,0)',margin=dict(l=0,r=0,t=0,b=0))
                    st.plotly_chart(fig_pie,use_container_width=True,key="pc_3")

        st.markdown("---")
        st.markdown("#### Heatmap Criticità per Deposito", unsafe_allow_html=True)
        pivot_gap = df_filtered.pivot_table(
            values='gap',index='deposito',
            columns=df_filtered['giorno'].dt.strftime('%d/%m'),
            aggfunc='sum',fill_value=0)
        if len(pivot_gap)>0:
            fig_heat = go.Figure(go.Heatmap(
                z=pivot_gap.values,x=pivot_gap.columns,y=pivot_gap.index,
                colorscale=[[0,'#b91c1c'],[0.35,'#ef4444'],[0.45,'#fdba74'],
                            [0.5,'#fefce8'],[0.55,'#bbf7d0'],[0.7,'#22c55e'],[1,'#166534']],
                zmid=0,text=pivot_gap.values,texttemplate='%{text:.0f}',
                textfont=dict(size=10,color="#1e293b"),colorbar=dict(title="Gap")))
            fig_heat.update_layout(height=max(300,len(pivot_gap)*40),**PLOTLY_TEMPLATE)
            st.plotly_chart(fig_heat,use_container_width=True,key="pc_4")


# ══════════════════════════════════════════════════
# TAB 2 — ANALISI & ASSENZE
# ══════════════════════════════════════════════════
with tab2:
    if len(df_filtered)==0:
        st.info("Nessun dato per i filtri selezionati.")
    else:
        st2_a,st2_b,st2_c = st.tabs(["📉 Gap & Waterfall","🏖️ Ferie & Riposi","🤒 Assenze Complete"])

        with st2_a:
            st.markdown("#### Composizione Gap Medio Giornaliero", unsafe_allow_html=True)
            st.markdown(
                "<p style='font-size:0.85rem;'>"
                "Autisti − Assenze = <b style='color:#1e293b;'>Disponibili Netti</b> − Turni = "
                "<b style='color:#1e293b;'>Gap</b></p>", unsafe_allow_html=True)

            autisti_medio    = df_filtered.groupby("giorno")["totale_autisti"].sum().mean()
            assenze_medie    = df_filtered.groupby("giorno")["assenze_previste"].sum().mean()
            turni_medi       = df_filtered.groupby("giorno")["turni_richiesti"].sum().mean()
            disponibili_medi = autisti_medio-assenze_medie
            gap_medio_wf     = disponibili_medi-turni_medi

            fig_wf = go.Figure(go.Waterfall(
                orientation="v",
                measure=["absolute","relative","total","relative","total"],
                x=["Autisti in Forza","− Assenze Previste","= Disponibili Netti","− Turni da Coprire","= Gap / Buffer"],
                y=[autisti_medio,-assenze_medie,0,-turni_medi,0],
                text=[f"{autisti_medio:.0f}",f"−{assenze_medie:.0f}",f"{disponibili_medi:.0f}",
                      f"−{turni_medi:.0f}",f"{'+'if gap_medio_wf>=0 else ''}{gap_medio_wf:.0f}"],
                textposition="outside",textfont=dict(size=12,color="#1e293b"),
                connector={"line":{"color":"rgba(0,0,0,0.12)","width":1,"dash":"dot"}},
                increasing={"marker":{"color":"#22c55e","line":{"color":"#16a34a","width":1}}},
                decreasing={"marker":{"color":"#ef4444","line":{"color":"#dc2626","width":1}}},
                totals={"marker":{"color":"#3b82f6","line":{"color":"rgba(0,0,0,0.1)","width":1}}},
                hovertemplate="<b>%{x}</b><br>Valore: <b>%{y:.1f}</b> persone<extra></extra>"))

            fig_wf.add_hline(y=0,line_dash="dash",line_color="rgba(0,0,0,0.15)",line_width=1)

            ann_col = "#22c55e" if gap_medio_wf>=0 else "#ef4444"
            ann_txt = f"✅ Buffer: +{gap_medio_wf:.0f}" if gap_medio_wf>=0 else f"🚨 Deficit: {gap_medio_wf:.0f}"
            fig_wf.add_annotation(x="= Gap / Buffer",
                y=gap_medio_wf+(10 if gap_medio_wf>=0 else -10),
                text=f"<b>{ann_txt}</b>",showarrow=True,arrowhead=2,arrowcolor=ann_col,
                font=dict(size=11,color=ann_col),
                bgcolor="rgba(255,255,255,0.9)",bordercolor=ann_col,borderwidth=1,borderpad=6)

            fig_wf.update_layout(height=480,showlegend=False,
                plot_bgcolor="rgba(255,255,255,0.6)",paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#475569",family="Inter, sans-serif"),
                margin=dict(t=30,b=70,l=20,r=20),
                xaxis=dict(gridcolor="rgba(0,0,0,0.05)",linecolor="rgba(0,0,0,0.1)",tickfont=dict(size=11)),
                yaxis=dict(title="Persone (media/giorno)",
                    gridcolor="rgba(0,0,0,0.06)",linecolor="rgba(0,0,0,0.1)",
                    zeroline=True,zerolinecolor="rgba(0,0,0,0.1)",zerolinewidth=1))
            st.plotly_chart(fig_wf,use_container_width=True,key="pc_5")

            wk1,wk2,wk3 = st.columns(3)
            with wk1: st.metric("👥 Autisti medi/giorno",f"{autisti_medio:.0f}")
            with wk2: st.metric("🏥 Assenze previste/giorno",f"{assenze_medie:.0f}",
                delta=f"−{assenze_medie/autisti_medio*100:.1f}% organico" if autisti_medio>0 else "",delta_color="inverse")
            with wk3: st.metric("🚌 Turni da coprire/giorno",f"{turni_medi:.0f}",
                delta="✅ coperti" if gap_medio_wf>=0 else f"🚨 deficit {gap_medio_wf:.0f}",
                delta_color="normal" if gap_medio_wf>=0 else "inverse")

            st.markdown("---")
            st.markdown("#### Trend Assenze per Tipologia", unsafe_allow_html=True)
            trend_df = df_filtered.groupby("giorno").agg(
                infortuni=("infortuni","sum"),malattie=("malattie","sum"),
                legge_104=("legge_104","sum"),congedo_parentale=("congedo_parentale","sum"),
                permessi_vari=("permessi_vari","sum")).reset_index()
            fig_trend = go.Figure()
            for col_t,label_t,colore_t in [
                ("infortuni","Infortuni","#ef4444"),("malattie","Malattie","#f97316"),
                ("legge_104","L.104","#eab308"),("congedo_parentale","Congedo parent.","#3b82f6"),
                ("permessi_vari","Permessi vari","#22c55e")]:
                fig_trend.add_trace(go.Scatter(x=trend_df["giorno"],y=trend_df[col_t],
                    mode="lines+markers",name=label_t,line=dict(color=colore_t,width=2),marker=dict(size=4),
                    hovertemplate=f"<b>{label_t}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y:.1f}}</b><extra></extra>"))
            fig_trend.update_layout(height=380,hovermode="x unified",
                legend=dict(orientation="h",y=-0.18,font=dict(size=10)),**PLOTLY_TEMPLATE)
            st.plotly_chart(fig_trend,use_container_width=True,key="pc_7")

        # ── FERIE & RIPOSI ──
        with st2_b:
            st.markdown("<p>Conteggio giornaliero di <b style='color:#1e293b;'>FP</b> (Ferie Programmate) "
                        "dal roster, per deposito.</p>", unsafe_allow_html=True)
            try:
                d0 = df_filtered["giorno"].min().date()
                d1 = df_filtered["giorno"].max().date()
                deps_str = ",".join([f"'{d}'" for d in deposito_sel])
                df_fp_r = pd.read_sql(f"""
                    SELECT data AS giorno, deposito,
                           COUNT(*) FILTER (WHERE turno='FP') AS ferie_programmate,
                           COUNT(*) FILTER (WHERE turno='R')  AS riposi
                    FROM roster WHERE data BETWEEN '{d0}' AND '{d1}' AND deposito IN ({deps_str})
                    GROUP BY data, deposito ORDER BY data, deposito;
                """, get_conn())
                df_fp_r["giorno"] = pd.to_datetime(df_fp_r["giorno"])
                fp_r_daily = df_fp_r.groupby("giorno")[["ferie_programmate","riposi"]].sum().reset_index()

                k1,k2,k3 = st.columns(3)
                with k1: st.metric("🏖️ Tot. Ferie Programmate", f"{int(fp_r_daily['ferie_programmate'].sum()):,}")
                with k2: st.metric("📅 Media FP/giorno", f"{fp_r_daily['ferie_programmate'].mean():.1f}")
                with k3: st.metric("📅 Media Riposi/giorno", f"{fp_r_daily['riposi'].mean():.1f}")

                view_fp_r = st.radio("Visualizza",["Per tipo (FP vs R)","Per deposito"],horizontal=True,key="view_fp_r")
                if view_fp_r=="Per tipo (FP vs R)":
                    fig_fpr = go.Figure()
                    fig_fpr.add_trace(go.Bar(x=fp_r_daily["giorno"],y=fp_r_daily["ferie_programmate"],
                        name="Ferie Programmate (FP)",marker_color="#22c55e",
                        hovertemplate="<b>FP</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"))
                    fig_fpr.add_trace(go.Bar(x=fp_r_daily["giorno"],y=fp_r_daily["riposi"],
                        name="Riposi (R)",marker_color="#3b82f6",
                        hovertemplate="<b>R</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"))
                    fig_fpr.update_layout(barmode="stack",height=430,hovermode="x unified",
                        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),**PLOTLY_TEMPLATE)
                    st.plotly_chart(fig_fpr,use_container_width=True,key="pc_8")
                else:
                    tipo_dep = st.radio("Tipo",["FP","R"],horizontal=True,key="tipo_dep_fpr")
                    col_sel  = "ferie_programmate" if tipo_dep=="FP" else "riposi"
                    fig_fpr_dep = go.Figure()
                    for dep in sorted(df_fp_r["deposito"].unique()):
                        df_d = df_fp_r[df_fp_r["deposito"]==dep]
                        fig_fpr_dep.add_trace(go.Bar(x=df_d["giorno"],y=df_d[col_sel],
                            name=dep.title(),marker_color=get_colore_deposito(dep),
                            hovertemplate=f"<b>{dep.title()}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y}}</b><extra></extra>"))
                    fig_fpr_dep.update_layout(barmode="stack",height=430,hovermode="x unified",
                        title=f"{'Ferie Programmate' if tipo_dep=='FP' else 'Riposi'} per Deposito",
                        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),**PLOTLY_TEMPLATE)
                    st.plotly_chart(fig_fpr_dep,use_container_width=True,key="pc_9")
            except Exception as e:
                st.warning(f"⚠️ Errore ferie/riposi: {e}")

        # ── ASSENZE COMPLETE ──
        with st2_c:
            st.markdown("<p>Assenze statistiche + nominali dal roster: "
                "<b style='color:#1e293b;'>PS</b> · <b style='color:#1e293b;'>AP</b> · "
                "<b style='color:#1e293b;'>PADm</b> · <b style='color:#1e293b;'>NF</b></p>", unsafe_allow_html=True)
            try:
                d0 = df_filtered["giorno"].min().date()
                d1 = df_filtered["giorno"].max().date()
                deps_str = ",".join([f"'{d}'" for d in deposito_sel])
                df_nominali = pd.read_sql(f"""
                    SELECT data AS giorno, deposito,
                           COUNT(*) FILTER (WHERE turno='PS')   AS ps,
                           COUNT(*) FILTER (WHERE turno='AP')   AS aspettativa,
                           COUNT(*) FILTER (WHERE turno='PADm') AS congedo_straord,
                           COUNT(*) FILTER (WHERE turno='NF')   AS non_in_forza
                    FROM roster WHERE data BETWEEN '{d0}' AND '{d1}' AND deposito IN ({deps_str})
                    GROUP BY data, deposito ORDER BY data, deposito;
                """, get_conn())
                df_nominali["giorno"] = pd.to_datetime(df_nominali["giorno"])
                nom_daily = df_nominali.groupby("giorno")[["ps","aspettativa","congedo_straord","non_in_forza"]].sum().reset_index()
                stat_daily = df_filtered.groupby("giorno").agg(
                    infortuni=("infortuni","sum"),malattie=("malattie","sum"),
                    legge_104=("legge_104","sum"),altre_assenze=("altre_assenze","sum"),
                    congedo_parentale=("congedo_parentale","sum"),permessi_vari=("permessi_vari","sum")).reset_index()
                df_assenze_full = stat_daily.merge(nom_daily,on="giorno",how="left").fillna(0)

                k1,k2,k3,k4,k5,k6 = st.columns(6)
                with k1: st.metric("🤕 Infortuni",   f"{int(df_assenze_full['infortuni'].sum()):,}")
                with k2: st.metric("🤒 Malattie",     f"{int(df_assenze_full['malattie'].sum()):,}")
                with k3: st.metric("♿ L.104",         f"{int(df_assenze_full['legge_104'].sum()):,}")
                with k4: st.metric("📋 PS",           f"{int(df_assenze_full['ps'].sum()):,}")
                with k5: st.metric("⏸️ Aspettativa", f"{int(df_assenze_full['aspettativa'].sum()):,}")
                with k6: st.metric("🔴 Non in forza",f"{int(df_assenze_full['non_in_forza'].sum()):,}")

                palette_stat = [
                    ("infortuni","Infortuni","#ef4444"),("malattie","Malattie","#f97316"),
                    ("legge_104","L.104","#eab308"),("altre_assenze","Altre assenze","#a78bfa"),
                    ("congedo_parentale","Congedo parentale","#3b82f6"),("permessi_vari","Permessi vari","#22c55e")]
                palette_nom = [
                    ("ps","PS","#f43f5e"),("aspettativa","AP (Aspettativa)","#8b5cf6"),
                    ("congedo_straord","PADm (Cong. straord.)","#0ea5e9"),("non_in_forza","NF (Non in forza)","#78909C")]

                fig_ass = go.Figure()
                for c_,l_,col_ in palette_stat:
                    fig_ass.add_trace(go.Bar(x=df_assenze_full["giorno"],y=df_assenze_full[c_],
                        name=l_,marker_color=col_,
                        hovertemplate=f"<b>{l_}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y:.1f}}</b><extra></extra>"))
                for c_,l_,col_ in palette_nom:
                    fig_ass.add_trace(go.Bar(x=df_assenze_full["giorno"],y=df_assenze_full[c_],
                        name=l_,marker_color=col_,marker_line=dict(width=0.5,color="rgba(255,255,255,0.4)"),
                        hovertemplate=f"<b>{l_}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y}}</b><extra></extra>"))
                fig_ass.update_layout(barmode="stack",height=500,hovermode="x unified",
                    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=10)),
                    **PLOTLY_TEMPLATE)
                st.plotly_chart(fig_ass,use_container_width=True,key="pc_10")

                # ── TABELLA NUMERICA ASSENZE ──
                st.markdown("#### Tabella Assenze — Riepilogo Numerico", unsafe_allow_html=True)
                df_tab_assenze = df_assenze_full.copy()
                df_tab_assenze["giorno"] = df_tab_assenze["giorno"].dt.strftime('%d/%m/%Y')
                df_tab_assenze = df_tab_assenze.rename(columns={
                    "giorno":"Data","infortuni":"Infortuni","malattie":"Malattie",
                    "legge_104":"L.104","altre_assenze":"Altre","congedo_parentale":"Cong. Parent.",
                    "permessi_vari":"Permessi","ps":"PS","aspettativa":"AP",
                    "congedo_straord":"PADm","non_in_forza":"NF"})
                num_cols = ["Infortuni","Malattie","L.104","Altre","Cong. Parent.","Permessi","PS","AP","PADm","NF"]
                df_tab_assenze["Totale"] = df_tab_assenze[num_cols].sum(axis=1)
                st.dataframe(df_tab_assenze,use_container_width=True,hide_index=True,height=400)

                with st.expander("🔍 Dettaglio singolo deposito"):
                    dep_ass = st.selectbox("Deposito",sorted(deposito_sel),key="dep_ass_detail",
                        format_func=lambda x: x.title())
                    df_dep_stat = df_filtered[df_filtered["deposito"]==dep_ass].groupby("giorno").agg(
                        infortuni=("infortuni","sum"),malattie=("malattie","sum"),
                        legge_104=("legge_104","sum"),altre_assenze=("altre_assenze","sum"),
                        congedo_parentale=("congedo_parentale","sum"),permessi_vari=("permessi_vari","sum")).reset_index()
                    df_dep_nom = df_nominali[df_nominali["deposito"]==dep_ass].copy()
                    df_dep_full = df_dep_stat.merge(
                        df_dep_nom[["giorno","ps","aspettativa","congedo_straord","non_in_forza"]],
                        on="giorno",how="left").fillna(0)
                    fig_dep_ass = go.Figure()
                    for c_,l_,col_ in palette_stat+palette_nom:
                        fig_dep_ass.add_trace(go.Bar(x=df_dep_full["giorno"],y=df_dep_full[c_],
                            name=l_,marker_color=col_,
                            hovertemplate=f"<b>{l_}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y:.1f}}</b><extra></extra>"))
                    fig_dep_ass.update_layout(barmode="stack",height=400,hovermode="x unified",
                        title=f"Assenze — {dep_ass.title()}",
                        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=10)),
                        **PLOTLY_TEMPLATE)
                    st.plotly_chart(fig_dep_ass,use_container_width=True,key="pc_11")
            except Exception as e:
                st.warning(f"⚠️ Errore assenze: {e}")


# ══════════════════════════════════════════════════
# TAB 3 — TURNI CALENDARIO
# ══════════════════════════════════════════════════
with tab3:
    st.markdown("### Turni per Deposito — Validità Temporale", unsafe_allow_html=True)
    st.markdown("<p>Turni giornalieri per deposito (Lu-Ve / Sa / Do) rispettando il range di validità.</p>",
                unsafe_allow_html=True)

    if not turni_cal_ok or len(df_tc_filtered)==0:
        st.warning("Nessun record trovato per il periodo selezionato.")
    else:
        tc1,tc2,tc3 = st.columns([1,1,2])
        with tc1:
            bar_mode = st.radio("Modalità barre",["Impilate","Affiancate"],horizontal=True)
            bmode    = "stack" if bar_mode=="Impilate" else "group"
        with tc2:
            show_totale = st.checkbox("Mostra linea totale",value=True)
        with tc3:
            dep_tc = st.multiselect("Depositi visibili",
                options=sorted(df_tc_filtered["deposito"].unique()),
                default=sorted(df_tc_filtered["deposito"].unique()),key="dep_tc_filter")

        df_tc_plot = df_tc_filtered[df_tc_filtered["deposito"].isin(dep_tc)].copy()

        if len(df_tc_plot)>0:
            df_tc_agg = (df_tc_plot.groupby(["giorno","deposito"])["turni"]
                         .sum().reset_index().sort_values(["giorno","deposito"]))
            fig_tc = go.Figure()
            for dep in sorted(df_tc_agg["deposito"].unique()):
                df_dep = df_tc_agg[df_tc_agg["deposito"]==dep]
                fig_tc.add_trace(go.Bar(x=df_dep["giorno"],y=df_dep["turni"],name=dep.title(),
                    marker_color=get_colore_deposito(dep),
                    marker_line=dict(width=0.4,color="rgba(255,255,255,0.15)"),
                    hovertemplate=f"<b>{dep.title()}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y}}</b><extra></extra>"))
            if show_totale:
                tot_gg = df_tc_agg.groupby("giorno")["turni"].sum().reset_index()
                fig_tc.add_trace(go.Scatter(x=tot_gg["giorno"],y=tot_gg["turni"],name="Totale",
                    mode="lines+markers",line=dict(color="#1e293b",width=2,dash="dot"),
                    marker=dict(size=5,symbol="diamond"),
                    hovertemplate="<b>Totale</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"))
            fig_tc.update_layout(barmode=bmode,height=520,hovermode="x unified",
                legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=10)),
                **PLOTLY_TEMPLATE)
            st.plotly_chart(fig_tc,use_container_width=True,key="pc_13")

            st.markdown("---")
            st.markdown("#### Esplora Codici Turno per Deposito", unsafe_allow_html=True)
            try:
                df_codici = pd.read_sql("SELECT deposito, codice_turno, valid, dal, al FROM turni ORDER BY deposito, valid, codice_turno;", get_conn())
                df_codici["dal"] = pd.to_datetime(df_codici["dal"]).dt.strftime("%d/%m/%Y")
                df_codici["al"]  = pd.to_datetime(df_codici["al"]).dt.strftime("%d/%m/%Y")
                dep_esplora = st.selectbox("📍 Seleziona deposito",
                    options=sorted(df_codici["deposito"].unique()),format_func=lambda x: x.title(),key="dep_esplora")
                tipi_disp = sorted(df_codici[df_codici["deposito"]==dep_esplora]["valid"].unique())
                tipo_sel  = st.radio("Tipo giorno",["Tutti"]+tipi_disp,horizontal=True,key="tipo_esplora")
                df_dep_codici = df_codici[df_codici["deposito"]==dep_esplora].copy()
                if tipo_sel!="Tutti": df_dep_codici = df_dep_codici[df_dep_codici["valid"]==tipo_sel]

                k1,k2,k3 = st.columns(3)
                with k1: st.metric("🔢 Codici turno",len(df_dep_codici))
                with k2: st.metric("📋 Tipi giorno",df_dep_codici["valid"].nunique())
                with k3:
                    periodo = f"{df_dep_codici['dal'].iloc[0]} → {df_dep_codici['al'].iloc[0]}" if len(df_dep_codici)>0 else "—"
                    st.metric("📅 Validità",periodo)

                if len(df_dep_codici)>0:
                    colore_dep = get_colore_deposito(dep_esplora)
                    for tipo in sorted(df_dep_codici["valid"].unique()):
                        df_tipo = df_dep_codici[df_dep_codici["valid"]==tipo]
                        label_t = {"Lu-Ve":"Lunedì — Venerdì","Sa":"Sabato","Do":"Domenica"}.get(tipo,tipo)
                        st.markdown(
                            f"<p style='color:#d4850a !important;font-weight:600;font-size:0.95rem;margin:14px 0 8px;'>"
                            f"{label_t} <span style='color:#94a3b8 !important;font-size:0.8rem;font-weight:400;'>"
                            f"({len(df_tipo)} turni · {df_tipo['dal'].iloc[0]} → {df_tipo['al'].iloc[0]})</span></p>",
                            unsafe_allow_html=True)
                        codici = df_tipo["codice_turno"].tolist()
                        for i in range(0,len(codici),8):
                            cols = st.columns(8)
                            for j,codice in enumerate(codici[i:i+8]):
                                with cols[j]:
                                    st.markdown(
                                        f"<div style='background:rgba(255,255,255,0.8);"
                                        f"border:1px solid {colore_dep}44;border-left:3px solid {colore_dep};"
                                        f"border-radius:6px;padding:7px 5px;text-align:center;"
                                        f"font-size:0.82rem;font-weight:600;color:#1e293b !important;"
                                        f"margin-bottom:4px;'>{codice}</div>",unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"⚠️ Impossibile caricare i codici turno: {e}")

            st.markdown("---")
            st.markdown("#### Distribuzione Turni per Deposito", unsafe_allow_html=True)
            tot_per_dep = df_tc_agg.groupby("deposito")["turni"].sum().reset_index()
            fig_pie_tc = go.Figure(go.Pie(
                labels=[d.title() for d in tot_per_dep["deposito"]],
                values=tot_per_dep["turni"],
                marker=dict(colors=[get_colore_deposito(d) for d in tot_per_dep["deposito"]]),
                hole=0.45,textinfo="label+percent+value",textfont=dict(size=11),
                hovertemplate="<b>%{label}</b><br>Turni: %{value}<br>%{percent}<extra></extra>"))
            fig_pie_tc.update_layout(height=420,showlegend=True,
                paper_bgcolor="rgba(0,0,0,0)",legend=dict(font=dict(color="#475569",size=10)),
                margin=dict(l=20,r=20,t=20,b=20))
            st.plotly_chart(fig_pie_tc,use_container_width=True,key="pc_14")

            st.markdown("---")
            st.markdown("#### Turni per Tipo Giorno — Lu-Ve / Sabato / Domenica", unsafe_allow_html=True)
            try:
                date_list = df_tc_plot["giorno"].dt.date.unique().tolist()
                date_str  = ",".join([f"'{d}'" for d in date_list])
                df_cal_mini = pd.read_sql(f"SELECT data, daytype FROM calendar WHERE data IN ({date_str});",get_conn())
                df_cal_mini["data"] = pd.to_datetime(df_cal_mini["data"])
                def daytype_to_cat(dt):
                    dt = (dt or "").strip().lower()
                    if dt in ["lunedi","martedi","mercoledi","giovedi","venerdi"]: return "Lu-Ve"
                    elif dt=="sabato":   return "Sabato"
                    elif dt=="domenica": return "Domenica"
                    return dt.title()
                df_tc_dt = df_tc_plot.merge(df_cal_mini,left_on="giorno",right_on="data",how="left")
                df_tc_dt["categoria"] = df_tc_dt["daytype"].apply(daytype_to_cat)
                cat_order = ["Lu-Ve","Sabato","Domenica"]
                primo_gg  = df_tc_dt.groupby("categoria")["giorno"].min().to_dict()
                agg_list  = []
                for cat,gg in primo_gg.items():
                    agg_list.append(df_tc_dt[df_tc_dt["giorno"]==gg][["deposito","turni","categoria"]])
                agg_dt = pd.concat(agg_list,ignore_index=True) if agg_list else pd.DataFrame()
                if len(agg_dt)>0:
                    agg_dt["categoria"] = pd.Categorical(agg_dt["categoria"],categories=cat_order,ordered=True)
                    agg_dt = agg_dt.sort_values(["categoria","deposito"])
                    tot_cat = agg_dt.groupby("categoria")["turni"].sum().reindex(cat_order,fill_value=0)
                    fig_dt = go.Figure()
                    for dep in sorted(agg_dt["deposito"].unique()):
                        dep_d  = agg_dt[agg_dt["deposito"]==dep]
                        valori = [dep_d[dep_d["categoria"]==cat]["turni"].sum() if cat in dep_d["categoria"].values else 0 for cat in cat_order]
                        fig_dt.add_trace(go.Bar(x=cat_order,y=valori,name=dep.title(),
                            marker_color=get_colore_deposito(dep),
                            marker_line=dict(width=0.3,color="rgba(255,255,255,0.15)"),
                            text=[f"{v:,}" if v>0 else "" for v in valori],
                            textposition="inside",textfont=dict(size=10,color="white"),
                            hovertemplate=f"<b>{dep.title()}</b><br>%{{x}}: <b>%{{y:,}}</b><extra></extra>"))
                    fig_dt.update_layout(barmode="stack",height=460,hovermode="x unified",
                        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=10)),
                        annotations=[dict(x=cat,y=tot_cat[cat],text=f"<b>{int(tot_cat[cat]):,}</b>",
                            xanchor="center",yanchor="bottom",showarrow=False,
                            font=dict(size=12,color="#1e293b"),yshift=5) for cat in cat_order if tot_cat[cat]>0],
                        **PLOTLY_TEMPLATE)
                    st.plotly_chart(fig_dt,use_container_width=True,key="pc_15")
                    k1,k2,k3 = st.columns(3)
                    with k1: st.metric("📅 Turni/giorno Lu-Ve",f"{int(tot_cat.get('Lu-Ve',0)):,}")
                    with k2: st.metric("📅 Turni/giorno Sabato",f"{int(tot_cat.get('Sabato',0)):,}")
                    with k3: st.metric("📅 Turni/giorno Domenica",f"{int(tot_cat.get('Domenica',0)):,}")
            except Exception as e:
                st.warning(f"⚠️ Errore analisi tipo giorno: {e}")
        else:
            st.info("Nessun dato per la selezione corrente.")


# ══════════════════════════════════════════════════
# TAB 4 — DEPOSITI
# ══════════════════════════════════════════════════
with tab4:
    if len(df_filtered)>0 and len(by_deposito)>0:
        st.markdown("#### Ranking Depositi per Gap Medio", unsafe_allow_html=True)
        colors_dep = ['#ef4444' if g<soglia_gap else '#f97316' if g<0 else '#22c55e' for g in by_deposito["media_gap_giorno"]]
        fig_dep = go.Figure(go.Bar(
            y=by_deposito["deposito"],x=by_deposito["media_gap_giorno"],orientation='h',
            marker=dict(color=colors_dep),
            text=by_deposito["media_gap_giorno"],texttemplate='%{text:.1f}',textposition='outside',
            textfont=dict(size=11)))
        fig_dep.add_vline(x=0,line_width=2,line_color="#64748b")
        fig_dep.update_layout(height=max(400,len(by_deposito)*35),showlegend=False,**PLOTLY_TEMPLATE)
        st.plotly_chart(fig_dep,use_container_width=True,key="pc_16")

        st.markdown("---")
        st.markdown("#### Comparazione Multi-Dimensionale", unsafe_allow_html=True)
        by_dep_n = by_deposito.copy()
        for col_ in ['turni_richiesti','disponibili_netti','assenze_previste']:
            mx = by_dep_n[col_].max()
            by_dep_n[f'{col_}_n'] = by_dep_n[col_]/mx*100 if mx>0 else 0

        fig_radar = go.Figure()
        for _, row in by_deposito.head(6).iterrows():
            nr = by_dep_n[by_dep_n['deposito']==row['deposito']]
            if len(nr)>0:
                dep_color = get_colore_deposito(row['deposito'])
                dep_fill  = hex_to_rgba(dep_color, 0.12)
                fig_radar.add_trace(go.Scatterpolar(
                    r=[nr['turni_richiesti_n'].values[0],nr['disponibili_netti_n'].values[0],
                       100-nr['assenze_previste_n'].values[0],row['tasso_copertura_%']],
                    theta=['Turni Richiesti','Disponibili','Presenza','Copertura %'],
                    fill='toself',
                    fillcolor=dep_fill,
                    name=row['deposito'].title(),
                    line=dict(color=dep_color)))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True,range=[0,100],gridcolor='rgba(0,0,0,0.08)'),
                       bgcolor='rgba(255,255,255,0.6)'),
            height=480,paper_bgcolor='rgba(0,0,0,0)',font={'color':'#475569'})
        st.plotly_chart(fig_radar,use_container_width=True,key="pc_17")

        st.markdown("---")
        st.markdown("#### Tabella Dettagliata", unsafe_allow_html=True)
        st.dataframe(
            by_deposito[["deposito","dipendenti_medi_giorno","giorni_periodo",
                "disponibili_netti","assenze_previste","media_gap_giorno","tasso_copertura_%"]].rename(columns={
                "deposito":"Deposito","dipendenti_medi_giorno":"Autisti medi",
                "giorni_periodo":"Giorni","disponibili_netti":"Disponibili",
                "assenze_previste":"Assenze","media_gap_giorno":"Gap/Giorno","tasso_copertura_%":"Copertura %"}),
            use_container_width=True,hide_index=True)


# ══════════════════════════════════════════════════
# TAB 5 — EXPORT
# ══════════════════════════════════════════════════
with tab5:
    st.markdown("#### Export Dati e Report", unsafe_allow_html=True)
    col_exp1,col_exp2 = st.columns(2)
    df_export = df_filtered.copy()
    df_export["giorno"] = df_export["giorno"].dt.strftime('%d/%m/%Y')

    with col_exp1:
        st.markdown("##### Dataset Filtrato (CSV)")
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Scarica CSV",data=csv,
            file_name=f"estate2026_data_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv")
        st.info(f"📦 {len(df_export):,} righe × {len(df_export.columns)} colonne")
    with col_exp2:
        st.markdown("##### Summary Report (Excel)")
        output = BytesIO()
        with pd.ExcelWriter(output,engine='xlsxwriter') as writer:
            df_export.to_excel(writer,sheet_name='Staffing',index=False)
            if len(by_deposito)>0: by_deposito.to_excel(writer,sheet_name='Per_Deposito',index=False)
            if turni_cal_ok and len(df_tc_filtered)>0:
                tc_exp = df_tc_filtered.copy()
                tc_exp["giorno"] = tc_exp["giorno"].dt.strftime('%d/%m/%Y')
                tc_exp.to_excel(writer,sheet_name='Turni_Calendario',index=False)
        st.download_button("⬇️ Scarica Excel Report",data=output.getvalue(),
            file_name=f"estate2026_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.success("✅ Include: Staffing · Per deposito · Turni calendario")
    st.markdown("---")
    st.markdown("##### Anteprima Dataset")
    st.dataframe(df_export.head(100),use_container_width=True,height=400)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(f"""
<div style='text-align:center;padding:24px 0 16px;'>
    <p style='font-size:0.85rem;font-weight:600;color:#d4850a !important;letter-spacing:1px;'>
        ESTATE 2026 · ANALYTICS DASHBOARD
    </p>
    <p style='font-size:0.75rem;color:#94a3b8 !important;margin-top:6px;'>
        Streamlit · Plotly · PostgreSQL · Aggiornato: {datetime.now().strftime("%d/%m/%Y %H:%M")}
    </p>
    <p style='font-size:0.7rem;color:#94a3b8 !important;margin-top:10px;letter-spacing:0.5px;'>
        Progettato e sviluppato da <span style='color:#475569 !important;font-weight:600;'>Samuele Felici</span>
        &nbsp;·&nbsp; © {datetime.now().year} — Tutti i diritti riservati
    </p>
</div>
""", unsafe_allow_html=True)
