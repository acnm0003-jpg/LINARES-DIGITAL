import streamlit as st
import plotly.graph_objects as go
import numpy as np
from fpdf import FPDF
import base64
from datetime import date
import google.generativeai as genai

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Linares-Digital", page_icon="🏭", layout="wide")

# --- 2. GESTIÓN DE LA CONEXIÓN IA (AUTO-DETECCIÓN) ---
def configurar_ia():
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    if not api_key:
        return None, []
    
    try:
        genai.configure(api_key=api_key)
        # Pedimos a Google qué modelos tiene disponibles para esta clave
        modelos = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos.append(m.name)
        return api_key, modelos
    except Exception as e:
        st.error(f"Error conectando con Google: {e}")
        return None, []

# --- 3. BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.header("⚙️ Configuración Técnica")
    
    # Verificación de API y Selección de Modelo
    api_key, lista_modelos = configurar_ia()
    
    if api_key and lista_modelos:
        st.success(f"✅ Conectado. {len(lista_modelos)} modelos disponibles.")
        # Aquí está la magia: Eliges el modelo de la lista real de Google
        modelo_seleccionado = st.selectbox("Modelo de IA a usar:", lista_modelos, index=0)
    elif api_key and not lista_modelos:
        st.warning("⚠️ Clave correcta pero no se encuentran modelos. Revisa permisos.")
        modelo_seleccionado = None
    else:
        st.error("❌ Falta la API Key en los Secrets.")
        modelo_seleccionado = None

    st.divider()
    st.header("Datos Empresa")
    sector = st.selectbox("Sector", ["Industria Metalmecánica", "Automoción", "Comercio", "Servicios"])
    tamano = st.selectbox("Tamaño", ["Microempresa", "Pequeña", "Mediana"])

# --- 4. FUNCIÓN DE GENERACIÓN DE TEXTO ---
def generar_informe(modelo_nombre, sector, tamano, debilidad, fortaleza, nmg):
    try:
        model = genai.GenerativeModel(modelo_nombre)
        
        prompt = f"""
        Actúa como consultor experto. Analiza esta PYME de Linares (España):
        - Sector: {sector}, Tamaño: {tamano}.
        - Madurez Digital: {nmg:.2f}/5.
        - Punto Fuerte: {fortaleza}.
        - Punto Débil: {debilidad}.
        
        Escribe un informe MUY BREVE (200 palabras) con:
        1. 🔮 RIESGO: Qué pasa si no mejoran '{debilidad}'.
        2. 🚀 ACCIONES: 2 pasos prácticos para mejorar.
        3. 💡 CONSEJO: Cómo usar '{fortaleza}'.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generando texto: {e}"

# --- 5. LÓGICA DE LA APP (AHP + RESULTADOS) ---
st.title("🏭 Diagnóstico Inteligente Linares-Digital")

# Cuestionario Simplificado para Test
c1, c2 = st.columns(2)
with c1:
    e1 = st.slider("Estrategia (30%)", 1, 5, 2)
    e2 = st.slider("Cultura (25%)", 1, 5, 3)
    e3 = st.slider("Procesos (20%)", 1, 5, 2)
with c2:
    e4 = st.slider("Clientes (15%)", 1, 5, 1)
    e5 = st.slider("Tecnología (10%)", 1, 5, 2)

PESOS = [0.30, 0.25, 0.20, 0.15, 0.10]
VALORES = [e1, e2, e3, e4, e5]
LABELS = ["Estrategia", "Cultura", "Procesos", "Clientes", "Tecnología"]

if st.button("🚀 EJECUTAR DIAGNÓSTICO", type="primary"):
    
    # Cálculos
    nmg = sum(v * p for v, p in zip(VALORES, PESOS))
    # Identificar debilidad/fortaleza
    diccionario = dict(zip(LABELS, VALORES))
    fortaleza = max(diccionario, key=diccionario.get)
    debilidad = min(diccionario, key=diccionario.get)
    
    # Resultados Gráficos
    st.metric("Nivel de Madurez", f"{nmg:.2f} / 5.0")
    
    # INTELIGENCIA ARTIFICIAL
    st.subheader("🤖 Análisis de Inteligencia Artificial")
    
    if modelo_seleccionado:
        with st.spinner(f"Consultando a {modelo_seleccionado}..."):
            texto_ia = generar_informe(modelo_seleccionado, sector, tamano, debilidad, fortaleza, nmg)
            st.info(texto_ia)
            
            # Botón PDF (Solo si hay texto IA)
            if "Error" not in texto_ia:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                # Codificación segura para PDF
                txt_pdf = f"INFORME LINARES DIGITAL\n\nEmpresa: {sector}\nMadurez: {nmg:.2f}\n\n{texto_ia}"
                txt_pdf = txt_pdf.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 8, txt_pdf)
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                b64 = base64.b64encode(pdf_bytes).decode()
                st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="informe.pdf">📥 Descargar PDF</a>', unsafe_allow_html=True)
    else:
        st.error("⚠️ No se puede generar el informe IA porque no hay conexión con Google.")
