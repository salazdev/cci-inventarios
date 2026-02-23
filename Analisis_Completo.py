import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PESTAÑA (Navegador)
st.set_page_config(page_title="Salaz Analytics", layout="wide")

# =========================================================
# BLOQUE DE MARCA PRINCIPAL (FUERA DE CUALQUIER LÓGICA)
# =========================================================
# Este bloque se ejecuta PRIMERO y SIEMPRE se verá arriba
with st.container():
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: white; margin-bottom: 0px;">SALAZ ANALYTICS</h1>
            <p style="font-size: 20px; color: #00eb93; margin-top: 0px;">Plataforma Inteligente de Gestión</p>
            <hr style="border: 1px solid #333;">
        </div>
    """, unsafe_allow_html=True)

# 2. ENLACE AL ARCHIVO (Asegúrate de que el nombre en GitHub coincida)
URL_ANALISIS = "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Analisis_Completo.xlsx"

@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        df = pd.read_excel(url)
        # Limpiamos espacios en los nombres de las columnas por seguridad
        df.columns = df.columns.str.strip()
        
        # Convertimos columnas clave a números (por si hay errores en el Excel)
        cols_numericas = ["Cantidad_Vendida", "Venta_Total", "Costo_Total", "Margen", "%_Margen", "Dias_Sin_Venta"]
        for col in cols_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Ejecutar carga
df = cargar_datos(URL_ANALISIS)

if df is not None:
    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("⚙️ Filtros")
    
    # Filtro dinámico por Estado
    if "Estado" in df.columns:
        lista_estados = ["Todos"] + sorted(df["Estado"].dropna().unique().tolist())
        estado_sel = st.sidebar.selectbox("Filtrar por Estado:", lista_estados)
        if estado_sel != "Todos":
            df = df[df["Estado"] == estado_sel]

    # --- MÉTRICAS PRINCIPALES (KPIs) ---
    c1, c2, c3, c4 = st.columns(4)
    
    # Usamos los nombres exactos de tus columnas con guion bajo
    with c1:
        st.metric("Total Elementos", f"{len(df):,}")
    with c2:
        total_venta = df["Venta_Total"].sum()
        st.metric("Venta Total", f"${total_venta:,.0f}")
    with c3:
        margen_prom = df["%_Margen"].mean()
        st.metric("Margen Promedio", f"{margen_prom:.1f}%")
    with c4:
        max_dias = df["Dias_Sin_Venta"].max()
        st.metric("Máx. Días Sin Venta", f"{int(max_dias)} días")

    st.divider()

    # --- GRÁFICOS ---
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("📦 Distribución por Estado")
        if "Estado" in df.columns:
            # Gráfico de torta para ver cuántos productos hay en cada estado
            fig_pie = px.pie(df, names="Estado", values="Venta_Total", 
                             hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_der:
        st.subheader("📉 Top 10 Productos con más Días Sin Venta")
        if "Dias_Sin_Venta" in df.columns and "Elemento" in df.columns:
            top_quedados = df.sort_values("Dias_Sin_Venta", ascending=False).head(10)
            fig_bar = px.bar(top_quedados, x="Dias_Sin_Venta", y="Elemento", 
                             orientation='h', color="Dias_Sin_Venta",
                             color_continuous_scale="Reds")
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABLA DE DATOS ---
    st.subheader("📋 Detalle General de Análisis")
    # Buscador rápido por nombre de elemento
    busqueda = st.text_input("🔍 Buscar elemento específico:")
    if busqueda:
        df_mostrar = df[df["Elemento"].astype(str).str.contains(busqueda, case=False)]
    else:
        df_mostrar = df

    st.dataframe(df_mostrar, use_container_width=True)

else:
    st.warning("Esperando conexión con el archivo Excel en GitHub...")
    st.info("Asegúrate de que el archivo en GitHub se llame exactamente 'Analisis_Completo.xlsx'")








