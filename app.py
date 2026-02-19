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

# --- FUNCIÓN DE IA (GOOGLE GEMINI - GRATIS) ---
def generar_analisis_ia(sector, tamano, debilidad, fortaleza, nivel_global):
    # 1. Obtener API Key de los secretos
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    
    if not api_key:
        return """
        ⚠️ **AVISO:** No se ha configurado la API Key de Google.
        
        **Modo Simulación (Sin IA):**
        - El sistema detecta que tu debilidad es **""" + debilidad + """**.
        - Se recomienda revisar los procesos manuales.
        *(Configura el secreto GOOGLE_API_KEY para análisis real)*
        """
    
    try:
        # 2. Configurar Google Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro') # Modelo rápido y gratis
        
        # 3. El Prompt (Instrucciones)
        prompt = f"""
        Actúa como un Consultor Estratégico de Industria 4.0 especializado en reindustrialización.
        
        Analiza esta empresa real de Linares (España):
        - Sector: {sector}
        - Tamaño: {tamano}
        - Nivel Madurez: {nivel_global:.2f}/5
        - Su Punto Fuerte es: {fortaleza}
        - Su Punto Débil Crítico es: {debilidad}

        Genera un informe estratégico breve con estas 3 secciones (usa estos iconos):

        1. 🔮 PREDICCIÓN DE ESCENARIOS (Riesgo y Oportunidad):
           - Predice un riesgo concreto a 1 año si no mejoran en '{debilidad}'.
           - Estima el impacto positivo (ej. % ahorro o eficiencia) si mejoran esa área.

        2. 🚀 HOJA DE RUTA (Acciones Inmediatas):
           - Dame 3 pasos muy concretos, baratos y aplicables mañana mismo para mejorar '{debilidad}'.
           - No digas generalidades, da nombres de herramientas o metodologías concretas.

        3. 💡 VENTAJA COMPETITIVA:
           - Una frase inspiradora sobre cómo usar su fortaleza en '{fortaleza}' para destacar en la región.
        
        Responde en español profesional. Sé directo.
        """
        
        # 4. Generar respuesta
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ Error conectando con Google Gemini: {e}"

# --- FUNCIÓN GENERAR PDF ---
def crear_pdf(nombre_empresa, nmg, fortaleza, debilidad, recomendaciones):
    pdf = FPDF()
    pdf.add_page()
    
    # Intentamos usar una fuente estándar para evitar errores de caracteres
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Informe Madurez: {nombre_empresa}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Fecha: {date.today()}", ln=True)
    pdf.cell(0, 10, f"Nivel Global: {nmg:.2f} / 5.0", ln=True)
    
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 10, f"Fortaleza: {fortaleza}", ln=True)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, f"Debilidad: {debilidad}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 10)
    # Limpieza básica de texto para PDF (quitamos negritas markdown)
    texto_limpio = recomendaciones.replace("**", "").replace("#", "")
    # Codificación para evitar errores con tildes (latin-1 suele ir bien)
    pdf.multi_cell(0, 6, texto_limpio.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ PRINCIPAL ---
st.title("🏭 Diagnóstico Linares-Digital 4.0 (IA Powered)")
st.markdown("Sistema inteligente de autodiagnóstico para la reindustrialización de PYMEs.")

# Sidebar
with st.sidebar:
    st.header("Datos de la Empresa")
    nombre_empresa = st.text_input("Nombre Comercial", "Mi Empresa S.L.")
    sector = st.selectbox("Sector", ["Industria Metalmecánica", "Automoción/Auxiliar", "Comercio/Retail", "Servicios", "Agroalimentario"])
    tamano = st.selectbox("Tamaño", ["Micro (<10 empl.)", "Pequeña (10-49)", "Mediana (50-250)"])
    st.info("ℹ️ Este sistema utiliza Inteligencia Artificial de Google (Gemini) para generar las predicciones.")

# --- PESOS AHP ---
PESOS = {
    "Estrategia y Liderazgo": 0.30,
    "Personas y Cultura": 0.25,
    "Operaciones y Procesos": 0.20,
    "Clientes y Productos": 0.15,
    "Tecnología e Infraestructura": 0.10
}

# --- CUESTIONARIO ---
st.write("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Estrategia (30%)")
    p1 = st.select_slider("Nivel de Estrategia Digital", options=["1. Inexistente", "2. Ideas sueltas", "3. Plan Básico", "4. Plan Definido", "5. Liderazgo Digital"], value="1. Inexistente")
    
    st.subheader("2. Personas (25%)")
    p2 = st.select_slider("Competencias Digitales", options=["1. Nulas", "2. Básicas (Email)", "3. Técnicas", "4. Avanzadas", "5. Expertas"], value="1. Nulas")
    
    st.subheader("3. Operaciones (20%)")
    p3 = st.select_slider("Digitalización de Procesos", options=["1. Papel", "2. Excel aislado", "3. Software Básico", "4. Integrado (ERP)", "5. Automatizado"], value="1. Papel")

with col2:
    st.subheader("4. Clientes (15%)")
    p4 = st.select_slider("Canales Digitales", options=["1. Ninguno", "2. Web estática", "3. Web/RRSS activas", "4. E-commerce", "5. Omnicanalidad"], value="1. Ninguno")

    st.subheader("5. Tecnología (10%)")
    p5 = st.select_slider("Infraestructura TI", options=["1. Obsoleta", "2. Básica", "3. Moderna Local", "4. Cloud/Nube", "5. IoT/IA"], value="1. Obsoleta")

# Mapeo simple de la opción elegida al número (el primer carácter)
scores = {
    "Estrategia y Liderazgo": int(p1[0]),
    "Personas y Cultura": int(p2[0]),
    "Operaciones y Procesos": int(p3[0]),
    "Clientes y Productos": int(p4[0]),
    "Tecnología e Infraestructura": int(p5[0])
}

# --- BOTÓN DE ACCIÓN ---
if st.button("🚀 ANALIZAR CON INTELIGENCIA ARTIFICIAL", type="primary"):
    
    # Cálculo AHP
    nmg = sum(scores[dim] * peso for dim, peso in PESOS.items())
    
    # Lógica DAFO
    fortaleza = max(scores, key=scores.get)
    debilidad = min(scores, key=scores.get)
    
    # Generar Informe IA
    with st.spinner("🤖 La IA está analizando tus respuestas y calculando predicciones..."):
        informe_ia = generar_analisis_ia(sector, tamano, debilidad, fortaleza, nmg)
    
    # Mostrar KPIs
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Nivel de Madurez", f"{nmg:.2f}/5.0")
    c2.metric("Punto Fuerte", fortaleza)
    c3.metric("Punto Débil", debilidad, delta="-Crítico", delta_color="inverse")
    
    # Gráfico Radar
    fig = go.Figure(data=go.Scatterpolar(
        r=list(scores.values()),
        theta=list(scores.keys()),
        fill='toself',
        name=nombre_empresa
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar Informe IA
    st.subheader("📋 Informe Estratégico y Predictivo")
    st.markdown(informe_ia)
    
    # Botón PDF
    pdf_bytes = crear_pdf(nombre_empresa, nmg, fortaleza, debilidad, informe_ia)
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Informe_Digital_{nombre_empresa}.pdf" style="text-decoration:none; color:white; background-color:red; padding:10px; border-radius:5px;">📄 DESCARGAR PDF</a>'
    st.markdown(href, unsafe_allow_html=True)



