import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="CCI - Inteligencia de Inventarios", layout="wide")
st.title("📈 Dashboard Estratégico - CCI RODAMIENTOS")

# --- LINK DE GITHUB ---
URL_GITHUB = "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202025.xlsx"

@st.cache_data
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

# 2. SECCIÓN DE CARGA
st.markdown("### 📂 Gestión de Datos")
col_info, col_subida = st.columns([2, 1])

with col_info:
    st.info("Mostrando datos de: **GitHub (Base Central)**")

with col_subida:
    archivo_nuevo = st.file_uploader("Actualizar con otro Excel:", type=["xlsx"])

# Lógica de carga
df = None
if archivo_nuevo is not None:
    df = cargar_datos(archivo_nuevo)
    st.success("✅ Usando archivo subido manualmente")
else:
    df = cargar_datos(URL_GITHUB)

if df is None:
    st.error("No se encontraron datos. Por favor sube un archivo.")
    st.stop()

# 3. FILTROS Y GRÁFICOS
st.divider()
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
    fig_linea = px.line(mensual, x='Mes', y='Cantidad', markers=True, title="Tendencia Unidades")
    st.plotly_chart(fig_linea, use_container_width=True)
with col_der:
    top_10 = df.groupby('Elemento')['Venta total'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_barras = px.bar(top_10, x='Venta total', y='Elemento', orientation='h', title="Top 10 Ventas ($)")
    st.plotly_chart(fig_barras, use_container_width=True)

st.subheader("📋 Detalle")
st.dataframe(df_filtro, use_container_width=True)
