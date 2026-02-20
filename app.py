import streamlit as st
import plotly.graph_objects as go
import numpy as np
from fpdf import FPDF
import base64
from datetime import date
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Linares-Digital", page_icon="🏭", layout="wide")

# Estilos CSS para mejorar la apariencia
st.markdown("""
<style>
    .stProgress .st-bo {background-color: #4CAF50;}
    .metric-card {border: 1px solid #e0e0e0; padding: 20px; border-radius: 10px; text-align: center;}
    h3 {color: #2c3e50;}
</style>
""", unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DEL CUESTIONARIO (BASE CIENTÍFICA) ---
# Preguntas diseñadas según HADA y SIRI para PYMEs
CUESTIONARIO = {
    "Estrategia y Liderazgo": [
        ("Hoja de Ruta Digital", [
            "1. No existe, actuamos por urgencias.",
            "2. Intenciones verbales, nada escrito.",
            "3. Plan básico anual sin presupuesto fijo.",
            "4. Plan estratégico con presupuesto asignado.",
            "5. Estrategia digital central y revisada trimestralmente."
        ]),
        ("Liderazgo e Inversión", [
            "1. La dirección ve la tecnología como un gasto.",
            "2. Apoyo pasivo, delegan en externos.",
            "3. Interés activo, inversiones puntuales.",
            "4. Liderazgo proactivo e inversión recurrente.",
            "5. Cultura 'Digital First' impulsada por dirección."
        ]),
        ("Análisis del Entorno", [
            "1. No miramos qué hace la competencia.",
            "2. Revisión ocasional de competidores locales.",
            "3. Monitorización básica del mercado.",
            "4. Uso de datos para analizar tendencias.",
            "5. Predicción de tendencias con herramientas digitales."
        ])
    ],
    "Personas y Cultura": [
        ("Competencias Digitales", [
            "1. Nulas o muy básicas (solo email/whatsapp).",
            "2. Ofimática básica (Word, Excel simple).",
            "3. Uso competente de software de gestión.",
            "4. Habilidades avanzadas en el equipo clave.",
            "5. Perfiles especializados (Analistas, Programadores)."
        ]),
        ("Formación y Cambio", [
            "1. Resistencia activa al cambio.",
            "2. Formación solo si es obligatoria.",
            "3. Formación puntual técnica.",
            "4. Plan de formación anual.",
            "5. Cultura de innovación y autoaprendizaje."
        ]),
         ("Colaboración Digital", [
            "1. Papel y reuniones presenciales.",
            "2. Email y teléfono.",
            "3. Nube básica (Drive/Dropbox) para archivos.",
            "4. Herramientas colaborativas (Teams/Slack/Trello).",
            "5. Flujos de trabajo digitales automatizados."
        ])
    ],
    "Operaciones y Procesos": [
        ("Integración de Sistemas", [
            "1. Todo manual o papel.",
            "2. Excel dispersos y software aislado.",
            "3. Software de gestión básico (Facturación).",
            "4. ERP integrado (Contabilidad-Stocks-Ventas).",
            "5. ERP avanzado conectado con planta/web."
        ]),
        ("Automatización", [
            "1. Tareas 100% manuales.",
            "2. Alguna macro de Excel.",
            "3. Automatización de tareas administrativas simples.",
            "4. Procesos clave automatizados.",
            "5. Automatización inteligente (RPA/IA)."
        ]),
        ("Toma de Decisiones", [
            "1. Basada en intuición/experiencia.",
            "2. Basada en informes a mes vencido.",
            "3. Basada en datos semanales.",
            "4. Cuadros de mando (Dashboards) actualizados.",
            "5. Predicción basada en datos en tiempo real."
        ])
    ],
    "Clientes y Productos": [
        ("Canales Digitales", [
            "1. Sin presencia digital.",
            "2. Web estática / Directorios.",
            "3. Web activa y Redes Sociales.",
            "4. Estrategia Omnicanal (Venta online/Leads).",
            "5. E-commerce integrado y automatizado."
        ]),
        ("Experiencia de Cliente", [
            "1. Trato puramente transaccional físico.",
            "2. Atención por email reactiva.",
            "3. CRM básico (Base de datos clientes).",
            "4. CRM activo con segmentación.",
            "5. Personalización masiva y predicción de demanda."
        ])
    ],
    "Tecnología e Infraestructura": [
        ("Infraestructura TI", [
            "1. Ordenadores domésticos obsoletos.",
            "2. Red básica local.",
            "3. Servidor propio o híbrido.",
            "4. Infraestructura Cloud (Nube) profesional.",
            "5. Arquitectura escalable y redundante."
        ]),
        ("Ciberseguridad", [
            "1. Sin protección (solo antivirus gratuito).",
            "2. Copias de seguridad manuales.",
            "3. Copias en nube y firewall.",
            "4. Plan de seguridad y recuperación.",
            "5. Monitorización de amenazas en tiempo real."
        ]),
        ("Tecnologías Habilitadoras", [
            "1. Ninguna.",
            "2. Pruebas piloto.",
            "3. Uso de IoT (Sensores) o Big Data básico.",
            "4. Integración de IoT/Robótica.",
            "5. Uso de IA y Gemelos Digitales."
        ])
    ]
}

PESOS_DIMENSIONES = [0.30, 0.25, 0.20, 0.15, 0.10] # Orden: Estrategia, Personas, Operaciones, Clientes, Tecnología

# --- 3. LÓGICA DE IA (PREDICTIVA) ---
def generar_analisis_ia(sector, tamano, debilidad, fortaleza, nmg, scores_dict):
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    
    if not api_key:
        return "⚠️ MODO SIMULACIÓN (Sin conexión a IA). Configura la API Key para ver predicciones reales."
    
    try:
        genai.configure(api_key=api_key)
        # Usamos un modelo más rápido si está disponible, o el estándar
        try:
            model = genai.GenerativeModel('models/gemini-1.5-flash')
        except:
            model = genai.GenerativeModel('models/gemini-pro')
            
        prompt = f"""
        Eres un Consultor de Estrategia Digital de alto nivel.
        Analiza esta PYME de Linares (España):
        - Sector: {sector} | Tamaño: {tamano}
        - Madurez Global: {nmg:.2f}/5.0
        - Perfil detallado: {scores_dict}
        
        Tu objetivo es convencer al gerente con argumentos económicos.
        
        Genera un informe con estas 4 secciones (Usa Markdown y emojis):

        1. 📉 PREDICCIÓN DE RIESGOS (Consecuencias de NO actuar):
           - Describe un escenario realista a 12 meses si no mejoran su debilidad en '{debilidad}'.
           - Estima (con rangos porcentuales) la pérdida potencial de eficiencia o clientes.

        2. 💰 ANÁLISIS DE OPORTUNIDAD (ROI):
           - ¿Merece la pena invertir en '{debilidad}' dado su tamaño y sector? 
           - Si la respuesta es SÍ, predice el beneficio económico o competitivo a corto plazo (6 meses) y largo plazo (2 años).

        3. 🚀 HOJA DE RUTA TÁCTICA (3 Pasos):
           - Paso 1 (Coste Cero): Algo que pueden hacer mañana.
           - Paso 2 (Inversión Baja): Herramienta o cambio de proceso recomendado.
           - Paso 3 (Consolidación): El objetivo a 1 año.

        4. 🏆 VENTAJA COMPETITIVA (Apalancamiento):
           - Cómo usar su fortaleza en '{fortaleza}' para ganar cuota de mercado en Linares.

        Sé duro con los riesgos pero motivador con las soluciones. No uses lenguaje genérico.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error en IA: {e}"

# --- 4. FUNCIÓN PDF ---
def crear_pdf(nombre, sector, nmg, informe_ia, scores):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Diagnostico Digital: {nombre}", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Sector: {sector} | Fecha: {date.today()}", ln=True, align='C')
    pdf.ln(5)
    
    # Tabla de Puntuaciones
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Desglose por Dimensiones:", ln=True)
    pdf.set_font("Arial", '', 10)
    for dim, score in scores.items():
        pdf.cell(0, 7, f"- {dim}: {score:.2f}/5.0", ln=True)
    pdf.ln(5)
    
    # Informe IA (Limpieza)
    pdf.set_font("Arial", '', 11)
    texto = informe_ia.replace("*", "").replace("#", "").encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, texto)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. INTERFAZ DE USUARIO ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2621/2621051.png", width=50)
    st.title("Configuración")
    nombre_empresa = st.text_input("Nombre Empresa", "Mi PYME S.L.")
    sector = st.selectbox("Sector", ["Industria Metalmecánica", "Automoción", "Comercio", "Hostelería", "Servicios Profesionales"])
    tamano = st.selectbox("Tamaño", ["Microempresa (1-9)", "Pequeña (10-49)", "Mediana (50-250)"])
    
    # Diagnóstico API
    if "GOOGLE_API_KEY" in st.secrets:
        st.success("✅ IA Activada")
    else:
        st.warning("⚠️ Modo Offline")

st.title("🏭 Linares-Digital: Modelo de Madurez Predictivo")
st.markdown("""
**Instrucciones:** Responda con honestidad para obtener una predicción financiera y operativa realista.
""")

# --- RENDERIZADO DEL CUESTIONARIO (TABS) ---
tabs = st.tabs(list(CUESTIONARIO.keys()))
user_scores = {}

for i, (dim_name, preguntas) in enumerate(CUESTIONARIO.items()):
    with tabs[i]:
        st.header(f"{dim_name}")
        puntajes_dim = []
        for pregunta, opciones in preguntas:
            resp = st.radio(f"**{pregunta}**", options=opciones, key=f"{dim_name}_{pregunta}")
            puntajes_dim.append(int(resp[0])) # Coge el número 1, 2, 3...
        
        # Guardamos la media de esta dimensión
        user_scores[dim_name] = np.mean(puntajes_dim)

# --- BOTÓN DE ANÁLISIS ---
st.write("---")
if st.button("🚀 GENERAR DIAGNÓSTICO PREDICTIVO", type="primary", use_container_width=True):
    
    # 1. CÁLCULO AHP
    # Ordenamos user_scores igual que PESOS_DIMENSIONES
    valores_ordenados = [user_scores[k] for k in CUESTIONARIO.keys()]
    nmg = sum(v * p for v, p in zip(valores_ordenados, PESOS_DIMENSIONES))
    
    # 2. ANÁLISIS DAFO
    fortaleza = max(user_scores, key=user_scores.get)
    debilidad = min(user_scores, key=user_scores.get)
    
    # 3. LLAMADA A LA IA
    with st.spinner("🔮 Simulando escenarios futuros y calculando ROI..."):
        informe = generar_analisis_ia(sector, tamano, debilidad, fortaleza, nmg, user_scores)
    
    # --- RESULTADOS ---
    st.divider()
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.metric("Nivel de Madurez Global", f"{nmg:.2f} / 5.0")
        
        # Gauge Chart (Velocímetro)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = nmg,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Estado Digital"},
            gauge = {'axis': {'range': [0, 5]},
                     'bar': {'color': "#2E86C1"},
                     'steps': [
                         {'range': [0, 2], 'color': "#FFCDD2"},
                         {'range': [2, 3.5], 'color': "#FFF9C4"},
                         {'range': [3.5, 5], 'color': "#C8E6C9"}]}))
        fig_gauge.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.markdown(f"**Fortaleza:** {fortaleza}")
        st.markdown(f"**Debilidad:** {debilidad}")

    with c2:
        # Radar Chart
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=list(user_scores.values()),
            theta=list(user_scores.keys()),
            fill='toself',
            name='Tu Empresa'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            title="Mapa de Competitividad"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # Informe IA
    st.subheader("🧠 Informe de Inteligencia Estratégica")
    st.markdown(informe)
    
    # PDF
    try:
        pdf_data = crear_pdf(nombre_empresa, sector, nmg, informe, user_scores)
        b64 = base64.b64encode(pdf_data).decode()
        st.markdown(f"""
        <div style="text-align:center; margin-top:20px;">
            <a href="data:application/octet-stream;base64,{b64}" download="Plan_Estrategico_{nombre_empresa}.pdf" 
            style="background-color:#E74C3C; color:white; padding:15px 30px; text-decoration:none; border-radius:5px; font-weight:bold;">
            📄 DESCARGAR INFORME EJECUTIVO (PDF)
            </a>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"No se pudo generar el PDF: {e}")
