import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CCI - Proyecto Maestro", layout="wide")
st.title("🚀 Sistema de Inteligencia de Negocios - CCI")

# 2. CONEXIÓN A GOOGLE SHEETS
SHEET_ID = "1fce2t6u3QoOvyeSOMZBHdTGJhUMMnkZ0vx21e69g8zM"
URL_SHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60) # Se actualiza cada 60 segundos si hay cambios
def cargar_datos_reales():
    try:
        df = pd.read_csv(URL_SHEET)
        df.columns = df.columns.str.strip()
        
        # Limpieza de columnas numéricas según tu lista
        cols_num = ["Dias_Sin_Venta", "Promedio_Dias_Entre_Ventas", "Cantidad", "Venta_total", "Costo_total_local"]
        for c in cols_num:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
        # Crear columna de Margen si existen los datos
        if "Venta_total" in df.columns and "Costo_total_local" in df.columns:
            df['Margen_Calculado'] = df['Venta_total'] - df['Costo_total_local']
            
        return df
    except Exception as e:
        st.error(f"Error en la conexión: {e}")
        return None

df = cargar_datos_reales()

if df is not None:
    # --- FILTROS LATERALES ---
    st.sidebar.header("🔍 Filtros Avanzados")
    
    # Filtro por Estado de Rotación
    if "Estado_Rotacion" in df.columns:
        estados = ["Todos"] + sorted(df["Estado_Rotacion"].dropna().unique().tolist())
        sel_estado = st.sidebar.selectbox("Estado de Rotación:", estados)
        if sel_estado != "Todos":
            df = df[df["Estado_Rotacion"] == sel_estado]
            
    # Filtro por Marca
    if "Elemento___Marca" in df.columns:
        marcas = ["Todas"] + sorted(df["Elemento___Marca"].dropna().unique().tolist())
        sel_marca = st.sidebar.selectbox("Filtrar por Marca:", marcas)
        if sel_marca != "Todas":
            df = df[df["Elemento___Marca"] == sel_marca]

    # --- MÉTRICAS ESTRATÉGICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Items en Stock", f"{len(df):,}")
    c2.metric("Venta Total", f"${df['Venta_total'].sum():,.0f}")
    c3.metric("Días Sin Venta (Prom)", f"{df['Dias_Sin_Venta'].mean():.1f}")
    if 'Margen_Calculado' in df.columns:
        c4.metric("Margen Proyectado", f"${df['Margen_Calculado'].sum():,.0f}")

    st.divider()

    # --- GRÁFICOS ---
    col_izq, col_der = st.columns(2)
    with col_izq:
        if "Estado_Rotacion" in df.columns:
            st.subheader("Análisis de Rotación")
            fig_pie = px.pie(df, names="Estado_Rotacion", values="Venta_total", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with col_der:
        if "Dias_Sin_Venta" in df.columns:
            st.subheader("Top Productos Críticos (Días sin Venta)")
            top_criticos = df.sort_values("Dias_Sin_Venta", ascending=False).head(10)
            fig_bar = px.bar(top_criticos, x="Dias_Sin_Venta", y="Elemento", 
                             color="Dias_Sin_Venta", color_continuous_scale="OrRd")
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABLA DE DATOS ---
    st.subheader("📋 Base de Datos Operativa")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Asegúrate de que la Hoja de Google esté compartida como 'Cualquier persona con el enlace'.")
