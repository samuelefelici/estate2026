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

# FORCE CACHE CLEAR (rimuovi dopo il primo run)
st.cache_data.clear()
st.cache_resource.clear()

# --------------------------------------------------
# CONFIGURAZIONE PAGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Estate 2026 - Executive Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# CSS CUSTOM - DESIGN FUTURISTICO
st.markdown("""
<style>
    /* Gradient background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card containers */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin: 10px 0;
    }
    
    /* Headers */
    h1 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-weight: 700 !important;
    }
    
    h2, h3 {
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Alert boxes */
    .alert-critical {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 15px;
        border-radius: 10px;
        color: #333;
        font-weight: 600;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(252, 182, 159, 0.4);
    }
    
    .alert-success {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 15px;
        border-radius: 10px;
        color: #333;
        font-weight: 600;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(168, 237, 234, 0.4);
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
    ]
else:
    df_filtered = df[df["deposito"].isin(deposito_sel)]

# --------------------------------------------------
# HEADER
# --------------------------------------------------
col_logo, col_title = st.columns([1, 4])

with col_title:
    st.title("🏖️ ESTATE 2026 - EXECUTIVE DASHBOARD")
    st.markdown(f"**Periodo:** {date_range[0].strftime('%d/%m/%Y')} - {date_range[1].strftime('%d/%m/%Y')}")

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
totale_turni = df_filtered["turni_richiesti"].sum()
with kpi2:
    st.metric(
        "🚌 Turni Richiesti",
        f"{int(totale_turni):,}",
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
gap_totale = df_filtered["gap"].sum()
delta_pct = (gap_totale / totale_turni * 100) if totale_turni > 0 else 0
with kpi4:
    st.metric(
        "⚖️ Gap Totale",
        f"{int(gap_totale):,}",
        delta=f"{delta_pct:.1f}%",
        delta_color="normal" if gap_totale >= 0 else "inverse",
        help="Saldo disponibilità vs richieste"
    )

# KPI 5: Assenze Previste
totale_assenze = df_filtered["assenze_previste"].sum()
with kpi5:
    st.metric(
        "🏥 Assenze Previste",
        f"{int(totale_assenze):,}",
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
    top_critici = giorni_critici.nsmallest(5, "gap")[["giorno", "deposito", "gap", "turni_richiesti", "disponibili_netti"]]
    st.dataframe(
        top_critici.style.format({"giorno": lambda x: x.strftime("%d/%m/%Y")}),
        use_container_width=True
    )
elif gap_totale < 0:
    st.markdown(f"""
    <div class="alert-warning">
        ⚠️ <b>ATTENZIONE</b>: Gap totale negativo ({int(gap_totale)}). Pianificare azioni correttive.
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
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.1)'
        ),
        row=1, col=1
    )
    
    fig_timeline.add_trace(
        go.Scatter(
            x=grouped["giorno"],
            y=grouped["disponibili_netti"],
            mode='lines+markers',
            name='Disponibili Netti',
            line=dict(color='#4ECDC4', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(78, 205, 196, 0.1)'
        ),
        row=1, col=1
    )
    
    # Plot 2: Barre gap
    colors = ['#FF6B6B' if g < soglia_gap else '#FFA07A' if g < 0 else '#95E1D3' 
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
        line_color="red",
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
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(255,255,255,0.9)'
    )
    
    fig_timeline.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig_timeline.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    st.plotly_chart(fig_timeline, use_container_width=True)

# --------------------------------------------------
# GRAFICO 2: GAUGE GAP TOTALE (DESTRA)
# --------------------------------------------------
with col_right:
    st.markdown("### ⚖️ STATO COPERTURA")
    
    # Gauge chart
    gap_pct = (gap_totale / totale_turni * 100) if totale_turni > 0 else 0
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=gap_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Gap % su Turni", 'font': {'size': 20}},
        delta={'reference': 0, 'suffix': '%'},
        gauge={
            'axis': {'range': [-20, 20], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [-20, -10], 'color': '#FF6B6B'},
                {'range': [-10, 0], 'color': '#FFA07A'},
                {'range': [0, 10], 'color': '#95E1D3'},
                {'range': [10, 20], 'color': '#4ECDC4'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': (soglia_gap / totale_turni * 100) if totale_turni > 0 else 0
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=280,
        paper_bgcolor='rgba(255,255,255,0.9)',
        font={'color': "darkgray", 'family': "Arial"}
    )
    
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # --------------------------------------------------
    # BREAKDOWN ASSENZE
    # --------------------------------------------------
    st.markdown("### 🏥 COMPOSIZIONE ASSENZE")
    
    assenze_breakdown = pd.DataFrame({
        'Tipo': ['Infortuni', 'Malattie', 'Legge 104', 'Congedi', 'Permessi', 'Altro'],
        'Totale': [
            df_filtered['infortuni'].sum(),
            df_filtered['malattie'].sum(),
            df_filtered['legge_104'].sum(),
            df_filtered['congedo_parentale'].sum(),
            df_filtered['permessi_vari'].sum(),
            df_filtered['altre_assenze'].sum()
        ]
    })
    
    fig_assenze = go.Figure(data=[go.Pie(
        labels=assenze_breakdown['Tipo'],
        values=assenze_breakdown['Totale'],
        hole=.4,
        marker_colors=['#FF6B6B', '#FFA07A', '#FFD93D', '#6BCB77', '#4D96FF', '#A8DADC']
    )])
    
    fig_assenze.update_layout(
        height=280,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1),
        paper_bgcolor='rgba(255,255,255,0.9)',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig_assenze, use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# HEATMAP CRITICITÀ PER DEPOSITO
# --------------------------------------------------
st.markdown("### 🗺️ HEATMAP CRITICITÀ PER DEPOSITO/GIORNO")

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
        [0, '#FF6B6B'],      # Rosso per gap negativi
        [0.45, '#FFA07A'],   # Arancione
        [0.5, '#FFFFCC'],    # Giallo neutro
        [0.55, '#95E1D3'],   # Verde chiaro
        [1, '#4ECDC4']       # Verde per gap positivi
    ],
    zmid=0,
    text=pivot_gap.values,
    texttemplate='%{text:.0f}',
    textfont={"size": 10},
    colorbar=dict(title="Gap")
))

fig_heatmap.update_layout(
    height=400,
    xaxis_title="Giorno",
    yaxis_title="Deposito",
    paper_bgcolor='rgba(255,255,255,0.9)',
    plot_bgcolor='rgba(255,255,255,0.9)'
)

st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# ANALISI PER DEPOSITO
# --------------------------------------------------
st.markdown("### 🏢 RANKING DEPOSITI")

by_deposito = df_filtered.groupby("deposito").agg({
    "turni_richiesti": "sum",
    "disponibili_netti": "sum",
    "gap": "sum",
    "assenze_previste": "sum"
}).reset_index()

# Merge con stats depositi
by_deposito = by_deposito.merge(df_depositi, on="deposito", how="left")

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

fig_depositi.add_trace(go.Bar(
    y=by_deposito["deposito"],
    x=by_deposito["gap"],
    orientation='h',
    marker=dict(
        color=by_deposito["gap"],
        colorscale=[
            [0, '#FF6B6B'],
            [0.5, '#FFFFCC'],
            [1, '#4ECDC4']
        ],
        cmin=by_deposito["gap"].min(),
        cmax=by_deposito["gap"].max(),
        colorbar=dict(title="Gap")
    ),
    text=by_deposito["gap"],
    textposition='outside',
    texttemplate='%{text:.0f}',
    hovertemplate='<b>%{y}</b><br>Gap: %{x:.0f}<extra></extra>'
))

fig_depositi.update_layout(
    height=max(400, len(by_deposito) * 30),
    xaxis_title="Gap (positivo = eccedenza, negativo = deficit)",
    yaxis_title="",
    paper_bgcolor='rgba(255,255,255,0.9)',
    plot_bgcolor='rgba(255,255,255,0.9)',
    showlegend=False
)

fig_depositi.add_vline(x=0, line_width=2, line_dash="dash", line_color="black")

st.plotly_chart(fig_depositi, use_container_width=True)

# Tabella depositi
st.dataframe(
    by_deposito[[
        "deposito", 
        "totale_dipendenti",
        "turni_richiesti", 
        "disponibili_netti", 
        "assenze_previste",
        "gap",
        "tasso_copertura_%"
    ]].style.format({
        "totale_dipendenti": "{:.0f}",
        "turni_richiesti": "{:.0f}",
        "disponibili_netti": "{:.0f}",
        "assenze_previste": "{:.0f}",
        "gap": "{:.0f}",
        "tasso_copertura_%": "{:.1f}%"
    }).background_gradient(subset=["gap"], cmap="RdYlGn", vmin=-100, vmax=100)
    .background_gradient(subset=["tasso_copertura_%"], cmap="RdYlGn", vmin=80, vmax=120),
    use_container_width=True
)

st.markdown("---")

# --------------------------------------------------
# SUNBURST: VISIONE GERARCHICA
# --------------------------------------------------
st.markdown("### 🌅 DISTRIBUZIONE GERARCHICA TURNI")

# Prepara dati per sunburst
df_sunburst = df_filtered.groupby(["deposito", "tipo_giorno"]).agg({
    "turni_richiesti": "sum"
}).reset_index()

fig_sunburst = px.sunburst(
    df_sunburst,
    path=['deposito', 'tipo_giorno'],
    values='turni_richiesti',
    color='turni_richiesti',
    color_continuous_scale='Viridis',
    title=""
)

fig_sunburst.update_layout(
    height=500,
    paper_bgcolor='rgba(255,255,255,0.9)'
)

st.plotly_chart(fig_sunburst, use_container_width=True)

# --------------------------------------------------
# DATI COMPLETI
# --------------------------------------------------
with st.expander("🔍 VISUALIZZA DATASET COMPLETO"):
    st.dataframe(
        df_filtered.style.format({
            "giorno": lambda x: x.strftime("%d/%m/%Y")
        }),
        use_container_width=True
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; padding: 20px;'>
    <p style='font-size: 0.9em;'>
        🚀 <b>Estate 2026 Executive Dashboard</b> | Powered by Streamlit + Supabase + Plotly
    </p>
    <p style='font-size: 0.8em; opacity: 0.8;'>
        Ultimo aggiornamento: {now}
    </p>
</div>
""".format(now=datetime.now().strftime("%d/%m/%Y %H:%M:%S")), unsafe_allow_html=True)
