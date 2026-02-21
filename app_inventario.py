import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="CCI - Inteligencia de Inventarios", layout="wide")
st.title("📈 Dashboard Estratégico - CCI RODAMIENTOS")

# --- LINK DE GITHUB ---
URL_GITHUB = "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202025.xlsx"

@st.cache_data(ttl=600)
def cargar_datos(fuente):
    try:
        df = pd.read_excel(fuente)
        df.columns = df.columns.str.strip()
        df["Fecha documento"] = pd.to_datetime(df["Fecha documento"], errors='coerce')
        df['Mes'] = df["Fecha documento"].dt.to_period('M').astype(str)
        for col in ["Cantidad", "Venta total", "Costo total local"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Margen'] = df["Venta total"] - df["Costo total local"]
        return df
    except:
        return None

# 2. LÓGICA DE CARGA HÍBRIDA (Nube + Manual)
# Primero intentamos cargar lo de la nube (GitHub)
df = cargar_datos(URL_GITHUB)

# Agregamos la opción de carga manual en la barra lateral
st.sidebar.header("⚙️ Configuración")
archivo_manual = st.sidebar.file_uploader("📂 Cargar otro archivo Excel:", type=["xlsx"])

# Si el usuario sube algo, reemplazamos los datos de la nube
if archivo_manual is not None:
    df_manual = cargar_datos(archivo_manual)
    if df_manual is not None:
        df = df_manual
        st.sidebar.success("✅ Usando archivo manual")
    else:
        st.sidebar.error("Archivo no compatible")

if df is None:
    st.error("No hay datos disponibles. Por favor, verifica el archivo en GitHub o sube uno manualmente.")
    st.stop()

# 3. INTERFAZ Y GRÁFICOS
# Buscador de productos
elementos = ["Todos"] + sorted(df["Elemento"].dropna().astype(str).unique().tolist())
seleccion = st.selectbox("🔍 Buscar Producto/Elemento:", elementos)

df_filtro = df if seleccion == "Todos" else df[df["Elemento"].astype(str) == seleccion]

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Movimientos", f"{len(df_filtro):,}")
c2.metric("Cant. Total", f"{int(df_filtro['Cantidad'].sum()):,}")
c3.metric("Venta Total", f"${df_filtro['Venta total'].sum():,.0f}")
total_v = df_filtro['Venta total'].sum()
total_m = df_filtro['Margen'].sum()
pct = (total_m / total_v * 100) if total_v != 0 else 0
c4.metric("Margen Total", f"${total_m:,.0f}", f"{pct:.1f}%")

st.divider()
col_izq, col_der = st.columns(2)
with col_izq:
    mensual = df_filtro.groupby('Mes')['Cantidad'].sum().reset_index()
    st.plotly_chart(px.line(mensual, x='Mes', y='Cantidad', markers=True, title="Tendencia Unidades"), use_container_width=True)
with col_der:
    top_10 = df.groupby('Elemento')['Venta total'].sum().sort_values(ascending=False).head(10).reset_index()
    st.plotly_chart(px.bar(top_10, x='Venta total', y='Elemento', orientation='h', title="Top 10 Ventas ($)"), use_container_width=True)

st.subheader("📋 Detalle de Movimientos")
st.dataframe(df_filtro, use_container_width=True)
