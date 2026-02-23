import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN (Debe ser lo primero)
st.set_page_config(page_title="Salaz Analytics", layout="wide")

# 2. DEFINICIÓN DE FUENTES DE DATOS (Links de GitHub)
ARCHIVOS = {
    "📊 Movimientos 2025": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202025.xlsx",
    "📊 Movimientos 2024": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202024.xlsx",
    "📊 Movimientos 2023": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Movimientos%202023.xlsx",
    "🚀 Análisis Avanzado": "https://github.com/salazdev/cci-inventarios/raw/refs/heads/main/Analisis_Completo.xlsx"
}

@st.cache_data(ttl=300)
def cargar_datos(url):
    try:
        df = pd.read_excel(url)
        df.columns = df.columns.str.strip()
        return df
    except:
        return None

# 3. BARRA LATERAL - MENÚ DE NAVEGACIÓN
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1006/1006158.png", width=100) # Opcional: logo
st.sidebar.title("Menú Principal")
seleccion = st.sidebar.selectbox("Seleccione el Tablero:", list(ARCHIVOS.keys()))

# 4. LÓGICA DE VISUALIZACIÓN
df = cargar_datos(ARCHIVOS[seleccion])

if df is not None:
    st.title(f"{seleccion}")
    
    # --- CASO A: SI ELIGE ANÁLISIS AVANZADO ---
    if "Análisis Avanzado" in seleccion:
        # Ajustamos nombres de columnas específicos de este archivo
        cols_num = ["Venta_Total", "Cantidad_Vendida", "%_Margen", "Dias_Sin_Venta"]
        for c in cols_num:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # KPIs para Avanzado
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Productos", len(df))
        c2.metric("Venta Total", f"${df['Venta_Total'].sum():,.0f}")
        c3.metric("Margen Prom.", f"{df['%_Margen'].mean():.1f}%")
        c4.metric("Días Sin Venta (Máx)", f"{int(df['Dias_Sin_Venta'].max())}")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if "Estado" in df.columns:
                st.subheader("Distribución por Estado")
                st.plotly_chart(px.pie(df, names="Estado", values="Venta_Total", hole=0.4), use_container_width=True)
        with col2:
            if "Elemento" in df.columns:
                st.subheader("Top 10 Días sin Venta")
                top = df.sort_values("Dias_Sin_Venta", ascending=False).head(10)
                st.plotly_chart(px.bar(top, x="Dias_Sin_Venta", y="Elemento", orientation='h', color="Dias_Sin_Venta"), use_container_width=True)

    # --- CASO B: SI ELIGE MOVIMIENTOS 2024 o 2025 ---
    else:
        # Ajustamos nombres de columnas para movimientos
        for c in ["Cantidad", "Venta total", "Costo total local"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
        # KPIs para Movimientos
        c1, c2, c3 = st.columns(3)
        c1.metric("Movimientos", len(df))
        c2.metric("Venta Total", f"${df['Venta total'].sum():,.0f}")
        c3.metric("Cant. Total", f"{int(df['Cantidad'].sum()):,}")

        st.divider()
        # Aquí pondrías los gráficos de líneas que ya tenías antes...
        st.subheader("Histórico de Movimientos")
        st.line_chart(df.groupby(df.columns[0])[df.columns[1]].sum()) # Ejemplo rápido

    # TABLA FINAL (Común para ambos)
    st.subheader("📋 Detalle de Datos")
    st.dataframe(df, use_container_width=True)

else:
    st.error("No se pudo cargar la información. Verifique que el archivo exista en GitHub.")
    # --- 5. FOOTER (PIE DE PÁGINA) ---
st.markdown("---")
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: grey;
        text-align: center;
        padding: 10px;
        font-size: 14px;
    }
    </style>
    <div class="footer">
        <p>© 2026 Salaz Analytics | Soluciones de Inteligencia de Negocios</p>
    </div>
    """,
    unsafe_allow_html=True
)









