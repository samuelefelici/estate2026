"""
===============================================
ESTATE 2026 - ANALISI STAFFING AVANZATA
===============================================
Dashboard executive per il monitoraggio
della copertura turni estate 2026.

Features:
- KPI dirigenziali real-time
- Heatmap criticità per deposito
- Analisi predittiva assenze
- Drill-down per deposito e periodo
===============================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import psycopg2
from datetime import datetime, timedelta

# --------------------------------------------------
# CONFIGURAZIONE PAGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Estate 2026 - Executive Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚌"
)

# CSS CUSTOM - DARK MODE PROFESSIONALE TRASPORTI
st.markdown("""
<style>
    /* Dark Background principale */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f172a 100%);
    }
    
    /* Headers con glow effect */
    h1 {
        color: #60a5fa !important;
        text-shadow: 0 0 20px rgba(96, 165, 250, 0.5), 0 0 40px rgba(96, 165, 250, 0.3);
        font-weight: 900 !important;
        letter-spacing: 2px;
        font-size: 3rem !important;
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
    
    /* Metrics - Glass morphism style */
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
    
    [data-testid="stMetricDelta"] {
        font-weight: 700 !important;
    }
    
    /* Metric containers - Glassmorphism */
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
    
    /* Sidebar - Dark elegant */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 2px solid rgba(96, 165, 250, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #e0e7ff !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #60a5fa !important;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(96, 165, 250, 0.2) !important;
        margin: 30px 0 !important;
    }
    
    /* Alert boxes - Neon style */
    .alert-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.3) 100%);
        padding: 20px;
        border-radius: 16px;
        color: #fecaca;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 20px 0;
        box-shadow: 
            0 8px 32px rgba(239, 68, 68, 0.4),
            inset 0 0 20px rgba(239, 68, 68, 0.1);
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
        box-shadow: 
            0 8px 32px rgba(251, 146, 60, 0.4),
            inset 0 0 20px rgba(251, 146, 60, 0.1);
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
        box-shadow: 
            0 8px 32px rgba(34, 197, 94, 0.4),
            inset 0 0 20px rgba(34, 197, 94, 0.1);
        border: 2px solid rgba(34, 197, 94, 0.5);
        border-left: 6px solid #22c55e;
    }
    
    /* Plotly charts - Dark theme */
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
    
    /* Info box custom */
    .info-box {
        background: rgba(15, 23, 42, 0.8);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid rgba(96, 165, 250, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CONTROLLO PASSWORD
# --------------------------------------------------
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "🔒 Inserisci la password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "🔒 Inserisci la password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("❌ Password errata")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --------------------------------------------------
# CONNESSIONE DATABASE
# --------------------------------------------------
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        st.secrets["DATABASE_URL"],
        sslmode="require"
    )

conn = get_connection()

# Test connessione
try:
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    db_time = cur.fetchone()[0]
    cur.close()
    st.sidebar.success(f"✅ Database connesso\n{db_time.strftime('%d/%m/%Y %H:%M')}")
except Exception as e:
    st.sidebar.error(f"❌ Errore database: {e}")
    st.stop()

# --------------------------------------------------
# CARICAMENTO DATI
# --------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    """Carica dati dalla view v_staffing con dettagli assenze"""
    query = """
        SELECT 
            giorno,
            tipo_giorno,
            deposito,
            totale_autisti,
            assenze_programmate,
            assenze_previste,
            infortuni,
            malattie,
            legge_104,
            altre_assenze,
            congedo_parentale,
            permessi_vari,
            turni_richiesti,
            disponibili_netti,
            gap
        FROM v_staffing
        ORDER BY giorno, deposito;
    """
    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def load_depositi_stats():
    """Carica statistiche depositi"""
    query = """
        SELECT 
            deposito,
            COUNT(DISTINCT data) as giorni_attivi,
            COUNT(DISTINCT matricola) as totale_dipendenti
        FROM roster
        GROUP BY deposito
        ORDER BY deposito;
    """
    return pd.read_sql(query, conn)

# Carica i dati
try:
    df = load_data()
    df["giorno"] = pd.to_datetime(df["giorno"])
    
    df_depositi = load_depositi_stats()
    
    # RIMUOVI depbelvede dai dati
    df = df[df["deposito"] != "depbelvede"].copy()
    df_depositi = df_depositi[df_depositi["deposito"] != "depbelvede"].copy()
    
except Exception as e:
    st.error(f"❌ Errore nel caricamento dati: {e}")
    st.stop()

# --------------------------------------------------
# FILTRI SIDEBAR
# --------------------------------------------------
st.sidebar.markdown("## 🎛️ PANNELLO DI CONTROLLO")
st.sidebar.markdown("---")

depositi = sorted(df["deposito"].unique())
deposito_sel = st.sidebar.multiselect(
    "📍 DEPOSITI", 
    depositi, 
    default=depositi,
    help="Seleziona i depositi da analizzare"
)

min_date = df["giorno"].min().date()
max_date = df["giorno"].max().date()

date_range = st.sidebar.date_input(
    "📅 PERIODO ANALISI",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

st.sidebar.markdown("---")

# Soglia criticità
soglia_gap = st.sidebar.slider(
    "⚠️ SOGLIA CRITICA GAP",
    min_value=-50,
    max_value=0,
    value=-10,
    help="Gap inferiore a questo valore viene evidenziato come critico"
)

# Applica filtri
if len(date_range) == 2:
    df_filtered = df[
        (df["deposito"].isin(deposito_sel)) &
        (df["giorno"] >= pd.to_datetime(date_range[0])) &
        (df["giorno"] <= pd.to_datetime(date_range[1]))
    ].copy()
else:
    df_filtered = df[df["deposito"].isin(deposito_sel)].copy()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("<h1 style='text-align: center;'>🚌 ESTATE 2026 - ANALISI STAFFING</h1>", unsafe_allow_html=True)
if len(date_range) == 2:
    st.markdown(f"<p style='text-align: center; color: #93c5fd; font-size: 1.2rem; font-weight: 600;'>📅 {date_range[0].strftime('%d/%m/%Y')} - {date_range[1].strftime('%d/%m/%Y')} | 🏢 {len(deposito_sel)}/{len(depositi)} Depositi</p>", unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# KPI EXECUTIVE - ROW 1
# --------------------------------------------------
st.markdown("### 📊 INDICATORI CHIAVE DI PERFORMANCE")

# Calcola statistiche corrette
if len(df_filtered) > 0:
    giorni_analizzati = df_filtered['giorno'].nunique()
    
    # Mappa tipo_giorno a categoria
    def categorizza_tipo_giorno(tipo):
        if tipo in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            return 'Lu-Ve'
        elif tipo == 'Saturday':
            return 'Sabato'
        elif tipo == 'Sunday':
            return 'Domenica'
        else:
            return tipo
    
    df_filtered['categoria_giorno'] = df_filtered['tipo_giorno'].apply(categorizza_tipo_giorno)
    
    # Statistiche per categoria giorno (Lu-Ve, Sab, Dom)
    stats_per_categoria = df_filtered.groupby("categoria_giorno").agg({
        "turni_richiesti": "mean",
        "disponibili_netti": "mean",
        "gap": "mean"
    }).round(1)
    
    # Ordina categorie
    ordine_categorie = ['Lu-Ve', 'Sabato', 'Domenica']
    stats_per_categoria = stats_per_categoria.reindex([c for c in ordine_categorie if c in stats_per_categoria.index])
    
    # Mostra riepilogo categoria giorno
    if len(stats_per_categoria) > 0:
        tipo_str = " | ".join([f"<b>{cat}</b>: {int(row['turni_richiesti'])} turni" 
                               for cat, row in stats_per_categoria.iterrows()])
        st.markdown(f"""
        <div class='info-box'>
            <p style='color: #93c5fd; margin: 0; font-size: 0.95rem; font-weight: 600;'>
                📊 <b>Fabbisogno Medio Turni:</b> {tipo_str}
            </p>
        </div>
        """, unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

# KPI 1: Totale Dipendenti
totale_dipendenti = df_depositi[df_depositi["deposito"].isin(deposito_sel)]["totale_dipendenti"].sum()
with kpi1:
    st.metric(
        "👥 Autisti Totali",
        f"{int(totale_dipendenti):,}",
        help="Numero totale di autisti nei depositi selezionati"
    )

# KPI 2: Giorni Analizzati
with kpi2:
    st.metric(
        "📅 Giorni Analizzati",
        f"{giorni_analizzati}",
        help="Numero di giorni nel periodo selezionato"
    )

# KPI 3: Disponibilità Media Giornaliera
if len(df_filtered) > 0:
    disponibilita_media_giorno = df_filtered.groupby("giorno")["disponibili_netti"].sum().mean()
else:
    disponibilita_media_giorno = 0

with kpi3:
    st.metric(
        "📈 Disponibilità Media/Giorno",
        f"{int(disponibilita_media_giorno):,}",
        help="Media operatori disponibili per singolo giorno"
    )

# KPI 4: Gap Medio Giornaliero
if len(df_filtered) > 0:
    gap_medio_giorno = df_filtered.groupby("giorno")["gap"].sum().mean()
    media_turni_giorno = df_filtered.groupby("giorno")["turni_richiesti"].sum().mean()
    gap_pct_medio = (gap_medio_giorno / media_turni_giorno * 100) if media_turni_giorno > 0 else 0
else:
    gap_medio_giorno = 0
    gap_pct_medio = 0
    media_turni_giorno = 0

with kpi4:
    st.metric(
        "⚖️ Gap Medio/Giorno",
        f"{int(gap_medio_giorno):,}",
        delta=f"{gap_pct_medio:.1f}%",
        delta_color="normal" if gap_medio_giorno >= 0 else "inverse",
        help="Gap medio giornaliero (disponibili - turni richiesti)"
    )

# KPI 5: Giorni Critici
if len(df_filtered) > 0:
    gap_per_giorno = df_filtered.groupby("giorno")["gap"].sum()
    giorni_critici_count = (gap_per_giorno < soglia_gap).sum()
    pct_critici = (giorni_critici_count / giorni_analizzati * 100) if giorni_analizzati > 0 else 0
else:
    giorni_critici_count = 0
    pct_critici = 0

with kpi5:
    st.metric(
        "🚨 Giorni Critici",
        f"{giorni_critici_count}/{giorni_analizzati}",
        delta=f"{pct_critici:.0f}%",
        delta_color="inverse" if giorni_critici_count > 0 else "normal",
        help=f"Giorni con gap totale < {soglia_gap}"
    )

st.markdown("---")

# --------------------------------------------------
# ALLARMI CRITICITÀ
# --------------------------------------------------
if len(df_filtered) > 0:
    gap_per_giorno_df = df_filtered.groupby("giorno").agg({
        "gap": "sum",
        "turni_richiesti": "sum",
        "disponibili_netti": "sum",
        "deposito": "count"
    }).reset_index()
    gap_per_giorno_df.rename(columns={"deposito": "n_depositi"}, inplace=True)
    
    # Trova giorni critici
    giorni_critici_df = gap_per_giorno_df[gap_per_giorno_df["gap"] < soglia_gap]
    n_giorni_critici = len(giorni_critici_df)
    
    if n_giorni_critici > 0:
        st.markdown(f"""
        <div class="alert-critical">
            🚨 <b>ALLARME ROSSO</b>: {n_giorni_critici} giorni con deficit critico (gap giornaliero totale &lt; {soglia_gap})
        </div>
        """, unsafe_allow_html=True)
        
        top_critici = giorni_critici_df.nsmallest(5, "gap")[["giorno", "gap", "turni_richiesti", "disponibili_netti", "n_depositi"]].copy()
        top_critici["giorno"] = top_critici["giorno"].dt.strftime("%d/%m/%Y")
        top_critici.columns = ["Giorno", "Gap Totale", "Turni Richiesti", "Disponibili", "N° Depositi"]
        st.dataframe(top_critici, use_container_width=True, hide_index=True)
        
    elif gap_medio_giorno < 0:
        st.markdown(f"""
        <div class="alert-warning">
            ⚠️ <b>ATTENZIONE</b>: Gap medio giornaliero negativo ({int(gap_medio_giorno)}). Pianificare azioni correttive.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-success">
            ✅ <b>OPERATIVITÀ GARANTITA</b>: Copertura turni completamente assicurata nel periodo.
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# GRAFICI PRINCIPALE - LAYOUT 2 COLONNE
# --------------------------------------------------
col_left, col_right = st.columns([2, 1])

plotly_dark_template = {
    'plot_bgcolor': 'rgba(15, 23, 42, 0.8)',
    'paper_bgcolor': 'rgba(15, 23, 42, 0.5)',
    'font': {'color': '#cbd5e1', 'family': 'Arial, sans-serif'},
    'xaxis': {
        'gridcolor': 'rgba(96, 165, 250, 0.1)',
        'linecolor': 'rgba(96, 165, 250, 0.3)',
        'zerolinecolor': 'rgba(96, 165, 250, 0.3)'
    },
    'yaxis': {
        'gridcolor': 'rgba(96, 165, 250, 0.1)',
        'linecolor': 'rgba(96, 165, 250, 0.3)',
        'zerolinecolor': 'rgba(96, 165, 250, 0.3)'
    }
}

with col_left:
    st.markdown("### 📈 ANDAMENTO TEMPORALE STAFFING")
    
    if len(df_filtered) > 0:
        grouped = df_filtered.groupby("giorno").agg({
            "turni_richiesti": "sum",
            "disponibili_netti": "sum",
            "gap": "sum",
            "assenze_previste": "sum"
        }).reset_index()
        
        fig_timeline = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=("Turni vs Disponibilità", "Gap Giornaliero"),
            vertical_spacing=0.12
        )
        
        fig_timeline.add_trace(
            go.Scatter(
                x=grouped["giorno"],
                y=grouped["turni_richiesti"],
                mode='lines+markers',
                name='Turni Richiesti',
                line=dict(color='#ef4444', width=3, shape='spline'),
                marker=dict(size=8, symbol='circle', line=dict(width=2, color='#7f1d1d')),
                fill='tozeroy',
                fillcolor='rgba(239, 68, 68, 0.15)'
            ),
            row=1, col=1
        )
        
        fig_timeline.add_trace(
            go.Scatter(
                x=grouped["giorno"],
                y=grouped["disponibili_netti"],
                mode='lines+markers',
                name='Disponibili Netti',
                line=dict(color='#22c55e', width=3, shape='spline'),
                marker=dict(size=8, symbol='circle', line=dict(width=2, color='#14532d')),
                fill='tozeroy',
                fillcolor='rgba(34, 197, 94, 0.15)'
            ),
            row=1, col=1
        )
        
        colors = ['#dc2626' if g < soglia_gap else '#fb923c' if g < 0 else '#22c55e' 
                  for g in grouped["gap"]]
        
        fig_timeline.add_trace(
            go.Bar(
                x=grouped["giorno"],
                y=grouped["gap"],
                name="Gap",
                marker=dict(
                    color=colors,
                    line=dict(width=1, color='rgba(255,255,255,0.2)')
                ),
                showlegend=False
            ),
            row=2, col=1
        )
        
        fig_timeline.add_hline(
            y=soglia_gap, 
            line_dash="dash", 
            line_color="#dc2626",
            line_width=2,
            annotation_text="Soglia Critica",
            annotation_font_color="#fca5a5",
            row=2, col=1
        )
        
        fig_timeline.update_layout(
            height=600,
            hovermode="x unified",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(15, 23, 42, 0.8)',
                bordercolor='rgba(96, 165, 250, 0.3)',
                borderwidth=1
            ),
            **plotly_dark_template
        )
        
        fig_timeline.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(96, 165, 250, 0.1)')
        fig_timeline.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(96, 165, 250, 0.1)')
        
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.warning("⚠️ Nessun dato disponibile per i filtri selezionati")

with col_right:
    st.markdown("### ⚖️ STATO COPERTURA")
    
    gap_pct = (gap_medio_giorno / media_turni_giorno * 100) if media_turni_giorno > 0 else 0
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=gap_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': "Gap % Medio/Giorno", 
            'font': {'size': 16, 'color': '#93c5fd', 'family': 'Arial Black'}
        },
        delta={'reference': 0, 'suffix': '%', 'font': {'size': 18, 'color': '#cbd5e1'}},
        number={'suffix': '%', 'font': {'size': 32, 'color': '#60a5fa', 'family': 'Arial Black'}},
        gauge={
            'axis': {
                'range': [-20, 20], 
                'tickwidth': 2, 
                'tickcolor': "#60a5fa",
                'tickfont': {'color': '#cbd5e1'}
            },
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
            'threshold': {
                'line': {'color': "#ef4444", 'width': 4},
                'thickness': 0.75,
                'value': (soglia_gap / media_turni_giorno * 100) if media_turni_giorno > 0 else 0
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=280,
        paper_bgcolor='rgba(15, 23, 42, 0.5)',
        font={'color': '#cbd5e1'},
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    st.markdown("### 🏥 COMPOSIZIONE ASSENZE")
    
    if len(df_filtered) > 0:
        assenze_breakdown = pd.DataFrame({
            'Tipo': ['Infortuni', 'Malattie', 'Legge 104', 'Congedi', 'Permessi', 'Altro'],
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
            fig_assenze = go.Figure(data=[go.Pie(
                labels=assenze_breakdown['Tipo'],
                values=assenze_breakdown['Totale'],
                hole=.5,
                marker=dict(
                    colors=['#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#8b5cf6'],
                    line=dict(color='rgba(15, 23, 42, 0.8)', width=2)
                ),
                textinfo='label+percent',
                textfont=dict(size=12, color='white', family='Arial Black'),
                hovertemplate='<b>%{label}</b><br>%{value} assenze<br>%{percent}<extra></extra>'
            )])
            
            fig_assenze.update_layout(
                height=280,
                showlegend=False,
                paper_bgcolor='rgba(15, 23, 42, 0.5)',
                font={'color': '#cbd5e1'},
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            st.plotly_chart(fig_assenze, use_container_width=True)
        else:
            st.info("📊 Nessuna assenza prevista nel periodo selezionato")
    else:
        st.info("📊 Nessun dato disponibile")

st.markdown("---")

# HEATMAP
st.markdown("### 🗺️ HEATMAP CRITICITÀ PER DEPOSITO/GIORNO")

if len(df_filtered) > 0:
    pivot_gap = df_filtered.pivot_table(
        values='gap',
        index='deposito',
        columns=df_filtered['giorno'].dt.strftime('%d/%m'),
        aggfunc='sum',
        fill_value=0
    )
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=pivot_gap.values,
        x=pivot_gap.columns,
        y=pivot_gap.index,
        colorscale=[
            [0, '#7f1d1d'],
            [0.3, '#dc2626'],
            [0.45, '#fb923c'],
            [0.5, '#fef3c7'],
            [0.55, '#86efac'],
            [0.7, '#22c55e'],
            [1, '#14532d']
        ],
        zmid=0,
        text=pivot_gap.values,
        texttemplate='%{text:.0f}',
        textfont={"size": 10, "color": "white"},
        colorbar=dict(
            title=dict(text="Gap", font=dict(color='#93c5fd')),
            tickfont=dict(color='#cbd5e1')
        ),
        hovertemplate='<b>%{y}</b><br>%{x}<br>Gap: %{z:.0f}<extra></extra>'
    ))
    
    fig_heatmap.update_layout(
        height=max(300, len(pivot_gap) * 40),
        xaxis=dict(
            title="Giorno",
            titlefont=dict(color='#93c5fd'),
            tickfont=dict(color='#cbd5e1')
        ),
        yaxis=dict(
            title="Deposito",
            titlefont=dict(color='#93c5fd'),
            tickfont=dict(color='#cbd5e1')
        ),
        **plotly_dark_template
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.warning("⚠️ Nessun dato disponibile per i filtri selezionati")

st.markdown("---")

# RANKING DEPOSITI
st.markdown("### 🏢 RANKING DEPOSITI PER PERFORMANCE")

if len(df_filtered) > 0:
    by_deposito = df_filtered.groupby("deposito").agg({
        "turni_richiesti": "sum",
        "disponibili_netti": "sum",
        "gap": "sum",
        "assenze_previste": "sum"
    }).reset_index()
    
    by_deposito = by_deposito.merge(df_depositi, on="deposito", how="left")
    
    by_deposito["turni_richiesti"] = by_deposito["turni_richiesti"].astype(int)
    by_deposito["disponibili_netti"] = by_deposito["disponibili_netti"].astype(int)
    by_deposito["gap"] = by_deposito["gap"].astype(int)
    by_deposito["assenze_previste"] = by_deposito["assenze_previste"].astype(int)
    
    giorni_per_deposito = df_filtered.groupby("deposito")["giorno"].nunique()
    by_deposito = by_deposito.merge(
        giorni_per_deposito.rename("giorni_periodo"), 
        left_on="deposito", 
        right_index=True
    )
    by_deposito["media_gap_giorno"] = (by_deposito["gap"] / by_deposito["giorni_periodo"]).round(1)
    
    by_deposito["tasso_copertura_%"] = (
        (by_deposito["disponibili_netti"] / by_deposito["turni_richiesti"] * 100)
        .fillna(0)
        .round(1)
    )
    
    by_deposito = by_deposito.sort_values("media_gap_giorno")
    
    fig_depositi = go.Figure()
    
    colors_dep = ['#dc2626' if g < (soglia_gap / giorni_analizzati) else '#fb923c' if g < 0 else '#22c55e' 
                  for g in by_deposito["media_gap_giorno"]]
    
    fig_depositi.add_trace(go.Bar(
        y=by_deposito["deposito"],
        x=by_deposito["media_gap_giorno"],
        orientation='h',
        marker=dict(
            color=colors_dep,
            line=dict(width=1, color='rgba(255,255,255,0.2)')
        ),
        text=by_deposito["media_gap_giorno"],
        textposition='outside',
        texttemplate='%{text:.1f}',
        textfont=dict(color='#cbd5e1', size=12, family='Arial Black'),
        hovertemplate='<b>%{y}</b><br>Gap medio/giorno: %{x:.1f}<extra></extra>'
    ))
    
    fig_depositi.update_layout(
        height=max(400, len(by_deposito) * 35),
        xaxis=dict(
            title="Gap Medio per Giorno (positivo = eccedenza, negativo = deficit)",
            titlefont=dict(color='#93c5fd', size=14),
            tickfont=dict(color='#cbd5e1')
        ),
        yaxis=dict(
            title="",
            tickfont=dict(color='#cbd5e1', size=12)
        ),
        **plotly_dark_template,
        showlegend=False
    )
    
    fig_depositi.add_vline(
        x=0, 
        line_width=3, 
        line_dash="solid", 
        line_color="#60a5fa",
        annotation_text="Zero",
        annotation_font_color="#93c5fd"
    )
    
    st.plotly_chart(fig_depositi, use_container_width=True)
    
    st.dataframe(
        by_deposito[[
            "deposito", 
            "totale_dipendenti",
            "giorni_periodo",
            "disponibili_netti", 
            "assenze_previste",
            "media_gap_giorno",
            "tasso_copertura_%"
        ]].rename(columns={
            "deposito": "Deposito",
            "totale_dipendenti": "Tot. Autisti",
            "giorni_periodo": "Giorni",
            "disponibili_netti": "Disponibili Totali",
            "assenze_previste": "Assenze Previste",
            "media_gap_giorno": "Gap Medio/Giorno",
            "tasso_copertura_%": "Tasso Copertura %"
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("⚠️ Nessun dato disponibile per i filtri selezionati")

st.markdown("---")

# SUNBURST
st.markdown("### 🌅 DISTRIBUZIONE GERARCHICA TURNI")

if len(df_filtered) > 0:
    df_sunburst = df_filtered.groupby(["deposito", "categoria_giorno"]).agg({
        "turni_richiesti": "sum"
    }).reset_index()
    
    df_sunburst["turni_richiesti"] = df_sunburst["turni_richiesti"].astype(int)
    
    fig_sunburst = px.sunburst(
        df_sunburst,
        path=['deposito', 'categoria_giorno'],
        values='turni_richiesti',
        color='turni_richiesti',
        color_continuous_scale='Blues'
    )
    
    fig_sunburst.update_layout(
        height=500,
        paper_bgcolor='rgba(15, 23, 42, 0.5)',
        font={'color': '#cbd5e1', 'size': 12}
    )
    
    st.plotly_chart(fig_sunburst, use_container_width=True)
else:
    st.warning("⚠️ Nessun dato disponibile per i filtri selezionati")

# DATI COMPLETI
with st.expander("🔍 VISUALIZZA DATASET COMPLETO"):
    if len(df_filtered) > 0:
        df_display = df_filtered.copy()
        df_display["giorno"] = df_display["giorno"].dt.strftime("%d/%m/%Y")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Nessun dato disponibile")

# FOOTER
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 30px;'>
    <p style='font-size: 1.2em; font-weight: 700; color: #60a5fa; text-shadow: 0 0 10px rgba(96, 165, 250, 0.5);'>
        🚀 ESTATE 2026 EXECUTIVE DASHBOARD
    </p>
    <p style='font-size: 0.9em; color: #93c5fd; margin-top: 10px;'>
        Powered by Streamlit + Supabase + Plotly
    </p>
    <p style='font-size: 0.85em; color: #64748b; margin-top: 5px;'>
        Ultimo aggiornamento: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
    </p>
</div>
""", unsafe_allow_html=True)
