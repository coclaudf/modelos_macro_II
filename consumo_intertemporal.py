import streamlit as st
import numpy as np
import plotly.graph_objects as go


def verificar_autenticacion():
    # 1. Definir credenciales y dominio institucional
    CLAVE_SECRETA = "cfcyo2012"  # La clave para abrirlo por fuera
    DOMINIO_AULA = "campus.uner.edu.ar"  # Reemplaza por el dominio real de tu aula virtual
    
    # 2. Leer metadatos del navegador del alumno
    try:
        headers = st.context.headers
        referer = headers.get("referer", "").lower()
        fetch_dest = headers.get("sec-fetch-dest", "").lower()
        
        # Si el origen es el aula virtual O el destino detectado es un iframe, otorgar acceso libre
        if DOMINIO_AULA in referer or fetch_dest == "iframe":
            return True
    except Exception:
        # Salvaguarda por si corres el script en tu PC local (donde st.context no tiene estos headers)
        pass

    # 3. Pantalla de bloqueo si se abre por fuera del Aula Virtual
    st.sidebar.subheader("🔒 Acceso Restringido")
    password_ingresado = st.sidebar.text_input(
        "Este simulador pertenece al Aula Virtual. Introduce la clave de la cátedra para acceso directo:", 
        type="password"
    )
    
    if password_ingresado == CLAVE_SECRETA:
        return True
    elif password_ingresado:
        st.sidebar.error("❌ Clave incorrecta")
        
    # Mensaje pedagógico persuasivo en el cuerpo principal
    st.warning("⚠️ **Acceso No Autorizado:** Por favor, interactúa con este modelo directamente desde las lecturas de tu Aula Virtual o solicita la clave de desarrollo a la cátedra.")
    st.info("💡 *Nota para el alumno: Diseñamos estas herramientas para que sigan el hilo de tus apuntes teóricos en la plataforma de estudio.*")
    return False

# =============================================================================
# CONTROL DE FLUJO PRINCIPAL
# =============================================================================
if verificar_autenticacion():
    # TODO EL CÓDIGO DEL SIMULADOR VA AQUÍ ADENTRO
    st.title("Modelo de Consumo Intertemporal")
    # ... rest de tu app ...


# Configuración de página de alta definición
st.set_page_config(
    page_title="Simulador de Consumo Intertemporal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales complementarios
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .stAlert { margin-top: 1rem; }
    </style>
""", unsafe_allowed_html=True)

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
    y1 = st.sidebar.slider("Ingreso Período 1 (Y1)", 10.0, 100.0, 50.0, 5.0)
    y2 = st.sidebar.slider("Ingreso Período 2 (Y2)", 10.0, 100.0, 50.0, 5.0)
    beta = st.sidebar.slider("Factor de Descuento (β)", 0.5, 1.5, 1.0, 0.05)
    
    st.sidebar.subheader("⚡ Shock de Tasa de Interés")
    i_inicial = st.sidebar.slider("Tasa de Interés Inicial (i₀)", 0.0, 1.0, 0.10, 0.05, format="%.2f")
    i_final = st.sidebar.slider("Tasa de Interés Post-Shock (i₁)", 0.0, 1.0, 0.40, 0.05, format="%.2f")

    # Cálculos económicos óptimos (Utilidad logarítmica: U = ln(C1) + beta * ln(C2))
    # Riqueza en valor presente (Omega)
    omega_inicial = y1 + y2 / (1 + i_inicial)
    omega_final = y1 + y2 / (1 + i_final)
    
    # Elecciones óptimas iniciales
    c1_inicial = omega_inicial / (1 + beta)
    c2_inicial = (beta * (1 + i_inicial) * omega_inicial) / (1 + beta)
    u_inicial = np.log(c1_inicial) + beta * np.log(c2_inicial)
    
    # Elecciones óptimas finales
    c1_final = omega_final / (1 + beta)
    c2_final = (beta * (1 + i_final) * omega_final) / (1 + beta)
    
    # Descomposición de Hicks: Minimizar gasto con nueva tasa i_final manteniendo u_inicial
    # C2 = beta * (1 + i_final) * C1 -> Sustituyendo en la función de utilidad igualada a u_inicial:
    c1_hicks = np.exp((u_inicial - beta * np.log(beta * (1 + i_final))) / (1 + beta))
    c2_hicks = beta * (1 + i_final) * c1_hicks
    omega_hicks = c1_hicks + c2_hicks / (1 + i_final)

    # Definición de efectos económicos
    efecto_sustitucion = c1_hicks - c1_inicial
    efecto_ingreso = c1_final - c1_hicks
    efecto_total = c1_final - c1_inicial
    
    tipo_hogar = "Equilibrado" if abs(y1 - c1_inicial) < 0.01 else ("Ahorrante" if y1 > c1_inicial else "Deudor")

    # Despliegue de Gráficos en columnas (Estática vs Dinámica de Corto Plazo)
    st.subheader("📊 Análisis Geométrico Intertemporal vs Trayectoria Dinámica")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Espacio de Asignación Intertemporal (Estática)**")
        
        # Vectores para graficar restricciones y curvas de indiferencia
        c1_vec = np.linspace(0.1, max(omega_inicial, omega_final) * 1.1, 200)
        
        fig_static = go.Figure()
        
        # Restricción Presupuestaria Inicial
        rpi_y = (omega_inicial - c1_vec) * (1 + i_inicial)
        fig_static.add_trace(go.Scatter(x=c1_vec, y=rpi_y, name="RPI Inicial (i₀)", line=dict(color='gray', dash='dash')))
        
        # Restricción Presupuestaria Final
        rpf_y = (omega_final - c1_vec) * (1 + i_final)
        fig_static.add_trace(go.Scatter(x=c1_vec, y=rpf_y, name="RPF Final (i₁)", line=dict(color='blue')))
        
        # Restricción de Hicks (Teórica)
        rph_y = (omega_hicks - c1_vec) * (1 + i_final)
        fig_static.add_trace(go.Scatter(x=c1_vec, y=rph_y, name="RP Hicks (Gasto Mín)", line=dict(color='orange', width=1, dash='dot')))
        
        # Curva de Indiferencia Inicial
        indif_inicial = np.exp((u_inicial - np.log(c1_vec)) / beta)
        fig_static.add_trace(go.Scatter(x=c1_vec, y=indif_inicial, name="U₀ (Inicial)", line=dict(color='green', width=2)))
        
        # Puntos de Equilibrio
        fig_static.add_trace(go.Scatter(x=[c1_inicial], y=[c2_inicial], mode='markers+text', text=['A (Inicial)'], textposition='top right', marker=dict(color='green', size=10), showlegend=False))
        fig_static.add_trace(go.Scatter(x=[c1_final], y=[c2_final], mode='markers+text', text=['B (Final)'], textposition='top right', marker=dict(color='blue', size=10), showlegend=False))
        fig_static.add_trace(go.Scatter(x=[c1_hicks], y=[c2_hicks], mode='markers+text', text=['C (Hicks)'], textposition='bottom left', marker=dict(color='orange', size=8), showlegend=False))
        fig_static.add_trace(go.Scatter(x=[y1], y=[y2], mode='markers+text', text=['Dotación (Y)'], textposition='bottom right', marker=dict(color='black', symbol='x', size=10), showlegend=True, name="Dotación"))

        fig_static.update_layout(
            xaxis_title="Consumo Presente (C₁)", yaxis_title="Consumo Futuro (C₂)",
            xaxis=dict(range=[0, max(omega_inicial, omega_final)*1.05]), yaxis=dict(range=[0, max(omega_inicial, omega_final)*(1+i_final)*0.7]),
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
            margin=dict(l=20, r=20, t=20, b=20), height=450
        )
        st.plotly_chart(fig_static, use_container_width=True)

    with col2:
        st.write("**Evolución Temporal del Consumo y el Ingreso (Dinámica)**")
        
        # Construcción de la trayectoria temporal de 2 períodos
        periodos = ['Período 1 (Hoy)', 'Período 2 (Mañana)']
        
        fig_dynamic = go.Figure()
        # Trayectoria de Ingresos
        fig_dynamic.add_trace(go.Scatter(x=periodos, y=[y1, y2], name="Ingreso (Y)", line=dict(color='black', width=3), marker=dict(size=8)))
        # Trayectoria de Consumo Inicial
        fig_dynamic.add_trace(go.Scatter(x=periodos, y=[c1_inicial, c2_inicial], name="Consumo Inicial", line=dict(color='green', width=2, dash='dash'), marker=dict(size=6)))
        # Trayectoria de Consumo Final
        fig_dynamic.add_trace(go.Scatter(x=periodos, y=[c1_final, c2_final], name="Consumo Post-Shock", line=dict(color='blue', width=3), marker=dict(size=8)))
        
        fig_dynamic.update_layout(
            yaxis_title="Unidades de Producción/Consumo",
            yaxis=dict(range=[0, max(y1, y2, c2_inicial, c2_final)*1.15]),
            legend=dict(yanchor="bottom", y=0.01, xanchor="left", x=0.01),
            margin=dict(l=20, r=20, t=20, b=20), height=450
        )
        st.plotly_chart(fig_dynamic, use_container_width=True)

    # Tabla resumen de efectos para los estudiantes
    st.markdown("### 📋 Desglose Cuantitativo de Efectos en el Período 1 ($C_1$)")
    metrics = st.columns(4)
    metrics[0].metric(label="Perfil de Familia", value=tipo_hogar)
    metrics[1].metric(label="Efecto Sustitución (ES)", value=f"{efecto_sustitucion:.2f}", delta="C₁ ↓" if efecto_sustitucion < 0 else "C₁ ↑")
    metrics[2].metric(label="Efecto Ingreso (EI)", value=f"{efecto_income:=efecto_ingreso:.2f}", delta="C₁ ↑" if efecto_ingreso > 0 else "C₁ ↓")
    metrics[3].metric(label="Efecto Total (ET)", value=f"{efecto_total:.2f}")

    # Caja pedagógica adaptativa
    st.info(f"""
    **Intuición Económica para el Alumno:**  
    Al incrementarse la tasa de interés de **{i_inicial*100:.0f}%** a **{i_final*100:.0f}%**, el consumo futuro se vuelve relativamente más barato, generando un **Efecto Sustitución Inequívocamente Negativo** de **{efecto_sustitucion:.2f}** unidades en el consumo presente ($C_1$).  
    Como el agente posee un perfil **{tipo_hogar}**, el **Efecto Ingreso** actúa de la siguiente manera: 
    { "Al ser ahorrante, el alza de tasa expande su riqueza intertemporal (Efecto Ingreso positivo), contrarrestando parcialmente la sustitución." if tipo_hogar == "Ahorrante" else "Al ser deudor, el alza de tasa encarece el servicio de su deuda actual, volviéndolo más pobre intertemporalmente. Ambos efectos se refuerzan hacia la caída del consumo presente." if tipo_hogar == "Deudor" else "Al estar en equilibrio exacto de dotación, el Efecto Ingreso puro de Hicks es nulo; la modificación conductual responde netamente al Efecto Sustitución." }
    """)

# =============================================================================
# MÓDULO 2: TEORÍA DEL INGRESO PERMANENTE CON TRANSICIÓN DINÁMICA COMPLETA
# =============================================================================
elif modelo_seleccionado == "2. Dinámica del Ingreso Permanente (Largo Plazo y Liquidez)":
    
    st.sidebar.subheader("🎛️ Parámetros Estacionarios")
    y_estado_estacionario = st.sidebar.slider("Ingreso Base de Estado Estacionario (Y₀)", 10.0, 100.0, 50.0, 5.0)
    r_interes = st.sidebar.slider("Tasa de Interés Real (r)", 0.01, 0.20, 0.05, 0.01, format="%.2f")
    horizonte_t = 10  # Períodos de la simulación (t=0 a t=10)
    
    st.sidebar.subheader("⚡ Tipología de Shocks en t=1")
    tipo_shock = st.sidebar.selectbox(
        "Seleccione la naturaleza del shock de ingreso:",
        ["Temporal Transitorio (Solo en t=1)", 
         "Permanente (De t=1 en adelante)", 
         "Futuro Anticipado Positivo (Anuncio en t=1, ocurre en t=4)",
         "Futuro Anticipado Negativo (Anuncio en t=1, ocurre en t=4)"]
)
    magnitud_shock = st.sidebar.slider("Magnitud del Shock (ΔY)", -30.0, 30.0, 15.0, 5.0)
    
    st.sidebar.subheader("🛡️ Imperfecciones de Mercado")
    restriccion_liquidez = st.sidebar.checkbox("Activar Restricción de Liquidez Estricta (No Endeudamiento)")

    # Construcción de vectores temporales (Anclaje estricto en t=0)
    t_vec = np.arange(0, horizonte_t + 1)
    y_trayectoria = np.full(horizonte_t + 1, y_estado_estacionario, dtype=float)
    
    # Aplicación del shock físico al vector de ingresos
    if tipo_shock == "Temporal Transitorio (Solo en t=1)":
        y_trayectoria[1] = y_estado_estacionario + magnitud_shock
    elif tipo_shock == "Permanente (De t=1 en adelante)":
        y_trayectoria[1:] = y_estado_estacionario + magnitud_shock
    elif tipo_shock in ["Futuro Anticipado Positivo (Anuncio en t=1, ocurre en t=4)", 
                        "Futuro Anticipado Negativo (Anuncio en t=1, ocurre en t=4)"]:
        # El shock físico ocurre en t=4 en adelante, pero el anuncio es conocido en t=1
        y_trayectoria[4:] = y_estado_estacionario + magnitud_shock

    # --- SIMULACIÓN 1: CONSUMIDOR RACIONAL SIN RESTRICCIONES ---
    c_libre = np.zeros(horizonte_t + 1)
    a_libre = np.zeros(horizonte_t + 1)  # Activos netos al final de cada período
    
    # Período 0: Estado estacionario pleno
    c_libre[0] = y_estado_estacionario
    a_libre[0] = 0.0
    
    # Cálculo del Valor Presente de Ingresos desde t=1 hasta T para determinar el Ingreso Permanente
    vpi_1 = sum(y_trayectoria[t] / ((1 + r_interes) ** (t - 1)) for t in range(1, horizonte_t + 1))
    factor_anualidad = sum(1 / ((1 + r_interes) ** (t - 1)) for t in range(1, horizonte_t + 1))
    c_permanente_optimo = vpi_1 / factor_anualidad
    
    # Llenado de trayectorias sin restricciones para t>=1
    for t in range(1, horizonte_t + 1):
        c_libre[t] = c_permanente_optimo
        a_libre[t] = a_libre[t-1] * (1 + r_interes) + y_trayectoria[t] - c_libre[t]

    # --- SIMULACIÓN 2: CONSUMIDOR BAJO RESTRICCIÓN DE LIQUIDEZ (A_t >= 0) ---
    c_restric = np.zeros(horizonte_t + 1)
    a_restric = np.zeros(horizonte_t + 1)
    
    c_restric[0] = y_estado_estacionario
    a_restric[0] = 0.0
    
    # Algoritmo de optimización forward con restricción de liquidez period-by-period
    for t in range(1, horizonte_t + 1):
        # El consumidor intenta suavizar el consumo evaluando el valor presente remanente
        vpi_remanente = sum(y_trayectoria[k] / ((1 + r_interes) ** (k - t)) for k in range(t, horizonte_t + 1))
        factor_anualidad_remanente = sum(1 / ((1 + r_interes) ** (k - t)) for k in range(t, horizonte_t + 1))
        
        # Consumo deseado basado en la riqueza remanente acumulada
        c_deseado = (a_restric[t-1] * (1 + r_interes) + vpi_remanente) / factor_anualidad_remanente
        
        # Evaluación de la restricción de liquidez: si el consumo deseado genera deuda (activos < 0)
        if c_deseado > (y_trayectoria[t] + a_restric[t-1] * (1 + r_interes)):
            # El agente consume toda su liquidez corriente disponible y sus activos caen a cero
            c_restric[t] = y_trayectoria[t] + a_restric[t-1] * (1 + r_interes)
            a_restric[t] = 0.0
        else:
            # Al agente se le permite ahorrar libremente
            c_restric[t] = c_deseado
            a_restric[t] = a_restric[t-1] * (1 + r_interes) + y_trayectoria[t] - c_restric[t]

    # --- VISUALIZACIÓN DINÁMICA DE LA TRAYECTORIA ---
    st.subheader(f"📈 Senda Temporal de Transición Dinámica: {tipo_shock}")
    
    fig_lineas = go.Figure()
    
    # Línea de Ingreso Físico (Y)
    fig_lineas.add_trace(go.Scatter(x=t_vec, y=y_trayectoria, name="Ingreso Disponible (Yₜ)",
                                    line=dict(color='black', width=3, shape='hv')))
    
    # Línea de Consumo Optimo (Sin Restricciones)
    fig_lineas.add_trace(go.Scatter(x=t_vec, y=c_libre, name="Consumo Permanente (Teórico Libre)",
                                    line=dict(color='blue', width=2.5, dash='dash')))
    
    # Línea de Consumo Efectivo con Restricción de Liquidez
    if restriccion_liquidez:
        fig_lineas.add_trace(go.Scatter(x=t_vec, y=c_restric, name="Consumo con Restricción de Liquidez",
                                        line=dict(color='crimson', width=3)))
        
    # Elementos de anclaje visual (Línea de Estado Estacionario Base)
    fig_lineas.add_line_preset_treatment = True
    fig_lineas.add_hline(y=y_estado_estacionario, line_dash="dot", line_color="gray", 
                         annotation_text="EE Inicial (t=0)", annotation_position="bottom left")

    fig_lineas.update_layout(
        xaxis=dict(tickmode='linear', tick0=0, dtick=1, title="Períodos Temporales (t)"),
        yaxis=dict(title="Escala de Valores (Moneda Real)"),
        margin=dict(l=40, r=40, t=20, b=20),
        height=500,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
    )
    st.plotly_chart(fig_lineas, use_container_width=True)

    # Gráfico complementario de acumulación de Activos/Ahorro
    st.subheader("🏦 Senda de Acumulación / Desacumulación de Activos Netos ($A_t$)")
    fig_assets = go.Figure()
    fig_assets.add_trace(go.Scatter(x=t_vec, y=a_libre, name="Activos Sin Restricción", line=dict(color='blue', dash='dash')))
    if restriccion_liquidez:
        fig_assets.add_trace(go.Scatter(x=t_vec, y=a_restric, name="Activos Con Restricción", line=dict(color='crimson', width=2.5)))
    fig_assets.add_hline(y=0.0, line_color="black", line_width=1)
    fig_assets.update_layout(
        xaxis=dict(tickmode='linear', tick0=0, dtick=1, title="Períodos Temporales (t)"),
        yaxis=dict(title="Stock de Activos Netos"),
        margin=dict(l=40, r=40, t=20, b=20), height=300
    )
    st.plotly_chart(fig_assets, use_container_width=True)

    # --- RECUADRO PEDAGÓGICO ADAPTATIVO ---
    st.success("### 🎓 Guía de Análisis Macroeconómico para el Alumno")
    
    # Bloques condicionales explicativos basados en la selección de parámetros
    if tipo_shock == "Temporal Transitorio (Solo en t=1)":
        st.write("""
        * **Comportamiento del Consumidor Racional:** Al experimentar una variación transitoria del ingreso en $t=1$, el agente reconoce que su Ingreso Permanente ($Y_p$) apenas se altera. Por ende, el consumo óptimo permanece plano, recurriendo al mercado de capitales (desahorro si el shock es negativo o ahorro si es positivo) para suavizar completamente su trayectoria.
        * **Efecto de la Restricción de Liquidez:** Si el shock es negativo y la restricción está activa, el alumno observará cómo el consumo cae uno a uno con el ingreso en $t=1$. El modelo se vuelve transitoriamente **Keynesiano** debido a la imposibilidad de acceder al crédito para suavizar la caída.
        """)
    elif tipo_shock == "Permanente (De t=1 en adelante)":
        st.write("""
        * **Comportamiento General:** Al ser un cambio que se sostiene a lo largo de todo el ciclo de vida, el Ingreso Permanente se ajusta exactamente en la misma magnitud que el shock físico. El consumo salta de forma idéntica en $t=1$ y se estabiliza en su nuevo nivel. 
        * **Nota sobre la restricción:** Aquí las restricciones de liquidez no operan activamente, dado que el consumidor no requiere financiamiento intertemporal; se ajusta de inmediato a su nueva realidad presupuestaria.
        """)
    else:  # Shocks anticipados
        st.write("""
        * **El Rol Central de las Expectativas Racionales:** Este escenario es clave. Aunque el impacto físico sobre el bolsillo ocurre recién en el período $t=4$, el anuncio ocurre en $t=1$. El consumidor con previsión perfecta calcula el cambio en su riqueza intertemporal y **salta su consumo inmediatamente en el período 1**.
        * **Interacción con la Restricción de Liquidez:** 
            * Si el shock futuro es *positivo*, el consumidor libre querrá consumir más desde hoy endeudándose. Al activar la restricción de liquidez, verás que el consumo se queda atrapado en el nivel de ingreso corriente hasta $t=4$. La restricción destruye la capacidad de anticipación distributiva.
            * Si el shock futuro es *negativo*, el agente necesita *ahorrar hoy* para prepararse. Dado que la restricción impide endeudarse pero permite ahorrar, el consumidor con restricción de liquidez se comporta exactamente igual que el libre, contrayendo su consumo de manera preventiva desde el período 1.
        """)
