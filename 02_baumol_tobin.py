import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de página de alta definición
st.set_page_config(
    page_title="Simulador Baumol-Tobin - Sachs & Larraín",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales complementarios
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .stAlert { margin-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# SECTOR DE SEGURIDAD / AUTENTICACIÓN INTEGRADA CON EL AULA VIRTUAL
# =============================================================================
def verificar_autenticacion():
    CLAVE_SECRETA = "Macro2026"  # Clave de acceso directo por explorador externo
    
    try:
        headers = st.context.headers
        referer = headers.get("referer", "").lower()
        fetch_dest = headers.get("sec-fetch-dest", "").lower()
        
        # Acceso libre si se detecta que proviene de un iframe o aula virtual
        if fetch_dest == "iframe" or "moodle" in referer or "canvas" in referer or "classroom" in referer:
            return True
    except Exception:
        pass

    # Pantalla de bloqueo en la barra lateral si se accede por fuera del aula
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
        
        # Vértice superior (Retiro / Saldo Máximo del tramo)
        t_list.append(t_inicio)
        m_list.append(monto_retiro)
        
        # Vértice inferior (Agotamiento del efectivo en el tramo)
        t_list.append(t_fin)
        m_list.append(monto_retiro * (1 - (t_fin - t_inicio) / duracion_intervalo))
        
    return np.array(t_list), np.array(m_list)

# Ejecutar el validador antes de renderizar la app
if verificar_autenticacion():

    # TÍTULO PRINCIPAL Y ENCUADRE PEDAGÓGICO
    st.title("🏦 Demanda Transaccional de Dinero: Modelo de Baumol-Tobin")
    st.markdown("""
    *Desarrollado para la cátedra de Macroeconomía II (Basado en la notación de Sachs & Larraín). 
    Este modelo analiza el dilema de optimización microeconómica entre la liquidez monetaria y el rendimiento de los activos financieros.*
    """)

    # --- BARRA LATERAL: PARAMETRIZACIÓN (Sachs & Larraín) ---
    st.sidebar.header("🛠️ Variables Macroeconómicas Base")
    Q = st.sidebar.slider("Ingreso / Gasto Real del Período (Q)", 100.0, 5000.0, 1000.0, 100.0)
    P = st.sidebar.slider("Nivel General de Precios (P)", 0.5, 5.0, 1.0, 0.1)

    st.sidebar.subheader("⚙️ Estado Inicial (Período 0)")
    b0 = st.sidebar.slider("Costo Real por Transacción (b₀)", 0.5, 20.0, 2.0, 0.5)
    i0 = st.sidebar.slider("Tasa de Interés Nominal (i₀)", 0.01, 0.50, 0.10, 0.01, format="%.2f")

    st.sidebar.subheader("⚡ Shock de Mercado / Innovación (Período 1)")
    b1 = st.sidebar.slider("Costo Real Post-Shock (b₁)", 0.5, 20.0, 2.0, 0.5)
    i1 = st.sidebar.slider("Tasa de Interés Post-Shock (i₁)", 0.01, 0.50, 0.10, 0.01, format="%.2f")

    # --- CÁLCULOS MATEMÁTICOS DE OPTIMIZACIÓN ---
    # Estado Inicial
    N0_opt = np.sqrt((i0 * Q) / (2 * b0))
    m_p0_opt = Q / (2 * N0_opt)
    M0_opt = P * m_p0_opt
    CT0_opt = b0 * N0_opt + i0 * (Q / (2 * N0_opt))
    dias_entre_retiros0 = 30 / N0_opt

    # Estado Post-Shock
    N1_opt = np.sqrt((i1 * Q) / (2 * b1))
    m_p1_opt = Q / (2 * N1_opt)
    M1_opt = P * m_p1_opt
    CT1_opt = b1 * N1_opt + i1 * (Q / (2 * N1_opt))
    dias_entre_retiros1 = 30 / N1_opt

    # --- MÉTRICAS PRINCIPALES ---
    st.subheader("📋 Indicadores de Equilibrio Transaccional (Mes de 30 Días)")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    m_col1.metric(
        label="Viajes Óptimos al Banco (N*)",
        value=f"{N1_opt:.2f}",
        delta=f"{N1_opt - N0_opt:.2f}" if abs(N1_opt - N0_opt) > 0.001 else None
    )
    m_col2.metric(
        label="Saldos Reales Medios (M/P)*",
        value=f"${m_p1_opt:.2f}",
        delta=f"{m_p1_opt - m_p0_opt:.2f}" if abs(m_p1_opt - m_p0_opt) > 0.001 else None
    )
    m_col3.metric(
        label="Días entre Retiros",
        value=f"{dias_entre_retiros1:.1f} días",
        delta=f"{dias_entre_retiros1 - dias_entre_retiros0:.1f}" if abs(dias_entre_retiros1 - dias_entre_retiros0) > 0.1 else None
    )
    m_col4.metric(
        label="Costo Total Mínimo (CT*)",
        value=f"${CT1_opt:.2f}",
        delta=f"{CT1_opt - CT0_opt:.2f}" if abs(CT1_opt - CT0_opt) > 0.001 else None
    )

    # --- CUERPO PRINCIPAL: GRÁFICOS EN PARALELO ---
    col_g1, col_g2 = st.columns(2)

    # -------------------------------------------------------------------------
    # COLUMNA 1: MINIMIZACIÓN DE COSTOS (ESTÁTICA)
    # -------------------------------------------------------------------------
    with col_g1:
        st.write("**Minimización de Costos Totales de Manejo de Efectivo**")
        
        # Rango para el eje X (Número de transacciones N)
        N_max = max(N0_opt, N1_opt) * 2.2
        N_grid = np.linspace(0.2, max(N_max, 5.0), 300)
        
        fig_costos = go.Figure()

        # Componentes de Costo Post-Shock (o Inicial si no hay shock)
        costo_transaccion = b1 * N_grid
        costo_oportunidad = i1 * (Q / (2 * N_grid))
        costo_total = costo_transaccion + costo_oportunidad

        # Curva de Costo Total
        fig_costos.add_trace(go.Scatter(
            x=N_grid, y=costo_total, name="Costo Total CT(N)",
            line=dict(color='blue', width=3)
        ))
        
        # Componente Costo de Transacción
        fig_costos.add_trace(go.Scatter(
            x=N_grid, y=costo_transaccion, name="Costo Transaccional (b·N)",
            line=dict(color='orange', dash='dash')
        ))

        # Componente Costo de Oportunidad
        fig_costos.add_trace(go.Scatter(
            x=N_grid, y=costo_oportunidad, name="Costo Oportunidad (i·Q/2N)",
            line=dict(color='green', dash='dash')
        ))

        # Punto Óptimo Inicial (Si difiere)
        if abs(N1_opt - N0_opt) > 0.001 or abs(CT1_opt - CT0_opt) > 0.001:
            fig_costos.add_trace(go.Scatter(
                x=[N0_opt], y=[CT0_opt], mode='markers+text',
                text=['N₀* (Inicial)'], textposition='top center',
                marker=dict(color='gray', size=10, symbol='circle'), name="Óptimo Inicial"
            ))

        # Punto Óptimo Final
        fig_costos.add_trace(go.Scatter(
            x=[N1_opt], y=[CT1_opt], mode='markers+text',
            text=['N₁* (Óptimo)'], textposition='top right',
            marker=dict(color='blue', size=12, symbol='star'), name="Óptimo Post-Shock"
        ))

        # Línea guía vertical en N*
        fig_costos.add_vline(x=N1_opt, line_dash="dot", line_color="gray")

        fig_costos.update_layout(
            xaxis_title="Número de Transacciones / Viajes (N)",
            yaxis_title="Costos en Términos Reales",
            xaxis=dict(range=[0, max(N_max, 5.0)]),
            yaxis=dict(range=[0, CT1_opt * 2.5]),
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.7)"),
            margin=dict(l=20, r=20, t=20, b=20), height=450
        )
        st.plotly_chart(fig_costos, use_container_width=True)

    # -------------------------------------------------------------------------
    # COLUMNA 2: TRAYECTORIA TEMPORAL "DIENTE DE SIERRA" (DINÁMICA)
    # -------------------------------------------------------------------------
    with col_g2:
        st.write("**Patrón Temporal de Saldos Monetarios Reales (Diente de Sierra)**")
        
        fig_saw = go.Figure()

        # Generación de la trayectoria temporal para el estado post-shock
        t_dias1, m_p_dias1 = generar_diente_sierra(Q, N1_opt, dias=30)
        
        # Trazo del Diente de Sierra
        fig_saw.add_trace(go.Scatter(
            x=t_dias1, y=m_p_dias1, name="Saldo Monetario Real (M/P)ₜ",
            line=dict(color='crimson', width=2.5)
        ))

        # Línea de Saldos Reales Medios (M/P)*
        fig_saw.add_hline(
            y=m_p1_opt, line_dash="dash", line_color="blue",
            annotation_text=f"Saldo Promedio (M/P)* = ${m_p1_opt:.2f}", 
            annotation_position="top right"
        )

        fig_saw.update_layout(
            xaxis_title="Días del Período / Mes (t)",
            yaxis_title="Saldos Reales Retenidos (M/P)",
            xaxis=dict(range=[0, 30], tickmode='linear', tick0=0, dtick=5),
            yaxis=dict(range=[0, (Q / N1_opt) * 1.25]),
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.7)"),
            margin=dict(l=20, r=20, t=20, b=20), height=450
        )
        st.plotly_chart(fig_saw, use_container_width=True)

    # --- RECUADRO PEDAGÓGICO DE SÍNTESIS ---
    st.info(f"""
    ### 🎓 Lección de Análisis Macroeconómico (Sachs & Larraín)
    
    El modelo de **Baumol-Tobin** demuestra que la demanda real de dinero no es un mero porcentaje del ingreso, sino el resultado de un proceso de **optimizacion de costos**:
    
    1. **Igualdad en el Óptimo:** En el punto mínimo $N^* = {N1_opt:.2f}$, el costo transaccional ($b \\cdot N = \\${b1*N1_opt:.2f}$) es exactamente igual al costo de oportunidad ($i \\cdot \\frac{{Q}}{{2N}} = \\${i1*(Q/(2*N1_opt)):.2f}$).
    2. **Economías de Escala en la Liquidez ($\epsilon_Q = 0.5$):** Si el ingreso real ($Q$) se duplica, la demanda óptima de dinero $(\\frac{{M}}{{P}})^*$ no se duplica; solo aumenta en un $\\sqrt{{2}} \\approx 41.4\\%$. Los agentes con mayores ingresos administran su liquidez de forma más eficiente.
    3. **Sensibilidad a la Innovación Financiera ($b$):** La digitalización del sistema bancario o la masificación de transferencias inmediatas reduce el costo de transacción $b$. Como se observa en la simulación, una caída en $b$ disminuye la demanda media de dinero en efectivo $(\\frac{{M}}{{P}})^*$ e incrementa la frecuencia de transferencias ($N^*$).
    """)
