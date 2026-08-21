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

    .stApp, [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; color: #000000 !important; }
    section[data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 2px solid #CBD5E1 !important; }
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #000000 !important; }

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
    st.markdown("""*Desarrollado para la cátedra de Macroeconomía II. Este entorno interactivo permite analizar la microfundamentación del consumo, la descomposición de efectos y la dinámica temporal bajo la Teoría del Ingreso Permanente.*""")

    st.sidebar.header("🛠️ Configuración General")
    modelo_seleccionado = st.sidebar.radio(
        "Seleccione el enfoque analítico:",
        [
            "1. Modelo de 2 Períodos (Tasa de Interés y Efecto Hicks)", 
            "2. Modelo de 2 Períodos (Shocks de Ingreso: Transitorio vs Permanente)",
            "3. Dinámica de Largo Plazo (10 Períodos y Restricciones de Liquidez)"
        ]
    )

    # Configuración base para todos los gráficos (Alto Contraste)
    eje_formato = dict(
        showline=True, 
        linecolor='black', 
        linewidth=2, 
        gridcolor='#9CA3AF', 
        tickfont=dict(color='black', size=13),
        titlefont=dict(color='black', size=14, family="Arial")
    )
    fuente_gral = dict(color='black', family="Arial")

    # =============================================================================
    # MÓDULO 1: DOS PERÍODOS CON DESCOMPOSICIÓN DE HICKS (Tasa de Interés)
    # =============================================================================
    if modelo_seleccionado == "1. Modelo de 2 Períodos (Tasa de Interés y Efecto Hicks)":
        
        modo_uso_m1 = st.sidebar.radio("Modo de Interacción:", ["📚 Escenarios Predefinidos (Recomendado)", "🎛️ Modo Manual (Deslizadores)"])

        if modo_uso_m1 == "🎛️ Modo Manual (Deslizadores)":
            st.sidebar.subheader("🎛️ Parámetros del Modelo")
            y1 = st.sidebar.slider("Ingreso Período 1 (Y₁)", 10.0, 100.0, 50.0, 5.0)
            y2 = st.sidebar.slider("Ingreso Período 2 (Y₂)", 10.0, 100.0, 55.0, 5.0)
            beta = st.sidebar.slider("Factor de Descuento (β)", 0.5, 1.5, 1.0, 0.05)
            
            st.sidebar.subheader("⚡ Shock de Tasa de Interés")
            i_inicial = st.sidebar.slider("Tasa de Interés Inicial (i₀)", 0.0, 1.0, 0.10, 0.05, format="%.2f")
            i_final = st.sidebar.slider("Tasa de Interés Post-Shock (i₁)", 0.0, 1.0, 0.10, 0.05, format="%.2f")
            
        else:
            st.sidebar.subheader("📚 Selección de Escenario")
            
            familia_predef = st.sidebar.selectbox("1. Tipo de Familia Inicial:", 
                ["Equilibrada (Y₁ ≈ C₁)", "Ahorrante (Y₁ > C₁)", "Deudora (Y₁ < C₁)"])
            
            shock_predef = st.sidebar.selectbox("2. Variación de Tasa de Interés:", 
                ["Situación Inicial (Sin Variación)", "Suba de Tasa de Interés", "Baja de Tasa de Interés"])
            
            beta = 1.0
            if familia_predef == "Equilibrada (Y₁ ≈ C₁)":
                y1, y2 = 50.0, 55.0
            elif familia_predef == "Ahorrante (Y₁ > C₁)":
                y1, y2 = 80.0, 20.0
            else: 
                y1, y2 = 20.0, 80.0
                
            if shock_predef == "Situación Inicial (Sin Variación)":
                i_inicial, i_final = 0.10, 0.10
            elif shock_predef == "Suba de Tasa de Interés":
                i_inicial, i_final = 0.10, 1.00
            else: 
                i_inicial, i_final = 0.50, 0.05

        st.sidebar.subheader("🔍 Visualización")
        zoom_activado = st.sidebar.checkbox("Activar Lupa (Enfocar en la zona de equilibrio)")

        omega_inicial = y1 + y2 / (1 + i_inicial)
        omega_final = y1 + y2 / (1 + i_final)
        
        c1_inicial = omega_inicial / (1 + beta)
        c2_inicial = (beta * (1 + i_inicial) * omega_inicial) / (1 + beta)
        u_inicial = np.log(c1_inicial) + beta * np.log(c2_inicial)
        
        c1_final = omega_final / (1 + beta)
        c2_final = (beta * (1 + i_final) * omega_final) / (1 + beta)
        u_final = np.log(c1_final) + beta * np.log(c2_final)
        
        c1_hicks = np.exp((u_inicial - beta * np.log(beta * (1 + i_final))) / (1 + beta))
        c2_hicks = beta * (1 + i_final) * c1_hicks
        omega_hicks = c1_hicks + c2_hicks / (1 + i_final)

        efecto_sustitucion = c1_hicks - c1_inicial
        efecto_ingreso = c1_final - c1_hicks
        efecto_total = c1_final - c1_inicial
        
        tipo_hogar = "Equilibrado" if abs(y1 - c1_inicial) < 0.01 else ("Ahorrante" if y1 > c1_inicial else "Deudor")
        hay_shock_m1 = (i_inicial != i_final)

        st.subheader("📊 Módulo 1: Análisis Geométrico (Descomposición de Efectos)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Espacio de Asignación Intertemporal**")
            max_omega_x = max(omega_inicial, omega_final, omega_hicks)
            max_omega_y = max(omega_inicial * (1+i_inicial), omega_final * (1+i_final), omega_hicks * (1+i_final))
            
            if zoom_activado:
                min_x = min(c1_inicial, c1_final, c1_hicks, y1) * 0.85
                max_x = max(c1_inicial, c1_final, c1_hicks, y1) * 1.15
                min_y = min(c2_inicial, c2_final, c2_hicks, y2) * 0.85
                max_y = max(c2_inicial, c2_final, c2_hicks, y2) * 1.15
                rango_x, rango_y = [min_x, max_x], [min_y, max_y]
            else:
                rango_x, rango_y = [0, max_omega_x * 1.1], [0, max_omega_y * 1.1]
            
            c1_vec = np.linspace(0.1, max_omega_x * 1.2, 300)
            fig_static = go.Figure()
            
            fig_static.add_trace(go.Scatter(x=c1_vec, y=np.where(c1_vec <= max_omega_y*1.5, c1_vec, np.nan), name="Senda Suavización (45°)", line=dict(color='darkgray', width=1.5, dash='dot')))

            if hay_shock_m1:
                fig_static.add_trace(go.Scatter(x=c1_vec, y=(omega_inicial - c1_vec) * (1 + i_inicial), name="RP Inicial (i₀)", line=dict(color='black', width=2, dash='dash')))
                fig_static.add_trace(go.Scatter(x=c1_vec, y=(omega_hicks - c1_vec) * (1 + i_final), name="RP Hicks (Teórica)", line=dict(color='orange', width=2, dash='dot')))
            
            fig_static.add_trace(go.Scatter(x=c1_vec, y=(omega_final - c1_vec) * (1 + i_final), name="RP Final (i₁)" if hay_shock_m1 else "Restricción Presupuestaria", line=dict(color='blue', width=2.5, dash='dash')))
            
            u0_y = np.exp((u_inicial - np.log(c1_vec)) / beta)
            fig_static.add_trace(go.Scatter(x=c1_vec, y=np.where(u0_y <= max_omega_y*1.5, u0_y, np.nan), name="U₀ (Bienestar Inicial)", line=dict(color='green', width=2)))
            
            if hay_shock_m1:
                u1_y = np.exp((u_final - np.log(c1_vec)) / beta)
                fig_static.add_trace(go.Scatter(x=c1_vec, y=np.where(u1_y <= max_omega_y*1.5, u1_y, np.nan), name="U₁ (Bienestar Final)", line=dict(color='blue', width=2)))
            
            fig_static.add_trace(go.Scatter(x=[y1], y=[y2], mode='markers+text', text=['Dotación (Y)'], textposition='bottom right', marker=dict(color='black', symbol='x', size=10), name="Dotación"))
            if hay_shock_m1:
                fig_static.add_trace(go.Scatter(x=[c1_inicial], y=[c2_inicial], mode='markers+text', text=['A (Inicial)'], textposition='top right', marker=dict(color='green', size=10), showlegend=False))
                fig_static.add_trace(go.Scatter(x=[c1_hicks], y=[c2_hicks], mode='markers+text', text=['C (Hicks)'], textposition='bottom left', marker=dict(color='orange', size=8), showlegend=False))
            fig_static.add_trace(go.Scatter(x=[c1_final], y=[c2_final], mode='markers+text', text=['B (Final)'] if hay_shock_m1 else ['A (Óptimo)'], textposition='top right', marker=dict(color='blue', size=10), showlegend=False))

            fig_static.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=fuente_gral,
                xaxis_title="Consumo Presente (C₁)", yaxis_title="Consumo Futuro (C₂)", 
                xaxis=dict(**eje_formato, range=rango_x), yaxis=dict(**eje_formato, range=rango_y), 
                legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.9)"), 
                margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_static, use_container_width=True)

        with col2:
            st.write("**Evolución Temporal del Consumo y el Ingreso**")
            fig_dynamic = go.Figure()
            fig_dynamic.add_trace(go.Scatter(x=['Período 1', 'Período 2'], y=[y1, y2], name="Ingreso Disponible (Y)", line=dict(color='black', width=3), marker=dict(size=8)))
            if hay_shock_m1: fig_dynamic.add_trace(go.Scatter(x=['Período 1', 'Período 2'], y=[c1_inicial, c2_inicial], name="Consumo Inicial", line=dict(color='green', width=2, dash='dash'), marker=dict(size=6)))
            fig_dynamic.add_trace(go.Scatter(x=['Período 1', 'Período 2'], y=[c1_final, c2_final], name="Consumo Final", line=dict(color='blue', width=3), marker=dict(size=8)))
            
            fig_dynamic.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=fuente_gral,
                yaxis_title="Unidades de Producción/Consumo", 
                yaxis=dict(**eje_formato, range=[0, max(y1, y2, c2_inicial, c2_final)*1.15]), 
                xaxis=dict(**eje_formato), 
                legend=dict(yanchor="bottom", y=0.01, xanchor="left", x=0.01), margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_dynamic, use_container_width=True)

        metrics = st.columns(4)
        metrics[0].metric(label="Perfil de Familia", value=tipo_hogar)
        metrics[1].metric(label="Efecto Sustitución (ES)", value=f"{efecto_sustitucion:.2f}")
        metrics[2].metric(label="Efecto Ingreso (EI)", value=f"{efecto_ingreso:.2f}")
        metrics[3].metric(label="Efecto Total (ET)", value=f"{efecto_total:.2f}")

        st.info(f"**Análisis de Sachs & Larraín:** Al modificarse la tasa de interés, el consumo futuro cambia su precio relativo, generando un **Efecto Sustitución** de **{efecto_sustitucion:.2f}** unidades. Al ser de perfil **{tipo_hogar}**, el **Efecto Ingreso** provocado por el cambio en su riqueza intertemporal es de **{efecto_ingreso:.2f}**.")


    # =============================================================================
    # MÓDULO 2: SHOCKS DE INGRESO EN 2 PERÍODOS (Todas las posibilidades)
    # =============================================================================
    elif modelo_seleccionado == "2. Modelo de 2 Períodos (Shocks de Ingreso: Transitorio vs Permanente)":
        
        modo_uso_m2 = st.sidebar.radio("Modo de Interacción:", ["📚 Escenarios Predefinidos (Recomendado)", "🎛️ Modo Manual (Deslizadores)"])
        
        if modo_uso_m2 == "🎛️ Modo Manual (Deslizadores)":
            st.sidebar.subheader("🎛️ Ingreso Base")
            y1_base = st.sidebar.slider("Ingreso Base Período 1", 10.0, 100.0, 50.0, 5.0)
            y2_base = st.sidebar.slider("Ingreso Base Período 2", 10.0, 100.0, 50.0, 5.0)
            
            st.sidebar.subheader("⚡ Shocks de Ingreso")
            dy1 = st.sidebar.slider("Shock en Período 1 (ΔY₁)", -40.0, 50.0, 0.0, 5.0)
            dy2 = st.sidebar.slider("Shock en Período 2 (ΔY₂)", -40.0, 50.0, 0.0, 5.0)
            
            i_rate = 0.10
            beta = 1 / (1 + i_rate)
        else:
            st.sidebar.subheader("📚 Selección de Escenario")
            escenario_shock = st.sidebar.selectbox("Naturaleza del Shock de Ingreso:", [
                "Situación Inicial (Ingreso Estable)",
                "A. Shock Transitorio Positivo (Sube solo Y₁)",
                "B. Shock Transitorio Negativo (Baja solo Y₁)",
                "C. Shock Permanente Positivo (Sube Y₁ y Y₂)",
                "D. Shock Permanente Negativo (Baja Y₁ y Y₂)",
                "E. Shock Futuro Anticipado Positivo (Sube solo Y₂)",
                "F. Shock Futuro Anticipado Negativo (Baja solo Y₂)"
            ])
            
            y1_base, y2_base = 50.0, 50.0
            i_rate = 0.10
            beta = 1 / (1 + i_rate)
            
            if escenario_shock == "Situación Inicial (Ingreso Estable)":
                dy1, dy2 = 0.0, 0.0
            elif escenario_shock == "A. Shock Transitorio Positivo (Sube solo Y₁)":
                dy1, dy2 = 40.0, 0.0
            elif escenario_shock == "B. Shock Transitorio Negativo (Baja solo Y₁)":
                dy1, dy2 = -30.0, 0.0
            elif escenario_shock == "C. Shock Permanente Positivo (Sube Y₁ y Y₂)":
                dy1, dy2 = 40.0, 40.0
            elif escenario_shock == "D. Shock Permanente Negativo (Baja Y₁ y Y₂)":
                dy1, dy2 = -30.0, -30.0
            elif escenario_shock == "E. Shock Futuro Anticipado Positivo (Sube solo Y₂)":
                dy1, dy2 = 0.0, 40.0
            else: # F. Futuro Negativo
                dy1, dy2 = 0.0, -30.0

        st.sidebar.subheader("🔍 Visualización")
        zoom_activado_m2 = st.sidebar.checkbox("Activar Lupa (Enfocar en la zona de equilibrio)")

        y1_final = y1_base + dy1
        y2_final = y2_base + dy2
        
        omega_0 = y1_base + y2_base / (1 + i_rate)
        omega_1 = y1_final + y2_final / (1 + i_rate)
        
        c1_0 = omega_0 / (1 + beta)
        c2_0 = (beta * (1 + i_rate) * omega_0) / (1 + beta)
        u_0 = np.log(c1_0) + beta * np.log(c2_0)
        
        c1_1 = omega_1 / (1 + beta)
        c2_1 = (beta * (1 + i_rate) * omega_1) / (1 + beta)
        u_1 = np.log(c1_1) + beta * np.log(c2_1)
        
        delta_c1 = c1_1 - c1_0
        delta_y1 = dy1
        
        if delta_y1 != 0: pmc = delta_c1 / delta_y1
        else: pmc = 0.0

        hay_shock_m2 = (dy1 != 0 or dy2 != 0)

        st.subheader("📊 Módulo 2: Geometría de la Teoría del Ingreso Permanente (2 Períodos)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Espacio Intertemporal: Shocks y Suavización**")
            max_om_x = max(omega_0, omega_1)
            max_om_y = max(omega_0 * (1+i_rate), omega_1 * (1+i_rate))
            
            if zoom_activado_m2:
                min_x = min(c1_0, c1_1, y1_base, y1_final) * 0.85
                max_x = max(c1_0, c1_1, y1_base, y1_final) * 1.15
                min_y = min(c2_0, c2_1, y2_base, y2_final) * 0.85
                max_y = max(c2_0, c2_1, y2_base, y2_final) * 1.15
                r_x, r_y = [min_x, max_x], [min_y, max_y]
            else:
                r_x, r_y = [0, max_om_x * 1.1], [0, max_om_y * 1.1]
                
            c1_v = np.linspace(0.1, max_om_x * 1.2, 300)
            fig_m2 = go.Figure()
            
            fig_m2.add_trace(go.Scatter(x=c1_v, y=c1_v, name="Senda 45°", line=dict(color='darkgray', width=1.5, dash='dot')))
            
            if hay_shock_m2:
                fig_m2.add_trace(go.Scatter(x=c1_v, y=(omega_0 - c1_v)*(1+i_rate), name="RP₀ (Inicial)", line=dict(color='black', width=2, dash='dash')))
                fig_m2.add_trace(go.Scatter(x=[y1_base], y=[y2_base], mode='markers+text', text=['X₀ (Inicial)'], textposition='bottom left', marker=dict(color='black', symbol='square', size=8), name="Dotación X₀"))
            
            fig_m2.add_trace(go.Scatter(x=c1_v, y=(omega_1 - c1_v)*(1+i_rate), name="RP₁ (Post-Shock)" if hay_shock_m2 else "Restricción Presupuestaria", line=dict(color='blue', width=2.5, dash='dash')))
            
            u0_y = np.exp((u_0 - np.log(c1_v)) / beta)
            fig_m2.add_trace(go.Scatter(x=c1_v, y=np.where(u0_y <= max_om_y*1.5, u0_y, np.nan), name="U₀", line=dict(color='green', width=2)))
            
            if hay_shock_m2:
                u1_y = np.exp((u_1 - np.log(c1_v)) / beta)
                fig_m2.add_trace(go.Scatter(x=c1_v, y=np.where(u1_y <= max_om_y*1.5, u1_y, np.nan), name="U₁", line=dict(color='blue', width=2)))
                
            fig_m2.add_trace(go.Scatter(x=[y1_final], y=[y2_final], mode='markers+text', text=['X₁ (Final)'] if hay_shock_m2 else ['X₀ (Dotación)'], textposition='top right', marker=dict(color='purple', symbol='x', size=10), name="Dotación X₁"))
            
            if hay_shock_m2: fig_m2.add_trace(go.Scatter(x=[c1_0], y=[c2_0], mode='markers+text', text=['A (Inicial)'], textposition='top left', marker=dict(color='green', size=10), showlegend=False))
            fig_m2.add_trace(go.Scatter(x=[c1_1], y=[c2_1], mode='markers+text', text=['B (Final)'] if hay_shock_m2 else ['A (Óptimo)'], textposition='top left', marker=dict(color='blue', size=10), showlegend=False))

            fig_m2.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=fuente_gral,
                xaxis_title="Consumo Presente (C₁)", yaxis_title="Consumo Futuro (C₂)", 
                xaxis=dict(**eje_formato, range=r_x), yaxis=dict(**eje_formato, range=r_y), 
                legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.9)"), margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_m2, use_container_width=True)

        with col2:
            st.write("**Evolución Dinámica: Ingreso vs Consumo**")
            fig_d2 = go.Figure()
            fig_d2.add_trace(go.Scatter(x=['Período 1', 'Período 2'], y=[y1_base, y2_base], name="Y Inicial", line=dict(color='black', width=2, dash='dash'), marker=dict(size=6)))
            if hay_shock_m2: fig_d2.add_trace(go.Scatter(x=['Período 1', 'Período 2'], y=[y1_final, y2_final], name="Y Post-Shock", line=dict(color='purple', width=3), marker=dict(size=8, symbol='x')))
            fig_d2.add_trace(go.Scatter(x=['Período 1', 'Período 2'], y=[c1_1, c2_1], name="Consumo Óptimo (C*)", line=dict(color='blue', width=3), marker=dict(size=8)))
            
            min_y_axis = min(y1_final, y2_final, c2_1, 0)
            max_y_axis = max(y1_final, y2_final, c2_1, y1_base) * 1.15
            
            fig_d2.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=fuente_gral,
                yaxis_title="Unidades", yaxis=dict(**eje_formato, range=[min_y_axis, max_y_axis]), 
                xaxis=dict(**eje_formato), 
                legend=dict(yanchor="bottom", y=0.01, xanchor="left", x=0.01), margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_d2, use_container_width=True)

        metrics = st.columns(4)
        metrics[0].metric(label="Variación Ingreso (ΔY₁)", value=f"{delta_y1:.2f}")
        metrics[1].metric(label="Variación Consumo (ΔC₁)", value=f"{delta_c1:.2f}")
        metrics[2].metric(label="Propensión Marginal (PMgC)", value=f"{pmc:.2f}")
        metrics[3].metric(label="Nuevo Ahorro (S₁)", value=f"{(y1_final - c1_1):.2f}")

        # TEXTO PEDAGÓGICO DINÁMICO EXHAUSTIVO
        explicacion_m2 = "### 🎓 Teoría del Ingreso Permanente (Milton Friedman)\n"
        if not hay_shock_m2:
            explicacion_m2 += "El agente se encuentra en su **Situación Inicial**. Dado que prefiere suavizar su consumo y no hay alteraciones en su ingreso futuro, su nivel de consumo y ahorro se mantienen estables de acuerdo a sus preferencias intertemporales."
        elif dy1 > 0 and dy2 == 0:
            explicacion_m2 += f"**Shock Transitorio Positivo:** El ingreso aumentó sorpresivamente hoy en {dy1:.1f} unidades. La dotación se mueve en horizontal hacia la derecha. Como el agente desea suavizar su nivel de vida, ahorra gran parte de este ingreso extra para el futuro. Notá que la **Propensión Marginal a Consumir (PMgC)** del período 1 es baja ({pmc:.2f})."
        elif dy1 < 0 and dy2 == 0:
            explicacion_m2 += f"**Shock Transitorio Negativo:** El ingreso cayó hoy de forma imprevista en {abs(dy1):.1f} unidades (ej. gasto médico o pérdida laboral temporal). La dotación retrocede en horizontal. Para no sacrificar drásticamente su nivel de vida actual, el agente **desahorra o se endeuda**. Su PMgC es baja ({pmc:.2f}) para amortiguar el impacto sobre el consumo."
        elif dy1 > 0 and dy2 > 0:
            explicacion_m2 += f"**Shock Permanente Positivo:** El agente sabe que es más rico hoy y mañana (la dotación salta en diagonal ascendente). Por lo tanto, no hay incentivos para ahorrar preventivamente; ajusta su consumo actual de manera casi proporcional al shock. La **PMgC** es alta, cercana a la unidad ({pmc:.2f})."
        elif dy1 < 0 and dy2 < 0:
            explicacion_m2 += f"**Shock Permanente Negativo:** El agente sufre un recorte definitivo de sus ingresos (ej. mayor presión impositiva permanente). La dotación cae en diagonal descendente. Como sabe que mañana tampoco recuperará su poder adquisitivo, ajusta su consumo hacia abajo **hoy mismo** de forma drástica. La PMgC es muy alta ({pmc:.2f})."
        elif dy1 == 0 and dy2 > 0:
            explicacion_m2 += "**Shock Futuro Anticipado Positivo:** El agente sabe que *mañana* recibirá más ingresos (ej. herencia o ascenso). La dotación sube verticalmente. Por 'efecto riqueza', la restricción presupuestaria se expande desde hoy. Como el agente quiere disfrutar parte de esa riqueza ya mismo, **incrementa su consumo hoy** reduciendo su ahorro (o tomando deuda)."
        elif dy1 == 0 and dy2 < 0:
            explicacion_m2 += "**Shock Futuro Anticipado Negativo:** El agente anticipa que *mañana* será más pobre (ej. jubilación o despido anunciado). La dotación cae verticalmente. Para evitar un colapso del consumo en el futuro, el agente aplica el **ahorro preventivo**: reduce su consumo hoy mismo para guardar fondos que amortigüen la caída futura."

        st.success(explicacion_m2)


    # =============================================================================
    # MÓDULO 3: DINÁMICA DE LARGO PLAZO (10 PERÍODOS Y LIQUIDEZ)
    # =============================================================================
    elif modelo_seleccionado == "3. Dinámica de Largo Plazo (10 Períodos y Restricciones de Liquidez)":
        
        modo_uso_m3 = st.sidebar.radio("Modo de Interacción:", ["📚 Escenarios Predefinidos (Recomendado)", "🎛️ Modo Manual (Deslizadores)"])

        if modo_uso_m3 == "🎛️ Modo Manual (Deslizadores)":
            st.sidebar.subheader("🎛️ Parámetros Estacionarios")
            y_ee = st.sidebar.slider("Ingreso Base Estacionario (Y₀)", 10.0, 100.0, 50.0, 5.0)
            r = st.sidebar.slider("Tasa de Interés Real (r)", 0.01, 0.20, 0.05, 0.01, format="%.2f")
            
            st.sidebar.subheader("⚡ Tipología de Shocks en t=1")
            tipo_shock = st.sidebar.selectbox("Naturaleza del shock de ingreso:",
                ["Temporal Transitorio (Solo en t=1)", "Permanente (De t=1 en adelante)", 
                 "Futuro Anticipado Positivo (Anuncio en t=1, ocurre en t=4)", "Futuro Anticipado Negativo (Anuncio en t=1, ocurre en t=4)"])
            magnitud_shock = st.sidebar.slider("Magnitud del Shock (ΔY)", -30.0, 30.0, 0.0, 5.0)
            restriccion_liquidez = st.sidebar.checkbox("Activar Restricción de Liquidez Estricta (No Endeudamiento)")
            
        else: 
            st.sidebar.subheader("📚 Selección de Escenario")
            escenario_shock = st.sidebar.selectbox("1. Escenario Macroeconómico:", [
                "Situación Inicial (Sin Shock)",
                "A. Transitorio Positivo (Ej. Bono extra hoy)",
                "B. Transitorio Negativo (Ej. Multa o reparación imprevista hoy)",
                "C. Permanente Positivo (Ej. Ascenso laboral hoy)",
                "D. Permanente Negativo (Ej. Recorte salarial permanente hoy)",
                "E. Anticipado Positivo (Ej. Anuncio de herencia para el año 4)",
                "F. Anticipado Negativo (Ej. Anuncio de despido para el año 4)"
            ])
            restriccion_liquidez = st.sidebar.checkbox("Activar Restricción de Liquidez (Impacta en Shocks Anticipados)")
            
            y_ee = 50.0
            r = 0.05
            
            if escenario_shock == "Situación Inicial (Sin Shock)":
                tipo_shock, magnitud_shock = "Temporal Transitorio (Solo en t=1)", 0.0
            elif escenario_shock == "A. Transitorio Positivo (Ej. Bono extra hoy)":
                tipo_shock, magnitud_shock = "Temporal Transitorio (Solo en t=1)", 30.0
            elif escenario_shock == "B. Transitorio Negativo (Ej. Multa o reparación imprevista hoy)":
                tipo_shock, magnitud_shock = "Temporal Transitorio (Solo en t=1)", -25.0
            elif escenario_shock == "C. Permanente Positivo (Ej. Ascenso laboral hoy)":
                tipo_shock, magnitud_shock = "Permanente (De t=1 en adelante)", 20.0
            elif escenario_shock == "D. Permanente Negativo (Ej. Recorte salarial permanente hoy)":
                tipo_shock, magnitud_shock = "Permanente (De t=1 en adelante)", -20.0
            elif escenario_shock == "E. Anticipado Positivo (Ej. Anuncio de herencia para el año 4)":
                tipo_shock, magnitud_shock = "Futuro Anticipado Positivo (Anuncio en t=1, ocurre en t=4)", 30.0
            elif escenario_shock == "F. Anticipado Negativo (Ej. Anuncio de despido para el año 4)":
                tipo_shock, magnitud_shock = "Futuro Anticipado Negativo (Anuncio en t=1, ocurre en t=4)", -20.0

        st.sidebar.subheader("🔍 Visualización")
        zoom_activado_m3 = st.sidebar.checkbox("Activar Lupa (Enfocar en la zona de equilibrio)")

        horizonte_t = 10
        t_vec = np.arange(0, horizonte_t + 1)
        y_trayectoria = np.full(horizonte_t + 1, y_ee, dtype=float)
        
        if tipo_shock == "Temporal Transitorio (Solo en t=1)":
            y_trayectoria[1] = y_ee + magnitud_shock
        elif tipo_shock == "Permanente (De t=1 en adelante)":
            y_trayectoria[1:] = y_ee + magnitud_shock
        elif tipo_shock in ["Futuro Anticipado Positivo (Anuncio en t=1, ocurre en t=4)", "Futuro Anticipado Negativo (Anuncio en t=1, ocurre en t=4)"]:
            y_trayectoria[4:] = y_ee + magnitud_shock

        gamma_futuro = sum(1 / ((1 + r) ** (t - 1)) for t in range(2, horizonte_t + 1))

        # SIMULACIÓN 1: LIBRE
        c_libre = np.zeros(horizonte_t + 1)
        a_libre = np.zeros(horizonte_t + 1)
        c_libre[0] = y_ee
        
        vpi_1 = sum(y_trayectoria[t] / ((1 + r) ** (t - 1)) for t in range(1, horizonte_t + 1))
        factor_anualidad = sum(1 / ((1 + r) ** (t - 1)) for t in range(1, horizonte_t + 1))
        c_p_optimo = vpi_1 / factor_anualidad
        
        for t in range(1, horizonte_t + 1):
            c_libre[t] = c_p_optimo
            a_libre[t] = a_libre[t-1] * (1 + r) + y_trayectoria[t] - c_libre[t]

        # SIMULACIÓN 2: RESTRINGIDO
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

        # ESPACIO 2D
        y1_inicial, y_fut_inicial = y_ee, y_ee * gamma_futuro
        y1_final = y_trayectoria[1]
        y_fut_final = sum(y_trayectoria[t] / ((1 + r) ** (t - 1)) for t in range(2, horizonte_t + 1))
        
        omega_2d_inicial = y1_inicial + y_fut_inicial
        omega_2d_final = y1_final + y_fut_final
        
        c1_inicial_plot, cfut_inicial_plot = y_ee, y_ee * gamma_futuro
        c1_libre_plot, cfut_libre_plot = c_libre[1], c_libre[1] * gamma_futuro
        c1_restric_plot, cfut_restric_plot = c_restric[1], sum(c_restric[t] / ((1 + r) ** (t - 1)) for t in range(2, horizonte_t + 1))

        hay_shock_m3 = (magnitud_shock != 0.0)

        st.subheader(f"📊 Módulo 3: Dinámica de Largo Plazo y Restricción de Liquidez")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.write("**Desplazamiento Analítico de Rectas e Isocuantas (t=1)**")
            max_omega_2d = max(omega_2d_inicial, omega_2d_final)
            
            if zoom_activado_m3:
                min_x2 = min(c1_inicial_plot, c1_libre_plot, c1_restric_plot, y1_inicial, y1_final) * 0.85
                max_x2 = max(c1_inicial_plot, c1_libre_plot, c1_restric_plot, y1_inicial, y1_final) * 1.15
                min_y2 = min(cfut_inicial_plot, cfut_libre_plot, cfut_restric_plot, y_fut_inicial, y_fut_final) * 0.85
                max_y2 = max(cfut_inicial_plot, cfut_libre_plot, cfut_restric_plot, y_fut_inicial, y_fut_final) * 1.15
                rango_x2, rango_y2 = [min_x2, max_x2], [min_y2, max_y2]
            else:
                rango_x2, rango_y2 = [0, max_omega_2d * 1.1], [0, max_omega_2d * 1.1]
            
            c1_grid = np.linspace(0.1, max_omega_2d * 1.2, 300)
            fig_macro_static = go.Figure()
            
            if hay_shock_m3:
                fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=omega_2d_inicial - c1_grid, name="RP Inicial (Estado Est.)", line=dict(color='black', width=2, dash='dash')))
            
            if restriccion_liquidez:
                grid_restric = np.where(c1_grid <= y1_final, omega_2d_final - c1_grid, np.nan)
                fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=grid_restric, name="RP Final (Con Restricción)", line=dict(color='crimson', width=3, dash='dash')))
                fig_macro_static.add_vline(x=y1_final, line_dash="dot", line_color="crimson", annotation_text="Límite Crédito (Y₁)")
            else:
                fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=omega_2d_final - c1_grid, name="RP Post-Shock (Libre)" if hay_shock_m3 else "Restricción Presupuestaria", line=dict(color='blue', width=2.5, dash='dash')))

            u_init_2d = np.log(c1_inicial_plot) + gamma_futuro * np.log(cfut_inicial_plot / gamma_futuro)
            indif_init_2d = gamma_futuro * np.exp((u_init_2d - np.log(c1_grid)) / gamma_futuro)
            fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=np.where(indif_init_2d <= max_omega_2d*1.5, indif_init_2d, np.nan), name="U₀ (EE Inicial)", line=dict(color='green', width=2)))
            
            if hay_shock_m3:
                u_libre_2d = np.log(c1_libre_plot) + gamma_futuro * np.log(cfut_libre_plot / gamma_futuro)
                indif_libre_2d = gamma_futuro * np.exp((u_libre_2d - np.log(c1_grid)) / gamma_futuro)
                fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=np.where(indif_libre_2d <= max_omega_2d*1.5, indif_libre_2d, np.nan), name="U₁ (Post-Shock Libre)", line=dict(color='blue', width=2)))

            if hay_shock_m3: fig_macro_static.add_trace(go.Scatter(x=[y1_inicial], y=[y_fut_inicial], mode='markers+text', text=['X₀ (Dotación EE)'], textposition='bottom left', marker=dict(color='black', symbol='square', size=8), name="Dotación Inicial"))
            fig_macro_static.add_trace(go.Scatter(x=[y1_final], y=[y_fut_final], mode='markers+text', text=['X₁ (Dotación Shock)'] if hay_shock_m3 else ['X₀ (Dotación)'], textposition='top right', marker=dict(color='purple', symbol='x', size=10), name="Dotación Post-Shock"))
            fig_macro_static.add_trace(go.Scatter(x=[c1_libre_plot], y=[cfut_libre_plot], mode='markers+text', text=['A óptimo (Libre)'], textposition='top left', marker=dict(color='blue', size=10), showlegend=False))
            
            if restriccion_liquidez: fig_macro_static.add_trace(go.Scatter(x=[c1_restric_plot], y=[cfut_restric_plot], mode='markers+text', text=['B óptimo (Restringido)'], textposition='bottom right', marker=dict(color='crimson', size=10), showlegend=False))
            fig_macro_static.add_trace(go.Scatter(x=c1_grid, y=c1_grid * gamma_futuro, name="Senda de Suavización Plena", line=dict(color='darkgray', dash='dot', width=1.5)))

            fig_macro_static.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=fuente_gral,
                xaxis_title="Consumo Presente Actual (C₁)", yaxis_title="VP del Consumo Futuro Acumulado", 
                xaxis=dict(**eje_formato, range=rango_x2), yaxis=dict(**eje_formato, range=rango_y2), 
                legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.9)"), margin=dict(l=20, r=20, t=20, b=20), height=450
            )
            st.plotly_chart(fig_macro_static, use_container_width=True)

        with col_g2:
            st.write("**Senda Temporal de Transición Dinámica ($t=0$ a $t=10$)**")
            fig_lineas = go.Figure()
            fig_lineas.add_trace(go.Scatter(x=t_vec, y=y_trayectoria, name="Ingreso Disponible (Yₜ)", line=dict(color='black', width=3, shape='hv')))
            fig_lineas.add_trace(go.Scatter(x=t_vec, y=c_libre, name="Consumo Permanente (Libre)", line=dict(color='blue', width=2.5, dash='dash')))
            if restriccion_liquidez: fig_lineas.add_trace(go.Scatter(x=t_vec, y=c_restric, name="Consumo Efectivo (Con Restricción)", line=dict(color='crimson', width=3)))
            fig_lineas.add_hline(y=y_ee, line_dash="dot", line_color="gray", annotation_text="EE Base (t=0)", annotation_position="bottom left")
            
            fig_lineas.update_layout(
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=fuente_gral,
                xaxis=dict(**eje_formato, tickmode='linear', tick0=0, dtick=1, title="Períodos Temporales (t)"), 
                yaxis=dict(**eje_formato, title="Escala Monetaria"), margin=dict(l=20, r=20, t=20, b=20), height=450, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.9)")
            )
            st.plotly_chart(fig_lineas, use_container_width=True)

        st.subheader("🏦 Senda de Acumulación / Desacumulación de Activos Netos ($A_t$)")
        fig_assets = go.Figure()
        fig_assets.add_trace(go.Scatter(x=t_vec, y=a_libre, name="Activos Sin Restricción", line=dict(color='blue', dash='dash')))
        if restriccion_liquidez: fig_assets.add_trace(go.Scatter(x=t_vec, y=a_restric, name="Activos Con Restricción", line=dict(color='crimson', width=2.5)))
        fig_assets.add_hline(y=0.0, line_color="black", line_width=1)
        
        fig_assets.update_layout(
            template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=fuente_gral,
            xaxis=dict(**eje_formato, tickmode='linear', tick0=0, dtick=1, title="Períodos Temporales (t)"), 
            yaxis=dict(**eje_formato, title="Stock de Activos Netos"), margin=dict(l=20, r=20, t=20, b=20), height=250, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.9)")
        )
        st.plotly_chart(fig_assets, use_container_width=True)

        # TEXTO PEDAGÓGICO DINÁMICO
        explicacion_m3 = "### 🎓 Dinámica de Largo Plazo y Expectativas\n"
        if not hay_shock_m3:
            explicacion_m3 += "El consumidor se encuentra en la **senda estacionaria de largo plazo**, consumiendo su Ingreso Permanente."
        elif tipo_shock == "Temporal Transitorio (Solo en t=1)" and magnitud_shock > 0:
            explicacion_m3 += "* **Shock Transitorio Positivo:** El pico de ingreso en t=1 se absorbe distribuyendo el consumo extra a lo largo de los 10 períodos. El agente da un salto positivo en su acumulación de activos financieros ($A_t$) en t=1 (ahorro transitorio) y luego los va desacumulando lentamente para financiar el mayor nivel de consumo futuro."
        elif tipo_shock == "Temporal Transitorio (Solo en t=1)" and magnitud_shock < 0:
            explicacion_m3 += "* **Shock Transitorio Negativo:** El bache de ingresos en t=1 obliga al consumidor a financiarse (o desahorrar). El stock de activos financieros ($A_t$) cae por debajo de cero inicialmente, y el agente dedica los ingresos normales de los años siguientes a pagar esa deuda, manteniendo su consumo suavizado."
        elif tipo_shock == "Permanente (De t=1 en adelante)" and magnitud_shock > 0:
            explicacion_m3 += "* **Shock Permanente Positivo:** El ingreso permanente subió exactamente en la misma magnitud que el corriente. El consumo da un salto en t=1 y se mantiene plano en el nuevo nivel. Como el nuevo flujo de ingresos es capaz de sostener el nuevo consumo por sí solo, la senda de activos netos no se altera."
        elif tipo_shock == "Permanente (De t=1 en adelante)" and magnitud_shock < 0:
            explicacion_m3 += "* **Shock Permanente Negativo:** El consumidor entiende que su empobrecimiento es definitivo. Ajusta drásticamente hacia abajo su senda de consumo permanente desde t=1. Dado que asume su nueva realidad, no necesita tomar deuda ni acumular activos; la senda de $A_t$ permanece en equilibrio nulo."
        else: # Anticipados
            explicacion_m3 += "* **Expectativas Racionales (Shock Anticipado en t=4):** El consumidor anticipa el cambio de ingresos que ocurrirá en el futuro. El valor presente de su riqueza total ($\Omega$) cambia hoy (t=1), por lo que el nivel de consumo óptimo se ajusta **inmediatamente**, adelantándose al shock.\n"
            if restriccion_liquidez and magnitud_shock > 0:
                explicacion_m3 += "  * ⚠️ **Restricción de Liquidez Activa:** Aunque el agente sabe que será más rico en t=4 y querría consumir más hoy, el mercado de capitales imperfecto **no le permite endeudarse**. Queda atrapado contra la restricción (Punto B en el gráfico izquierdo, $A_t = 0$ en el inferior). Su consumo efectivo no puede subir hasta que el ingreso se materialice físicamente en t=4."
            elif restriccion_liquidez and magnitud_shock < 0:
                explicacion_m3 += "  * ⚠️ **Restricción de Liquidez (Frente a caída futura):** Como el agente anticipa que será más pobre, necesita **ahorrar preventivamente** desde hoy. Dado que el sistema financiero siempre permite guardar fondos (solo restringe pedir prestado), la restricción *no* resulta vinculante. La trayectoria del consumo restringido logra igualar a la del consumo libre sin problemas, acumulando activos en t=1, 2 y 3."

        st.success(explicacion_m3)
