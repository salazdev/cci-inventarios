import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CCI - Dashboard", layout="wide")
st.title("📈 Dashboard Estratégico - CCI RODAMIENTOS")

# 2. BASE DE DATOS EN LA NUBE (Configura tus links aquí)
# Reemplaza estos links con los "Raw" de tus archivos en GitHub
ARCHIVOS_DISPONIBLES = {
    "Año 2025": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202025.xlsx",
    "Año 2024": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202024.xlsx",
    "Año 2023": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202023.xlsx"# Asegúrate de que este archivo exista en tu GitHub
}

@st.cache_data(ttl=600)
def cargar_datos_nube(url):
    try:
        df = pd.read_excel(url)
        df.columns = df.columns.str.strip()
        for col in ["Cantidad", "Venta total", "Costo total local"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        if "Fecha documento" in df.columns:
            df["Fecha documento"] = pd.to_datetime(df["Fecha documento"], errors='coerce')
            df['Mes'] = df["Fecha documento"].dt.to_period('M').astype(str)
        df['Margen'] = df["Venta total"] - df["Costo total local"]
        return df
    except Exception as e:
        return None

# 3. INTERFAZ DE SELECCIÓN (Funciona perfecto en celular)
st.sidebar.header("📂 Selección de Datos")
seleccion_año = st.sidebar.selectbox("¿Qué año desea consultar?", list(ARCHIVOS_DISPONIBLES.keys()))

# Botón de refresco manual
if st.sidebar.button("🔄 Sincronizar con GitHub"):
    st.cache_data.clear()
    st.rerun()

# CARGA DE DATOS
url_elegida = ARCHIVOS_DISPONIBLES[seleccion_año]
df = cargar_datos_nube(url_elegida)

if df is not None:
    st.success(f"✅ Visualizando datos de: {seleccion_año}")
    
    # --- DASHBOARD ---
    elementos = ["Todos"] + sorted(df["Elemento"].dropna().unique().tolist())
    sel_prod = st.selectbox("🔍 Buscar Producto:", elementos)
    df_f = df if sel_prod == "Todos" else df[df["Elemento"] == sel_prod]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros", f"{len(df_f):,}")
    c2.metric("Cant. Total", f"{int(df_f['Cantidad'].sum()):,}")
    c3.metric("Venta Total", f"${df_f['Venta total'].sum():,.0f}")
    v = df_f['Venta total'].sum()
    m = df_f['Margen'].sum()
    c4.metric("Margen %", f"{(m/v*100 if v!=0 else 0):.1f}%")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        res_m = df_f.groupby('Mes')['Cantidad'].sum().reset_index()
        st.plotly_chart(px.line(res_m, x='Mes', y='Cantidad', title="Volumen Mensual"), use_container_width=True)
    with col2:
        top = df.groupby('Elemento')['Venta total'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(top, x='Venta total', y='Elemento', orientation='h', title="Top 10 Ventas"), use_container_width=True)

    st.dataframe(df_f, use_container_width=True)
else:
    st.error("⚠️ El archivo seleccionado no se encuentra en GitHub o el enlace es incorrecto.")

