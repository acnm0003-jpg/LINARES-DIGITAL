import streamlit as st
import plotly.graph_objects as go
import numpy as np
from fpdf import FPDF
import base64
from datetime import date
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Linares-Digital", page_icon="🏭", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; }
    .stRadio > label { font-weight: bold; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL Y DIAGNÓSTICO ---
with st.sidebar:
    st.header("Datos de la Empresa")
    nombre_empresa = st.text_input("Nombre Comercial", "Mi Empresa S.L.")
    sector = st.selectbox("Sector", ["Industria Metalmecánica", "Automoción/Auxiliar", "Comercio/Retail", "Servicios", "Agroalimentario"])
    tamano = st.selectbox("Tamaño", ["Micro (<10 empl.)", "Pequeña (10-49)", "Mediana (50-250)"])
    
    st.divider()
    st.markdown("### 🔧 Diagnóstico de API")
    
    # Intento de conexión y listado de modelos
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    if not api_key:
        st.error("Falta la API Key en los Secretos.")
    else:
        try:
            genai.configure(api_key=api_key)
            st.success("API Key detectada.")
            
            # Buscamos modelos disponibles
            st.markdown("**Modelos disponibles para tu clave:**")
            modelos_disponibles = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    nombre_modelo = m.name
                    st.code(nombre_modelo) # Muestra el nombre exacto
                    modelos_disponibles.append(nombre_modelo)
        except Exception as e:
            st.error(f"Error de conexión: {e}")

# --- FUNCIÓN DE IA (GOOGLE GEMINI) ---
def generar_analisis_ia(sector, tamano, debilidad, fortaleza, nivel_global):
    if not api_key:
        return "⚠️ Error: No hay API Key configurada."
    
    try:
        # Intentamos usar el primer modelo disponible de la lista, o gemini-pro por defecto
        # Esto soluciona el error 404 buscando uno que sí exista
        modelo_a_usar = 'models/gemini-1.5-flash' # Opción preferida
        
        # Lógica de fallback (si falla el flash, usa el pro)
        try:
             model = genai.GenerativeModel(modelo_a_usar)
        except:
             model = genai.GenerativeModel('models/gemini-pro')

        prompt = f"""
        Actúa como un Consultor Estratégico de Industria 4.0.
        Analiza esta empresa de Linares (España):
        - Sector: {sector}, Tamaño: {tamano}
        - Nivel Madurez: {nivel_global:.2f}/5
        - Fortaleza: {fortaleza}
        - Debilidad Crítica: {debilidad}

        Genera un informe estratégico breve (máximo 200 palabras) con:
        1. 🔮 PREDICCIÓN DE RIESGO: Qué pasará en 1 año si no mejoran '{debilidad}'.
        2. 🚀 3 ACCIONES INMEDIATAS: Pasos baratos para mejorar mañana.
        3. 💡 VENTAJA: Cómo aprovechar '{fortaleza}'.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ Error en la generación (Intenta recargar la página): {e}"

# --- FUNCIÓN PDF ---
def crear_pdf(nombre_empresa, nmg, fortaleza, debilidad, recomendaciones):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Informe Madurez: {nombre_empresa}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Nivel Global: {nmg:.2f} / 5.0", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 10)
    texto_limpio = recomendaciones.replace("**", "").replace("#", "").replace("🔮", "").replace("🚀", "").replace("💡", "")
    pdf.multi_cell(0, 6, texto_limpio.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ PRINCIPAL ---
st.title("🏭 Diagnóstico Linares-Digital 4.0")

# --- PESOS AHP ---
PESOS = {"Estrategia": 0.30, "Cultura": 0.25, "Operaciones": 0.20, "Clientes": 0.15, "Tecnología": 0.10}

col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Estrategia (30%)")
    p1 = st.select_slider("Nivel de Estrategia", options=["1. Inexistente", "2. Ideas sueltas", "3. Plan Básico", "4. Plan Definido", "5. Liderazgo"], value="1. Inexistente")
    st.subheader("2. Personas (25%)")
    p2 = st.select_slider("Competencias Digitales", options=["1. Nulas", "2. Básicas", "3. Técnicas", "4. Avanzadas", "5. Expertas"], value="1. Nulas")
    st.subheader("3. Operaciones (20%)")
    p3 = st.select_slider("Digitalización Procesos", options=["1. Papel", "2. Excel", "3. Software Básico", "4. ERP Integrado", "5. Automatizado"], value="1. Papel")
with col2:
    st.subheader("4. Clientes (15%)")
    p4 = st.select_slider("Canales Digitales", options=["1. Ninguno", "2. Web estática", "3. Activos", "4. E-commerce", "5. Omnicanal"], value="1. Ninguno")
    st.subheader("5. Tecnología (10%)")
    p5 = st.select_slider("Infraestructura", options=["1. Obsoleta", "2. Básica", "3. Local", "4. Cloud", "5. IoT/IA"], value="1. Obsoleta")

scores = {"Estrategia": int(p1[0]), "Cultura": int(p2[0]), "Operaciones": int(p3[0]), "Clientes": int(p4[0]), "Tecnología": int(p5[0])}

if st.button("🚀 ANALIZAR CON IA", type="primary"):
    nmg = sum(scores[dim] * peso for dim, peso in PESOS.items())
    fortaleza = max(scores, key=scores.get)
    debilidad = min(scores, key=scores.get)
    
    with st.spinner("🤖 Consultando a Google Gemini..."):
        informe_ia = generar_analisis_ia(sector, tamano, debilidad, fortaleza, nmg)
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Nivel Madurez", f"{nmg:.2f}")
    c2.metric("Fortaleza", fortaleza)
    c3.metric("Debilidad", debilidad)
    
    fig = go.Figure(data=go.Scatterpolar(r=list(scores.values()), theta=list(scores.keys()), fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🧠 Análisis Inteligente")
    st.info(informe_ia)
    
    pdf_bytes = crear_pdf(nombre_empresa, nmg, fortaleza, debilidad, informe_ia)
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Informe.pdf">📄 DESCARGAR PDF</a>'
    st.markdown(href, unsafe_allow_html=True)




