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
    h3 {color: #2c3e50;}
</style>
""", unsafe_allow_html=True)

# --- 2. DEFINICIÓN DEL CUESTIONARIO COMPLETO (12 Preguntas) ---
CUESTIONARIO = {
    "Estrategia y Liderazgo": [
        ("1. Visión Digital", [
            "1. No hay estrategia, operamos al día.",
            "2. Conversaciones ocasionales, sin plan.",
            "3. Metas claras pero no integradas.",
            "4. Estrategia fundamental en el plan anual.",
            "5. Innovación como motor principal."
        ]),
        ("2. Liderazgo de la Dirección", [
            "1. Delega o no lo ve prioritario.",
            "2. Apoya proyectos puntuales.",
            "3. Asigna presupuesto específico.",
            "4. Lidera activamente la estrategia.",
            "5. Fomenta cultura de riesgo y experimentación."
        ]),
        ("3. Medición y KPIs", [
            "1. No medimos retorno.",
            "2. Métricas básicas esporádicas.",
            "3. Seguimiento de KPIs específicos.",
            "4. Cuadro de mando (Dashboard) regular.",
            "5. Decisiones basadas en datos (Data-Driven)."
        ])
    ],
    "Clientes y Marketing": [
        ("4. Presencia Online", [
            "1. Sin web ni redes sociales.",
            "2. Web básica / Perfiles inactivos.",
            "3. Web funcional / Redes regulares.",
            "4. Web móvil / Interacción activa.",
            "5. Experiencia omnicanal integrada."
        ]),
        ("5. Venta Online (E-commerce)", [
            "1. No vendemos online.",
            "2. Plataformas de terceros ocasional.",
            "3. Tienda propia básica (pocas ventas).",
            "4. Tienda importante integrada con stock.",
            "5. Canal principal con analítica avanzada."
        ]),
        ("6. Gestión de Clientes (CRM)", [
            "1. Papel o Excel disperso.",
            "2. Base de datos centralizada básica.",
            "3. Software CRM para comunicación.",
            "4. CRM integrado con ventas/marketing.",
            "5. Predicción de necesidades (IA)."
        ])
    ],
    "Operaciones y Procesos": [
        ("7. Gestión Administrativa", [
            "1. Papel y hojas de cálculo.",
            "2. Software aislado (ej. solo facturas).",
            "3. ERP integrado (Facturación/Stock).",
            "4. ERP en nube con automatización.",
            "5. Analítica para decisiones en tiempo real."
        ]),
        ("8. Procesos Operativos", [
            "1. Completamente manuales.",
            "2. Herramientas digitales aisladas.",
            "3. Digitalización parcial del proceso.",
            "4. Digitalizados y conectados (Trazabilidad).",
            "5. Sensores IoT y optimización real."
        ])
    ],
    "Tecnología e Infraestructura": [
        ("9. Infraestructura TI", [
            "1. Equipos antiguos, sin red.",
            "2. Equipos funcionales, software básico.",
            "3. Inversión y software nube básico.",
            "4. Infraestructura Cloud segura.",
            "5. Tecnología proactiva competitiva."
        ]),
        ("10. Ciberseguridad", [
            "1. Sin política (solo antivirus).",
            "2. Copias de seguridad periódicas.",
            "3. Contraseñas y firewall.",
            "4. Formación y protocolos de incidentes.",
            "5. Auditorías y protección avanzada."
        ])
    ],
    "Personas y Cultura": [
        ("11. Habilidades Digitales", [
            "1. Muy básicas, resistencia.",
            "2. Manejo básico, dificultad adaptación.",
            "3. Formación puntual por herramientas.",
            "4. Plan de formación continua.",
            "5. Talento digital y autoaprendizaje."
        ]),
        ("12. Cultura de Innovación", [
            "1. Trabajo individual, sin comunicación.",
            "2. Email/WhatsApp básico.",
            "3. Plataformas colaborativas (Teams).",
            "4. Trabajo transversal activo.",
            "5. Experimentación y aprendizaje del error."
        ])
    ]
}

# Pesos AHP calculados en el TFM
PESOS_DIMENSIONES = {
    "Estrategia y Liderazgo": 0.30,
    "Personas y Cultura": 0.25,
    "Operaciones y Procesos": 0.20,
    "Clientes y Marketing": 0.15,
    "Tecnología e Infraestructura": 0.10
}

# --- 3. FUNCIÓN IA PREDICTIVA (GEMINI PRO) ---
def generar_analisis_ia(sector, tamano, debilidad, fortaleza, nmg, detalles):
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    
    if not api_key:
        return "⚠️ MODO SIMULACIÓN. Configura la API Key para predicciones reales."
    
    try:
        genai.configure(api_key=api_key)
        try:
             model = genai.GenerativeModel('models/gemini-pro')
        except:
             model = genai.GenerativeModel('gemini-pro')
            
        prompt = f"""
        Actúa como un Consultor Estratégico de Industria 4.0.
        Analiza esta empresa de Linares (España):
        - Sector: {sector} | Tamaño: {tamano}
        - Madurez Global: {nmg:.2f}/5.0
        - Dimensión más Fuerte: {fortaleza}
        - Dimensión más Débil: {debilidad}
        
        Detalles del diagnóstico: {detalles}

        Genera un informe estratégico (máximo 300 palabras) con estas 3 secciones obligatorias:

        1. 🔮 PREDICCIÓN DE IMPACTO (Riesgo vs Oportunidad):
           - Qué pasará en 12 meses si NO mejoran en '{debilidad}' (riesgo operativo/financiero).
           - Qué beneficio tangible (estimado) obtendrán si suben 1 punto en esa dimensión.

        2. 🚀 HOJA DE RUTA TÁCTICA (3 Pasos):
           - Paso 1 (Inmediato/Gratis): Acción concreta para empezar mañana.
           - Paso 2 (Inversión Baja): Herramienta o cambio recomendado a 3 meses.
           - Paso 3 (Transformación): Objetivo a 1 año.

        3. 💡 VENTAJA COMPETITIVA:
           - Cómo apalancar su fortaleza en '{fortaleza}' para ganar mercado local.

        Usa un tono profesional pero directo. No uses frases genéricas.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error técnico IA: {e}"

# --- 4. FUNCIÓN PDF ---
def crear_pdf(nombre, sector, nmg, informe_ia, scores):
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Informe Digital: {nombre}", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Sector: {sector} | Fecha: {date.today()}", ln=True, align='C')
    pdf.ln(5)
    
    # Tabla Resultados
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Resultados del Diagnóstico:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Nivel Global: {nmg:.2f} / 5.0", ln=True)
    for dim, score in scores.items():
        pdf.cell(0, 6, f"- {dim}: {score:.2f}", ln=True)
    pdf.ln(5)
    
    # Informe IA
    pdf.set_font("Arial", '', 11)
    # Limpieza de caracteres para PDF
    texto = informe_ia.replace("*", "").replace("#", "").encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, texto)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. INTERFAZ DE USUARIO ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2621/2621051.png", width=50)
    st.header("Datos de la Empresa")
    nombre_empresa = st.text_input("Nombre Comercial", "Mi Empresa S.L.")
    sector = st.selectbox("Sector", ["Industria Metalmecánica", "Automoción", "Comercio", "Hostelería", "Servicios"])
    tamano = st.selectbox("Tamaño", ["Micro (1-9)", "Pequeña (10-49)", "Mediana (50-250)"])
    
    if "GOOGLE_API_KEY" in st.secrets:
        st.success("✅ IA Conectada")
    else:
        st.warning("⚠️ Modo Offline")

st.title("🏭 Diagnóstico Linares-Digital")
st.markdown("Responda a las 12 preguntas clave para obtener su hoja de ruta personalizada.")

# --- RENDERIZADO DEL CUESTIONARIO ---
user_scores = {}
tabs = st.tabs(list(CUESTIONARIO.keys()))

for i, (dim_name, preguntas) in enumerate(CUESTIONARIO.items()):
    with tabs[i]:
        st.header(f"{dim_name}")
        puntajes = []
        for preg, opciones in preguntas:
            # Usamos un radio button horizontal para que sea más limpio
            sel = st.radio(f"**{preg}**", options=opciones, key=preg)
            puntajes.append(int(sel[0])) # Extraemos el número (1..5)
        user_scores[dim_name] = np.mean(puntajes)

# --- BOTÓN DE CÁLCULO ---
st.write("---")
if st.button("🚀 GENERAR INFORME PREDICTIVO", type="primary", use_container_width=True):
    
    # 1. Cálculo Global Ponderado
    nmg = 0
    for dim, score in user_scores.items():
        nmg += score * PESOS_DIMENSIONES[dim]
        
    # 2. Análisis DAFO
    fortaleza = max(user_scores, key=user_scores.get)
    debilidad = min(user_scores, key=user_scores.get)
    
    # 3. Consulta a IA
    with st.spinner("🧠 Analizando datos y calculando predicciones..."):
        # Preparamos un resumen de puntuaciones para que la IA tenga contexto
        detalles_texto = ", ".join([f"{k}: {v:.1f}" for k,v in user_scores.items()])
        informe = generar_analisis_ia(sector, tamano, debilidad, fortaleza, nmg, detalles_texto)
    
    # --- VISUALIZACIÓN ---
    st.divider()
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.metric("Madurez Digital", f"{nmg:.2f} / 5.0")
        st.caption(f"Fortaleza: {fortaleza}")
        st.caption(f"Debilidad: {debilidad}")
        
        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = nmg,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {'axis': {'range': [0, 5]}, 'bar': {'color': "#3498DB"}}
        ))
        fig_gauge.update_layout(height=200, margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with c2:
        # Radar Chart
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=list(user_scores.values()),
            theta=list(user_scores.keys()),
            fill='toself', name='Tu Empresa'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
        st.plotly_chart(fig_radar, use_container_width=True)

    # Informe IA
    st.subheader("🤖 Análisis Estratégico (IA)")
    st.markdown(informe)
    
    # Descarga PDF
    try:
        pdf_bytes = crear_pdf(nombre_empresa, sector, nmg, informe, user_scores)
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f"""
        <div style="text-align:center">
            <a href="data:application/octet-stream;base64,{b64}" download="Plan_Director_{nombre_empresa}.pdf" 
            style="background-color:#E74C3C; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;">
            📄 DESCARGAR INFORME EN PDF
            </a>
        </div>
        """, unsafe_allow_html=True)
    except:
        st.error("Error generando PDF.")
