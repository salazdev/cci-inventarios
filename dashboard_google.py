import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="CCI - Google Sheets Live", layout="wide")
st.title("🚀 Dashboard Automatizado (Google Sheets)")

# 2. TU ID DE HOJA CONFIGURADO
SHEET_ID = "1fce2t6u3QoOvyeSOMZBHdTGJhUMMnkZ0vx21e69g8zM"
URL_SHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60) # Se actualiza cada minuto si hay cambios en el Sheet
def cargar_datos_google():
    try:
        # Cargamos los datos desde Google
        df = pd.read_csv(URL_SHEET)
        df.columns = df.columns.str.strip()
        
        # Limpieza de columnas numéricas (usando tus nombres de columna)
        cols_num = ["Venta_Total", "Cantidad_Vendida", "Costo_Total", "Margen", "Dias_Sin_Venta"]
        for c in cols_num:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None

df = cargar_datos_google()

if df is not None:
    # --- FILTRO LATERAL ---
    st.sidebar.header("Filtros")
    if "Estado" in df.columns:
        estados = ["Todos"] + sorted(df["Estado"].dropna().unique().tolist())
        sel_estado = st.sidebar.selectbox("Estado del Inventario:", estados)
        if sel_estado != "Todos":
            df = df[df["Estado"] == sel_estado]

    # --- MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Items", len(df))
    if "Venta_Total" in df.columns:
        c2.metric("Venta Total", f"${df['Venta_Total'].sum():,.0f}")
    if "Margen" in df.columns:
        c3.metric("Margen Total", f"${df['Margen'].sum():,.0f}")
    if "Dias_Sin_Venta" in df.columns:
        c4.metric("Días Sin Venta (Prom)", f"{df['Dias_Sin_Venta'].mean():.1f}")

    st.divider()

    # --- GRÁFICOS ---
    col_a, col_b = st.columns(2)
    with col_a:
        if "Estado" in df.columns:
            st.subheader("Análisis por Estado")
            fig_pie = px.pie(df, names="Estado", values="Venta_Total", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_b:
        if "Elemento" in df.columns:
            st.subheader("Top 10 Ventas por Producto")
            top_10 = df.sort_values("Venta_Total", ascending=False).head(10)
            fig_bar = px.bar(top_10, x="Venta_Total", y="Elemento", orientation='h', color="Venta_Total")
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABLA ---
    st.subheader("📋 Datos en Tiempo Real")
    st.dataframe(df, use_container_width=True)

else:
    st.info("Asegúrate de que la hoja de Google Sheets tenga permisos de 'Cualquier persona con el enlace puede leer'.")