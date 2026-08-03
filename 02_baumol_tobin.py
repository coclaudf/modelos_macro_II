import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de página de alta definición
st.set_page_config(
    page_title="Simulador Baumol-Tobin - Sachs & Larraín",
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
    /* Fuerza el mismo verde oscuro uniforme a ABSOLUTAMENTE TODO el texto, números y LaTeX */
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
    /* Fuerza el mismo azul oscuro uniforme a ABSOLUTAMENTE TODO el texto, números y LaTeX */
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
    
    # 1. Pase directo para iFrames en Moodle (Parámetros 'embed' o 'uner')
    qp = st.query_params
    if "embed" in qp or qp.get("embed") == "true" or "uner" in qp:
        return True

    # 2. Respaldo por encabezado HTTP Referer
    try:
        referer = st.context.headers.get("referer", "").lower()
        if any(dominio in referer for dominio in ["uner.edu.ar", "moodle"]):
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

# Función auxiliar para la construcción de la curva en diente de sierra (Sawtooth)
def generar_diente_sierra(Q_real, N_opt, dias=30):
    if N_opt <= 0:
        return np.array([0, dias]), np.array([Q_real, Q_real])
    
    duracion_intervalo = dias / N_opt
    monto_retiro = Q_real / N_opt
    
    t_list = []
    m_list = []
    
    for k in range(int(np.ceil(N_opt))):
        t_inicio = k * duracion_intervalo
        t_fin = min((k + 1) * duracion_intervalo, dias)
        
        t_list.append(t_inicio)
        m_list.append(monto_retiro)
        
        t_list.append(t_fin)
        m_list.append(monto_retiro * (1 - (t_fin - t_inicio) / duracion_intervalo))
        
    return np.array(t_list), np.array(m_list)

if verificar_autenticacion():

    st.title("🏦 Demanda Transaccional de Dinero: Modelo de Baumol-Tobin")
    st.markdown("""
    *Desarrollado para la cátedra de Macroeconomía II (Basado en la notación de Sachs & Larraín). 
    Este modelo analiza el dilema de optimización microeconómica entre la liquidez monetaria y el rendimiento de los activos financieros.*
    """)

    # --- BARRA LATERAL: PARAMETRIZACIÓN ---
    st.sidebar.header("🛠️ Configuración de Parámetros")
    P = st.sidebar.slider("Nivel General de Precios (P)", 0.5, 5.0, 1.0, 0.1)

    # 1. CONTROLES DE SHOCK (ARRIBA)
    st.sidebar.subheader("⚡ Shocks / Modificaciones")
    Q1 = st.sidebar.slider("Ingreso Real Post-Shock (Q₁)", 100.0, 5000.0, 1000.0, 100.0)
    b1 = st.sidebar.slider("Costo Real Post-Shock (b₁)", 0.5, 20.0, 2.0, 0.5)
    i1 = st.sidebar.slider("Tasa de Interés Post-Shock (i₁)", 0.01, 0.50, 0.10, 0.01, format="%.2f")

    # 2. CONTROLES DE SITUACIÓN INICIAL (ABAJO)
    st.sidebar.subheader("⚙️ Estado Inicial de la Economía")
    st.sidebar.caption("(Solo modificar de ser necesario cambiar el estado inicial de la economía)")
    Q0 = st.sidebar.slider("Ingreso Real Inicial (Q₀)", 100.0, 5000.0, 1000.0, 100.0)
    b0 = st.sidebar.slider("Costo Real por Transacción Inicial (b₀)", 0.5, 20.0, 2.0, 0.5)
    i0 = st.sidebar.slider("Tasa de Interés Nominal Inicial (i₀)", 0.01, 0.50, 0.10, 0.01, format="%.2f")

    # --- CÁLCULOS MATEMÁTICOS DE OPTIMIZACIÓN ---
    N0_opt = np.sqrt((i0 * Q0) / (2 * b0))
    m_p0_opt = Q0 / (2 * N0_opt)
    CT0_opt = b0 * N0_opt + i0 * (Q0 / (2 * N0_opt))
    dias_entre_retiros0 = 30 / N0_opt

    N1_opt = np.sqrt((i1 * Q1) / (2 * b1))
    m_p1_opt = Q1 / (2 * N1_opt)
    CT1_opt = b1 * N1_opt + i1 * (Q1 / (2 * N1_opt))
    dias_entre_retiros1 = 30 / N1_opt

    hay_shock = (b0 != b1) or (i0 != i1) or (Q0 != Q1)

    # --- MÉTRICAS PRINCIPALES ---
    st.subheader("📋 Indicadores de Equilibrio Transaccional (Mes de 30 Días)")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    m_col1.metric(
        label="Viajes Óptimos al Banco (N*)",
        value=f"{N1_opt:.2f}",
        delta=f"{N1_opt - N0_opt:.2f}" if hay_shock else None
    )
    m_col2.metric(
        label="Saldos Reales Medios (M/P)*",
        value=f"USD {m_p1_opt:.2f}",
        delta=f"USD {m_p1_opt - m_p0_opt:.2f}" if hay_shock else None
    )
    m_col3.metric(
        label="Días entre Retiros",
        value=f"{dias_entre_retiros1:.1f} días",
        delta=f"{dias_entre_retiros1 - dias_entre_retiros0:.1f}" if hay_shock else None
    )
    m_col4.metric(
        label="Costo Total Mínimo (CT*)",
        value=f"USD {CT1_opt:.2f}",
        delta=f"USD {CT1_opt - CT0_opt:.2f}" if hay_shock else None
    )

    # --- CUERPO PRINCIPAL: GRÁFICOS EN PARALELO ---
    col_g1, col_g2 = st.columns(2)

    # -------------------------------------------------------------------------
    # COLUMNA 1: MINIMIZACIÓN DE COSTOS
    # -------------------------------------------------------------------------
    with col_g1:
        st.write("**Minimización de Costos Totales de Manejo de Efectivo**")
        
        N_max = max(N0_opt, N1_opt) * 2.2
        N_grid = np.linspace(0.15, max(N_max, 5.0), 300)
        
        fig_costos = go.Figure()

        if hay_shock:
            costo_trans0 = b0 * N_grid
            costo_oport0 = i0 * (Q0 / (2 * N_grid))
            costo_total0 = costo_trans0 + costo_oport0

            fig_costos.add_trace(go.Scatter(
                x=N_grid, y=costo_total0, name="CT₀ (Costo Total Inicial)",
                line=dict(color='black', width=3)
            ))
            fig_costos.add_trace(go.Scatter(
                x=N_grid, y=costo_trans0, name="Transacción b₀·N (Inicial)",
                line=dict(color='#444444', width=1.5)
            ))
            fig_costos.add_trace(go.Scatter(
                x=N_grid, y=costo_oport0, name="Oportunidad i₀·Q₀/2N (Inicial)",
                line=dict(color='#666666', width=1.5)
            ))
            fig_costos.add_trace(go.Scatter(
                x=[N0_opt], y=[CT0_opt], mode='markers+text',
                text=['N₀*'], textposition='top center',
                marker=dict(color='black', size=9, symbol='square'), name="Óptimo N₀*"
            ))

        costo_trans1 = b1 * N_grid
        costo_oport1 = i1 * (Q1 / (2 * N_grid))
        costo_total1 = costo_trans1 + costo_oport1

        fig_costos.add_trace(go.Scatter(
            x=N_grid, y=costo_total1, name="CT₁ (Costo Total Post-Shock)" if hay_shock else "CT(N) Costo Total",
            line=dict(color='#1D4ED8', width=3.5)
        ))
        fig_costos.add_trace(go.Scatter(
            x=N_grid, y=costo_trans1, name="Transacción b₁·N (Post-Shock)" if hay_shock else "Costo Transaccional (b·N)",
            line=dict(color='#D97706', width=2.5)
        ))
        fig_costos.add_trace(go.Scatter(
            x=N_grid, y=costo_oport1, name="Oportunidad i₁·Q₁/2N (Post-Shock)" if hay_shock else "Costo Oportunidad (i·Q/2N)",
            line=dict(color='#15803D', width=2.5)
        ))
        fig_costos.add_trace(go.Scatter(
            x=[N1_opt], y=[CT1_opt], mode='markers+text',
            text=['N₁* (Óptimo)'] if hay_shock else ['N* (Óptimo)'], textposition='top right',
            marker=dict(color='#1D4ED8', size=11, symbol='star'), name="Óptimo N₁*" if hay_shock else "Óptimo N*"
        ))

        fig_costos.add_vline(x=N1_opt, line_dash="dot", line_color="#1D4ED8" if hay_shock else "gray")
        if hay_shock:
            fig_costos.add_vline(x=N0_opt, line_dash="dot", line_color="black")

        fig_costos.update_layout(
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#111827', size=12),
            xaxis=dict(
                title=dict(text="Número de Transacciones / Viajes (N)", font=dict(color='#111827', size=13)),
                tickfont=dict(color='#111827', size=11),
                range=[0, max(N_max, 5.0)],
                showline=True, linecolor='#374151', linewidth=1.5,
                gridcolor='#E5E7EB'
            ),
            yaxis=dict(
                title=dict(text="Costos en Términos Reales", font=dict(color='#111827', size=13)),
                tickfont=dict(color='#111827', size=11),
                range=[0, max(CT0_opt, CT1_opt) * 2.2],
                showline=True, linecolor='#374151', linewidth=1.5,
                gridcolor='#E5E7EB'
            ),
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.95)", font=dict(color='#111827')),
            margin=dict(l=20, r=20, t=20, b=20), height=450
        )
        st.plotly_chart(fig_costos, use_container_width=True)

    # -------------------------------------------------------------------------
    # COLUMNA 2: TRAYECTORIA TEMPORAL "DIENTE DE SIERRA"
    # -------------------------------------------------------------------------
    with col_g2:
        st.write("**Patrón Temporal de Saldos Monetarios Reales (Diente de Sierra)**")
        
        fig_saw = go.Figure()

        if hay_shock:
            t_dias0, m_p_dias0 = generar_diente_sierra(Q0, N0_opt, dias=30)
            fig_saw.add_trace(go.Scatter(
                x=t_dias0, y=m_p_dias0, name="Saldo Inicial (M/P)₀",
                line=dict(color='black', width=2)
            ))
            fig_saw.add_hline(
                y=m_p0_opt, line_dash="dot", line_color="black",
                annotation_text=f"Base = USD {m_p0_opt:.1f}", annotation_position="bottom left"
            )

        t_dias1, m_p_dias1 = generar_diente_sierra(Q1, N1_opt, dias=30)
        fig_saw.add_trace(go.Scatter(
            x=t_dias1, y=m_p_dias1, name="Saldo Post-Shock (M/P)₁" if hay_shock else "Saldo Monetario Real (M/P)ₜ",
            line=dict(color='#DC2626', width=2.5)
        ))

        fig_saw.add_hline(
            y=m_p1_opt, line_dash="dash", line_color="#1D4ED8",
            annotation_text=f"Óptimo = USD {m_p1_opt:.1f}", annotation_position="top right"
        )

        fig_saw.update_layout(
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#111827', size=12),
            xaxis=dict(
                title=dict(text="Días del Período / Mes (t)", font=dict(color='#111827', size=13)),
                tickfont=dict(color='#111827', size=11),
                range=[0, 30], tickmode='linear', tick0=0, dtick=5,
                showline=True, linecolor='#374151', linewidth=1.5,
                gridcolor='#E5E7EB'
            ),
            yaxis=dict(
                title=dict(text="Saldos Reales Retenidos (M/P)", font=dict(color='#111827', size=13)),
                tickfont=dict(color='#111827', size=11),
                range=[0, max(Q0 / N0_opt, Q1 / N1_opt) * 1.25],
                showline=True, linecolor='#374151', linewidth=1.5,
                gridcolor='#E5E7EB'
            ),
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.95)", font=dict(color='#111827')),
            margin=dict(l=20, r=20, t=20, b=20), height=450
        )
        st.plotly_chart(fig_saw, use_container_width=True)

    # --- LEYENDA EXPLICATIVA DINÁMICA DE SHOCKS ---
    if hay_shock:
        explicacion_dinamica = "### ⚡ Diagnóstico Dinámico del Shock Aplicado:\n"
        
        if i1 != i0:
            if i1 > i0:
                explicacion_dinamica += f"* **Alza en la Tasa de Interés ($i_0 = {i0:.2f} \\to i_1 = {i1:.2f}$):** Eleva el costo de oportunidad de mantener dinero líquido. La curva verde de costo de oportunidad gira en sentido antihorario hacia arriba. El agente incrementa los viajes al banco ($N^*$: {N0_opt:.2f} a {N1_opt:.2f}) y reduce sus saldos monetarios reales medios ($(M/P)^*$: USD {m_p0_opt:.1f} a USD {m_p1_opt:.1f}).\n"
            else:
                explicacion_dinamica += f"* **Caída en la Tasa de Interés ($i_0 = {i0:.2f} \\to i_1 = {i1:.2f}$):** Abarata la tenencia de efectivo. La curva verde gira en sentido horario hacia abajo. Los viajes al banco disminuyen ($N^*$: {N0_opt:.2f} a {N1_opt:.2f}) y el saldo promedio retenido aumenta ($(M/P)^*$: USD {m_p0_opt:.1f} a USD {m_p1_opt:.1f}).\n"
        
        if b1 != b0:
            if b1 < b0:
                explicacion_dinamica += f"* **Reducción del Costo Transaccional ($b_0 = {b0:.2f} \\to b_1 = {b1:.2f}$):** Abarata acudir al banco o transferir fondos. La recta de costo transaccional (naranja) se vuelve más plana. Aumenta la frecuencia óptima de retiros ($N^*$: {N0_opt:.2f} a {N1_opt:.2f}) y cae la demanda media de efectivo ($(M/P)^*$: USD {m_p0_opt:.1f} a USD {m_p1_opt:.1f}).\n"
            else:
                explicacion_dinamica += f"* **Aumento del Costo Transaccional ($b_0 = {b0:.2f} \\to b_1 = {b1:.2f}$):** Encarece las transacciones. La recta naranja gira volviéndose más empinada. El agente realiza menos viajes ($N^*$: {N0_opt:.2f} a {N1_opt:.2f}) y acumula más efectivo por viaje ($(M/P)^*$: USD {m_p0_opt:.1f} a USD {m_p1_opt:.1f}).\n"

        if Q1 != Q0:
            if Q1 > Q0:
                explicacion_dinamica += f"* **Expansión del Ingreso Real ($Q_0 = {Q0:.0f} \\to Q_1 = {Q1:.0f}$):** Incrementa el volumen de transacciones del hogar. La curva verde de costo de oportunidad se desplaza hacia arriba. Eleva tanto el número óptimo de retiros ($N^*$: {N0_opt:.2f} a {N1_opt:.2f}) como la demanda de dinero ($(M/P)^*$: USD {m_p0_opt:.1f} a USD {m_p1_opt:.1f}), reflejando economías de escala.\n"
            else:
                explicacion_dinamica += f"* **Contracción del Ingreso Real ($Q_0 = {Q0:.0f} \\to Q_1 = {Q1:.0f}$):** Disminuye la escala transaccional. La curva verde se desplaza hacia abajo, reduciendo la frecuencia de retiros ($N^*$: {N0_opt:.2f} a {N1_opt:.2f}) y la demanda media de liquidez ($(M/P)^*$: USD {m_p0_opt:.1f} a USD {m_p1_opt:.1f}).\n"
        
        st.success(explicacion_dinamica)

    # --- RECUADRO PEDAGÓGICO GENERAL DE SÍNTESIS ---
    costo_trans_val = b1 * N1_opt
    costo_oport_val = i1 * (Q1 / (2 * N1_opt))

    st.info(f"""
    ### 🎓 Lección de Análisis Macroeconómico (Sachs & Larraín)
    
    El modelo de **Baumol-Tobin** demuestra que la demanda real de dinero no es un mero porcentaje del ingreso, sino el resultado de un proceso de **optimización de costos**:
    
    1. **Igualdad en el Óptimo:** En el punto de equilibrio mínimo $N^* = {N1_opt:.2f}$, el costo transaccional $b \\cdot N$ (USD {costo_trans_val:.2f}) es exactamente igual al costo de oportunidad $i \\cdot \\frac{{Q}}{{2N}}$ (USD {costo_oport_val:.2f}).
    2. **Economías de Escala en la Liquidez:** La elasticidad ingreso es $\\epsilon_Q = 0.5$. Si el ingreso real ($Q$) se duplica, la demanda óptima de dinero $(M/P)^*$ no se duplica; solo aumenta en un factor de $\\sqrt{{2}} \\approx 41.4\\%$. Los agentes con mayores ingresos administran su liquidez de forma más eficiente.
    3. **Sensibilidad a la Innovación Financiera ($b$), Tasa ($i$) e Ingreso ($Q$):**
       * Un aumento en la tasa de interés ($i$) o en el ingreso ($Q$) desplaza la curva de costo de oportunidad hacia arriba (giro antihorario), incrementando el número óptimo de viajes ($N^*$) y reduciendo la demanda de dinero.
       * Una reducción en el costo de transacción ($b$) debido a la bancarización o digitalización vuelve la recta de costo transaccional más plana, reduciendo la tenencia promedio de dinero en efectivo $(M/P)^*$.
    """)
