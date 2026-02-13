import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import psycopg2

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

st.set_page_config(page_title="Estate 2026 - Staffing", layout="wide")

# --------------------------------------------------
# PASSWORD GATE
# --------------------------------------------------

def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("Password errata")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        st.secrets["DATABASE_URL"],
        sslmode="require"
    )


conn = get_connection()

cur = conn.cursor()
cur.execute("select now();")
st.write("DB OK:", cur.fetchone()[0])
cur.close()


# --------------------------------------------------
# QUERY
# --------------------------------------------------

@st.cache_data
def load_data():
    query = """
        SELECT *
        FROM v_staffing
        ORDER BY giorno, deposito;
    """
    return pd.read_sql(query, conn)

df = load_data()

df["giorno"] = pd.to_datetime(df["giorno"])

# --------------------------------------------------
# FILTRI
# --------------------------------------------------

st.sidebar.header("Filtri")

depositi = df["deposito"].unique()
deposito_sel = st.sidebar.multiselect("Deposito", depositi, default=depositi)

min_date = df["giorno"].min()
max_date = df["giorno"].max()

date_range = st.sidebar.date_input(
    "Intervallo date",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

df = df[
    (df["deposito"].isin(deposito_sel)) &
    (df["giorno"] >= pd.to_datetime(date_range[0])) &
    (df["giorno"] <= pd.to_datetime(date_range[1]))
]

# --------------------------------------------------
# GRAFICO PRINCIPALE
# --------------------------------------------------

st.title("Analisi Staffing Estate 2026")

grouped = df.groupby("giorno").agg({
    "turni_richiesti": "sum",
    "disponibili_netti": "sum",
    "gap": "sum"
}).reset_index()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=grouped["giorno"],
    y=grouped["turni_richiesti"],
    mode='lines',
    name='Turni Richiesti'
))

fig.add_trace(go.Scatter(
    x=grouped["giorno"],
    y=grouped["disponibili_netti"],
    mode='lines',
    name='Disponibili Netti'
))

fig.add_trace(go.Bar(
    x=grouped["giorno"],
    y=grouped["gap"],
    name="Gap",
    marker_color=["red" if g < 0 else "green" for g in grouped["gap"]],
    opacity=0.4
))

fig.update_layout(
    height=600,
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TABELLA DETTAGLIO
# --------------------------------------------------

st.subheader("Dettaglio Giornaliero")
st.dataframe(grouped)
