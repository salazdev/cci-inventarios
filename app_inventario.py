import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="CCI - Inteligencia de Inventarios", layout="wide")
st.title("📈 Dashboard Estratégico - CCI RODAMIENTOS")

# --- NOMBRES EXACTOS DE LAS COLUMNAS SEGÚN TU EXCEL ---
COL_FECHA = "Fecha documento"
COL_PRODUCTO = "Elemento"
COL_CANTIDAD = "Cantidad"
COL_VENTA = "Venta total"
COL_COSTO = "Costo total local"

# 2. CARGA DE DATOS (OPCIÓN DE SUBIR ARCHIVO)
st.sidebar.header("Configuración")
uploaded_file = st.sidebar.file_uploader("📂 Paso 1: Suba su archivo Excel", type=["xlsx"])

@st.cache_data
def procesar_datos(file):
    df = pd.read_excel(file)
    # Limpiamos espacios en los nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Convertir Fecha a formato real
    df[COL_FECHA] = pd.to_datetime(df[COL_FECHA], errors='coerce')
    # Crear columna de Mes para los gráficos (formato YYYY-MM)
    df['Mes'] = df[COL_FECHA].dt.to_period('M').astype(str)
    
    # Aseguramos que las columnas numéricas sean números
    for col in [COL_CANTIDAD, COL_VENTA, COL_COSTO]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calcular Margen Bruto (Venta - Costo)
    if COL_VENTA in df.columns and COL_COSTO in df.columns:
        df['Margen'] = df[COL_VENTA] - df[COL_COSTO]
    else:
        df['Margen'] = 0
        
    return df

# 3. EJECUCIÓN PRINCIPAL
if uploaded_file:
    try:
        df = procesar_datos(uploaded_file)
        
        # --- SOLUCIÓN AL ERROR DE ORDENAMIENTO (Lineas 42-45 aprox) ---
        # Convertimos a texto para que sorted() no falle entre números y letras
        elementos_unicos = df[COL_PRODUCTO].dropna().astype(str).unique()
        lista_elementos = ["Todos"] + sorted(elementos_unicos.tolist())
        
        st.sidebar.divider()
        seleccion_prod = st.sidebar.selectbox("🔍 Seleccionar Elemento:", lista_elementos)

        # 4. DASHBOARD
        # Filtrar según la selección
        if seleccion_prod == "Todos":
            df_actual = df
        else:
            df_actual = df[df[COL_PRODUCTO].astype(str) == seleccion_prod]

        # --- KPIs Superiores ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Movimientos", f"{len(df_actual):,}")
        c2.metric("Cant. Total", f"{int(df_actual[COL_CANTIDAD].sum()):,}")
        c3.metric("Venta Total", f"${df_actual[COL_VENTA].sum():,.0f}")
        
        # Cálculo de % de margen
        total_v = df_actual[COL_VENTA].sum()
        total_m = df_actual['Margen'].sum()
        pct_margen = (total_m / total_v * 100) if total_v != 0 else 0
        c4.metric("Margen Total", f"${total_m:,.0f}", f"{pct_margen:.1f}%")

        # --- GRÁFICOS ---
        st.divider()
        col_izq, col_der = st.columns(2)

        with col_izq:
            st.subheader("📅 Tendencia Mensual")
            # Agrupar por mes
            mensual = df_actual.groupby('Mes')[COL_CANTIDAD].sum().reset_index()
            fig_linea = px.line(mensual, x='Mes', y=COL_CANTIDAD, 
                               title=f"Unidades vendidas: {seleccion_prod}",
                               markers=True, line_shape="spline")
            st.plotly_chart(fig_linea, use_container_width=True)

        with col_der:
            st.subheader("🏆 Top 10 Productos (Ventas)")
            top_10 = df.groupby(COL_PRODUCTO)[COL_VENTA].sum().sort_values(ascending=False).head(10).reset_index()
            fig_barras = px.bar(top_10, x=COL_VENTA, y=COL_PRODUCTO, orientation='h', 
                                color=COL_VENTA, color_continuous_scale='Viridis')
            # Invertir el eje Y para que el mejor salga arriba
            fig_barras.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_barras, use_container_width=True)

        # --- TABLA DETALLADA ---
        st.subheader("📋 Detalle de Movimientos")
        st.dataframe(df_actual, use_container_width=True)

    except Exception as e:
        st.error(f"Se produjo un error al procesar el archivo: {e}")
        st.info("Revisa que el archivo tenga las columnas: 'Fecha documento', 'Elemento', 'Cantidad', 'Venta total' y 'Costo total local'.")

else:
    st.warning("👈 Por favor, sube un archivo Excel en la barra lateral para ver los indicadores.")
    # Imagen de bienvenida amigable
    st.info("Esta aplicación te permitirá ver la rotación y margen de CCI RODAMIENTOS de forma automática.")