import streamlit as st
import plotly.graph_objects as go
import numpy as np
from fpdf import FPDF
import base64
from datetime import date
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Linares-Digital", page_icon="🏭", layout="wide")

# --- 2. FUNCIÓN DE IA (CORREGIDA A GEMINI-PRO) ---
def generar_analisis_ia(sector, tamano, debilidad, fortaleza, nivel_global):
    # Intentamos obtener la clave de los secretos
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    
    if not api_key:
        return "⚠️ ERROR: No se ha detectado la API Key en los 'Secrets' de Streamlit. Por favor, configúrala."
    
    try:
        # Configuración
        genai.configure(api_key=api_key)
        
        # Usamos el modelo estándar 'gemini-pro' que es el más estable
        model = genai.GenerativeModel('gemini-pro')

        # Prompt (Instrucciones)
        prompt = f"""
        Actúa como un Consultor Estratégico de Industria 4.0 para una PYME.
        
        PERFIL DE LA EMPRESA:
        - Ubicación: Linares (España).
        - Sector: {sector}.
        - Tamaño: {tamano}.
        - Nivel de Madurez Digital: {nivel_global:.2f} sobre 5.0.
        
        DIAGNÓSTICO:
        - Punto Fuerte: {fortaleza}.
        - Punto Débil Crítico: {debilidad}.

        Genera un informe estratégico breve (máximo 250 palabras) con estas 3 secciones:

        1. PREDICCIÓN DE ESCENARIOS (Riesgo y Oportunidad):
           Predice qué pasará en 1 año si no mejoran su debilidad en '{debilidad}' y qué beneficio económico o de eficiencia obtendrían si la solucionan.

        2. HOJA DE RUTA (3 Acciones Inmediatas):
           Dame 3 pasos muy concretos, de bajo coste y aplicables mañana mismo para mejorar '{debilidad}'. Menciona herramientas específicas si aplica.

        3. VENTAJA COMPETITIVA:
           Una frase sobre cómo usar su fortaleza en '{fortaleza}' para destacar en el mercado de Linares.
        
        Usa un tono profesional, directo y alentador.
        """
        
        # Generación
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ Error técnico al conectar con Google Gemini: {e}"

# --- 3. FUNCIÓN GENERAR PDF ---
def crear_pdf(nombre_empresa, nmg, fortaleza, debilidad, recomendaciones):
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Informe Madurez: {nombre_empresa}", ln=True, align='C')
    pdf.ln(10)
    
    # Datos
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Fecha: {date.today()}", ln=True)
    pdf.cell(0, 10, f"Nivel Global: {nmg:.2f} / 5.0", ln=True)
    
    # Colores para KPIs
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 10, f"Fortaleza: {fortaleza}", ln=True)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, f"Debilidad: {debilidad}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    # Cuerpo del texto (Limpieza de caracteres especiales)
    pdf.set_font("Arial", '', 10)
    
    # Quitamos emojis y markdown básico para que FPDF no falle
    texto_limpio = recomendaciones.replace("*", "").replace("#", "")
    texto_limpio = texto_limpio.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 6, texto_limpio)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. INTERFAZ: BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8637/8637106.png", width=50)
    st.header("Datos de la Empresa")
    nombre_empresa = st.text_input("Nombre Comercial", "Mi Empresa S.L.")
    sector = st.selectbox("Sector", ["Industria Metalmecánica", "Automoción/Auxiliar", "Comercio/Retail", "Servicios", "Agroalimentario"])
    tamano = st.selectbox("Tamaño", ["Micro (<10 empl.)", "Pequeña (10-49)", "Mediana (50-250)"])
    
    st.divider()
    # Diagnóstico de conexión (Semáforo)
    api_key_check = st.secrets.get("GOOGLE_API_KEY", None)
    if api_key_check:
        st.success("✅ IA Conectada (Google Gemini)")
    else:
        st.error("❌ Falta API Key en Secrets")

# --- 5. INTERFAZ: CUESTIONARIO PRINCIPAL ---
st.title("🏭 Diagnóstico Linares-Digital 4.0")
st.markdown("Herramienta de autodiagnóstico basada en IA y el modelo AHP.")

# Pesos AHP definidos en el TFM
PESOS = {
    "Estrategia y Liderazgo": 0.30,
    "Personas y Cultura": 0.25,
    "Operaciones y Procesos": 0.20,
    "Clientes y Productos": 0.15,
    "Tecnología e Infraestructura": 0.10
}

st.write("---")
c1, c2 = st.columns(2)

with c1:
    st.subheader("1. Estrategia (30%)")
    p1 = st.select_slider("Nivel de Estrategia Digital", options=["1. Inexistente", "2. Ideas sueltas", "3. Plan Básico", "4. Plan Definido", "5. Liderazgo Digital"], value="1. Inexistente")
    
    st.subheader("2. Personas (25%)")
    p2 = st.select_slider("Competencias Digitales", options=["1. Nulas", "2. Básicas (Email)", "3. Técnicas", "4. Avanzadas", "5. Expertas"], value="1. Nulas")
    
    st.subheader("3. Operaciones (20%)")
    p3 = st.select_slider("Digitalización de Procesos", options=["1. Papel", "2. Excel aislado", "3. Software Básico", "4. Integrado (ERP)", "5. Automatizado"], value="1. Papel")

with c2:
    st.subheader("4. Clientes (15%)")
    p4 = st.select_slider("Canales Digitales", options=["1. Ninguno", "2. Web estática", "3. Web/RRSS activas", "4. E-commerce", "5. Omnicanalidad"], value="1. Ninguno")

    st.subheader("5. Tecnología (10%)")
    p5 = st.select_slider("Infraestructura TI", options=["1. Obsoleta", "2. Básica", "3. Moderna Local", "4. Cloud/Nube", "5. IoT/IA"], value="1. Obsoleta")

# Mapeo de respuestas a valores numéricos (primer carácter de la opción)
scores = {
    "Estrategia y Liderazgo": int(p1[0]),
    "Personas y Cultura": int(p2[0]),
    "Operaciones y Procesos": int(p3[0]),
    "Clientes y Productos": int(p4[0]),
    "Tecnología e Infraestructura": int(p5[0])
}

# --- 6. LÓGICA DE PROCESAMIENTO ---
if st.button("🚀 ANALIZAR CON INTELIGENCIA ARTIFICIAL", type="primary"):
    
    # Cálculo AHP (Suma ponderada)
    nmg = sum(scores[dim] * peso for dim, peso in PESOS.items())
    
    # Análisis DAFO automático
    fortaleza = max(scores, key=scores.get)
    debilidad = min(scores, key=scores.get)
    
    # Llamada a la IA
    with st.spinner("🤖 La IA está analizando tu perfil y calculando predicciones..."):
        informe_ia = generar_analisis_ia(sector, tamano, debilidad, fortaleza, nmg)
    
    # --- MOSTRAR RESULTADOS ---
    st.divider()
    
    # Métricas clave
    k1, k2, k3 = st.columns(3)
    k1.metric("Nivel de Madurez", f"{nmg:.2f}/5.0")
    k2.metric("Punto Fuerte", fortaleza)
    k3.metric("Punto Débil", debilidad, delta="-Crítico", delta_color="inverse")
    
    # Gráfico de Radar
    fig = go.Figure(data=go.Scatterpolar(
        r=list(scores.values()),
        theta=list(scores.keys()),
        fill='toself',
        name=nombre_empresa
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Informe de Texto IA
    st.subheader("📋 Informe Estratégico y Predictivo")
    st.info(informe_ia)
    
    # Botón Descarga PDF
    try:
        pdf_bytes = crear_pdf(nombre_empresa, nmg, fortaleza, debilidad, informe_ia)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Informe_{nombre_empresa}.pdf" style="text-decoration:none; color:white; background-color:#FF4B4B; padding:10px; border-radius:5px; font-weight:bold;">📥 DESCARGAR INFORME PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")





