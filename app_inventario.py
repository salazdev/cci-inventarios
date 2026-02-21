import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="CCI - Inteligencia de Inventarios", layout="wide")
st.title("📈 Dashboard Estratégico - CCI RODAMIENTOS")

# --- LINK DE GITHUB YA VALIDADO ---
URL_GITHUB = "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202025.xlsx"

# Nombres de columnas
COL_FECHA = "Fecha documento"
COL_PRODUCTO = "Elemento"
COL_CANTIDAD = "Cantidad"
COL_VENTA = "Venta total"
COL_COSTO = "Costo total local"

@st.cache_data
def cargar_datos(fuente):
    df = pd.read_excel(fuente)
    df.columns = df.columns.str.strip()
    df[COL_FECHA] = pd.to_datetime(df[COL_FECHA], errors='coerce')
    df['Mes'] = df[COL_FECHA].dt.to_period('M').astype(str)
    for col in [COL_CANTIDAD, COL_VENTA, COL_COSTO]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['Margen'] = df[COL_VENTA] - df[COL_COSTO]
    return df

# 2. CARGA DE DATOS
df = None

# Intentamos cargar desde GitHub primero para tener datos por defecto
try:
    df = cargar_datos(URL_GITHUB)
except:
    pass

# AGREGAMOS ESTO: Un cargador manual que siempre esté visible en la barra lateral
st.sidebar.header("Configuración de Datos")
archivo_nuevo = st.sidebar.file_uploader("📂 Subir nuevo Excel (Opcional):", type=["xlsx"])

# Si el usuario sube un archivo, reemplazamos los datos de GitHub
if archivo_nuevo is not None:
    df = cargar_datos(archivo_nuevo)
    st.sidebar.success("✅ Usando archivo subido manualmente")

# Si no hay archivo en GitHub ni manual, detenemos la app
if df is None:
    st.info("Por favor, suba un archivo Excel para comenzar.")
    st.stop()

# 3. INTERFAZ Y GRÁFICOS (Recuperando el diseño anterior)
if df is not None:
    # Filtro de Producto
    elementos = ["Todos"] + sorted(df[COL_PRODUCTO].dropna().astype(str).unique().tolist())
    seleccion = st.sidebar.selectbox("🔍 Seleccionar Producto:", elementos)

    df_filtro = df if seleccion == "Todos" else df[df[COL_PRODUCTO].astype(str) == seleccion]

    # --- KPIs Superiores ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Movimientos", f"{len(df_filtro):,}")
    c2.metric("Cant. Total", f"{int(df_filtro[COL_CANTIDAD].sum()):,}")
    c3.metric("Venta Total", f"${df_filtro[COL_VENTA].sum():,.0f}")
    
    total_v = df_filtro[COL_VENTA].sum()
    total_m = df_filtro['Margen'].sum()
    pct_margen = (total_m / total_v * 100) if total_v != 0 else 0
    c4.metric("Margen Total", f"${total_m:,.0f}", f"{pct_margen:.1f}%")

    st.divider()

    # --- Las dos columnas de Gráficos ---
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("📅 Tendencia Mensual (Unidades)")
        mensual = df_filtro.groupby('Mes')[COL_CANTIDAD].sum().reset_index()
        fig_linea = px.line(mensual, x='Mes', y=COL_CANTIDAD, markers=True, 
                            title=f"Ventas de: {seleccion}")
        st.plotly_chart(fig_linea, use_container_width=True)

    with col_der:
        st.subheader("🏆 Top 10 Productos (Ventas $)")
        top_10 = df.groupby(COL_PRODUCTO)[COL_VENTA].sum().sort_values(ascending=False).head(10).reset_index()
        fig_barras = px.bar(top_10, x=COL_VENTA, y=COL_PRODUCTO, orientation='h', 
                            color=COL_VENTA, color_continuous_scale='Blues')
        fig_barras.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_barras, use_container_width=True)

    # Tabla de datos al final
    st.subheader("📋 Detalle de Movimientos")
    st.dataframe(df_filtro, use_container_width=True)

