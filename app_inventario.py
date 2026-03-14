import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io  # Necesario para la descarga de archivos

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Salaz Analytics", layout="wide")

# Marca Personalizada
st.markdown("""
    <div style="text-align: left;">
        <h3 style="margin-bottom: 0px; color: #00eb93; letter-spacing: 1px;">Salaz Analytics</h3>
        <p style="font-size: 12px; color: gray; margin-top: 0px;">PLATAFORMA INTELIGENTE DE GESTIÓN</p>
    </div>
""", unsafe_allow_html=True)
st.divider()

# --- FUNCIÓN DE CONVERSIÓN A EXCEL ---
def convertir_a_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos_Salaz_Analytics')
    return output.getvalue()

# 2. CONFIGURACIÓN DE FUENTES
ID_DRIVE = "19qgKGn1RjoSE9DBEntQavxLGyl9NXb12"
URL_DRIVE_DIRECTO = f"https://docs.google.com/spreadsheets/d/{ID_DRIVE}/export?format=xlsx"

ARCHIVOS_FIJOS = {
    "📦 Pedidos Sugeridos (Google Drive)": URL_DRIVE_DIRECTO,
    "📊 Movimientos 2025": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202025.xlsx",
    "🚀 Análisis Avanzado": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Analisis_Completo.xlsx",
    "   Informe_Gerencial": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Informe_Comercial_Gerencial.xlsx"
}

@st.cache_data(ttl=300)
def cargar_excel(url):
    try:
        return pd.read_excel(url)
    except:
        return None

# 3. BARRA LATERAL (Estructura de Suite)
st.sidebar.title("Menú Principal")
modulo = st.sidebar.radio("Ir a:", ["🏠 Inicio", "📦 Inventarios y Ventas", "📄 Cámara de Comercio (IA)"])

if modulo == "🏠 Inicio":
    st.title("Bienvenido a SALAZ ANALYTICS")
    st.write("Seleccione un módulo en el panel izquierdo para comenzar.")

elif modulo == "📦 Inventarios y Ventas":
    st.sidebar.divider()
    opcion = st.sidebar.selectbox("Seleccionar Base de Datos:", list(ARCHIVOS_FIJOS.keys()))
    
    st.sidebar.subheader("📁 Carga de Ventas (CSV o XLSX)")
    archivo_manual = st.sidebar.file_uploader("Subir archivo", type=["xlsx", "csv"])

    df_principal = cargar_excel(ARCHIVOS_FIJOS[opcion])

    if df_principal is not None:
        if archivo_manual:
            # Detectar si es CSV o XLSX
            if archivo_manual.name.endswith('.csv'):
                df_ventas_manual = pd.read_csv(archivo_manual)
            else:
                df_ventas_manual = pd.read_excel(archivo_manual)
            
            st.sidebar.success("✅ Archivo procesado")
            
            # --- BOTÓN DE DESCARGA EN FORMATO XLSX ---
            excel_data = convertir_a_excel(df_ventas_manual)
            st.sidebar.download_button(
                label="📥 Descargar archivo como .xlsx",
                data=excel_data,
                file_name=f"Ventas_Procesadas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Lógica de Cruce (Tu código original)
            if "Referencia" in df_principal.columns and "Referencia" in df_ventas_manual.columns:
                st.subheader("⚖️ Comparativo Inteligente")
                df_comparativo = pd.merge(df_principal[['Referencia', 'Pedido 4 meses', 'Existencias']], 
                                          df_ventas_manual, on="Referencia", how="inner")
                st.dataframe(df_comparativo, use_container_width=True)

        # Visualización de Pedidos
        st.header(f"Tablero: {opcion}")
        st.dataframe(df_principal, use_container_width=True)

elif modulo == "📄 Cámara de Comercio (IA)":
    st.header("📄 Asistente de Cámara de Comercio")
    st.info("Módulo en desarrollo: Aquí integraremos n8n para leer tus PDFs y generar alertas de la DIAN.")
    pdf_subido = st.file_uploader("Suba el PDF de la Cámara de Comercio", type=["pdf"])

# 5. PIE DE PÁGINA
st.markdown("---")
st.caption("SALAZ ANALYTICS | Plataforma Inteligente de Gestión")
