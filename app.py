"""
===============================================
ESTATE 2026 - DASHBOARD ANALYTICS PREMIUM
Versione User-Friendly — Redesign UX
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
    page_title="Estate 2026 – Pianificazione Turni",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚍"
)

# --------------------------------------------------
# PALETTE COLORI — Warm Professional
# Più leggibile, accessibile, caldi e rassicuranti
# --------------------------------------------------
PALETTE = {
    "bg_deep":     "#0d1117",
    "bg_card":     "rgba(22, 30, 46, 0.92)",
    "bg_glass":    "rgba(30, 40, 62, 0.75)",
    "accent":      "#F5A623",   # arancio ambrato — principale
    "accent2":     "#4FC3F7",   # azzurro cielo — secondario
    "accent3":     "#81C784",   # verde morbido — positivo
    "danger":      "#EF5350",   # rosso caldo — critico
    "warning":     "#FFB74D",   # arancio — attenzione
    "success":     "#66BB6A",   # verde — ok
    "text_main":   "#ECF0F1",
    "text_sub":    "#B0BEC5",
    "text_muted":  "#78909C",
    "border":      "rgba(245, 166, 35, 0.25)",
    "border_soft": "rgba(79, 195, 247, 0.15)",
}

COLORI_DEPOSITI = {
    "ancona":                   "#F5A623",
    "polverigi":                "#EF5350",
    "marina":                   "#EC407A",
    "marina di montemarciano":  "#EC407A",
    "filottrano":               "#66BB6A",
    "jesi":                     "#42A5F5",
    "osimo":                    "#AB47BC",
    "castelfidardo":            "#26C6DA",
    "castelfdardo":             "#26C6DA",
    "ostra":                    "#FF7043",
    "belvedere ostrense":       "#78909C",
    "belvedereostrense":        "#78909C",
    "depbelvede":               "#78909C",
    "moie":                     "#9CCC65",
}

def get_colore_deposito(dep: str) -> str:
    return COLORI_DEPOSITI.get(str(dep).strip().lower(), "#78909C")

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

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
    [data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="stHeader"]  {{ display: none !important; }}
    footer {{ display: none !important; }}
    .block-container {{ padding-top: 0 !important; max-width: 100% !important; }}
    * {{ font-family: 'Outfit', sans-serif !important; }}
    .stApp {{ background: {PALETTE['bg_deep']} !important; }}

    @keyframes gridPulse {{ 0%, 100% {{ opacity: 0.05; }} 50% {{ opacity: 0.12; }} }}
    @keyframes nebula {{
        0%, 100% {{ transform: translate(-50%, -50%) scale(1);   opacity: 0.45; }}
        50%       {{ transform: translate(-50%, -50%) scale(1.1); opacity: 0.65; }}
    }}
    @keyframes rise {{
        0%   {{ transform: translateY(0) translateX(0);    opacity: 0; }}
        10%  {{ opacity: 0.7; }}
        90%  {{ opacity: 0.4; }}
        100% {{ transform: translateY(-100vh) translateX(20px); opacity: 0; }}
    }}
    @keyframes twinkle {{ 0%, 100% {{ opacity: 0.15; }} 50% {{ opacity: 0.9; }} }}
    @keyframes shimmer {{
        0%   {{ background-position: -200% center; }}
        100% {{ background-position:  200% center; }}
    }}

    .ca-bg-grid {{
        position: fixed; inset: 0; z-index: 0; pointer-events: none;
        background-image:
            linear-gradient(rgba(245,166,35,0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(245,166,35,0.04) 1px, transparent 1px);
        background-size: 56px 56px;
        animation: gridPulse 6s ease-in-out infinite;
    }}
    .ca-bg-nebula {{
        position: fixed; top: 50%; left: 50%;
        width: 900px; height: 700px;
        background: radial-gradient(ellipse,
            rgba(245,166,35,0.10) 0%, rgba(13,17,23,0.5) 45%, transparent 70%);
        animation: nebula 9s ease-in-out infinite;
        pointer-events: none; z-index: 0;
    }}
    .ca-particle {{ position: fixed; border-radius: 50%; animation: rise linear infinite; pointer-events: none; z-index: 0; }}
    .ca-star {{ position: fixed; width: 2px; height: 2px; background: {PALETTE['accent']}; border-radius: 50%; animation: twinkle ease-in-out infinite; pointer-events: none; z-index: 0; }}

    div[data-testid="stTextInput"] > div > div {{
        background: rgba(13, 17, 23, 0.95) !important;
        border: 1.5px solid {PALETTE['border']} !important;
        border-radius: 12px !important;
    }}
    div[data-testid="stTextInput"] > div > div:focus-within {{
        border-color: {PALETTE['accent']} !important;
        box-shadow: 0 0 0 4px rgba(245,166,35,0.12) !important;
    }}
    div[data-testid="stTextInput"] input {{
        color: {PALETTE['text_main']} !important;
        font-size: 1rem !important;
        letter-spacing: 3px !important;
    }}
    div[data-testid="stTextInput"] label {{ display: none !important; }}

    .login-title {{
        text-align: center;
        font-size: 2rem;
        font-weight: 800;
        color: {PALETTE['accent']};
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 6px;
        background: linear-gradient(90deg, {PALETTE['accent']}, {PALETTE['accent2']}, {PALETTE['accent']});
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s linear infinite;
    }}
    .login-sub {{
        text-align: center;
        font-size: 0.85rem;
        color: {PALETTE['text_muted']};
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 28px;
    }}

    .ca-security {{
        position: fixed; bottom: 0; left: 0; right: 0;
        padding: 9px 20px;
        background: rgba(13,17,23,0.95);
        border-top: 1px solid {PALETTE['border']};
        backdrop-filter: blur(8px);
        z-index: 9999;
    }}
    .ca-security-row {{ display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap; }}
    .ca-security-item {{
        color: {PALETTE['text_sub']}; font-size: 0.70rem; letter-spacing: 2px;
        text-transform: uppercase; display: flex; align-items: center; gap: 8px;
    }}
    .ca-sep {{ color: {PALETTE['border']}; font-size: 1rem; }}
    </style>
    <div class="ca-bg-grid"></div>
    <div class="ca-bg-nebula"></div>
    <div class="ca-star" style="top:8%;left:15%;animation-duration:3s;animation-delay:0s;"></div>
    <div class="ca-star" style="top:22%;left:78%;animation-duration:4s;animation-delay:1s;"></div>
    <div class="ca-star" style="top:55%;left:92%;animation-duration:2.5s;animation-delay:0.5s;"></div>
    <div class="ca-star" style="top:72%;left:5%;animation-duration:5s;animation-delay:2s;"></div>
    <div class="ca-star" style="top:88%;left:45%;animation-duration:3.5s;animation-delay:1.5s;"></div>
    <div class="ca-star" style="top:35%;left:32%;animation-duration:4.5s;animation-delay:0.8s;"></div>
    <div class="ca-particle" style="width:3px;height:3px;background:{PALETTE['accent']};left:10%;bottom:0;animation-duration:9s;animation-delay:0s;"></div>
    <div class="ca-particle" style="width:2px;height:2px;background:{PALETTE['accent2']};left:25%;bottom:0;animation-duration:12s;animation-delay:2s;"></div>
    <div class="ca-particle" style="width:4px;height:4px;background:{PALETTE['danger']};left:40%;bottom:0;animation-duration:8s;animation-delay:1s;"></div>
    <div class="ca-particle" style="width:2px;height:2px;background:{PALETTE['success']};left:55%;bottom:0;animation-duration:11s;animation-delay:3s;"></div>
    <div class="ca-particle" style="width:3px;height:3px;background:{PALETTE['accent']};left:70%;bottom:0;animation-duration:10s;animation-delay:0.5s;"></div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<div style='height:16vh'></div>", unsafe_allow_html=True)
        st.markdown("<p class='login-title'>🚍 Estate 2026</p>", unsafe_allow_html=True)
        st.markdown("<p class='login-sub'>Pianificazione & Analisi Turni</p>", unsafe_allow_html=True)

        def _entered():
            if st.session_state["_pwd"] == st.secrets["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
            else:
                st.session_state["password_correct"] = False

        st.text_input(
            "Password", type="password", on_change=_entered, key="_pwd",
            placeholder="🔒  Inserisci la password di accesso", label_visibility="collapsed"
        )

        if st.session_state.get("password_correct") is False:
            st.error("❌ Password non corretta. Riprova.")

        if logo_b64:
            st.markdown(
                f"<div style='text-align:center; margin-top:28px;'>"
                f"<img src='data:image/png;base64,{logo_b64}' "
                f"style='height:380px; width:auto; opacity:0.9; filter: drop-shadow(0 0 24px rgba(245,166,35,0.4));'/>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown(f"""
    <div class='ca-security'>
        <div class='ca-security-row'>
            <span class='ca-security-item'>🔒 Connessione cifrata</span>
            <span class='ca-sep'>·</span>
            <span class='ca-security-item'>🛡️ Sistema protetto</span>
            <span class='ca-sep'>·</span>
            <span class='ca-security-item'>⏰ Accesso riservato · Estate 2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    return False


if not check_password():
    st.stop()


# --------------------------------------------------
# SPLASH SCREEN (mantenuto con nuova palette)
# --------------------------------------------------
if not st.session_state.get("splash_done"):
    st.session_state["splash_done"] = True
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
[data-testid="stSidebar"]{{display:none!important}}
[data-testid="stHeader"]{{display:none!important}}
footer{{display:none!important}}
.block-container{{padding:0!important;max-width:100%!important}}
.stApp{{background:{PALETTE['bg_deep']}!important;overflow:hidden}}
* {{ font-family: 'Outfit', sans-serif !important; }}
@keyframes corePulse{{
  0%,100%{{transform:translate(-50%,-50%) scale(1);box-shadow:0 0 30px 8px rgba(245,166,35,0.7),0 0 80px 30px rgba(245,166,35,0.2)}}
  50%{{transform:translate(-50%,-50%) scale(1.15);box-shadow:0 0 55px 18px rgba(245,166,35,0.9),0 0 130px 55px rgba(245,166,35,0.35)}}}}
@keyframes spin1{{from{{transform:translate(-50%,-50%) rotate(0deg)}}to{{transform:translate(-50%,-50%) rotate(360deg)}}}}
@keyframes spin2{{from{{transform:translate(-50%,-50%) rotate(0deg)}}to{{transform:translate(-50%,-50%) rotate(-360deg)}}}}
@keyframes spin3{{from{{transform:translate(-50%,-50%) rotate(45deg)}}to{{transform:translate(-50%,-50%) rotate(405deg)}}}}
@keyframes orb1{{from{{transform:rotate(0deg) translateX(105px) rotate(0deg)}}to{{transform:rotate(360deg) translateX(105px) rotate(-360deg)}}}}
@keyframes orb2{{from{{transform:rotate(120deg) translateX(160px) rotate(-120deg)}}to{{transform:rotate(480deg) translateX(160px) rotate(-480deg)}}}}
@keyframes orb3{{from{{transform:rotate(240deg) translateX(215px) rotate(-240deg)}}to{{transform:rotate(600deg) translateX(215px) rotate(-600deg)}}}}
@keyframes orb4{{from{{transform:rotate(60deg) translateX(260px) rotate(-60deg)}}to{{transform:rotate(420deg) translateX(260px) rotate(-420deg)}}}}
@keyframes orb5{{from{{transform:rotate(180deg) translateX(105px) rotate(-180deg)}}to{{transform:rotate(540deg) translateX(105px) rotate(-540deg)}}}}
@keyframes blobFloat{{0%,100%{{transform:translate(-50%,-50%) scale(1) rotate(0deg);opacity:0.4}}50%{{transform:translate(-50%,-50%) scale(1.2) rotate(120deg);opacity:0.7}}}}
@keyframes fadeOutSplash{{0%,70%{{opacity:1}}95%{{opacity:0;visibility:visible}}100%{{opacity:0;visibility:hidden}}}}
@keyframes progressFill{{from{{width:0%}}to{{width:100%}}}}
@keyframes textPulse{{0%,100%{{opacity:0.3;letter-spacing:4px}}50%{{opacity:1;letter-spacing:6px}}}}
@keyframes gridPulse2{{0%,100%{{opacity:0.03}}50%{{opacity:0.08}}}}
@keyframes starTwinkle{{0%,100%{{opacity:0.1}}50%{{opacity:0.8}}}}
.sp-wrap{{position:fixed;inset:0;z-index:99999;background:{PALETTE['bg_deep']};display:flex;flex-direction:column;align-items:center;justify-content:center;animation:fadeOutSplash 3.6s ease forwards}}
.sp-wrap::before{{content:'';position:absolute;inset:0;
    background-image:linear-gradient(rgba(245,166,35,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(245,166,35,0.04) 1px,transparent 1px);
    background-size:56px 56px;animation:gridPulse2 4s ease-in-out infinite}}
.sp-star{{position:absolute;width:2px;height:2px;background:{PALETTE['accent']};border-radius:50%;animation:starTwinkle ease-in-out infinite}}
.sp-arena{{position:relative;width:580px;height:580px;flex-shrink:0}}
.sp-ring{{position:absolute;top:50%;left:50%;border-radius:50%}}
.sp-ring-1{{width:520px;height:520px;margin:-260px 0 0 -260px;border:1.5px solid transparent;border-top:1.5px solid rgba(245,166,35,0.8);border-right:1.5px solid rgba(245,166,35,0.2);animation:spin1 3s linear infinite}}
.sp-ring-2{{width:410px;height:410px;margin:-205px 0 0 -205px;border:1px solid transparent;border-top:1px solid rgba(79,195,247,0.6);border-left:1px solid rgba(79,195,247,0.3);animation:spin2 2s linear infinite}}
.sp-ring-3{{width:310px;height:310px;margin:-155px 0 0 -155px;border:2px solid transparent;border-bottom:2px solid rgba(245,166,35,0.5);border-right:2px solid rgba(79,195,247,0.4);animation:spin3 4s linear infinite}}
.sp-ring-4{{width:220px;height:220px;margin:-110px 0 0 -110px;border:1px solid transparent;border-top:1px solid rgba(129,199,132,0.5);animation:spin1 1.5s linear infinite reverse}}
.sp-blob{{position:absolute;top:50%;left:50%;border-radius:50%;pointer-events:none}}
.sp-blob-1{{width:380px;height:220px;margin:-110px 0 0 -190px;background:radial-gradient(ellipse,rgba(245,166,35,0.15) 0%,transparent 70%);animation:blobFloat 5s ease-in-out infinite}}
.sp-core{{position:absolute;top:50%;left:50%;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;background:radial-gradient(circle,#ffffff 0%,#FFE082 35%,{PALETTE['accent']} 70%,#E65100 100%);animation:corePulse 2s ease-in-out infinite;z-index:20}}
.sp-orb{{position:absolute;top:50%;left:50%;border-radius:50%}}
.sp-orb-1{{width:10px;height:10px;margin:-5px 0 0 -5px;background:{PALETTE['accent']};box-shadow:0 0 12px 4px rgba(245,166,35,0.9);animation:orb1 2.2s linear infinite}}
.sp-orb-2{{width:8px;height:8px;margin:-4px 0 0 -4px;background:{PALETTE['danger']};box-shadow:0 0 10px 3px rgba(239,83,80,0.9);animation:orb2 3.3s linear infinite}}
.sp-orb-3{{width:7px;height:7px;margin:-3.5px 0 0 -3.5px;background:{PALETTE['success']};box-shadow:0 0 10px 3px rgba(102,187,106,0.9);animation:orb3 4.4s linear infinite}}
.sp-orb-4{{width:6px;height:6px;margin:-3px 0 0 -3px;background:{PALETTE['accent2']};box-shadow:0 0 8px 3px rgba(79,195,247,0.9);animation:orb4 5.5s linear infinite}}
.sp-orb-5{{width:9px;height:9px;margin:-4.5px 0 0 -4.5px;background:#CE93D8;box-shadow:0 0 10px 3px rgba(206,147,216,0.9);animation:orb5 1.8s linear infinite}}
.sp-text{{margin-top:-30px;text-align:center;z-index:10}}
.sp-title{{color:{PALETTE['accent']};font-size:1.6rem;font-weight:800;letter-spacing:4px;text-transform:uppercase;margin:0 0 4px;}}
.sp-label{{color:{PALETTE['text_muted']};font-size:0.68rem;letter-spacing:3px;text-transform:uppercase;margin:0 0 16px;animation:textPulse 2s ease-in-out infinite}}
.sp-bar-wrap{{width:220px;height:3px;background:rgba(245,166,35,0.1);border-radius:3px;margin:0 auto;overflow:hidden}}
.sp-bar{{height:100%;background:linear-gradient(90deg,#E65100,{PALETTE['accent']},#FFE082,{PALETTE['accent']},#E65100);background-size:200% 100%;animation:progressFill 3.2s cubic-bezier(.4,0,.2,1) forwards;box-shadow:0 0 10px rgba(245,166,35,0.8)}}
</style>
<div class="sp-wrap">
  <div class="sp-star" style="top:7%;left:12%;animation-duration:2.8s;animation-delay:0s"></div>
  <div class="sp-star" style="top:18%;left:81%;animation-duration:4s;animation-delay:.8s"></div>
  <div class="sp-star" style="top:72%;left:91%;animation-duration:3.2s;animation-delay:.3s"></div>
  <div class="sp-star" style="top:85%;left:7%;animation-duration:5s;animation-delay:1.5s"></div>
  <div class="sp-arena">
    <div class="sp-blob sp-blob-1"></div>
    <div class="sp-ring sp-ring-1"></div>
    <div class="sp-ring sp-ring-2"></div>
    <div class="sp-ring sp-ring-3"></div>
    <div class="sp-ring sp-ring-4"></div>
    <div class="sp-orb sp-orb-1"></div>
    <div class="sp-orb sp-orb-2"></div>
    <div class="sp-orb sp-orb-3"></div>
    <div class="sp-orb sp-orb-4"></div>
    <div class="sp-orb sp-orb-5"></div>
    <div class="sp-core"></div>
  </div>
  <div class="sp-text">
    <p class="sp-title">🚍 Estate 2026</p>
    <p class="sp-label">Caricamento in corso…</p>
    <div class="sp-bar-wrap"><div class="sp-bar"></div></div>
  </div>
</div>
""", unsafe_allow_html=True)
    # Splash fades out via CSS animation (no sleep/rerun needed)


# --------------------------------------------------
# CSS DASHBOARD — User-Friendly Warm Theme
# --------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
""", unsafe_allow_html=True)

st.markdown(f"""<style>

/* ─── RESET E BASE ─── */
*, body, .stApp {{ font-family: 'Outfit', sans-serif !important; }}
.stApp {{
    background: linear-gradient(145deg, #0d1117 0%, #13192b 50%, #0d1117 100%);
    background-attachment: fixed;
}}

/* ─── TITOLI ─── */
h1 {{ color: {PALETTE['accent']} !important; font-weight: 800 !important; letter-spacing: 1px; font-size: 2.6rem !important; }}
h2 {{ color: {PALETTE['text_main']} !important; font-weight: 700 !important; margin-top: 24px !important; font-size: 1.4rem !important; }}
h3 {{ color: {PALETTE['text_sub']} !important; font-weight: 600 !important; font-size: 1.1rem !important; }}
p, span, label {{ color: {PALETTE['text_sub']} !important; }}

/* ─── KPI CARDS ─── */
[data-testid="metric-container"] {{
    background: {PALETTE['bg_card']};
    padding: 22px 20px;
    border-radius: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    border: 1px solid {PALETTE['border_soft']};
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}}
[data-testid="metric-container"]::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {PALETTE['accent']}, {PALETTE['accent2']});
    opacity: 0;
    transition: opacity 0.25s;
}}
[data-testid="metric-container"]:hover::before {{ opacity: 1; }}
[data-testid="metric-container"]:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(245,166,35,0.15);
    border-color: {PALETTE['border']};
}}
[data-testid="stMetricValue"] {{
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    color: {PALETTE['accent']} !important;
    line-height: 1.1 !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: {PALETTE['text_sub']} !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}
[data-testid="stMetricDelta"] {{
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}}

/* ─── TABS ─── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background: rgba(13,17,23,0.6);
    padding: 8px;
    border-radius: 12px;
    border: 1px solid {PALETTE['border_soft']};
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    border-radius: 8px;
    color: {PALETTE['text_sub']} !important;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 10px 20px;
    border: 1px solid transparent;
    transition: all 0.2s;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: rgba(245,166,35,0.08);
    border-color: {PALETTE['border']};
    color: {PALETTE['accent']} !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, rgba(245,166,35,0.2) 0%, rgba(245,166,35,0.1) 100%) !important;
    color: {PALETTE['accent']} !important;
    border-color: {PALETTE['border']} !important;
}}

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0d1117 0%, #13192b 100%);
    border-right: 1px solid {PALETTE['border']};
}}
[data-testid="stSidebar"] * {{ color: {PALETTE['text_main']} !important; }}

/* ─── ALERT / BANNER ─── */
.alert-critical {{
    background: linear-gradient(135deg, rgba(239,83,80,0.15) 0%, rgba(239,83,80,0.05) 100%);
    padding: 16px 20px; border-radius: 12px; color: #FFCDD2;
    font-size: 0.95rem; margin: 16px 0;
    border: 1px solid rgba(239,83,80,0.3); border-left: 4px solid {PALETTE['danger']};
}}
.alert-warning {{
    background: linear-gradient(135deg, rgba(255,183,77,0.15) 0%, rgba(255,183,77,0.05) 100%);
    padding: 16px 20px; border-radius: 12px; color: #FFE0B2;
    font-size: 0.95rem; margin: 16px 0;
    border: 1px solid rgba(255,183,77,0.3); border-left: 4px solid {PALETTE['warning']};
}}
.alert-success {{
    background: linear-gradient(135deg, rgba(102,187,106,0.15) 0%, rgba(102,187,106,0.05) 100%);
    padding: 16px 20px; border-radius: 12px; color: #C8E6C9;
    font-size: 0.95rem; margin: 16px 0;
    border: 1px solid rgba(102,187,106,0.3); border-left: 4px solid {PALETTE['success']};
}}
.alert-info {{
    background: linear-gradient(135deg, rgba(79,195,247,0.12) 0%, rgba(79,195,247,0.04) 100%);
    padding: 16px 20px; border-radius: 12px; color: #B3E5FC;
    font-size: 0.95rem; margin: 16px 0;
    border: 1px solid rgba(79,195,247,0.25); border-left: 4px solid {PALETTE['accent2']};
}}

/* ─── GRAFICI ─── */
.js-plotly-plot {{
    border-radius: 16px;
    border: 1px solid {PALETTE['border_soft']};
}}

/* ─── DATAFRAME ─── */
[data-testid="stDataFrame"] {{
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid {PALETTE['border_soft']};
}}

/* ─── EXPANDER ─── */
[data-testid="stExpander"] {{
    background: {PALETTE['bg_card']};
    border: 1px solid {PALETTE['border_soft']};
    border-radius: 12px;
}}

/* ─── BOTTONI ─── */
button {{
    background: linear-gradient(135deg, {PALETTE['accent']} 0%, #E65100 100%) !important;
    color: #0d1117 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}}
button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(245,166,35,0.35) !important;
}}
.stDownloadButton button {{
    background: linear-gradient(135deg, {PALETTE['success']} 0%, #2E7D32 100%) !important;
    color: #fff !important;
}}

/* ─── INPUT ─── */
input, select, textarea {{
    background: rgba(13,17,23,0.9) !important;
    color: {PALETTE['text_main']} !important;
    border: 1px solid {PALETTE['border']} !important;
    border-radius: 8px !important;
}}

/* ─── INSIGHT CARD ─── */
.insight-card {{
    background: linear-gradient(135deg, rgba(245,166,35,0.08) 0%, rgba(245,166,35,0.03) 100%);
    padding: 18px;
    border-radius: 14px;
    border: 1px solid {PALETTE['border']};
    margin: 12px 0;
    transition: all 0.2s;
}}
.insight-card:hover {{
    border-color: {PALETTE['accent']};
    background: linear-gradient(135deg, rgba(245,166,35,0.12) 0%, rgba(245,166,35,0.05) 100%);
}}
.insight-card h4 {{
    color: {PALETTE['accent']} !important;
    margin-bottom: 8px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}}

/* ─── GLOSSARIO TOOLTIP ─── */
.glossario {{
    background: rgba(13,17,23,0.95);
    border: 1px solid {PALETTE['border']};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 0.82rem;
    color: {PALETTE['text_sub']};
    line-height: 1.6;
    margin-top: 6px;
}}
.term {{
    color: {PALETTE['accent']};
    font-weight: 700;
}}

/* ─── SEPARATOR ─── */
hr {{ border-color: {PALETTE['border_soft']} !important; margin: 24px 0 !important; }}

/* ─── SECTION HEADER ─── */
.section-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 20px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid {PALETTE['border_soft']};
}}
.section-header span {{
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: {PALETTE['text_main']} !important;
    letter-spacing: 0.4px;
}}
.section-icon {{
    width: 30px; height: 30px;
    background: linear-gradient(135deg, rgba(245,166,35,0.2), rgba(245,166,35,0.05));
    border: 1px solid {PALETTE['border']};
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
}}

/* ─── LEGEND BOX ─── */
.legend-box {{
    background: rgba(13,17,23,0.7);
    border: 1px solid {PALETTE['border_soft']};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 0.82rem;
    color: {PALETTE['text_sub']};
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    margin: 8px 0 16px;
}}
.legend-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    color: {PALETTE['text_sub']};
}}
.legend-dot {{
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TEMPLATE PLOTLY GLOBALE — Warm Theme
# --------------------------------------------------
PLOTLY_TEMPLATE = {
    'plot_bgcolor':  'rgba(13, 17, 23, 0.85)',
    'paper_bgcolor': 'rgba(13, 17, 23, 0.0)',
    'font': {'color': PALETTE['text_sub'], 'family': 'Outfit, Arial, sans-serif'},
    'xaxis': {
        'gridcolor': 'rgba(245,166,35,0.06)',
        'linecolor': 'rgba(245,166,35,0.2)',
        'zerolinecolor': 'rgba(245,166,35,0.2)'
    },
    'yaxis': {
        'gridcolor': 'rgba(245,166,35,0.06)',
        'linecolor': 'rgba(245,166,35,0.2)',
        'zerolinecolor': 'rgba(245,166,35,0.2)'
    },
}

def plot_layout(**kwargs):
    """Restituisce un dict layout con il tema warm applicato."""
    base = dict(
        plot_bgcolor='rgba(13,17,23,0.85)',
        paper_bgcolor='rgba(13,17,23,0.0)',
        font=dict(color=PALETTE['text_sub'], family='Outfit, Arial, sans-serif'),
    )
    base.update(kwargs)
    return base

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
    st.sidebar.success(f"✅ Banca dati connessa\n{db_time.strftime('%d/%m/%Y %H:%M')}")
except Exception as e:
    st.sidebar.error(f"❌ Errore connessione: {e}")
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
        FROM v_staffing
        ORDER BY giorno, deposito;
    """, get_conn())

@st.cache_data(ttl=600)
def load_depositi_stats() -> pd.DataFrame:
    return pd.read_sql("""
        SELECT deposito, giorni_attivi, dipendenti_medi_giorno
        FROM v_depositi_organico_medio
        ORDER BY deposito;
    """, get_conn())

@st.cache_data(ttl=600)
def load_turni_calendario() -> pd.DataFrame:
    return pd.read_sql("""
        SELECT tg.data AS giorno, tg.deposito, COUNT(tg.id) AS turni
        FROM turni_giornalieri tg
        GROUP BY tg.data, tg.deposito
        ORDER BY tg.data, tg.deposito;
    """, get_conn())

@st.cache_data(ttl=600)
def load_copertura() -> pd.DataFrame:
    return pd.read_sql("""
        WITH
        forza AS (
            SELECT r.data AS giorno, r.deposito,
                   COUNT(DISTINCT r.matricola) AS persone_in_forza,
                   COUNT(*) FILTER (WHERE r.turno IN ('R','FP','PS','AP','PADm','NF','FI')) AS assenze_nominali
            FROM roster r
            GROUP BY r.data, r.deposito
        ),
        turni AS (
            SELECT data AS giorno, deposito, COUNT(*) AS turni_richiesti
            FROM turni_giornalieri
            GROUP BY data, deposito
        ),
        ass AS (
            SELECT c.data AS giorno, a.deposito,
                   ROUND(COALESCE(a.infortuni,0)+COALESCE(a.malattie,0)+COALESCE(a.legge_104,0)+
                         COALESCE(a.altre_assenze,0)+COALESCE(a.congedo_parentale,0)+COALESCE(a.permessi_vari,0))::int AS assenze_statistiche
            FROM assenze a
            JOIN calendar c ON c.daytype = a.daytype
        )
        SELECT f.giorno, f.deposito, f.persone_in_forza,
               COALESCE(t.turni_richiesti,0) AS turni_richiesti,
               f.assenze_nominali,
               COALESCE(a.assenze_statistiche,0) AS assenze_statistiche,
               f.persone_in_forza - COALESCE(t.turni_richiesti,0)
               - f.assenze_nominali - COALESCE(a.assenze_statistiche,0) AS gap
        FROM forza f
        LEFT JOIN turni t USING (giorno, deposito)
        LEFT JOIN ass   a USING (giorno, deposito)
        ORDER BY f.giorno, f.deposito;
    """, get_conn())

# --- caricamento ---
try:
    df_raw      = load_staffing()
    df_raw["giorno"] = pd.to_datetime(df_raw["giorno"])
    df_depositi = load_depositi_stats()
    df_raw      = df_raw[df_raw["deposito"] != "depbelvede"].copy()
    df_depositi = df_depositi[df_depositi["deposito"] != "depbelvede"].copy()
except Exception as e:
    st.error(f"❌ Errore caricamento dati: {e}")
    st.stop()

try:
    df_turni_cal = load_turni_calendario()
    df_turni_cal["giorno"] = pd.to_datetime(df_turni_cal["giorno"])
    turni_cal_ok = len(df_turni_cal) > 0
    if not turni_cal_ok:
        st.sidebar.warning("⚠️ Nessun turno trovato nel calendario")
except Exception as e:
    st.sidebar.error(f"❌ Errore turni: {e}")
    df_turni_cal = pd.DataFrame()
    turni_cal_ok = False

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
    df.loc[df["deposito_norm"] == "ancona", "ferie_extra"] += 5.0
    mask_eligible = ~df["deposito_norm"].isin(["ancona", "moie"])
    eligible = df[mask_eligible].copy()
    if not eligible.empty:
        eligible["peso"]  = eligible["totale_autisti"].clip(lower=0)
        sum_pesi          = eligible.groupby("giorno")["peso"].transform("sum")
        eligible["quota"] = np.where(sum_pesi > 0, 5.0 * eligible["peso"] / sum_pesi, 0.0)
        df.loc[eligible.index, "ferie_extra"] += eligible["quota"].values
    df["assenze_previste_adj"]  = df["assenze_previste"]  + df["ferie_extra"]
    df["disponibili_netti_adj"] = (df["disponibili_netti"] - df["ferie_extra"]).clip(lower=0)
    df["gap_adj"]               = df["gap"] - df["ferie_extra"]
    df.drop(columns=["deposito_norm"], inplace=True)
    return df

df_raw["categoria_giorno"] = df_raw["tipo_giorno"].apply(categorizza_tipo_giorno)

# --------------------------------------------------
# SIDEBAR — Più chiara e guidata
# --------------------------------------------------
st.sidebar.markdown(f"""
<div style='text-align:center; padding: 16px 0 8px;'>
    <p style='font-size:1.1rem; font-weight:800; color:{PALETTE["accent"]}; letter-spacing:1px; margin:0;'>🚍 ESTATE 2026</p>
    <p style='font-size:0.72rem; color:{PALETTE["text_muted"]}; letter-spacing:2px; margin:4px 0 0;'>CONTROLLO PIANIFICAZIONE</p>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Nota esplicativa
st.sidebar.markdown(f"""
<div style='background:rgba(245,166,35,0.06);border:1px solid {PALETTE["border"]};
border-radius:10px;padding:10px 12px;margin-bottom:12px;'>
<p style='font-size:0.78rem;color:{PALETTE["text_sub"]};margin:0;line-height:1.5;'>
💡 <b style="color:{PALETTE["accent"]}">Come usare la dashboard:</b><br>
Seleziona i depositi e il periodo che vuoi analizzare. I grafici si aggiorneranno automaticamente.
</p>
</div>
""", unsafe_allow_html=True)

depositi_lista = sorted(df_raw["deposito"].unique())
deposito_sel   = st.sidebar.multiselect(
    "📍 Depositi da analizzare",
    depositi_lista,
    default=depositi_lista,
    help="Seleziona uno o più depositi. Di default sono tutti selezionati."
)

min_date   = df_raw["giorno"].min().date()
max_date   = df_raw["giorno"].max().date()
date_range = st.sidebar.date_input(
    "📅 Periodo di analisi",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    help="Scegli il periodo di date che vuoi visualizzare."
)
st.sidebar.markdown("---")

soglia_gap = st.sidebar.slider(
    "🚨 Soglia di allarme (gap)",
    min_value=-50, max_value=0, value=-10,
    help="Quando il gap scende sotto questa soglia, il giorno viene marcato come CRITICO (in rosso)."
)

ferie_10 = st.sidebar.checkbox(
    "🏖️ Simula 10 gg ferie estive",
    value=False,
    help="Aggiunge una stima di 10 giornate ferie: 5 al deposito di Ancona, 5 distribuiti proporzionalmente sugli altri depositi (escluso Moie)."
)

with st.sidebar.expander("⚙️ Filtri avanzati", expanded=False):
    show_forecast  = st.checkbox("📈 Mostra previsioni",   value=True, key="sf1")
    show_insights  = st.checkbox("💡 Mostra suggerimenti", value=True, key="sf2")
    min_gap_filter = st.number_input("Gap minimo", value=-100, key="sf3")
    max_gap_filter = st.number_input("Gap massimo", value=100, key="sf4")

st.sidebar.markdown("---")

# --- filtro staffing ---
if len(date_range) == 2:
    df_filtered = df_raw[
        (df_raw["deposito"].isin(deposito_sel)) &
        (df_raw["giorno"] >= pd.to_datetime(date_range[0])) &
        (df_raw["giorno"] <= pd.to_datetime(date_range[1]))
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
        st.error(f"❌ Errore simulazione ferie: {e}"); st.stop()

df_filtered = df_filtered[
    (df_filtered["gap"] >= min_gap_filter) &
    (df_filtered["gap"] <= max_gap_filter)
].copy()

# --- filtro copertura ---
if len(df_copertura) > 0:
    if ferie_10:
        df_cop = df_copertura.copy()
        df_cop["deposito_norm"] = df_cop["deposito"].str.strip().str.lower()
        df_cop["ferie_extra"]   = 0.0
        df_cop.loc[df_cop["deposito_norm"] == "ancona", "ferie_extra"] += 5.0
        mask_elig = ~df_cop["deposito_norm"].isin(["ancona","moie"])
        elig = df_cop[mask_elig].copy()
        if not elig.empty:
            elig["peso"] = elig["persone_in_forza"].clip(lower=0)
            sum_p = elig.groupby("giorno")["peso"].transform("sum")
            elig["quota"] = np.where(sum_p > 0, 5.0*elig["peso"]/sum_p, 0.0)
            df_cop.loc[elig.index, "ferie_extra"] += elig["quota"].values
        df_cop["assenze_nominali"] = df_cop["assenze_nominali"] + df_cop["ferie_extra"]
        df_cop["gap"] = (df_cop["persone_in_forza"] - df_cop["turni_richiesti"]
                         - df_cop["assenze_nominali"] - df_cop["assenze_statistiche"])
        df_cop.drop(columns=["deposito_norm","ferie_extra"], inplace=True)
        df_copertura_filtered = df_cop
    else:
        df_copertura_filtered = df_copertura.copy()

    if len(date_range) == 2:
        df_copertura_filtered = df_copertura_filtered[
            (df_copertura_filtered["giorno"] >= pd.to_datetime(date_range[0])) &
            (df_copertura_filtered["giorno"] <= pd.to_datetime(date_range[1])) &
            (df_copertura_filtered["deposito"].isin(deposito_sel))
        ]
    else:
        df_copertura_filtered = df_copertura_filtered[
            df_copertura_filtered["deposito"].isin(deposito_sel)
        ]
else:
    df_copertura_filtered = pd.DataFrame()

# --- filtro turni calendario ---
if turni_cal_ok and len(df_turni_cal) > 0:
    if len(date_range) == 2:
        df_tc_filtered = df_turni_cal[
            (df_turni_cal["giorno"] >= pd.to_datetime(date_range[0])) &
            (df_turni_cal["giorno"] <= pd.to_datetime(date_range[1])) &
            (df_turni_cal["deposito"].isin(deposito_sel))
        ].copy()
    else:
        df_tc_filtered = df_turni_cal[df_turni_cal["deposito"].isin(deposito_sel)].copy()
else:
    df_tc_filtered = pd.DataFrame()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    ferie_badge = ' <span style="background:rgba(79,195,247,0.15);border:1px solid rgba(79,195,247,0.3);border-radius:20px;padding:3px 10px;font-size:0.78rem;color:#4FC3F7;font-weight:600;">🏖️ Simulazione Ferie attiva</span>' if ferie_10 else ""
    st.markdown(f"""
    <div style='margin-bottom: 8px;'>
        <h1 style='margin:0; font-size:2.2rem;'>🚍 Pianificazione Estate 2026</h1>
        <p style='color:{PALETTE["text_muted"]}; font-size:0.9rem; margin:4px 0 0; letter-spacing:0.5px;'>
            Analisi turni e copertura del servizio {ferie_badge}
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    if len(date_range) == 2:
        st.markdown(f"""
        <div style='text-align:right; padding-top:8px;'>
            <p style='font-size:0.78rem; color:{PALETTE["text_muted"]}; margin:0;'>PERIODO ANALIZZATO</p>
            <p style='font-size:1rem; color:{PALETTE["accent"]}; font-weight:700; margin:2px 0;'>
                {date_range[0].strftime('%d/%m')} → {date_range[1].strftime('%d/%m/%Y')}
            </p>
            <p style='font-size:0.78rem; color:{PALETTE["text_muted"]}; margin:0;'>{len(deposito_sel)} depositi · {len(df_filtered):,} record</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# KPI CARDS con descrizioni leggibili
# --------------------------------------------------
if len(df_filtered) > 0:
    totale_dipendenti  = df_depositi[df_depositi["deposito"].isin(deposito_sel)]["dipendenti_medi_giorno"].sum()
    gap_per_giorno     = df_filtered.groupby("giorno")["gap"].sum()
    gap_medio_giorno   = gap_per_giorno.mean()
    media_turni_giorno = df_filtered.groupby("giorno")["turni_richiesti"].sum().mean()
    gap_pct_medio      = (gap_medio_giorno / media_turni_giorno * 100) if media_turni_giorno > 0 else 0
    giorni_analizzati  = df_filtered["giorno"].nunique()
    giorni_critici_count = (gap_per_giorno < soglia_gap).sum()
    pct_critici        = (giorni_critici_count / giorni_analizzati * 100) if giorni_analizzati > 0 else 0

    turni_luv = df_filtered[
        df_filtered["tipo_giorno"].str.lower().isin(['lunedi','martedi','mercoledi','giovedi','venerdi'])
    ].groupby("giorno")["turni_richiesti"].sum().mean()
    turni_luv = int(turni_luv) if not np.isnan(turni_luv) else 0

    # Stato generale
    if giorni_critici_count == 0:
        stato_html = f"<span style='color:{PALETTE['success']};font-weight:700;'>✅ Tutto sotto controllo</span>"
    elif pct_critici < 20:
        stato_html = f"<span style='color:{PALETTE['warning']};font-weight:700;'>⚠️ Attenzione richiesta</span>"
    else:
        stato_html = f"<span style='color:{PALETTE['danger']};font-weight:700;'>🚨 Situazione critica</span>"

    st.markdown(f"<p style='font-size:0.9rem;margin-bottom:12px;'>Stato generale del periodo: {stato_html}</p>", unsafe_allow_html=True)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(
            "👤 Autisti in organico",
            f"{int(totale_dipendenti):,}",
            help="Numero totale di autisti presenti nell'organico dei depositi selezionati (media giornaliera)."
        )
    with kpi2:
        st.metric(
            "🚌 Turni da coprire (Lu-Ve)",
            f"{turni_luv:,}",
            help="Quante corse/turni devono essere garantite in un tipico giorno feriale (lunedì-venerdì)."
        )
    with kpi3:
        gap_label = "🟢 Margine" if gap_medio_giorno >= 0 else "🔴 Deficit"
        st.metric(
            f"⚖️ {gap_label} medio giornaliero",
            f"{int(gap_medio_giorno):+,}",
            delta=f"{gap_pct_medio:.1f}% rispetto ai turni",
            delta_color="normal" if gap_medio_giorno >= 0 else "inverse",
            help="Differenza media tra autisti disponibili e turni da coprire. Positivo = margine, Negativo = mancano autisti."
        )
    with kpi4:
        st.metric(
            "🚨 Giorni con deficit",
            f"{giorni_critici_count} su {giorni_analizzati}",
            delta=f"{pct_critici:.0f}% dei giorni",
            delta_color="inverse" if giorni_critici_count > 0 else "normal",
            help=f"Giorni in cui il gap scende sotto la soglia di allarme ({soglia_gap}). Meno è, meglio è."
        )

st.markdown("---")

# --------------------------------------------------
# AI INSIGHTS — Più leggibili e in italiano semplice
# --------------------------------------------------
if show_insights and len(df_filtered) > 0:
    st.markdown(f"""
    <div class='section-header'>
        <div class='section-icon'>💡</div>
        <span>Punti di attenzione principali</span>
    </div>
    """, unsafe_allow_html=True)

    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        by_dep    = df_filtered.groupby("deposito")["gap"].mean()
        worst_dep = by_dep.idxmin()
        best_dep  = by_dep.idxmax()
        colore_dep_worst = PALETTE['danger'] if by_dep.min() < soglia_gap else PALETTE['warning']
        st.markdown(f"""<div class='insight-card'>
            <h4>🏭 Deposito più critico</h4>
            <p style='font-size:1.05rem;margin:0 0 6px;color:{PALETTE['text_main']};'><b>{worst_dep.title()}</b></p>
            <p style='font-size:0.85rem;color:{colore_dep_worst};margin:0;'>Gap medio: <b>{by_dep.min():.1f}</b> autisti/giorno</p>
            <p style='font-size:0.8rem;color:{PALETTE['text_muted']};margin-top:8px;'>💡 Valuta di spostare turni da altri depositi o pianificare assunzioni temporanee.</p>
        </div>""", unsafe_allow_html=True)
    with ic2:
        by_cat    = df_filtered.groupby("categoria_giorno")["gap"].mean()
        worst_cat = by_cat.idxmin()
        label_map = {"Lu-Ve": "Giorni feriali (Lun-Ven)", "Sabato": "Sabato", "Domenica": "Domenica"}
        st.markdown(f"""<div class='insight-card'>
            <h4>📅 Tipo giorno più difficile</h4>
            <p style='font-size:1.05rem;margin:0 0 6px;color:{PALETTE['text_main']};'><b>{label_map.get(worst_cat, worst_cat)}</b></p>
            <p style='font-size:0.85rem;color:{PALETTE['warning']};margin:0;'>Gap medio: <b>{by_cat.min():.1f}</b> autisti</p>
            <p style='font-size:0.8rem;color:{PALETTE['text_muted']};margin-top:8px;'>💡 Prevedi turni aggiuntivi o rinforzi per questo tipo di giornata.</p>
        </div>""", unsafe_allow_html=True)
    with ic3:
        assenze_trend = df_filtered.groupby("giorno")["assenze_previste"].sum()
        if len(assenze_trend) > 1:
            crescente  = assenze_trend.iloc[-1] > assenze_trend.iloc[0]
            trend_txt  = "in aumento ⚠️" if crescente else "in calo ✅"
            trend_col  = PALETTE['warning'] if crescente else PALETTE['success']
        else:
            trend_txt, trend_col = "stabile", PALETTE['text_sub']
        media_ass = df_filtered.groupby("giorno")["assenze_previste"].sum().mean()
        st.markdown(f"""<div class='insight-card'>
            <h4>🤒 Andamento assenze</h4>
            <p style='font-size:1.05rem;margin:0 0 6px;color:{trend_col};'><b>Trend {trend_txt}</b></p>
            <p style='font-size:0.85rem;color:{PALETTE['text_sub']};margin:0;'>Media: <b>{media_ass:.1f}</b> assenti/giorno</p>
            <p style='font-size:0.8rem;color:{PALETTE['text_muted']};margin-top:8px;'>💡 Monitora settimana per settimana per cogliere picchi anticipati.</p>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")

# --------------------------------------------------
# AGGREGATI PER DEPOSITO
# --------------------------------------------------
if len(df_filtered) > 0:
    by_deposito = df_filtered.groupby("deposito").agg(
        turni_richiesti=("turni_richiesti","sum"),
        disponibili_netti=("disponibili_netti","sum"),
        gap=("gap","sum"),
        assenze_previste=("assenze_previste","sum"),
    ).reset_index()
    by_deposito = by_deposito.merge(df_depositi, on="deposito", how="left")
    giorni_per_dep = df_filtered.groupby("deposito")["giorno"].nunique().rename("giorni_periodo")
    by_deposito    = by_deposito.merge(giorni_per_dep, left_on="deposito", right_index=True)
    by_deposito["media_gap_giorno"]  = (by_deposito["gap"] / by_deposito["giorni_periodo"]).round(1)
    by_deposito["tasso_copertura_%"] = (by_deposito["disponibili_netti"] / by_deposito["turni_richiesti"] * 100).fillna(0).round(1)
    by_deposito = by_deposito.sort_values("media_gap_giorno")
else:
    by_deposito = pd.DataFrame()

# --------------------------------------------------
# TABS — Etichette più descrittive
# --------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Riepilogo generale",
    "📈 Analisi assenze",
    "🗓️ Turni programmati",
    "🏭 Per deposito",
    "📥 Scarica dati",
])

# ══════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════
with tab1:
    if len(df_filtered) == 0:
        st.info("Nessun dato disponibile per i filtri selezionati. Prova ad allargare il periodo o selezionare più depositi.")
    else:
        # Legenda colori semplice
        st.markdown(f"""
        <div class='legend-box'>
            <span style='font-size:0.8rem;color:{PALETTE["text_muted"]};font-weight:600;'>COME LEGGERE IL GRAFICO:</span>
            <span class='legend-item'><span class='legend-dot' style='background:{PALETTE["success"]};'></span> Verde = Margine disponibile (personale in eccesso)</span>
            <span class='legend-item'><span class='legend-dot' style='background:{PALETTE["danger"]};'></span> Rosso = Deficit (mancano autisti per coprire i turni)</span>
            <span class='legend-item'><span class='legend-dot' style='background:#546E7A;'></span> Grigio scuro = Turni da coprire</span>
            <span class='legend-item'>━━ Linea = Totale autisti in forza quel giorno</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='section-header'>
            <div class='section-icon'>👥</div>
            <span>Copertura giornaliera del servizio</span>
        </div>
        <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
            Ogni barra mostra come vengono "usati" gli autisti quel giorno: turni da coprire + assenze.
            Il verde indica quanti autisti rimangono liberi; il rosso indica quanti ne mancano.
        </p>
        """, unsafe_allow_html=True)

        if len(df_copertura_filtered) > 0:
            cop = df_copertura_filtered.groupby("giorno").agg(
                persone_in_forza    = ("persone_in_forza",    "sum"),
                turni_richiesti     = ("turni_richiesti",     "sum"),
                assenze_nominali    = ("assenze_nominali",    "sum"),
                assenze_statistiche = ("assenze_statistiche", "sum"),
                gap                 = ("gap",                 "sum"),
            ).reset_index()

            giorni_ok      = int((cop["gap"] >= 0).sum())
            giorni_allarme = int((cop["gap"] <  0).sum())
            gap_medio_cop  = cop["gap"].mean()
            gap_min_cop    = cop["gap"].min()

            kc1, kc2, kc3, kc4 = st.columns(4)
            with kc1:
                st.metric("👥 Autisti/giorno (media)", f"{cop['persone_in_forza'].mean():.0f}",
                          help="Numero medio di autisti presenti in organico ogni giorno nel periodo selezionato.")
            with kc2:
                st.metric("✅ Giorni con copertura ok", f"{giorni_ok}",
                          help="Giorni in cui ci sono abbastanza autisti per coprire tutti i turni.")
            with kc3:
                st.metric("🚨 Giorni in deficit", f"{giorni_allarme}",
                          help="Giorni in cui mancano autisti per coprire tutti i turni previsti.",
                          delta=f"-{giorni_allarme}" if giorni_allarme > 0 else "0",
                          delta_color="inverse" if giorni_allarme > 0 else "normal")
            with kc4:
                st.metric("📉 Gap medio/giorno", f"{gap_medio_cop:.1f}",
                          delta=f"minimo: {gap_min_cop:.0f}",
                          delta_color="normal" if gap_medio_cop >= 0 else "inverse",
                          help="Media giornaliera della differenza tra autisti disponibili e turni da coprire.")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            fig_cop = make_subplots(
                rows=2, cols=1, row_heights=[0.70, 0.30],
                shared_xaxes=True, vertical_spacing=0.05,
                subplot_titles=(
                    "Distribuzione degli autisti per tipologia ogni giorno",
                    "Margine disponibile (+) o Deficit (–)"
                ),
            )
            fig_cop.add_trace(go.Bar(
                x=cop["giorno"], y=cop["turni_richiesti"], name="Turni da coprire",
                marker_color="rgba(84,110,122,0.85)",
                hovertemplate="<b>Turni da coprire</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"
            ), row=1, col=1)
            fig_cop.add_trace(go.Bar(
                x=cop["giorno"], y=cop["assenze_nominali"], name="Assenze da programma (ferie, riposi…)",
                marker_color="rgba(55,71,79,0.90)",
                hovertemplate="<b>Assenze programmate</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"
            ), row=1, col=1)
            fig_cop.add_trace(go.Bar(
                x=cop["giorno"], y=cop["assenze_statistiche"], name="Assenze impreviste (malattie…)",
                marker_color="rgba(38,50,56,0.95)",
                hovertemplate="<b>Assenze impreviste</b><br>%{x|%d/%m/%Y}: <b>%{y:.0f}</b><extra></extra>"
            ), row=1, col=1)
            buf_colors = [f"rgba(102,187,106,0.85)" if g >= 0 else f"rgba(239,83,80,0.90)" for g in cop["gap"]]
            fig_cop.add_trace(go.Bar(
                x=cop["giorno"], y=cop["gap"], name="Margine / Deficit",
                marker=dict(color=buf_colors, line=dict(width=0.8, color="rgba(255,255,255,0.1)")),
                text=[f"<b>{int(g)}</b>" if g < 0 else "" for g in cop["gap"]],
                textposition="outside", textfont=dict(size=11, color="#EF9A9A"),
                hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Margine/Deficit: <b>%{y}</b><extra></extra>"
            ), row=1, col=1)
            fig_cop.add_trace(go.Scatter(
                x=cop["giorno"], y=cop["persone_in_forza"], name="Tot. autisti in forza",
                mode="lines", line=dict(color=PALETTE["accent"], width=2.5, dash="dot"),
                hovertemplate="<b>Autisti in forza</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"
            ), row=1, col=1)

            gap_colors2 = ["rgba(102,187,106,0.85)" if g >= 0 else "rgba(239,83,80,0.90)" for g in cop["gap"]]
            fig_cop.add_trace(go.Bar(
                x=cop["giorno"], y=cop["gap"], name="Gap",
                marker=dict(color=gap_colors2, line=dict(width=0.5, color="rgba(255,255,255,0.08)")),
                text=[f"<b>{int(g)}</b>" for g in cop["gap"]],
                textposition="outside", textfont=dict(size=9, color=PALETTE["text_sub"]),
                showlegend=False,
                hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Gap: <b>%{y}</b><extra></extra>"
            ), row=2, col=1)
            fig_cop.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.35)", line_width=1.5, row=2, col=1)
            if soglia_gap < 0:
                fig_cop.add_hline(
                    y=soglia_gap, line_dash="dash", line_color=PALETTE["danger"], line_width=2,
                    annotation_text=f"⚠️ Soglia allarme ({soglia_gap})",
                    annotation_font=dict(color=PALETTE["danger"], size=11),
                    annotation_position="top left", row=2, col=1
                )
            fig_cop.update_layout(
                barmode="stack", height=680, hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            font=dict(size=11, family="Outfit, Arial"), bgcolor="rgba(13,17,23,0.8)",
                            bordercolor=PALETTE["border_soft"], borderwidth=1),
                plot_bgcolor="rgba(13,17,23,0.85)", paper_bgcolor="rgba(13,17,23,0.0)",
                font=dict(color=PALETTE["text_sub"], family="Outfit, Arial, sans-serif"),
                margin=dict(t=60, b=20, l=10, r=10),
            )
            ax_style = dict(gridcolor="rgba(245,166,35,0.06)", linecolor="rgba(245,166,35,0.15)")
            fig_cop.update_xaxes(tickformat="%d/%m", tickangle=-45, **ax_style)
            fig_cop.update_yaxes(**ax_style, zeroline=False)
            fig_cop.update_yaxes(title_text="Autisti", row=1, col=1)
            fig_cop.update_yaxes(title_text="Margine/Deficit", row=2, col=1)
            st.plotly_chart(fig_cop, use_container_width=True, key="pc_main_cop")

        else:
            st.info("Dati di copertura non disponibili per i filtri selezionati.")

        with st.expander("📊 Approfondimento — Indicatore di salute e distribuzione assenze"):
            eg1, eg2 = st.columns(2)
            with eg1:
                st.markdown(f"##### Indicatore di salute del servizio")
                st.markdown(f"<p style='font-size:0.82rem;color:{PALETTE['text_muted']};'>Il quadrante verde indica che ci sono abbastanza autisti. Il rosso indica deficit.</p>", unsafe_allow_html=True)
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=gap_pct_medio,
                    title={'text': "Margine disponibile (%)", 'font': {'size': 14, 'color': PALETTE['text_sub']}},
                    delta={'reference': 0, 'suffix': '%'},
                    number={'suffix': '%', 'font': {'size': 28, 'color': PALETTE['accent']}},
                    gauge={
                        'axis': {'range': [-20, 20], 'tickcolor': PALETTE['text_muted']},
                        'bar':  {'color': PALETTE['accent'], 'thickness': 0.7},
                        'bgcolor': "rgba(13,17,23,0.8)", 'borderwidth': 2, 'bordercolor': PALETTE['border'],
                        'steps': [
                            {'range': [-20,-10], 'color': 'rgba(239,83,80,0.3)'},
                            {'range': [-10,  0], 'color': 'rgba(255,183,77,0.25)'},
                            {'range': [  0, 10], 'color': 'rgba(102,187,106,0.25)'},
                            {'range': [ 10, 20], 'color': 'rgba(102,187,106,0.4)'},
                        ],
                        'threshold': {
                            'line': {'color': PALETTE['danger'], 'width': 4},
                            'thickness': 0.75,
                            'value': (soglia_gap / media_turni_giorno * 100) if media_turni_giorno > 0 else 0
                        }
                    }
                ))
                fig_gauge.update_layout(
                    height=280,
                    paper_bgcolor='rgba(13,17,23,0.5)',
                    margin=dict(l=20,r=20,t=40,b=20),
                    font=dict(family="Outfit, Arial")
                )
                st.plotly_chart(fig_gauge, use_container_width=True, key="pc_2")
            with eg2:
                st.markdown("##### Tipologie di assenza — proporzioni")
                st.markdown(f"<p style='font-size:0.82rem;color:{PALETTE['text_muted']};'>Quali tipi di assenza incidono di più sull'organico.</p>", unsafe_allow_html=True)
                ab = pd.DataFrame({
                    'Tipo': ['Infortuni','Malattie','Legge 104','Congedi parentali','Permessi vari','Altre assenze'],
                    'Totale': [int(df_filtered[c].sum()) for c in
                               ['infortuni','malattie','legge_104','congedo_parentale','permessi_vari','altre_assenze']]
                })
                ab = ab[ab['Totale'] > 0]
                if len(ab) > 0:
                    fig_pie = go.Figure(go.Pie(
                        labels=ab['Tipo'], values=ab['Totale'], hole=.5,
                        marker=dict(colors=[PALETTE['danger'], PALETTE['warning'], PALETTE['accent'],
                                            PALETTE['accent2'], PALETTE['success'], PALETTE['text_muted']]),
                        textinfo='label+percent',
                        textfont=dict(family="Outfit, Arial", size=11)
                    ))
                    fig_pie.update_layout(
                        height=280, showlegend=False,
                        paper_bgcolor='rgba(13,17,23,0.5)',
                        margin=dict(l=0,r=0,t=10,b=0),
                        font=dict(color=PALETTE['text_sub'], family="Outfit, Arial")
                    )
                    st.plotly_chart(fig_pie, use_container_width=True, key="pc_3")

        st.markdown("---")
        st.markdown(f"""
        <div class='section-header'>
            <div class='section-icon'>🌡️</div>
            <span>Mappa di calore — Criticità per deposito e giorno</span>
        </div>
        <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
            Ogni cella rappresenta un giorno per quel deposito. <span style='color:{PALETTE["danger"]};'>Rosso</span> = deficit di autisti.
            <span style='color:{PALETTE["success"]};'>Verde</span> = margine sufficiente.
        </p>
        """, unsafe_allow_html=True)
        pivot_gap = df_filtered.pivot_table(
            values='gap', index='deposito',
            columns=df_filtered['giorno'].dt.strftime('%d/%m'),
            aggfunc='sum', fill_value=0
        )
        if len(pivot_gap) > 0:
            fig_heat = go.Figure(go.Heatmap(
                z=pivot_gap.values, x=pivot_gap.columns, y=[d.title() for d in pivot_gap.index],
                colorscale=[
                    [0,    PALETTE['danger']],
                    [0.3,  '#EF9A9A'],
                    [0.45, PALETTE['warning']],
                    [0.5,  '#FFF9C4'],
                    [0.55, '#C8E6C9'],
                    [0.7,  PALETTE['success']],
                    [1,    '#1B5E20']
                ],
                zmid=0,
                text=pivot_gap.values,
                texttemplate='%{text:.0f}',
                textfont=dict(size=10, family="Outfit, Arial"),
                colorbar=dict(
                    title="Gap<br>(autisti)",
                    tickfont=dict(color=PALETTE['text_sub'], family="Outfit, Arial")
                )
            ))
            fig_heat.update_layout(
                height=max(280, len(pivot_gap)*44),
                plot_bgcolor="rgba(13,17,23,0.85)",
                paper_bgcolor="rgba(13,17,23,0.0)",
                font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
                xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
                yaxis=dict(tickfont=dict(size=11)),
                margin=dict(l=10, r=10, t=20, b=40)
            )
            st.plotly_chart(fig_heat, use_container_width=True, key="pc_4")


# ══════════════════════════════════════════════════
# TAB 2 — ANALISI & ASSENZE
# ══════════════════════════════════════════════════
with tab2:
    if len(df_filtered) == 0:
        st.info("Nessun dato disponibile per i filtri selezionati.")
    else:
        st2_a, st2_b, st2_c = st.tabs([
            "📉 Scomposizione del gap",
            "🏖️ Ferie e riposi",
            "🤒 Tutte le assenze",
        ])

        # ── SOTTO-TAB A ─────────────────────────────────────────────────────
        with st2_a:
            st.markdown(f"""
            <div class='section-header'>
                <div class='section-icon'>📊</div>
                <span>Da quanti autisti si parte, dove vanno a finire</span>
            </div>
            <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
                Questo grafico mostra il <b>percorso</b> che porta dagli autisti totali al margine (o deficit) finale.
                Prima si sottraggono le assenze → si ottengono i <b>Disponibili</b>,
                poi si sottraggono i turni da coprire → si ottiene il <b>risultato finale</b>.
            </p>
            """, unsafe_allow_html=True)

            autisti_medio    = df_filtered.groupby("giorno")["totale_autisti"].sum().mean()
            assenze_medie    = df_filtered.groupby("giorno")["assenze_previste"].sum().mean()
            turni_medi       = df_filtered.groupby("giorno")["turni_richiesti"].sum().mean()
            disponibili_medi = autisti_medio - assenze_medie
            gap_medio_wf     = disponibili_medi - turni_medi

            fig_wf = go.Figure(go.Waterfall(
                orientation="v",
                measure=["absolute", "relative", "total", "relative", "total"],
                x=[
                    "👥 Autisti\ntotali",
                    "➖ Assenze\npreviste",
                    "= Autisti\ndisponibili",
                    "➖ Turni\nda coprire",
                    "= Risultato\nfinale",
                ],
                y=[autisti_medio, -assenze_medie, 0, -turni_medi, 0],
                text=[
                    f"<b>{autisti_medio:.0f}</b>",
                    f"<b>−{assenze_medie:.0f}</b>",
                    f"<b>{disponibili_medi:.0f}</b>",
                    f"<b>−{turni_medi:.0f}</b>",
                    f"<b>{'+'if gap_medio_wf>=0 else ''}{gap_medio_wf:.0f}</b>",
                ],
                textposition="outside",
                textfont=dict(size=13, color=PALETTE['text_main'], family="Outfit, Arial Black"),
                connector={"line": {"color": PALETTE["border"], "width": 1.5, "dash": "dot"}},
                increasing={"marker": {"color": PALETTE["success"], "line": {"color": "#2E7D32", "width": 1}}},
                decreasing={"marker": {"color": PALETTE["danger"],  "line": {"color": "#B71C1C", "width": 1}}},
                totals={"marker": {"color": PALETTE["accent"], "line": {"color": "rgba(255,255,255,0.2)", "width": 1}}},
                hovertemplate="<b>%{x}</b><br>Valore medio: <b>%{y:.1f}</b> autisti<extra></extra>",
            ))

            fig_wf.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)", line_width=1)

            col_annot = PALETTE["success"] if gap_medio_wf >= 0 else PALETTE["danger"]
            label_annot = (
                f"✅ Margine: +{gap_medio_wf:.0f} autisti" if gap_medio_wf >= 0
                else f"🚨 Mancano: {abs(gap_medio_wf):.0f} autisti"
            )
            fig_wf.add_annotation(
                x="= Risultato\nfinale",
                y=gap_medio_wf + (14 if gap_medio_wf >= 0 else -14),
                text=f"<b>{label_annot}</b>",
                showarrow=True, arrowhead=2, arrowcolor=col_annot,
                font=dict(size=12, color=col_annot, family="Outfit, Arial Black"),
                bgcolor="rgba(13,17,23,0.95)",
                bordercolor=col_annot, borderwidth=1.5, borderpad=7,
            )

            fig_wf.update_layout(
                height=500, showlegend=False,
                plot_bgcolor="rgba(13,17,23,0.85)", paper_bgcolor="rgba(13,17,23,0.0)",
                font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
                margin=dict(t=30, b=80, l=20, r=20),
                xaxis=dict(gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"],
                           tickfont=dict(size=11, family="Outfit, Arial")),
                yaxis=dict(title="Autisti (media/giorno)",
                           gridcolor="rgba(245,166,35,0.08)", linecolor=PALETTE["border"],
                           zeroline=True, zerolinecolor="rgba(255,255,255,0.15)", zerolinewidth=1.5),
            )
            st.plotly_chart(fig_wf, use_container_width=True, key="pc_5")

            wk1, wk2, wk3 = st.columns(3)
            with wk1:
                st.metric("👥 Autisti in organico (media/gg)", f"{autisti_medio:.0f}",
                          help="Quanti autisti ci sono in totale in organico, in media, ogni giorno.")
            with wk2:
                st.metric("🏥 Assenze medie al giorno", f"{assenze_medie:.0f}",
                          delta=f"−{assenze_medie/autisti_medio*100:.1f}% dell'organico" if autisti_medio > 0 else "",
                          delta_color="inverse",
                          help="Quanti autisti in media sono assenti ogni giorno (ferie, malattie, L.104 ecc.).")
            with wk3:
                risultato_label = "✅ Il servizio è coperto" if gap_medio_wf >= 0 else f"🚨 Deficit di {abs(gap_medio_wf):.0f} autisti"
                st.metric("🚌 Turni da coprire (media/gg)", f"{turni_medi:.0f}",
                          delta=risultato_label,
                          delta_color="normal" if gap_medio_wf >= 0 else "inverse",
                          help="Quanti turni devono essere garantiti ogni giorno.")

            st.markdown("---")
            st.markdown(f"""
            <div class='section-header'>
                <div class='section-icon'>📈</div>
                <span>Andamento delle assenze nel tempo</span>
            </div>
            <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
                Ogni linea mostra quanti autisti sono stati assenti per quella causa ogni giorno.
            </p>
            """, unsafe_allow_html=True)
            trend_df = df_filtered.groupby("giorno").agg(
                infortuni=("infortuni","sum"), malattie=("malattie","sum"),
                legge_104=("legge_104","sum"), congedo_parentale=("congedo_parentale","sum"),
                permessi_vari=("permessi_vari","sum"),
            ).reset_index()
            fig_trend = go.Figure()
            assenze_config = [
                ("infortuni",         "Infortuni sul lavoro",  PALETTE['danger']),
                ("malattie",          "Malattie",              PALETTE['warning']),
                ("legge_104",         "Assistenza (L.104)",    PALETTE['accent']),
                ("congedo_parentale", "Congedo parentale",     PALETTE['accent2']),
                ("permessi_vari",     "Permessi vari",         PALETTE['success']),
            ]
            for col_t, label_t, colore_t in assenze_config:
                fig_trend.add_trace(go.Scatter(
                    x=trend_df["giorno"], y=trend_df[col_t],
                    mode="lines+markers", name=label_t,
                    line=dict(color=colore_t, width=2.5),
                    marker=dict(size=5),
                    hovertemplate=f"<b>{label_t}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y:.1f}}</b> autisti<extra></extra>"
                ))
            fig_trend.update_layout(
                height=400, hovermode="x unified",
                legend=dict(orientation="h", y=-0.22, font=dict(family="Outfit, Arial", size=11)),
                plot_bgcolor="rgba(13,17,23,0.85)", paper_bgcolor="rgba(13,17,23,0.0)",
                font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
                xaxis=dict(title="Data", tickformat="%d/%m", tickangle=-45,
                           gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"]),
                yaxis=dict(title="Autisti assenti", gridcolor="rgba(245,166,35,0.06)",
                           linecolor=PALETTE["border"]),
                margin=dict(t=20, b=80, l=10, r=10)
            )
            st.plotly_chart(fig_trend, use_container_width=True, key="pc_7")

        # ── SOTTO-TAB B — FERIE & RIPOSI ────────────────────────────────────
        with st2_b:
            st.markdown(f"""
            <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
                Mostra quante <b>Ferie Programmate (FP)</b> e <b>Riposi (R)</b> sono previsti ogni giorno,
                secondo il programma dei turni (roster).
            </p>
            """, unsafe_allow_html=True)
            try:
                d0 = df_filtered["giorno"].min().date()
                d1 = df_filtered["giorno"].max().date()
                deps_str = ",".join([f"'{d}'" for d in deposito_sel])
                df_fp_r = pd.read_sql(f"""
                    SELECT data AS giorno, deposito,
                           COUNT(*) FILTER (WHERE turno='FP') AS ferie_programmate,
                           COUNT(*) FILTER (WHERE turno='R')  AS riposi
                    FROM roster
                    WHERE data BETWEEN '{d0}' AND '{d1}' AND deposito IN ({deps_str})
                    GROUP BY data, deposito ORDER BY data, deposito;
                """, get_conn())
                df_fp_r["giorno"] = pd.to_datetime(df_fp_r["giorno"])
                fp_r_daily = df_fp_r.groupby("giorno")[["ferie_programmate","riposi"]].sum().reset_index()

                k1,k2,k3,k4 = st.columns(4)
                with k1: st.metric("🏖️ Ferie programmate totali",    f"{int(fp_r_daily['ferie_programmate'].sum()):,}",
                                   help="Totale giornate ferie programmate nel periodo.")
                with k2: st.metric("😴 Riposi totali",                f"{int(fp_r_daily['riposi'].sum()):,}",
                                   help="Totale giornate di riposo nel periodo.")
                with k3: st.metric("📅 Ferie medie al giorno",        f"{fp_r_daily['ferie_programmate'].mean():.1f}",
                                   help="Quante ferie in media ogni giorno nel periodo.")
                with k4: st.metric("📅 Riposi medi al giorno",        f"{fp_r_daily['riposi'].mean():.1f}",
                                   help="Quanti riposi in media ogni giorno nel periodo.")

                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                view_fp_r = st.radio(
                    "Visualizza per:",
                    ["Totale (ferie vs riposi)", "Singolo deposito"],
                    horizontal=True, key="view_fp_r"
                )

                if view_fp_r == "Totale (ferie vs riposi)":
                    fig_fpr = go.Figure()
                    fig_fpr.add_trace(go.Bar(x=fp_r_daily["giorno"], y=fp_r_daily["ferie_programmate"],
                        name="Ferie programmate", marker_color=PALETTE["success"],
                        hovertemplate="<b>Ferie programmate</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"))
                    fig_fpr.add_trace(go.Bar(x=fp_r_daily["giorno"], y=fp_r_daily["riposi"],
                        name="Riposi", marker_color=PALETTE["accent2"],
                        hovertemplate="<b>Riposi</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"))
                    fig_fpr.update_layout(
                        barmode="stack", height=420, hovermode="x unified",
                        plot_bgcolor="rgba(13,17,23,0.85)", paper_bgcolor="rgba(13,17,23,0.0)",
                        font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        xaxis=dict(title="Data", tickformat="%d/%m", tickangle=-45,
                                   gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"]),
                        yaxis=dict(title="Numero di autisti", gridcolor="rgba(245,166,35,0.06)",
                                   linecolor=PALETTE["border"]),
                        margin=dict(t=40, b=60, l=10, r=10)
                    )
                    st.plotly_chart(fig_fpr, use_container_width=True, key="pc_8")
                else:
                    tipo_dep = st.radio("Tipo di assenza:", ["Ferie (FP)","Riposi (R)"], horizontal=True, key="tipo_dep_fpr")
                    col_sel  = "ferie_programmate" if "Ferie" in tipo_dep else "riposi"
                    label_sel = "Ferie programmate" if "Ferie" in tipo_dep else "Riposi"
                    fig_fpr_dep = go.Figure()
                    for dep in sorted(df_fp_r["deposito"].unique()):
                        df_d = df_fp_r[df_fp_r["deposito"]==dep]
                        fig_fpr_dep.add_trace(go.Bar(
                            x=df_d["giorno"], y=df_d[col_sel],
                            name=dep.title(), marker_color=get_colore_deposito(dep),
                            hovertemplate=f"<b>{dep.title()}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y}}</b> {label_sel}<extra></extra>"))
                    fig_fpr_dep.update_layout(
                        barmode="stack", height=420, hovermode="x unified",
                        title=f"{label_sel} per deposito",
                        plot_bgcolor="rgba(13,17,23,0.85)", paper_bgcolor="rgba(13,17,23,0.0)",
                        font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        xaxis=dict(title="Data", tickformat="%d/%m", tickangle=-45,
                                   gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"]),
                        yaxis=dict(title="Numero di autisti", gridcolor="rgba(245,166,35,0.06)",
                                   linecolor=PALETTE["border"]),
                        margin=dict(t=50, b=60, l=10, r=10)
                    )
                    st.plotly_chart(fig_fpr_dep, use_container_width=True, key="pc_9")
            except Exception as e:
                st.warning(f"⚠️ Impossibile caricare dati ferie/riposi: {e}")

        # ── SOTTO-TAB C — ASSENZE COMPLETE ──────────────────────────────────
        with st2_c:
            st.markdown(f"""
            <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
                Panoramica completa di tutte le assenze: sia quelle statistiche (stima basata su dati storici)
                che quelle nominali dal programma turni (PS = permesso straordinario, AP = aspettativa, ecc.)
            </p>
            """, unsafe_allow_html=True)

            # Glossario assenze
            with st.expander("📖 Glossario dei codici assenza — clicca per aprire"):
                st.markdown(f"""
                <div class='glossario'>
                <span class='term'>Infortuni</span> — Autisti assenti per infortuni sul lavoro.<br>
                <span class='term'>Malattie</span> — Assenze per malattia (stima basata su dati storici).<br>
                <span class='term'>L.104</span> — Permessi per assistenza a familiari disabili (Legge 104/1992).<br>
                <span class='term'>Congedo parentale</span> — Assenze per maternità/paternità o congedi familiari.<br>
                <span class='term'>Permessi vari</span> — Altri permessi retribuiti.<br>
                <span class='term'>PS (Permesso Straordinario)</span> — Permessi non programmati.<br>
                <span class='term'>AP (Aspettativa)</span> — Autisti in aspettativa non retribuita.<br>
                <span class='term'>PADm (Congedo Straordinario)</span> — Congedo per assistenza familiare grave.<br>
                <span class='term'>NF (Non in Forza)</span> — Autisti temporaneamente non disponibili.
                </div>
                """, unsafe_allow_html=True)

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
                    FROM roster
                    WHERE data BETWEEN '{d0}' AND '{d1}' AND deposito IN ({deps_str})
                    GROUP BY data, deposito ORDER BY data, deposito;
                """, get_conn())
                df_nominali["giorno"] = pd.to_datetime(df_nominali["giorno"])
                nom_daily = df_nominali.groupby("giorno")[["ps","aspettativa","congedo_straord","non_in_forza"]].sum().reset_index()
                stat_daily = df_filtered.groupby("giorno").agg(
                    infortuni=("infortuni","sum"), malattie=("malattie","sum"),
                    legge_104=("legge_104","sum"), altre_assenze=("altre_assenze","sum"),
                    congedo_parentale=("congedo_parentale","sum"), permessi_vari=("permessi_vari","sum"),
                ).reset_index()
                df_assenze_full = stat_daily.merge(nom_daily, on="giorno", how="left").fillna(0)

                k1,k2,k3,k4,k5,k6 = st.columns(6)
                with k1: st.metric("🤕 Infortuni",      f"{int(df_assenze_full['infortuni'].sum()):,}")
                with k2: st.metric("🤒 Malattie",        f"{int(df_assenze_full['malattie'].sum()):,}")
                with k3: st.metric("♿ Legge 104",        f"{int(df_assenze_full['legge_104'].sum()):,}")
                with k4: st.metric("📋 Perm. straord.",  f"{int(df_assenze_full['ps'].sum()):,}")
                with k5: st.metric("⏸️ Aspettativa",    f"{int(df_assenze_full['aspettativa'].sum()):,}")
                with k6: st.metric("🔴 Non in forza",   f"{int(df_assenze_full['non_in_forza'].sum()):,}")

                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                palette_ass = [
                    ("infortuni",         "Infortuni sul lavoro",      PALETTE['danger']),
                    ("malattie",          "Malattie",                  PALETTE['warning']),
                    ("legge_104",         "Assistenza L.104",          PALETTE['accent']),
                    ("altre_assenze",     "Altre assenze",             "#7E57C2"),
                    ("congedo_parentale", "Congedo parentale",         PALETTE['accent2']),
                    ("permessi_vari",     "Permessi vari",             PALETTE['success']),
                    ("ps",                "Perm. Straord. (PS)",       "#EC407A"),
                    ("aspettativa",       "Aspettativa (AP)",          "#AB47BC"),
                    ("congedo_straord",   "Cong. Straord. (PADm)",     "#29B6F6"),
                    ("non_in_forza",      "Non in Forza (NF)",         PALETTE['text_muted']),
                ]
                fig_ass = go.Figure()
                for c_,l_,col_ in palette_ass:
                    if c_ in df_assenze_full.columns:
                        fig_ass.add_trace(go.Bar(
                            x=df_assenze_full["giorno"], y=df_assenze_full[c_],
                            name=l_, marker_color=col_,
                            marker_line=dict(width=0.5, color="rgba(255,255,255,0.1)"),
                            hovertemplate=f"<b>{l_}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y:.0f}}</b> autisti<extra></extra>"
                        ))
                fig_ass.update_layout(
                    barmode="stack", height=520, hovermode="x unified",
                    plot_bgcolor="rgba(13,17,23,0.85)", paper_bgcolor="rgba(13,17,23,0.0)",
                    font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                font=dict(size=10, family="Outfit, Arial")),
                    xaxis=dict(title="Data", tickformat="%d/%m", tickangle=-45,
                               gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"]),
                    yaxis=dict(title="Autisti assenti",
                               gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"]),
                    margin=dict(t=50, b=60, l=10, r=10)
                )
                st.plotly_chart(fig_ass, use_container_width=True, key="pc_10")

                with st.expander("🔍 Approfondimento per singolo deposito"):
                    dep_ass = st.selectbox(
                        "Scegli il deposito da analizzare:",
                        sorted(deposito_sel), key="dep_ass_detail",
                        format_func=lambda x: x.title()
                    )
                    df_dep_stat = df_filtered[df_filtered["deposito"]==dep_ass].groupby("giorno").agg(
                        infortuni=("infortuni","sum"), malattie=("malattie","sum"),
                        legge_104=("legge_104","sum"), altre_assenze=("altre_assenze","sum"),
                        congedo_parentale=("congedo_parentale","sum"), permessi_vari=("permessi_vari","sum"),
                    ).reset_index()
                    df_dep_nom  = df_nominali[df_nominali["deposito"]==dep_ass].copy()
                    df_dep_full = df_dep_stat.merge(
                        df_dep_nom[["giorno","ps","aspettativa","congedo_straord","non_in_forza"]],
                        on="giorno", how="left"
                    ).fillna(0)
                    fig_dep_ass = go.Figure()
                    for c_,l_,col_ in palette_ass:
                        if c_ in df_dep_full.columns:
                            fig_dep_ass.add_trace(go.Bar(
                                x=df_dep_full["giorno"], y=df_dep_full[c_],
                                name=l_, marker_color=col_,
                                hovertemplate=f"<b>{l_}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y:.0f}}</b><extra></extra>"))
                    fig_dep_ass.update_layout(
                        barmode="stack", height=400, hovermode="x unified",
                        title=f"Assenze — {dep_ass.title()}",
                        plot_bgcolor="rgba(13,17,23,0.85)", paper_bgcolor="rgba(13,17,23,0.0)",
                        font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                    font=dict(size=10, family="Outfit, Arial")),
                        xaxis=dict(tickformat="%d/%m", tickangle=-45,
                                   gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"]),
                        yaxis=dict(title="Autisti", gridcolor="rgba(245,166,35,0.06)",
                                   linecolor=PALETTE["border"]),
                        margin=dict(t=50, b=60, l=10, r=10)
                    )
                    st.plotly_chart(fig_dep_ass, use_container_width=True, key="pc_11")
            except Exception as e:
                st.warning(f"⚠️ Impossibile caricare dati assenze: {e}")


# ══════════════════════════════════════════════════
# TAB 3 — TURNI CALENDARIO
# ══════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <div class='section-header'>
        <div class='section-icon'>🗓️</div>
        <span>Turni programmati per deposito</span>
    </div>
    <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
        Quanti turni devono essere coperti ogni giorno in ciascun deposito,
        rispettando il tipo di giornata (feriale, sabato, domenica).
    </p>
    """, unsafe_allow_html=True)

    if not turni_cal_ok or len(df_tc_filtered) == 0:
        st.warning("Nessun turno trovato per il periodo selezionato.")
    else:
        tc1, tc2, tc3 = st.columns([1,1,2])
        with tc1:
            bar_mode = st.radio("Stile del grafico:", ["Barre impilate","Barre affiancate"], horizontal=False)
            bmode    = "stack" if "impilate" in bar_mode else "group"
        with tc2:
            show_totale = st.checkbox("Mostra linea del totale", value=True)
        with tc3:
            dep_tc = st.multiselect(
                "Depositi da mostrare:",
                options=sorted(df_tc_filtered["deposito"].unique()),
                default=sorted(df_tc_filtered["deposito"].unique()),
                key="dep_tc_filter"
            )

        df_tc_plot = df_tc_filtered[df_tc_filtered["deposito"].isin(dep_tc)].copy()

        if len(df_tc_plot) > 0:
            df_tc_agg = (df_tc_plot.groupby(["giorno","deposito"])["turni"]
                         .sum().reset_index().sort_values(["giorno","deposito"]))
            fig_tc = go.Figure()
            for dep in sorted(df_tc_agg["deposito"].unique()):
                df_dep = df_tc_agg[df_tc_agg["deposito"]==dep]
                fig_tc.add_trace(go.Bar(
                    x=df_dep["giorno"], y=df_dep["turni"], name=dep.title(),
                    marker_color=get_colore_deposito(dep),
                    marker_line=dict(width=0.4, color="rgba(255,255,255,0.1)"),
                    hovertemplate=f"<b>{dep.title()}</b><br>Data: %{{x|%d/%m/%Y}}<br>Turni: <b>%{{y}}</b><extra></extra>"
                ))
            if show_totale:
                tot_gg = df_tc_agg.groupby("giorno")["turni"].sum().reset_index()
                fig_tc.add_trace(go.Scatter(
                    x=tot_gg["giorno"], y=tot_gg["turni"], name="Totale turni",
                    mode="lines+markers",
                    line=dict(color=PALETTE["accent"], width=2.5, dash="dot"),
                    marker=dict(size=6, symbol="diamond"),
                    hovertemplate="<b>Totale</b><br>Data: %{x|%d/%m/%Y}<br>Turni: <b>%{y}</b><extra></extra>"
                ))
            fig_tc.update_layout(
                barmode=bmode, height=520, hovermode="x unified",
                plot_bgcolor="rgba(13,17,23,0.85)", paper_bgcolor="rgba(13,17,23,0.0)",
                font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            font=dict(size=11, family="Outfit, Arial")),
                xaxis=dict(title="Data", tickformat="%d/%m", tickangle=-45,
                           gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"]),
                yaxis=dict(title="Turni richiesti",
                           gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"]),
                margin=dict(t=40, b=60, l=10, r=10)
            )
            st.plotly_chart(fig_tc, use_container_width=True, key="pc_13")

            st.markdown("---")
            st.markdown(f"""
            <div class='section-header'>
                <div class='section-icon'>🔎</div>
                <span>Esplora i codici turno per deposito</span>
            </div>
            """, unsafe_allow_html=True)
            try:
                df_codici = pd.read_sql("""
                    SELECT deposito, codice_turno, valid, dal, al FROM turni
                    ORDER BY deposito, valid, codice_turno;
                """, get_conn())
                df_codici["dal"] = pd.to_datetime(df_codici["dal"]).dt.strftime("%d/%m/%Y")
                df_codici["al"]  = pd.to_datetime(df_codici["al"]).dt.strftime("%d/%m/%Y")

                dep_esplora = st.selectbox(
                    "📍 Seleziona il deposito:",
                    options=sorted(df_codici["deposito"].unique()),
                    format_func=lambda x: f"🏭 {x.title()}", key="dep_esplora"
                )
                tipi_disp = sorted(df_codici[df_codici["deposito"]==dep_esplora]["valid"].unique())
                tipo_sel  = st.radio(
                    "Tipo di giornata:",
                    ["Tutti"] + tipi_disp,
                    horizontal=True, key="tipo_esplora",
                    help="Lu-Ve = giorni feriali, Sa = sabato, Do = domenica"
                )

                df_dep_codici = df_codici[df_codici["deposito"]==dep_esplora].copy()
                if tipo_sel != "Tutti":
                    df_dep_codici = df_dep_codici[df_dep_codici["valid"]==tipo_sel]

                k1,k2,k3 = st.columns(3)
                with k1: st.metric("🔢 Codici turno trovati", len(df_dep_codici))
                with k2: st.metric("📋 Tipi di giornata",     df_dep_codici["valid"].nunique())
                with k3:
                    periodo = f"{df_dep_codici['dal'].iloc[0]} → {df_dep_codici['al'].iloc[0]}" if len(df_dep_codici)>0 else "—"
                    st.metric("📅 Periodo di validità", periodo)

                if len(df_dep_codici) > 0:
                    colore_dep = get_colore_deposito(dep_esplora)
                    label_tipo_map = {
                        "Lu-Ve": "📅 Lunedì — Venerdì (giorni feriali)",
                        "Sa":    "📅 Sabato",
                        "Do":    "📅 Domenica / Festivi"
                    }
                    for tipo in sorted(df_dep_codici["valid"].unique()):
                        df_tipo = df_dep_codici[df_dep_codici["valid"]==tipo]
                        st.markdown(
                            f"<p style='color:{PALETTE['text_main']};font-weight:700;font-size:0.95rem;"
                            f"margin:18px 0 8px;'>{label_tipo_map.get(tipo, tipo)} "
                            f"<span style='color:{PALETTE['text_muted']};font-size:0.78rem;font-weight:400;'>"
                            f"({len(df_tipo)} turni · {df_tipo['dal'].iloc[0]} → {df_tipo['al'].iloc[0]})"
                            f"</span></p>", unsafe_allow_html=True
                        )
                        codici = df_tipo["codice_turno"].tolist()
                        for i in range(0, len(codici), 8):
                            cols = st.columns(8)
                            for j, codice in enumerate(codici[i:i+8]):
                                with cols[j]:
                                    st.markdown(
                                        f"<div style='background:rgba(13,17,23,0.9);"
                                        f"border:1px solid {colore_dep}44;border-left:3px solid {colore_dep};"
                                        f"border-radius:8px;padding:8px 6px;text-align:center;"
                                        f"font-size:0.83rem;font-weight:700;color:{PALETTE['text_main']};"
                                        f"letter-spacing:0.5px;margin-bottom:6px;font-family:\"Outfit\",monospace;"
                                        f"transition:all 0.2s;'>{codice}</div>",
                                        unsafe_allow_html=True
                                    )
                else:
                    st.info("Nessun codice turno trovato per la selezione corrente.")
            except Exception as e:
                st.warning(f"⚠️ Impossibile caricare i codici turno: {e}")

            st.markdown("---")
            st.markdown(f"""
            <div class='section-header'>
                <div class='section-icon'>🥧</div>
                <span>Distribuzione turni per deposito</span>
            </div>
            <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
                Quota percentuale dei turni totali attribuita a ciascun deposito nel periodo.
            </p>
            """, unsafe_allow_html=True)
            tot_per_dep = df_tc_agg.groupby("deposito")["turni"].sum().reset_index()
            fig_pie_tc = go.Figure(go.Pie(
                labels=[d.title() for d in tot_per_dep["deposito"]],
                values=tot_per_dep["turni"],
                marker=dict(colors=[get_colore_deposito(d) for d in tot_per_dep["deposito"]]),
                hole=0.42, textinfo="label+percent+value",
                textfont=dict(family="Outfit, Arial", size=11),
                hovertemplate="<b>%{label}</b><br>Turni totali: %{value}<br>Quota: %{percent}<extra></extra>"
            ))
            fig_pie_tc.update_layout(
                height=440, showlegend=True,
                paper_bgcolor="rgba(13,17,23,0.0)",
                legend=dict(font=dict(color=PALETTE['text_sub'], family="Outfit, Arial")),
                font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
                margin=dict(l=20,r=20,t=20,b=20)
            )
            st.plotly_chart(fig_pie_tc, use_container_width=True, key="pc_14")

            st.markdown("---")
            st.markdown(f"""
            <div class='section-header'>
                <div class='section-icon'>📊</div>
                <span>Confronto turni per tipo di giornata</span>
            </div>
            <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
                Quanti turni vengono richiesti in un giorno feriale, sabato o domenica/festivo.
                Utile per capire dove si concentra il carico di lavoro.
            </p>
            """, unsafe_allow_html=True)
            try:
                date_list = df_tc_plot["giorno"].dt.date.unique().tolist()
                date_str  = ",".join([f"'{d}'" for d in date_list])
                df_cal_mini = pd.read_sql(f"SELECT data, daytype FROM calendar WHERE data IN ({date_str});", get_conn())
                df_cal_mini["data"] = pd.to_datetime(df_cal_mini["data"])

                def daytype_to_cat(dt):
                    dt = (dt or "").strip().lower()
                    if dt in ["lunedi","martedi","mercoledi","giovedi","venerdi"]: return "Lu-Ve"
                    elif dt == "sabato":   return "Sabato"
                    elif dt == "domenica": return "Domenica"
                    return dt.title()

                df_tc_dt = df_tc_plot.merge(df_cal_mini, left_on="giorno", right_on="data", how="left")
                df_tc_dt["categoria"] = df_tc_dt["daytype"].apply(daytype_to_cat)
                cat_order = ["Lu-Ve","Sabato","Domenica"]
                primo_gg  = df_tc_dt.groupby("categoria")["giorno"].min().to_dict()
                agg_list  = []
                for cat, gg in primo_gg.items():
                    df_g = df_tc_dt[df_tc_dt["giorno"]==gg][["deposito","turni","categoria"]]
                    agg_list.append(df_g)
                agg_dt = pd.concat(agg_list, ignore_index=True) if agg_list else pd.DataFrame()
                if len(agg_dt) > 0:
                    agg_dt["categoria"] = pd.Categorical(agg_dt["categoria"], categories=cat_order, ordered=True)
                    agg_dt = agg_dt.sort_values(["categoria","deposito"])
                    tot_cat = agg_dt.groupby("categoria")["turni"].sum().reindex(cat_order, fill_value=0)

                    cat_labels = {
                        "Lu-Ve":    "📅 Feriale\n(Lun–Ven)",
                        "Sabato":   "📅 Sabato",
                        "Domenica": "🎉 Domenica\ne Festivi"
                    }

                    fig_dt = go.Figure()
                    for dep in sorted(agg_dt["deposito"].unique()):
                        dep_d  = agg_dt[agg_dt["deposito"]==dep]
                        valori = [dep_d[dep_d["categoria"]==cat]["turni"].sum() if cat in dep_d["categoria"].values else 0 for cat in cat_order]
                        fig_dt.add_trace(go.Bar(
                            x=[cat_labels.get(c,c) for c in cat_order], y=valori, name=dep.title(),
                            marker_color=get_colore_deposito(dep),
                            marker_line=dict(width=0.4, color="rgba(255,255,255,0.1)"),
                            text=[f"{v:,}" if v > 0 else "" for v in valori],
                            textposition="inside", textfont=dict(size=11, color="white", family="Outfit, Arial"),
                            hovertemplate=f"<b>{dep.title()}</b><br>Tipo: %{{x}}<br>Turni: <b>%{{y:,}}</b><extra></extra>"
                        ))
                    fig_dt.update_layout(
                        barmode="stack", height=460, hovermode="x unified",
                        plot_bgcolor="rgba(13,17,23,0.85)", paper_bgcolor="rgba(13,17,23,0.0)",
                        font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                    font=dict(size=11, family="Outfit, Arial")),
                        xaxis=dict(title="Tipo di giornata", gridcolor="rgba(245,166,35,0.06)",
                                   linecolor=PALETTE["border"], tickfont=dict(size=12)),
                        yaxis=dict(title="Turni richiesti", gridcolor="rgba(245,166,35,0.06)",
                                   linecolor=PALETTE["border"]),
                        annotations=[
                            dict(x=cat_labels.get(cat, cat), y=tot_cat[cat],
                                 text=f"<b>Totale: {int(tot_cat[cat]):,}</b>",
                                 xanchor="center", yanchor="bottom", showarrow=False,
                                 font=dict(size=13, color=PALETTE['accent'], family="Outfit, Arial"),
                                 yshift=8)
                            for cat in cat_order if tot_cat[cat] > 0
                        ],
                        margin=dict(t=50, b=60, l=10, r=10)
                    )
                    st.plotly_chart(fig_dt, use_container_width=True, key="pc_15")

                    k1,k2,k3 = st.columns(3)
                    with k1: st.metric("📅 Turni in un giorno feriale",      f"{int(tot_cat.get('Lu-Ve',0)):,}",
                                       help="Quanti turni devono essere garantiti in un tipico giorno feriale.")
                    with k2: st.metric("📅 Turni in un giorno di sabato",    f"{int(tot_cat.get('Sabato',0)):,}",
                                       help="Quanti turni devono essere garantiti ogni sabato.")
                    with k3: st.metric("🎉 Turni in una domenica/festivo",   f"{int(tot_cat.get('Domenica',0)):,}",
                                       help="Quanti turni devono essere garantiti nelle domeniche e nei giorni festivi.")
            except Exception as e:
                st.warning(f"⚠️ Impossibile caricare l'analisi per tipo di giornata: {e}")
        else:
            st.info("Nessun dato disponibile per la selezione corrente.")


# ══════════════════════════════════════════════════
# TAB 4 — DEPOSITI
# ══════════════════════════════════════════════════
with tab4:
    if len(df_filtered) > 0 and len(by_deposito) > 0:
        st.markdown(f"""
        <div class='section-header'>
            <div class='section-icon'>🏆</div>
            <span>Situazione di ogni deposito — dal più critico al più virtuoso</span>
        </div>
        <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
            I depositi in <span style='color:{PALETTE["danger"]};'>rosso</span> sono quelli con deficit più grave.
            In <span style='color:{PALETTE["warning"]};'>arancione</span> quelli a rischio.
            In <span style='color:{PALETTE["success"]};'>verde</span> quelli che ce la fanno.
        </p>
        """, unsafe_allow_html=True)

        colors_dep = [
            PALETTE['danger']  if g < soglia_gap else
            PALETTE['warning'] if g < 0 else
            PALETTE['success']
            for g in by_deposito["media_gap_giorno"]
        ]
        # Emoji per ogni barra
        emojis = [
            "🔴" if g < soglia_gap else "🟡" if g < 0 else "🟢"
            for g in by_deposito["media_gap_giorno"]
        ]
        labels_dep = [f"{e} {d.title()}" for e, d in zip(emojis, by_deposito["deposito"])]

        fig_dep = go.Figure(go.Bar(
            y=labels_dep,
            x=by_deposito["media_gap_giorno"],
            orientation='h',
            marker=dict(
                color=colors_dep,
                line=dict(width=0.8, color="rgba(255,255,255,0.1)")
            ),
            text=[f"  {'+'if v>=0 else ''}{v:.1f} autisti/giorno" for v in by_deposito["media_gap_giorno"]],
            texttemplate='%{text}',
            textposition='outside',
            textfont=dict(size=12, family="Outfit, Arial", color=PALETTE['text_main']),
            hovertemplate="<b>%{y}</b><br>Gap medio: <b>%{x:.1f}</b> autisti/giorno<extra></extra>"
        ))
        fig_dep.add_vline(
            x=0, line_width=2, line_color=PALETTE["accent"],
            annotation_text="Linea di pareggio", annotation_font=dict(color=PALETTE["accent"], size=11)
        )
        if soglia_gap < 0:
            fig_dep.add_vline(
                x=soglia_gap, line_width=2, line_color=PALETTE["danger"], line_dash="dash",
                annotation_text=f"Soglia allarme ({soglia_gap})",
                annotation_font=dict(color=PALETTE["danger"], size=10)
            )
        fig_dep.update_layout(
            height=max(380, len(by_deposito)*48),
            showlegend=False,
            plot_bgcolor="rgba(13,17,23,0.85)", paper_bgcolor="rgba(13,17,23,0.0)",
            font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
            xaxis=dict(title="Gap medio (autisti/giorno) — Positivo = margine, Negativo = deficit",
                       gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"],
                       zeroline=False),
            yaxis=dict(gridcolor="rgba(245,166,35,0.06)", linecolor=PALETTE["border"],
                       tickfont=dict(size=12)),
            margin=dict(t=20, b=60, l=10, r=80)
        )
        st.plotly_chart(fig_dep, use_container_width=True, key="pc_16")

        st.markdown("---")
        st.markdown(f"""
        <div class='section-header'>
            <div class='section-icon'>🕸️</div>
            <span>Confronto multi-dimensionale tra depositi</span>
        </div>
        <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:16px;'>
            Ogni linea rappresenta un deposito. Più grande è l'area colorata, meglio quel deposito
            se la cava. Le dimensioni confrontate sono: turni richiesti, autisti disponibili,
            tasso di presenza e copertura percentuale.
        </p>
        """, unsafe_allow_html=True)
        by_dep_n = by_deposito.copy()
        for col_ in ['turni_richiesti','disponibili_netti','assenze_previste']:
            mx = by_dep_n[col_].max()
            by_dep_n[f'{col_}_n'] = by_dep_n[col_] / mx * 100 if mx > 0 else 0
        fig_radar = go.Figure()
        radar_labels = ['Turni\nrichiesti','Autisti\ndisponibili','Tasso\npresenza','Copertura\n%']
        for _, row in by_deposito.head(6).iterrows():
            nr = by_dep_n[by_dep_n['deposito']==row['deposito']]
            if len(nr) > 0:
                fig_radar.add_trace(go.Scatterpolar(
                    r=[
                        nr['turni_richiesti_n'].values[0],
                        nr['disponibili_netti_n'].values[0],
                        100-nr['assenze_previste_n'].values[0],
                        row['tasso_copertura_%']
                    ],
                    theta=radar_labels,
                    fill='toself',
                    name=row['deposito'].title(),
                    line=dict(color=get_colore_deposito(row['deposito']), width=2),
                    fillcolor=get_colore_deposito(row['deposito']).replace("#","rgba(") + ",0.1)" if "#" in get_colore_deposito(row['deposito']) else get_colore_deposito(row['deposito']),
                    hovertemplate=f"<b>{row['deposito'].title()}</b><br>%{{theta}}: <b>%{{r:.1f}}</b><extra></extra>"
                ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,100],
                                gridcolor='rgba(245,166,35,0.12)',
                                linecolor='rgba(245,166,35,0.2)',
                                tickfont=dict(color=PALETTE['text_muted'], size=9)),
                angularaxis=dict(tickfont=dict(color=PALETTE['text_sub'], size=11, family="Outfit, Arial")),
                bgcolor='rgba(13,17,23,0.85)'
            ),
            height=480,
            paper_bgcolor='rgba(13,17,23,0.0)',
            font=dict(color=PALETTE['text_sub'], family="Outfit, Arial"),
            legend=dict(font=dict(color=PALETTE['text_sub'], family="Outfit, Arial", size=11),
                        bgcolor="rgba(13,17,23,0.7)", bordercolor=PALETTE["border"], borderwidth=1),
            margin=dict(t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True, key="pc_17")

        st.markdown("---")
        st.markdown(f"""
        <div class='section-header'>
            <div class='section-icon'>📋</div>
            <span>Tabella di riepilogo per deposito</span>
        </div>
        """, unsafe_allow_html=True)
        df_tabella = by_deposito[[
            "deposito","dipendenti_medi_giorno","giorni_periodo",
            "disponibili_netti","assenze_previste","media_gap_giorno","tasso_copertura_%"
        ]].rename(columns={
            "deposito":               "Deposito",
            "dipendenti_medi_giorno": "Autisti in organico",
            "giorni_periodo":         "Giorni nel periodo",
            "disponibili_netti":      "Disponibili (tot.)",
            "assenze_previste":       "Assenze (tot.)",
            "media_gap_giorno":       "Gap medio/giorno",
            "tasso_copertura_%":      "Copertura (%)"
        })
        df_tabella["Deposito"] = df_tabella["Deposito"].str.title()
        st.dataframe(
            df_tabella,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Gap medio/giorno": st.column_config.NumberColumn(
                    "Gap medio/giorno",
                    help="Margine medio giornaliero. Negativo = mancano autisti.",
                    format="%.1f"
                ),
                "Copertura (%)": st.column_config.ProgressColumn(
                    "Copertura (%)",
                    help="Percentuale di copertura dei turni. 100% = tutti i turni coperti.",
                    min_value=0, max_value=120, format="%.1f%%"
                )
            }
        )
    else:
        st.info("Nessun dato disponibile per i filtri selezionati.")


# ══════════════════════════════════════════════════
# TAB 5 — EXPORT
# ══════════════════════════════════════════════════
with tab5:
    st.markdown(f"""
    <div class='section-header'>
        <div class='section-icon'>📥</div>
        <span>Scarica i dati filtrati</span>
    </div>
    <p style='font-size:0.85rem;color:{PALETTE["text_muted"]};margin-bottom:20px;'>
        Esporta i dati attualmente visibili (in base ai filtri applicati nella barra laterale)
        in formato CSV o Excel.
    </p>
    """, unsafe_allow_html=True)

    col_exp1, col_exp2 = st.columns(2)
    df_export = df_filtered.copy()
    df_export["giorno"] = df_export["giorno"].dt.strftime('%d/%m/%Y')

    with col_exp1:
        st.markdown(f"""
        <div style='background:{PALETTE["bg_card"]};border:1px solid {PALETTE["border_soft"]};
        border-radius:14px;padding:20px;margin-bottom:12px;'>
            <p style='font-size:1rem;font-weight:700;color:{PALETTE["text_main"]};margin:0 0 6px;'>📄 File CSV</p>
            <p style='font-size:0.82rem;color:{PALETTE["text_muted"]};margin:0 0 14px;'>
                Formato semplice, apribile con Excel, Google Sheets o qualsiasi programma.
                Contiene tutti i dati del periodo selezionato.
            </p>
        </div>
        """, unsafe_allow_html=True)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Scarica CSV",
            data=csv,
            file_name=f"estate2026_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.caption(f"📦 {len(df_export):,} righe · {len(df_export.columns)} colonne")

    with col_exp2:
        st.markdown(f"""
        <div style='background:{PALETTE["bg_card"]};border:1px solid {PALETTE["border_soft"]};
        border-radius:14px;padding:20px;margin-bottom:12px;'>
            <p style='font-size:1rem;font-weight:700;color:{PALETTE["text_main"]};margin:0 0 6px;'>📊 Report Excel</p>
            <p style='font-size:0.82rem;color:{PALETTE["text_muted"]};margin:0 0 14px;'>
                File multi-foglio con riepilogo generale, dati per deposito e turni calendario.
                Ideale per presentazioni e analisi approfondite.
            </p>
        </div>
        """, unsafe_allow_html=True)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, sheet_name='Dati staffing', index=False)
            if len(by_deposito) > 0:
                by_deposito.to_excel(writer, sheet_name='Per deposito', index=False)
            if turni_cal_ok and len(df_tc_filtered) > 0:
                tc_exp = df_tc_filtered.copy()
                tc_exp["giorno"] = tc_exp["giorno"].dt.strftime('%d/%m/%Y')
                tc_exp.to_excel(writer, sheet_name='Turni calendario', index=False)
        st.download_button(
            "⬇️ Scarica Report Excel",
            data=output.getvalue(),
            file_name=f"estate2026_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.caption("✅ Include: Staffing · Per deposito · Turni calendario")

    st.markdown("---")
    st.markdown(f"""
    <div class='section-header'>
        <div class='section-icon'>👁️</div>
        <span>Anteprima dei dati (prime 100 righe)</span>
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(df_export.head(100), use_container_width=True, height=380)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(f"""
<div style='text-align:center;padding:24px 20px;'>
    <p style='font-size:0.95rem;font-weight:700;color:{PALETTE["accent"]};margin:0;letter-spacing:1px;'>
        🚍 Estate 2026 — Pianificazione & Analisi Turni
    </p>
    <p style='font-size:0.8rem;color:{PALETTE["text_muted"]};margin:6px 0 0;'>
        Dati aggiornati · Streamlit · Plotly · PostgreSQL
    </p>
    <p style='font-size:0.78rem;color:{PALETTE["text_muted"]};margin:4px 0 0;opacity:0.6;'>
        Ultimo aggiornamento: {datetime.now().strftime("%d/%m/%Y %H:%M")}
    </p>
</div>
""", unsafe_allow_html=True)
