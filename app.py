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
    "ancona": "#22c55e", "polverigi": "#166534",
    "marina": "#ec4899", "marina di montemarciano": "#ec4899",
    "filottrano": "#a855f7", "jesi": "#f97316", "osimo": "#eab308",
    "castelfidardo": "#38bdf8", "castelfdardo": "#38bdf8",
    "ostra": "#ef4444", "belvedere ostrense": "#94a3b8",
    "belvedereostrense": "#94a3b8", "depbelvede": "#94a3b8", "moie": "#a78bfa",
}

def get_colore_deposito(dep: str) -> str:
    return COLORI_DEPOSITI.get(str(dep).strip().lower(), "#64748b")

def hex_to_rgba(hx: str, a: float = 0.15) -> str:
    h = hx.lstrip('#')
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"

# ==================================================
# GLOBAL LIGHT THEME OVERRIDE  (applies to ALL pages)
# ==================================================
st.markdown("""<style>
    /* NUCLEAR OPTION — force light on every element */
    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    .main, .block-container,
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"] {
        background-color: #faf9f6 !important;
        color: #1e293b !important;
    }
    [data-testid="stHeader"] {
        background: rgba(250,249,246,0.85) !important;
        backdrop-filter: blur(12px) !important;
    }
    /* Sidebar warm cream */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div > div,
    [data-testid="stSidebar"] [data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fdf8f0 0%, #f7efe3 50%, #f5ead8 100%) !important;
        color: #44403c !important;
    }
    [data-testid="stSidebar"] * {
        color: #44403c !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #78350f !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #e8d5be !important;
    }
    [data-testid="stSidebar"] .stSuccess {
        background: rgba(34,197,94,0.1) !important;
        color: #166534 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] > div {
        background: #ffffff !important;
        border-color: #e8d5be !important;
    }
    /* Border-right on sidebar */
    [data-testid="stSidebar"]::after {
        content: '';
        position: absolute; top: 0; right: 0; bottom: 0;
        width: 1px;
        background: linear-gradient(180deg, #e8d5be, #d4b896, #e8d5be);
    }
</style>""", unsafe_allow_html=True)


# ==================================================
# LOGIN
# ==================================================
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

    yr = datetime.now().year

    # Login-specific overrides — cream/warm white
    st.markdown(f"""<style>
    /* === LOGIN PAGE === */
    [data-testid="stSidebar"] {{ display: none !important; }}
    footer {{ display: none !important; }}
    .block-container {{ padding-top: 0 !important; max-width: 100% !important; }}

    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    .main, .block-container {{
        background: linear-gradient(160deg, #fffcf5 0%, #faf3e6 40%, #f7efe0 70%, #fdf8f0 100%) !important;
    }}
    [data-testid="stHeader"] {{
        background: rgba(255,252,245,0.7) !important;
    }}

    @keyframes gentleFloat {{
        0%   {{ transform: translateY(0); opacity:0; }}
        15%  {{ opacity:0.45; }}
        85%  {{ opacity:0.2; }}
        100% {{ transform: translateY(-100vh); opacity:0; }}
    }}

    .login-dot {{
        position: fixed; border-radius: 50%; pointer-events: none; z-index: 0;
        animation: gentleFloat linear infinite;
    }}

    /* Password input */
    div[data-testid="stTextInput"] > div > div {{
        background: #ffffff !important;
        border: 1.5px solid #d4b896 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 12px rgba(180,83,9,0.06) !important;
    }}
    div[data-testid="stTextInput"] > div > div:focus-within {{
        border-color: #b45309 !important;
        box-shadow: 0 0 0 3px rgba(180,83,9,0.1), 0 2px 12px rgba(180,83,9,0.08) !important;
    }}
    div[data-testid="stTextInput"] input {{
        color: #1e293b !important;
        font-size: 1rem !important;
        letter-spacing: 2px !important;
        background: transparent !important;
    }}
    div[data-testid="stTextInput"] label {{ display: none !important; }}

    .ca-logo-img {{
        transition: transform 0.4s ease;
        filter: drop-shadow(0 4px 12px rgba(0,0,0,0.08));
    }}
    .ca-logo-img:hover {{
        transform: scale(1.02);
    }}

    /* Footer bar */
    .login-footer {{
        position: fixed; bottom: 0; left: 0; right: 0;
        padding: 12px 20px 14px;
        background: rgba(255,252,245,0.92);
        border-top: 1px solid #e8d5be;
        backdrop-filter: blur(12px);
        z-index: 9999;
    }}
    .login-footer-row {{
        display: flex; justify-content: center; align-items: center;
        gap: 16px; flex-wrap: wrap;
    }}
    .login-footer-item {{
        color: #a18e79; font-size: 0.68rem; letter-spacing: 1.3px;
        text-transform: uppercase; display: flex; align-items: center; gap: 5px;
    }}
    .login-footer-item svg {{ color: #c9a96e; }}
    .login-footer-sep {{ color: #d4b896; font-size: 0.7rem; }}
    .login-credits {{
        text-align: center; margin-top: 8px;
        font-size: 0.66rem; color: #a18e79; letter-spacing: 0.4px;
    }}
    .login-credits b {{ color: #78350f; }}
    </style>

st.markdown(f"""
<style>
/* === LOGIN PAGE === */
[data-testid="stSidebar"] {{ display: none !important; }}
footer {{ display: none !important; }}
.block-container {{ padding-top: 0 !important; max-width: 100% !important; }}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container {{
    background: linear-gradient(160deg, #fffcf5 0%, #faf3e6 40%, #f7efe0 70%, #fdf8f0 100%) !important;
}}

/* Dots senza HTML: solo background layers */
@keyframes bgFloat {{
  0%   {{ background-position: 10% 110%, 30% 110%, 55% 110%, 78% 110%, 92% 110%; opacity: 0; }}
  15%  {{ opacity: .45; }}
  85%  {{ opacity: .2; }}
  100% {{ background-position: 10% -20%, 30% -25%, 55% -18%, 78% -22%, 92% -28%; opacity: 0; }}
}}

[data-testid="stAppViewContainer"] {{
  background-image:
    radial-gradient(circle, #d4b896 0 2px, transparent 3px),
    radial-gradient(circle, #c9a96e 0 1.5px, transparent 2.5px),
    radial-gradient(circle, #e8d5be 0 1.5px, transparent 2.5px),
    radial-gradient(circle, #c9a96e 0 2px, transparent 3px),
    radial-gradient(circle, #d4b896 0 1.5px, transparent 2.5px);
  background-repeat: no-repeat;
  animation: bgFloat 14s linear infinite;
}}

</style>
""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<div style='height:12vh'></div>", unsafe_allow_html=True)

        if logo_b64:
            st.markdown(
                f"<div style='text-align:center; margin-bottom:28px;'>"
                f"<img class='ca-logo-img' src='data:image/png;base64,{logo_b64}' "
                f"style='height:380px; width:auto;'/>"
                f"</div>", unsafe_allow_html=True)

        def _entered():
            if st.session_state["_pwd"] == st.secrets["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
            else:
                st.session_state["password_correct"] = False

        st.text_input("Password", type="password", on_change=_entered, key="_pwd",
            placeholder="🔒  Inserisci password", label_visibility="collapsed")

        if st.session_state.get("password_correct") is False:
            st.error("❌ Password errata")

    st.markdown(f"""
    <div class='login-footer'>
        <div class='login-footer-row'>
            <span class='login-footer-item'>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                Connessione cifrata</span>
            <span class='login-footer-sep'>·</span>
            <span class='login-footer-item'>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                Sistema protetto</span>
            <span class='login-footer-sep'>·</span>
            <span class='login-footer-item'>Estate 2026</span>
        </div>
        <p class='login-credits'>
            Progettato e sviluppato da <b>Samuele Felici</b> &nbsp;·&nbsp; &copy; {yr} — Tutti i diritti riservati
        </p>
    </div>
    """, unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()


# ==================================================
# SPLASH SCREEN — LIGHT WARM
# ==================================================
if not st.session_state.get("splash_done"):
    st.session_state["splash_done"] = True
    st.markdown("""<style>
    [data-testid="stSidebar"] { display:none !important; }
    footer { display:none !important; }
    .block-container { padding:0 !important; max-width:100% !important; }
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    .main, .block-container {
        background: linear-gradient(160deg,#fffcf5,#faf3e6,#f7efe0) !important;
        overflow: hidden !important;
    }

    @keyframes fadeOutSplash { 0%,72%{opacity:1} 100%{opacity:0} }
    @keyframes progressFill  { from{width:0%} to{width:100%} }
    @keyframes pulseCore {
      0%,100% { transform:translate(-50%,-50%) scale(1);
                box-shadow:0 0 20px 5px rgba(180,83,9,0.25), 0 0 50px 15px rgba(180,83,9,0.08); }
      50%     { transform:translate(-50%,-50%) scale(1.08);
                box-shadow:0 0 30px 10px rgba(180,83,9,0.4), 0 0 70px 25px rgba(180,83,9,0.12); }
    }
    @keyframes spinR { from{transform:translate(-50%,-50%) rotate(0deg)} to{transform:translate(-50%,-50%) rotate(360deg)} }
    @keyframes spinL { from{transform:translate(-50%,-50%) rotate(0deg)} to{transform:translate(-50%,-50%) rotate(-360deg)} }
    @keyframes textPulse { 0%,100%{opacity:0.3} 50%{opacity:0.7} }

    .sp-wrap {
        position:fixed; inset:0; z-index:99999;
        background: linear-gradient(160deg,#fffcf5,#faf3e6,#f7efe0);
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        animation: fadeOutSplash 3.2s ease forwards;
    }
    .sp-arena { position:relative; width:240px; height:240px; margin-bottom:24px; }
    .sp-core {
        position:absolute; top:50%; left:50%; width:28px; height:28px;
        border-radius:50%;
        background: radial-gradient(circle, #fbbf24 0%, #f59e0b 35%, #d97706 65%, #b45309 100%);
        animation: pulseCore 2s ease-in-out infinite; z-index:10;
        transform: translate(-50%,-50%);
    }
    .sp-ring {
        position:absolute; top:50%; left:50%; border-radius:50%;
        border:1.5px solid transparent;
    }
    .sp-ring-1 {
        width:140px; height:140px;
        border-top-color: rgba(180,83,9,0.35);
        border-right-color: rgba(180,83,9,0.08);
        animation: spinR 2.5s linear infinite;
        transform: translate(-50%,-50%);
    }
    .sp-ring-2 {
        width:200px; height:200px;
        border-bottom-color: rgba(201,169,110,0.3);
        border-left-color: rgba(201,169,110,0.06);
        animation: spinL 3.5s linear infinite;
        transform: translate(-50%,-50%);
    }
    .sp-label {
        color: #a18e79; font-size:0.65rem; letter-spacing:3px;
        text-transform:uppercase; margin:0 0 12px;
        animation: textPulse 2s ease-in-out infinite;
    }
    .sp-bar-wrap {
        width:160px; height:2px; background:rgba(180,83,9,0.1);
        border-radius:2px; overflow:hidden;
    }
    .sp-bar {
        height:100%;
        background: linear-gradient(90deg,#b45309,#f59e0b,#b45309);
        background-size:200% 100%;
        animation: progressFill 2.8s cubic-bezier(.4,0,.2,1) forwards;
    }
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
    import time; time.sleep(3.0); st.rerun()


# ==================================================
# CSS DASHBOARD — WARM LIGHT MODERN
# ==================================================
st.markdown("""<style>
    /* ── TITOLI ── */
    h1 { color: #92400e !important; font-weight: 800 !important; letter-spacing: 0.3px; font-size: 2.3rem !important; }
    h2 { color: #1e293b !important; font-weight: 700 !important; margin-top: 20px !important; font-size: 1.25rem !important; }
    h3 { color: #334155 !important; font-weight: 600 !important; font-size: 1.05rem !important; }
    h4 { color: #1e293b !important; font-weight: 700 !important; }
    h5 { color: #334155 !important; font-weight: 600 !important; }
    p, span, label, div { color: #475569; }

    /* ── KPI CARDS ── */
    [data-testid="metric-container"] {
        background: #ffffff !important;
        padding: 18px 16px; border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);
        border: 1px solid #f1ece4;
        transition: all 0.2s ease;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(180,83,9,0.08);
        border-color: #e8d5be;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.9rem !important; font-weight: 800 !important;
        color: #92400e !important; line-height: 1.1 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important; font-weight: 600 !important;
        color: #78716c !important; text-transform: uppercase; letter-spacing: 0.7px;
    }
    [data-testid="stMetricDelta"] { font-size: 0.78rem !important; font-weight: 600 !important; }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; background: #ffffff; padding: 6px; border-radius: 12px;
        border: 1px solid #ede5d8; box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; border-radius: 8px;
        color: #78716c !important; font-weight: 600; font-size: 0.86rem;
        padding: 10px 18px; border: 1px solid transparent !important;
        transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #fffbf0 !important;
        color: #92400e !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg,#fef3c7,#fde68a) !important;
        color: #78350f !important;
        border-color: #fbbf24 !important;
        box-shadow: 0 1px 3px rgba(251,191,36,0.25) !important;
    }

    /* ── ALERTS ── */
    .alert-critical { background:#fef2f2; padding:14px 18px; border-radius:10px; color:#991b1b !important; border:1px solid #fecaca; border-left:4px solid #ef4444; margin:12px 0; }
    .alert-warning  { background:#fffbeb; padding:14px 18px; border-radius:10px; color:#92400e !important; border:1px solid #fde68a; border-left:4px solid #f59e0b; margin:12px 0; }
    .alert-success  { background:#f0fdf4; padding:14px 18px; border-radius:10px; color:#166534 !important; border:1px solid #bbf7d0; border-left:4px solid #22c55e; margin:12px 0; }

    /* ── CHARTS / DATAFRAME / EXPANDER ── */
    .js-plotly-plot { border-radius: 14px; border: 1px solid #ede5d8; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #ede5d8; }
    [data-testid="stExpander"] { background: #ffffff !important; border: 1px solid #ede5d8 !important; border-radius: 10px !important; }

    /* ── BOTTONI ── */
    .stDownloadButton button {
        background: linear-gradient(135deg,#22c55e,#16a34a) !important;
        color: #fff !important; border: none !important; border-radius: 8px !important;
    }
    .stDownloadButton button:hover { box-shadow: 0 4px 12px rgba(34,197,94,0.3) !important; }
    button[kind="primary"], div.stButton > button {
        background: linear-gradient(135deg,#f59e0b,#d97706) !important;
        color: #fff !important; border: none !important; border-radius: 8px !important;
    }

    /* ── INPUTS ── */
    input, select, textarea,
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        background: #ffffff !important; color: #1e293b !important;
        border-color: #e2ddd4 !important; border-radius: 8px !important;
    }

    /* ── INSIGHT CARD ── */
    .insight-card {
        background: #ffffff; padding: 16px; border-radius: 12px;
        border: 1px solid #f1ece4; margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03); transition: all 0.2s;
    }
    .insight-card:hover { border-color: #d4b896; box-shadow: 0 4px 12px rgba(180,83,9,0.06); }
    .insight-card h4 { color: #92400e !important; margin-bottom: 6px !important; font-size: 0.92rem !important; }

    /* ── SEPARATORS ── */
    hr { border-color: #ede5d8 !important; margin: 18px 0 !important; }

    /* ── LEGEND BOX ── */
    .legend-box {
        background: #ffffff; border: 1px solid #ede5d8; border-radius: 10px;
        padding: 10px 14px; font-size: 0.78rem; color: #78716c;
        display: flex; flex-wrap: wrap; gap: 14px; align-items: center; margin: 8px 0 14px;
    }
    .legend-item { display: flex; align-items: center; gap: 5px; }
    .legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
</style>""", unsafe_allow_html=True)


# --------------------------------------------------
# TEMPLATE PLOTLY
# --------------------------------------------------
PLOTLY_TEMPLATE = {
    'plot_bgcolor':  '#ffffff',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'font': {'color': '#475569', 'family': 'Inter, -apple-system, sans-serif', 'size': 12},
    'xaxis': {'gridcolor': '#f5f0e8', 'linecolor': '#ede5d8', 'zerolinecolor': '#ede5d8'},
    'yaxis': {'gridcolor': '#f5f0e8', 'linecolor': '#ede5d8', 'zerolinecolor': '#ede5d8'},
}


# ==================================================
# DATABASE
# ==================================================
def get_conn():
    if "db_conn" not in st.session_state or st.session_state["db_conn"].closed:
        st.session_state["db_conn"] = psycopg2.connect(st.secrets["DATABASE_URL"], sslmode="require")
    else:
        try:
            c = st.session_state["db_conn"].cursor(); c.execute("SELECT 1;"); c.close()
        except Exception:
            st.session_state["db_conn"] = psycopg2.connect(st.secrets["DATABASE_URL"], sslmode="require")
    return st.session_state["db_conn"]

conn = get_conn()
try:
    cur = conn.cursor(); cur.execute("SELECT NOW();"); db_time = cur.fetchone()[0]; cur.close()
    st.sidebar.success(f"✅ DB connesso — {db_time.strftime('%d/%m/%Y %H:%M')}")
except Exception as e:
    st.sidebar.error(f"❌ Errore DB: {e}"); st.stop()


# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data(ttl=600)
def load_staffing():
    return pd.read_sql("SELECT giorno,tipo_giorno,deposito,totale_autisti,assenze_programmate,assenze_previste,infortuni,malattie,legge_104,altre_assenze,congedo_parentale,permessi_vari,turni_richiesti,disponibili_netti,gap FROM v_staffing ORDER BY giorno,deposito;", get_conn())

@st.cache_data(ttl=600)
def load_depositi_stats():
    return pd.read_sql("SELECT deposito,giorni_attivi,dipendenti_medi_giorno FROM v_depositi_organico_medio ORDER BY deposito;", get_conn())

@st.cache_data(ttl=600)
def load_turni_calendario():
    return pd.read_sql("SELECT tg.data AS giorno,tg.deposito,COUNT(tg.id) AS turni FROM turni_giornalieri tg GROUP BY tg.data,tg.deposito ORDER BY tg.data,tg.deposito;", get_conn())

@st.cache_data(ttl=600)
def load_copertura():
    return pd.read_sql("""
        WITH forza AS (SELECT r.data AS giorno,r.deposito,COUNT(DISTINCT r.matricola) AS persone_in_forza,COUNT(*) FILTER (WHERE r.turno IS NOT NULL AND TRIM(r.turno)<>'') AS assenze_nominali FROM roster r GROUP BY r.data,r.deposito),
        turni AS (SELECT data AS giorno,deposito,COUNT(*) AS turni_richiesti FROM turni_giornalieri GROUP BY data,deposito),
        ass AS (SELECT c.data AS giorno,a.deposito,ROUND(COALESCE(a.infortuni,0)+COALESCE(a.malattie,0)+COALESCE(a.legge_104,0)+COALESCE(a.altre_assenze,0)+COALESCE(a.congedo_parentale,0)+COALESCE(a.permessi_vari,0))::int AS assenze_statistiche FROM assenze a JOIN calendar c ON c.daytype=a.daytype)
        SELECT f.giorno,f.deposito,f.persone_in_forza,COALESCE(t.turni_richiesti,0) AS turni_richiesti,f.assenze_nominali,COALESCE(a.assenze_statistiche,0) AS assenze_statistiche,f.persone_in_forza-COALESCE(t.turni_richiesti,0)-f.assenze_nominali-COALESCE(a.assenze_statistiche,0) AS gap
        FROM forza f LEFT JOIN turni t USING(giorno,deposito) LEFT JOIN ass a USING(giorno,deposito) ORDER BY f.giorno,f.deposito;
    """, get_conn())

try:
    df_raw = load_staffing(); df_raw["giorno"] = pd.to_datetime(df_raw["giorno"])
    df_depositi = load_depositi_stats()
    df_raw = df_raw[df_raw["deposito"]!="depbelvede"].copy()
    df_depositi = df_depositi[df_depositi["deposito"]!="depbelvede"].copy()
except Exception as e:
    st.error(f"❌ {e}"); st.stop()

try:
    df_turni_cal = load_turni_calendario(); df_turni_cal["giorno"] = pd.to_datetime(df_turni_cal["giorno"])
    turni_cal_ok = len(df_turni_cal)>0
except Exception:
    df_turni_cal = pd.DataFrame(); turni_cal_ok = False

try:
    df_copertura = load_copertura(); df_copertura["giorno"] = pd.to_datetime(df_copertura["giorno"])
except Exception:
    df_copertura = pd.DataFrame()


# ==================================================
# UTILITY
# ==================================================
def categorizza_tipo_giorno(tipo):
    t = (tipo or "").strip().lower()
    if t in ['lunedi','martedi','mercoledi','giovedi','venerdi']: return 'Lu-Ve'
    elif t=='sabato': return 'Sabato'
    elif t=='domenica': return 'Domenica'
    return tipo

def applica_ferie_10gg(df_in):
    df = df_in.copy()
    df["deposito_norm"] = df["deposito"].astype(str).str.strip().str.lower()
    df["ferie_extra"] = 0.0
    df.loc[df["deposito_norm"]=="ancona","ferie_extra"] += 5.0
    mask = ~df["deposito_norm"].isin(["ancona","moie"])
    el = df[mask].copy()
    if not el.empty:
        el["peso"] = el["totale_autisti"].clip(lower=0)
        s = el.groupby("giorno")["peso"].transform("sum")
        el["quota"] = np.where(s>0,5.0*el["peso"]/s,0.0)
        df.loc[el.index,"ferie_extra"] += el["quota"].values
    df["assenze_previste_adj"] = df["assenze_previste"]+df["ferie_extra"]
    df["disponibili_netti_adj"] = (df["disponibili_netti"]-df["ferie_extra"]).clip(lower=0)
    df["gap_adj"] = df["gap"]-df["ferie_extra"]
    df.drop(columns=["deposito_norm"],inplace=True)
    return df

df_raw["categoria_giorno"] = df_raw["tipo_giorno"].apply(categorizza_tipo_giorno)


# ==================================================
# SIDEBAR CONTROLS
# ==================================================
st.sidebar.markdown("## ⚙️ Controlli")
st.sidebar.markdown("---")
modalita = st.sidebar.radio("📊 Vista",["Dashboard Completa","Analisi Comparativa","Report Esportabile"])
st.sidebar.markdown("---")
depositi_lista = sorted(df_raw["deposito"].unique())
deposito_sel = st.sidebar.multiselect("📍 Depositi",depositi_lista,default=depositi_lista)
min_date = df_raw["giorno"].min().date(); max_date = df_raw["giorno"].max().date()
date_range = st.sidebar.date_input("📅 Periodo",value=(min_date,max_date),min_value=min_date,max_value=max_date)
st.sidebar.markdown("---")
soglia_gap = st.sidebar.slider("⚠️ Soglia Critica",min_value=-50,max_value=0,value=-10)
ferie_10 = st.sidebar.checkbox("✅ Con 10 gg ferie (5 AN + 5 altri)",value=False)
with st.sidebar.expander("🔧 Filtri Avanzati"):
    show_forecast = st.checkbox("📈 Previsioni",value=True)
    show_insights = st.checkbox("💡 Insights",value=True)
    min_gap_filter = st.number_input("Gap Min",value=-100)
    max_gap_filter = st.number_input("Gap Max",value=100)
st.sidebar.markdown("---")


# ==================================================
# APPLY FILTERS
# ==================================================
if len(date_range)==2:
    df_filtered = df_raw[(df_raw["deposito"].isin(deposito_sel))&(df_raw["giorno"]>=pd.to_datetime(date_range[0]))&(df_raw["giorno"]<=pd.to_datetime(date_range[1]))].copy()
else:
    df_filtered = df_raw[df_raw["deposito"].isin(deposito_sel)].copy()

if ferie_10:
    try:
        df_filtered = applica_ferie_10gg(df_filtered)
        df_filtered["assenze_previste"] = df_filtered["assenze_previste_adj"]
        df_filtered["disponibili_netti"] = df_filtered["disponibili_netti_adj"]
        df_filtered["gap"] = df_filtered["gap_adj"]
    except Exception as e:
        st.error(f"❌ {e}"); st.stop()

df_filtered = df_filtered[(df_filtered["gap"]>=min_gap_filter)&(df_filtered["gap"]<=max_gap_filter)].copy()

# copertura filter
if len(df_copertura)>0:
    if ferie_10:
        df_cop = df_copertura.copy()
        df_cop["dn"] = df_cop["deposito"].str.strip().str.lower()
        df_cop["fe"] = 0.0
        df_cop.loc[df_cop["dn"]=="ancona","fe"] += 5.0
        me = ~df_cop["dn"].isin(["ancona","moie"])
        el2 = df_cop[me].copy()
        if not el2.empty:
            el2["p"] = el2["persone_in_forza"].clip(lower=0)
            s2 = el2.groupby("giorno")["p"].transform("sum")
            el2["q"] = np.where(s2>0,5.0*el2["p"]/s2,0.0)
            df_cop.loc[el2.index,"fe"] += el2["q"].values
        df_cop["assenze_nominali"] = df_cop["assenze_nominali"]+df_cop["fe"]
        df_cop["gap"] = df_cop["persone_in_forza"]-df_cop["turni_richiesti"]-df_cop["assenze_nominali"]-df_cop["assenze_statistiche"]
        df_cop.drop(columns=["dn","fe"],inplace=True)
        df_copertura_filtered = df_cop
    else:
        df_copertura_filtered = df_copertura.copy()
    if len(date_range)==2:
        df_copertura_filtered = df_copertura_filtered[(df_copertura_filtered["giorno"]>=pd.to_datetime(date_range[0]))&(df_copertura_filtered["giorno"]<=pd.to_datetime(date_range[1]))&(df_copertura_filtered["deposito"].isin(deposito_sel))]
    else:
        df_copertura_filtered = df_copertura_filtered[df_copertura_filtered["deposito"].isin(deposito_sel)]
else:
    df_copertura_filtered = pd.DataFrame()

if turni_cal_ok:
    if len(date_range)==2:
        df_tc_filtered = df_turni_cal[(df_turni_cal["giorno"]>=pd.to_datetime(date_range[0]))&(df_turni_cal["giorno"]<=pd.to_datetime(date_range[1]))&(df_turni_cal["deposito"].isin(deposito_sel))].copy()
    else:
        df_tc_filtered = df_turni_cal[df_turni_cal["deposito"].isin(deposito_sel)].copy()
else:
    df_tc_filtered = pd.DataFrame()


# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div style='margin-bottom:1rem;'>
    <h1 style='margin-bottom:0 !important;'>Estate 2026</h1>
    <p style='color:#78716c !important;font-size:0.92rem;font-weight:500;margin:2px 0 0;'>
        Analytics Dashboard · Conerobus S.p.A.</p>
</div>""", unsafe_allow_html=True)

if len(date_range)==2:
    fb = " · 🏖️ Ferie simulate" if ferie_10 else ""
    st.markdown(f"<p style='font-size:0.82rem;color:#a8a29e !important;margin-top:-10px;'>"
        f"{date_range[0].strftime('%d/%m/%Y')} → {date_range[1].strftime('%d/%m/%Y')} · "
        f"{len(deposito_sel)} depositi · {len(df_filtered):,} records{fb}</p>",unsafe_allow_html=True)
st.markdown("---")


# ==================================================
# KPI
# ==================================================
st.markdown("### Key Performance Indicators")
if len(df_filtered)>0:
    totale_dipendenti = df_depositi[df_depositi["deposito"].isin(deposito_sel)]["dipendenti_medi_giorno"].sum()
    gap_per_giorno = df_filtered.groupby("giorno")["gap"].sum()
    gap_medio_giorno = gap_per_giorno.mean()
    media_turni_giorno = df_filtered.groupby("giorno")["turni_richiesti"].sum().mean()
    gap_pct_medio = (gap_medio_giorno/media_turni_giorno*100) if media_turni_giorno>0 else 0
    giorni_analizzati = df_filtered["giorno"].nunique()
    giorni_critici_count = int((gap_per_giorno<soglia_gap).sum())
    pct_critici = (giorni_critici_count/giorni_analizzati*100) if giorni_analizzati>0 else 0
    turni_luv = df_filtered[df_filtered["tipo_giorno"].str.lower().isin(['lunedi','martedi','mercoledi','giovedi','venerdi'])].groupby("giorno")["turni_richiesti"].sum().mean()
    turni_luv = int(turni_luv) if not np.isnan(turni_luv) else 0
    k1,k2,k3,k4 = st.columns(4)
    with k1: st.metric("👤 Autisti",f"{int(totale_dipendenti):,}")
    with k2: st.metric("🚌 Turni/gg Lu-Ve",f"{turni_luv:,}")
    with k3: st.metric("⚖️ Gap Medio/gg",f"{int(gap_medio_giorno):,}",delta=f"{gap_pct_medio:.1f}%",delta_color="normal" if gap_medio_giorno>=0 else "inverse")
    with k4: st.metric("🚨 Giorni Critici",f"{giorni_critici_count}/{giorni_analizzati}",delta=f"{pct_critici:.0f}%",delta_color="inverse")
st.markdown("---")

# INSIGHTS
if show_insights and len(df_filtered)>0:
    st.markdown("### Insights")
    ic1,ic2,ic3 = st.columns(3)
    with ic1:
        bd = df_filtered.groupby("deposito")["gap"].mean(); wd = bd.idxmin()
        st.markdown(f"<div class='insight-card'><h4>⚠ Deposito Critico</h4><p style='color:#1e293b !important;'><b>{wd}</b> — gap medio: <b>{bd.min():.1f}</b></p></div>",unsafe_allow_html=True)
    with ic2:
        bc = df_filtered.groupby("categoria_giorno")["gap"].mean(); wc = bc.idxmin()
        st.markdown(f"<div class='insight-card'><h4>📅 Giorno Critico</h4><p style='color:#1e293b !important;'><b>{wc}</b> — gap medio: <b>{bc.min():.1f}</b></p></div>",unsafe_allow_html=True)
    with ic3:
        at_ = df_filtered.groupby("giorno")["assenze_previste"].sum()
        tt = "crescente" if len(at_)>1 and at_.iloc[-1]>at_.iloc[0] else "decrescente" if len(at_)>1 else "stabile"
        ti = "📈" if tt=="crescente" else "📉" if tt=="decrescente" else "➡️"
        st.markdown(f"<div class='insight-card'><h4>📊 Trend Assenze</h4><p style='color:#1e293b !important;'>{ti} Trend <b>{tt}</b></p></div>",unsafe_allow_html=True)
    st.markdown("---")


# ==================================================
# AGGREGATI
# ==================================================
if len(df_filtered)>0:
    by_deposito = df_filtered.groupby("deposito").agg(turni_richiesti=("turni_richiesti","sum"),disponibili_netti=("disponibili_netti","sum"),gap=("gap","sum"),assenze_previste=("assenze_previste","sum")).reset_index()
    by_deposito = by_deposito.merge(df_depositi,on="deposito",how="left")
    gpd = df_filtered.groupby("deposito")["giorno"].nunique().rename("giorni_periodo")
    by_deposito = by_deposito.merge(gpd,left_on="deposito",right_index=True)
    by_deposito["media_gap_giorno"] = (by_deposito["gap"]/by_deposito["giorni_periodo"]).round(1)
    by_deposito["tasso_copertura_%"] = (by_deposito["disponibili_netti"]/by_deposito["turni_richiesti"]*100).fillna(0).round(1)
    by_deposito = by_deposito.sort_values("media_gap_giorno")
else:
    by_deposito = pd.DataFrame()


# ==================================================
# TABS
# ==================================================
tab1,tab2,tab3,tab4,tab5 = st.tabs(["📊 Overview","📈 Analisi & Assenze","🚌 Turni Calendario","🎯 Depositi","📥 Export"])

# ───────── TAB 1 ─────────
with tab1:
    if len(df_filtered)==0: st.info("Nessun dato.")
    else:
        st.markdown("#### Copertura del Servizio")
        st.markdown("<p style='font-size:0.85rem;'><span style='color:#22c55e;'>Verde</span> = buffer · <span style='color:#ef4444;'>Rosso</span> = deficit</p>",unsafe_allow_html=True)
        if len(df_copertura_filtered)>0:
            cop = df_copertura_filtered.groupby("giorno").agg(persone_in_forza=("persone_in_forza","sum"),turni_richiesti=("turni_richiesti","sum"),assenze_nominali=("assenze_nominali","sum"),assenze_statistiche=("assenze_statistiche","sum"),gap=("gap","sum")).reset_index()
            kc1,kc2,kc3,kc4 = st.columns(4)
            with kc1: st.metric("👥 Media/gg",f"{cop['persone_in_forza'].mean():.0f}")
            with kc2: st.metric("✅ Giorni OK",f"{int((cop['gap']>=0).sum())}")
            with kc3: st.metric("🚨 Deficit",f"{int((cop['gap']<0).sum())}")
            with kc4: st.metric("📉 Gap medio",f"{cop['gap'].mean():.1f}",delta=f"min: {cop['gap'].min():.0f}")

            fig_cop = make_subplots(rows=2,cols=1,row_heights=[0.70,0.30],shared_xaxes=True,vertical_spacing=0.05,subplot_titles=("Distribuzione persone in forza","Buffer / Deficit"))
            fig_cop.add_trace(go.Bar(x=cop["giorno"],y=cop["turni_richiesti"],name="Turni",marker_color="#94a3b8"),row=1,col=1)
            fig_cop.add_trace(go.Bar(x=cop["giorno"],y=cop["assenze_nominali"],name="Assenze roster",marker_color="#cbd5e1"),row=1,col=1)
            fig_cop.add_trace(go.Bar(x=cop["giorno"],y=cop["assenze_statistiche"],name="Assenze storiche",marker_color="#e2e8f0"),row=1,col=1)
            bc = ["rgba(34,197,94,0.8)" if g>=0 else "rgba(239,68,68,0.85)" for g in cop["gap"]]
            fig_cop.add_trace(go.Bar(x=cop["giorno"],y=cop["gap"],name="Buffer/Deficit",marker=dict(color=bc),text=[f"{int(g)}" if g<0 else "" for g in cop["gap"]],textposition="outside",textfont=dict(size=10,color="#ef4444")),row=1,col=1)
            fig_cop.add_trace(go.Scatter(x=cop["giorno"],y=cop["persone_in_forza"],name="In forza",mode="lines",line=dict(color="#78716c",width=2,dash="dot")),row=1,col=1)
            gc2 = ["rgba(34,197,94,0.8)" if g>=0 else "rgba(239,68,68,0.85)" for g in cop["gap"]]
            fig_cop.add_trace(go.Bar(x=cop["giorno"],y=cop["gap"],marker=dict(color=gc2),text=[f"{int(g)}" for g in cop["gap"]],textposition="outside",textfont=dict(size=9,color="#475569"),showlegend=False),row=2,col=1)
            fig_cop.add_hline(y=0,line_color="#94a3b8",line_width=1,row=2,col=1)
            if soglia_gap<0: fig_cop.add_hline(y=soglia_gap,line_dash="dash",line_color="#ef4444",line_width=2,annotation_text=f"Soglia ({soglia_gap})",annotation_font=dict(color="#ef4444",size=10),row=2,col=1)
            fig_cop.update_layout(barmode="stack",height=680,hovermode="x unified",legend=dict(orientation="h",y=1.02,xanchor="right",x=1,font=dict(size=10),bgcolor="rgba(255,255,255,0.8)"),plot_bgcolor="#ffffff",paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#475569"),margin=dict(t=60,b=20,l=10,r=10))
            fig_cop.update_xaxes(tickformat="%d/%m",tickangle=-45,gridcolor="#f5f0e8",linecolor="#ede5d8")
            fig_cop.update_yaxes(gridcolor="#f5f0e8",linecolor="#ede5d8",zeroline=False)
            fig_cop.update_yaxes(title_text="Persone",row=1,col=1); fig_cop.update_yaxes(title_text="Gap",row=2,col=1)
            st.plotly_chart(fig_cop,use_container_width=True,key="pc1")
            st.markdown("""<div class='legend-box'><div class='legend-item'><div class='legend-dot' style='background:#94a3b8;'></div> Turni</div><div class='legend-item'><div class='legend-dot' style='background:#cbd5e1;'></div> Assenze roster</div><div class='legend-item'><div class='legend-dot' style='background:#e2e8f0;'></div> Assenze storiche</div><div class='legend-item'><div class='legend-dot' style='background:#22c55e;'></div> Buffer</div><div class='legend-item'><div class='legend-dot' style='background:#ef4444;'></div> Deficit</div><div class='legend-item'><div style='width:18px;height:2px;border-top:2px dotted #78716c;'></div> In forza</div></div>""",unsafe_allow_html=True)

        with st.expander("📊 Gauge & Distribuzione"):
            eg1,eg2 = st.columns(2)
            with eg1:
                fig_g = go.Figure(go.Indicator(mode="gauge+number+delta",value=gap_pct_medio,title={'text':"Gap %",'font':{'size':13,'color':'#78716c'}},delta={'reference':0,'suffix':'%'},number={'suffix':'%','font':{'size':24,'color':'#92400e'}},gauge={'axis':{'range':[-20,20]},'bar':{'color':"#f59e0b"},'bgcolor':"#faf9f6",'borderwidth':1,'bordercolor':"#ede5d8",'steps':[{'range':[-20,-10],'color':'#fef2f2'},{'range':[-10,0],'color':'#fffbeb'},{'range':[0,10],'color':'#f0fdf4'},{'range':[10,20],'color':'#ecfdf5'}]}))
                fig_g.update_layout(height=250,paper_bgcolor='rgba(0,0,0,0)',margin=dict(l=20,r=20,t=30,b=20))
                st.plotly_chart(fig_g,use_container_width=True,key="pc2")
            with eg2:
                ab = pd.DataFrame({'T':['Infortuni','Malattie','L.104','Congedi','Permessi','Altro'],'V':[int(df_filtered[c].sum()) for c in ['infortuni','malattie','legge_104','congedo_parentale','permessi_vari','altre_assenze']]})
                ab = ab[ab['V']>0]
                if len(ab)>0:
                    fig_p = go.Figure(go.Pie(labels=ab['T'],values=ab['V'],hole=.5,marker=dict(colors=['#ef4444','#f97316','#eab308','#3b82f6','#22c55e','#94a3b8']),textinfo='label+percent'))
                    fig_p.update_layout(height=250,showlegend=False,paper_bgcolor='rgba(0,0,0,0)',margin=dict(l=0,r=0,t=0,b=0))
                    st.plotly_chart(fig_p,use_container_width=True,key="pc3")

        st.markdown("---")
        st.markdown("#### Heatmap Criticità")
        pv = df_filtered.pivot_table(values='gap',index='deposito',columns=df_filtered['giorno'].dt.strftime('%d/%m'),aggfunc='sum',fill_value=0)
        if len(pv)>0:
            fig_h = go.Figure(go.Heatmap(z=pv.values,x=pv.columns,y=pv.index,colorscale=[[0,'#991b1b'],[0.35,'#ef4444'],[0.45,'#fdba74'],[0.5,'#fefce8'],[0.55,'#bbf7d0'],[0.7,'#22c55e'],[1,'#166534']],zmid=0,text=pv.values,texttemplate='%{text:.0f}',textfont=dict(size=10,color="#334155"),colorbar=dict(title="Gap")))
            fig_h.update_layout(height=max(300,len(pv)*40),**PLOTLY_TEMPLATE)
            st.plotly_chart(fig_h,use_container_width=True,key="pc4")


# ───────── TAB 2 ─────────
with tab2:
    if len(df_filtered)==0: st.info("Nessun dato.")
    else:
        st2a,st2b,st2c = st.tabs(["📉 Gap & Waterfall","🏖️ Ferie & Riposi","🤒 Assenze Complete"])
        with st2a:
            st.markdown("#### Composizione Gap Medio")
            am = df_filtered.groupby("giorno")["totale_autisti"].sum().mean()
            asm_ = df_filtered.groupby("giorno")["assenze_previste"].sum().mean()
            tm = df_filtered.groupby("giorno")["turni_richiesti"].sum().mean()
            dm = am-asm_; gm = dm-tm
            fig_wf = go.Figure(go.Waterfall(orientation="v",measure=["absolute","relative","total","relative","total"],x=["Autisti","− Assenze","= Disponibili","− Turni","= Gap"],y=[am,-asm_,0,-tm,0],text=[f"{am:.0f}",f"−{asm_:.0f}",f"{dm:.0f}",f"−{tm:.0f}",f"{'+'if gm>=0 else ''}{gm:.0f}"],textposition="outside",textfont=dict(size=12,color="#1e293b"),connector={"line":{"color":"#ede5d8","width":1,"dash":"dot"}},increasing={"marker":{"color":"#22c55e"}},decreasing={"marker":{"color":"#ef4444"}},totals={"marker":{"color":"#3b82f6"}}))
            fig_wf.add_hline(y=0,line_dash="dash",line_color="#ede5d8")
            ac_ = "#22c55e" if gm>=0 else "#ef4444"
            at2 = f"✅ +{gm:.0f}" if gm>=0 else f"🚨 {gm:.0f}"
            fig_wf.add_annotation(x="= Gap",y=gm+(10 if gm>=0 else -10),text=f"<b>{at2}</b>",showarrow=True,arrowhead=2,arrowcolor=ac_,font=dict(size=11,color=ac_),bgcolor="#ffffff",bordercolor=ac_,borderwidth=1,borderpad=5)
            fig_wf.update_layout(height=440,showlegend=False,plot_bgcolor="#ffffff",paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#475569"),margin=dict(t=30,b=60,l=20,r=20),xaxis=dict(gridcolor="#f5f0e8",linecolor="#ede5d8"),yaxis=dict(title="Persone (media/gg)",gridcolor="#f5f0e8",linecolor="#ede5d8"))
            st.plotly_chart(fig_wf,use_container_width=True,key="pc5")
            w1,w2,w3 = st.columns(3)
            with w1: st.metric("👥 Autisti/gg",f"{am:.0f}")
            with w2: st.metric("🏥 Assenze/gg",f"{asm_:.0f}",delta=f"−{asm_/am*100:.1f}%" if am>0 else "",delta_color="inverse")
            with w3: st.metric("🚌 Turni/gg",f"{tm:.0f}",delta="✅" if gm>=0 else f"🚨 {gm:.0f}",delta_color="normal" if gm>=0 else "inverse")
            st.markdown("---")
            st.markdown("#### Trend Assenze")
            td = df_filtered.groupby("giorno").agg(infortuni=("infortuni","sum"),malattie=("malattie","sum"),legge_104=("legge_104","sum"),congedo_parentale=("congedo_parentale","sum"),permessi_vari=("permessi_vari","sum")).reset_index()
            fig_t = go.Figure()
            for c_,l_,cc_ in [("infortuni","Infortuni","#ef4444"),("malattie","Malattie","#f97316"),("legge_104","L.104","#eab308"),("congedo_parentale","Congedo","#3b82f6"),("permessi_vari","Permessi","#22c55e")]:
                fig_t.add_trace(go.Scatter(x=td["giorno"],y=td[c_],mode="lines+markers",name=l_,line=dict(color=cc_,width=2),marker=dict(size=4)))
            fig_t.update_layout(height=350,hovermode="x unified",legend=dict(orientation="h",y=-0.18,font=dict(size=10)),**PLOTLY_TEMPLATE)
            st.plotly_chart(fig_t,use_container_width=True,key="pc7")

        with st2b:
            try:
                d0=df_filtered["giorno"].min().date(); d1=df_filtered["giorno"].max().date()
                ds = ",".join([f"'{d}'" for d in deposito_sel])
                dfp = pd.read_sql(f"SELECT data AS giorno,deposito,COUNT(*) FILTER (WHERE turno='FP') AS ferie_programmate,COUNT(*) FILTER (WHERE turno='R') AS riposi FROM roster WHERE data BETWEEN '{d0}' AND '{d1}' AND deposito IN ({ds}) GROUP BY data,deposito ORDER BY data,deposito;",get_conn())
                dfp["giorno"] = pd.to_datetime(dfp["giorno"])
                fpd = dfp.groupby("giorno")[["ferie_programmate","riposi"]].sum().reset_index()
                k1,k2,k3 = st.columns(3)
                with k1: st.metric("🏖️ Tot. FP",f"{int(fpd['ferie_programmate'].sum()):,}")
                with k2: st.metric("📅 Media FP/gg",f"{fpd['ferie_programmate'].mean():.1f}")
                with k3: st.metric("📅 Media R/gg",f"{fpd['riposi'].mean():.1f}")
                vw = st.radio("Vista",["Per tipo","Per deposito"],horizontal=True,key="vfpr")
                if vw=="Per tipo":
                    fig_f = go.Figure()
                    fig_f.add_trace(go.Bar(x=fpd["giorno"],y=fpd["ferie_programmate"],name="FP",marker_color="#22c55e"))
                    fig_f.add_trace(go.Bar(x=fpd["giorno"],y=fpd["riposi"],name="R",marker_color="#3b82f6"))
                    fig_f.update_layout(barmode="stack",height=400,hovermode="x unified",legend=dict(orientation="h",y=1.02,x=1,xanchor="right"),**PLOTLY_TEMPLATE)
                    st.plotly_chart(fig_f,use_container_width=True,key="pc8")
                else:
                    tp = st.radio("Tipo",["FP","R"],horizontal=True,key="tdfp")
                    cs = "ferie_programmate" if tp=="FP" else "riposi"
                    fig_fd = go.Figure()
                    for dep in sorted(dfp["deposito"].unique()):
                        dd = dfp[dfp["deposito"]==dep]
                        fig_fd.add_trace(go.Bar(x=dd["giorno"],y=dd[cs],name=dep.title(),marker_color=get_colore_deposito(dep)))
                    fig_fd.update_layout(barmode="stack",height=400,hovermode="x unified",legend=dict(orientation="h",y=1.02,x=1,xanchor="right"),**PLOTLY_TEMPLATE)
                    st.plotly_chart(fig_fd,use_container_width=True,key="pc9")
            except Exception as e: st.warning(f"⚠️ {e}")

        with st2c:
            try:
                d0=df_filtered["giorno"].min().date(); d1=df_filtered["giorno"].max().date()
                ds = ",".join([f"'{d}'" for d in deposito_sel])
                dn = pd.read_sql(f"SELECT data AS giorno,deposito,COUNT(*) FILTER (WHERE turno='PS') AS ps,COUNT(*) FILTER (WHERE turno='AP') AS aspettativa,COUNT(*) FILTER (WHERE turno='PADm') AS congedo_straord,COUNT(*) FILTER (WHERE turno='NF') AS non_in_forza FROM roster WHERE data BETWEEN '{d0}' AND '{d1}' AND deposito IN ({ds}) GROUP BY data,deposito ORDER BY data,deposito;",get_conn())
                dn["giorno"] = pd.to_datetime(dn["giorno"])
                nd = dn.groupby("giorno")[["ps","aspettativa","congedo_straord","non_in_forza"]].sum().reset_index()
                sd = df_filtered.groupby("giorno").agg(infortuni=("infortuni","sum"),malattie=("malattie","sum"),legge_104=("legge_104","sum"),altre_assenze=("altre_assenze","sum"),congedo_parentale=("congedo_parentale","sum"),permessi_vari=("permessi_vari","sum")).reset_index()
                daf = sd.merge(nd,on="giorno",how="left").fillna(0)
                k1,k2,k3,k4,k5,k6 = st.columns(6)
                with k1: st.metric("🤕 Infortuni",f"{int(daf['infortuni'].sum()):,}")
                with k2: st.metric("🤒 Malattie",f"{int(daf['malattie'].sum()):,}")
                with k3: st.metric("♿ L.104",f"{int(daf['legge_104'].sum()):,}")
                with k4: st.metric("📋 PS",f"{int(daf['ps'].sum()):,}")
                with k5: st.metric("⏸️ AP",f"{int(daf['aspettativa'].sum()):,}")
                with k6: st.metric("🔴 NF",f"{int(daf['non_in_forza'].sum()):,}")
                ps_ = [("infortuni","Infortuni","#ef4444"),("malattie","Malattie","#f97316"),("legge_104","L.104","#eab308"),("altre_assenze","Altre","#a78bfa"),("congedo_parentale","Cong.par.","#3b82f6"),("permessi_vari","Permessi","#22c55e")]
                pn_ = [("ps","PS","#f43f5e"),("aspettativa","AP","#8b5cf6"),("congedo_straord","PADm","#0ea5e9"),("non_in_forza","NF","#94a3b8")]
                fig_a = go.Figure()
                for c_,l_,cc_ in ps_: fig_a.add_trace(go.Bar(x=daf["giorno"],y=daf[c_],name=l_,marker_color=cc_))
                for c_,l_,cc_ in pn_: fig_a.add_trace(go.Bar(x=daf["giorno"],y=daf[c_],name=l_,marker_color=cc_))
                fig_a.update_layout(barmode="stack",height=460,hovermode="x unified",legend=dict(orientation="h",y=1.02,x=1,xanchor="right",font=dict(size=10)),**PLOTLY_TEMPLATE)
                st.plotly_chart(fig_a,use_container_width=True,key="pc10")
                st.markdown("#### Tabella Assenze")
                dt_ = daf.copy(); dt_["giorno"] = dt_["giorno"].dt.strftime('%d/%m/%Y')
                dt_ = dt_.rename(columns={"giorno":"Data","infortuni":"Infortuni","malattie":"Malattie","legge_104":"L.104","altre_assenze":"Altre","congedo_parentale":"Cong.Par.","permessi_vari":"Permessi","ps":"PS","aspettativa":"AP","congedo_straord":"PADm","non_in_forza":"NF"})
                nc = ["Infortuni","Malattie","L.104","Altre","Cong.Par.","Permessi","PS","AP","PADm","NF"]
                dt_["Totale"] = dt_[nc].sum(axis=1)
                st.dataframe(dt_,use_container_width=True,hide_index=True,height=400)
                with st.expander("🔍 Dettaglio deposito"):
                    da = st.selectbox("Deposito",sorted(deposito_sel),key="da_d",format_func=lambda x: x.title())
                    dds = df_filtered[df_filtered["deposito"]==da].groupby("giorno").agg(infortuni=("infortuni","sum"),malattie=("malattie","sum"),legge_104=("legge_104","sum"),altre_assenze=("altre_assenze","sum"),congedo_parentale=("congedo_parentale","sum"),permessi_vari=("permessi_vari","sum")).reset_index()
                    ddn = dn[dn["deposito"]==da].copy()
                    ddf = dds.merge(ddn[["giorno","ps","aspettativa","congedo_straord","non_in_forza"]],on="giorno",how="left").fillna(0)
                    fig_da = go.Figure()
                    for c_,l_,cc_ in ps_+pn_: fig_da.add_trace(go.Bar(x=ddf["giorno"],y=ddf[c_],name=l_,marker_color=cc_))
                    fig_da.update_layout(barmode="stack",height=370,hovermode="x unified",title=f"Assenze — {da.title()}",legend=dict(orientation="h",y=1.02,x=1,xanchor="right",font=dict(size=10)),**PLOTLY_TEMPLATE)
                    st.plotly_chart(fig_da,use_container_width=True,key="pc11")
            except Exception as e: st.warning(f"⚠️ {e}")


# ───────── TAB 3 ─────────
with tab3:
    st.markdown("### Turni per Deposito")
    if not turni_cal_ok or len(df_tc_filtered)==0: st.warning("Nessun record.")
    else:
        tc1,tc2,tc3 = st.columns([1,1,2])
        with tc1: bm = "stack" if st.radio("Barre",["Impilate","Affiancate"],horizontal=True)=="Impilate" else "group"
        with tc2: st_tot = st.checkbox("Linea totale",value=True)
        with tc3: dep_tc = st.multiselect("Depositi",sorted(df_tc_filtered["deposito"].unique()),default=sorted(df_tc_filtered["deposito"].unique()),key="dtcf")
        dtp = df_tc_filtered[df_tc_filtered["deposito"].isin(dep_tc)].copy()
        if len(dtp)>0:
            dta = dtp.groupby(["giorno","deposito"])["turni"].sum().reset_index().sort_values(["giorno","deposito"])
            fig_tc = go.Figure()
            for dep in sorted(dta["deposito"].unique()):
                dd = dta[dta["deposito"]==dep]
                fig_tc.add_trace(go.Bar(x=dd["giorno"],y=dd["turni"],name=dep.title(),marker_color=get_colore_deposito(dep)))
            if st_tot:
                tg = dta.groupby("giorno")["turni"].sum().reset_index()
                fig_tc.add_trace(go.Scatter(x=tg["giorno"],y=tg["turni"],name="Totale",mode="lines+markers",line=dict(color="#1e293b",width=2,dash="dot"),marker=dict(size=5,symbol="diamond")))
            fig_tc.update_layout(barmode=bm,height=480,hovermode="x unified",legend=dict(orientation="h",y=1.02,x=1,xanchor="right",font=dict(size=10)),**PLOTLY_TEMPLATE)
            st.plotly_chart(fig_tc,use_container_width=True,key="pc13")

            st.markdown("---")
            st.markdown("#### Codici Turno")
            try:
                dc = pd.read_sql("SELECT deposito,codice_turno,valid,dal,al FROM turni ORDER BY deposito,valid,codice_turno;",get_conn())
                dc["dal"] = pd.to_datetime(dc["dal"]).dt.strftime("%d/%m/%Y"); dc["al"] = pd.to_datetime(dc["al"]).dt.strftime("%d/%m/%Y")
                de_ = st.selectbox("📍 Deposito",sorted(dc["deposito"].unique()),format_func=lambda x: x.title(),key="de")
                tv_ = sorted(dc[dc["deposito"]==de_]["valid"].unique())
                ts_ = st.radio("Tipo giorno",["Tutti"]+tv_,horizontal=True,key="te")
                ddc = dc[dc["deposito"]==de_].copy()
                if ts_!="Tutti": ddc = ddc[ddc["valid"]==ts_]
                k1,k2,k3 = st.columns(3)
                with k1: st.metric("🔢 Codici",len(ddc))
                with k2: st.metric("📋 Tipi",ddc["valid"].nunique())
                with k3: st.metric("📅 Validità",f"{ddc['dal'].iloc[0]} → {ddc['al'].iloc[0]}" if len(ddc)>0 else "—")
                if len(ddc)>0:
                    cd_ = get_colore_deposito(de_)
                    for tipo in sorted(ddc["valid"].unique()):
                        dt2 = ddc[ddc["valid"]==tipo]
                        lb = {"Lu-Ve":"Lunedì — Venerdì","Sa":"Sabato","Do":"Domenica"}.get(tipo,tipo)
                        st.markdown(f"<p style='color:#92400e !important;font-weight:600;font-size:0.9rem;margin:12px 0 6px;'>"
                            f"{lb} <span style='color:#a8a29e !important;font-size:0.76rem;font-weight:400;'>"
                            f"({len(dt2)} turni · {dt2['dal'].iloc[0]} → {dt2['al'].iloc[0]})</span></p>",unsafe_allow_html=True)
                        codici = dt2["codice_turno"].tolist()
                        for i in range(0,len(codici),8):
                            cols = st.columns(8)
                            for j,cod in enumerate(codici[i:i+8]):
                                with cols[j]:
                                    st.markdown(
                                        f"<div style='"
                                        f"background-color:#ffffff !important;"
                                        f"border:1px solid {cd_}55;"
                                        f"border-left:3px solid {cd_};"
                                        f"border-radius:6px;"
                                        f"padding:7px 4px;"
                                        f"text-align:center;"
                                        f"font-size:0.82rem;"
                                        f"font-weight:700;"
                                        f"color:#1e293b !important;"
                                        f"margin-bottom:4px;"
                                        f"box-shadow:0 1px 3px rgba(0,0,0,0.06);"
                                        f"'>"
                                        f"<span style='color:#1e293b !important;'>{cod}</span>"
                                        f"</div>",unsafe_allow_html=True)
            except Exception as e: st.warning(f"⚠️ {e}")

            st.markdown("---")
            st.markdown("#### Distribuzione Turni")
            tpd = dta.groupby("deposito")["turni"].sum().reset_index()
            fig_pt = go.Figure(go.Pie(labels=[d.title() for d in tpd["deposito"]],values=tpd["turni"],marker=dict(colors=[get_colore_deposito(d) for d in tpd["deposito"]]),hole=0.45,textinfo="label+percent+value",textfont=dict(size=11)))
            fig_pt.update_layout(height=380,showlegend=True,paper_bgcolor="rgba(0,0,0,0)",legend=dict(font=dict(size=10)),margin=dict(l=20,r=20,t=20,b=20))
            st.plotly_chart(fig_pt,use_container_width=True,key="pc14")

            st.markdown("---")
            st.markdown("#### Turni per Tipo Giorno")
            try:
                dl_ = dtp["giorno"].dt.date.unique().tolist()
                dstr_ = ",".join([f"'{d}'" for d in dl_])
                dcm_ = pd.read_sql(f"SELECT data,daytype FROM calendar WHERE data IN ({dstr_});",get_conn())
                dcm_["data"] = pd.to_datetime(dcm_["data"])
                def dtc_(dt):
                    dt = (dt or "").strip().lower()
                    if dt in ["lunedi","martedi","mercoledi","giovedi","venerdi"]: return "Lu-Ve"
                    elif dt=="sabato": return "Sabato"
                    elif dt=="domenica": return "Domenica"
                    return dt.title()
                dtdt_ = dtp.merge(dcm_,left_on="giorno",right_on="data",how="left")
                dtdt_["cat"] = dtdt_["daytype"].apply(dtc_)
                co_ = ["Lu-Ve","Sabato","Domenica"]
                pg_ = dtdt_.groupby("cat")["giorno"].min().to_dict()
                al2 = [dtdt_[dtdt_["giorno"]==gg][["deposito","turni","cat"]] for _,gg in pg_.items()]
                adt_ = pd.concat(al2,ignore_index=True) if al2 else pd.DataFrame()
                if len(adt_)>0:
                    adt_["cat"] = pd.Categorical(adt_["cat"],categories=co_,ordered=True)
                    tc2_ = adt_.groupby("cat")["turni"].sum().reindex(co_,fill_value=0)
                    fig_dt = go.Figure()
                    for dep in sorted(adt_["deposito"].unique()):
                        dd = adt_[adt_["deposito"]==dep]
                        vs = [dd[dd["cat"]==c]["turni"].sum() if c in dd["cat"].values else 0 for c in co_]
                        fig_dt.add_trace(go.Bar(x=co_,y=vs,name=dep.title(),marker_color=get_colore_deposito(dep),text=[f"{v:,}" if v>0 else "" for v in vs],textposition="inside",textfont=dict(size=10,color="white")))
                    fig_dt.update_layout(barmode="stack",height=420,hovermode="x unified",legend=dict(orientation="h",y=1.02,x=1,xanchor="right",font=dict(size=10)),annotations=[dict(x=c,y=tc2_[c],text=f"<b>{int(tc2_[c]):,}</b>",xanchor="center",yanchor="bottom",showarrow=False,font=dict(size=12,color="#1e293b"),yshift=5) for c in co_ if tc2_[c]>0],**PLOTLY_TEMPLATE)
                    st.plotly_chart(fig_dt,use_container_width=True,key="pc15")
                    k1,k2,k3 = st.columns(3)
                    with k1: st.metric("📅 Lu-Ve",f"{int(tc2_.get('Lu-Ve',0)):,}")
                    with k2: st.metric("📅 Sabato",f"{int(tc2_.get('Sabato',0)):,}")
                    with k3: st.metric("📅 Domenica",f"{int(tc2_.get('Domenica',0)):,}")
            except Exception as e: st.warning(f"⚠️ {e}")


# ───────── TAB 4 ─────────
with tab4:
    if len(df_filtered)>0 and len(by_deposito)>0:
        st.markdown("#### Ranking Depositi per Gap Medio")
        cd2 = ['#ef4444' if g<soglia_gap else '#f97316' if g<0 else '#22c55e' for g in by_deposito["media_gap_giorno"]]
        fig_d = go.Figure(go.Bar(y=by_deposito["deposito"],x=by_deposito["media_gap_giorno"],orientation='h',marker=dict(color=cd2),text=by_deposito["media_gap_giorno"],texttemplate='%{text:.1f}',textposition='outside',textfont=dict(size=11,color="#1e293b")))
        fig_d.add_vline(x=0,line_width=2,line_color="#94a3b8")
        fig_d.update_layout(height=max(360,len(by_deposito)*35),showlegend=False,**PLOTLY_TEMPLATE)
        st.plotly_chart(fig_d,use_container_width=True,key="pc16")
        st.markdown("---")
        st.markdown("#### Tabella Dettagliata")
        st.dataframe(by_deposito[["deposito","dipendenti_medi_giorno","giorni_periodo","disponibili_netti","assenze_previste","media_gap_giorno","tasso_copertura_%"]].rename(columns={"deposito":"Deposito","dipendenti_medi_giorno":"Autisti medi","giorni_periodo":"Giorni","disponibili_netti":"Disponibili","assenze_previste":"Assenze","media_gap_giorno":"Gap/Giorno","tasso_copertura_%":"Copertura %"}),use_container_width=True,hide_index=True)


# ───────── TAB 5 ─────────
with tab5:
    st.markdown("#### Export Dati")
    c1,c2 = st.columns(2)
    dex = df_filtered.copy(); dex["giorno"] = dex["giorno"].dt.strftime('%d/%m/%Y')
    with c1:
        st.markdown("##### CSV")
        st.download_button("⬇️ Scarica CSV",data=dex.to_csv(index=False).encode('utf-8'),file_name=f"estate2026_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv")
        st.info(f"📦 {len(dex):,} righe")
    with c2:
        st.markdown("##### Excel")
        o = BytesIO()
        with pd.ExcelWriter(o,engine='xlsxwriter') as w:
            dex.to_excel(w,sheet_name='Staffing',index=False)
            if len(by_deposito)>0: by_deposito.to_excel(w,sheet_name='Depositi',index=False)
            if turni_cal_ok and len(df_tc_filtered)>0:
                te = df_tc_filtered.copy(); te["giorno"] = te["giorno"].dt.strftime('%d/%m/%Y')
                te.to_excel(w,sheet_name='Turni',index=False)
        st.download_button("⬇️ Scarica Excel",data=o.getvalue(),file_name=f"estate2026_report_{datetime.now().strftime('%Y%m%d')}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.success("✅ Staffing · Depositi · Turni")
    st.markdown("---")
    st.dataframe(dex.head(100),use_container_width=True,height=400)


# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
yr = datetime.now().year
st.markdown(f"""
<div style='text-align:center;padding:18px 0 10px;'>
    <p style='font-size:0.8rem;font-weight:700;color:#92400e !important;letter-spacing:1px;'>
        ESTATE 2026 · ANALYTICS DASHBOARD</p>
    <p style='font-size:0.7rem;color:#a8a29e !important;margin-top:4px;'>
        Streamlit · Plotly · PostgreSQL · {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
    <p style='font-size:0.65rem;color:#a8a29e !important;margin-top:8px;'>
        Progettato e sviluppato da <b style='color:#78350f !important;'>Samuele Felici</b> · © {yr} — Tutti i diritti riservati</p>
</div>
""", unsafe_allow_html=True)
