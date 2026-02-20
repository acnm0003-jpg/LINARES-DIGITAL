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
    div[data-testid="stRadio"] > label {font-size: 1.1rem; font-weight: bold; color: #1E88E5;}
    p {font-size: 1rem;}
</style>
""", unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN TÉCNICA (IA) EN BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2621/2621051.png", width=50)
    st.header("⚙️ Configuración")
    
    # --- AUTO-DETECCIÓN DE MODELOS ---
    api_key = st.secrets.get("GOOGLE_API_KEY", None)
    modelo_seleccionado = None
    
    if not api_key:
        st.error("❌ Falta API Key en Secrets")
    else:
        try:
            genai.configure(api_key=api_key)
            # Buscamos modelos compatibles con texto
            modelos_disponibles = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    modelos_disponibles.append(m.name)
            
            if modelos_disponibles:
                st.success(f"✅ Conectado")
                # El usuario elige el modelo que quiera
                modelo_seleccionado = st.selectbox("Modelo IA:", modelos_disponibles, index=0)
            else:
                st.warning("⚠️ Clave válida pero no se encuentran modelos.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

    st.divider()
    st.header("Datos Empresa")
    nombre_empresa = st.text_input("Nombre Comercial", "Mi Empresa S.L.")
    sector = st.selectbox("Sector", ["Industria Metalmecánica", "Automoción/Auxiliar", "Comercio Minorista", "Hostelería", "Servicios Profesionales", "Agroalimentario"])
    tamano = st.selectbox("Tamaño", ["Microempresa (1-9 empl.)", "Pequeña (10-49 empl.)", "Mediana (50-250 empl.)"])

# --- 3. DEFINICIÓN DEL CUESTIONARIO (LENGUAJE PYME) ---
# Estructura: "Pregunta Clara" : ["1. Opción muy básica", ..., "5. Opción avanzada"]
CUESTIONARIO = {
    "Estrategia y Liderazgo": [
        ("¿Tenéis un plan claro para usar la tecnología en el futuro?", [
            "1. No, trabajamos el día a día sin pensar en tecnología.",
            "2. Lo hablamos a veces (hay intención), pero no hay nada escrito.",
            "3. Tenemos algunas metas claras para este año.",
            "4. Tenemos un plan estratégico detallado y con presupuesto asignado.",
            "5. La tecnología es el corazón de nuestro negocio y nos diferencia."
        ]),
        ("¿Quién impulsa la tecnología en la empresa?", [
            "1. Nadie en concreto, o lo vemos como un gasto molesto.",
            "2. Cuando algo se rompe, llamamos a un técnico externo.",
            "3. La dirección aprueba compras si son muy necesarias.",
            "4. La dirección busca activamente nuevas soluciones tecnológicas.",
            "5. Dirección y empleados proponen y prueban innovaciones constantemente."
        ]),
        ("¿Miden los resultados de lo que hacen en internet o con software?", [
            "1. No medimos nada, nos guiamos por intuición.",
            "2. Miramos cosas sueltas de vez en cuando (ej. visitas web).",
            "3. Revisamos algunos datos básicos a final de mes.",
            "4. Tenemos un cuadro de mando (dashboard) que revisamos semanalmente.",
            "5. Tomamos decisiones diarias basadas en datos en tiempo real."
        ])
    ],
    "Clientes y Marketing": [
        ("¿Dónde pueden encontrarles sus clientes en internet?", [
            "1. No estamos en internet (ni web ni redes).",
            "2. Tenemos una ficha básica (ej. Google Maps) o web antigua.",
            "3. Tenemos web actualizada y redes sociales activas.",
            "4. Los clientes nos contactan y piden presupuesto por canales digitales.",
            "5. Ofrecemos una experiencia total (App, área cliente, soporte auto.)."
        ]),
        ("¿Venden productos o servicios a través de internet?", [
            "1. No, solo vendemos en persona o por teléfono.",
            "2. Usamos plataformas de otros (ej. Amazon, Booking, Portales).",
            "3. Tenemos tienda online propia pero vendemos poco.",
            "4. La venta online es una parte importante y está conectada con el almacén.",
            "5. Vendemos en todo el mundo con logística automatizada."
        ]),
        ("¿Cómo guardan y gestionan los datos de sus clientes?", [
            "1. En agendas de papel, post-its o de memoria.",
            "2. En un Excel o en la agenda del móvil.",
            "3. Usamos un programa de gestión de clientes (CRM) básico.",
            "4. El CRM nos avisa para llamar a clientes y registrar ventas.",
            "5. El sistema predice qué cliente va a comprar usando IA."
        ])
    ],
    "Operaciones y Procesos": [
        ("¿Cómo gestionan las facturas, contabilidad y nóminas?", [
            "1. Todo en papel y carpetas físicas.",
            "2. Usamos Word/Excel y se lo mandamos a la gestoría.",
            "3. Tenemos un programa de facturación en el ordenador.",
            "4. Usamos un sistema (ERP) que conecta facturas con almacén/compras.",
            "5. Todo está en la nube y automatizado (sin papeles)."
        ]),
        ("¿Cómo se controla el trabajo diario (taller, almacén, servicios)?", [
            "1. Órdenes verbales o notas escritas a mano.",
            "2. Usamos hojas de cálculo para llevar el control.",
            "3. Tenemos software específico pero no se habla con contabilidad.",
            "4. Todo el proceso se registra digitalmente y podemos ver la trazabilidad.",
            "5. Usamos sensores o tablets para control en tiempo real (IoT)."
        ])
    ],
    "Tecnología e Infraestructura": [
        ("¿Qué tipo de ordenadores y conexión tienen?", [
            "1. Equipos muy viejos y lentos. Sin red interna.",
            "2. Ordenadores domésticos básicos. WiFi estándar.",
            "3. Equipos profesionales. Tenemos un servidor en la oficina.",
            "4. Trabajamos en la nube (Cloud), no dependemos del servidor físico.",
            "5. Infraestructura puntera, escalable y accesible desde cualquier sitio."
        ]),
        ("¿Cómo protegen los datos de la empresa (Ciberseguridad)?", [
            "1. No hacemos nada especial (solo antivirus gratuito).",
            "2. Hacemos copias de seguridad en un disco duro a veces.",
            "3. Copias automáticas y contraseñas seguras.",
            "4. Tenemos firewall profesional, copias en la nube y formación.",
            "5. Auditorías de seguridad y planes de respuesta ante ataques."
        ])
    ],
    "Personas y Cultura": [
        ("¿Saben los empleados usar las herramientas digitales?", [
            "1. Les cuesta mucho, prefieren hacerlo como siempre.",
            "2. Saben lo básico (correo, whatsapp), pero nada más.",
            "3. Saben usar los programas necesarios para su puesto.",
            "4. Reciben formación y se adaptan rápido a cambios.",
            "5. Tenemos expertos digitales en la plantilla."
        ]),
        ("¿Cómo se comunica y trabaja el equipo?", [
            "1. Cada uno a lo suyo. Comunicación de pasillo.",
            "2. Usamos email y teléfono para todo.",
            "3. Compartimos archivos en la nube (Drive/Dropbox).",
            "4. Usamos herramientas de equipo (Teams, Slack, Trello) y colaboramos.",
            "5. Trabajo colaborativo fluido, ágil y transparente entre departamentos."
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

# --- 4. FUNCIÓN IA PREDICTIVA ---
def generar_analisis_ia(modelo, sector, tamano, debilidad, fortaleza, nmg, detalles):
    try:
        # Usamos el modelo que el usuario ha seleccionado en la barra lateral
        ai_model = genai.GenerativeModel(modelo)
            
        prompt = f"""
        Actúa como un Mentor de Negocios Digitales para una PYME de Linares (España).
        
        DATOS DE LA EMPRESA:
        - Sector: {sector} | Tamaño: {tamano}
        - Madurez Global: {nmg:.2f}/5.0
        - Su Punto Fuerte es: {fortaleza}
        - Su Punto Débil es: {debilidad}
        - Respuestas detalladas: {detalles}

        Tu tarea es crear un plan de acción CLARO y SENCILLO. Nada de teoría.
        
        Genera el informe con estas 3 secciones (Usa negritas y listas):

        1. ⚠️ EL RIESGO DE NO ACTUAR (Consecuencias):
           Explica qué problemas reales (dinero, tiempo, clientes) tendrá esta empresa en 1 año si no mejora en '{debilidad}'. Sé realista.

        2. 🛠️ TU PLAN DE ACCIÓN (Paso a paso para solucionar '{debilidad}'):
           - ACCIÓN 1 (GRATIS - PARA HACER MAÑANA): Dime una herramienta gratuita o un cambio de hábito sencillo.
           - ACCIÓN 2 (CORTO PLAZO): Qué tecnología barata deberían contratar o qué proceso cambiar en 3 meses.
           - ACCIÓN 3 (OBJETIVO 1 AÑO): Dónde deberían estar si hacen lo anterior.

        3. 💡 TU VENTAJA OCULTA:
           Una frase motivadora sobre cómo usar su fortaleza en '{fortaleza}' para vender más o trabajar mejor.

        Escribe en español profesional pero cercano.
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
    pdf.cell(0, 10, f"Informe Digital: {nombre}", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Sector: {sector} | Fecha: {date.today()}", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Resultados del Diagnóstico:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Nivel Global: {nmg:.2f} / 5.0", ln=True)
    for dim, score in scores.items():
        pdf.cell(0, 6, f"- {dim}: {score:.2f}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 11)
    # Limpieza de caracteres para PDF
    texto = informe_ia.replace("*", "").replace("#", "").encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, texto)
    return pdf.output(dest='S').encode('latin-1')

# --- 6. INTERFAZ DE USUARIO ---
st.title("🏭 MODELO DE MADUREZ LINARES-DIGITAL")
st.markdown("Autodiagnóstico para PYMEs: Responda estas 12 preguntas para obtener su plan de mejora.")

user_scores = {}
tabs = st.tabs(list(CUESTIONARIO.keys()))

for i, (dim_name, preguntas) in enumerate(CUESTIONARIO.items()):
    with tabs[i]:
        st.subheader(f"{dim_name}")
        puntajes = []
        for preg, opciones in preguntas:
            # Mostramos la pregunta clara y las opciones descriptivas
            sel = st.radio(f"**{preg}**", options=opciones, key=preg)
            puntajes.append(int(sel[0])) # Extrae el número (1..5) del principio del texto
        user_scores[dim_name] = np.mean(puntajes)

# --- 7. BOTÓN DE CÁLCULO ---
st.write("---")

if st.button("🚀 OBTENER MI DIAGNÓSTICO Y PLAN", type="primary", use_container_width=True):
    
    # 1. Cálculo AHP
    nmg = 0
    for dim, score in user_scores.items():
        nmg += score * PESOS_DIMENSIONES[dim]
    
    # 2. DAFO
    fortaleza = max(user_scores, key=user_scores.get)
    debilidad = min(user_scores, key=user_scores.get)
    
    # 3. Consulta a IA
    if modelo_seleccionado:
        with st.spinner("🤖 El sistema está analizando tus respuestas y redactando tu plan..."):
            detalles_texto = ", ".join([f"{k}: {v:.1f}" for k,v in user_scores.items()])
            informe = generar_analisis_ia(modelo_seleccionado, sector, tamano, debilidad, fortaleza, nmg, detalles_texto)
    else:
        informe = "⚠️ Error: No hay conexión con la IA. Revise la API Key."

    # --- RESULTADOS ---
    st.divider()
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Nivel de Madurez Global", f"{nmg:.2f} / 5.0")
        st.success(f"Fortaleza: {fortaleza}")
        st.error(f"Punto Débil: {debilidad}")
        
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

    st.subheader("📋 Tu Plan de Acción Personalizado")
    st.markdown(informe)
    
    try:
        pdf_bytes = crear_pdf(nombre_empresa, sector, nmg, informe, user_scores)
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f'<div style="text-align:center"><a href="data:application/octet-stream;base64,{b64}" download="Plan_Accion_{nombre_empresa}.pdf" style="background-color:#E74C3C; color:white; padding:15px; text-decoration:none; border-radius:5px; font-weight:bold;">📥 DESCARGAR INFORME COMPLETO</a></div>', unsafe_allow_html=True)
    except:
        st.warning("No se pudo generar el PDF.")
