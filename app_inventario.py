import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Salaz Analytics", layout="wide")

# Marca Personalizada
st.markdown("""
    <div style="text-align: left;">
        <h3 style="margin-bottom: 0px; color: #00eb93; letter-spacing: 1px;">SALAZ ANALYTICS</h3>
        <p style="font-size: 12px; color: gray; margin-top: 0px;">PLATAFORMA INTELIGENTE DE GESTIÓN</p>
    </div>
""", unsafe_allow_html=True)
st.divider()

# 2. CONFIGURACIÓN DE FUENTES (Tu Link de Drive ya integrado)
ID_DRIVE = "19qgKGn1RjoSE9DBEntQavxLGyl9NXb12"
URL_DRIVE_DIRECTO = f"https://docs.google.com/spreadsheets/d/{ID_DRIVE}/export?format=xlsx"

ARCHIVOS_FIJOS = {
    "📦 Pedidos Sugeridos (Google Drive)": URL_DRIVE_DIRECTO,
    "📊 Movimientos 2025": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202025.xlsx",
    "📊 Movimientos 2024": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202024.xlsx",
    "🚀 Análisis Avanzado": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Analisis_Completo.xlsx"
}

@st.cache_data(ttl=300) # Se actualiza cada 5 minutos
def cargar_excel(url):
    try:
        return pd.read_excel(url)
    except:
        return None

# 3. BARRA LATERAL (Menú y Carga de Archivos)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1006/1006158.png", width=80)
st.sidebar.title("Panel de Control")

opcion = st.sidebar.selectbox("Ver Tablero:", list(ARCHIVOS_FIJOS.keys()))

st.sidebar.divider()
st.sidebar.subheader("📁 Carga Manual de Ventas")
archivo_manual = st.sidebar.file_uploader("Subir Excel de Ventas Recientes", type=["xlsx"])

# 4. PROCESAMIENTO DE DATOS
df_principal = cargar_excel(ARCHIVOS_FIJOS[opcion])

if df_principal is not None:
    
    # --- LÓGICA ESPECIAL PARA PEDIDOS SUGERIDOS ---
    if "Pedidos Sugeridos" in opcion:
        st.header("📢 Gestión de Importaciones y Pedidos")
        
        # Alerta de 4 meses
        llegada_estimada = datetime.now() + timedelta(days=120)
        st.info(f"💡 **Nota de Logística:** Los pedidos realizados hoy llegarán aproximadamente el **{llegada_estimada.strftime('%d de Junio, 2026')}**.")

        # Si el usuario subió un archivo manual, comparamos
        if archivo_manual:
            df_ventas = pd.read_excel(archivo_manual)
            st.success("✅ Archivo de ventas cargado. Comparando con sugeridos de Drive...")
            
            # Aquí podrías hacer un merge/cruce si las columnas coinciden
            # Ejemplo: df_comparativo = pd.merge(df_principal, df_ventas, on="Referencia")
        
        # Gráficos de Alerta basados en tu Excel (Imagen enviada)
        if "Pedido 4 meses" in df_principal.columns:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Referencias", len(df_principal))
            c2.metric("Unidades a Pedir", f"{int(df_principal['Pedido 4 meses'].sum()):,}")
            
            # Gráfico de Barras: Top Pedidos
            st.subheader("🔥 Top 10 Pedidos Urgentes")
            fig = px.bar(df_principal.nlargest(10, 'Pedido 4 meses'), 
                         x='Pedido 4 meses', y='Referencia', orientation='h',
                         color='Pedido 4 meses', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)

    # --- TABLA DE DATOS ---
    st.subheader(f"📋 Datos actuales: {opcion}")
    st.dataframe(df_principal, use_container_width=True)

else:
    st.error("⚠️ No se pudo conectar con el archivo. Asegúrate de que el Drive tenga el acceso de 'Cualquier persona con el enlace'.")

# 5. PIE DE PÁGINA
st.markdown("---")
st.caption("SALAZ ANALYTICS | Gestión de Datos en Tiempo Real")
