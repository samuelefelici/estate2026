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
    page_icon="📊"
)

# CSS CUSTOM - DESIGN MIGLIORATO
st.markdown("""
<style>
    /* Background principale */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
    }
    
    /* Headers */
    h1 {
        color: white !important;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        font-weight: 800 !important;
        letter-spacing: 1px;
    }
    
    h2, h3 {
        color: white !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.3);
        font-weight: 600 !important;
    }
    
    /* Metrics - stile card */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #1e3c72 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #1e3c72 !important;
    }
    
    /* Metric containers */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(240,240,255,0.95) 100%);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Alert boxes */
    .alert-critical {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        padding: 18px;
        border-radius: 12px;
        color: white;
        font-weight: 700;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.4);
        border-left: 5px solid #7f1d1d;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 18px;
        border-radius: 12px;
        color: white;
        font-weight: 700;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
        border-left: 5px solid #b45309;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 18px;
        border-radius: 12px;
        color: white;
        font-weight: 700;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        border-left: 5px solid #047857;
    }
    
    /* Plotly charts background */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
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
except Exception as e:
    st.error(f"❌ Errore nel caricamento dati: {e}")
    st.stop()

# --------------------------------------------------
# FILTRI SIDEBAR
# --------------------------------------------------
st.sidebar.header("🎛️ CONTROLLI")

depositi = sorted(df["deposito"].unique())
deposito_sel = st.sidebar.multiselect(
    "📍 Depositi", 
    depositi, 
    default=depositi,
    help="Seleziona depositi da analizzare"
)

min_date = df["giorno"].min().date()
max_date = df["giorno"].max().date()

date_range = st.sidebar.date_input(
    "📅 Periodo Analisi",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Soglia criticità
soglia_gap = st.sidebar.slider(
    "⚠️ Soglia Gap Critico",
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
st.title("🏖️ ESTATE 2026 - EXECUTIVE DASHBOARD")
if len(date_range) == 2:
    st.markdown(f"**Periodo:** {date_range[0].strftime('%d/%m/%Y')} - {date_range[1].strftime('%d/%m/%Y')} | **Depositi:** {len(deposito_sel)}/{len(depositi)}")

st.markdown("---")

# --------------------------------------------------
# KPI EXECUTIVE - ROW 1
# --------------------------------------------------
st.markdown("### 📊 INDICATORI CHIAVE")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

# KPI 1: Totale Dipendenti
totale_dipendenti = df_depositi[df_depositi["deposito"].isin(deposito_sel)]["totale_dipendenti"].sum()
with kpi1:
    st.metric(
        "👥 Totale Dipendenti",
        f"{int(totale_dipendenti):,}",
        help="Numero totale di autisti nei depositi selezionati"
    )

# KPI 2: Turni Totali
totale_turni = int(df_filtered["turni_richiesti"].sum())
with kpi2:
    st.metric(
        "🚌 Turni Richiesti",
        f"{totale_turni:,}",
        help="Totale turni da coprire nel periodo"
    )

# KPI 3: Disponibilità Media
disponibilita_media = df_filtered["disponibili_netti"].mean()
with kpi3:
    st.metric(
        "📈 Disponibilità Media/Giorno",
        f"{disponibilita_media:.1f}",
        help="Media giornaliera operatori disponibili"
    )

# KPI 4: Gap Totale
gap_totale = int(df_filtered["gap"].sum())
delta_pct = (gap_totale / totale_turni * 100) if totale_turni > 0 else 0
with kpi4:
    st.metric(
        "⚖️ Gap Totale",
        f"{gap_totale:,}",
        delta=f"{delta_pct:.1f}%",
        delta_color="normal" if gap_totale >= 0 else "inverse",
        help="Saldo disponibilità vs richieste"
    )

# KPI 5: Assenze Previste
totale_assenze = int(df_filtered["assenze_previste"].sum())
with kpi5:
    st.metric(
        "🏥 Assenze Previste",
        f"{totale_assenze:,}",
        help="Totale assenze stimate nel periodo"
    )

st.markdown("---")

# --------------------------------------------------
# ALLARMI CRITICITÀ
# --------------------------------------------------
giorni_critici = df_filtered[df_filtered["gap"] < soglia_gap]
n_giorni_critici = len(giorni_critici)

if n_giorni_critici > 0:
    st.markdown(f"""
    <div class="alert-critical">
        🚨 <b>ALLARME CRITICITÀ</b>: {n_giorni_critici} giorni con gap inferiore a {soglia_gap}
    </div>
    """, unsafe_allow_html=True)
    
    # Mostra top 5 giorni critici
    top_critici = giorni_critici.nsmallest(5, "gap")[["giorno", "deposito", "gap", "turni_richiesti", "disponibili_netti"]].copy()
    top_critici["giorno"] = top_critici["giorno"].dt.strftime("%d/%m/%Y")
    st.dataframe(top_critici, use_container_width=True, hide_index=True)
    
elif gap_totale < 0:
    st.markdown(f"""
    <div class="alert-warning">
        ⚠️ <b>ATTENZIONE</b>: Gap totale negativo ({gap_totale}). Pianificare azioni correttive.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="alert-success">
        ✅ <b>SITUAZIONE SOTTO CONTROLLO</b>: Copertura turni garantita nel periodo.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# GRAFICI PRINCIPALE - LAYOUT 2 COLONNE
# --------------------------------------------------
col_left, col_right = st.columns([2, 1])

# --------------------------------------------------
# GRAFICO 1: ANDAMENTO TEMPORALE (SINISTRA)
# --------------------------------------------------
with col_left:
    st.markdown("### 📈 ANDAMENTO TEMPORALE STAFFING")
    
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
    
    # Plot 1: Linee turni e disponibilità
    fig_timeline.add_trace(
        go.Scatter(
            x=grouped["giorno"],
            y=grouped["turni_richiesti"],
            mode='lines+markers',
            name='Turni Richiesti',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.1)'
        ),
        row=1, col=1
    )
    
    fig_timeline.add_trace(
        go.Scatter(
            x=grouped["giorno"],
            y=grouped["disponibili_netti"],
            mode='lines+markers',
            name='Disponibili Netti',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ),
        row=1, col=1
    )
    
    # Plot 2: Barre gap
    colors = ['#dc2626' if g < soglia_gap else '#f97316' if g < 0 else '#22c55e' 
              for g in grouped["gap"]]
    
    fig_timeline.add_trace(
        go.Bar(
            x=grouped["giorno"],
            y=grouped["gap"],
            name="Gap",
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Linea soglia critica
    fig_timeline.add_hline(
        y=soglia_gap, 
        line_dash="dash", 
        line_color="#dc2626",
        annotation_text="Soglia Critica",
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
            x=1
        ),
        plot_bgcolor='rgba(255,255,255,0.95)',
        paper_bgcolor='rgba(255,255,255,0.95)'
    )
    
    fig_timeline.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig_timeline.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    st.plotly_chart(fig_timeline, use_container_width=True)

# --------------------------------------------------
# GRAFICO 2: GAUGE + ASSENZE (DESTRA)
# --------------------------------------------------
with col_right:
    st.markdown("### ⚖️ STATO COPERTURA")
    
    # Gauge chart
    gap_pct = (gap_totale / totale_turni * 100) if totale_turni > 0 else 0
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=gap_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Gap % su Turni", 'font': {'size': 18, 'color': '#1e3c72'}},
        delta={'reference': 0, 'suffix': '%'},
        number={'suffix': '%', 'font': {'size': 32, 'color': '#1e3c72'}},
        gauge={
            'axis': {'range': [-20, 20], 'tickwidth': 2, 'tickcolor': "#1e3c72"},
            'bar': {'color': "#1e3c72", 'thickness': 0.7},
            'bgcolor': "white",
            'borderwidth': 3,
            'bordercolor': "#1e3c72",
            'steps': [
                {'range': [-20, -10], 'color': '#fca5a5'},
                {'range': [-10, 0], 'color': '#fed7aa'},
                {'range': [0, 10], 'color': '#bbf7d0'},
                {'range': [10, 20], 'color': '#86efac'}
            ],
            'threshold': {
                'line': {'color': "#dc2626", 'width': 4},
                'thickness': 0.75,
                'value': (soglia_gap / totale_turni * 100) if totale_turni > 0 else 0
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=280,
        paper_bgcolor='rgba(255,255,255,0.95)',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # --------------------------------------------------
    # BREAKDOWN ASSENZE
    # --------------------------------------------------
    st.markdown("### 🏥 COMPOSIZIONE ASSENZE")
    
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
    
    # Filtra solo valori > 0
    assenze_breakdown = assenze_breakdown[assenze_breakdown['Totale'] > 0]
    
    if len(assenze_breakdown) > 0:
        fig_assenze = go.Figure(data=[go.Pie(
            labels=assenze_breakdown['Tipo'],
            values=assenze_breakdown['Totale'],
            hole=.4,
            marker_colors=['#ef4444', '#f97316', '#eab308', '#84cc16', '#06b6d4', '#8b5cf6'],
            textinfo='label+percent',
            textfont=dict(size=11, color='white')
        )])
        
        fig_assenze.update_layout(
            height=280,
            showlegend=False,
            paper_bgcolor='rgba(255,255,255,0.95)',
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig_assenze, use_container_width=True)
    else:
        st.info("📊 Nessuna assenza prevista nel periodo selezionato")

st.markdown("---")

# --------------------------------------------------
# HEATMAP CRITICITÀ PER DEPOSITO
# --------------------------------------------------
st.markdown("### 🗺️ HEATMAP CRITICITÀ PER DEPOSITO/GIORNO")

if len(df_filtered) > 0:
    # Pivot table per heatmap
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
            [0, '#dc2626'],
            [0.45, '#f97316'],
            [0.5, '#fef3c7'],
            [0.55, '#86efac'],
            [1, '#22c55e']
        ],
        zmid=0,
        text=pivot_gap.values,
        texttemplate='%{text:.0f}',
        textfont={"size": 10},
        colorbar=dict(title="Gap", titleside="right")
    ))
    
    fig_heatmap.update_layout(
        height=max(300, len(pivot_gap) * 40),
        xaxis_title="Giorno",
        yaxis_title="Deposito",
        paper_bgcolor='rgba(255,255,255,0.95)',
        plot_bgcolor='rgba(255,255,255,0.95)'
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.warning("⚠️ Nessun dato disponibile per i filtri selezionati")

st.markdown("---")

# --------------------------------------------------
# ANALISI PER DEPOSITO
# --------------------------------------------------
st.markdown("### 🏢 RANKING DEPOSITI")

if len(df_filtered) > 0:
    by_deposito = df_filtered.groupby("deposito").agg({
        "turni_richiesti": "sum",
        "disponibili_netti": "sum",
        "gap": "sum",
        "assenze_previste": "sum"
    }).reset_index()
    
    # Merge con stats depositi
    by_deposito = by_deposito.merge(df_depositi, on="deposito", how="left")
    
    # Converti a int
    by_deposito["turni_richiesti"] = by_deposito["turni_richiesti"].astype(int)
    by_deposito["disponibili_netti"] = by_deposito["disponibili_netti"].astype(int)
    by_deposito["gap"] = by_deposito["gap"].astype(int)
    by_deposito["assenze_previste"] = by_deposito["assenze_previste"].astype(int)
    
    # Calcola tasso copertura
    by_deposito["tasso_copertura_%"] = (
        (by_deposito["disponibili_netti"] / by_deposito["turni_richiesti"] * 100)
        .fillna(0)
        .round(1)
    )
    
    # Ordina per gap
    by_deposito = by_deposito.sort_values("gap")
    
    # Grafico a barre orizzontali
    fig_depositi = go.Figure()
    
    colors_dep = ['#dc2626' if g < soglia_gap else '#f97316' if g < 0 else '#22c55e' 
                  for g in by_deposito["gap"]]
    
    fig_depositi.add_trace(go.Bar(
        y=by_deposito["deposito"],
        x=by_deposito["gap"],
        orientation='h',
        marker=dict(color=colors_dep),
        text=by_deposito["gap"],
        textposition='outside',
        texttemplate='%{text:.0f}',
        hovertemplate='<b>%{y}</b><br>Gap: %{x:.0f}<extra></extra>'
    ))
    
    fig_depositi.update_layout(
        height=max(400, len(by_deposito) * 35),
        xaxis_title="Gap (positivo = eccedenza, negativo = deficit)",
        yaxis_title="",
        paper_bgcolor='rgba(255,255,255,0.95)',
        plot_bgcolor='rgba(255,255,255,0.95)',
        showlegend=False
    )
    
    fig_depositi.add_vline(x=0, line_width=3, line_dash="dash", line_color="#1e3c72")
    
    st.plotly_chart(fig_depositi, use_container_width=True)
    
    # Tabella depositi - SENZA background_gradient
    st.dataframe(
        by_deposito[[
            "deposito", 
            "totale_dipendenti",
            "turni_richiesti", 
            "disponibili_netti", 
            "assenze_previste",
            "gap",
            "tasso_copertura_%"
        ]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("⚠️ Nessun dato disponibile per i filtri selezionati")

st.markdown("---")

# --------------------------------------------------
# SUNBURST: VISIONE GERARCHICA
# --------------------------------------------------
st.markdown("### 🌅 DISTRIBUZIONE GERARCHICA TURNI")

if len(df_filtered) > 0:
    df_sunburst = df_filtered.groupby(["deposito", "tipo_giorno"]).agg({
        "turni_richiesti": "sum"
    }).reset_index()
    
    df_sunburst["turni_richiesti"] = df_sunburst["turni_richiesti"].astype(int)
    
    fig_sunburst = px.sunburst(
        df_sunburst,
        path=['deposito', 'tipo_giorno'],
        values='turni_richiesti',
        color='turni_richiesti',
        color_continuous_scale='Viridis'
    )
    
    fig_sunburst.update_layout(
        height=500,
        paper_bgcolor='rgba(255,255,255,0.95)'
    )
    
    st.plotly_chart(fig_sunburst, use_container_width=True)
else:
    st.warning("⚠️ Nessun dato disponibile per i filtri selezionati")

# --------------------------------------------------
# DATI COMPLETI
# --------------------------------------------------
with st.expander("🔍 VISUALIZZA DATASET COMPLETO"):
    if len(df_filtered) > 0:
        df_display = df_filtered.copy()
        df_display["giorno"] = df_display["giorno"].dt.strftime("%d/%m/%Y")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Nessun dato disponibile")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: white; padding: 20px;'>
    <p style='font-size: 1em; font-weight: 600;'>
        🚀 <b>Estate 2026 Executive Dashboard</b> | Powered by Streamlit + Supabase + Plotly
    </p>
    <p style='font-size: 0.85em; opacity: 0.9;'>
        Ultimo aggiornamento: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
    </p>
</div>
""", unsafe_allow_html=True)
