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
# ESTILOS VISUALES Y FORZADO DE ALTO CONTRASTE (BLINDAJE PARA MOODLE)
# =============================================================================
st.markdown("""
    <style>
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    header { visibility: hidden !important; }
    div[data-testid="stHeader"] { display: none !important; }

    .stApp, [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; color: #0F172A !important; }
    section[data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 2px solid #CBD5E1 !important; }
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #0F172A !important; }

    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentSuccess"]) { background-color: #ECFDF5 !important; border: 1.5px solid #059669 !important; border-radius: 8px !important; }
    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentSuccess"]) * { color: #064E3B !important; font-weight: 500 !important; }

    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentInfo"]) { background-color: #EFF6FF !important; border: 1.5px solid #2563EB !important; border-radius: 8px !important; }
    div[data-testid="stAlert"]:has(div[data-testid="stNotificationContentInfo"]) * { color: #1E3A8A !important; font-weight: 500 !important; }

    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# SECTOR DE SEGURIDAD / AUTENTICACIÓN INTEGRADA CON EL AULA VIRTUAL
# =============================================================================
def verificar_autenticacion():
    CLAVE_SECRETA = "Macro2026"
    qp = st.query_params
    if "embed" in qp or qp.get("embed") == "true" or "uner" in qp or "aula" in qp:
        return True
    try:
        headers = st.context.headers
        referer = headers.get("referer", "").lower()
        fetch_dest = headers.get("sec-fetch-dest", "").lower()
        if fetch_dest == "iframe" or any(dom in referer for dom in ["moodle", "canvas", "classroom", "uner.edu.ar"]):
            return True
    except Exception:
        pass
    st.sidebar.subheader("🔒 Acceso Restringido")
    password_ingresado = st.sidebar.text_input("Introduce la clave de la cátedra para acceso directo:", type="password")
    if password_ingresado == CLAVE_SECRETA: return True
    elif password_ingresado: st.sidebar.error("❌ Clave incorrecta")
    st.warning("⚠️ **Acceso No Autorizado.**")
    return False

if verificar_autenticacion():

    st.title("👨‍💻 Simulador Macroeconómico: Teoría del Consumo Intertemporal")
    st.markdown("""*Desarrollado para la cátedra de Macroeconomía II. Este entorno interactivo permite analizar la microfundamentación del consumo, la descomposición de efectos de tasas de interés y la dinámica temporal bajo la Teoría del Ingreso Permanente.*""")

    st.sidebar.header("🛠️ Configuración General")
    modelo_seleccionado = st.sidebar.radio(
        "Seleccione el enfoque analítico:",
        ["1. Modelo de 2 Períodos (Efectos Hicks y Trayectoria)", "2. Dinámica del Ingreso Permanente (Largo Plazo y Liquidez)"]
    )

    # =============================================================================
    # MÓDULO 1: DOS PERÍODOS CON DESCOMPOSICIÓN DE HICKS
    # =============================================================================
    if modelo_seleccionado == "1. Modelo de 2 Períodos (Efectos Hicks y Trayectoria)":
        
        modo_uso_m1 = st.sidebar.radio("Modo de Interacción:", ["📚 Escenarios Predefinidos (Recomendado)", "🎛️ Modo Manual (Deslizadores)"])

        if modo_uso_m1 == "🎛️ Modo Manual (Deslizadores)":
            st.sidebar.subheader("🎛️ Parámetros del Modelo")
            y1 = st.sidebar.slider("Ingreso Período 1 (Y₁)", 10.0, 100.0, 50.0, 5.0)
            y2 = st.sidebar.slider("Ingreso Período 2 (Y₂)", 10.0, 100.0, 55.0, 5.0)
            beta = st.sidebar.slider("Factor de Descuento (β)", 0.5, 1.5, 1.0, 0.05)
            
            st.sidebar.subheader("⚡ Shock de Tasa de Interés")
            i_inicial = st.sidebar.slider("Tasa de Interés Inicial (i₀)", 0.0, 1.0, 0.10, 0.05, format="%.2f")
            i_final = st.sidebar.slider("Tasa de Interés Post-Shock (i₁)", 0.0, 1.0, 0.10, 0.05, format="%.2f")
            
        else: # Escenarios Predefinidos
            st.sidebar.subheader("📚 Selección de Escenario")
            st.sidebar.info("Seleccione las características para ver el impacto geométrico óptimo.")
            
            familia_predef = st.sidebar.selectbox("1. Tipo de Familia Inicial:", 
                ["Equilibrada (Y₁ ≈ C₁)", "Ahorrante (Y₁ > C₁)", "Deudora (Y₁ < C₁)"])
            
            shock_predef = st.sidebar.selectbox("2. Shock de Tasa de Interés:", 
                ["Situación Inicial (Sin Shock)", "Fuerte Alza de Tasa (10% a 100%)", "Fuerte Baja de Tasa (50% a 5%)"])
            
            # Parametrización automática según selección
            beta = 1.0
            if familia_predef == "Equilibrada (Y₁ ≈ C₁)":
                y1, y2 = 50.0, 55.0
            elif familia_predef == "Ahorrante (Y₁ > C₁)":
                y1, y2 = 80.0, 20.0
            else: # Deudora
                y1, y2 = 20.0, 80.0
                
            if shock_predef == "Situación Inicial (Sin Shock)":
                i_inicial, i_final = 0.10, 0.10
            elif shock_predef == "Fuerte Alza de Tasa (10% a 100%)":
                i_inicial, i_final = 0.10, 1.00
            else: # Fuerte Baja
                i_inicial, i_final = 0.50, 0.05

        st.sidebar.subheader("🔍 Visualización")
        zoom_activado = st.sidebar.checkbox("Activar Lupa (Enfocar en la zona de equilibrio)")

        # --- CÁLCULOS MATEMÁTICOS ---
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
        
        tipo_hogar = "Equilibrado" if abs(y1 - c1_inicial) < 0.01 else ("Ahorrante" if y1 > c1_inicial else "Deudor")
        hay_shock_m1 = (i_inicial != i_final)

        st.subheader("📊 Módulo 1: Análisis Geométrico Intertemporal vs Trayectoria Dinámica")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Espacio de Asignación Intertemporal (Estática)**")
            
            max_omega_x = max(omega_inicial, omega_final, omega_hicks)
            max_omega_y = max(omega_inicial * (1+i_inicial), omega_final * (1+i_final), omega_hicks * (1+i_final))
            
            if zoom_activado:
                min_x = min(c1_inicial, c1_final, c1_hicks, y1) * 0.85
                max_x = max(c1_inicial, c1_final, c1_hicks, y1) * 1.15
                min_y = min(c2_inicial, c2_final, c2_hicks, y2) * 0.85
                max_y = max(c2_inicial, c2_final, c2_hicks, y2) * 1.15
                rango_x = [min_x, max_x]
                rango_y = [min_y, max_y]
            else:
                rango_x = [0, max_omega_x * 1.1]
                rango_y = [0, max_omega_y * 1.1]
            
            c1_vec = np.linspace(0.1, max_omega_x * 1.2, 300)
            fig_static = go.Figure()
            
            # 1. RESTRICCIONES (PUNTEADAS)
            if hay_shock_m1:
                fig_static.add_trace(go.Scatter(x=c1_vec, y=(omega_inicial - c1_vec) * (1 + i_inicial), name="RP Inicial (i₀)", line=dict(color='gray', width=2, dash='dash')))
                fig_static.add_trace(go.Scatter(x=c1_vec, y=(omega_hicks - c1_vec) * (1 + i_final), name="RP Hicks (Teórica)", line=dict(color='orange', width=2, dash='dot')))
            
            fig_static.add_trace(go.Scatter(x=c1_vec, y=(omega_final - c1_vec) * (1 + i_final), name="RP Final (i₁)" if hay_shock_m1 else "Restricción Presupuestaria", line=dict(color='blue', width=2.5, dash='dash')))
            
            # 2. ISOCUANTAS (LLENAS)
            u0_y = np.exp((u_inicial - np.log(c1_vec)) / beta)
            fig_static.add_trace(go.Scatter(x=c1_vec, y=np.where(u0_y <= max_omega_y*1.5, u0_y, np.nan), name="U₀ (Bienestar Inicial)", line=dict(color='green', width=2)))
            
            if hay_shock_m1:
                u1_y = np.exp((u_final - np.log(c1_vec)) / beta)
                fig_static.add_trace(go.Scatter(x=c1_vec, y=np.where(u1_y <= max_omega_y*1.5, u1_y, np.nan), name="U₁ (Bienestar Final)", line=dict(color='blue', width=2)))
            
            # 3. PUNTOS Y DOTACIÓN
            fig_static.add_trace(go.Scatter(x=[y1], y=[y2], mode='markers+text', text=['Dotación (Y)'], textposition='bottom right', marker=dict(color='black', symbol='x', size=10), name="Dotación"))
            if hay_shock_m1:
                fig_static.add_trace(go.Scatter(x=[c1_inicial], y=[c2_inicial], mode='markers+text', text=['A (Inicial)'], textposition='top right', marker=dict(color='green', size=10), showlegend=False))
                fig_static.add_trace(go.Scatter(x=[c1_hicks], y=[c2_hicks], mode='markers+text', text=['C (Hicks)'], textposition='bottom left', marker=dict(color='orange', size=8), showlegend=False))
            fig_static.add_trace(go.Scatter(x=[c1_final], y=[c2_final], mode='markers+text', text=['B (Final)'] if hay_shock_m1 else ['A (Óptimo)'], textposition='top right', marker=dict(color='blue', size=10), showlegend=False))

            fig_static.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white',
                xaxis_title="Consumo Presente (C₁)", yaxis_title="Consumo Futuro (C₂)",
                xaxis=dict(range=rango_x, showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'), 
                yaxis=dict(range=rango_y, showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'),
                legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.8)"), margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_static, use_container_width=True)

        with col2:
            st.write("**Evolución Temporal del Consumo y el Ingreso (Dinámica)**")
            periodos = ['Período 1 (Hoy)', 'Período 2 (Mañana)']
            fig_dynamic = go.Figure()
            fig_dynamic.add_trace(go.Scatter(x=periodos, y=[y1, y2], name="Ingreso Disponible (Y)", line=dict(color='black', width=3), marker=dict(size=8)))
            
            if hay_shock_m1:
                fig_dynamic.add_trace(go.Scatter(x=periodos, y=[c1_inicial, c2_inicial], name="Consumo Inicial", line=dict(color='green', width=2, dash='dash'), marker=dict(size=6)))
            
            fig_dynamic.add_trace(go.Scatter(x=periodos, y=[c1_final, c2_final], name="Consumo Final", line=dict(color='blue', width=3), marker=dict(size=8)))
            
            fig_dynamic.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white',
                yaxis_title="Unidades de Producción/Consumo", yaxis=dict(range=[0, max(y1, y2, c2_inicial, c2_final)*1.15], showline=True, linecolor='#374151', gridcolor='#E5E7EB'),
                xaxis=dict(showline=True, linecolor='#374151', gridcolor='#E5E7EB'),
                legend=dict(yanchor="bottom", y=0.01, xanchor="left", x=0.01), margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_dynamic, use_container_width=True)

        st.markdown("### 📋 Desglose Cuantitativo de Efectos en el Período 1 ($C_1$)")
        metrics = st.columns(4)
        metrics[0].metric(label="Perfil de Familia", value=tipo_hogar)
        metrics[1].metric(label="Efecto Sustitución (ES)", value=f"{efecto_sustitucion:.2f}", delta="C₁ ↓" if efecto_sustitucion < 0 else ("C₁ ↑" if efecto_sustitucion > 0 else "0.00"))
        metrics[2].metric(label="Efecto Ingreso (EI)", value=f"{efecto_ingreso:.2f}", delta="C₁ ↑" if efecto_ingreso > 0 else ("C₁ ↓" if efecto_ingreso < 0 else "0.00"))
        metrics[3].metric(label="Efecto Total (ET)", value=f"{efecto_total:.2f}")

        st.info(f"""
        **Intuición Económica para el Alumno:** Al incrementarse la tasa de interés, el consumo futuro se vuelve relativamente más barato, generando un **Efecto Sustitución** de **{efecto_sustitucion:.2f}** unidades sobre el consumo presente.  
        Como el agente posee un perfil **{tipo_hogar}**, el **Efecto Ingreso** actúa de la siguiente manera: 
        { "Al ser ahorrante, el alza de tasa expande su riqueza intertemporal (Efecto Ingreso positivo), contrarrestando parcialmente la sustitución." if tipo_hogar == "Ahorrante" else "Al ser deudor, el alza de tasa encarece el servicio de su deuda actual, volviéndolo más pobre intertemporalmente. Ambos efectos se refuerzan hacia la caída del consumo presente." if tipo_hogar == "Deudor" else "Al estar en equilibrio exacto de dotación, el Efecto Ingreso puro de Hicks es nulo; la modificación conductual responde netamente al Efecto Sustitución." }
        """)

    # =============================================================================
    # MÓDULO 2: TEORÍA DEL INGRESO PERMANENTE CON COHESIÓN GEOMÉTRICA Y DINÁMICA
    # =============================================================================
    elif modelo_seleccionado == "2. Dinámica del Ingreso Permanente (Largo Plazo y Liquidez)":
        
        modo_uso_m2 = st.sidebar.radio("Modo de Interacción:", ["📚 Escenarios Predefinidos (Recomendado)", "🎛️ Modo Manual (Deslizadores)"])

        if modo_uso_m2 == "🎛️ Modo Manual (Deslizadores)":
            st.sidebar.subheader("🎛️ Parámetros Estacionarios")
            y_ee = st.sidebar.slider("Ingreso Base Estacionario (Y₀)", 10.0, 100.0, 50.0, 5.0)
            r = st.sidebar.slider("Tasa de Interés Real (r)", 0.01, 0.20, 0.05, 0.01, format="%.2f")
            
            st.sidebar.subheader("⚡ Tipología de Shocks en t=1")
            tipo_shock = st.sidebar.selectbox("Naturaleza del shock de ingreso:",
                ["Temporal Transitorio (Solo en t=1)", "Permanente (De t=1 en adelante)", 
                 "Futuro Anticipado Positivo (Anuncio en t=1, ocurre en t=4)", "Futuro Anticipado Negativo (Anuncio en t=1, ocurre en t=4)"])
            magnitud_shock = st.sidebar.slider("Magnitud del Shock (ΔY)", -30.0, 30.0, 0.0, 5.0)
            restriccion_liquidez = st.sidebar.checkbox("Activar Restricción de Liquidez Estricta (No Endeudamiento)")
            
        else: # Escenarios Predefinidos
            st.sidebar.subheader("📚 Selección de Escenario")
            st.sidebar.info("Selecciona el tipo de shock para ver cómo se comporta la senda dinámica óptima.")
            
            escenario_shock = st.sidebar.selectbox("1. Escenario Macroeconómico:", [
                "Situación Inicial (Sin Shock)",
                "A. Transitorio Positivo (Ej. Ganar Lotería hoy)",
                "B. Transitorio Negativo (Ej. Gasto médico imprevisto hoy)",
                "C. Permanente Positivo (Ej. Ascenso laboral hoy)",
                "D. Anticipado Positivo (Ej. Anuncio de herencia para el futuro)",
                "E. Anticipado Negativo (Ej. Anuncio de despido para el futuro)"
            ])
            restriccion_liquidez = st.sidebar.checkbox("Activar Restricción de Liquidez (Impacta en Shocks Anticipados)")
            
            # Variables base ancladas
            y_ee = 50.0
            r = 0.05
            
            if escenario_shock == "Situación Inicial (Sin Shock)":
                tipo_shock = "Temporal Transitorio (Solo en t=1)"
                magnitud_shock = 0.0
            elif escenario_shock == "A. Transitorio Positivo (Ej. Ganar Lotería hoy)":
                tipo_shock = "Temporal Transitorio (Solo en t=1)"
                magnitud_shock = 30.0
            elif escenario_shock == "B. Transitorio Negativo (Ej. Gasto médico imprevisto hoy)":
                tipo_shock = "Temporal Transitorio (Solo en t=1)"
                magnitud_shock = -25.0
            elif escenario_shock == "C. Permanente Positivo (Ej. Ascenso laboral hoy)":
                tipo_shock = "Permanente (De t=1 en adelante)"
                magnitud_shock = 20.0
            elif escenario_shock == "D. Anticipado Positivo (Ej. Anuncio de herencia para el futuro)":
                tipo_shock = "Futuro Anticipado Positivo (Anuncio en t=1, ocurre en t=4)"
                magnitud_shock = 30.0
            elif escenario_shock == "E. Anticipado Negativo (Ej. Anuncio de despido para el futuro)":
                tipo_shock = "Futuro Anticipado Negativo (Anuncio en t=1, ocurre en t=4)"
                magnitud_shock = -20.0

        st.sidebar.subheader("🔍 Visualización")
        zoom_activado_m2 = st.sidebar.checkbox("Activar Lupa (Enfocar en la zona de equilibrio)")

        horizonte_t = 10
        # --- CONSTRUCCIÓN DE VECTORES PARA LA DINÁMICA ---
        t_vec = np.arange(0, horizonte_t + 1)
        y_trayectoria = np.full(horizonte_t + 1, y_ee, dtype=float)
        
        if tipo_shock == "Temporal Transitorio (Solo en t=1)":
            y_trayectoria[1] = y_ee + magnitud_shock
        elif tipo_shock == "Permanente (De t=1 en adelante)":
            y_trayectoria[1:] = y_ee + magnitud_shock
        elif tipo_shock in ["Futuro Anticipado Positivo (Anuncio en t=1, ocurre en t=4)", 
                            "Futuro Anticipado Negativo (Anuncio en t=1, ocurre en t=4)"]:
            y_trayectoria[4:] = y_ee + magnitud_shock

        gamma_futuro = sum(1 / ((1 + r) ** (t - 1)) for t in range(2, horizonte_t + 1))

        # --- SIMULACIÓN 1: CONSUMIDOR LIBRE ---
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

        # --- COMPRESIÓN BIDIMENSIONAL PARA EL GRÁFICO ESTÁTICO (En t=1) ---
        y1_inicial, y_fut_inicial = y_ee, y_ee * gamma_futuro
        y1_final = y_trayectoria[1]
        y_fut_final = sum(y_trayectoria[t] / ((1 + r) ** (t - 1)) for t in range(2, horizonte_t + 1))
        
        omega_2d_inicial = y1_inicial + y_fut_inicial
        omega_2d_final = y1_final + y_fut_final
        
        c1_inicial_plot, cfut_inicial_plot = y_ee, y_ee * gamma_futuro
        c1_libre_plot, cfut_libre_plot = c_libre[1], c_libre[1] * gamma_futuro
        c1_restric_plot, cfut_restric_plot = c_restric[1], sum(c_restric[t] / ((1 + r) ** (t - 1)) for t in range(2, horizonte_t + 1))

        hay_shock_m2 = (magnitud_shock != 0.0)

        st.subheader(f"📊 Módulo 2: Geometría Intertemporal de Shocks vs Senda de Transición")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.write("**Desplazamiento Analítico de Rectas e Isocuantas (t=1)**")
            
            max_omega_2d = max(omega_2d_inicial, omega_2d_final)
            
            if zoom_activado_m2:
                min_x2 = min(c1_inicial_plot, c1_libre_plot, c1_restric_plot, y1_inicial, y1_final) * 0.85
                max_x2 = max(c1_inicial_plot, c1_libre_plot, c1_restric_plot, y1_inicial, y1_final) * 1.15
                min_y2 = min(cfut_inicial_plot, cfut_libre_plot, cfut_restric_plot, y_fut_inicial, y_fut_final) * 0.85
                max_y2 = max(cfut_inicial_plot, cfut_libre_plot, cfut_restric_plot, y_fut_inicial, y_fut_final) * 1.15
                rango_x2 = [min_x2, max_x2]
                rango_y2 = [min_y2, max_y2]
            else:
                rango_x2 = [0, max_omega_2d * 1.1]
                rango_y2 = [0, max_omega_2d * 1.1]
            
            c1_grid = np.linspace(0.1, max_omega_2d * 1.2, 300)
            fig_macro_static = go.Figure()
            
            # 1. RESTRICCIONES (PUNTEADAS)
            if hay_shock_m2:
                fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=omega_2d_inicial - c1_grid, name="RP Inicial (Estado Est.)", line=dict(color='gray', width=2, dash='dash')))
            
            if restriccion_liquidez:
                grid_restric = np.where(c1_grid <= y1_final, omega_2d_final - c1_grid, np.nan)
                fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=grid_restric, name="RP Final (Con Restricción)", line=dict(color='crimson', width=3, dash='dash')))
                fig_macro_static.add_vline(x=y1_final, line_dash="dot", line_color="crimson", annotation_text="Límite Crédito (Y₁)")
            else:
                fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=omega_2d_final - c1_grid, name="RP Post-Shock (Libre)" if hay_shock_m2 else "Restricción Presupuestaria", line=dict(color='blue', width=2.5, dash='dash')))

            # 2. ISOCUANTAS (LLENAS)
            u_init_2d = np.log(c1_inicial_plot) + gamma_futuro * np.log(cfut_inicial_plot / gamma_futuro)
            indif_init_2d = gamma_futuro * np.exp((u_init_2d - np.log(c1_grid)) / gamma_futuro)
            fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=np.where(indif_init_2d <= max_omega_2d*1.5, indif_init_2d, np.nan), name="U₀ (EE Inicial)", line=dict(color='green', width=2)))
            
            if hay_shock_m2:
                u_libre_2d = np.log(c1_libre_plot) + gamma_futuro * np.log(cfut_libre_plot / gamma_futuro)
                indif_libre_2d = gamma_futuro * np.exp((u_libre_2d - np.log(c1_grid)) / gamma_futuro)
                fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=np.where(indif_libre_2d <= max_omega_2d*1.5, indif_libre_2d, np.nan), name="U₁ (Post-Shock Libre)", line=dict(color='blue', width=2)))

            # 3. PUNTOS Y DOTACIONES
            if hay_shock_m2:
                fig_macro_static.add_trace(go.Scatter(x=[y1_inicial], y=[y_fut_inicial], mode='markers+text', text=['X₀ (Dotación EE)'], textposition='bottom left', marker=dict(color='black', symbol='square', size=8), name="Dotación Inicial"))
            fig_macro_static.add_trace(go.Scatter(x=[y1_final], y=[y_fut_final], mode='markers+text', text=['X₁ (Dotación Shock)'] if hay_shock_m2 else ['X₀ (Dotación)'], textposition='top right', marker=dict(color='purple', symbol='x', size=10), name="Dotación Post-Shock"))
            fig_macro_static.add_trace(go.Scatter(x=[c1_libre_plot], y=[cfut_libre_plot], mode='markers+text', text=['A óptimo (Libre)'], textposition='top left', marker=dict(color='blue', size=10), showlegend=False))
            
            if restriccion_liquidez:
                fig_macro_static.add_trace(go.Scatter(x=[c1_restric_plot], y=[cfut_restric_plot], mode='markers+text', text=['B óptimo (Restringido)'], textposition='bottom right', marker=dict(color='crimson', size=10), showlegend=False))

            fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=c1_grid * gamma_futuro, name="Senda de Suavización Plena", line=dict(color='darkgray', dash='dot', width=1.5)))

            fig_macro_static.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white',
                xaxis_title="Consumo Presente Actual (C₁)", yaxis_title="VP del Consumo Futuro Acumulado (C_Futuro)",
                xaxis=dict(range=rango_x2, showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'),
                yaxis=dict(range=rango_y2, showline=True, linecolor='#374151', linewidth=1.5, gridcolor='#E5E7EB'),
                legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.7)"), margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_macro_static, use_container_width=True)

        with col_g2:
            st.write("**Senda Temporal de Transición Dinámica ($t=0$ a $t=10$)**")
            fig_lineas = go.Figure()
            fig_lineas.add_trace(go.Scatter(x=t_vec, y=y_trayectoria, name="Ingreso Disponible (Yₜ)", line=dict(color='black', width=3, shape='hv')))
            fig_lineas.add_trace(go.Scatter(x=t_vec, y=c_libre, name="Consumo Permanente (Libre)", line=dict(color='blue', width=2.5, dash='dash')))
            
            if restriccion_liquidez:
                fig_lineas.add_trace(go.Scatter(x=t_vec, y=c_restric, name="Consumo Efectivo (Con Restricción)", line=dict(color='crimson', width=3)))
                
            fig_lineas.add_hline(y=y_ee, line_dash="dot", line_color="gray", annotation_text="EE Base (t=0)", annotation_position="bottom left")
            fig_lineas.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white',
                xaxis=dict(tickmode='linear', tick0=0, dtick=1, title="Períodos Temporales (t)", showline=True, linecolor='#374151', gridcolor='#E5E7EB'), 
                yaxis=dict(title="Escala de Valores Monetarios", showline=True, linecolor='#374151', gridcolor='#E5E7EB'),
                margin=dict(l=20, r=20, t=20, b=20), height=450, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
            )
            st.plotly_chart(fig_lineas, use_container_width=True)

        # Gráfico complementario secundario: Evolución del Stock de Activos Netos
        st.subheader("🏦 Senda de Acumulación / Desacumulación de Activos Netos ($A_t$)")
        fig_assets = go.Figure()
        fig_assets.add_trace(go.Scatter(x=t_vec, y=a_libre, name="Activos Sin Restricción", line=dict(color='blue', dash='dash')))
        if restriccion_liquidez:
            fig_assets.add_trace(go.Scatter(x=t_vec, y=a_restric, name="Activos Con Restricción", line=dict(color='crimson', width=2.5)))
        fig_assets.add_hline(y=0.0, line_color="black", line_width=1)
        fig_assets.update_layout(
            template="plotly_white", paper_bgcolor='white', plot_bgcolor='white',
            xaxis=dict(tickmode='linear', tick0=0, dtick=1, title="Períodos Temporales (t)", showline=True, linecolor='#374151', gridcolor='#E5E7EB'), 
            yaxis=dict(title="Stock de Activos Netos", showline=True, linecolor='#374151', gridcolor='#E5E7EB'),
            margin=dict(l=20, r=20, t=20, b=20), height=250, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig_assets, use_container_width=True)

        # --- RECUADRO PEDAGÓGICO ADAPTATIVO ---
        st.success("### 🎓 Guía de Análisis Macroeconómico para el Alumno")
        
        if tipo_shock == "Temporal Transitorio (Solo en t=1)":
            st.write("""
            * **Interpretación de la Estática (Gráfico Izquierdo):** El shock positivo mueve la dotación **X₁** horizontalmente a la derecha de **X₀**. La restricción presupuestaria se expande de forma paralela. Como el agente desea suavizar consumo, el óptimo libre busca una isocuanta más alta desplazándose principalmente hacia arriba en el eje futuro. Consume poco hoy y guarda el resto.
            * **Conexión con la Dinámica (Gráfico Derecho):** En la trayectoria temporal, el consumo se mantiene perfectamente estable (plano). El pico transitorio del ingreso en $t=1$ se absorbe por completo mediante un salto en la acumulación de activos financieros ($A_t$).
            """)
        elif tipo_shock == "Permanente (De t=1 en adelante)":
            st.write("""
            * **Interpretación de la Estática (Gráfico Izquierdo):** Al incrementarse el ingreso en todos los períodos, la dotación salta en diagonal hacia arriba y a la derecha (**X₁**). La restricción presupuestaria se desplaza masivamente hacia afuera. El nuevo punto óptimo de tangencia coincide perfectamente sobre la nueva dotación. 
            * **Conexión con la Dinámica (Gráfico Derecho):** Dado que la variación alteró el ingreso permanente en la misma proporción que el ingreso corriente, el consumo da un salto idéntico en $t=1$ y se estabiliza. No hay incentivos para ahorrar ni desahorrar; la senda de activos netos se mantiene inalterada en cero.
            """)
        else:  # Shocks anticipados
            st.write("""
            * **El Rol de las Expectativas Racionales (Previsión Perfecta):** Note que en el período $t=1$, el ingreso físico aún no se ha modificado (el eje X de la dotación no cambia). Sin embargo, como el consumidor anticipa el cambio futuro, la dotación se desplaza verticalmente en el gráfico izquierdo. La restricción presupuestaria se expande por "efecto riqueza" desde hoy. El consumidor libre salta de inmediato a un consumo más alto en el período 1.
            * **La Dinámica frente a Restricciones de Liquidez:** 
              * Si el shock futuro es *positivo* y se activa la restricción de liquidez, la recta de balance sufre un quiebre estricto (kink) vertical en el nivel de ingreso corriente actual. El consumidor no puede endeudarse para adelantar consumo. Verás en el gráfico analítico que queda atrapado en una solución de esquina (**Punto B**) y en la trayectoria el consumo no se moverá hasta que físicamente llegue el período $t=4$.
              * Si el shock futuro es *negativo*, el agente necesita ahorrar de forma preventiva. Dado que el sistema financiero permite resguardar valor sin inconvenientes, el consumidor restringido replica con total exactitud al consumidor libre, contrayendo su nivel de consumo desde el período 1.
            """)
