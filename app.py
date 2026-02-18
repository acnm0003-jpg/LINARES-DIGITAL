import streamlit as st
import plotly.graph_objects as go
import numpy as np
from fpdf import FPDF
import base64
from datetime import date

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Linares-Digital", page_icon="🏭", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; }
    .stRadio > label { font-weight: bold; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE IA (OPENAI) ---
import openai

def generar_recomendaciones_ia(api_key, sector, tamano, debilidad, fortaleza, nivel_global):
    """Genera recomendaciones usando GPT si hay API Key, sino usa lógica experta."""
    
    if not api_key:
        return f"""
        **[MODO SIMULACIÓN - EXPERTO VIRTUAL]**
        
        **Diagnóstico para {sector} ({tamano}):**
        
        1. **Punto Crítico ({debilidad}):** Detectamos un cuello de botella aquí.
           - *Acción:* Implementar un protocolo de digitalización básico en esta área antes de 3 meses.
           - *Beneficio:* Reducción de costes operativos estimada en un 15%.
           
        2. **Potenciar Fortaleza ({fortaleza}):** Tu empresa destaca aquí.
           - *Acción:* Utilizar esta fortaleza como palanca para digitalizar el resto.
           - *Beneficio:* Liderazgo en el mercado local de Linares.
           
        *(Para recomendaciones generadas por IA en tiempo real, introduzca una API Key válida).*
        """
    
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = f"""
        Actúa como un consultor experto en Transformación Digital para PYMEs industriales.
        Contexto: Empresa de Linares (España), Sector: {sector}, Tamaño: {tamano}.
        Nivel de Madurez Global: {nivel_global}/5.
        
        Su mayor Fortaleza es: {fortaleza}.
        Su mayor Debilidad es: {debilidad}.
        
        Genera una respuesta con este formato exacto:
        1. ANÁLISIS DE SITUACIÓN: Breve explicación de por qué su debilidad en {debilidad} es peligrosa.
        2. PLAN DE ACCIÓN (3 Pasos): Acciones concretas, baratas y rápidas para mejorar {debilidad}.
        3. BENEFICIO ESPERADO: Qué ganará la empresa (en euros o tiempo) si lo hace.
        
        Tono: Profesional, motivador y directo.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al conectar con la IA: {e}"

# --- FUNCIÓN GENERAR PDF ---
def crear_pdf(nombre_empresa, nmg, fortaleza, debilidad, recomendaciones, radar_chart_bytes):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabecera
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Informe de Madurez Digital: {nombre_empresa}", ln=True, align='C')
    pdf.ln(10)
    
    # Datos Generales
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Fecha: {date.today()}", ln=True)
    pdf.cell(0, 10, f"Nivel Global (NMG): {nmg:.2f} / 5.0", ln=True)
    pdf.ln(5)
    
    # Fortalezas y Debilidades
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 10, f"Punto Fuerte: {fortaleza}", ln=True)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, f"Punto de Mejora: {debilidad}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    
    # Recomendaciones (limpiamos el texto para evitar caracteres raros en PDF básicos)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Hoja de Ruta Recomendada:", ln=True)
    pdf.set_font("Arial", '', 11)
    
    # Multi-cell para texto largo
    recomendaciones_limpias = recomendaciones.replace("**", "").replace("*", "")
    pdf.multi_cell(0, 7, recomendaciones_limpias)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ PRINCIPAL ---
st.title("🏭 Diagnóstico Linares-Digital 4.0")
st.markdown("Herramienta avanzada de autodiagnóstico y hoja de ruta para la reindustrialización de PYMEs.")

# Sidebar
with st.sidebar:
    st.header("Configuración")
    nombre_empresa = st.text_input("Nombre de la Empresa", "Mi Empresa S.L.")
    sector = st.selectbox("Sector", ["Industria Metalmecánica", "Automoción/Auxiliar", "Comercio/Retail", "Servicios", "Agroalimentario"])
    tamano = st.selectbox("Tamaño", ["Micro (<10 empl.)", "Pequeña (10-49)", "Mediana (50-250)"])
    
    st.divider()
    st.markdown("### 🧠 Motor de IA")
    api_key = st.text_input("OpenAI API Key (Opcional)", type="password", help="Si no introduces clave, se usará el sistema experto basado en reglas.")
    
# --- PESOS AHP (Definidos en el TFM) ---
PESOS = {
    "Estrategia": 0.30,
    "Cultura": 0.25,
    "Operaciones": 0.20,
    "Clientes": 0.15,
    "Tecnología": 0.10
}

# --- CUESTIONARIO CON RÚBRICAS ---
st.write("---")
st.subheader("1. Estrategia y Liderazgo (Peso: 30%)")
p1 = st.radio("¿Dispone la empresa de una hoja de ruta digital?", 
              ["1. No, actuamos según surgen problemas.", 
               "2. Tenemos algunas ideas, pero no escritas.",
               "3. Existe un plan básico anual.",
               "4. Hay un plan estratégico definido y con presupuesto.",
               "5. La estrategia digital lidera el modelo de negocio."], index=0)

st.subheader("2. Personas y Cultura (Peso: 25%)")
p2 = st.radio("¿Cuál es el nivel de competencias digitales de la plantilla?",
              ["1. Muy bajo (uso básico de email/móvil).",
               "2. Habilidades básicas de ofimática.",
               "3. Habilidades técnicas específicas del puesto.",
               "4. Personal capacitado y en formación continua.",
               "5. Talento digital avanzado (programación, análisis datos)."], index=0)

st.subheader("3. Operaciones y Procesos (Peso: 20%)")
p3 = st.radio("¿Nivel de integración de sistemas (ERP, producción)?",
              ["1. Gestión en papel o Excel disperso.",
               "2. Software contable/facturación aislado.",
               "3. ERP básico implementado.",
               "4. Sistemas integrados (Ventas conectados con Stock).",
               "5. Automatización total y datos en tiempo real."], index=0)

st.subheader("4. Clientes y Productos (Peso: 15%)")
p4 = st.radio("¿Cómo interactúa digitalmente con el cliente?",
              ["1. No hay interacción digital (solo física/teléfono).",
               "2. Presencia web estática o RRSS básicas.",
               "3. Canal de comunicación activo y captación.",
               "4. Venta online o CRM integrado.",
               "5. Servicios digitales personalizados y servitización."], index=0)

st.subheader("5. Tecnología e Infraestructura (Peso: 10%)")
p5 = st.radio("¿Infraestructura y Ciberseguridad?",
              ["1. Ordenadores domésticos sin seguridad específica.",
               "2. Antivirus básico y copias manuales.",
               "3. Servidor local y copias en nube.",
               "4. Infraestructura Cloud y seguridad perimetral.",
               "5. IoT, Gemelos Digitales y Ciberseguridad avanzada."], index=0)

# --- MAPEO DE RESPUESTAS A NÚMEROS ---
def map_score(opcion):
    return int(opcion.split(".")[0])

scores = {
    "Estrategia": map_score(p1),
    "Cultura": map_score(p2),
    "Operaciones": map_score(p3),
    "Clientes": map_score(p4),
    "Tecnología": map_score(p5)
}

# --- BOTÓN DE PROCESAMIENTO ---
if st.button("🔍 ANALIZAR MADUREZ Y GENERAR HOJA DE RUTA", type="primary"):
    
    # 1. Cálculo AHP
    nmg = sum(scores[dim] * peso for dim, peso in PESOS.items())
    
    # 2. Identificar Puntos Fuertes y Débiles
    fortaleza = max(scores, key=scores.get)
    debilidad = min(scores, key=scores.get)
    
    # 3. Generar Recomendaciones (IA o Experto)
    with st.spinner("Consultando con el Motor de Inteligencia Artificial..."):
        recomendaciones = generar_recomendaciones_ia(api_key, sector, tamano, debilidad, fortaleza, nmg)

    # --- MOSTRAR RESULTADOS ---
    st.write("---")
    col_kpi, col_chart = st.columns([1, 1])
    
    with col_kpi:
        st.markdown(f"### Nivel Global: **{nmg:.2f} / 5.0**")
        st.progress(nmg / 5)
        
        if nmg < 2:
            st.error("Estado: INICIAL. Urge digitalización básica.")
        elif nmg < 3.5:
            st.warning("Estado: EN TRANSICIÓN. Necesita integración.")
        else:
            st.success("Estado: AVANZADO. Foco en innovación.")

        st.markdown(f"""
        - 🟢 **Punto Fuerte:** {fortaleza} (Nivel {scores[fortaleza]})
        - 🔴 **Punto Crítico:** {debilidad} (Nivel {scores[debilidad]})
        """)
    
    with col_chart:
        # Gráfico Radar
        fig = go.Figure(data=go.Scatterpolar(
            r=list(scores.values()),
            theta=list(scores.keys()),
            fill='toself',
            name='Tu Empresa'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # --- MOSTRAR HOJA DE RUTA ---
    st.subheader("🚀 Hoja de Ruta Personalizada")
    st.info(recomendaciones)
    
    # --- DESCARGAR PDF ---
    pdf_bytes = crear_pdf(nombre_empresa, nmg, fortaleza, debilidad, recomendaciones, None)
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Informe_Madurez_{nombre_empresa}.pdf">📥 DESCARGAR INFORME EN PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

