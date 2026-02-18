import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Linares-Digital", page_icon="🏭", layout="wide")

# --- CABECERA ---
st.title("🏭 Modelo de Madurez Digital: Linares-Digital")
st.markdown("""
Esta herramienta permite a las PYMEs de Linares autoevaluar su nivel de madurez digital.
El diagnóstico utiliza la metodología **AHP (Saaty)** para ponderar las dimensiones según su impacto estratégico.
""")

# --- SIDEBAR: DATOS DE LA EMPRESA ---
st.sidebar.header("Perfil de la Empresa")
sector = st.sidebar.selectbox("Sector de Actividad", ["Industria/Metal", "Comercio", "Servicios", "Agroalimentario", "Otro"])
tamano = st.sidebar.selectbox("Tamaño de la empresa", ["Micro (<10)", "Pequeña (10-49)", "Mediana (50-250)"])

# --- FUNCIONES DE CÁLCULO (ALGORITMO AHP) ---
# Pesos definidos en el TFM (Apartado 4.4)
PESOS = {
    "Estrategia y Liderazgo": 0.30,
    "Personas y Cultura": 0.25,
    "Operaciones y Procesos": 0.20,
    "Clientes y Productos": 0.15,
    "Tecnología e Infraestructura": 0.10
}

def obtener_nivel(score):
    if score < 1.5: return "Nivel 1: Inicial (Analógico)"
    elif score < 2.5: return "Nivel 2: Consciente (Silos)"
    elif score < 3.5: return "Nivel 3: Definido (Integrado)"
    elif score < 4.5: return "Nivel 4: Gestionado (Data-Driven)"
    else: return "Nivel 5: Optimizado (Innovador)"

# --- FORMULARIO DE EVALUACIÓN ---
st.header("📝 Cuestionario de Autodiagnóstico")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Estrategia y Liderazgo")
    el_1 = st.slider("¿Existe una estrategia digital formalizada?", 1, 5, help="1: No existe / 5: Estrategia central del negocio")
    el_2 = st.slider("¿Existe presupuesto específico para digitalización?", 1, 5, help="1: No / 5: Presupuesto anual consolidado")
    el_3 = st.slider("¿La dirección impulsa el cambio digital?", 1, 5, help="1: Pasivo / 5: Liderazgo proactivo")
    promedio_el = np.mean([el_1, el_2, el_3])

    st.subheader("2. Personas y Cultura")
    pc_1 = st.slider("Nivel de competencias digitales del equipo", 1, 5, help="1: Muy bajo / 5: Expertos")
    pc_2 = st.slider("Disposición al aprendizaje y cambio", 1, 5, help="1: Resistencia / 5: Cultura innovadora")
    pc_3 = st.slider("Uso de herramientas colaborativas", 1, 5, help="1: Solo email / 5: Suites completas (Teams/Slack)")
    promedio_pc = np.mean([pc_1, pc_2, pc_3])
    
    st.subheader("3. Operaciones y Procesos")
    op_1 = st.slider("Nivel de integración de sistemas (ERP, etc.)", 1, 5, help="1: Excel/Papel / 5: ERP Integrado total")
    op_2 = st.slider("Automatización de tareas repetitivas", 1, 5, help="1: Manual / 5: Automatizado")
    op_3 = st.slider("Uso de datos en tiempo real", 1, 5, help="1: Intución / 5: Dashboards en tiempo real")
    promedio_op = np.mean([op_1, op_2, op_3])

with col2:
    st.subheader("4. Clientes y Productos")
    cp_1 = st.slider("Presencia en canales digitales", 1, 5, help="1: Nula / 5: Omnicanalidad")
    cp_2 = st.slider("Personalización de productos/servicios", 1, 5, help="1: Estándar / 5: Personalización masiva por datos")
    promedio_cp = np.mean([cp_1, cp_2])

    st.subheader("5. Tecnología e Infraestructura")
    ti_1 = st.slider("Conectividad y Ciberseguridad", 1, 5, help="1: Básica / 5: Avanzada y monitorizada")
    ti_2 = st.slider("Uso de la Nube (Cloud)", 1, 5, help="1: Servidor local / 5: Todo en Cloud")
    promedio_ti = np.mean([ti_1, ti_2])

# --- BOTÓN DE CÁLCULO ---
if st.button("🚀 OBTENER DIAGNÓSTICO", type="primary"):
    
    # 1. Cálculo del Nivel Global (NMG)
    nmg = (promedio_el * PESOS["Estrategia y Liderazgo"] +
           promedio_pc * PESOS["Personas y Cultura"] +
           promedio_op * PESOS["Operaciones y Procesos"] +
           promedio_cp * PESOS["Clientes y Productos"] +
           promedio_ti * PESOS["Tecnología e Infraestructura"])
    
    nivel_texto = obtener_nivel(nmg)

    # --- RESULTADOS VISUALES ---
    st.divider()
    st.header("📊 Resultados del Diagnóstico")
    
    col_res1, col_res2 = st.columns([1, 2])
    
    with col_res1:
        st.metric(label="Nivel de Madurez Global", value=f"{nmg:.2f} / 5.0")
        st.info(f"**Estado:** {nivel_texto}")
        
        # Identificar dimensión más débil
        scores = {
            "Estrategia": promedio_el,
            "Personas": promedio_pc,
            "Operaciones": promedio_op,
            "Clientes": promedio_cp,
            "Tecnología": promedio_ti
        }
        debilidad = min(scores, key=scores.get)
        st.warning(f"⚠️ Atención prioritaria en: **{debilidad}**")

    with col_res2:
        # Gráfico de Radar
        categories = list(scores.keys())
        values = list(scores.values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Tu Empresa'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5])
            ),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- RECOMENDACIONES INTELIGENTES (SIMULACIÓN DE IA) ---
    st.subheader("💡 Recomendaciones Personalizadas (Hoja de Ruta)")
    
    st.markdown(f"""
    Basado en el perfil de tu empresa (**{sector}**, {tamano}) y tus resultados, nuestra IA sugiere las siguientes acciones prioritarias:
    """)
    
    # Lógica de recomendación simple (Puede sustituirse por API de OpenAI)
    if promedio_el < 2.5:
        st.write("- **Estrategia:** Debes definir un plan a 2 años. No compres tecnología sin saber para qué.")
    if promedio_pc < 2.5:
        st.write("- **Cultura:** Inicia talleres de formación digital básicos. La resistencia al cambio es tu mayor riesgo actual.")
    if promedio_op < 2.5:
        st.write("- **Procesos:** Abandona el papel y el Excel. Implementa un ERP básico en la nube (ej. Odoo, Sage).")
    if promedio_ti < 2.5:
        st.write("- **Tecnología:** Revisa tu ciberseguridad. Una copia de seguridad en la nube es el primer paso obligatorio.")
    if nmg > 3.5:
        st.success("¡Tu nivel es alto! Estás listo para explorar Inteligencia Artificial y Big Data.")

    st.caption("Nota: Este informe ha sido generado automáticamente por el sistema Linares-Digital.")
