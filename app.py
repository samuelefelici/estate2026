"""
===============================================
ESTATE 2026 - DASHBOARD ANALYTICS PREMIUM
===============================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import psycopg2
from datetime import datetime, timedelta
from io import BytesIO
import base64, os

# --------------------------------------------------
# CONFIGURAZIONE PAGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Estate 2026 - Analytics Premium",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚍"
)

# --------------------------------------------------
# MAPPA COLORI DEPOSITI
# --------------------------------------------------
COLORI_DEPOSITI = {
    "ancona":                     "#22c55e",
    "polverigi":                  "#166534",
    "marina":                     "#ec4899",
    "marina di montemarciano":    "#ec4899",
    "filottrano":                 "#4ade80",
    "jesi":                       "#f97316",
    "osimo":                      "#eab308",
    "castelfidardo":              "#38bdf8",
    "castelfdardo":               "#38bdf8",
    "ostra":                      "#ef4444",
    "belvedere ostrense":         "#94a3b8",
    "belvedereostrense":          "#94a3b8",
    "depbelvede":                 "#94a3b8",
    "moie":                       "#a78bfa",
}

def get_colore_deposito(dep: str) -> str:
    return COLORI_DEPOSITI.get(str(dep).strip().lower(), "#64748b")

# --------------------------------------------------
# LOGIN
# --------------------------------------------------
from textwrap import dedent  # ✅ serve per evitare problemi di indentazione nelle stringhe multilinea

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

    st.markdown(dedent(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="stHeader"]  {{ display: none !important; }}
    footer {{ display: none !important; }}
    .block-container {{ padding-top: 0 !important; max-width: 100% !important; }}
    .stApp {{ background: #020b18 !important; }}

    @keyframes gridPulse {{ 0%, 100% {{ opacity: 0.07; }} 50% {{ opacity: 0.16; }} }}
    @keyframes nebula {{
        0%, 100% {{ transform: translate(-50%, -50%) scale(1);   opacity: 0.55; }}
        50%      {{ transform: translate(-50%, -50%) scale(1.1); opacity: 0.80; }}
    }}

    /* ✅ seconda nebula calda e leggera */
    @keyframes nebulaWarm {{
        0%, 100% {{ transform: translate(-50%, -50%) scale(1);    opacity: 0.16; }}
        50%      {{ transform: translate(-50%, -50%) scale(1.08); opacity: 0.28; }}
    }}

    @keyframes rise {{
        0%   {{ transform: translateY(0) translateX(0);    opacity: 0; }}
        10%  {{ opacity: 0.8; }}
        90%  {{ opacity: 0.5; }}
        100% {{ transform: translateY(-100vh) translateX(20px); opacity: 0; }}
    }}
    @keyframes twinkle {{ 0%, 100% {{ opacity: 0.2; }} 50% {{ opacity: 1; }} }}

    .ca-bg-grid {{
        position: fixed; inset: 0; z-index: 0; pointer-events: none;
        background-image:
            linear-gradient(rgba(59,130,246,0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59,130,246,0.06) 1px, transparent 1px);
        background-size: 48px 48px;
        animation: gridPulse 5s ease-in-out infinite;
    }}

    .ca-bg-nebula {{
        position: fixed; top: 50%; left: 50%;
        width: 900px; height: 700px;
        background: radial-gradient(ellipse,
            rgba(37,99,235,0.22) 0%, rgba(15,23,42,0.5) 45%, transparent 70%);
        animation: nebula 8s ease-in-out infinite;
        pointer-events: none; z-index: 0;
    }}

    .ca-bg-nebula-warm {{
        position: fixed; top: 52%; left: 52%;
        width: 980px; height: 780px;
        background: radial-gradient(ellipse,
            rgba(251,191,36,0.22) 0%,
            rgba(245,158,11,0.14) 30%,
            rgba(180,83,9,0.10) 52%,
            transparent 72%);
        animation: nebulaWarm 9.5s ease-in-out infinite;
        pointer-events: none; z-index: 0;
        filter: blur(0.2px);
    }}

    /* ✅ titolo più premium */
    .ca-login-title {{
        text-align:center;
        margin-bottom: 14px;
        z-index: 2;
        position: relative;

        font-size: 1.02rem;
        font-weight: 900;
        letter-spacing: 6px;
        text-transform: uppercase;

        color: #fde68a;
        background: linear-gradient(90deg,
            rgba(245,158,11,0.00),
            rgba(245,158,11,0.12),
            rgba(245,158,11,0.00));
        border: 1px solid rgba(245,158,11,0.22);
        border-radius: 14px;
        padding: 10px 14px;

        text-shadow:
          0 0 18px rgba(245,158,11,0.35),
          0 0 38px rgba(180,83,9,0.25);
        backdrop-filter: blur(8px);
    }}

    .ca-particle {{ position: fixed; border-radius: 50%; animation: rise linear infinite; pointer-events: none; z-index: 0; }}
    .ca-star {{ position: fixed; width: 2px; height: 2px; background: white; border-radius: 50%; animation: twinkle ease-in-out infinite; pointer-events: none; z-index: 0; }}

    div[data-testid="stTextInput"] > div > div {{
        background: rgba(5, 15, 40, 0.9) !important;
        border: 1px solid rgba(245,158,11,0.35) !important;
        border-radius: 10px !important;
    }}
    div[data-testid="stTextInput"] > div > div:focus-within {{
        border-color: rgba(245,158,11,0.75) !important;
        box-shadow: 0 0 0 3px rgba(245,158,11,0.14) !important;
    }}
    div[data-testid="stTextInput"] input {{
        color: #fff7ed !important;
        font-size: 1rem !important;
        letter-spacing: 3px !important;
    }}
    div[data-testid="stTextInput"] label {{ display: none !important; }}

    /* ✅ logo con glow caldo e più luminoso dietro */
    .ca-logo-wrap {{
        position: relative;
        display: inline-block;
    }}
    .ca-logo-glow {{
        position:absolute;
        inset:-44px;
        z-index:0;
        border-radius:30px;
        background: radial-gradient(circle at 50% 45%,
            rgba(251,191,36,0.62) 0%,
            rgba(245,158,11,0.40) 30%,
            rgba(180,83,9,0.22) 55%,
            rgba(2,11,24,0.0) 74%);
        filter: blur(12px);
    }}
    .ca-logo-img {{
        position: relative;
        z-index: 1;
        transition: filter 0.4s ease;
        cursor: default;
    }}
    .ca-logo-img:hover {{
        filter: drop-shadow(0 0 18px rgba(251,191,36,0.55))
                drop-shadow(0 0 36px rgba(245,158,11,0.35))
                drop-shadow(0 0 55px rgba(59,130,246,0.15))
                brightness(1.08);
    }}

    .ca-security {{
        position: fixed; bottom: 0; left: 0; right: 0;
        padding: 10px 20px 12px 20px;
        background: rgba(2,11,24,0.94);
        border-top: 1px solid rgba(59,130,246,0.22);
        backdrop-filter: blur(10px);
        box-shadow: 0 -12px 30px rgba(0,0,0,0.45);
        z-index: 9999;
    }}
    .ca-security-row {{
        display: flex; justify-content: center; align-items: center;
        gap: 18px; flex-wrap: wrap;
    }}
    .ca-security-item {{
        color: rgba(226,232,240,0.92);
        font-size: 0.72rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 8px;
        text-shadow: 0 0 10px rgba(59,130,246,0.25);
    }}
    .ca-security-item svg {{
        color: rgba(147,197,253,0.95);
        filter: drop-shadow(0 0 10px rgba(59,130,246,0.25));
    }}
    .ca-sep {{
        color: rgba(147,197,253,0.55);
        font-size: 1rem;
        text-shadow: 0 0 10px rgba(59,130,246,0.15);
    }}

    /* ✅ credits: pill + contrasto (il tuo marrone sul nome resta inline) */
    .ca-security-credits {{
        margin-top: 7px;
        text-align: center;
        font-size: 0.72rem;
        letter-spacing: 0.6px;
        color: rgba(226,232,240,0.82);
        text-shadow: 0 0 12px rgba(0,0,0,0.55);
        background: rgba(255, 247, 237, 0.10);
        border: 1px solid rgba(245,158,11,0.18);
        display: inline-block;
        padding: 6px 10px;
        border-radius: 12px;
    }}
    </style>

    <div class="ca-bg-grid"></div>
    <div class="ca-bg-nebula"></div>
    <div class="ca-bg-nebula-warm"></div>

    <div class="ca-star" style="top:8%;  left:15%; animation-duration:3s;   animation-delay:0s;"></div>
    <div class="ca-star" style="top:22%; left:78%; animation-duration:4s;   animation-delay:1s;"></div>
    <div class="ca-star" style="top:55%; left:92%; animation-duration:2.5s; animation-delay:0.5s;"></div>
    <div class="ca-star" style="top:72%; left:5%;  animation-duration:5s;   animation-delay:2s;"></div>
    <div class="ca-star" style="top:88%; left:45%; animation-duration:3.5s; animation-delay:1.5s;"></div>
    <div class="ca-star" style="top:35%; left:32%; animation-duration:4.5s; animation-delay:0.8s;"></div>
    <div class="ca-star" style="top:15%; left:62%; animation-duration:2.8s; animation-delay:2.5s;"></div>
    <div class="ca-star" style="top:65%; left:55%; animation-duration:3.2s; animation-delay:0.3s;"></div>

    <div class="ca-particle" style="width:3px;height:3px;background:#3b82f6;left:10%;bottom:0;animation-duration:9s; animation-delay:0s;"></div>
    <div class="ca-particle" style="width:2px;height:2px;background:#60a5fa;left:25%;bottom:0;animation-duration:12s;animation-delay:2s;"></div>
    <div class="ca-particle" style="width:4px;height:4px;background:#ef4444;left:40%;bottom:0;animation-duration:8s; animation-delay:1s;"></div>
    <div class="ca-particle" style="width:2px;height:2px;background:#22c55e;left:55%;bottom:0;animation-duration:11s;animation-delay:3s;"></div>
    <div class="ca-particle" style="width:3px;height:3px;background:#3b82f6;left:70%;bottom:0;animation-duration:10s;animation-delay:0.5s;"></div>
    <div class="ca-particle" style="width:2px;height:2px;background:#93c5fd;left:82%;bottom:0;animation-duration:13s;animation-delay:4s;"></div>
    <div class="ca-particle" style="width:3px;height:3px;background:#60a5fa;left:92%;bottom:0;animation-duration:9s; animation-delay:1.5s;"></div>
    """), unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<div style='height:18vh'></div>", unsafe_allow_html=True)

        st.markdown("<div class='ca-login-title'>ANALISI ESTATE 2026</div>", unsafe_allow_html=True)

        def _entered():
            st.session_state["password_correct"] = (st.session_state["_pwd"] == st.secrets["APP_PASSWORD"])

        st.text_input(
            "Password",
            type="password",
            on_change=_entered,
            key="_pwd",
            placeholder="🔒  Inserisci password",
            label_visibility="collapsed",
        )

        if st.session_state.get("password_correct") is False:
            st.error("❌ Password errata")

        if logo_b64:
            st.markdown(
                dedent(f"""
                <div style='text-align:center; margin-top:28px;'>
                  <div class="ca-logo-wrap">
                    <div class="ca-logo-glow"></div>
                    <img class='ca-logo-img' src='data:image/png;base64,{logo_b64}'
                         style='height:420px; width:auto; opacity:0.96;'/>
                  </div>
                </div>
                """),
                unsafe_allow_html=True,
            )

    # ✅ footer fisso: FUORI dal container centrale
    st.markdown(dedent(f"""
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
          </svg>Accesso riservato · Estate 2026
        </span>
      </div>

      <div style="text-align:center;">
        <div class="ca-security-credits">
          Progettato e sviluppato da <b style='color:#78350f !important;'>Samuele Felici</b> · © {yr} — Tutti i diritti riservati
        </div>
      </div>
    </div>
    """), unsafe_allow_html=True)

    return False


if not check_password():
    st.stop()


# --------------------------------------------------
# SPLASH SCREEN (solo al primo accesso)
# --------------------------------------------------
if not st.session_state.get("splash_done"):
    st.session_state["splash_done"] = True

    st.markdown("""
<style>
[data-testid="stSidebar"]{display:none!important}
[data-testid="stHeader"]{display:none!important}
footer{display:none!important}
.block-container{padding:0!important;max-width:100%!important}
.stApp{background:#020b18!important;overflow:hidden}

/* ───────────────────────────────────────────────
   Palette “calda premium” coerente col login
   ─────────────────────────────────────────────── */
:root{
  --warm-1: rgba(251,191,36,0.70);  /* amber */
  --warm-2: rgba(245,158,11,0.45);  /* orange */
  --warm-3: rgba(180,83,9,0.28);    /* brown */
  --cool-1: rgba(59,130,246,0.14);  /* blue soft */
}

/* sfondo: griglia + nebule calde */
@keyframes gridPulse{0%,100%{opacity:0.05}50%{opacity:0.11}}
@keyframes nebulaCool{0%,100%{transform:translate(-50%,-50%) scale(1);opacity:.22}50%{transform:translate(-50%,-50%) scale(1.08);opacity:.34}}
@keyframes nebulaWarm{0%,100%{transform:translate(-50%,-50%) scale(1);opacity:.18}50%{transform:translate(-50%,-50%) scale(1.10);opacity:.30}}

@keyframes corePulse{
  0%,100%{
    transform:translate(-50%,-50%) scale(1);
    box-shadow:
      0 0 28px 8px rgba(251,191,36,0.55),
      0 0 70px 26px rgba(245,158,11,0.22),
      0 0 120px 48px rgba(180,83,9,0.14);
  }
  50%{
    transform:translate(-50%,-50%) scale(1.15);
    box-shadow:
      0 0 46px 16px rgba(251,191,36,0.75),
      0 0 110px 44px rgba(245,158,11,0.30),
      0 0 170px 70px rgba(180,83,9,0.18);
  }
}

@keyframes spin1{from{transform:translate(-50%,-50%) rotate(0deg)}to{transform:translate(-50%,-50%) rotate(360deg)}}
@keyframes spin2{from{transform:translate(-50%,-50%) rotate(0deg)}to{transform:translate(-50%,-50%) rotate(-360deg)}}
@keyframes spin3{from{transform:translate(-50%,-50%) rotate(45deg)}to{transform:translate(-50%,-50%) rotate(405deg)}}

@keyframes orb1{from{transform:rotate(0deg) translateX(105px) rotate(0deg)}to{transform:rotate(360deg) translateX(105px) rotate(-360deg)}}
@keyframes orb2{from{transform:rotate(120deg) translateX(160px) rotate(-120deg)}to{transform:rotate(480deg) translateX(160px) rotate(-480deg)}}
@keyframes orb3{from{transform:rotate(240deg) translateX(215px) rotate(-240deg)}to{transform:rotate(600deg) translateX(215px) rotate(-600deg)}}
@keyframes orb4{from{transform:rotate(60deg) translateX(260px) rotate(-60deg)}to{transform:rotate(420deg) translateX(260px) rotate(-420deg)}}
@keyframes orb5{from{transform:rotate(180deg) translateX(105px) rotate(-180deg)}to{transform:rotate(540deg) translateX(105px) rotate(-540deg)}}

@keyframes blobFloat{0%,100%{transform:translate(-50%,-50%) scale(1) rotate(0deg);opacity:.40}50%{transform:translate(-50%,-50%) scale(1.18) rotate(120deg);opacity:.62}}
@keyframes fadeOutSplash{0%,80%{opacity:1}100%{opacity:0}}
@keyframes progressFill{from{width:0%}to{width:100%}}
@keyframes textPulse{0%,100%{opacity:.55;letter-spacing:4px}50%{opacity:1;letter-spacing:6px}}
@keyframes starTwinkle{0%,100%{opacity:.10}50%{opacity:.65}}

.sp-wrap{
  position:fixed;inset:0;z-index:99999;
  background:#020b18;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  animation:fadeOutSplash 3.6s ease forwards;
  overflow:hidden;
}
.sp-wrap::before{
  content:'';
  position:absolute;inset:0;
  background-image:
    linear-gradient(rgba(59,130,246,0.05) 1px,transparent 1px),
    linear-gradient(90deg,rgba(59,130,246,0.05) 1px,transparent 1px);
  background-size:48px 48px;
  animation:gridPulse 4s ease-in-out infinite;
}

/* nebule background */
.sp-nebula-cool{
  position:absolute; top:48%; left:50%;
  width:900px; height:700px;
  background:radial-gradient(ellipse,
    rgba(59,130,246,0.18) 0%,
    rgba(15,23,42,0.55) 45%,
    transparent 72%);
  animation:nebulaCool 8.5s ease-in-out infinite;
  pointer-events:none;
  filter:blur(.3px);
}
.sp-nebula-warm{
  position:absolute; top:52%; left:52%;
  width:980px; height:780px;
  background:radial-gradient(ellipse,
    rgba(251,191,36,0.22) 0%,
    rgba(245,158,11,0.14) 30%,
    rgba(180,83,9,0.10) 52%,
    transparent 74%);
  animation:nebulaWarm 9.5s ease-in-out infinite;
  pointer-events:none;
  filter:blur(.2px);
}

.sp-star{position:absolute;width:2px;height:2px;background:#fff;border-radius:50%;animation:starTwinkle ease-in-out infinite}
.sp-arena{position:relative;width:580px;height:580px;flex-shrink:0;z-index:2}
.sp-ring{position:absolute;top:50%;left:50%;border-radius:50%}

/* ring con accenti caldi */
.sp-ring-1{
  width:520px;height:520px;margin:-260px 0 0 -260px;
  border:1.5px solid transparent;
  border-top:1.5px solid rgba(245,158,11,0.70);
  border-right:1.5px solid rgba(245,158,11,0.18);
  animation:spin1 3s linear infinite;
}
.sp-ring-2{
  width:410px;height:410px;margin:-205px 0 0 -205px;
  border:1px solid transparent;
  border-top:1px solid rgba(251,191,36,0.55);
  border-left:1px solid rgba(251,191,36,0.20);
  animation:spin2 2s linear infinite;
}
.sp-ring-3{
  width:310px;height:310px;margin:-155px 0 0 -155px;
  border:2px solid transparent;
  border-bottom:2px solid rgba(180,83,9,0.55);
  border-right:2px solid rgba(180,83,9,0.22);
  animation:spin3 4s linear infinite;
}
.sp-ring-4{
  width:220px;height:220px;margin:-110px 0 0 -110px;
  border:1px solid transparent;
  border-top:1px solid rgba(245,158,11,0.35);
  animation:spin1 1.5s linear infinite reverse;
}

/* blob caldo */
.sp-blob{position:absolute;top:50%;left:50%;border-radius:50%;pointer-events:none}
.sp-blob-1{
  width:420px;height:240px;margin:-120px 0 0 -210px;
  background:radial-gradient(ellipse, rgba(251,191,36,0.16) 0%, transparent 72%);
  animation:blobFloat 5s ease-in-out infinite;
}

/* core caldo */
.sp-core{
  position:absolute;top:50%;left:50%;
  width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;
  background:radial-gradient(circle,
    #ffffff 0%,
    #fff7ed 28%,
    rgba(251,191,36,0.95) 55%,
    rgba(245,158,11,0.90) 75%,
    rgba(180,83,9,0.95) 100%);
  animation:corePulse 2s ease-in-out infinite;
  z-index:20;
}

/* orb: più coerenti (caldi + 1 accento blu) */
.sp-orb{position:absolute;top:50%;left:50%;border-radius:50%}
.sp-orb-1{width:10px;height:10px;margin:-5px 0 0 -5px;background:#fbbf24;box-shadow:0 0 12px 4px rgba(251,191,36,0.95);animation:orb1 2.2s linear infinite}
.sp-orb-2{width:8px;height:8px;margin:-4px 0 0 -4px;background:#f59e0b;box-shadow:0 0 10px 3px rgba(245,158,11,0.9);animation:orb2 3.3s linear infinite}
.sp-orb-3{width:7px;height:7px;margin:-3.5px 0 0 -3.5px;background:#b45309;box-shadow:0 0 10px 3px rgba(180,83,9,0.85);animation:orb3 4.4s linear infinite}
.sp-orb-4{width:6px;height:6px;margin:-3px 0 0 -3px;background:#60a5fa;box-shadow:0 0 9px 3px rgba(96,165,250,0.60);animation:orb4 5.5s linear infinite}
.sp-orb-5{width:9px;height:9px;margin:-4.5px 0 0 -4.5px;background:#fde68a;box-shadow:0 0 10px 3px rgba(253,230,138,0.85);animation:orb5 1.8s linear infinite}

/* testo + progress bar (caldi) */
.sp-text{margin-top:-30px;text-align:center;z-index:10}
.sp-label{
  color:#fde68a;
  font-size:0.70rem;
  letter-spacing:4px;
  text-transform:uppercase;
  margin:0 0 14px;
  animation:textPulse 2s ease-in-out infinite;
  text-shadow:0 0 16px rgba(245,158,11,0.28),0 0 34px rgba(180,83,9,0.20);
}
.sp-bar-wrap{
  width:240px;height:2px;
  background:rgba(245,158,11,0.12);
  border-radius:2px;
  margin:0 auto;
  overflow:hidden;
  border:1px solid rgba(245,158,11,0.14);
}
.sp-bar{
  height:100%;
  background:linear-gradient(90deg, rgba(180,83,9,0.85), rgba(251,191,36,0.95), rgba(180,83,9,0.85));
  background-size:200% 100%;
  animation:progressFill 3.2s cubic-bezier(.4,0,.2,1) forwards;
  box-shadow:0 0 10px rgba(251,191,36,0.55);
}
</style>

<div class="sp-wrap">
  <div class="sp-nebula-cool"></div>
  <div class="sp-nebula-warm"></div>

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
    <p class="sp-label">Inizializzazione sistema</p>
    <div class="sp-bar-wrap"><div class="sp-bar"></div></div>
  </div>
</div>
""", unsafe_allow_html=True)

    import time
    time.sleep(3.4)
    st.rerun()


# --------------------------------------------------
# CSS DASHBOARD (warm premium, coerente con login/splash)
# --------------------------------------------------
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
  :root{
    --bg0: #020b18;
    --bg1: #0b1226;
    --bg2: #0f172a;

    --blue:  #60a5fa;
    --blue2: #93c5fd;

    --amber: #fbbf24;
    --amber2:#f59e0b;
    --brown: #b45309;
    --sand:  #fde68a;

    --text:  #cbd5e1;
    --muted: #94a3b8;

    --glass: rgba(15,23,42,0.55);
    --glass2: rgba(2,11,24,0.55);
    --brd: rgba(96,165,250,0.18);
    --brd-warm: rgba(245,158,11,0.18);
  }

  /* ─────────────────────────
     SFONDO APP
     ───────────────────────── */
  .stApp{
    background:
      radial-gradient(1100px 780px at 52% 48%, rgba(245,158,11,0.14) 0%, rgba(2,11,24,0.0) 62%),
      radial-gradient(900px 680px at 50% 45%, rgba(59,130,246,0.12) 0%, rgba(2,11,24,0.0) 60%),
      linear-gradient(135deg, var(--bg1) 0%, #0b1630 45%, var(--bg2) 100%);
    background-attachment: fixed;
  }

  /* ─────────────────────────
     TITOLI
     ───────────────────────── */
  h1{
    color: var(--sand) !important;
    text-shadow: 0 0 18px rgba(245,158,11,0.28), 0 0 34px rgba(180,83,9,0.20);
    font-weight: 900 !important;
    letter-spacing: 2px;
    font-size: 3rem !important;
    margin-bottom: 1rem !important;
  }
  h2{
    color: var(--blue2) !important;
    text-shadow: 0 0 12px rgba(96,165,250,0.22);
    font-weight: 800 !important;
    margin-top: 30px !important;
    letter-spacing: .5px;
  }
  h3{
    color: #e2e8f0 !important;
    text-shadow: 0 0 10px rgba(0,0,0,0.35);
    font-weight: 700 !important;
  }

  /* ─────────────────────────
     KPI / METRIC
     ───────────────────────── */
  [data-testid="stMetricValue"]{
    font-size: 2.55rem !important;
    font-weight: 900 !important;
    color: var(--sand) !important;
    text-shadow: 0 0 18px rgba(245,158,11,0.22), 0 0 30px rgba(180,83,9,0.15);
  }
  [data-testid="stMetricLabel"]{
    font-size: 0.98rem !important;
    font-weight: 700 !important;
    color: var(--blue2) !important;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  [data-testid="metric-container"]{
    background: linear-gradient(135deg, rgba(15,23,42,0.72) 0%, rgba(2,11,24,0.72) 100%);
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 10px 34px rgba(0,0,0,0.55), inset 0 1px 1px rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(245,158,11,0.14);
    transition: all 0.28s ease;
  }
  [data-testid="metric-container"]:hover{
    transform: translateY(-5px);
    box-shadow: 0 14px 44px rgba(245,158,11,0.10), 0 10px 34px rgba(0,0,0,0.55);
    border: 1px solid rgba(245,158,11,0.26);
  }

  /* ─────────────────────────
     TABS
     ───────────────────────── */
  .stTabs [data-baseweb="tab-list"]{
    gap: 8px;
    background: rgba(15,23,42,0.45);
    padding: 10px;
    border-radius: 12px;
    border: 1px solid rgba(96,165,250,0.10);
    backdrop-filter: blur(10px);
  }
  .stTabs [data-baseweb="tab"]{
    background: rgba(2,11,24,0.35);
    border-radius: 10px;
    color: var(--blue2);
    font-weight: 700;
    padding: 12px 22px;
    border: 1px solid rgba(245,158,11,0.10);
    transition: all 0.25s ease;
  }
  .stTabs [data-baseweb="tab"]:hover{
    border-color: rgba(245,158,11,0.26);
    box-shadow: 0 10px 26px rgba(0,0,0,0.35);
  }
  .stTabs [aria-selected="true"]{
    background: linear-gradient(135deg, rgba(245,158,11,0.92) 0%, rgba(180,83,9,0.88) 100%);
    color: #0b1226;
    border: 1px solid rgba(253,230,138,0.35);
    text-shadow: none;
  }

  /* ─────────────────────────
     SIDEBAR
     ───────────────────────── */
  [data-testid="stSidebar"]{
    background: linear-gradient(180deg, rgba(2,11,24,0.95) 0%, rgba(15,23,42,0.92) 100%);
    border-right: 2px solid rgba(245,158,11,0.14);
  }
  [data-testid="stSidebar"] *{
    color: #e2e8f0 !important;
  }

  hr{
    border-color: rgba(245,158,11,0.14) !important;
    margin: 30px 0 !important;
  }

  /* ─────────────────────────
     ALERTS
     ───────────────────────── */
  .alert-critical{
    background: linear-gradient(135deg, rgba(239,68,68,0.18) 0%, rgba(220,38,38,0.26) 100%);
    padding: 20px; border-radius: 16px;
    color: #fecaca; font-weight: 800; font-size: 1.06rem;
    margin: 20px 0;
    box-shadow: 0 10px 34px rgba(239,68,68,0.22);
    border: 1px solid rgba(239,68,68,0.35);
    border-left: 6px solid #ef4444;
  }
  .alert-warning{
    background: linear-gradient(135deg, rgba(251,191,36,0.14) 0%, rgba(245,158,11,0.22) 100%);
    padding: 20px; border-radius: 16px;
    color: #ffedd5; font-weight: 800; font-size: 1.06rem;
    margin: 20px 0;
    box-shadow: 0 10px 34px rgba(245,158,11,0.14);
    border: 1px solid rgba(245,158,11,0.28);
    border-left: 6px solid var(--amber2);
  }
  .alert-success{
    background: linear-gradient(135deg, rgba(34,197,94,0.16) 0%, rgba(22,163,74,0.22) 100%);
    padding: 20px; border-radius: 16px;
    color: #bbf7d0; font-weight: 800; font-size: 1.06rem;
    margin: 20px 0;
    box-shadow: 0 10px 34px rgba(34,197,94,0.14);
    border: 1px solid rgba(34,197,94,0.28);
    border-left: 6px solid #22c55e;
  }
  .alert-info{
    background: linear-gradient(135deg, rgba(59,130,246,0.14) 0%, rgba(37,99,235,0.20) 100%);
    padding: 20px; border-radius: 16px;
    color: #bfdbfe; font-weight: 800; font-size: 1.06rem;
    margin: 20px 0;
    box-shadow: 0 10px 34px rgba(59,130,246,0.14);
    border: 1px solid rgba(59,130,246,0.26);
    border-left: 6px solid #3b82f6;
  }

  /* ─────────────────────────
     PLOTLY / DATAFRAME / EXPANDER
     ───────────────────────── */
  .js-plotly-plot{
    border-radius: 16px;
    box-shadow: 0 10px 34px rgba(0,0,0,0.55);
    background: rgba(15,23,42,0.45) !important;
    border: 1px solid rgba(245,158,11,0.12);
  }
  [data-testid="stDataFrame"]{
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 10px 34px rgba(0,0,0,0.55);
    border: 1px solid rgba(96,165,250,0.12);
  }
  [data-testid="stExpander"]{
    background: rgba(15,23,42,0.45);
    border: 1px solid rgba(245,158,11,0.12);
    border-radius: 12px;
    backdrop-filter: blur(10px);
  }

  p, span, label{ color: var(--text) !important; }

  input, select, textarea{
    background: rgba(2,11,24,0.55) !important;
    color: #fff7ed !important;
    border: 1px solid rgba(245,158,11,0.20) !important;
    border-radius: 10px !important;
  }

  /* ─────────────────────────
     BUTTONS
     ───────────────────────── */
  button{
    background: linear-gradient(135deg, rgba(245,158,11,0.95) 0%, rgba(180,83,9,0.92) 100%) !important;
    color: #0b1226 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 10px 26px rgba(0,0,0,0.35);
  }
  button:hover{
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 34px rgba(245,158,11,0.16), 0 10px 26px rgba(0,0,0,0.35) !important;
    filter: brightness(1.05);
  }

  .stDownloadButton button{
    background: linear-gradient(135deg, rgba(34,197,94,0.92) 0%, rgba(22,163,74,0.90) 100%) !important;
    color: #052e16 !important;
  }

  /* ─────────────────────────
     CARDS CUSTOM
     ───────────────────────── */
  .info-box{
    background: rgba(15,23,42,0.50);
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 20px;
    border: 1px solid rgba(245,158,11,0.12);
    backdrop-filter: blur(10px);
  }

  .insight-card{
    background: linear-gradient(135deg, rgba(245,158,11,0.10) 0%, rgba(59,130,246,0.10) 100%);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(245,158,11,0.18);
    margin: 15px 0;
    box-shadow: 0 10px 34px rgba(0,0,0,0.40);
  }
  .insight-card h4{
    color: var(--sand) !important;
    margin-bottom: 10px !important;
    text-shadow: 0 0 16px rgba(245,158,11,0.22);
  }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# TEMPLATE PLOTLY GLOBALE
# --------------------------------------------------
PLOTLY_TEMPLATE = {
    'plot_bgcolor':  'rgba(15, 23, 42, 0.8)',
    'paper_bgcolor': 'rgba(15, 23, 42, 0.5)',
    'font': {'color': '#cbd5e1', 'family': 'Arial, sans-serif'},
    'xaxis': {'gridcolor': 'rgba(96,165,250,0.1)', 'linecolor': 'rgba(96,165,250,0.3)', 'zerolinecolor': 'rgba(96,165,250,0.3)'},
    'yaxis': {'gridcolor': 'rgba(96,165,250,0.1)', 'linecolor': 'rgba(96,165,250,0.3)', 'zerolinecolor': 'rgba(96,165,250,0.3)'},
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
    st.sidebar.success(f"✅ DB connesso\n{db_time.strftime('%d/%m/%Y %H:%M')}")
except Exception as e:
    st.sidebar.error(f"❌ Errore DB: {e}")
    st.stop()


# --------------------------------------------------
# CARICAMENTO DATI
# --------------------------------------------------
@st.cache_data(ttl=600)
def load_staffing() -> pd.DataFrame:
    query = """
        SELECT
            giorno, tipo_giorno, deposito, totale_autisti,
            assenze_programmate, assenze_previste, infortuni, malattie,
            legge_104, altre_assenze, congedo_parentale, permessi_vari,
            turni_richiesti, disponibili_netti, gap
        FROM v_staffing
        ORDER BY giorno, deposito;
    """
    return pd.read_sql(query, get_conn())


@st.cache_data(ttl=600)
def load_depositi_stats() -> pd.DataFrame:
    query = """
        SELECT deposito, giorni_attivi, dipendenti_medi_giorno
        FROM v_depositi_organico_medio
        ORDER BY deposito;
    """
    return pd.read_sql(query, get_conn())


@st.cache_data(ttl=600)
def load_turni_calendario() -> pd.DataFrame:
    query = """
        SELECT
            tg.data       AS giorno,
            tg.deposito,
            COUNT(tg.id)  AS turni
        FROM turni_giornalieri tg
        GROUP BY tg.data, tg.deposito
        ORDER BY tg.data, tg.deposito;
    """
    return pd.read_sql(query, get_conn())


@st.cache_data(ttl=600)
def load_copertura() -> pd.DataFrame:
    query = """
        WITH
        forza AS (
            SELECT
                r.data                              AS giorno,
                r.deposito,
                COUNT(DISTINCT r.matricola)         AS persone_in_forza,
                COUNT(*) FILTER (
                    WHERE r.turno IS NOT NULL AND TRIM(r.turno) <> ''
                )                                   AS assenze_nominali
            FROM roster r
            GROUP BY r.data, r.deposito
        ),
        turni AS (
            SELECT data AS giorno, deposito, COUNT(*) AS turni_richiesti
            FROM turni_giornalieri
            GROUP BY data, deposito
        ),
        ass AS (
            SELECT
                c.data                              AS giorno,
                a.deposito,
                ROUND(
                    COALESCE(a.infortuni,0) +
                    COALESCE(a.malattie,0) +
                    COALESCE(a.legge_104,0) +
                    COALESCE(a.altre_assenze,0) +
                    COALESCE(a.congedo_parentale,0) +
                    COALESCE(a.permessi_vari,0)
                )::int                              AS assenze_statistiche
            FROM assenze a
            JOIN calendar c ON c.daytype = a.daytype
        )
        SELECT
            f.giorno,
            f.deposito,
            f.persone_in_forza,
            COALESCE(t.turni_richiesti,    0)       AS turni_richiesti,
            f.assenze_nominali,
            COALESCE(a.assenze_statistiche, 0)      AS assenze_statistiche,
            f.persone_in_forza
            - COALESCE(t.turni_richiesti,    0)
            - f.assenze_nominali
            - COALESCE(a.assenze_statistiche, 0)    AS gap
        FROM forza f
        LEFT JOIN turni t USING (giorno, deposito)
        LEFT JOIN ass   a USING (giorno, deposito)
        ORDER BY f.giorno, f.deposito;
    """
    return pd.read_sql(query, get_conn())

# --- caricamento iniziale ---
try:
    df_raw      = load_staffing()
    df_raw["giorno"] = pd.to_datetime(df_raw["giorno"])
    df_depositi = load_depositi_stats()

    df_raw      = df_raw[df_raw["deposito"] != "depbelvede"].copy()
    df_depositi = df_depositi[df_depositi["deposito"] != "depbelvede"].copy()
except Exception as e:
    st.error(f"❌ Errore caricamento staffing: {e}")
    st.stop()

try:
    df_turni_cal = load_turni_calendario()
    df_turni_cal["giorno"] = pd.to_datetime(df_turni_cal["giorno"])
    turni_cal_ok = len(df_turni_cal) > 0
    if not turni_cal_ok:
        st.sidebar.warning("⚠️ Turni: query OK ma 0 righe restituite")
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
# UTILITY FUNCTIONS
# --------------------------------------------------
def categorizza_tipo_giorno(tipo: str) -> str:
    t = (tipo or "").strip().lower()
    if t in ['lunedi', 'martedi', 'mercoledi', 'giovedi', 'venerdi']:
        return 'Lu-Ve'
    elif t == 'sabato':
        return 'Sabato'
    elif t == 'domenica':
        return 'Domenica'
    return tipo


def applica_ferie_10gg(df_in: pd.DataFrame) -> pd.DataFrame:
    df = df_in.copy()
    required = {"giorno", "deposito", "totale_autisti", "assenze_previste", "disponibili_netti", "gap"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Mancano colonne: {missing}")

    df["deposito_norm"] = df["deposito"].astype(str).str.strip().str.lower()
    df["ferie_extra"]   = 0.0

    mask_ancona = df["deposito_norm"] == "ancona"
    df.loc[mask_ancona, "ferie_extra"] += 5.0

    mask_eligible = ~df["deposito_norm"].isin(["ancona", "moie"])
    eligible = df[mask_eligible].copy()
    if not eligible.empty:
        eligible["peso"]     = eligible["totale_autisti"].clip(lower=0)
        sum_pesi             = eligible.groupby("giorno")["peso"].transform("sum")
        eligible["quota"]    = np.where(sum_pesi > 0, 5.0 * eligible["peso"] / sum_pesi, 0.0)
        df.loc[eligible.index, "ferie_extra"] += eligible["quota"].values

    df["assenze_previste_adj"]   = df["assenze_previste"] + df["ferie_extra"]
    df["disponibili_netti_adj"]  = (df["disponibili_netti"] - df["ferie_extra"]).clip(lower=0)
    df["gap_adj"]                = df["gap"] - df["ferie_extra"]
    df.drop(columns=["deposito_norm"], inplace=True)
    return df


df_raw["categoria_giorno"] = df_raw["tipo_giorno"].apply(categorizza_tipo_giorno)


# --------------------------------------------------
# SIDEBAR – FILTRI
# --------------------------------------------------
st.sidebar.markdown("## <i class='fas fa-sliders-h'></i> CONTROLLI", unsafe_allow_html=True)
st.sidebar.markdown("---")

modalita = st.sidebar.radio(
    "📊 Modalità Vista",
    ["Dashboard Completa", "Analisi Comparativa", "Report Esportabile"],
    help="Scegli come visualizzare i dati"
)
st.sidebar.markdown("---")

depositi_lista = sorted(df_raw["deposito"].unique())
deposito_sel   = st.sidebar.multiselect("📍 DEPOSITI", depositi_lista, default=depositi_lista)

min_date  = df_raw["giorno"].min().date()
max_date  = df_raw["giorno"].max().date()
date_range = st.sidebar.date_input("📅 PERIODO", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)
st.sidebar.markdown("---")

soglia_gap = st.sidebar.slider("⚠️ SOGLIA CRITICA", min_value=-50, max_value=0, value=-10,
                               help="Gap sotto questa soglia è critico")

ferie_10 = st.sidebar.checkbox(
    "✅ Con 10 giornate di ferie (5 Ancona + 5 altri depositi)",
    value=False,
    help="Simula +10 assenze/giorno distribuite proporzionalmente"
)

with st.sidebar.expander("🔧 Filtri Avanzati"):
    show_forecast = st.sidebar.checkbox("📈 Mostra Previsioni", value=True)
    show_insights = st.sidebar.checkbox("💡 Mostra Insights AI", value=True)
    min_gap_filter = st.sidebar.number_input("Gap Minimo", value=-100)
    max_gap_filter = st.sidebar.number_input("Gap Massimo", value=100)

st.sidebar.markdown("---")

# --- applicazione filtri su staffing ---
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
        st.error(f"❌ Errore ferie: {e}")
        st.stop()

df_filtered = df_filtered[
    (df_filtered["gap"] >= min_gap_filter) &
    (df_filtered["gap"] <= max_gap_filter)
].copy()

# --- filtro df_copertura ---
if len(df_copertura) > 0:
    if ferie_10:
        df_cop = df_copertura.copy()
        df_cop["deposito_norm"] = df_cop["deposito"].str.strip().str.lower()
        df_cop["ferie_extra"] = 0.0
        df_cop.loc[df_cop["deposito_norm"] == "ancona", "ferie_extra"] += 5.0
        mask_elig = ~df_cop["deposito_norm"].isin(["ancona", "moie"])
        elig = df_cop[mask_elig].copy()
        if not elig.empty:
            elig["peso"] = elig["persone_in_forza"].clip(lower=0)
            sum_p = elig.groupby("giorno")["peso"].transform("sum")
            elig["quota"] = np.where(sum_p > 0, 5.0 * elig["peso"] / sum_p, 0.0)
            df_cop.loc[elig.index, "ferie_extra"] += elig["quota"].values
        df_cop["assenze_nominali"]    = df_cop["assenze_nominali"] + df_cop["ferie_extra"]
        df_cop["gap"]                 = (
            df_cop["persone_in_forza"]
            - df_cop["turni_richiesti"]
            - df_cop["assenze_nominali"]
            - df_cop["assenze_statistiche"]
        )
        df_cop.drop(columns=["deposito_norm", "ferie_extra"], inplace=True)
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
# HEADER PREMIUM
# --------------------------------------------------
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h1><i class='fas fa-chart-line'></i> ESTATE 2026</h1>
    <h1 style='font-size: 2rem; margin-top: -1rem;'>Analytics Dashboard Premium</h1>
</div>
""", unsafe_allow_html=True)

if len(date_range) == 2:
    ferie_badge = " | 🏖️ CON SIMULAZIONE FERIE" if ferie_10 else ""
    st.markdown(
        f"<p style='text-align:center;color:#93c5fd;font-size:1.2rem;font-weight:600;'>"
        f"<i class='far fa-calendar-alt'></i> {date_range[0].strftime('%d/%m/%Y')} → {date_range[1].strftime('%d/%m/%Y')} | "
        f"<i class='fas fa-building'></i> {len(deposito_sel)} Depositi | "
        f"<i class='fas fa-database'></i> {len(df_filtered):,} Records{ferie_badge}</p>",
        unsafe_allow_html=True
    )

st.markdown("---")


# --------------------------------------------------
# ██ KPI CARDS — MODIFICATO ██
# --------------------------------------------------
st.markdown("### <i class='fas fa-chart-line'></i> KEY PERFORMANCE INDICATORS", unsafe_allow_html=True)

if len(df_filtered) > 0:
    totale_dipendenti         = df_depositi[df_depositi["deposito"].isin(deposito_sel)]["dipendenti_medi_giorno"].sum()
    gap_medio_giorno          = df_filtered.groupby("giorno")["gap"].sum().mean()
    media_turni_giorno        = df_filtered.groupby("giorno")["turni_richiesti"].sum().mean()
    gap_pct_medio             = (gap_medio_giorno / media_turni_giorno * 100) if media_turni_giorno > 0 else 0
    gap_per_giorno            = df_filtered.groupby("giorno")["gap"].sum()
    giorni_analizzati         = df_filtered["giorno"].nunique()
    giorni_critici_count      = (gap_per_giorno < soglia_gap).sum()
    pct_critici               = (giorni_critici_count / giorni_analizzati * 100) if giorni_analizzati > 0 else 0
    totale_assenze            = df_filtered["assenze_previste"].sum()
    tasso_assenze             = (totale_assenze / (totale_dipendenti * giorni_analizzati) * 100) \
                                if (totale_dipendenti > 0 and giorni_analizzati > 0) else 0

    # Totale turni Lu-Ve: somma turni_richiesti nei giorni feriali del periodo filtrato
    turni_luv_totale = df_filtered[
        df_filtered["tipo_giorno"].str.lower().isin(
            ['lunedi', 'martedi', 'mercoledi', 'giovedi', 'venerdi']
        )
    ].groupby("giorno")["turni_richiesti"].sum().mean()
    turni_luv_totale = turni_luv_totale if not np.isnan(turni_luv_totale) else 0

    # 4 KPI: Autisti · Totale Turni Lu-Ve · Gap Medio · Giorni Critici
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("👤 Autisti", f"{int(totale_dipendenti):,}")
    with kpi2:
        st.metric(
            "🚌 Turni/giorno Lu-Ve",
            f"{int(turni_luv_totale):,}",
            help="Media dei turni richiesti in un giorno feriale (Lu-Ve) nel periodo selezionato"
        )
    with kpi3:
        st.metric(
            "⚖️ Gap Medio/giorno",
            f"{int(gap_medio_giorno):,}",
            delta=f"{gap_pct_medio:.1f}%",
            delta_color="normal" if gap_medio_giorno >= 0 else "inverse"
        )
    with kpi4:
        st.metric(
            "🚨 Giorni Critici",
            f"{giorni_critici_count}/{giorni_analizzati}",
            delta=f"{pct_critici:.0f}%",
            delta_color="inverse"
        )

st.markdown("---")


# --------------------------------------------------
# AI INSIGHTS
# --------------------------------------------------
if show_insights and len(df_filtered) > 0:
    st.markdown("### <i class='fas fa-brain'></i> AI INSIGHTS", unsafe_allow_html=True)
    ic1, ic2, ic3 = st.columns(3)

    with ic1:
        by_dep    = df_filtered.groupby("deposito")["gap"].mean()
        worst_dep = by_dep.idxmin()
        st.markdown(f"""
        <div class='insight-card'>
            <h4><i class='fas fa-exclamation-triangle'></i> Deposito Critico</h4>
            <p style='font-size:1.1rem;margin:0;'><b>{worst_dep}</b> — gap medio: <b>{by_dep.min():.1f}</b></p>
            <p style='font-size:0.9rem;color:#fed7aa;margin-top:10px;'>💡 Considera redistribuzione turni o assunzioni</p>
        </div>""", unsafe_allow_html=True)

    with ic2:
        by_cat    = df_filtered.groupby("categoria_giorno")["gap"].mean()
        worst_cat = by_cat.idxmin()
        st.markdown(f"""
        <div class='insight-card'>
            <h4><i class='fas fa-calendar-times'></i> Giorno Critico</h4>
            <p style='font-size:1.1rem;margin:0;'><b>{worst_cat}</b> — gap medio: <b>{by_cat.min():.1f}</b></p>
            <p style='font-size:0.9rem;color:#fed7aa;margin-top:10px;'>💡 Pianifica turni extra per questi giorni</p>
        </div>""", unsafe_allow_html=True)

    with ic3:
        assenze_trend = df_filtered.groupby("giorno")["assenze_previste"].sum()
        if len(assenze_trend) > 1:
            crescente     = assenze_trend.iloc[-1] > assenze_trend.iloc[0]
            trend_txt     = "crescente" if crescente else "decrescente"
            trend_icon    = "📈" if crescente else "📉"
        else:
            trend_txt, trend_icon = "stabile", "➡️"
        st.markdown(f"""
        <div class='insight-card'>
            <h4><i class='fas fa-chart-line'></i> Trend Assenze</h4>
            <p style='font-size:1.1rem;margin:0;'>{trend_icon} Trend <b>{trend_txt}</b></p>
            <p style='font-size:0.9rem;color:#bfdbfe;margin-top:10px;'>💡 Monitora evoluzione settimanale</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")


# --------------------------------------------------
# AGGREGATI PER DEPOSITO
# --------------------------------------------------
if len(df_filtered) > 0:
    by_deposito = df_filtered.groupby("deposito").agg(
        turni_richiesti=("turni_richiesti", "sum"),
        disponibili_netti=("disponibili_netti", "sum"),
        gap=("gap", "sum"),
        assenze_previste=("assenze_previste", "sum"),
    ).reset_index()
    by_deposito = by_deposito.merge(df_depositi, on="deposito", how="left")
    giorni_per_dep = df_filtered.groupby("deposito")["giorno"].nunique().rename("giorni_periodo")
    by_deposito    = by_deposito.merge(giorni_per_dep, left_on="deposito", right_index=True)
    by_deposito["media_gap_giorno"]  = (by_deposito["gap"] / by_deposito["giorni_periodo"]).round(1)
    by_deposito["tasso_copertura_%"] = (
        by_deposito["disponibili_netti"] / by_deposito["turni_richiesti"] * 100
    ).fillna(0).round(1)
    by_deposito = by_deposito.sort_values("media_gap_giorno")
else:
    by_deposito = pd.DataFrame()


# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📈 Analisi & Assenze",
    "🚌 Turni Calendario",
    "🎯 Depositi",
    "📥 Export",
])


# ══════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════
with tab1:
    if len(df_filtered) > 0:
        st.markdown("#### <i class='fas fa-users'></i> Copertura del Servizio — Persone per Giorno", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#93c5fd;font-size:0.9rem;'>"
            "Ogni barra mostra come vengono distribuite le <b>persone in forza</b> quel giorno. "
            "Il tratto rosso indica quanti turni devono essere coperti. "
            "<span style='color:#22c55e;'>Verde</span> = persone libere disponibili &nbsp;|&nbsp; "
            "<span style='color:#ef4444;'>Rosso</span> = deficit.</p>",
            unsafe_allow_html=True
        )

        if len(df_copertura_filtered) > 0:
            cop = df_copertura_filtered.groupby("giorno").agg(
                persone_in_forza    = ("persone_in_forza",     "sum"),
                turni_richiesti     = ("turni_richiesti",      "sum"),
                assenze_nominali    = ("assenze_nominali",     "sum"),
                assenze_statistiche = ("assenze_statistiche",  "sum"),
                gap                 = ("gap",                  "sum"),
            ).reset_index()

            cop["totale_assenze"] = cop["assenze_nominali"] + cop["assenze_statistiche"]
            cop["buffer"]  = cop["gap"].clip(lower=0)
            cop["deficit"] = cop["gap"].clip(upper=0).abs()

            giorni_ok      = int((cop["gap"] >= 0).sum())
            giorni_allarme = int((cop["gap"] <  0).sum())
            gap_medio      = cop["gap"].mean()
            gap_min        = cop["gap"].min()

            kc1, kc2, kc3, kc4 = st.columns(4)
            with kc1:
                st.metric("👥 Persone in forza (media/gg)", f"{cop['persone_in_forza'].mean():.0f}")
            with kc2:
                st.metric("✅ Giorni in copertura", f"{giorni_ok}")
            with kc3:
                st.metric("🚨 Giorni in deficit", f"{giorni_allarme}")
            with kc4:
                st.metric("📉 Gap medio/giorno", f"{gap_medio:.1f}", delta=f"min: {gap_min:.0f}")

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            fig_cop = make_subplots(
                rows=2, cols=1,
                row_heights=[0.70, 0.30],
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(
                    "Come vengono utilizzate le persone in forza ogni giorno",
                    "Buffer disponibile (▲) / Deficit (▼)"
                ),
            )

            fig_cop.add_trace(go.Bar(
                x=cop["giorno"], y=cop["turni_richiesti"],
                name="Turni da coprire",
                marker_color="rgba(100,116,139,0.80)",
                hovertemplate="<b>Turni da coprire</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"
            ), row=1, col=1)

            fig_cop.add_trace(go.Bar(
                x=cop["giorno"], y=cop["assenze_nominali"],
                name="Assenze roster (FP / R / PS …)",
                marker_color="rgba(71,85,105,0.85)",
                hovertemplate="<b>Assenze roster</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"
            ), row=1, col=1)

            fig_cop.add_trace(go.Bar(
                x=cop["giorno"], y=cop["assenze_statistiche"],
                name="Assenze storiche (infort./malattie…)",
                marker_color="rgba(51,65,85,0.90)",
                hovertemplate="<b>Assenze storiche</b><br>%{x|%d/%m/%Y}: <b>%{y:.0f}</b><extra></extra>"
            ), row=1, col=1)

            buf_colors = [
                "rgba(34,197,94,0.85)" if g >= 0 else "rgba(220,38,38,0.90)"
                for g in cop["gap"]
            ]
            fig_cop.add_trace(go.Bar(
                x=cop["giorno"],
                y=cop["gap"],
                name="Buffer / Deficit",
                marker=dict(color=buf_colors, line=dict(width=0.8, color="rgba(255,255,255,0.15)")),
                text=[f"<b>{int(g)}</b>" if g < 0 else "" for g in cop["gap"]],
                textposition="outside",
                textfont=dict(size=11, color="#fca5a5"),
                hovertemplate=(
                    "<b>%{x|%d/%m/%Y}</b><br>"
                    "Buffer/Deficit: <b>%{y}</b><br>"
                    "<i>🟢 positivo = margine libero · 🔴 negativo = DEFICIT</i>"
                    "<extra></extra>"
                )
            ), row=1, col=1)

            fig_cop.add_trace(go.Scatter(
                x=cop["giorno"], y=cop["persone_in_forza"],
                name="Persone in forza",
                mode="lines",
                line=dict(color="#94a3b8", width=2, dash="dot"),
                hovertemplate="<b>Persone in forza</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"
            ), row=1, col=1)

            gap_colors = [
                "rgba(34,197,94,0.85)" if g >= 0 else "rgba(220,38,38,0.90)"
                for g in cop["gap"]
            ]
            fig_cop.add_trace(go.Bar(
                x=cop["giorno"], y=cop["gap"],
                name="Gap",
                marker=dict(color=gap_colors, line=dict(width=0.5, color="rgba(255,255,255,0.1)")),
                text=[f"<b>{int(g)}</b>" for g in cop["gap"]],
                textposition="outside",
                textfont=dict(size=9, color="#cbd5e1"),
                showlegend=False,
                hovertemplate=(
                    "<b>%{x|%d/%m/%Y}</b><br>"
                    "Gap: <b>%{y}</b><br>"
                    "<i>🟢 buffer · 🔴 DEFICIT</i>"
                    "<extra></extra>"
                )
            ), row=2, col=1)

            fig_cop.add_hline(y=0, line_dash="solid",
                              line_color="rgba(255,255,255,0.5)", line_width=1.5,
                              row=2, col=1)
            if soglia_gap < 0:
                fig_cop.add_hline(
                    y=soglia_gap, line_dash="dash", line_color="#dc2626", line_width=2,
                    annotation_text=f"Soglia critica ({soglia_gap})",
                    annotation_font=dict(color="#dc2626", size=11),
                    annotation_position="top left",
                    row=2, col=1
                )

            fig_cop.update_layout(
                barmode="stack",
                height=700,
                hovermode="x unified",
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=11),
                    bgcolor="rgba(15,23,42,0.7)",
                    bordercolor="rgba(96,165,250,0.2)", borderwidth=1,
                ),
                plot_bgcolor="rgba(15,23,42,0.85)",
                paper_bgcolor="rgba(15,23,42,0.0)",
                font=dict(color="#cbd5e1", family="Arial, sans-serif"),
                margin=dict(t=60, b=20, l=10, r=10),
            )
            fig_cop.update_xaxes(
                tickformat="%d/%m", tickangle=-45,
                gridcolor="rgba(96,165,250,0.08)",
                linecolor="rgba(96,165,250,0.2)",
                showgrid=True,
            )
            fig_cop.update_yaxes(
                gridcolor="rgba(96,165,250,0.08)",
                linecolor="rgba(96,165,250,0.2)",
                zeroline=False,
            )
            fig_cop.update_yaxes(title_text="Persone", row=1, col=1)
            fig_cop.update_yaxes(title_text="Gap", row=2, col=1)

            st.plotly_chart(fig_cop, use_container_width=True, key="pc_main_cop")

            c1, c2, c3, c4, c5 = st.columns(5)
            cards = [
                (c1, "#64748b", "rgba(100,116,139,0.12)", "▪ Turni da coprire",
                 "Turni che devono essere garantiti ogni giorno"),
                (c2, "#475569", "rgba(71,85,105,0.15)", "▪ Assenze roster",
                 "FP, R, PS, AP, PADm, NF e tutti i codici turno assegnati"),
                (c3, "#334155", "rgba(51,65,85,0.20)", "▪ Assenze storiche",
                 "Infortuni, malattie, L.104, permessi (medie anni precedenti)"),
                (c4, "#22c55e", "rgba(34,197,94,0.15)", "🟢 Buffer",
                 "Verde = persone libere · Rosso = DEFICIT"),
                (c5, "#94a3b8", "rgba(148,163,184,0.05)", "— Persone in forza",
                 "Linea tratteggiata = organico totale del giorno"),
            ]
            for col, border, bg, title, desc in cards:
                with col:
                    st.markdown(
                        f"<div style='background:{bg};border-left:4px solid {border};"
                        f"border-radius:8px;padding:10px 12px;min-height:72px;'>"
                        f"<span style='color:#e2e8f0;font-size:0.78rem;font-weight:700;'>{title}</span><br>"
                        f"<span style='color:#94a3b8;font-size:0.75rem;'>{desc}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

        else:
            st.info("Dati copertura non disponibili per i filtri selezionati.")

        with st.expander("📊 Statistiche aggiuntive — Gauge Gap % e Distribuzione Assenze"):
            eg1, eg2 = st.columns(2)
            with eg1:
                st.markdown("##### Stato Copertura (Gap %)")
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=gap_pct_medio,
                    title={'text': "Gap % Medio", 'font': {'size': 15, 'color': '#93c5fd'}},
                    delta={'reference': 0, 'suffix': '%'},
                    number={'suffix': '%', 'font': {'size': 30, 'color': '#60a5fa'}},
                    gauge={
                        'axis': {'range': [-20, 20], 'tickcolor': "#60a5fa"},
                        'bar': {'color': "#3b82f6", 'thickness': 0.7},
                        'bgcolor': "rgba(15,23,42,0.8)", 'borderwidth': 3, 'bordercolor': "#60a5fa",
                        'steps': [
                            {'range': [-20, -10], 'color': 'rgba(220,38,38,0.3)'},
                            {'range': [-10,   0], 'color': 'rgba(251,146,60,0.3)'},
                            {'range': [  0,  10], 'color': 'rgba(34,197,94,0.3)'},
                            {'range': [ 10,  20], 'color': 'rgba(16,185,129,0.3)'},
                        ],
                        'threshold': {
                            'line': {'color': "#ef4444", 'width': 4}, 'thickness': 0.75,
                            'value': (soglia_gap / media_turni_giorno * 100) if media_turni_giorno > 0 else 0
                        }
                    }
                ))
                fig_gauge.update_layout(height=280, paper_bgcolor='rgba(15,23,42,0.5)',
                                        margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_gauge, use_container_width=True, key="pc_2")
            with eg2:
                st.markdown("##### Distribuzione Assenze Storiche")
                ab = pd.DataFrame({
                    'Tipo':   ['Infortuni', 'Malattie', 'L.104', 'Congedi', 'Permessi', 'Altro'],
                    'Totale': [int(df_filtered[c].sum()) for c in
                               ['infortuni', 'malattie', 'legge_104', 'congedo_parentale', 'permessi_vari', 'altre_assenze']]
                })
                ab = ab[ab['Totale'] > 0]
                if len(ab) > 0:
                    fig_pie = go.Figure(go.Pie(
                        labels=ab['Tipo'], values=ab['Totale'], hole=.5,
                        marker=dict(colors=['#64748b','#78716c','#6b7280','#71717a','#737373','#57534e']),
                        textinfo='label+percent'
                    ))
                    fig_pie.update_layout(height=280, showlegend=False,
                                          paper_bgcolor='rgba(15,23,42,0.5)',
                                          margin=dict(l=0, r=0, t=0, b=0))
                    st.plotly_chart(fig_pie, use_container_width=True, key="pc_3")

        st.markdown("---")
        st.markdown("#### <i class='fas fa-fire'></i> Heatmap Criticità per Deposito", unsafe_allow_html=True)
        pivot_gap = df_filtered.pivot_table(
            values='gap', index='deposito',
            columns=df_filtered['giorno'].dt.strftime('%d/%m'),
            aggfunc='sum', fill_value=0
        )
        if len(pivot_gap) > 0:
            fig_heat = go.Figure(go.Heatmap(
                z=pivot_gap.values, x=pivot_gap.columns, y=pivot_gap.index,
                colorscale=[[0,'#7f1d1d'],[0.3,'#dc2626'],[0.45,'#fb923c'],
                             [0.5,'#fef3c7'],[0.55,'#86efac'],[0.7,'#22c55e'],[1,'#14532d']],
                zmid=0, text=pivot_gap.values, texttemplate='%{text:.0f}',
                colorbar=dict(title="Gap")
            ))
            fig_heat.update_layout(height=max(300, len(pivot_gap) * 40), **PLOTLY_TEMPLATE)
            st.plotly_chart(fig_heat, use_container_width=True, key="pc_4")
    else:
        st.info("Nessun dato per i filtri selezionati.")


# ══════════════════════════════════════════════════
# TAB 2 — ANALISI & ASSENZE
# ══════════════════════════════════════════════════
with tab2:
    if len(df_filtered) == 0:
        st.info("Nessun dato per i filtri selezionati.")
    else:
        # ██ Rimosso sotto-tab "Distribuzione Gap" — ora 3 sotto-tab ██
        st2_a, st2_b, st2_c = st.tabs([
            "📉 Gap & Waterfall",
            "🏖️ Ferie & Riposi",
            "🤒 Assenze Complete",
        ])

        # ─────────────────────────────────────────────
        # SOTTO-TAB A — GAP & WATERFALL  ← MODIFICATO
        # ─────────────────────────────────────────────
        with st2_a:

            # ██ WATERFALL — logica più chiara con subtotale "Disponibili Netti" ██
            st.markdown("#### <i class='fas fa-water'></i> Composizione Gap Medio Giornaliero", unsafe_allow_html=True)
            st.markdown(
                "<p style='color:#93c5fd;font-size:0.9rem;'>"
                "Il grafico mostra <b>come si arriva al gap partendo dagli autisti</b>: "
                "prima si sottraggono le assenze previste → si ottengono i <b>Disponibili Netti</b>, "
                "poi si sottraggono i turni da coprire → si ottiene il <b>Gap/Buffer</b> finale.</p>",
                unsafe_allow_html=True
            )

            autisti_medio      = df_filtered.groupby("giorno")["totale_autisti"].sum().mean()
            assenze_medie      = df_filtered.groupby("giorno")["assenze_previste"].sum().mean()
            turni_medi         = df_filtered.groupby("giorno")["turni_richiesti"].sum().mean()
            disponibili_medi   = autisti_medio - assenze_medie          # subtotale intermedio
            gap_medio_wf       = disponibili_medi - turni_medi           # = gap finale

            # Colore del totale finale: verde se >= 0, rosso se negativo
            colore_gap = "#22c55e" if gap_medio_wf >= 0 else "#ef4444"

            fig_wf = go.Figure(go.Waterfall(
                orientation="v",
                measure=["absolute", "relative", "relative", "total"],
                x=[
                    "👥 Autisti in Forza",
                    "➖ Assenze Previste",
                    "➖ Turni da Coprire",
                    "= Gap / Buffer",
                ],
                y=[autisti_medio, -assenze_medie, -turni_medi, 0],
                text=[
                    f"<b>{autisti_medio:.0f}</b>",
                    f"<b>−{assenze_medie:.0f}</b>",
                    f"<b>−{turni_medi:.0f}</b>",
                    f"<b>{'+' if gap_medio_wf >= 0 else ''}{gap_medio_wf:.0f}</b>",
                ],
                textposition="outside",
                textfont=dict(size=13, color="#e2e8f0"),
                connector={"line": {"color": "rgba(96,165,250,0.4)", "width": 1.5, "dash": "dot"}},
                increasing={"marker": {"color": "#22c55e", "line": {"color": "#16a34a", "width": 1}}},
                decreasing={"marker": {"color": "#ef4444", "line": {"color": "#dc2626", "width": 1}}},
                totals={"marker": {"color": colore_gap, "line": {"color": "rgba(255,255,255,0.3)", "width": 1}}},
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Valore: <b>%{y:.1f}</b> persone<br>"
                    "<extra></extra>"
                ),
            ))

            # Annotazione: Disponibili Netti (subtotale dopo assenze)
            fig_wf.add_annotation(
                x="➖ Assenze Previste",
                y=disponibili_medi,
                text=f"Disponibili Netti: <b>{disponibili_medi:.0f}</b>",
                showarrow=True,
                arrowhead=2,
                ax=0, ay=-35,
                font=dict(size=12, color="#93c5fd"),
                bgcolor="rgba(15,23,42,0.85)",
                bordercolor="rgba(59,130,246,0.6)",
                borderwidth=1,
                borderpad=6,
            )

            # Linea di riferimento a zero
            fig_wf.add_hline(
                y=0,
                line_dash="dash",
                line_color="rgba(255,255,255,0.3)",
                line_width=1,
            )

            # Annotazione esplicativa sul gap finale
            annotation_color = "#22c55e" if gap_medio_wf >= 0 else "#ef4444"
            annotation_text  = (
                f"✅ Buffer: +{gap_medio_wf:.0f}" if gap_medio_wf >= 0
                else f"🚨 Deficit: {gap_medio_wf:.0f}"
            )
            fig_wf.add_annotation(
                x="= Gap / Buffer",
                y=gap_medio_wf + (8 if gap_medio_wf >= 0 else -8),
                text=annotation_text,
                showarrow=False,
                font=dict(size=12, color=annotation_color, family="Arial Black"),
                bgcolor="rgba(15,23,42,0.85)",
                bordercolor=annotation_color,
                borderwidth=1,
                borderpad=6,
            )

            fig_wf.update_layout(
                height=480,
                showlegend=False,
                plot_bgcolor="rgba(15,23,42,0.8)",
                paper_bgcolor="rgba(15,23,42,0.5)",
                font=dict(color="#cbd5e1", family="Arial, sans-serif"),
                margin=dict(t=30, b=60, l=20, r=20),
                xaxis=dict(
                    gridcolor="rgba(96,165,250,0.08)",
                    linecolor="rgba(96,165,250,0.2)",
                    tickfont=dict(size=12),
                ),
                yaxis=dict(
                    title="Persone (media/giorno)",
                    gridcolor="rgba(96,165,250,0.1)",
                    linecolor="rgba(96,165,250,0.2)",
                    zeroline=True,
                    zerolinecolor="rgba(255,255,255,0.25)",
                    zerolinewidth=1.5,
                ),
            )
            st.plotly_chart(fig_wf, use_container_width=True, key="pc_5")

            # 3 KPI esplicativi sotto il waterfall
            wk1, wk2, wk3 = st.columns(3)
            with wk1:
                st.metric(
                    "👥 Autisti medi/giorno",
                    f"{autisti_medio:.0f}",
                    help="Organico medio giornaliero nei depositi selezionati"
                )
            with wk2:
                st.metric(
                    "🏥 Assenze previste/giorno",
                    f"{assenze_medie:.0f}",
                    delta=f"−{assenze_medie/autisti_medio*100:.1f}% dell'organico" if autisti_medio > 0 else "",
                    delta_color="inverse",
                    help="Media giornaliera di assenze statistiche (malattie, infortuni, L.104, permessi…)"
                )
            with wk3:
                st.metric(
                    "🚌 Turni da coprire/giorno",
                    f"{turni_medi:.0f}",
                    delta=f"{'✅ coperti' if gap_medio_wf >= 0 else f'🚨 deficit {gap_medio_wf:.0f}'}",
                    delta_color="normal" if gap_medio_wf >= 0 else "inverse",
                    help="Media giornaliera di turni richiesti dal servizio"
                )

            st.markdown("---")
            # ── TREND ASSENZE (rimasto invariato) ───────────────────────────
            st.markdown("#### <i class='fas fa-chart-line'></i> Trend Assenze per Tipologia", unsafe_allow_html=True)
            trend_df = df_filtered.groupby("giorno").agg(
                infortuni=("infortuni", "sum"),
                malattie=("malattie", "sum"),
                legge_104=("legge_104", "sum"),
                congedo_parentale=("congedo_parentale", "sum"),
                permessi_vari=("permessi_vari", "sum"),
            ).reset_index()

            fig_trend = go.Figure()
            for col, label, colore in [
                ("infortuni",         "Infortuni",       "#ef4444"),
                ("malattie",          "Malattie",        "#f97316"),
                ("legge_104",         "L.104",           "#eab308"),
                ("congedo_parentale", "Congedo parent.", "#06b6d4"),
                ("permessi_vari",     "Permessi vari",   "#22c55e"),
            ]:
                fig_trend.add_trace(go.Scatter(
                    x=trend_df["giorno"], y=trend_df[col],
                    mode="lines+markers", name=label,
                    line=dict(color=colore, width=2),
                    marker=dict(size=5),
                    hovertemplate=f"<b>{label}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y:.1f}}</b><extra></extra>"
                ))
            fig_trend.update_layout(
                height=400, hovermode="x unified",
                legend=dict(orientation="h", y=-0.18),
                **PLOTLY_TEMPLATE
            )
            st.plotly_chart(fig_trend, use_container_width=True, key="pc_7")

        # ─────────────────────────────────────────────
        # SOTTO-TAB B — FERIE & RIPOSI
        # ─────────────────────────────────────────────
        with st2_b:
            st.markdown(
                "<p style='color:#93c5fd;'>Conteggio giornaliero di <b>FP (Ferie Programmate)</b> e "
                "<b>R (Riposi)</b> dalla tabella roster, per deposito.</p>",
                unsafe_allow_html=True
            )
            try:
                d0 = df_filtered["giorno"].min().date()
                d1 = df_filtered["giorno"].max().date()
                deps_str = ",".join([f"'{d}'" for d in deposito_sel])

                df_fp_r = pd.read_sql(f"""
                    SELECT
                        data                                  AS giorno,
                        deposito,
                        COUNT(*) FILTER (WHERE turno = 'FP') AS ferie_programmate,
                        COUNT(*) FILTER (WHERE turno = 'R')  AS riposi
                    FROM roster
                    WHERE data BETWEEN '{d0}' AND '{d1}'
                      AND deposito IN ({deps_str})
                    GROUP BY data, deposito
                    ORDER BY data, deposito;
                """, get_conn())
                df_fp_r["giorno"] = pd.to_datetime(df_fp_r["giorno"])
                fp_r_daily = df_fp_r.groupby("giorno")[["ferie_programmate", "riposi"]].sum().reset_index()

                k1, k2, k3, k4 = st.columns(4)
                with k1: st.metric("🏖️ Tot. Ferie Programmate", f"{int(fp_r_daily['ferie_programmate'].sum()):,}")
                with k2: st.metric("💤 Tot. Riposi",            f"{int(fp_r_daily['riposi'].sum()):,}")
                with k3: st.metric("📅 Media FP/giorno",        f"{fp_r_daily['ferie_programmate'].mean():.1f}")
                with k4: st.metric("📅 Media Riposi/giorno",    f"{fp_r_daily['riposi'].mean():.1f}")

                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

                view_fp_r = st.radio(
                    "Visualizza", ["Per tipo (FP vs R)", "Per deposito"],
                    horizontal=True, key="view_fp_r"
                )

                if view_fp_r == "Per tipo (FP vs R)":
                    fig_fpr = go.Figure()
                    fig_fpr.add_trace(go.Bar(
                        x=fp_r_daily["giorno"], y=fp_r_daily["ferie_programmate"],
                        name="Ferie Programmate (FP)", marker_color="#22c55e",
                        hovertemplate="<b>FP</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"
                    ))
                    fig_fpr.add_trace(go.Bar(
                        x=fp_r_daily["giorno"], y=fp_r_daily["riposi"],
                        name="Riposi (R)", marker_color="#3b82f6",
                        hovertemplate="<b>R</b><br>%{x|%d/%m/%Y}: <b>%{y}</b><extra></extra>"
                    ))
                    fig_fpr.update_layout(
                        barmode="stack", height=450, hovermode="x unified",
                        plot_bgcolor="rgba(15,23,42,0.8)", paper_bgcolor="rgba(15,23,42,0.5)",
                        font=dict(color="#cbd5e1"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        xaxis=dict(tickformat="%d/%m", tickangle=-45,
                                   gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)"),
                        yaxis=dict(title="Persone",
                                   gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)"),
                    )
                    st.plotly_chart(fig_fpr, use_container_width=True, key="pc_8")
                else:
                    tipo_dep = st.radio("Tipo", ["FP", "R"], horizontal=True, key="tipo_dep_fpr")
                    col_sel  = "ferie_programmate" if tipo_dep == "FP" else "riposi"
                    fig_fpr_dep = go.Figure()
                    for dep in sorted(df_fp_r["deposito"].unique()):
                        df_d = df_fp_r[df_fp_r["deposito"] == dep]
                        fig_fpr_dep.add_trace(go.Bar(
                            x=df_d["giorno"], y=df_d[col_sel],
                            name=dep.title(), marker_color=get_colore_deposito(dep),
                            hovertemplate=f"<b>{dep.title()}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y}}</b><extra></extra>"
                        ))
                    fig_fpr_dep.update_layout(
                        barmode="stack", height=450, hovermode="x unified",
                        title=f"{'Ferie Programmate' if tipo_dep == 'FP' else 'Riposi'} per Deposito",
                        plot_bgcolor="rgba(15,23,42,0.8)", paper_bgcolor="rgba(15,23,42,0.5)",
                        font=dict(color="#cbd5e1"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        xaxis=dict(tickformat="%d/%m", tickangle=-45,
                                   gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)"),
                        yaxis=dict(title="Persone",
                                   gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)"),
                    )
                    st.plotly_chart(fig_fpr_dep, use_container_width=True, key="pc_9")

            except Exception as e:
                st.warning(f"⚠️ Errore ferie/riposi: {e}")

        # ─────────────────────────────────────────────
        # SOTTO-TAB C — ASSENZE COMPLETE
        # ─────────────────────────────────────────────
        with st2_c:
            st.markdown(
                "<p style='color:#93c5fd;'>Assenze statistiche + nominali dal roster: "
                "<b>PS</b> · <b>AP</b> (Aspettativa) · <b>PADm</b> (Congedo straord.) · <b>NF</b> (Non in forza).</p>",
                unsafe_allow_html=True
            )
            try:
                d0 = df_filtered["giorno"].min().date()
                d1 = df_filtered["giorno"].max().date()
                deps_str = ",".join([f"'{d}'" for d in deposito_sel])

                df_nominali = pd.read_sql(f"""
                    SELECT
                        data AS giorno, deposito,
                        COUNT(*) FILTER (WHERE turno = 'PS')   AS ps,
                        COUNT(*) FILTER (WHERE turno = 'AP')   AS aspettativa,
                        COUNT(*) FILTER (WHERE turno = 'PADm') AS congedo_straord,
                        COUNT(*) FILTER (WHERE turno = 'NF')   AS non_in_forza
                    FROM roster
                    WHERE data BETWEEN '{d0}' AND '{d1}'
                      AND deposito IN ({deps_str})
                    GROUP BY data, deposito
                    ORDER BY data, deposito;
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
                with k1: st.metric("🤕 Infortuni",    f"{int(df_assenze_full['infortuni'].sum()):,}")
                with k2: st.metric("🤒 Malattie",      f"{int(df_assenze_full['malattie'].sum()):,}")
                with k3: st.metric("♿ L.104",          f"{int(df_assenze_full['legge_104'].sum()):,}")
                with k4: st.metric("📋 PS",            f"{int(df_assenze_full['ps'].sum()):,}")
                with k5: st.metric("⏸️ Aspettativa",  f"{int(df_assenze_full['aspettativa'].sum()):,}")
                with k6: st.metric("🔴 Non in forza", f"{int(df_assenze_full['non_in_forza'].sum()):,}")

                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

                palette_stat = [
                    ("infortuni",         "Infortuni",         "#ef4444"),
                    ("malattie",          "Malattie",          "#f97316"),
                    ("legge_104",         "L.104",             "#eab308"),
                    ("altre_assenze",     "Altre assenze",     "#a78bfa"),
                    ("congedo_parentale", "Congedo parentale", "#06b6d4"),
                    ("permessi_vari",     "Permessi vari",     "#22c55e"),
                ]
                palette_nom = [
                    ("ps",              "PS",                    "#f43f5e"),
                    ("aspettativa",     "AP (Aspettativa)",      "#8b5cf6"),
                    ("congedo_straord", "PADm (Cong. straord.)", "#0ea5e9"),
                    ("non_in_forza",    "NF (Non in forza)",     "#64748b"),
                ]

                fig_ass = go.Figure()
                for col, label, colore in palette_stat:
                    fig_ass.add_trace(go.Bar(
                        x=df_assenze_full["giorno"], y=df_assenze_full[col],
                        name=label, marker_color=colore,
                        hovertemplate=f"<b>{label}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y:.1f}}</b><extra></extra>"
                    ))
                for col, label, colore in palette_nom:
                    fig_ass.add_trace(go.Bar(
                        x=df_assenze_full["giorno"], y=df_assenze_full[col],
                        name=label, marker_color=colore,
                        marker_line=dict(width=1, color="rgba(255,255,255,0.4)"),
                        hovertemplate=f"<b>{label}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y}}</b><extra></extra>"
                    ))
                fig_ass.update_layout(
                    barmode="stack", height=520, hovermode="x unified",
                    plot_bgcolor="rgba(15,23,42,0.8)", paper_bgcolor="rgba(15,23,42,0.5)",
                    font=dict(color="#cbd5e1", family="Arial, sans-serif"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
                    xaxis=dict(title="Data", tickformat="%d/%m", tickangle=-45,
                               gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)"),
                    yaxis=dict(title="Persone assenti",
                               gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)"),
                )
                st.plotly_chart(fig_ass, use_container_width=True, key="pc_10")

                with st.expander("🔍 Dettaglio singolo deposito"):
                    dep_ass = st.selectbox(
                        "Deposito", sorted(deposito_sel), key="dep_ass_detail",
                        format_func=lambda x: x.title()
                    )
                    df_dep_stat = df_filtered[df_filtered["deposito"] == dep_ass].groupby("giorno").agg(
                        infortuni=("infortuni","sum"), malattie=("malattie","sum"),
                        legge_104=("legge_104","sum"), altre_assenze=("altre_assenze","sum"),
                        congedo_parentale=("congedo_parentale","sum"), permessi_vari=("permessi_vari","sum"),
                    ).reset_index()
                    df_dep_nom = df_nominali[df_nominali["deposito"] == dep_ass].copy()
                    df_dep_full = df_dep_stat.merge(
                        df_dep_nom[["giorno","ps","aspettativa","congedo_straord","non_in_forza"]],
                        on="giorno", how="left"
                    ).fillna(0)
                    fig_dep_ass = go.Figure()
                    for col, label, colore in palette_stat + palette_nom:
                        fig_dep_ass.add_trace(go.Bar(
                            x=df_dep_full["giorno"], y=df_dep_full[col],
                            name=label, marker_color=colore,
                            hovertemplate=f"<b>{label}</b><br>%{{x|%d/%m/%Y}}: <b>%{{y:.1f}}</b><extra></extra>"
                        ))
                    fig_dep_ass.update_layout(
                        barmode="stack", height=420, hovermode="x unified",
                        title=f"Assenze — {dep_ass.title()}",
                        plot_bgcolor="rgba(15,23,42,0.8)", paper_bgcolor="rgba(15,23,42,0.5)",
                        font=dict(color="#cbd5e1"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
                        xaxis=dict(tickformat="%d/%m", tickangle=-45,
                                   gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)"),
                        yaxis=dict(title="Persone",
                                   gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)"),
                    )
                    st.plotly_chart(fig_dep_ass, use_container_width=True, key="pc_11")

            except Exception as e:
                st.warning(f"⚠️ Errore assenze: {e}")


# ══════════════════════════════════════════════════
# TAB 3 — TURNI CALENDARIO
# ══════════════════════════════════════════════════
with tab3:
    st.markdown("### <i class='fas fa-calendar-check'></i> Turni per Deposito — Validità Temporale",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#93c5fd;'>Turni giornalieri per deposito, rispettando il tipo di giorno "
        "(Lu-Ve / Sa / Do) e il range di validita <b>dal &rarr; al</b> della tabella turni.</p>",
        unsafe_allow_html=True
    )

    if not turni_cal_ok or len(df_tc_filtered) == 0:
        st.warning("Nessun record trovato per il periodo selezionato.")
        st.info(
            "**Debug rapido**: controlla che i valori di `valid` nella tabella `turni` "
            "(`Lu-Ve`, `Sa`, `Do`) coincidano esattamente con i valori di `daytype` "
            "in `calendar`, e che le date `dal`/`al` rientrino nel periodo selezionato."
        )
    else:
        tc_col1, tc_col2, tc_col3 = st.columns([1, 1, 2])
        with tc_col1:
            bar_mode = st.radio("Modalità barre", ["Impilate", "Affiancate"], horizontal=True)
            bmode    = "stack" if bar_mode == "Impilate" else "group"
        with tc_col2:
            show_totale = st.checkbox("Mostra linea totale", value=True)
        with tc_col3:
            dep_tc = st.multiselect(
                "Depositi visibili nel grafico",
                options=sorted(df_tc_filtered["deposito"].unique()),
                default=sorted(df_tc_filtered["deposito"].unique()),
                key="dep_tc_filter"
            )

        df_tc_plot = df_tc_filtered[df_tc_filtered["deposito"].isin(dep_tc)].copy()

        if len(df_tc_plot) == 0:
            st.info("Nessun dato per la selezione corrente.")
        else:
            df_tc_agg = (
                df_tc_plot.groupby(["giorno", "deposito"])["turni"]
                .sum().reset_index()
                .sort_values(["giorno", "deposito"])
            )

            fig_tc = go.Figure()

            for dep in sorted(df_tc_agg["deposito"].unique()):
                df_dep = df_tc_agg[df_tc_agg["deposito"] == dep]
                colore = get_colore_deposito(dep)
                fig_tc.add_trace(go.Bar(
                    x=df_dep["giorno"],
                    y=df_dep["turni"],
                    name=dep.title(),
                    marker_color=colore,
                    marker_line=dict(width=0.4, color="rgba(255,255,255,0.12)"),
                    hovertemplate=(
                        f"<b>{dep.title()}</b><br>"
                        "Data: %{x|%d/%m/%Y}<br>"
                        "Turni: <b>%{y}</b><extra></extra>"
                    )
                ))

            if show_totale:
                totale_gg = df_tc_agg.groupby("giorno")["turni"].sum().reset_index()
                fig_tc.add_trace(go.Scatter(
                    x=totale_gg["giorno"],
                    y=totale_gg["turni"],
                    name="Totale",
                    mode="lines+markers",
                    line=dict(color="#ffffff", width=2.5, dash="dot"),
                    marker=dict(size=7, symbol="diamond"),
                    hovertemplate="<b>Totale</b><br>Data: %{x|%d/%m/%Y}<br>Turni: <b>%{y}</b><extra></extra>"
                ))

            fig_tc.update_layout(
                barmode=bmode,
                height=550,
                hovermode="x unified",
                plot_bgcolor="rgba(15, 23, 42, 0.8)",
                paper_bgcolor="rgba(15, 23, 42, 0.5)",
                font=dict(color="#cbd5e1", family="Arial, sans-serif"),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=11, color="#cbd5e1")
                ),
                xaxis=dict(title="Data", tickformat="%d/%m", tickangle=-45,
                           gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)",
                           zerolinecolor="rgba(96,165,250,0.3)"),
                yaxis=dict(title="Turni Richiesti",
                           gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)",
                           zerolinecolor="rgba(96,165,250,0.3)"),
            )
            st.plotly_chart(fig_tc, use_container_width=True, key="pc_13")

            st.markdown("---")
            st.markdown("#### <i class='fas fa-search'></i> Esplora Codici Turno per Deposito", unsafe_allow_html=True)

            try:
                df_codici = pd.read_sql("""
                    SELECT deposito, codice_turno, valid, dal, al
                    FROM turni
                    ORDER BY deposito, valid, codice_turno;
                """, get_conn())
                df_codici["dal"] = pd.to_datetime(df_codici["dal"]).dt.strftime("%d/%m/%Y")
                df_codici["al"]  = pd.to_datetime(df_codici["al"]).dt.strftime("%d/%m/%Y")

                depositi_con_turni = sorted(df_codici["deposito"].unique())
                dep_esplora = st.selectbox(
                    "📍 Seleziona deposito", options=depositi_con_turni,
                    format_func=lambda x: x.title(), key="dep_esplora"
                )
                tipi_disponibili = sorted(df_codici[df_codici["deposito"] == dep_esplora]["valid"].unique())
                tipo_sel = st.radio(
                    "Tipo giorno", options=["Tutti"] + tipi_disponibili,
                    horizontal=True, key="tipo_esplora"
                )

                df_dep_codici = df_codici[df_codici["deposito"] == dep_esplora].copy()
                if tipo_sel != "Tutti":
                    df_dep_codici = df_dep_codici[df_dep_codici["valid"] == tipo_sel]

                k1, k2, k3 = st.columns(3)
                with k1: st.metric("🔢 Codici turno", len(df_dep_codici))
                with k2: st.metric("📋 Tipi giorno",  df_dep_codici["valid"].nunique())
                with k3:
                    periodo = f"{df_dep_codici['dal'].iloc[0]} → {df_dep_codici['al'].iloc[0]}" \
                              if len(df_dep_codici) > 0 else "—"
                    st.metric("📅 Validità", periodo)

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                if len(df_dep_codici) > 0:
                    colore_dep = get_colore_deposito(dep_esplora)
                    for tipo in sorted(df_dep_codici["valid"].unique()):
                        df_tipo = df_dep_codici[df_dep_codici["valid"] == tipo]
                        label_tipo = {"Lu-Ve": "📅 Lunedì — Venerdì",
                                      "Sa": "📅 Sabato", "Do": "📅 Domenica"}.get(tipo, tipo)
                        st.markdown(
                            f"<p style='color:#93c5fd;font-weight:700;font-size:1rem;"
                            f"margin:16px 0 8px;letter-spacing:1px;'>{label_tipo}"
                            f" <span style='color:#64748b;font-size:0.8rem;font-weight:400;'>"
                            f"({len(df_tipo)} turni · {df_tipo['dal'].iloc[0]} → {df_tipo['al'].iloc[0]})"
                            f"</span></p>", unsafe_allow_html=True
                        )
                        codici = df_tipo["codice_turno"].tolist()
                        cols_per_row = 8
                        for i in range(0, len(codici), cols_per_row):
                            cols = st.columns(cols_per_row)
                            for j, codice in enumerate(codici[i:i+cols_per_row]):
                                with cols[j]:
                                    st.markdown(
                                        f"<div style='background:rgba(15,23,42,0.8);"
                                        f"border:1px solid {colore_dep}55;"
                                        f"border-left:3px solid {colore_dep};"
                                        f"border-radius:8px;padding:8px 6px;text-align:center;"
                                        f"font-size:0.85rem;font-weight:700;color:#e2e8f0;"
                                        f"letter-spacing:0.5px;margin-bottom:6px;"
                                        f"'>{codice}</div>", unsafe_allow_html=True
                                    )
                else:
                    st.info("Nessun codice turno trovato per la selezione.")

            except Exception as e:
                st.warning(f"⚠️ Impossibile caricare i codici turno: {e}")

            st.markdown("---")
            st.markdown("#### <i class='fas fa-chart-pie'></i> Distribuzione Turni per Deposito", unsafe_allow_html=True)
            totale_per_dep = df_tc_agg.groupby("deposito")["turni"].sum().reset_index()
            fig_pie_tc = go.Figure(go.Pie(
                labels=[d.title() for d in totale_per_dep["deposito"]],
                values=totale_per_dep["turni"],
                marker=dict(colors=[get_colore_deposito(d) for d in totale_per_dep["deposito"]]),
                hole=0.4, textinfo="label+percent+value",
                hovertemplate="<b>%{label}</b><br>Turni: %{value}<br>%{percent}<extra></extra>"
            ))
            fig_pie_tc.update_layout(
                height=450, showlegend=True,
                paper_bgcolor="rgba(15,23,42,0.5)",
                legend=dict(font=dict(color="#cbd5e1")),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_pie_tc, use_container_width=True, key="pc_14")

            st.markdown("---")
            st.markdown("#### <i class='fas fa-calendar-week'></i> Turni per Giorno — Lu-Ve / Sabato / Domenica", unsafe_allow_html=True)

            if turni_cal_ok and len(df_tc_plot) > 0:
                try:
                    date_list = df_tc_plot["giorno"].dt.date.unique().tolist()
                    date_str  = ",".join([f"'{d}'" for d in date_list])
                    df_cal_mini = pd.read_sql(
                        f"SELECT data, daytype FROM calendar WHERE data IN ({date_str});",
                        get_conn()
                    )
                    df_cal_mini["data"] = pd.to_datetime(df_cal_mini["data"])

                    df_tc_daytype = df_tc_plot.merge(
                        df_cal_mini, left_on="giorno", right_on="data", how="left"
                    )

                    def daytype_to_categoria(dt: str) -> str:
                        dt = (dt or "").strip().lower()
                        if dt in ["lunedi","martedi","mercoledi","giovedi","venerdi"]: return "Lu-Ve"
                        elif dt == "sabato":   return "Sabato"
                        elif dt == "domenica": return "Domenica"
                        return dt.title()

                    df_tc_daytype["categoria"] = df_tc_daytype["daytype"].apply(daytype_to_categoria)
                    cat_order = ["Lu-Ve", "Sabato", "Domenica"]
                    primo_giorno_per_cat = df_tc_daytype.groupby("categoria")["giorno"].min().to_dict()

                    agg_daytype_list = []
                    for cat, primo_gg in primo_giorno_per_cat.items():
                        df_giorno = df_tc_daytype[df_tc_daytype["giorno"] == primo_gg][["deposito","turni","categoria"]]
                        agg_daytype_list.append(df_giorno)

                    agg_daytype = pd.concat(agg_daytype_list, ignore_index=True) if agg_daytype_list else pd.DataFrame()
                    agg_daytype["categoria"] = pd.Categorical(agg_daytype["categoria"], categories=cat_order, ordered=True)
                    agg_daytype = agg_daytype.sort_values(["categoria", "deposito"])
                    totale_cat = agg_daytype.groupby("categoria")["turni"].sum().reindex(cat_order, fill_value=0)

                    fig_daytype = go.Figure()
                    for dep in sorted(agg_daytype["deposito"].unique()):
                        dep_data = agg_daytype[agg_daytype["deposito"] == dep]
                        valori = [dep_data[dep_data["categoria"] == cat]["turni"].sum()
                                  if cat in dep_data["categoria"].values else 0 for cat in cat_order]
                        fig_daytype.add_trace(go.Bar(
                            x=cat_order, y=valori, name=dep.title(),
                            marker_color=get_colore_deposito(dep),
                            marker_line=dict(width=0.4, color="rgba(255,255,255,0.12)"),
                            text=[f"{v:,}" if v > 0 else "" for v in valori],
                            textposition="inside", textfont=dict(size=11, color="white"),
                            hovertemplate=f"<b>{dep.title()}</b><br>Tipo: %{{x}}<br>Turni: <b>%{{y:,}}</b><extra></extra>"
                        ))

                    fig_daytype.update_layout(
                        barmode="stack", height=480, hovermode="x unified",
                        plot_bgcolor="rgba(15,23,42,0.8)", paper_bgcolor="rgba(15,23,42,0.5)",
                        font=dict(color="#cbd5e1", family="Arial, sans-serif"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
                        xaxis=dict(title="Tipo Giorno", gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)"),
                        yaxis=dict(title="Turni Totali", gridcolor="rgba(96,165,250,0.1)", linecolor="rgba(96,165,250,0.3)"),
                        annotations=[
                            dict(x=cat, y=totale_cat[cat], text=f"<b>{int(totale_cat[cat]):,}</b>",
                                 xanchor="center", yanchor="bottom", showarrow=False,
                                 font=dict(size=13, color="#ffffff"), yshift=6)
                            for cat in cat_order if totale_cat[cat] > 0
                        ]
                    )
                    st.plotly_chart(fig_daytype, use_container_width=True, key="pc_15")

                    k1, k2, k3 = st.columns(3)
                    with k1: st.metric("📅 Turni/giorno Lu-Ve",    f"{int(totale_cat.get('Lu-Ve', 0)):,}")
                    with k2: st.metric("📅 Turni/giorno Sabato",   f"{int(totale_cat.get('Sabato', 0)):,}")
                    with k3: st.metric("📅 Turni/giorno Domenica", f"{int(totale_cat.get('Domenica', 0)):,}")

                except Exception as e:
                    st.warning(f"⚠️ Impossibile caricare analisi per tipo giorno: {e}")


# ══════════════════════════════════════════════════
# TAB 4 — DEPOSITI
# ══════════════════════════════════════════════════
with tab4:
    if len(df_filtered) > 0 and len(by_deposito) > 0:
        st.markdown("#### <i class='fas fa-trophy'></i> Ranking Depositi per Gap Medio", unsafe_allow_html=True)
        soglia_per_dep = soglia_gap
        colors_dep = [
            '#dc2626' if g < soglia_per_dep else '#fb923c' if g < 0 else '#22c55e'
            for g in by_deposito["media_gap_giorno"]
        ]
        fig_dep = go.Figure(go.Bar(
            y=by_deposito["deposito"], x=by_deposito["media_gap_giorno"], orientation='h',
            marker=dict(color=colors_dep),
            text=by_deposito["media_gap_giorno"], texttemplate='%{text:.1f}', textposition='outside'
        ))
        fig_dep.add_vline(x=0, line_width=3, line_color="#60a5fa")
        fig_dep.update_layout(height=max(400, len(by_deposito) * 35), showlegend=False, **PLOTLY_TEMPLATE)
        st.plotly_chart(fig_dep, use_container_width=True, key="pc_16")

        st.markdown("---")
        st.markdown("#### <i class='fas fa-chart-radar'></i> Comparazione Multi-Dimensionale", unsafe_allow_html=True)
        by_dep_n = by_deposito.copy()
        for col in ['turni_richiesti', 'disponibili_netti', 'assenze_previste']:
            mx = by_dep_n[col].max()
            by_dep_n[f'{col}_n'] = by_dep_n[col] / mx * 100 if mx > 0 else 0

        fig_radar = go.Figure()
        for _, row in by_deposito.head(6).iterrows():
            nr = by_dep_n[by_dep_n['deposito'] == row['deposito']]
            if len(nr) > 0:
                fig_radar.add_trace(go.Scatterpolar(
                    r=[nr['turni_richiesti_n'].values[0],
                       nr['disponibili_netti_n'].values[0],
                       100 - nr['assenze_previste_n'].values[0],
                       row['tasso_copertura_%']],
                    theta=['Turni Richiesti', 'Disponibili', 'Presenza', 'Copertura %'],
                    fill='toself', name=row['deposito'].title(),
                    line=dict(color=get_colore_deposito(row['deposito']))
                ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(96,165,250,0.2)'),
                bgcolor='rgba(15,23,42,0.8)'
            ),
            height=500, paper_bgcolor='rgba(15,23,42,0.5)', font={'color': '#cbd5e1'}
        )
        st.plotly_chart(fig_radar, use_container_width=True, key="pc_17")

        st.markdown("---")
        st.markdown("#### <i class='fas fa-table'></i> Tabella Dettagliata", unsafe_allow_html=True)
        st.dataframe(
            by_deposito[[
                "deposito","dipendenti_medi_giorno","giorni_periodo",
                "disponibili_netti","assenze_previste","media_gap_giorno","tasso_copertura_%"
            ]].rename(columns={
                "deposito":"Deposito","dipendenti_medi_giorno":"Autisti medi",
                "giorni_periodo":"Giorni","disponibili_netti":"Disponibili",
                "assenze_previste":"Assenze","media_gap_giorno":"Gap/Giorno","tasso_copertura_%":"Copertura %"
            }),
            use_container_width=True, hide_index=True
        )


# ══════════════════════════════════════════════════
# TAB 5 — EXPORT
# ══════════════════════════════════════════════════
with tab5:
    st.markdown("#### <i class='fas fa-download'></i> Export Dati e Report", unsafe_allow_html=True)
    col_exp1, col_exp2 = st.columns(2)

    df_export = df_filtered.copy()
    df_export["giorno"] = df_export["giorno"].dt.strftime('%d/%m/%Y')

    with col_exp1:
        st.markdown("##### 📊 Dataset Filtrato (CSV)")
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Scarica CSV", data=csv,
            file_name=f"estate2026_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        st.info(f"📦 {len(df_export):,} righe × {len(df_export.columns)} colonne")

    with col_exp2:
        st.markdown("##### 📈 Summary Report (Excel)")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, sheet_name='Staffing', index=False)
            if len(by_deposito) > 0:
                by_deposito.to_excel(writer, sheet_name='Per_Deposito', index=False)
            if turni_cal_ok and len(df_tc_filtered) > 0:
                tc_exp = df_tc_filtered.copy()
                tc_exp["giorno"] = tc_exp["giorno"].dt.strftime('%d/%m/%Y')
                tc_exp.to_excel(writer, sheet_name='Turni_Calendario', index=False)
        st.download_button(
            "⬇️ Scarica Excel Report", data=output.getvalue(),
            file_name=f"estate2026_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("✅ Include: Staffing · Per deposito · Turni calendario")

    st.markdown("---")
    st.markdown("##### 👀 Anteprima Dataset")
    st.dataframe(df_export.head(100), use_container_width=True, height=400)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(f"""
<div style='text-align:center;padding:30px;'>
    <p style='font-size:1.2em;font-weight:700;color:#60a5fa;'>
        <i class='fas fa-rocket'></i> ESTATE 2026 PREMIUM ANALYTICS
    </p>
    <p style='font-size:0.9em;color:#93c5fd;margin-top:10px;'>
        <i class='fas fa-bolt'></i> Powered by Streamlit · Plotly · PostgreSQL
    </p>
    <p style='font-size:0.85em;color:#64748b;margin-top:5px;'>
        <i class='far fa-clock'></i> Aggiornato: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
    </p>
</div>
""", unsafe_allow_html=True)
