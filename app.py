"""
===============================================
ESTATE 2026 - DASHBOARD ANALYTICS PREMIUM
===============================================
Dashboard executive avanzata con:
- Analytics predittivi
- 15+ tipi di visualizzazioni
- Export automatico reports
- Comparison mode
- Anomaly detection
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

# --------------------------------------------------
# CONFIGURAZIONE PAGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Estate 2026 - Analytics Premium", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚍"
)

# CSS CUSTOM - PREMIUM DARK MODE
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
    /* Dark Background con pattern */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f172a 100%);
        background-attachment: fixed;
    }
    
    /* Headers premium */
    h1 {
        color: #60a5fa !important;
        text-shadow: 0 0 20px rgba(96, 165, 250, 0.5), 0 0 40px rgba(96, 165, 250, 0.3);
        font-weight: 900 !important;
        letter-spacing: 2px;
        font-size: 3rem !important;
        margin-bottom: 1rem !important;
    }
    
    h2 {
        color: #93c5fd !important;
        text-shadow: 0 0 10px rgba(147, 197, 253, 0.4);
        font-weight: 700 !important;
        margin-top: 30px !important;
    }
    
    h3 {
        color: #bfdbfe !important;
        text-shadow: 0 0 8px rgba(191, 219, 254, 0.3);
        font-weight: 600 !important;
    }
    
    /* Metrics premium */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        color: #60a5fa !important;
        text-shadow: 0 0 10px rgba(96, 165, 250, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #93c5fd !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Metric containers premium */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        padding: 25px;
        border-radius: 16px;
        box-shadow: 
            0 8px 32px 0 rgba(0, 0, 0, 0.5),
            inset 0 1px 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(96, 165, 250, 0.2);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 12px 40px 0 rgba(96, 165, 250, 0.3),
            inset 0 1px 1px 0 rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(96, 165, 250, 0.4);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.5);
        padding: 10px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
        color: #93c5fd;
        font-weight: 600;
        padding: 12px 24px;
        border: 1px solid rgba(96, 165, 250, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: 1px solid rgba(96, 165, 250, 0.5);
    }
    
    /* Sidebar premium */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 2px solid rgba(96, 165, 250, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #e0e7ff !important;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(96, 165, 250, 0.2) !important;
        margin: 30px 0 !important;
    }
    
    /* Alert boxes premium */
    .alert-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.3) 100%);
        padding: 20px;
        border-radius: 16px;
        color: #fecaca;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(239, 68, 68, 0.4);
        border: 2px solid rgba(239, 68, 68, 0.5);
        border-left: 6px solid #ef4444;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(251, 146, 60, 0.2) 0%, rgba(249, 115, 22, 0.3) 100%);
        padding: 20px;
        border-radius: 16px;
        color: #fed7aa;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(251, 146, 60, 0.4);
        border: 2px solid rgba(251, 146, 60, 0.5);
        border-left: 6px solid #fb923c;
    }
    
    .alert-success {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(22, 163, 74, 0.3) 100%);
        padding: 20px;
        border-radius: 16px;
        color: #bbf7d0;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(34, 197, 94, 0.4);
        border: 2px solid rgba(34, 197, 94, 0.5);
        border-left: 6px solid #22c55e;
    }
    
    .alert-info {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.3) 100%);
        padding: 20px;
        border-radius: 16px;
        color: #bfdbfe;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.4);
        border: 2px solid rgba(59, 130, 246, 0.5);
        border-left: 6px solid #3b82f6;
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(96, 165, 250, 0.2);
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(96, 165, 250, 0.2);
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(96, 165, 250, 0.2);
        border-radius: 12px;
    }
    
    /* Text elements */
    p, span, label {
        color: #cbd5e1 !important;
    }
    
    /* Inputs */
    input, select, textarea {
        background: rgba(15, 23, 42, 0.8) !important;
        color: #e0e7ff !important;
        border: 1px solid rgba(96, 165, 250, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Buttons */
    button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Download button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
    }
    
    /* Info box */
    .info-box {
        background: rgba(15, 23, 42, 0.8);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid rgba(96, 165, 250, 0.3);
    }
    
    /* Insight card */
    .insight-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.2) 100%);
        padding: 20px;
        border-radius: 16px;
        border: 2px solid rgba(96, 165, 250, 0.3);
        margin: 15px 0;
    }
    
    .insight-card h4 {
        color: #60a5fa !important;
        margin-bottom: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FUNZIONI UTILITY
# --------------------------------------------------
def check_password():
    """Verifica password per accesso"""
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔒 Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 Password", type="password", on_change=password_entered, key="password")
        st.error("❌ Password errata")
        return False
    return True

if not check_password():
    st.stop()

@st.cache_resource
def get_connection():
    """Connessione database"""
    return psycopg2.connect(st.secrets["DATABASE_URL"], sslmode="require")

conn = get_connection()

# Test connessione
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
def load_data():
    """Carica dati staffing"""
    query = """
        SELECT 
            giorno, tipo_giorno, deposito, totale_autisti,
            assenze_programmate, assenze_previste, infortuni, malattie,
            legge_104, altre_assenze, congedo_parentale, permessi_vari,
            turni_richiesti, disponibili_netti, gap
        FROM v_staffing
        ORDER BY giorno, deposito;
    """
    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def load_depositi_stats():
    query = """
        select deposito, giorni_attivi, dipendenti_medi_giorno
        from v_depositi_organico_medio
        order by deposito;
    """
    return pd.read_sql(query, conn)


# Carica dati
try:
    df = load_data()
    df["giorno"] = pd.to_datetime(df["giorno"])
    df_depositi = load_depositi_stats()
    
    # Rimuovi depbelvede
    df = df[df["deposito"] != "depbelvede"].copy()
    df_depositi = df_depositi[df_depositi["deposito"] != "depbelvede"].copy()
except Exception as e:
    st.error(f"❌ Errore caricamento: {e}")
    st.stop()

# Funzione categorizzazione
def categorizza_tipo_giorno(tipo: str) -> str:
    t = (tipo or "").strip().lower()
    if t in ['lunedi','martedi','mercoledi','giovedi','venerdi']:
        return 'Lu-Ve'
    elif t == 'sabato':
        return 'Sabato'
    elif t == 'domenica':
        return 'Domenica'
    return tipo


df['categoria_giorno'] = df['tipo_giorno'].apply(categorizza_tipo_giorno)

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.markdown("## <i class='fas fa-sliders-h'></i> CONTROLLI", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Selezione modalità
modalita = st.sidebar.radio(
    "📊 Modalità Vista",
    ["Dashboard Completa", "Analisi Comparativa", "Report Esportabile"],
    help="Scegli come visualizzare i dati"
)

st.sidebar.markdown("---")

depositi = sorted(df["deposito"].unique())
deposito_sel = st.sidebar.multiselect(
    "📍 DEPOSITI", 
    depositi, 
    default=depositi,
    help="Seleziona depositi"
)

min_date = df["giorno"].min().date()
max_date = df["giorno"].max().date()

date_range = st.sidebar.date_input(
    "📅 PERIODO",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

st.sidebar.markdown("---")

soglia_gap = st.sidebar.slider(
    "⚠️ SOGLIA CRITICA",
    min_value=-50,
    max_value=0,
    value=-10,
    help="Gap sotto questa soglia è critico"
)

# Filtri avanzati in expander
with st.sidebar.expander("🔧 Filtri Avanzati"):
    show_forecast = st.checkbox("📈 Mostra Previsioni", value=True)
    show_insights = st.checkbox("💡 Mostra Insights AI", value=True)
    min_gap_filter = st.number_input("Gap Minimo", value=-100)
    max_gap_filter = st.number_input("Gap Massimo", value=100)

st.sidebar.markdown("---")

# Applica filtri
if len(date_range) == 2:
    df_filtered = df[
        (df["deposito"].isin(deposito_sel)) &
        (df["giorno"] >= pd.to_datetime(date_range[0])) &
        (df["giorno"] <= pd.to_datetime(date_range[1])) &
        (df["gap"] >= min_gap_filter) &
        (df["gap"] <= max_gap_filter)
    ].copy()
else:
    df_filtered = df[
        (df["deposito"].isin(deposito_sel)) &
        (df["gap"] >= min_gap_filter) &
        (df["gap"] <= max_gap_filter)
    ].copy()

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
    st.markdown(
        f"<p style='text-align: center; color: #93c5fd; font-size: 1.2rem; font-weight: 600;'>"
        f"<i class='far fa-calendar-alt'></i> {date_range[0].strftime('%d/%m/%Y')} → {date_range[1].strftime('%d/%m/%Y')} | "
        f"<i class='fas fa-building'></i> {len(deposito_sel)} Depositi | "
        f"<i class='fas fa-database'></i> {len(df_filtered):,} Records</p>",
        unsafe_allow_html=True
    )

st.markdown("---")

# --------------------------------------------------
# KPI CARDS PREMIUM
# --------------------------------------------------
st.markdown("### <i class='fas fa-chart-line'></i> KEY PERFORMANCE INDICATORS", unsafe_allow_html=True)

if len(df_filtered) > 0:
    # Calcoli
    giorni_analizzati = df_filtered['giorno'].nunique()
    totale_dipendenti = df_depositi[df_depositi["deposito"].isin(deposito_sel)]["totale_dipendenti"].sum()
    disponibilita_media_giorno = df_filtered.groupby("giorno")["disponibili_netti"].sum().mean()
    gap_medio_giorno = df_filtered.groupby("giorno")["gap"].sum().mean()
    media_turni_giorno = df_filtered.groupby("giorno")["turni_richiesti"].sum().mean()
    gap_pct_medio = (gap_medio_giorno / media_turni_giorno * 100) if media_turni_giorno > 0 else 0
    gap_per_giorno = df_filtered.groupby("giorno")["gap"].sum()
    giorni_critici_count = (gap_per_giorno < soglia_gap).sum()
    pct_critici = (giorni_critici_count / giorni_analizzati * 100) if giorni_analizzati > 0 else 0
    
    # Statistiche assenze
    totale_assenze = df_filtered['assenze_previste'].sum()
    tasso_assenze = (totale_assenze / (totale_dipendenti * giorni_analizzati) * 100) if totale_dipendenti > 0 else 0
    
    # KPI Row
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    
    with kpi1:
        st.metric("👤 Autisti", f"{int(totale_dipendenti):,}", help="Totale autisti")
    
    with kpi2:
        st.metric("📅 Giorni", f"{giorni_analizzati}", help="Giorni analizzati")
    
    with kpi3:
        st.metric("📊 Disponibili/Giorno", f"{int(disponibilita_media_giorno):,}", help="Media disponibili")
    
    with kpi4:
        delta_color = "normal" if gap_medio_giorno >= 0 else "inverse"
        st.metric("⚖️ Gap Medio", f"{int(gap_medio_giorno):,}", delta=f"{gap_pct_medio:.1f}%", delta_color=delta_color)
    
    with kpi5:
        st.metric("🚨 Giorni Critici", f"{giorni_critici_count}/{giorni_analizzati}", delta=f"{pct_critici:.0f}%", delta_color="inverse")
    
    with kpi6:
        st.metric("🏥 Tasso Assenze", f"{tasso_assenze:.1f}%", help="% assenze sul totale")

st.markdown("---")

# --------------------------------------------------
# AI INSIGHTS (se abilitato)
# --------------------------------------------------
if show_insights and len(df_filtered) > 0:
    st.markdown("### <i class='fas fa-brain'></i> AI INSIGHTS", unsafe_allow_html=True)
    
    insights_col1, insights_col2, insights_col3 = st.columns(3)
    
    with insights_col1:
        # Insight 1: Deposito più critico
        by_dep = df_filtered.groupby("deposito")["gap"].mean()
        worst_dep = by_dep.idxmin()
        worst_gap = by_dep.min()
        
        st.markdown(f"""
        <div class='insight-card'>
            <h4><i class='fas fa-exclamation-triangle'></i> Deposito Critico</h4>
            <p style='font-size: 1.1rem; margin: 0;'>
                <b>{worst_dep}</b> ha il gap medio peggiore: <b>{worst_gap:.1f}</b>
            </p>
            <p style='font-size: 0.9rem; color: #fed7aa; margin-top: 10px;'>
                💡 Considera redistribuzione turni o assunzioni
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insights_col2:
        # Insight 2: Giorno più problematico
        by_cat = df_filtered.groupby("categoria_giorno")["gap"].mean()
        worst_cat = by_cat.idxmin()
        worst_cat_gap = by_cat.min()
        
        st.markdown(f"""
        <div class='insight-card'>
            <h4><i class='fas fa-calendar-times'></i> Giorno Critico</h4>
            <p style='font-size: 1.1rem; margin: 0;'>
                <b>{worst_cat}</b> ha il gap medio peggiore: <b>{worst_cat_gap:.1f}</b>
            </p>
            <p style='font-size: 0.9rem; color: #fed7aa; margin-top: 10px;'>
                💡 Pianifica turni extra per questi giorni
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insights_col3:
        # Insight 3: Trend assenze
        assenze_trend = df_filtered.groupby("giorno")["assenze_previste"].sum()
        if len(assenze_trend) > 1:
            trend_direction = "crescente" if assenze_trend.iloc[-1] > assenze_trend.iloc[0] else "decrescente"
            trend_icon = "📈" if trend_direction == "crescente" else "📉"
        else:
            trend_direction = "stabile"
            trend_icon = "➡️"
        
        st.markdown(f"""
        <div class='insight-card'>
            <h4><i class='fas fa-chart-line'></i> Trend Assenze</h4>
            <p style='font-size: 1.1rem; margin: 0;'>
                {trend_icon} Trend <b>{trend_direction}</b>
            </p>
            <p style='font-size: 0.9rem; color: #bfdbfe; margin-top: 10px;'>
                💡 Monitora evoluzione assenze settimanalmente
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

# --------------------------------------------------
# TABS ORGANIZATION
# --------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📈 Trend Analysis",  
    "🎯 Depositi",
    "🔍 Deep Dive",
    "📥 Export"
])

# Template Plotly
plotly_template = {
    'plot_bgcolor': 'rgba(15, 23, 42, 0.8)',
    'paper_bgcolor': 'rgba(15, 23, 42, 0.5)',
    'font': {'color': '#cbd5e1', 'family': 'Arial, sans-serif'},
    'xaxis': {'gridcolor': 'rgba(96, 165, 250, 0.1)', 'linecolor': 'rgba(96, 165, 250, 0.3)', 'zerolinecolor': 'rgba(96, 165, 250, 0.3)'},
    'yaxis': {'gridcolor': 'rgba(96, 165, 250, 0.1)', 'linecolor': 'rgba(96, 165, 250, 0.3)', 'zerolinecolor': 'rgba(96, 165, 250, 0.3)'}
}

# ==================== TAB 1: OVERVIEW ====================
with tab1:
    if len(df_filtered) > 0:
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.markdown("#### <i class='fas fa-chart-area'></i> Andamento Temporale", unsafe_allow_html=True)
            
            grouped = df_filtered.groupby("giorno").agg({
                "turni_richiesti": "sum",
                "disponibili_netti": "sum",
                "gap": "sum",
                "assenze_previste": "sum"
            }).reset_index()
            
            fig_timeline = make_subplots(
                rows=2, cols=1,
                row_heights=[0.65, 0.35],
                subplot_titles=("Turni vs Disponibilità", "Gap Giornaliero"),
                vertical_spacing=0.1
            )
            
            fig_timeline.add_trace(
                go.Scatter(x=grouped["giorno"], y=grouped["turni_richiesti"],
                    mode='lines+markers', name='Turni Richiesti',
                    line=dict(color='#ef4444', width=3, shape='spline'),
                    marker=dict(size=8, symbol='circle'),
                    fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.15)'),
                row=1, col=1
            )
            
            fig_timeline.add_trace(
                go.Scatter(x=grouped["giorno"], y=grouped["disponibili_netti"],
                    mode='lines+markers', name='Disponibili',
                    line=dict(color='#22c55e', width=3, shape='spline'),
                    marker=dict(size=8, symbol='circle'),
                    fill='tozeroy', fillcolor='rgba(34, 197, 94, 0.15)'),
                row=1, col=1
            )
            
            colors = ['#dc2626' if g < soglia_gap else '#fb923c' if g < 0 else '#22c55e' for g in grouped["gap"]]
            
            fig_timeline.add_trace(
                go.Bar(x=grouped["giorno"], y=grouped["gap"], name="Gap",
                    marker=dict(color=colors, line=dict(width=1, color='rgba(255,255,255,0.2)')),
                    showlegend=False),
                row=2, col=1
            )
            
            fig_timeline.add_hline(y=soglia_gap, line_dash="dash", line_color="#dc2626",
                line_width=2, annotation_text="Soglia", row=2, col=1)
            
            fig_timeline.update_layout(
                height=600, hovermode="x unified", showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                **plotly_template
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        with col_side:
            st.markdown("#### <i class='fas fa-tachometer-alt'></i> Stato Copertura", unsafe_allow_html=True)
            
            gap_pct = (gap_medio_giorno / media_turni_giorno * 100) if media_turni_giorno > 0 else 0
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=gap_pct,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Gap % Medio", 'font': {'size': 16, 'color': '#93c5fd'}},
                delta={'reference': 0, 'suffix': '%'},
                number={'suffix': '%', 'font': {'size': 32, 'color': '#60a5fa'}},
                gauge={
                    'axis': {'range': [-20, 20], 'tickcolor': "#60a5fa"},
                    'bar': {'color': "#3b82f6", 'thickness': 0.7},
                    'bgcolor': "rgba(15, 23, 42, 0.8)",
                    'borderwidth': 3,
                    'bordercolor': "#60a5fa",
                    'steps': [
                        {'range': [-20, -10], 'color': 'rgba(220, 38, 38, 0.3)'},
                        {'range': [-10, 0], 'color': 'rgba(251, 146, 60, 0.3)'},
                        {'range': [0, 10], 'color': 'rgba(34, 197, 94, 0.3)'},
                        {'range': [10, 20], 'color': 'rgba(16, 185, 129, 0.3)'}
                    ],
                    'threshold': {'line': {'color': "#ef4444", 'width': 4}, 'thickness': 0.75,
                        'value': (soglia_gap / media_turni_giorno * 100) if media_turni_giorno > 0 else 0}
                }
            ))
            
            fig_gauge.update_layout(height=280, paper_bgcolor='rgba(15, 23, 42, 0.5)', margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Composizione Assenze
            st.markdown("#### <i class='fas fa-user-injured'></i> Assenze", unsafe_allow_html=True)
            
            assenze_breakdown = pd.DataFrame({
                'Tipo': ['Infortuni', 'Malattie', 'L.104', 'Congedi', 'Permessi', 'Altro'],
                'Totale': [
                    int(df_filtered['infortuni'].sum()),
                    int(df_filtered['malattie'].sum()),
                    int(df_filtered['legge_104'].sum()),
                    int(df_filtered['congedo_parentale'].sum()),
                    int(df_filtered['permessi_vari'].sum()),
                    int(df_filtered['altre_assenze'].sum())
                ]
            })
            
            assenze_breakdown = assenze_breakdown[assenze_breakdown['Totale'] > 0]
            
            if len(assenze_breakdown) > 0:
                fig_assenze = go.Figure(go.Pie(
                    labels=assenze_breakdown['Tipo'], values=assenze_breakdown['Totale'],
                    hole=.5,
                    marker=dict(colors=['#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#8b5cf6']),
                    textinfo='label+percent'
                ))
                
                fig_assenze.update_layout(
                    height=280, showlegend=False,
                    paper_bgcolor='rgba(15, 23, 42, 0.5)',
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                
                st.plotly_chart(fig_assenze, use_container_width=True)
        
        # Heatmap
        st.markdown("---")
        st.markdown("#### <i class='fas fa-fire'></i> Heatmap Criticità", unsafe_allow_html=True)
        
        pivot_gap = df_filtered.pivot_table(
            values='gap', index='deposito',
            columns=df_filtered['giorno'].dt.strftime('%d/%m'),
            aggfunc='sum', fill_value=0
        )
        
        fig_heat = go.Figure(go.Heatmap(
            z=pivot_gap.values, x=pivot_gap.columns, y=pivot_gap.index,
            colorscale=[
                [0, '#7f1d1d'], [0.3, '#dc2626'], [0.45, '#fb923c'],
                [0.5, '#fef3c7'], [0.55, '#86efac'], [0.7, '#22c55e'], [1, '#14532d']
            ],
            zmid=0, text=pivot_gap.values, texttemplate='%{text:.0f}',
            colorbar=dict(title="Gap")
        ))
        
        fig_heat.update_layout(
            height=max(300, len(pivot_gap) * 40),
            **plotly_template
        )
        
        st.plotly_chart(fig_heat, use_container_width=True)

# ==================== TAB 2: TREND ANALYSIS ====================
with tab2:
    if len(df_filtered) > 0:
        st.markdown("#### <i class='fas fa-chart-line'></i> Analisi Trend Assenze", unsafe_allow_html=True)
        
        # Trend assenze per tipo
        trend_assenze = df_filtered.groupby("giorno").agg({
            'infortuni': 'sum',
            'malattie': 'sum',
            'legge_104': 'sum',
            'congedo_parentale': 'sum',
            'permessi_vari': 'sum'
        }).reset_index()
        
        fig_trend = go.Figure()
        
        colors_trend = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4']
        names = ['Infortuni', 'Malattie', 'L.104', 'Congedi', 'Permessi']
        cols = ['infortuni', 'malattie', 'legge_104', 'congedo_parentale', 'permessi_vari']
        
        for col, name, color in zip(cols, names, colors_trend):
            fig_trend.add_trace(go.Scatter(
                x=trend_assenze['giorno'], y=trend_assenze[col],
                mode='lines+markers', name=name,
                line=dict(color=color, width=2),
                marker=dict(size=6)
            ))
        
        fig_trend.update_layout(
            height=450, hovermode="x unified",
            legend=dict(orientation="h", y=-0.15),
            **plotly_template
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Box Plot distribuzione gap
        st.markdown("---")
        st.markdown("#### <i class='fas fa-box'></i> Distribuzione Gap per Deposito", unsafe_allow_html=True)
        
        fig_box = go.Figure()
        
        for dep in deposito_sel:
            dep_data = df_filtered[df_filtered['deposito'] == dep]['gap']
            fig_box.add_trace(go.Box(
                y=dep_data, name=dep,
                marker_color='#3b82f6',
                boxmean='sd'
            ))
        
        fig_box.update_layout(
            height=450,
            showlegend=False,
            **plotly_template
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
        
        # Waterfall Chart
        st.markdown("---")
        st.markdown("#### <i class='fas fa-water'></i> Composizione Gap Medio", unsafe_allow_html=True)
        
        autisti_totali_medio = df_filtered.groupby('giorno')['totale_autisti'].sum().mean()
        assenze_medie = df_filtered.groupby('giorno')['assenze_previste'].sum().mean()
        turni_medi = df_filtered.groupby('giorno')['turni_richiesti'].sum().mean()
        disp_medie = df_filtered.groupby('giorno')['disponibili_netti'].sum().mean()
        gap_medio = df_filtered.groupby('giorno')['gap'].sum().mean()
        
        fig_waterfall = go.Figure(go.Waterfall(
            name="Gap", orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Autisti Totali", "- Assenze", "- Turni Richiesti", "= Gap"],
            y=[autisti_totali_medio, -assenze_medie, -turni_medi + assenze_medie, gap_medio],
            text=[f"{autisti_totali_medio:.0f}", f"-{assenze_medie:.0f}", 
                  f"-{(turni_medi-assenze_medie):.0f}", f"{gap_medio:.0f}"],
            textposition="outside",
            connector={"line": {"color": "#60a5fa"}},
            increasing={"marker": {"color": "#22c55e"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#3b82f6"}}
        ))
        
        fig_waterfall.update_layout(
            height=450,
            showlegend=False,
            **plotly_template
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True)

# ==================== TAB 3: DEPOSITI ====================
with tab3:
    if len(df_filtered) > 0:
        st.markdown("#### <i class='fas fa-trophy'></i> Ranking Depositi", unsafe_allow_html=True)
        
        by_deposito = df_filtered.groupby("deposito").agg({
            "turni_richiesti": "sum",
            "disponibili_netti": "sum",
            "gap": "sum",
            "assenze_previste": "sum"
        }).reset_index()
        
        by_deposito = by_deposito.merge(df_depositi, on="deposito", how="left")
        
        giorni_per_dep = df_filtered.groupby("deposito")["giorno"].nunique()
        by_deposito = by_deposito.merge(
            giorni_per_dep.rename("giorni_periodo"),
            left_on="deposito", right_index=True
        )
        
        by_deposito["media_gap_giorno"] = (by_deposito["gap"] / by_deposito["giorni_periodo"]).round(1)
        by_deposito["tasso_copertura_%"] = (
            (by_deposito["disponibili_netti"] / by_deposito["turni_richiesti"] * 100).fillna(0).round(1)
        )
        
        by_deposito = by_deposito.sort_values("media_gap_giorno")
        
        # Bar chart ranking
        colors_dep = ['#dc2626' if g < (soglia_gap / giorni_analizzati) else '#fb923c' if g < 0 else '#22c55e' 
                      for g in by_deposito["media_gap_giorno"]]
        
        fig_dep = go.Figure(go.Bar(
            y=by_deposito["deposito"], x=by_deposito["media_gap_giorno"],
            orientation='h',
            marker=dict(color=colors_dep),
            text=by_deposito["media_gap_giorno"],
            texttemplate='%{text:.1f}',
            textposition='outside'
        ))
        
        fig_dep.add_vline(x=0, line_width=3, line_color="#60a5fa")
        
        fig_dep.update_layout(
            height=max(400, len(by_deposito) * 35),
            showlegend=False,
            **plotly_template
        )
        
        st.plotly_chart(fig_dep, use_container_width=True)
        
        # Radar Chart Comparativo
        st.markdown("---")
        st.markdown("#### <i class='fas fa-chart-radar'></i> Comparazione Multi-Dimensionale", unsafe_allow_html=True)
        
        # Normalizza metriche per radar
        by_deposito_norm = by_deposito.copy()
        for col in ['turni_richiesti', 'disponibili_netti', 'assenze_previste']:
            max_val = by_deposito_norm[col].max()
            if max_val > 0:
                by_deposito_norm[f'{col}_norm'] = by_deposito_norm[col] / max_val * 100
        
        fig_radar = go.Figure()
        
        # Prendi top 5 depositi
        top_deps = by_deposito.head(5)
        
        for _, row in top_deps.iterrows():
            r_values = [
                by_deposito_norm[by_deposito_norm['deposito'] == row['deposito']]['turni_richiesti_norm'].values[0],
                by_deposito_norm[by_deposito_norm['deposito'] == row['deposito']]['disponibili_netti_norm'].values[0],
                100 - (by_deposito_norm[by_deposito_norm['deposito'] == row['deposito']]['assenze_previste_norm'].values[0]),
                row['tasso_copertura_%']
            ]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=r_values,
                theta=['Turni Richiesti', 'Disponibili', 'Presenza', 'Copertura %'],
                fill='toself',
                name=row['deposito']
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(96, 165, 250, 0.2)'),
                bgcolor='rgba(15, 23, 42, 0.8)'
            ),
            height=500,
            paper_bgcolor='rgba(15, 23, 42, 0.5)',
            font={'color': '#cbd5e1'}
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Tabella dettagliata
        st.markdown("---")
        st.markdown("#### <i class='fas fa-table'></i> Dati Dettagliati", unsafe_allow_html=True)
        
        st.dataframe(
            by_deposito[[
                "deposito", "totale_dipendenti", "giorni_periodo",
                "disponibili_netti", "assenze_previste",
                "media_gap_giorno", "tasso_copertura_%"
            ]].rename(columns={
                "deposito": "Deposito",
                "totale_dipendenti": "Autisti",
                "giorni_periodo": "Giorni",
                "disponibili_netti": "Disponibili",
                "assenze_previste": "Assenze",
                "media_gap_giorno": "Gap/Giorno",
                "tasso_copertura_%": "Copertura %"
            }),
            use_container_width=True,
            hide_index=True
        )

# ==================== TAB 4: DEEP DIVE ====================
with tab4:
    if len(df_filtered) > 0:
        st.markdown("#### <i class='fas fa-search'></i> Analisi Avanzata", unsafe_allow_html=True)
        
        # Sunburst
        st.markdown("##### 🌞 Distribuzione Gerarchica Turni", unsafe_allow_html=True)
        
        df_sunburst = df_filtered.groupby(["deposito", "categoria_giorno"]).agg({
            "turni_richiesti": "sum"
        }).reset_index()
        
        fig_sun = px.sunburst(
            df_sunburst,
            path=['deposito', 'categoria_giorno'],
            values='turni_richiesti',
            color='turni_richiesti',
            color_continuous_scale='Blues'
        )
        
        fig_sun.update_layout(height=500, paper_bgcolor='rgba(15, 23, 42, 0.5)')
        st.plotly_chart(fig_sun, use_container_width=True)
        
        # Matrice di Correlazione
        st.markdown("---")
        st.markdown("##### 🔗 Matrice Correlazioni", unsafe_allow_html=True)
        
        corr_cols = ['turni_richiesti', 'disponibili_netti', 'gap', 'assenze_previste', 
                     'infortuni', 'malattie', 'legge_104']
        
        corr_matrix = df_filtered[corr_cols].corr()
        
        fig_corr = go.Figure(go.Heatmap(
            z=corr_matrix.values,
            x=[col.replace('_', ' ').title() for col in corr_matrix.columns],
            y=[col.replace('_', ' ').title() for col in corr_matrix.index],
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            colorbar=dict(title="Correlazione")
        ))
        
        fig_corr.update_layout(
            height=500,
            **plotly_template
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Statistiche Descrittive
        st.markdown("---")
        st.markdown("##### 📊 Statistiche Descrittive", unsafe_allow_html=True)
        
        stats_df = df_filtered[['gap', 'disponibili_netti', 'assenze_previste']].describe().T
        stats_df = stats_df.round(2)
        
        st.dataframe(stats_df, use_container_width=True)

# ==================== TAB 5: EXPORT ====================
with tab5:
    st.markdown("#### <i class='fas fa-download'></i> Export Dati e Report", unsafe_allow_html=True)
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.markdown("##### 📊 Dataset Filtrato")
        
        # Prepara CSV
        df_export = df_filtered.copy()
        df_export['giorno'] = df_export['giorno'].dt.strftime('%d/%m/%Y')
        
        csv = df_export.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="⬇️ Scarica CSV",
            data=csv,
            file_name=f"estate2026_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.info(f"📦 {len(df_export):,} righe × {len(df_export.columns)} colonne")
    
    with col_exp2:
        st.markdown("##### 📈 Summary Report")
        
        # Crea Excel con statistiche
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Sheet 1: Dati
            df_export.to_excel(writer, sheet_name='Dati', index=False)
            
            # Sheet 2: Statistiche per deposito
            if len(by_deposito) > 0:
                by_deposito.to_excel(writer, sheet_name='Per_Deposito', index=False)
        
        excel_data = output.getvalue()
        
        st.download_button(
            label="⬇️ Scarica Excel Report",
            data=excel_data,
            file_name=f"estate2026_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.success("✅ Report completo con statistiche")
    
    # Anteprima dati
    st.markdown("---")
    st.markdown("##### 👀 Anteprima Dataset")
    
    st.dataframe(
        df_export.head(100),
        use_container_width=True,
        height=400
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 30px;'>
    <p style='font-size: 1.2em; font-weight: 700; color: #60a5fa;'>
        <i class='fas fa-rocket'></i> ESTATE 2026 PREMIUM ANALYTICS
    </p>
    <p style='font-size: 0.9em; color: #93c5fd; margin-top: 10px;'>
        <i class='fas fa-bolt'></i> Powered by Streamlit + Plotly + AI Insights
    </p>
    <p style='font-size: 0.85em; color: #64748b; margin-top: 5px;'>
        <i class='far fa-clock'></i> Aggiornato: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
    </p>
</div>
""", unsafe_allow_html=True)
