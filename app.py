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
                st.success(f"✅ Conectado: {len(modelos_disponibles)} modelos.")
                # El usuario elige el modelo que quiera (ej. gemini-1.5-flash)
                modelo_seleccionado = st.selectbox("Selecciona Modelo IA:", modelos_disponibles, index=0)
            else:
                st.warning("⚠️ Clave válida pero no se encuentran modelos.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

    st.divider()
    st.header("Datos Empresa")
    nombre_empresa = st.text_input("Nombre Comercial", "Mi Empresa S.L.")
    sector = st.selectbox("Sector", ["Industria Metalmecánica", "Automoción", "Comercio", "Servicios", "Agroalimentario"])
    tamano = st.selectbox("Tamaño", ["Micro (<10 empl.)", "Pequeña (10-49)", "Mediana (50-250)"])

# --- 3. DEFINICIÓN DEL CUESTIONARIO (BASE CIENTÍFICA) ---
CUESTIONARIO = {
    "Estrategia y Liderazgo": [
        ("1. Visión Digital", ["1. Inexistente", "2. Ideas sueltas", "3. Metas claras", "4. Plan estratégico", "5. Innovación core"]),
        ("2. Liderazgo", ["1. Pasivo", "2. Apoyo puntual", "3. Presupuesto asignado", "4. Liderazgo activo", "5. Cultura de riesgo"]),
        ("3. KPIs", ["1. Sin medición", "2. Esporádica", "3. KPIs básicos", "4. Dashboards", "5. Data-Driven"])
    ],
    "Clientes y Marketing": [
        ("4. Presencia Online", ["1. Nula", "2. Básica", "3. Activa", "4. Móvil/Omnicanal", "5. Experiencia total"]),
        ("5. Venta Online", ["1. No vende", "2. Terceros", "3. Propia básica", "4. Integrada stock", "5. Analítica avanzada"]),
        ("6. CRM", ["1. Papel/Excel", "2. BBDD básica", "3. Software CRM", "4. Integrado ventas", "5. Predicción IA"])
    ],
    "Operaciones y Procesos": [
        ("7. Administración", ["1. Manual", "2. Software aislado", "3. ERP Integrado", "4. Cloud/Auto", "5. Tiempo real"]),
        ("8. Producción/Ops", ["1. Manual", "2. Herramientas aisladas", "3. Digital parcial", "4. Conectado", "5. IoT/Sensores"])
    ],
    "Tecnología e Infraestructura": [
        ("9. Hardware/Red", ["1. Obsoleto", "2. Funcional", "3. Inversión regular", "4. Cloud seguro", "5. Puntero"]),
        ("10. Ciberseguridad", ["1. Nada", "2. Copias", "3. Firewall/Claves", "4. Protocolos", "5. Auditorías"])
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

# --- 4. FUNCIÓN IA PREDICTIVA ---
def generar_analisis_ia(modelo, sector, tamano, debilidad, fortaleza, nmg, detalles):
    try:
        # Usamos el modelo que el usuario ha seleccionado en la barra lateral
        ai_model = genai.GenerativeModel(modelo)
            
        prompt = f"""
        Actúa como un Consultor Estratégico de Industria 4.0.
        Analiza esta empresa de Linares (España):
        - Sector: {sector} | Tamaño: {tamano}
        - Madurez Global: {nmg:.2f}/5.0
        - Fortaleza: {fortaleza} | Debilidad: {debilidad}
        - Detalle Puntuaciones: {detalles}

        Genera un informe estratégico (máximo 300 palabras) con estas 3 secciones obligatorias:

        1. 🔮 PREDICCIÓN DE IMPACTO (Riesgo vs Oportunidad):
           - Qué pasará en 12 meses si NO mejoran en '{debilidad}' (riesgo operativo/financiero).
           - Qué beneficio tangible (estimado en % o eficiencia) obtendrán si suben 1 punto en esa dimensión.

        2. 🚀 HOJA DE RUTA TÁCTICA (3 Pasos):
           - Paso 1 (Inmediato/Gratis): Acción concreta para empezar mañana.
           - Paso 2 (Inversión Baja): Herramienta o cambio recomendado a 3 meses.
           - Paso 3 (Transformación): Objetivo a 1 año.

        3. 💡 VENTAJA COMPETITIVA:
           - Cómo apalancar su fortaleza en '{fortaleza}' para ganar mercado local.

        Usa un tono profesional pero directo.
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
    pdf.cell(0, 10, f"Diagnostico Digital: {nombre}", ln=True, align='C')
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
    texto = informe_ia.replace("*", "").replace("#", "").encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, texto)
    return pdf.output(dest='S').encode('latin-1')

# --- 6. INTERFAZ: CUESTIONARIO ---
st.title("🏭 Diagnóstico Linares-Digital")
st.markdown("Responda a las 12 preguntas clave para obtener su hoja de ruta predictiva.")

user_scores = {}
tabs = st.tabs(list(CUESTIONARIO.keys()))

for i, (dim_name, preguntas) in enumerate(CUESTIONARIO.items()):
    with tabs[i]:
        st.header(f"{dim_name}")
        puntajes = []
        for preg, opciones in preguntas:
            sel = st.radio(f"**{preg}**", options=opciones, key=preg)
            puntajes.append(int(sel[0])) # Extrae el número (1..5)
        user_scores[dim_name] = np.mean(puntajes)

# --- 7. BOTÓN DE CÁLCULO ---
st.write("---")

if st.button("🚀 GENERAR DIAGNÓSTICO PREDICTIVO", type="primary", use_container_width=True):
    
    # 1. Cálculo AHP
    nmg = 0
    for dim, score in user_scores.items():
        nmg += score * PESOS_DIMENSIONES[dim]
        
    # 2. DAFO
    fortaleza = max(user_scores, key=user_scores.get)
    debilidad = min(user_scores, key=user_scores.get)
    
    # 3. Consulta a IA (Usando el modelo seleccionado en la barra lateral)
    if modelo_seleccionado:
        with st.spinner(f"🧠 Consultando a {modelo_seleccionado} para generar predicciones..."):
            detalles_texto = ", ".join([f"{k}: {v:.1f}" for k,v in user_scores.items()])
            informe = generar_analisis_ia(modelo_seleccionado, sector, tamano, debilidad, fortaleza, nmg, detalles_texto)
    else:
        informe = "⚠️ No se ha podido conectar con la IA. Revise la API Key."

    # --- RESULTADOS ---
    st.divider()
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.metric("Nivel de Madurez Global", f"{nmg:.2f} / 5.0")
        
        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = nmg,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {'axis': {'range': [0, 5]}, 'bar': {'color': "#3498DB"},
                     'steps': [{'range': [0, 2], 'color': "#ffcdd2"}, {'range': [2, 3.5], 'color': "#fff9c4"}, {'range': [3.5, 5], 'color': "#c8e6c9"}]}
        ))
        fig_gauge.update_layout(height=250, margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.info(f"**Fortaleza:** {fortaleza}")
        st.error(f"**Debilidad:** {debilidad}")

    with c2:
        # Radar Chart
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=list(user_scores.values()), theta=list(user_scores.keys()), fill='toself', name='Tu Empresa'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), title="Mapa de Competitividad")
        st.plotly_chart(fig_radar, use_container_width=True)

    # Informe IA
    st.subheader("🤖 Informe Estratégico (IA)")
    st.markdown(informe)
    
    # PDF
    try:
        pdf_bytes = crear_pdf(nombre_empresa, sector, nmg, informe, user_scores)
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f'<div style="text-align:center"><a href="data:application/octet-stream;base64,{b64}" download="Informe_{nombre_empresa}.pdf" style="background-color:#E74C3C; color:white; padding:15px; text-decoration:none; border-radius:5px;">📄 DESCARGAR PDF</a></div>', unsafe_allow_html=True)
    except:
        st.warning("No se pudo generar el PDF (Error de caracteres).")

