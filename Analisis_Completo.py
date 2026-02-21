import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="CCI - Análisis Completo", layout="wide")
st.title("📊 Análisis de Inventario y Ventas - CCI")

# 2. ENLACE AL NUEVO ARCHIVO (Reemplaza con tu link Raw de GitHub)
URL_ANALISIS = "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Analisis_Completo.xlsx"

@st.cache_data(ttl=300)
def cargar_analisis(url):
    try:
        df = pd.read_excel(url)
        df.columns = df.columns.str.strip()
        
        # Convertir a números las columnas clave
        cols_num = ["Venta Total", "Cantidad", "%_Margen", "Días Sin Venta"]
        for c in cols_num:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        return df
    except:
        return None

df = cargar_analisis(URL_ANALISIS)

if df is not None:
    # --- FILTROS ---
    st.sidebar.header("Filtros de Análisis")
    # Filtro por Estado (Nuevo)
    if "Estado" in df.columns:
        estados = ["Todos"] + list(df["Estado"].unique())
        sel_estado = st.sidebar.selectbox("Filtrar por Estado:", estados)
        if sel_estado != "Todos":
            df = df[df["Estado"] == sel_estado]

    # --- MÉTRICAS PRINCIPALES ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Productos Analizados", len(df))
    with c2:
        st.metric("Venta Total Sum.", f"${df['Venta Total'].sum():,.0f}")
    with c3:
        st.metric("Promedio Margen", f"{df['%_Margen'].mean():.1f}%")
    with c4:
        st.metric("Máx. Días Sin Venta", f"{df['Días Sin Venta'].max()} días")

    st.divider()

    # --- GRÁFICOS ESTRATÉGICOS ---
    col_izq, col_der = st.columns(2)

    with col_izq:
        if "Estado" in df.columns:
            st.subheader("Distribución por Estado")
            fig_pie = px.pie(df, names="Estado", values="Venta Total", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_der:
        st.subheader("Días Sin Venta por Producto (Top 10)")
        top_dias = df.sort_values("Días Sin Venta", ascending=False).head(10)
        fig_bar = px.bar(top_dias, x="Días Sin Venta", y="Producto", orientation='h', color="Días Sin Venta")
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABLA DETALLADA ---
    st.subheader("📋 Detalle de Análisis Completo")
    st.dataframe(df, use_container_width=True)

else:
    st.error("No se pudo cargar el archivo 'Analisis_Completo.xlsx'. Verifica el link en GitHub.")