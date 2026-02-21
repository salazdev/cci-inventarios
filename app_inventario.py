import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CCI - Dashboard", layout="wide")
st.title("📈 Dashboard Estratégico - CCI RODAMIENTOS")

URL_GITHUB = "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202025.xlsx"

@st.cache_data(ttl=300)
def cargar_datos(fuente):
    try:
        df = pd.read_excel(fuente)
        df.columns = df.columns.str.strip()
        columnas_num = ["Cantidad", "Venta total", "Costo total local"]
        for col in columnas_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df["Fecha documento"] = pd.to_datetime(df["Fecha documento"], errors='coerce')
        df['Mes'] = df["Fecha documento"].dt.to_period('M').astype(str)
        df['Margen'] = df["Venta total"] - df["Costo total local"]
        return df
    except:
        return None

# --- SECCIÓN DE CONTROL EN BARRA LATERAL ---
st.sidebar.header("🕹️ Controles de Datos")

# Opción A: Botón de subir archivo (Para tu portátil)
archivo_manual = st.sidebar.file_uploader("📂 Subir archivo manual (PC):", type=["xlsx"])

# Opción B: Botón de reset
if st.sidebar.button("🔄 Volver a datos de GitHub"):
    st.cache_data.clear()
    st.rerun()

# 2. LÓGICA DE DECISIÓN
if archivo_manual is not None:
    # Si subes algo, manda lo manual
    df = cargar_datos(archivo_manual)
    st.sidebar.success("Usando: Archivo Manual")
else:
    # Si no hay nada manual, manda GitHub
    df = cargar_datos(URL_GITHUB)
    st.sidebar.info("Usando: Base de Datos GitHub")

if df is None:
    st.error("Error al cargar los datos. Asegúrate de que el Excel sea correcto.")
    st.stop()

# 3. DASHBOARD (Gráficos y Filtros)
elementos = ["Todos"] + sorted(df["Elemento"].dropna().unique().tolist())
seleccion = st.selectbox("🔍 Buscar Producto:", elementos)
df_filtro = df if seleccion == "Todos" else df[df["Elemento"] == seleccion]

# Métricas
c1, c2, c3, c4 = st.columns(4)
c1.metric("Movimientos", f"{len(df_filtro):,}")
c2.metric("Cant. Total", f"{int(df_filtro['Cantidad'].sum()):,}")
c3.metric("Venta Total", f"${df_filtro['Venta total'].sum():,.0f}")
v = df_filtro['Venta total'].sum()
m = df_filtro['Margen'].sum()
c4.metric("Margen Total", f"${m:,.0f}", f"{(m/v*100 if v!=0 else 0):.1f}%")

st.divider()
col1, col2 = st.columns(2)
with col1:
    resumen_mes = df_filtro.groupby('Mes')['Cantidad'].sum().reset_index()
    st.plotly_chart(px.line(resumen_mes, x='Mes', y='Cantidad', title="Tendencia Unidades"), use_container_width=True)
with col2:
    top_v = df.groupby('Elemento')['Venta total'].sum().sort_values(ascending=False).head(10).reset_index()
    st.plotly_chart(px.bar(top_v, x='Venta total', y='Elemento', orientation='h', title="Top 10 Ventas $"), use_container_width=True)

st.subheader("📋 Detalle de Datos")
st.dataframe(df_filtro, use_container_width=True)
