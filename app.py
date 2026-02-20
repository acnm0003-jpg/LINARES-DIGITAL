import streamlit as st
import plotly.graph_objects as go
import numpy as np
from fpdf import FPDF
import base64
from datetime import date
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Linares-Digital", page_icon="🏭", layout="wide")

# Estilos CSS
st.markdown("""
<style>
    .stProgress .st-bo {background-color: #4CAF50;}
    .metric-card {border: 1px solid #e0e0e0; padding: 20px; border-radius: 10px; text-align: center;}
</style>
""", unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN TÉCNICA (IA) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2621/2621051.png", width=50)
    st.header("⚙️ Configuración")
    
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    modelo_seleccionado = None
    
    if not api_key:
        st.error("❌ Falta API Key en Secrets")
    else:
        try:
            genai.configure(api_key=api_key)
            modelos_disponibles = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    modelos_disponibles.append(m.name)
            
            if modelos_disponibles:
                st.success(f"✅ Conectado")
                # Intentamos seleccionar gemini-1.5-flash por defecto si existe (es más rápido y mejor para instrucciones largas)
                default_index = 0
                for i, m in enumerate(modelos_disponibles):
                    if "gemini-1.5" in m:
                        default_index = i
                        break
                modelo_seleccionado = st.selectbox("Modelo IA:", modelos_disponibles, index=default_index)
            else:
                st.warning("⚠️ Clave válida pero no se encuentran modelos.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

    st.divider()
    st.header("Datos Empresa")
    nombre_empresa = st.text_input("Nombre Comercial", "Mi Empresa S.L.")
    sector = st.selectbox("Sector", ["Industria Metalmecánica", "Automoción/Auxiliar", "Comercio Minorista", "Hostelería", "Servicios Profesionales", "Agroalimentario"])
    tamano = st.selectbox("Tamaño", ["Microempresa (1-9 empl.)", "Pequeña (10-49 empl.)", "Mediana (50-250 empl.)"])

# --- 3. CUESTIONARIO (BASE CIENTÍFICA) ---
CUESTIONARIO = {
    "Estrategia y Liderazgo": [
        ("1. Visión Digital", ["1. Inexistente (Día a día)", "2. Ideas sueltas", "3. Metas claras", "4. Plan estratégico", "5. Innovación core"]),
        ("2. Liderazgo", ["1. Pasivo/Delegado", "2. Apoyo puntual", "3. Presupuesto asignado", "4. Liderazgo activo", "5. Cultura de riesgo"]),
        ("3. KPIs", ["1. Sin medición", "2. Esporádica", "3. KPIs básicos", "4. Dashboards", "5. Data-Driven"])
    ],
    "Clientes y Marketing": [
        ("4. Presencia Online", ["1. Nula", "2. Básica (Directorio)", "3. Activa (Web/Redes)", "4. Omnicanal", "5. Experiencia total"]),
        ("5. Venta Online", ["1. No vende", "2. Terceros (Marketplace)", "3. Propia básica", "4. Integrada stock", "5. Analítica avanzada"]),
        ("6. CRM", ["1. Papel/Agenda", "2. Excel/BBDD básica", "3. Software CRM", "4. Integrado ventas", "5. Predicción IA"])
    ],
    "Operaciones y Procesos": [
        ("7. Administración", ["1. Manual/Papel", "2. Software aislado", "3. ERP Integrado", "4. Cloud/Auto", "5. Tiempo real"]),
        ("8. Producción/Ops", ["1. Manual", "2. Herramientas aisladas", "3. Digital parcial", "4. Conectado", "5. IoT/Sensores"])
    ],
    "Tecnología e Infraestructura": [
        ("9. Hardware/Red", ["1. Obsoleto", "2. Funcional", "3. Inversión regular", "4. Cloud seguro", "5. Puntero"]),
        ("10. Ciberseguridad", ["1. Nada/Básico", "2. Copias", "3. Firewall/Claves", "4. Protocolos", "5. Auditorías"])
    ],
    "Personas y Cultura": [
        ("11. Habilidades", ["1. Resistencia", "2. Básicas", "3. Formación puntual", "4. Plan continuo", "5. Talento digital"]),
        ("12. Cultura", ["1. Individual", "2. Email/Whatsapp", "3. Colaborativo", "4. Transversal", "5. Ágil/Abierta"])
    ]
}

PESOS_DIMENSIONES = {
    "Estrategia y Liderazgo": 0.30,
    "Personas y Cultura": 0.25,
    "Operaciones y Procesos": 0.20,
    "Clientes y Marketing": 0.15,
    "Tecnología e Infraestructura": 0.10
}

# --- 4. FUNCIÓN IA SUPER-DETALLADA ---
def generar_analisis_ia(modelo, sector, tamano, debilidad, fortaleza, nmg, detalles):
    try:
        ai_model = genai.GenerativeModel(modelo)
            
        # AQUÍ ESTÁ LA CLAVE: UN PROMPT MUY ESPECÍFICO
        prompt = f"""
        Actúa como un Mentor de Negocios Digitales especializado en PYMEs de Linares (Jaén).
        Tu cliente es una empresa real con este perfil:
        - Sector: {sector}. Tamaño: {tamano}.
        - Nivel de Madurez: {nmg:.2f}/5.0.
        - Su mayor problema es: {debilidad}.
        - Su punto fuerte es: {fortaleza}.
        - Detalle de puntuaciones: {detalles}

        Tu objetivo es darle un MANUAL DE INSTRUCCIONES PRÁCTICO. No uses jerga corporativa abstracta. Dime CÓMO hacerlo paso a paso.

        Genera el informe con estas 3 secciones exactas:

        ### 1. 🔮 LA REALIDAD ECONÓMICA (Causa-Efecto)
        Explica, con un ejemplo cotidiano de su sector, qué dinero o eficiencia están perdiendo hoy por culpa de su debilidad en '{debilidad}'. Sé crudo y realista.

        ### 2. 🛠️ PLAN DE ACCIÓN PASO A PASO (Para solucionar '{debilidad}')
        Desglosa la solución en pasos masticados. No digas "Implementar un CRM". Di: "Paso 1: Abre esta web. Paso 2: Sube esto."
        - **Acción Inmediata (Coste 0€, para hacer mañana):** Explica qué herramienta gratuita usar y cómo configurarla en la primera hora.
        - **Acción a Corto Plazo (1-3 meses):** Qué proceso cambiar y cómo involucrar al equipo.
        - **Acción de Inversión (Solo si es necesaria):** Qué tecnología comprar, cuánto suele costar aprox y qué retorno dará.

        ### 3. 💡 TU VENTAJA OCULTA
        Explica cómo usar su fortaleza en '{fortaleza}' para que la competencia no pueda copiarles. Dame una idea de marketing o proceso concreta.

        Escribe en español directo, usando listas y negritas para facilitar la lectura.
        """
        
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error técnico IA: {e}"

# --- 5. FUNCIÓN PDF ---
def crear_pdf(nombre, sector, nmg, informe_ia, scores):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Diagnostico: {nombre}", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Sector: {sector} | Fecha: {date.today()}", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Puntuaciones:", ln=True)
    pdf.set_font("Arial", '', 10)
    for dim, score in scores.items():
        pdf.cell(0, 6, f"- {dim}: {score:.2f}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 11)
    # Reemplazo de caracteres para evitar errores en PDF básicos
    texto = informe_ia.replace("*", "").replace("#", "").encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, texto)
    return pdf.output(dest='S').encode('latin-1')

# --- 6. INTERFAZ ---
st.title("🏭 Diagnóstico Linares-Digital")
st.markdown("Auditoría de madurez digital y hoja de ruta paso a paso.")

user_scores = {}
tabs = st.tabs(list(CUESTIONARIO.keys()))

for i, (dim_name, preguntas) in enumerate(CUESTIONARIO.items()):
    with tabs[i]:
        st.subheader(f"{dim_name}")
        puntajes = []
        for preg, opciones in preguntas:
            sel = st.radio(f"**{preg}**", options=opciones, key=preg)
            puntajes.append(int(sel[0])) 
        user_scores[dim_name] = np.mean(puntajes)

st.write("---")

if st.button("🚀 OBTENER PLAN DE ACCIÓN DETALLADO", type="primary", use_container_width=True):
    
    # Cálculo
    nmg = 0
    for dim, score in user_scores.items():
        nmg += score * PESOS_DIMENSIONES[dim]
    
    fortaleza = max(user_scores, key=user_scores.get)
    debilidad = min(user_scores, key=user_scores.get)
    
    # IA
    if modelo_seleccionado:
        with st.spinner("🤖 El consultor virtual está redactando tu plan paso a paso..."):
            detalles_texto = ", ".join([f"{k}: {v:.1f}" for k,v in user_scores.items()])
            informe = generar_analisis_ia(modelo_seleccionado, sector, tamano, debilidad, fortaleza, nmg, detalles_texto)
    else:
        informe = "⚠️ Error: No hay conexión con la IA."

    # Resultados
    st.divider()
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Nivel Madurez", f"{nmg:.2f}/5.0")
        st.success(f"Fortaleza: {fortaleza}")
        st.error(f"Prioridad: {debilidad}")
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = nmg,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {'axis': {'range': [0, 5]}, 'bar': {'color': "#2E86C1"},
                     'steps': [{'range': [0, 2], 'color': "#FFCDD2"}, {'range': [2, 3.5], 'color': "#FFF9C4"}, {'range': [3.5, 5], 'color': "#C8E6C9"}]}
        ))
        fig_gauge.update_layout(height=200, margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with c2:
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=list(user_scores.values()), theta=list(user_scores.keys()), fill='toself', name='Tu Empresa'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), title="Radar de Competitividad")
        st.plotly_chart(fig_radar, use_container_width=True)

    st.subheader("📋 Tu Plan de Acción Paso a Paso")
    st.markdown(informe)
    
    try:
        pdf_bytes = crear_pdf(nombre_empresa, sector, nmg, informe, user_scores)
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f'<div style="text-align:center"><a href="data:application/octet-stream;base64,{b64}" download="Plan_Accion_{nombre_empresa}.pdf" style="background-color:#E74C3C; color:white; padding:15px; text-decoration:none; border-radius:5px; font-weight:bold;">📥 DESCARGAR INFORME COMPLETO</a></div>', unsafe_allow_html=True)
    except:
        st.warning("No se pudo generar el PDF.")
