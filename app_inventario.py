import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CCI - Dashboard", layout="wide")
st.title("📈 Dashboard Estratégico - CCI RODAMIENTOS")

# Mantenemos el link de 2025 solo como base por defecto
URL_DEFAULT = "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202025.xlsx"

@st.cache_data(ttl=300)
def procesar_excel(fuente):
    try:
        # Leemos el archivo (sea el de GitHub o el que subas tú)
        df = pd.read_excel(fuente)
        df.columns = df.columns.str.strip()
        
        # Identificar columnas numéricas dinámicamente
        for col in ["Cantidad", "Venta total", "Costo total local"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Configurar fechas
        col_fecha = "Fecha documento"
        if col_fecha in df.columns:
            df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
            df['Mes'] = df[col_fecha].dt.to_period('M').astype(str)
        
        df['Margen'] = df["Venta total"] - df["Costo total local"]
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return None

# --- LÓGICA DE CARGA (Aquí corregimos tu duda) ---
st.sidebar.header("📂 Fuente de Datos")

# Primero el botón de subida. Si hay algo aquí, mandará sobre GitHub.
archivo_usuario = st.sidebar.file_uploader("Subir archivo (2024, 2025, etc):", type=["xlsx"])

if archivo_usuario is not None:
    # SI SUBES UN ARCHIVO, USAMOS ESE Y OLVIDAMOS GITHUB
    df = procesar_excel(archivo_usuario)
    st.sidebar.success(f"✅ Cargado: {archivo_usuario.name}")
else:
    # SI NO HAS SUBIDO NADA, CARGAMOS EL 2025 DE GITHUB POR DEFECTO
    df = procesar_excel(URL_DEFAULT)
    st.sidebar.info("ℹ️ Mostrando Movimientos 2025 (GitHub)")

# --- DASHBOARD ---
if df is not None:
    # Filtro dinámico (funciona para cualquier año)
    elementos = ["Todos"] + sorted(df["Elemento"].dropna().unique().tolist())
    seleccion = st.selectbox("🔍 Seleccionar Producto:", elementos)
    df_filtro = df if seleccion == "Todos" else df[df["Elemento"] == seleccion]

    # Métricas e indicadores
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros", f"{len(df_filtro):,}")
    c2.metric("Cant. Total", f"{int(df_filtro['Cantidad'].sum()):,}")
    c3.metric("Venta Total", f"${df_filtro['Venta total'].sum():,.0f}")
    v = df_filtro['Venta total'].sum()
    m = df_filtro['Margen'].sum()
    c4.metric("Margen", f"${m:,.0f}", f"{(m/v*100 if v!=0 else 0):.1f}%")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if 'Mes' in df_filtro.columns:
            resumen = df_filtro.groupby('Mes')['Cantidad'].sum().reset_index()
            st.plotly_chart(px.line(resumen, x='Mes', y='Cantidad', title="Evolución Mensual"), use_container_width=True)
    with col2:
        top_v = df.groupby('Elemento')['Venta total'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(top_v, x='Venta total', y='Elemento', orientation='h', title="Top 10 Ventas"), use_container_width=True)

    st.dataframe(df_filtro, use_container_width=True)
else:
    st.warning("Esperando datos válidos...")
