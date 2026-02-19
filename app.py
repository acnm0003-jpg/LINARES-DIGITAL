import streamlit as st
import plotly.graph_objects as go
import numpy as np
from fpdf import FPDF
import base64
from datetime import date
import os

# --- 1. CONFIGURACIÓN E IMPORTACIONES SEGURAS ---
st.set_page_config(page_title="Linares-Digital", page_icon="🏭", layout="wide")

# Intentamos importar la librería de IA, si falla, no rompemos la app
try:
    import google.generativeai as genai
    LIB_IA_DISPONIBLE = True
except ImportError:
    LIB_IA_DISPONIBLE = False

# --- 2. FUNCIÓN DE GENERACIÓN (MODO HÍBRIDO: REAL O SIMULADO) ---
def generar_analisis_robusto(sector, tamano, debilidad, fortaleza, nivel_global):
    """
    Intenta usar IA. Si falla, usa plantillas de texto inteligentes.
    """
    mensaje_error = ""
    
    # --- INTENTO 1: IA REAL ---
    if LIB_IA_DISPONIBLE:
        api_key = st.secrets.get("GOOGLE_API_KEY", None)
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Probamos el modelo más básico y seguro
                model = genai.GenerativeModel('gemini-pro') 
                
                prompt = f"""
                Eres un experto en Industria 4.0. Escribe un informe para una PYME de Linares.
                Sector: {sector}. Tamaño: {tamano}. Madurez: {nivel_global}/5.
                Fortaleza: {fortaleza}. Debilidad: {debilidad}.
                
                Escribe 3 apartados breves con iconos:
                1. RIESGOS Y OPORTUNIDADES.
                2. HOJA DE RUTA (3 pasos).
                3. VENTAJA COMPETITIVA.
                """
                response = model.generate_content(prompt)
                if response.text:
                    return response.text # ¡ÉXITO!
            except Exception as e:
                mensaje_error = f"(Fallo de conexión IA: {str(e)})"
        else:
            mensaje_error = "(Falta API Key)"
    else:
        mensaje_error = "(Librería no instalada)"

    # --- INTENTO 2: MODO SIMULACIÓN (SI FALLA LA IA) ---
    # Esto asegura que la app SIEMPRE funcione
    return f"""
    ⚠️ **Nota:** El sistema está operando en **Modo Simulación** {mensaje_error}.
    
    ### 🔮 1. PREDICCIÓN DE ESCENARIOS
    Para una empresa del sector **{sector}** con un nivel de madurez **{nivel_global:.2f}**, la debilidad en **'{debilidad}'** representa un riesgo crítico de pérdida de competitividad del 15% anual. Solucionarlo podría optimizar costes operativos en un 20%.

    ### 🚀 2. HOJA DE RUTA (Acciones Inmediatas)
    Dado tu tamaño ({tamano}), recomendamos:
    1.  **Digitalización Básica:** Implementar herramientas en la nube para gestionar '{debilidad}'.
    2.  **Capacitación:** Formar a un "campeón digital" dentro del equipo actual.
    3.  **Subvenciones:** Solicitar el Kit Digital disponible para PYMEs en Andalucía.

    ### 💡 3. VENTAJA COMPETITIVA
    Vuestra fortaleza en **'{fortaleza}'** es vuestro mayor activo. Usadla para diferenciaros en calidad y servicio frente a competidores locales low-cost.
    """

# --- 3. FUNCIÓN PDF (Simplificada para no fallar) ---
def crear_pdf(nombre_empresa, nmg, fortaleza, debilidad, recomendaciones):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Diagnostico Digital: {nombre_empresa}", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Nivel Global: {nmg:.2f}/5.0", ln=True)
        pdf.ln(5)
        
        # Quitamos caracteres que rompen el PDF
        texto_seguro = recomendaciones.encode('latin-1', 'ignore').decode('latin-1')
        
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 6, texto_seguro)
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        return b"Error PDF"

# --- 4. INTERFAZ ---
with st.sidebar:
    st.header("🏢 Datos de Empresa")
    nombre_empresa = st.text_input("Nombre", "Mi Empresa S.L.")
    sector = st.selectbox("Sector", ["Industria", "Comercio", "Servicios", "Agro", "Otro"])
    tamano = st.selectbox("Tamaño", ["Micro", "Pequeña", "Mediana"])
    
    # Verificador de estado (Debug)
    if "GOOGLE_API_KEY" in st.secrets:
        st.caption("✅ API Key detectada")
    else:
        st.caption("⚠️ API Key no detectada (Usando simulación)")

st.title("Diagnóstico Linares-Digital")

# Pesos
PESOS = {"Estrategia": 0.30, "Cultura": 0.25, "Operaciones": 0.20, "Clientes": 0.15, "Tecnología": 0.10}

c1, c2 = st.columns(2)
with c1:
    p1 = st.slider("Estrategia (30%)", 1, 5, 1)
    p2 = st.slider("Cultura (25%)", 1, 5, 1)
    p3 = st.slider("Operaciones (20%)", 1, 5, 1)
with c2:
    p4 = st.slider("Clientes (15%)", 1, 5, 1)
    p5 = st.slider("Tecnología (10%)", 1, 5, 1)

scores = {"Estrategia": p1, "Cultura": p2, "Operaciones": p3, "Clientes": p4, "Tecnología": p5}

if st.button("🚀 OBTENER RESULTADOS", type="primary"):
    nmg = sum(scores[d] * p for d, p in PESOS.items())
    fortaleza = max(scores, key=scores.get)
    debilidad = min(scores, key=scores.get)
    
    # Llamamos a la función robusta
    informe = generar_analisis_robusto(sector, tamano, debilidad, fortaleza, nmg)
    
    st.divider()
    k1, k2 = st.columns(2)
    k1.metric("Madurez", f"{nmg:.2f}/5")
    k2.metric("Punto Débil", debilidad)
    
    # Gráfico
    fig = go.Figure(data=go.Scatterpolar(r=list(scores.values()), theta=list(scores.keys()), fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Informe de Resultados")
    st.info(informe)
    
    # PDF
    try:
        pdf_data = crear_pdf(nombre_empresa, nmg, fortaleza, debilidad, informe)
        b64 = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="reporte.pdf">📥 Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    except:
        st.warning("No se pudo generar el PDF en este momento.")






