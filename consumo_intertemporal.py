import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de página de alta definición
st.set_page_config(
    page_title="Simulador de Modelos de Consumo Intertemporal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# FORZADO DE ALTO CONTRASTE (BLINDAJE DE TEXTO UNIFORME PARA MOODLE)
# =============================================================================
st.markdown("""
    <style>
    /* 1. Fondo blanco puro universal */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    
    /* 2. Barra lateral en gris muy suave con bordes oscuros */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 2px solid #CBD5E1 !important;
    }
    
    /* 3. Forzado de texto oscuro general */
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #0F172A !important;
    }

    /* 4. BLINDAJE UNIFORME DE CAJAS ST.SUCCESS (DIAGNÓSTICO DINÁMICO) */
    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentSuccess"]) {
        background-color: #ECFDF5 !important;
        border: 1.5px solid #059669 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentSuccess"]) * {
        color: #064E3B !important;
        font-weight: 500 !important;
    }

    /* 5. BLINDAJE UNIFORME DE CAJAS ST.INFO (RECUADRO GENERAL DE SÍNTESIS) */
    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentInfo"]) {
        background-color: #EFF6FF !important;
        border: 1.5px solid #2563EB !important;
        border-radius: 8px !important;
    }
    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentInfo"]) * {
        color: #1E3A8A !important;
        font-weight: 500 !important;
    }

    /* 6. Optimización de márgenes superiores */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# SECTOR DE SEGURIDAD / AUTENTICACIÓN INTEGRADA CON EL AULA VIRTUAL
# =============================================================================
def verificar_autenticacion():
    CLAVE_SECRETA = "Macro2026"  # Clave de acceso directo por explorador externo
    
    # 1. Pase directo para iFrames en Moodle (Parámetros 'embed', 'uner' o 'aula')
    qp = st.query_params
    if "embed" in qp or qp.get("embed") == "true" or "uner" in qp or "aula" in qp:
        return True

    # 2. Respaldo por encabezado HTTP Referer / Fetch Dest
    try:
        headers = st.context.headers
        referer = headers.get("referer", "").lower()
        fetch_dest = headers.get("sec-fetch-dest", "").lower()
        
        if fetch_dest == "iframe" or any(dom in referer for dom in ["moodle", "canvas", "classroom", "uner.edu.ar"]):
            return True
    except Exception:
        pass

    # 3. Pantalla de bloqueo en la barra lateral si se accede por fuera del aula
    st.sidebar.subheader("🔒 Acceso Restringido")
    password_ingresado = st.sidebar.text_input(
        "Este simulador está integrado al Aula Virtual. Introduce la clave de la cátedra para acceso directo:", 
        type="password"
    )
    
    if password_ingresado == CLAVE_SECRETA:
        return True
    elif password_ingresado:
        st.sidebar.error("❌ Clave incorrecta")
        
    st.warning("⚠️ **Acceso No Autorizado:** Por favor, interactúa con este modelo directamente desde las lecturas de tu Aula Virtual o solicita la clave de desarrollo a la cátedra.")
    st.info("💡 *Nota pedagógica: Diseñamos estas herramientas para que sigan el hilo de tus apuntes teóricos dentro de la plataforma de estudio.*")
    return False

# Ejecutar el validador antes de renderizar la app
if verificar_autenticacion():

    # TÍTULO PRINCIPAL Y ENCUADRE PEDAGÓGICO
    st.title("👨‍💻 Simulador Macroeconómico: Teoría del Consumo Intertemporal")
    st.markdown("""
    *Desarrollado para la cátedra de Macroeconomía II. Este entorno interactivo permite analizar la microfundamentación 
    del consumo, la descomposición de efectos de tasas de interés y la dinámica temporal bajo la Teoría del Ingreso Permanente.*
    """)

    # --- BARRA LATERAL: SELECCIÓN DE MODELO ---
    st.sidebar.header("🛠️ Configuración General")
    modelo_seleccionado = st.sidebar.radio(
        "Seleccione el enfoque analítico:",
        ["1. Modelo de 2 Períodos (Efectos Hicks y Trayectoria)", 
         "2. Dinámica del Ingreso Permanente (Largo Plazo y Liquidez)"]
    )

    # =============================================================================
    # MÓDULO 1: DOS PERÍODOS CON DESCOMPOSICIÓN DE HICKS Y TRAYECTORIA TEMPORAL
    # =============================================================================
    if modelo_seleccionado == "1. Modelo de 2 Períodos (Efectos Hicks y Trayectoria)":
        
        st.sidebar.subheader("🎛️ Parámetros del Modelo")
        y1 = st.sidebar.slider("Ingreso Período 1 (Y₁)", 10.0, 100.0, 50.0, 5.0)
        y2 = st.sidebar.slider("Ingreso Período 2 (Y₂)", 10.0, 100.0, 55.0, 5.0)
        beta = st.sidebar.slider("Factor de Descuento (β)", 0.5, 1.5, 1.0, 0.05)
        
        st.sidebar.subheader("⚡ Shock de Tasa de Interés")
        i_inicial = st.sidebar.slider("Tasa de Interés Inicial (i₀)", 0.0, 1.0, 0.10, 0.05, format="%.2f")
        i_final = st.sidebar.slider("Tasa de Interés Post-Shock (i₁)", 0.0, 1.0, 0.10, 0.05, format="%.2f")

        # Cálculos económicos óptimos (U = ln(C1) + beta * ln(C2))
        omega_inicial = y1 + y2 / (1 + i_inicial)
        omega_final = y1 + y2 / (1 + i_final)
        
        c1_inicial = omega_inicial / (1 + beta)
        c2_inicial = (beta * (1 + i_inicial) * omega_inicial) / (1 + beta)
        u_inicial = np.log(c1_inicial) + beta * np.log(c2_inicial)
        
        c1_final = omega_final / (1 + beta)
        c2_final = (beta * (1 + i_final) * omega_final) / (1 + beta)
        u_final = np.log(c1_final) + beta * np.log(c2_final)
        
        # Descomposición de Hicks
        c1_hicks = np.exp((u_inicial - beta * np.log(beta * (1 + i_final))) / (1 + beta))
        c2_hicks = beta * (1 + i_final) * c1_hicks
        omega_hicks = c1_hicks + c2_hicks / (1 + i_final)

        efecto_sustitucion = c1_hicks - c1_inicial
        efecto_ingreso = c1_final - c1_hicks
        efecto_total = c1_final - c1_inicial
        
        hay_shock = (i_inicial != i_final)
        tipo_hogar = "Equilibrado" if abs(y1 - c1_inicial) < 0.01 else ("Ahorrante" if y1 > c1_inicial else "Deudor")

        st.subheader("📊 Módulo 1: Análisis Geométrico Intertemporal vs Trayectoria Dinámica")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Espacio de Asignación Intertemporal (Estática)**")
            c1_vec = np.linspace(0.1, max(omega_inicial, omega_final) * 1.1, 250)
            fig_static = go.Figure()
            
            # --- CURVAS BASE INICIALES (NEGRO SÓLIDO IF HAY SHOCK) ---
            if hay_shock:
                c2_presup_0 = (omega_inicial - c1_vec) * (1 + i_inicial)
                fig_static.add_trace(go.Scatter(
                    x=c1_vec, y=np.where(c2_presup_0 >= 0, c2_presup_0, np.nan), 
                    name="RPI Inicial (i₀)", line=dict(color='black', width=3)
                ))
                fig_static.add_trace(go.Scatter(
                    x=c1_vec, y=np.exp((u_inicial - np.log(c1_vec)) / beta), 
                    name="U₀ (Bienestar Inicial)", line=dict(color='#4B5563', width=2)
                ))
                fig_static.add_trace(go.Scatter(
                    x=[c1_inicial], y=[c2_inicial], mode='markers+text', 
                    text=['A (Inicial)'], textposition='top right', 
                    marker=dict(color='black', size=10, symbol='circle'), name="Óptimo A (Inicial)"
                ))

            # --- CURVAS POST-SHOCK (COLOR SÓLIDO DESTACADO) ---
            c2_presup_1 = (omega_final - c1_vec) * (1 + i_final)
            fig_static.add_trace(go.Scatter(
                x=c1_vec, y=np.where(c2_presup_1 >= 0, c2_presup_1, np.nan), 
                name="RPF Post-Shock (i₁)" if hay_shock else "Restricción Presupuestaria (RP)", 
                line=dict(color='#1D4ED8', width=3.5)
            ))
            
            if hay_shock:
                fig_static.add_trace(go.Scatter(
                    x=c1_vec, y=(omega_hicks - c1_vec) * (1 + i_final), 
                    name="RP Hicks (Compensada)", line=dict(color='#D97706', width=2, dash='dot')
                ))
                fig_static.add_trace(go.Scatter(
                    x=c1_vec, y=np.exp((u_final - np.log(c1_vec)) / beta), 
                    name="U₁ (Bienestar Final)", line=dict(color='#DC2626', width=2, dash='dash')
                ))
                fig_static.add_trace(go.Scatter(
                    x=[c1_hicks], y=[c2_hicks], mode='markers+text', 
                    text=['C (Hicks)'], textposition='bottom left', 
                    marker=dict(color='#D97706', size=9, symbol='diamond'), name="Punto C (Hicks)"
                ))
            else:
                fig_static.add_trace(go.Scatter(
                    x=c1_vec, y=np.exp((u_inicial - np.log(c1_vec)) / beta), 
                    name="U₀ (Curva Indiferencia)", line=dict(color='#DC2626', width=2.5)
                ))

            # Punto Final B y Dotación Y
            fig_static.add_trace(go.Scatter(
                x=[c1_final], y=[c2_final], mode='markers+text', 
                text=['B (Final)'] if hay_shock else ['Óptimo C*'], textposition='top right', 
                marker=dict(color='#1D4ED8', size=11, symbol='star'), name="Óptimo B (Final)" if hay_shock else "Óptimo C*"
            ))
            fig_static.add_trace(go.Scatter(
                x=[y1], y=[y2], mode='markers+text', 
                text=['Dotación (Y)'], textposition='bottom right', 
                marker=dict(color='#B45309', symbol='x', size=11), name="Dotación (Y)"
            ))

            fig_static.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white',
                font=dict(color='#111827', size=12),
                xaxis=dict(
                    title=dict(text="Consumo Presente (C₁)", font=dict(color='#111827', size=13)),
                    tickfont=dict(color='#111827', size=11),
                    range=[0, max(omega_inicial, omega_final) * 1.05],
                    showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'
                ),
                yaxis=dict(
                    title=dict(text="Consumo Futuro (C₂)", font=dict(color='#111827', size=13)),
                    tickfont=dict(color='#111827', size=11),
                    range=[0, max(omega_inicial, omega_final) * (1 + i_final) * 0.75],
                    showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'
                ),
                legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.95)", font=dict(color='#111827')),
                margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_static, use_container_width=True)

        with col2:
            st.write("**Evolución Temporal del Consumo y el Ingreso (Dinámica)**")
            periodos = ['Período 1 (Hoy)', 'Período 2 (Mañana)']
            fig_dynamic = go.Figure()
            
            fig_dynamic.add_trace(go.Scatter(
                x=periodos, y=[y1, y2], name="Ingreso Disponible (Y)", 
                line=dict(color='black', width=3), marker=dict(size=8)
            ))
            
            if hay_shock:
                fig_dynamic.add_trace(go.Scatter(
                    x=periodos, y=[c1_inicial, c2_inicial], name="Consumo Inicial (C₀)", 
                    line=dict(color='#4B5563', width=2, dash='dash'), marker=dict(size=7)
                ))
                
            fig_dynamic.add_trace(go.Scatter(
                x=periodos, y=[c1_final, c2_final], name="Consumo Post-Shock (C₁)" if hay_shock else "Consumo Óptimo (C*)", 
                line=dict(color='#1D4ED8', width=3), marker=dict(size=9)
            ))
            
            fig_dynamic.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white',
                font=dict(color='#111827', size=12),
                xaxis=dict(
                    tickfont=dict(color='#111827', size=11),
                    showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'
                ),
                yaxis=dict(
                    title=dict(text="Unidades de Producción / Consumo", font=dict(color='#111827', size=13)),
                    tickfont=dict(color='#111827', size=11),
                    range=[0, max(y1, y2, c2_inicial, c2_final) * 1.15],
                    showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'
                ),
                legend=dict(yanchor="bottom", y=0.01, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.95)", font=dict(color='#111827')),
                margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_dynamic, use_container_width=True)

        st.markdown("### 📋 Desglose Cuantitativo de Efectos en el Período 1 ($C_1$)")
        metrics = st.columns(4)
        metrics[0].metric(label="Perfil de Familia", value=tipo_hogar)
        metrics[1].metric(label="Efecto Sustitución (ES)", value=f"{efecto_sustitucion:.2f}", delta="C₁ ↓" if efecto_sustitucion < 0 else "C₁ ↑")
        metrics[2].metric(label="Efecto Ingreso (EI)", value=f"{efecto_ingreso:.2f}", delta="C₁ ↑" if efecto_ingreso > 0 else "C₁ ↓")
        metrics[3].metric(label="Efecto Total (ET)", value=f"{efecto_total:.2f}")

        # --- RECUADRO PEDAGÓGICO DE SÍNTESIS CON ALTO CONTRASTE ---
        st.info(f"""
        ### 🎓 Intuición Económica para el Alumno (Descomposición de Hicks)
        
        Al modificarse la tasa de interés de **{i_inicial*100:.1f}%** a **{i_final*100:.1f}%**, el consumo futuro se vuelve relativamente más barato, generando un **Efecto Sustitución Inequívocamente Negativo** de **{efecto_sustitucion:.2f}** unidades en el consumo presente ($C_1$).  
        
        Como el agente posee un perfil **{tipo_hogar}**, el **Efecto Ingreso** actúa de la siguiente manera: 
        * { "Al ser **ahorrante**, el alza de tasa expande su riqueza intertemporal (Efecto Ingreso positivo de " + f"{efecto_ingreso:.2f}" + " unidades), contrarrestando parcialmente la sustitución." if tipo_hogar == "Ahorrante" else "Al ser **deudor**, el alza de tasa encarece el servicio de su deuda actual, reduciendo su riqueza intertemporal. Ambos efectos se refuerzan hacia la caída del consumo presente." if tipo_hogar == "Deudor" else "Al estar en **equilibrio exacto de dotación**, el Efecto Ingreso puro de Hicks es nulo; la modificación conductual responde netamente al Efecto Sustitución." }
        """)

    # =============================================================================
    # MÓDULO 2: TEORÍA DEL INGRESO PERMANENTE CON COHESIÓN GEOMÉTRICA Y DINÁMICA
    # =============================================================================
    elif modelo_seleccionado == "2. Dinámica del Ingreso Permanente (Largo Plazo y Liquidez)":
        
        st.sidebar.subheader("🎛️ Parámetros Estacionarios")
        y_ee = st.sidebar.slider("Ingreso Base Estacionario (Y₀)", 10.0, 100.0, 50.0, 5.0)
        r = st.sidebar.slider("Tasa de Interés Real (r)", 0.01, 0.20, 0.05, 0.01, format="%.2f")
        horizonte_t = 10
        
        st.sidebar.subheader("⚡ Tipología de Shocks en t=1")
        tipo_shock = st.sidebar.selectbox(
            "Seleccione la naturaleza del shock de ingreso:",
            ["Temporal Transitorio (Solo en t=1)", 
             "Permanente (De t=1 en adelante)", 
             "Futuro Anticipado Positivo (Anuncio en t=1, ocurre en t=4)",
             "Futuro Anticipado Negativo (Anuncio en t=1, ocurre en t=4)"]
        )
        magnitud_shock = st.sidebar.slider("Magnitud del Shock (ΔY)", -30.0, 30.0, 0.0, 5.0)
        
        st.sidebar.subheader("🛡️ Imperfecciones de Mercado")
        restriccion_liquidez = st.sidebar.checkbox("Activar Restricción de Liquidez Estricta (No Endeudamiento)")

        # --- CONSTRUCCIÓN DE VECTORES PARA LA DINÁMICA DE LARGO PLAZO ---
        t_vec = np.arange(0, horizonte_t + 1)
        y_trayectoria = np.full(horizonte_t + 1, y_ee, dtype=float)
        
        if tipo_shock == "Temporal Transitorio (Solo en t=1)":
            y_trayectoria[1] = y_ee + magnitud_shock
        elif tipo_shock == "Permanente (De t=1 en adelante)":
            y_trayectoria[1:] = y_ee + magnitud_shock
        elif tipo_shock in ["Futuro Anticipado Positivo (Anuncio en t=1, ocurre en t=4)", 
                            "Futuro Anticipado Negativo (Anuncio en t=1, ocurre en t=4)"]:
            y_trayectoria[4:] = y_ee + magnitud_shock

        # Factor de descuento agregado para los períodos futuros colapsados (t=2 a t=10)
        gamma_futuro = sum(1 / ((1 + r) ** (t - 1)) for t in range(2, horizonte_t + 1))

        # --- SIMULACIÓN 1: CONSUMIDOR TEÓRICO LIBRE ---
        c_libre = np.zeros(horizonte_t + 1)
        a_libre = np.zeros(horizonte_t + 1)
        c_libre[0] = y_ee
        
        vpi_1 = sum(y_trayectoria[t] / ((1 + r) ** (t - 1)) for t in range(1, horizonte_t + 1))
        factor_anualidad = sum(1 / ((1 + r) ** (t - 1)) for t in range(1, horizonte_t + 1))
        c_p_optimo = vpi_1 / factor_anualidad
        
        for t in range(1, horizonte_t + 1):
            c_libre[t] = c_p_optimo
            a_libre[t] = a_libre[t-1] * (1 + r) + y_trayectoria[t] - c_libre[t]

        # --- SIMULACIÓN 2: CONSUMIDOR CON RESTRICCIÓN DE LIQUIDEZ ---
        c_restric = np.zeros(horizonte_t + 1)
        a_restric = np.zeros(horizonte_t + 1)
        c_restric[0] = y_ee
        
        for t in range(1, horizonte_t + 1):
            vpi_rem = sum(y_trayectoria[k] / ((1 + r) ** (k - t)) for k in range(t, horizonte_t + 1))
            fac_rem = sum(1 / ((1 + r) ** (k - t)) for k in range(t, horizonte_t + 1))
            c_deseado = (a_restric[t-1] * (1 + r) + vpi_rem) / fac_rem
            
            if c_deseado > (y_trayectoria[t] + a_restric[t-1] * (1 + r)):
                c_restric[t] = y_trayectoria[t] + a_restric[t-1] * (1 + r)
                a_restric[t] = 0.0
            else:
                c_restric[t] = c_deseado
                a_restric[t] = a_restric[t-1] * (1 + r) + y_trayectoria[t] - c_restric[t]

        # --- COMPRESIÓN BIDIMENSIONAL PARA EL GRÁFICO ESTÁTICO DE SHOCKS (En t=1) ---
        y1_inicial, y_fut_inicial = y_ee, y_ee * gamma_futuro
        y1_final = y_trayectoria[1]
        y_fut_final = sum(y_trayectoria[t] / ((1 + r) ** (t - 1)) for t in range(2, horizonte_t + 1))
        
        omega_2d_inicial = y1_inicial + y_fut_inicial
        omega_2d_final = y1_final + y_fut_final
        
        c1_inicial_plot, cfut_inicial_plot = y_ee, y_ee * gamma_futuro
        c1_libre_plot, cfut_libre_plot = c_libre[1], c_libre[1] * gamma_futuro
        c1_restric_plot, cfut_restric_plot = c_restric[1], sum(c_restric[t] / ((1 + r) ** (t - 1)) for t in range(2, horizonte_t + 1))

        hay_shock_mod2 = (magnitud_shock != 0.0)

        # DESPLIEGUE DE INTERFAZ EN PARALELO
        st.subheader("📊 Módulo 2: Geometría Intertemporal de Shocks vs Senda de Transición")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.write("**Desplazamiento Analítico de Rectas e Isocuantas (t=1)**")
            c1_grid = np.linspace(0.1, max(omega_2d_inicial, omega_2d_final) * 1.1, 300)
            fig_macro_static = go.Figure()
            
            # --- CURVAS BASE INICIALES (NEGRO SÓLIDO IF HAY SHOCK) ---
            if hay_shock_mod2:
                fig_macro_static.add_trace(go.Scatter(
                    x=c1_grid, y=omega_2d_inicial - c1_grid, 
                    name="RP Inicial (Estado Est.)", line=dict(color='black', width=3)
                ))
                u_init_2d = np.log(c1_inicial_plot) + gamma_futuro * np.log(cfut_inicial_plot / gamma_futuro)
                indif_init_2d = gamma_futuro * np.exp((u_init_2d - np.log(c1_grid)) / gamma_futuro)
                fig_macro_static.add_trace(go.Scatter(
                    x=c1_grid, y=indif_init_2d, 
                    name="U₀ (EE Inicial)", line=dict(color='#4B5563', width=2)
                ))
                fig_macro_static.add_trace(go.Scatter(
                    x=[y1_inicial], y=[y_fut_inicial], mode='markers+text', 
                    text=['X₀ (Dotación EE)'], textposition='bottom left', 
                    marker=dict(color='black', symbol='square', size=9), name="Dotación Inicial X₀"
                ))

            # --- CURVAS POST-SHOCK (COLOR SÓLIDO DESTACADO) ---
            if restriccion_liquidez:
                grid_restric = np.where(c1_grid <= y1_final, omega_2d_final - c1_grid, np.nan)
                fig_macro_static.add_trace(go.Scatter(
                    x=c1_grid, y=grid_restric, 
                    name="RP Final (Con Restricción)", line=dict(color='#DC2626', width=3.5)
                ))
                fig_macro_static.add_vline(x=y1_final, line_dash="dot", line_color="#DC2626", annotation_text="Límite Crédito (Y₁)")
            else:
                fig_macro_static.add_trace(go.Scatter(
                    x=c1_grid, y=omega_2d_final - c1_grid, 
                    name="RP Post-Shock (Libre)" if hay_shock_mod2 else "Restricción Presupuestaria", 
                    line=dict(color='#1D4ED8', width=3.5)
                ))

            u_libre_2d = np.log(c1_libre_plot) + gamma_futuro * np.log(cfut_libre_plot / gamma_futuro)
            indif_libre_2d = gamma_futuro * np.exp((u_libre_2d - np.log(c1_grid)) / gamma_futuro)
            fig_macro_static.add_trace(go.Scatter(
                x=c1_grid, y=indif_libre_2d, 
                name="U₁ (Post-Shock Libre)" if hay_shock_mod2 else "U (Indiferencia)", 
                line=dict(color='#1D4ED8', width=2, dash='dot')
            ))

            # Mapeo de Puntos de Decisión e Ingresos
            fig_macro_static.add_trace(go.Scatter(
                x=[y1_final], y=[y_fut_final], mode='markers+text', 
                text=['X₁ (Dotación Shock)'], textposition='top right', 
                marker=dict(color='#7E22CE', symbol='x', size=11), name="Dotación Post-Shock X₁"
            ))
            fig_macro_static.add_trace(go.Scatter(
                x=[c1_libre_plot], y=[cfut_libre_plot], mode='markers+text', 
                text=['A óptimo (Libre)'], textposition='top left', 
                marker=dict(color='#1D4ED8', size=11, symbol='star'), name="Óptimo A (Libre)"
            ))
            
            if restriccion_liquidez:
                fig_macro_static.add_trace(go.Scatter(
                    x=[c1_restric_plot], y=[cfut_restric_plot], mode='markers+text', 
                    text=['B óptimo (Restringido)'], textposition='bottom right', 
                    marker=dict(color='#DC2626', size=11, symbol='star'), name="Óptimo B (Restringido)"
                ))

            # Rayo de suavización perfecta corregido por el factor temporal
            fig_macro_static.add_trace(go.Scatter(
                x=c1_grid, y=c1_grid * gamma_futuro, 
                name="Senda Suavización Plena", 
                line=dict(color='#6B7280', dash='dot', width=1.5)
            ))

            fig_macro_static.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white',
                font=dict(color='#111827', size=12),
                xaxis=dict(
                    title=dict(text="Consumo Presente Actual (C₁)", font=dict(color='#111827', size=13)),
                    tickfont=dict(color='#111827', size=11),
                    range=[0, max(y1_inicial, y1_final) * 2.5],
                    showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'
                ),
                yaxis=dict(
                    title=dict(text="VP del Consumo Futuro Acumulado (C_Futuro)", font=dict(color='#111827', size=13)),
                    tickfont=dict(color='#111827', size=11),
                    range=[0, max(y_fut_inicial, y_fut_final) * 1.3],
                    showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'
                ),
                legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.95)", font=dict(color='#111827')),
                margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_macro_static, use_container_width=True)

        with col_g2:
            st.write("**Senda Temporal de Transición Dinámica ($t=0$ a $t=10$)**")
            fig_lineas = go.Figure()
            fig_lineas.add_trace(go.Scatter(
                x=t_vec, y=y_trayectoria, name="Ingreso Disponible (Yₜ)", 
                line=dict(color='black', width=3, shape='hv')
            ))
            fig_lineas.add_trace(go.Scatter(
                x=t_vec, y=c_libre, name="Consumo Permanente (Libre)", 
                line=dict(color='#1D4ED8', width=2.5, dash='dash')
            ))
            
            if restriccion_liquidez:
                fig_lineas.add_trace(go.Scatter(
                    x=t_vec, y=c_restric, name="Consumo Efectivo (Con Restricción)", 
                    line=dict(color='#DC2626', width=3)
                ))
                
            fig_lineas.add_hline(y=y_ee, line_dash="dot", line_color="gray", annotation_text="EE Base (t=0)", annotation_position="bottom left")
            fig_lineas.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white',
                font=dict(color='#111827', size=12),
                xaxis=dict(
                    tickmode='linear', tick0=0, dtick=1,
                    title=dict(text="Períodos Temporales (t)", font=dict(color='#111827', size=13)),
                    tickfont=dict(color='#111827', size=11),
                    showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'
                ),
                yaxis=dict(
                    title=dict(text="Escala de Valores Monetarios", font=dict(color='#111827', size=13)),
                    tickfont=dict(color='#111827', size=11),
                    showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'
                ),
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.95)", font=dict(color='#111827')),
                margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_lineas, use_container_width=True)

        # Gráfico complementario secundario: Evolución del Stock de Activos Netos
        st.subheader("🏦 Senda de Acumulación / Desacumulación de Activos Netos ($A_t$)")
        fig_assets = go.Figure()
        fig_assets.add_trace(go.Scatter(
            x=t_vec, y=a_libre, name="Activos Sin Restricción", 
            line=dict(color='#1D4ED8', dash='dash', width=2)
        ))
        if restriccion_liquidez:
            fig_assets.add_trace(go.Scatter(
                x=t_vec, y=a_restric, name="Activos Con Restricción", 
                line=dict(color='#DC2626', width=2.5)
            ))
        fig_assets.add_hline(y=0.0, line_color="black", line_width=1.5)
        fig_assets.update_layout(
            template="plotly_white", paper_bgcolor='white', plot_bgcolor='white',
            font=dict(color='#111827', size=12),
            xaxis=dict(
                tickmode='linear', tick0=0, dtick=1,
                title=dict(text="Períodos Temporales (t)", font=dict(color='#111827', size=13)),
                tickfont=dict(color='#111827', size=11),
                showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'
            ),
            yaxis=dict(
                title=dict(text="Stock de Activos Netos (Aₜ)", font=dict(color='#111827', size=13)),
                tickfont=dict(color='#111827', size=11),
                showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'
            ),
            margin=dict(l=20, r=20, t=20, b=20), height=250, 
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.95)", font=dict(color='#111827'))
        )
        st.plotly_chart(fig_assets, use_container_width=True)

        # --- RECUADRO PEDAGÓGICO ADAPTATIVO CON ALTO CONTRASTE ---
        explicacion_m2 = "### 🎓 Guía de Análisis Macroeconómico para el Alumno\n"
        
        if tipo_shock == "Temporal Transitorio (Solo en t=1)":
            explicacion_m2 += """
            * **Interpretación de la Estática (Gráfico Izquierdo):** El shock positivo mueve la dotación **X₁** horizontalmente a la derecha de **X₀**. La restricción presupuestaria se expande de forma paralela. Como el agente desea suavizar consumo, el óptimo libre busca una isocuanta más alta desplazándose principalmente hacia arriba en el eje futuro. Consume poco hoy y guarda el resto.
            * **Conexión con la Dinámica (Gráfico Derecho):** En la trayectoria temporal, el consumo se mantiene perfectamente estable (plano). El pico transitorio del ingreso en $t=1$ se absorbe por completo mediante un salto en la acumulación de activos financieros ($A_t$).
            """
        elif tipo_shock == "Permanente (De t=1 en adelante)":
            explicacion_m2 += """
            * **Interpretación de la Estática (Gráfico Izquierdo):** Al incrementarse el ingreso en todos los períodos, la dotación salta en diagonal hacia arriba y a la derecha (**X₁**). La restricción presupuestaria se desplaza masivamente hacia afuera. El nuevo punto óptimo de tangencia coincide perfectamente sobre la nueva dotación. 
            * **Conexión con la Dinámica (Gráfico Derecho):** Dado que la variación alteró el ingreso permanente en la misma proporción que el ingreso corriente, el consumo da un salto idéntico en $t=1$ y se estabiliza. No hay incentivos para ahorrar ni desahorrar; la senda de activos netos se mantiene inalterada en cero.
            """
        else:  # Shocks anticipados
            explicacion_m2 += """
            * **El Rol de las Expectativas Racionales (Previsión Perfecta):** Note que en el período $t=1$, el ingreso físico aún no se ha modificado (el eje X de la dotación no cambia). Sin embargo, como el consumidor anticipa el cambio futuro, la dotación se desplaza verticalmente en el gráfico izquierdo. La restricción presupuestaria se expande por "efecto riqueza" desde hoy. El consumidor libre salta de inmediato a un consumo más alto en el período 1.
            * **La Dinámica frente a Restricciones de Liquidez:**
                * Si el shock futuro es *positivo* y se activa la restricción de liquidez, la recta de balance sufre un quiebre estricto (*kink*) vertical en el nivel de ingreso corriente actual. El consumidor no puede endeudarse para adelantar consumo. Verás en el gráfico analítico que queda atrapado en una solución de esquina (**Punto B**) y en la trayectoria el consumo no se moverá hasta que físicamente llegue el período $t=4$.
                * Si el shock futuro es *negativo*, el agente necesita ahorrar de forma preventiva. Dado que el sistema financiero permite resguardar valor sin inconvenientes, el consumidor restringido replica con total exactitud al consumidor libre, contrayendo su nivel de consumo desde el período 1.
            """
        
        st.success(explicacion_m2)
