import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de página de alta definición
st.set_page_config(
    page_title="Simulador Consumo Intertemporal - Sachs & Larraín",
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
    CLAVE_SECRETA = "Macro2026"
    
    # 1. Pase directo para iFrames en Moodle (Parámetros 'embed', 'uner' o 'aula')
    qp = st.query_params
    if "embed" in qp or qp.get("embed") == "true" or "uner" in qp or "aula" in qp:
        return True

    # 2. Respaldo por encabezado HTTP Referer
    try:
        referer = st.context.headers.get("referer", "").lower()
        if any(dominio in referer for dominio in ["uner.edu.ar", "moodle", "canvas"]):
            return True
    except Exception:
        pass

    # 3. Pantalla de bloqueo con contraseña para acceso directo por navegador
    st.sidebar.subheader("🔒 Acceso Restringido")
    password_ingresado = st.sidebar.text_input(
        "Este simulador está integrado al Campus Virtual. Introduce la clave de la cátedra:", 
        type="password"
    )
    
    if password_ingresado == CLAVE_SECRETA:
        return True
    elif password_ingresado:
        st.sidebar.error("❌ Clave incorrecta")
        
    st.warning("⚠️ **Acceso No Autorizado:** Por favor, interactúa con este modelo directamente desde las lecturas de tu Aula Virtual.")
    return False

# Ejecución del validador de seguridad
if verificar_autenticacion():

    st.title("📈 Optimización del Consumo Intertemporal (Modelo de Fisher)")
    st.markdown("""
    *Desarrollado para la cátedra de Macroeconomía II (Basado en la notación de Sachs & Larraín). 
    Este modelo evalúa la suavización del consumo, las decisiones de ahorro/endeudamiento y los efectos ingreso y sustitución frente a cambios en la tasa de interés.*
    """)

    # --- BARRA LATERAL: PARAMETRIZACIÓN ---
    st.sidebar.header("🛠️ Configuración de Parámetros")

    # 1. CONTROLES DE SHOCK (ARRIBA)
    st.sidebar.subheader("⚡ Shocks / Modificaciones")
    Q1_1 = st.sidebar.slider("Ingreso Período 1 Post-Shock (Q₁‚₁)", 100.0, 5000.0, 1000.0, 100.0)
    Q2_1 = st.sidebar.slider("Ingreso Período 2 Post-Shock (Q₂‚₁)", 100.0, 5000.0, 1000.0, 100.0)
    r1 = st.sidebar.slider("Tasa de Interés Post-Shock (r₁)", 0.0, 0.50, 0.10, 0.01, format="%.2f")
    rho1 = st.sidebar.slider("Tasa Preferencia Temporal Post-Shock (ρ₁)", 0.0, 0.30, 0.05, 0.01, format="%.2f")

    # 2. CONTROLES DE SITUACIÓN INICIAL (ABAJO)
    st.sidebar.subheader("⚙️ Estado Inicial de la Economía")
    st.sidebar.caption("(Solo modificar de ser necesario cambiar el estado inicial de la economía)")
    Q1_0 = st.sidebar.slider("Ingreso Período 1 Inicial (Q₁‚₀)", 100.0, 5000.0, 1000.0, 100.0)
    Q2_0 = st.sidebar.slider("Ingreso Período 2 Inicial (Q₂‚₀)", 100.0, 5000.0, 1000.0, 100.0)
    r0 = st.sidebar.slider("Tasa de Interés Inicial (r₀)", 0.0, 0.50, 0.10, 0.01, format="%.2f")
    rho0 = st.sidebar.slider("Tasa Preferencia Temporal Inicial (ρ₀)", 0.0, 0.30, 0.05, 0.01, format="%.2f")

    # --- CÁLCULOS MATEMÁTICOS DE OPTIMIZACIÓN (Sachs & Larraín) ---
    # Riqueza Total Presente (Omega)
    Omega0 = Q1_0 + (Q2_0 / (1 + r0))
    Omega1 = Q1_1 + (Q2_1 / (1 + r1))

    # Consumo Óptimo Período 1: C1* = ((1 + rho) / (2 + rho)) * Omega
    C1_0_opt = ((1 + rho0) / (2 + rho0)) * Omega0
    C1_1_opt = ((1 + rho1) / (2 + rho1)) * Omega1

    # Consumo Óptimo Período 2: C2* = ((1 + r) / (1 + rho)) * C1*
    C2_0_opt = ((1 + r0) / (1 + rho0)) * C1_0_opt
    C2_1_opt = ((1 + r1) / (1 + rho1)) * C1_1_opt

    # Ahorro / Endeudamiento Período 1 (S1 = Q1 - C1*)
    S1_0 = Q1_0 - C1_0_opt
    S1_1 = Q1_1 - C1_1_opt

    hay_shock = (Q1_0 != Q1_1) or (Q2_0 != Q2_1) or (r0 != r1) or (rho0 != rho1)

    # --- MÉTRICAS PRINCIPALES ---
    st.subheader("📋 Indicadores de Equilibrio Intertemporal")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    m_col1.metric(
        label="Consumo Presente (C₁*)",
        value=f"USD {C1_1_opt:.2f}",
        delta=f"USD {C1_1_opt - C1_0_opt:.2f}" if hay_shock else None
    )
    m_col2.metric(
        label="Consumo Futuro (C₂*)",
        value=f"USD {C2_1_opt:.2f}",
        delta=f"USD {C2_1_opt - C2_0_opt:.2f}" if hay_shock else None
    )
    m_col3.metric(
        label="Riqueza Humana (Ω)",
        value=f"USD {Omega1:.2f}",
        delta=f"USD {Omega1 - Omega0:.2f}" if hay_shock else None
    )
    
    # Definición de posición financiera
    posicion_txt = "Ahorrador" if S1_1 > 0.01 else ("Prestatario" if S1_1 < -0.01 else "Autarquía")
    m_col4.metric(
        label=f"Ahorro S₁ ({posicion_txt})",
        value=f"USD {S1_1:.2f}",
        delta=f"USD {S1_1 - S1_0:.2f}" if hay_shock else None
    )

    # --- CUERPO PRINCIPAL: GRÁFICO INTERTEMPORAL DE ALTO CONTRASTE ---
    st.write("**Espacio de Consumo Intertemporal ($C_1$ vs $C_2$)**")
    
    # Rango para ejes
    max_c1 = max(Omega0, Omega1) * 1.25
    c1_grid = np.linspace(1.0, max_c1, 400)

    fig_macro = go.Figure()

    # -------------------------------------------------------------------------
    # 1. SITUACIÓN INICIAL (LÍNEA NEGRA SÓLIDA REFERENCIAL IF HAYS HOCK)
    # -------------------------------------------------------------------------
    if hay_shock:
        # Restricción Presupuestaria Inicial (Negro Sólido)
        c2_presup_0 = (Omega0 - c1_grid) * (1 + r0)
        c2_presup_0_clean = np.where(c2_presup_0 >= 0, c2_presup_0, np.nan)
        
        fig_macro.add_trace(go.Scatter(
            x=c1_grid, y=c2_presup_0_clean, name="RP₀ (Restricción Inicial)",
            line=dict(color='black', width=3)
        ))

        # Curva de Indiferencia Inicial (Gris Oscuro Sólido)
        c2_indif_0 = C2_0_opt * ((C1_0_opt / c1_grid) ** (1 + rho0))
        c2_indif_0_clean = np.where(c2_indif_0 <= max_c1 * 1.5, c2_indif_0, np.nan)
        
        fig_macro.add_trace(go.Scatter(
            x=c1_grid, y=c2_indif_0_clean, name="U₀ (Indiferencia Inicial)",
            line=dict(color='#4B5563', width=2)
        ))

        # Punto de Dotación Inicial E₀
        fig_macro.add_trace(go.Scatter(
            x=[Q1_0], y=[Q2_0], mode='markers+text',
            text=['E₀ (Dotación)'], textposition='top right',
            marker=dict(color='black', size=9, symbol='square'), name="Dotación E₀"
        ))

        # Óptimo de Consumo Inicial C₀*
        fig_macro.add_trace(go.Scatter(
            x=[C1_0_opt], y=[C2_0_opt], mode='markers+text',
            text=['C₀*'], textposition='bottom left',
            marker=dict(color='black', size=10, symbol='circle'), name="Óptimo C₀*"
        ))

    # -------------------------------------------------------------------------
    # 2. SITUACIÓN POST-SHOCK (COLOR SÓLIDO DESTACADO)
    # -------------------------------------------------------------------------
    # Restricción Presupuestaria Post-Shock (Azul Rey Sólido)
    c2_presup_1 = (Omega1 - c1_grid) * (1 + r1)
    c2_presup_1_clean = np.where(c2_presup_1 >= 0, c2_presup_1, np.nan)

    fig_macro.add_trace(go.Scatter(
        x=c1_grid, y=c2_presup_1_clean, name="RP₁ (Restricción Post-Shock)" if hay_shock else "RP (Restricción Presupuestaria)",
        line=dict(color='#1D4ED8', width=3.5)
    ))

    # Curva de Indiferencia Post-Shock (Rojo Carmesí Sólido)
    c2_indif_1 = C2_1_opt * ((C1_1_opt / c1_grid) ** (1 + rho1))
    c2_indif_1_clean = np.where(c2_indif_1 <= max_c1 * 1.5, c2_indif_1, np.nan)

    fig_macro.add_trace(go.Scatter(
        x=c1_grid, y=c2_indif_1_clean, name="U₁ (Indiferencia Post-Shock)" if hay_shock else "U (Curva de Indiferencia)",
        line=dict(color='#DC2626', width=2.5)
    ))

    # Punto de Dotación Post-Shock E₁
    fig_macro.add_trace(go.Scatter(
        x=[Q1_1], y=[Q2_1], mode='markers+text',
        text=['E₁ (Dotación)'] if hay_shock else ['E (Dotación)'], textposition='top right',
        marker=dict(color='#D97706', size=11, symbol='diamond'), name="Dotación E₁" if hay_shock else "Dotación E"
    ))

    # Óptimo de Consumo Post-Shock C₁*
    fig_macro.add_trace(go.Scatter(
        x=[C1_1_opt], y=[C2_1_opt], mode='markers+text',
        text=['C₁* (Óptimo)'] if hay_shock else ['C* (Óptimo)'], textposition='top right',
        marker=dict(color='#1D4ED8', size=12, symbol='star'), name="Óptimo C₁*" if hay_shock else "Óptimo C*"
    ))

    # Líneas de Proyección al Punto Óptimo
    fig_macro.add_vline(x=C1_1_opt, line_dash="dot", line_color="#1D4ED8" if hay_shock else "gray")
    fig_macro.add_hline(y=C2_1_opt, line_dash="dot", line_color="#1D4ED8" if hay_shock else "gray")

    fig_macro.update_layout(
        template="plotly_white",
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#111827', size=12),
        xaxis=dict(
            title=dict(text="Consumo Presente (C₁)", font=dict(color='#111827', size=13)),
            tickfont=dict(color='#111827', size=11),
            range=[0, max_c1],
            showline=True, linecolor='#374151', linewidth=1.5,
            gridcolor='#E5E7EB'
        ),
        yaxis=dict(
            title=dict(text="Consumo Futuro (C₂)", font=dict(color='#111827', size=13)),
            tickfont=dict(color='#111827', size=11),
            range=[0, max_c1 * (1 + max(r0, r1))],
            showline=True, linecolor='#374151', linewidth=1.5,
            gridcolor='#E5E7EB'
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.95)", font=dict(color='#111827')),
        margin=dict(l=20, r=20, t=20, b=20), height=520
    )

    st.plotly_chart(fig_macro, use_container_width=True)

    # --- LEYENDA EXPLICATIVA DINÁMICA DE SHOCKS ---
    if hay_shock:
        explicacion_dinamica = "### ⚡ Diagnóstico Dinámico del Shock Aplicado:\n"
        
        if r1 != r0:
            pivot_txt = "Giro en torno al punto de dotación E"
            if r1 > r0:
                explicacion_dinamica += f"* **Incremento en la Tasa de Interés ($r_0 = {r0:.2f} \\to r_1 = {r1:.2f}$):** La restricción presupuestaria gira en sentido horario volviéndose más empinada. Aumenta el costo de oportunidad del consumo presente. "
                if S1_0 > 0:
                    explicacion_dinamica += f"Al ser un **agente ahorrador ($S_1 > 0$)**, el Efecto Ingreso es positivo y refuerza el consumo futuro ($C_2^*$), mientras que el Efecto Sustitución desincentiva $C_1^*$.\n"
                else:
                    explicacion_dinamica += f"Al ser un **agente prestatario ($S_1 < 0$)**, el alza de tasa genera un Efecto Ingreso negativo que reduce el bienestar y contrae el consumo presente ($C_1^*$).\n"
            else:
                explicacion_dinamica += f"* **Caída en la Tasa de Interés ($r_0 = {r0:.2f} \\to r_1 = {r1:.2f}$):** La restricción presupuestaria gira en sentido antihorario volviéndose más plana, abaratando el consumo presente respecto al futuro.\n"
        
        if Q1_1 != Q1_0 or Q2_1 != Q2_0:
            explicacion_dinamica += f"* **Variación en los Ingresos ($\Delta Q$):** Desplaza en forma paralela la restricción presupuestaria. La Riqueza Humana $(\\Omega)$ varía de **USD {Omega0:.1f}** a **USD {Omega1:.1f}**, permitiendo alcanzar una curva de indiferencia más alta ($U_1$).\n"

        if rho1 != rho0:
            if rho1 > rho0:
                explicacion_dinamica += f"* **Mayor Impaciencia Intertemporal ($\rho_0 = {rho0:.2f} \\to \\rho_1 = {rho1:.2f}$):** El agente valora más el presente. La curva de indiferencia se vuelve más empinada en el plano, reasignando consumo desde $C_2^*$ hacia $C_1^*$.\n"
            else:
                explicacion_dinamica += f"* **Mayor Paciencia Intertemporal ($\rho_0 = {rho0:.2f} \\to \\rho_1 = {rho1:.2f}$):** El agente prefiere diferir consumo hacia el futuro, aumentando su tasa de ahorro $S_1$.\n"

        st.success(explicacion_dinamica)

    # --- RECUADRO PEDAGÓGICO GENERAL DE SÍNTESIS ---
    st.info(f"""
    ### 🎓 Lección de Análisis Macroeconómico (Sachs & Larraín)
    
    El modelo de **Consumo Intertemporal de Fisher** demuestra cómo las familias distribuyen su ingreso a lo largo del tiempo para maximizar su bienestar:
    
    1. **Condición de Tangencia:** En el óptimo, la Tasa Marginal de Sustitución Intertemporal ($TMS = 1 + \\rho$) se iguala al precio relativo del consumo presente en términos del futuro ($1 + r$).
    2. **Suavización del Consumo (*Consumption Smoothing*):** Los agentes prefieren trayectorias de consumo estables frente a ingresos volátiles. Por ello, $C_1^*$ depende del valor presente de la riqueza total de por vida $(\\Omega = Q_1 + \\frac{{Q_2}}{{1+r}})$, y no solo del ingreso corriente $Q_1$.
    3. **Efectos Ingreso y Sustitución ($\Delta r$):** Un cambio en la tasa de interés ($r$) altera la pendiente de la restricción presupuestaria (giro sobre la dotación $E$). El resultado neto sobre $C_1^*$ depende del contrapeso entre el **Efecto Sustitución** (que siempre reduce $C_1^*$ ante subas de $r$) y el **Efecto Ingreso** (cuyo signo depende de si el agente es Ahorrador o Prestatario).
    """)
