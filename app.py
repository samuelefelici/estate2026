"""
===============================================
ESTATE 2026 - ANALISI STAFFING
===============================================
Dashboard per monitorare la copertura turni
estate 2026 per deposito e giorno.

Mostra:
- Turni richiesti vs disponibilità
- Gap di copertura
- Assenze previste
===============================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import psycopg2

# --------------------------------------------------
# CONFIGURAZIONE PAGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Estate 2026 - Staffing", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CONTROLLO PASSWORD
# --------------------------------------------------
def check_password():
    """
    Controlla la password inserita dall'utente.
    La password corretta è memorizzata nei secrets.
    """
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # Se non c'è ancora una sessione, chiedi la password
    if "password_correct" not in st.session_state:
        st.text_input(
            "🔒 Inserisci la password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    # Se la password è errata, mostra errore
    elif not st.session_state["password_correct"]:
        st.text_input(
            "🔒 Inserisci la password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("❌ Password errata")
        return False
    
    # Password corretta
    else:
        return True

# Se la password non è corretta, blocca l'app
if not check_password():
    st.stop()

# --------------------------------------------------
# CONNESSIONE AL DATABASE
# --------------------------------------------------
@st.cache_resource
def get_connection():
    """
    Crea una connessione al database PostgreSQL.
    La connessione viene cachata per evitare riconnessioni continue.
    """
    return psycopg2.connect(
        st.secrets["DATABASE_URL"],
        sslmode="require"
    )

# Connetti al database
conn = get_connection()

# Test connessione
try:
    cur = conn.cursor()
    cur.execute("SELECT NOW();")
    db_time = cur.fetchone()[0]
    cur.close()
    st.sidebar.success(f"✅ Database connesso - {db_time.strftime('%Y-%m-%d %H:%M')}")
except Exception as e:
    st.sidebar.error(f"❌ Errore database: {e}")
    st.stop()

# --------------------------------------------------
# CARICAMENTO DATI
# --------------------------------------------------
@st.cache_data(ttl=600)  # Cache per 10 minuti
def load_data():
    """
    Carica i dati dalla view v_staffing.
    La view contiene l'analisi giornaliera per deposito con:
    - Turni richiesti
    - Operatori disponibili
    - Assenze previste
    - Gap di copertura
    """
    query = """
        SELECT 
            giorno,
            tipo_giorno,
            deposito,
            turni_richiesti,
            operatori_roster,
            operatori_in_riposo,
            operatori_disponibili,
            assenze_previste,
            disponibili_netti,
            gap
        FROM v_staffing
        ORDER BY giorno, deposito;
    """
    return pd.read_sql(query, conn)

# Carica i dati
try:
    df = load_data()
    df["giorno"] = pd.to_datetime(df["giorno"])
except Exception as e:
    st.error(f"❌ Errore nel caricamento dati: {e}")
    st.stop()

# --------------------------------------------------
# FILTRI SIDEBAR
# --------------------------------------------------
st.sidebar.header("🎛️ Filtri")

# Filtro depositi
depositi = sorted(df["deposito"].unique())
deposito_sel = st.sidebar.multiselect(
    "Deposito", 
    depositi, 
    default=depositi,
    help="Seleziona uno o più depositi da analizzare"
)

# Filtro date
min_date = df["giorno"].min().date()
max_date = df["giorno"].max().date()

date_range = st.sidebar.date_input(
    "Intervallo date",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    help="Seleziona il periodo da analizzare"
)

# Applica filtri al dataframe
if len(date_range) == 2:
    df_filtered = df[
        (df["deposito"].isin(deposito_sel)) &
        (df["giorno"] >= pd.to_datetime(date_range[0])) &
        (df["giorno"] <= pd.to_datetime(date_range[1]))
    ]
else:
    df_filtered = df[df["deposito"].isin(deposito_sel)]

# --------------------------------------------------
# HEADER PRINCIPALE
# --------------------------------------------------
st.title("📊 Analisi Staffing Estate 2026")
st.markdown("---")

# --------------------------------------------------
# KPI - METRICHE PRINCIPALI
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    totale_turni = df_filtered["turni_richiesti"].sum()
    st.metric(
        "Turni Totali Richiesti", 
        f"{int(totale_turni):,}",
        help="Numero totale di turni da coprire nel periodo"
    )

with col2:
    totale_disponibili = df_filtered["disponibili_netti"].sum()
    st.metric(
        "Disponibili Netti Totali", 
        f"{int(totale_disponibili):,}",
        help="Operatori disponibili meno assenze previste"
    )

with col3:
    gap_totale = df_filtered["gap"].sum()
    delta_color = "normal" if gap_totale >= 0 else "inverse"
    st.metric(
        "Gap Totale", 
        f"{int(gap_totale):,}",
        delta=f"{'Eccedenza' if gap_totale >= 0 else 'Deficit'}",
        delta_color=delta_color,
        help="Disponibili - Richiesti (positivo = ok, negativo = carenza)"
    )

with col4:
    giorni_critici = len(df_filtered[df_filtered["gap"] < 0])
    st.metric(
        "Giorni Critici", 
        giorni_critici,
        help="Giorni con gap negativo (deficit di personale)"
    )

st.markdown("---")

# --------------------------------------------------
# GRAFICO PRINCIPALE - ANDAMENTO TEMPORALE
# --------------------------------------------------
st.subheader("📈 Andamento Temporale")

# Raggruppa per giorno (somma di tutti i depositi)
grouped = df_filtered.groupby("giorno").agg({
    "turni_richiesti": "sum",
    "disponibili_netti": "sum",
    "gap": "sum"
}).reset_index()

# Crea il grafico con Plotly
fig = go.Figure()

# Linea turni richiesti
fig.add_trace(go.Scatter(
    x=grouped["giorno"],
    y=grouped["turni_richiesti"],
    mode='lines+markers',
    name='Turni Richiesti',
    line=dict(color='#FF6B6B', width=2),
    marker=dict(size=6)
))

# Linea disponibili netti
fig.add_trace(go.Scatter(
    x=grouped["giorno"],
    y=grouped["disponibili_netti"],
    mode='lines+markers',
    name='Disponibili Netti',
    line=dict(color='#4ECDC4', width=2),
    marker=dict(size=6)
))

# Barre gap
fig.add_trace(go.Bar(
    x=grouped["giorno"],
    y=grouped["gap"],
    name="Gap",
    marker_color=["#FF6B6B" if g < 0 else "#95E1D3" for g in grouped["gap"]],
    opacity=0.5
))

# Layout del grafico
fig.update_layout(
    height=500,
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    xaxis_title="Data",
    yaxis_title="Numero Operatori/Turni"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TABELLA DETTAGLIO GIORNALIERO
# --------------------------------------------------
st.subheader("📋 Dettaglio Giornaliero")

# Mostra tabella con formattazione
st.dataframe(
    grouped.style.format({
        "turni_richiesti": "{:.0f}",
        "disponibili_netti": "{:.0f}",
        "gap": "{:.0f}"
    }).background_gradient(subset=["gap"], cmap="RdYlGn", vmin=-50, vmax=50),
    use_container_width=True
)

# --------------------------------------------------
# DETTAGLIO PER DEPOSITO
# --------------------------------------------------
st.markdown("---")
st.subheader("🏢 Analisi per Deposito")

# Raggruppa per deposito
by_deposito = df_filtered.groupby("deposito").agg({
    "turni_richiesti": "sum",
    "disponibili_netti": "sum",
    "gap": "sum"
}).reset_index().sort_values("gap")

# Grafico a barre per deposito
fig_dep = go.Figure()

fig_dep.add_trace(go.Bar(
    x=by_deposito["deposito"],
    y=by_deposito["turni_richiesti"],
    name="Turni Richiesti",
    marker_color="#FF6B6B"
))

fig_dep.add_trace(go.Bar(
    x=by_deposito["deposito"],
    y=by_deposito["disponibili_netti"],
    name="Disponibili Netti",
    marker_color="#4ECDC4"
))

fig_dep.update_layout(
    height=400,
    barmode='group',
    xaxis_title="Deposito",
    yaxis_title="Numero Operatori/Turni",
    xaxis_tickangle=-45
)

st.plotly_chart(fig_dep, use_container_width=True)

# Tabella depositi
st.dataframe(
    by_deposito.style.format({
        "turni_richiesti": "{:.0f}",
        "disponibili_netti": "{:.0f}",
        "gap": "{:.0f}"
    }).background_gradient(subset=["gap"], cmap="RdYlGn", vmin=-200, vmax=200),
    use_container_width=True
)

# --------------------------------------------------
# TABELLA COMPLETA (espandibile)
# --------------------------------------------------
with st.expander("🔍 Visualizza dati completi"):
    st.dataframe(df_filtered, use_container_width=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption("Estate 2026 - Sistema di analisi staffing | Powered by Streamlit + Supabase")
