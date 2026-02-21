import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración básica
st.set_page_config(page_title="CCI - Inventarios", layout="wide")
st.title("📈 Dashboard CCI RODAMIENTOS")

# FUNCION DE PROCESAMIENTO
def procesar_datos(archivo):
    try:
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip()
        
        # Ajuste de columnas numéricas
        cols_negocio = ["Cantidad", "Venta total", "Costo total local"]
        for c in cols_negocio:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
        # Ajuste de Fechas
        if "Fecha documento" in df.columns:
            df["Fecha documento"] = pd.to_datetime(df["Fecha documento"], errors='coerce')
            df['Mes'] = df["Fecha documento"].dt.to_period('M').astype(str)
        
        df['Margen'] = df["Venta total"] - df["Costo total local"]
        return df
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return None

# INTERFAZ DE CARGA (Aquí está el cambio clave)
st.markdown("### 📥 Paso 1: Cargue su archivo Excel (2024, 2025 o cualquier año)")
archivo_usuario = st.file_uploader("Seleccione el archivo desde su dispositivo:", type=["xlsx"])

if archivo_usuario is not None:
    # Solo procesamos si el usuario sube algo
    df = procesar_datos(archivo_usuario)
    
    if df is not None:
        st.success(f"✅ Archivo '{archivo_usuario.name}' cargado con éxito")
        
        # --- DASHBOARD ---
        elementos = ["Todos"] + sorted(df["Elemento"].dropna().unique().tolist())
        sel = st.selectbox("🔍 Buscar Producto:", elementos)
        df_f = df if sel == "Todos" else df[df["Elemento"] == sel]

        # KPIs
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Registros", f"{len(df_f):,}")
        c2.metric("Cant. Total", f"{int(df_f['Cantidad'].sum()):,}")
        c3.metric("Venta Total", f"${df_f['Venta total'].sum():,.0f}")
        v = df_f['Venta total'].sum()
        m = df_f['Margen'].sum()
        c4.metric("Margen %", f"{(m/v*100 if v!=0 else 0):.1f}%")

        st.divider()
        # Gráficos
        col1, col2 = st.columns(2)
        with col1:
            res_m = df_f.groupby('Mes')['Cantidad'].sum().reset_index()
            st.plotly_chart(px.line(res_m, x='Mes', y='Cantidad', title="Volumen Mensual"), use_container_width=True)
        with col2:
            top = df.groupby('Elemento')['Venta total'].sum().sort_values(ascending=False).head(10).reset_index()
            st.plotly_chart(px.bar(top, x='Venta total', y='Elemento', orientation='h', title="Top 10 Ventas"), use_container_width=True)

        st.dataframe(df_f, use_container_width=True)
else:
    st.info("👋 ¡Hola! Por favor sube un archivo de movimientos para ver el análisis.")
    st.stop()
