import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de página
st.set_page_config(
    page_title="Simulador de Cuenta Corriente y Ahorro-Inversión",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# BLINDAJE DE ALTO CONTRASTE (ESTÉTICA UNIFICADA)
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

# Botón Despertador para Moodle
st.markdown("""
<div style="background-color: #FFFBEB; border-left: 4px solid #F59E0B; padding: 15px; margin-bottom: 20px; border-radius: 4px; font-family: sans-serif;">
    <p style="margin-top: 0; color: #92400E; font-size: 14px;">
        <strong>⚠️ ¿El simulador aparece en blanco o te pide contraseña?</strong> Esto ocurre por inactividad.
    </p>
    <a href="https://TULINKDESTREAMLIT.streamlit.app" target="_blank" style="background-color: #D97706; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block; font-size: 14px;">
        🚀 Hacer clic aquí para despertarlo
    </a>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SEGURIDAD Y AULA VIRTUAL
# =============================================================================
def verificar_autenticacion():
    CLAVE_SECRETA = "Macro2026"
    qp = st.query_params
    if "embed" in qp or qp.get("embed") == "true" or "uner" in qp or "aula" in qp: return True
    try:
        referer = st.context.headers.get("referer", "").lower()
        if any(dom in referer for dom in ["moodle", "canvas", "classroom", "uner.edu.ar"]): return True
    except: pass
    st.sidebar.subheader("🔒 Acceso Restringido")
    pwd = st.sidebar.text_input("Introduce la clave:", type="password")
    if pwd == CLAVE_SECRETA: return True
    elif pwd: st.sidebar.error("❌ Clave incorrecta")
    return False

if verificar_autenticacion():

    st.title("🌍 Modelo Intertemporal: Ahorro, Inversión y Cuenta Corriente")
    st.markdown("*Análisis del equilibrio macroeconómico con sector público y movilidad de capitales (Sachs & Larraín).*")

    # Colores unificados de alto contraste
    COLOR_TEXTO, COLOR_EJE, COLOR_GRILLA = '#111827', '#374151', '#9CA3AF'
    C_BLUE, C_GREEN, C_PURPLE, C_RED, C_GRAY = '#1D4ED8', '#15803D', '#7E22CE', '#DC2626', '#6B7280'

    eje_formato = dict(
        showline=True, linecolor=COLOR_EJE, linewidth=2, gridcolor=COLOR_GRILLA,
        tickfont=dict(color=COLOR_TEXTO, size=13, family="Arial"),
        title_font=dict(color=COLOR_TEXTO, size=15, family="Arial", weight="bold")
    )

    # --- BARRA LATERAL: SELECCIÓN DE MÓDULO ---
    st.sidebar.header("🛠️ Módulo de Análisis")
    modulo = st.sidebar.radio("Seleccione el enfoque:", [
        "1. País Individual (S, I y Cuenta Corriente)",
        "2. Modelo de Dos Países (Ajuste Distribuido)"
    ])

    st.sidebar.markdown("---")

    # =============================================================================
    # MÓDULO 1: PAÍS INDIVIDUAL
    # =============================================================================
    if modulo == "1. País Individual (S, I y Cuenta Corriente)":
        
        st.sidebar.subheader("⚙️ Entorno Institucional")
        regimen = st.sidebar.radio("Régimen de Apertura:", [
            "A. Pequeña Economía Abierta (r dada)",
            "B. Economía Cerrada / Controles de Capital (CC=0)",
            "C. Gran Economía Abierta (Impacto en r mundial)"
        ])

        st.sidebar.subheader("⚡ Escenarios Macroeconómicos")
        escenario = st.sidebar.selectbox("Shock Aplicado:", [
            "0. Situación Inicial (Equilibrio base)",
            "1. Auge Exportador Transitorio (Suba de Ingreso)",
            "2. Boom de Inversión ('Animal Spirits')",
            "3. Aumento del Gasto Público Transitorio (Déficit)",
            "4. Equivalencia Ricardiana (Baja T con deuda)",
            "5. Shock Externo Global (Sube r* mundial)",
            "6. Trampa de Liquidez (Colapso de Inversión)"
        ])

        # MATEMÁTICA
        sr, ir = 500.0, 500.0
        S0_base, I0_base = 100.0, 200.0
        r_world_base = 0.10

        S0, I0, r_world = S0_base, I0_base, r_world_base
        show_ricardian = False

        if escenario == "1. Auge Exportador Transitorio (Suba de Ingreso)": S0 = S0_base + 50.0  
        elif escenario == "2. Boom de Inversión ('Animal Spirits')": I0 = I0_base + 50.0  
        elif escenario == "3. Aumento del Gasto Público Transitorio (Déficit)": S0 = S0_base - 50.0  
        elif escenario == "4. Equivalencia Ricardiana (Baja T con deuda)":
            show_ricardian = True
            S0 = S0_base 
        elif escenario == "5. Shock Externo Global (Sube r* mundial)": r_world = 0.15 
        elif escenario == "6. Trampa de Liquidez (Colapso de Inversión)": I0 = I0_base - 140.0 

        r_autarky = (I0 - S0) / (sr + ir)
        ZLB_activa = False

        if "Cerrada" in regimen:
            r_eq = r_autarky
            if r_eq < 0.0: r_eq, ZLB_activa = 0.0, True
        elif "Pequeña" in regimen:
            r_eq = r_world
        else: 
            r_eq = r_world_base + 0.40 * (r_autarky - r_world_base)
            if "Shock Externo" in escenario: r_eq = 0.15 
            if r_eq < 0.0: r_eq = 0.0

        S_eq, I_eq = S0 + sr * r_eq, I0 - ir * r_eq
        CC_eq = S_eq - I_eq

        if ZLB_activa and "Cerrada" in regimen:
            CC_eq, S_efectivo = 0.0, I_eq
        else: S_efectivo = S_eq

        r_vec = np.linspace(0.0, 0.25, 200)
        S_curva, I_curva = S0 + sr * r_vec, I0 - ir * r_vec
        CC_curva = S_curva - I_curva

        # DASHBOARD M1
        st.subheader("📋 Equilibrio Macroeconómico Resultante")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tasa de Interés (r)", f"{r_eq*100:.1f}%", "- ZLB Activa" if ZLB_activa else None, delta_color="off")
        m2.metric("Ahorro Nacional (S)", f"{S_efectivo:.1f}")
        m3.metric("Inversión Nacional (I)", f"{I_eq:.1f}")
        m4.metric("Cuenta Corriente (CC)", f"{CC_eq:.1f}", "Déficit" if CC_eq < -0.1 else ("Superávit" if CC_eq > 0.1 else "Equilibrio"), delta_color="inverse" if CC_eq < 0 else "normal")

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            fig_si = go.Figure()
            if "0." not in escenario:
                fig_si.add_trace(go.Scatter(x=S0_base + sr * r_vec, y=r_vec, name="S₀ (Ahorro Inicial)", line=dict(color=C_GREEN, width=1.5, dash='dot')))
                fig_si.add_trace(go.Scatter(x=I0_base - ir * r_vec, y=r_vec, name="I₀ (Inversión Inicial)", line=dict(color=C_BLUE, width=1.5, dash='dot')))

            fig_si.add_trace(go.Scatter(x=S_curva, y=r_vec, name="S₁ (Ahorro Nacional)", line=dict(color=C_GREEN, width=3)))
            fig_si.add_trace(go.Scatter(x=I_curva, y=r_vec, name="I₁ (Inversión Nacional)", line=dict(color=C_BLUE, width=3)))

            if show_ricardian:
                fig_si.add_trace(go.Scatter(x=(S0 + 40) + sr * r_vec, y=r_vec, name="S_priv (Ahorro Privado)", line=dict(color='#86EFAC', width=2, dash='dash')))
                fig_si.add_trace(go.Scatter(x=np.full(len(r_vec), -40), y=r_vec, name="S_pub (Ahorro Público)", line=dict(color='#FCA5A5', width=2, dash='dash')))
                fig_si.add_annotation(x=200, y=0.20, text="S_Total no se mueve<br>(Spriv compensa Spub)", showarrow=False, font=dict(color=COLOR_TEXTO, size=12), bgcolor="#F3F4F6")

            fig_si.add_hline(y=r_eq, line_dash="dash", line_color=COLOR_TEXTO, annotation_text=f"r = {r_eq*100:.1f}%", annotation_position="top left")

            if abs(CC_eq) > 0.1 and not (ZLB_activa and "Cerrada" in regimen):
                color_banda = "rgba(220, 38, 38, 0.2)" if CC_eq < 0 else "rgba(21, 128, 61, 0.2)" 
                fig_si.add_shape(type="rect", x0=min(S_eq, I_eq), x1=max(S_eq, I_eq), y0=r_eq-0.005, y1=r_eq+0.005, fillcolor=color_banda, line_width=0)
                fig_si.add_annotation(x=(S_eq+I_eq)/2, y=r_eq+0.015, text="Déficit CC" if CC_eq < 0 else "Superávit CC", showarrow=False, font=dict(color=COLOR_TEXTO, size=11))

            if ZLB_activa and "Cerrada" in regimen:
                fig_si.add_shape(type="rect", x0=I_eq, x1=S_eq, y0=-0.005, y1=0.005, fillcolor="rgba(107, 114, 128, 0.3)", line_width=0)
                fig_si.add_annotation(x=(S_eq+I_eq)/2, y=0.015, text="Brecha Recesiva", showarrow=False, font=dict(color=C_RED, size=11))

            fig_si.update_layout(
                title=dict(text="Mercado de Fondos (Ahorro e Inversión)", font=dict(color=COLOR_TEXTO, size=16)),
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=dict(color=COLOR_TEXTO, family="Arial", size=14),
                legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.9)", bordercolor="black", borderwidth=1), 
                margin=dict(l=20, r=20, t=40, b=20), height=450
            )
            fig_si.update_xaxes(title_text="Fondos (S, I)", range=[-50, 300], **eje_formato)
            fig_si.update_yaxes(title_text="Tasa de Interés Real (r)", range=[0, 0.25], tickformat=".0%", **eje_formato)
            st.plotly_chart(fig_si, use_container_width=True, theme=None)

        with col_g2:
            fig_cc = go.Figure()
            if "0." not in escenario:
                fig_cc.add_trace(go.Scatter(x=(S0_base - I0_base) + (sr + ir) * r_vec, y=r_vec, name="CC₀ (Base)", line=dict(color=C_PURPLE, width=1.5, dash='dot')))
            fig_cc.add_trace(go.Scatter(x=CC_curva, y=r_vec, name="CC₁ (Cuenta Corriente)", line=dict(color=C_PURPLE, width=3)))
            fig_cc.add_hline(y=r_eq, line_dash="dash", line_color=COLOR_TEXTO)
            fig_cc.add_vline(x=0, line_dash="solid", line_color="black", line_width=1) 

            if not (ZLB_activa and "Cerrada" in regimen):
                fig_cc.add_trace(go.Scatter(x=[CC_eq], y=[r_eq], mode='markers+text', text=['Eq.'], textposition='bottom right', marker=dict(color='black', size=10), showlegend=False))

            fig_cc.update_layout(
                title=dict(text="Función de Cuenta Corriente (S - I)", font=dict(color=COLOR_TEXTO, size=16)),
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=dict(color=COLOR_TEXTO, family="Arial", size=14),
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.9)", bordercolor="black", borderwidth=1), 
                margin=dict(l=20, r=20, t=40, b=20), height=450
            )
            fig_cc.update_xaxes(title_text="Saldo de Cuenta Corriente (CC)", range=[-150, 150], **eje_formato)
            fig_cc.update_yaxes(title_text="Tasa de Interés Real (r)", range=[0, 0.25], tickformat=".0%", **eje_formato)
            st.plotly_chart(fig_cc, use_container_width=True, theme=None)

        # GENERACIÓN DEL TEXTO PEDAGÓGICO COMPACTO (Corrección estética)
        regimen_txt = ""
        if "Cerrada" in regimen: regimen_txt = "Al tener la Cuenta Corriente bloqueada (Economía Cerrada), el país no puede importar ni exportar ahorro. La tasa de interés interna (r) ajusta para forzar que S=I."
        elif "Pequeña" in regimen: regimen_txt = "Es una economía tomadora de precios. La tasa interna está anclada a la mundial (r = r*). Cualquier descalce entre S e I se resuelve exportando fondos o importando capitales."
        else: regimen_txt = "Al ser un país Grande, sus shocks internos tienen volumen suficiente para modificar la oferta global de fondos, alterando parcialmente la tasa de interés mundial (r*)."

        dinamica_txt = ""
        if "0." in escenario: dinamica_txt = "La economía está en su punto de equilibrio natural. Al 10% de tasa, el Ahorro financia exactamente la Inversión local, resultando en CC nula."
        elif "1." in escenario:
            dinamica_txt = "El incremento del ingreso presente induce a las familias a ahorrar el excedente. La curva S se desplaza a la derecha, moviendo también la CC.\n\n"
            dinamica_txt += "📉 **Resultado:** Como la CC es cero, la abundancia de ahorro desploma la tasa de interés hasta que la Inversión absorbe los fondos." if "Cerrada" in regimen else "🚢 **Resultado:** A la tasa internacional, el exceso de ahorro doméstico sale del país buscando rentabilidad, generando un Superávit de CC."
        elif "2." in escenario:
            dinamica_txt = "Mejoran las expectativas de rentabilidad. Las empresas demandan más fondos prestables, desplazando la Inversión a la derecha. Esto empuja la curva CC a la izquierda.\n\n"
            dinamica_txt += "📈 **Resultado:** La competencia por fondos empuja la tasa hacia arriba para racionar crédito, manteniendo CC=0." if "Cerrada" in regimen else "🚢 **Resultado:** Para financiar proyectos sin subir drásticamente la tasa, el país recurre al ahorro externo. Entran flujos de capital (Déficit de CC)."
        elif "3." in escenario:
            dinamica_txt = "El gobierno gasta más sin subir impuestos hoy, reduciendo el Ahorro Público. La curva S retrocede a la izquierda, arrastrando a la CC.\n\n"
            dinamica_txt += "👯‍♂️ **Déficits Gemelos:** El déficit fiscal reduce los fondos. Para mantener la inversión doméstica, se importa ahorro del exterior (Déficit de CC)." if "Abierta" in regimen else "📈 **Crowding Out:** El déficit desplaza al sector privado subiendo la tasa local."
        elif "4." in escenario:
            dinamica_txt = "El gobierno redujo impuestos emitiendo deuda (Cae Ahorro Público). Los agentes racionales anticipan que esa deuda significa mayores impuestos futuros, por lo que ahorran por completo ese ingreso extra (Sube Ahorro Privado).\n\n"
            dinamica_txt += "🛡️ **Resultado:** El salto del S privado compensa exactamente la caída del S público. La curva de Ahorro Nacional (S) queda inalterada. ¡Se rompe la hipótesis de déficits gemelos!"
        elif "5." in escenario:
            dinamica_txt = "Encarecimiento del crédito mundial. No hay desplazamientos de curvas, sino un movimiento a lo largo de las mismas.\n\n"
            dinamica_txt += "🛡️ **Resultado:** La economía cerrada está blindada a este shock." if "Cerrada" in regimen else "⚠️ **Ajuste:** La alta tasa mundial frena los proyectos (Cae I) e incentiva el ahorro (Cae C). Esta contracción interna mejora forzosamente la CC hacia el superávit."
        elif "6." in escenario:
            dinamica_txt = "La expectativa de rentabilidad colapsa y la curva de Inversión sufre una retracción masiva a la izquierda.\n\n"
            if "Cerrada" in regimen: dinamica_txt += "🚨 **Zero Lower Bound:** Para igualar S e I, la tasa debería ser negativa. Al chocar contra el piso del 0%, el Ahorro supera a la Inversión. La única salida es la recesión: el Ingreso Nacional cae hasta cerrar las brechas (cruz keynesiana)."
            else: dinamica_txt += "🚢 **Válvula de Escape:** El exceso de fondos local simplemente abandona el país buscando rendimientos a la tasa mundial, generando un Superávit masivo de Cuenta Corriente sin necesidad de una gran recesión interna."

        texto_final = f"""### 🎓 Análisis del Escenario: {escenario.split('.')[1].strip()}
**🌍 Régimen Institucional:** {regimen_txt}

**💡 Dinámica Macroeconómica:** {dinamica_txt}"""
        
        st.success(texto_final)


    # =============================================================================
    # MÓDULO 2: DOS PAÍSES (AJUSTE DISTRIBUIDO)
    # =============================================================================
    elif modulo == "2. Modelo de Dos Países (Ajuste Distribuido)":
        
        st.sidebar.subheader("⚡ Shock en la Economía Global")
        escenario_2p = st.sidebar.selectbox("Seleccione el origen del shock:", [
            "0. Situación Inicial (Equilibrio Global, r*=10%)",
            "1. Boom de Inversión en País GRANDE",
            "2. Boom de Inversión en País PEQUEÑO",
            "3. Política Fiscal Expansiva en País GRANDE (Cae Ahorro)",
            "4. Política Fiscal Expansiva en País PEQUEÑO (Cae Ahorro)"
        ])

        # Parámetros Base - Asimetría Estructural
        # País A (Grande): Representa el ~90% del mercado de fondos
        sr_A, ir_A = 2000.0, 2000.0
        S0_A_base, I0_A_base = 400.0, 800.0 # r_autarky_A = 400/4000 = 10%
        
        # País B (Pequeño): Representa el ~10% del mercado
        sr_B, ir_B = 200.0, 200.0
        S0_B_base, I0_B_base = 40.0, 80.0 # r_autarky_B = 40/400 = 10%
        
        S0_A, I0_A = S0_A_base, I0_A_base
        S0_B, I0_B = S0_B_base, I0_B_base

        # Aplicación de Shocks
        if "1." in escenario_2p: I0_A += 220.0 # Boom en el Grande (+220 unidades de demanda)
        elif "2." in escenario_2p: I0_B += 110.0 # Boom enorme en el Pequeño (relativo a su tamaño)
        elif "3." in escenario_2p: S0_A -= 220.0 # Déficit en el Grande
        elif "4." in escenario_2p: S0_B -= 110.0 # Déficit en el Pequeño

        # Equilibrio Global: S_A + S_B = I_A + I_B -> Despeje de r*
        r_star = ((I0_A + I0_B) - (S0_A + S0_B)) / (sr_A + ir_A + sr_B + ir_B)

        # Resultados por país
        S_A_eq, I_A_eq = S0_A + sr_A * r_star, I0_A - ir_A * r_star
        S_B_eq, I_B_eq = S0_B + sr_B * r_star, I0_B - ir_B * r_star
        CC_A, CC_B = S_A_eq - I_A_eq, S_B_eq - I_B_eq

        # Vectores para gráficos
        r_vec = np.linspace(0.0, 0.25, 200)
        SA_curva, IA_curva = S0_A + sr_A * r_vec, I0_A - ir_A * r_vec
        SB_curva, IB_curva = S0_B + sr_B * r_vec, I0_B - ir_B * r_vec

        # DASHBOARD M2
        st.subheader("📋 Equilibrio Global y Cuentas Corrientes")
        m1, m2, m3 = st.columns(3)
        m1.metric("Tasa de Interés Mundial (r*)", f"{r_star*100:.1f}%")
        m2.metric("Cuenta Corriente País GRANDE", f"{CC_A:.1f}", "Déficit" if CC_A < -0.1 else ("Superávit" if CC_A > 0.1 else "Eq."), delta_color="inverse" if CC_A < 0 else "normal")
        m3.metric("Cuenta Corriente País PEQUEÑO", f"{CC_B:.1f}", "Déficit" if CC_B < -0.1 else ("Superávit" if CC_B > 0.1 else "Eq."), delta_color="inverse" if CC_B < 0 else "normal")

        col_a, col_b = st.columns(2)

        # GRÁFICO PAÍS A (GRANDE)
        with col_a:
            fig_a = go.Figure()
            if "0." not in escenario_2p and ("GRANDE" in escenario_2p):
                fig_a.add_trace(go.Scatter(x=S0_A_base + sr_A * r_vec, y=r_vec, name="S₀ (Inicial)", line=dict(color=C_GREEN, width=1.5, dash='dot')))
                fig_a.add_trace(go.Scatter(x=I0_A_base - ir_A * r_vec, y=r_vec, name="I₀ (Inicial)", line=dict(color=C_BLUE, width=1.5, dash='dot')))
            
            fig_a.add_trace(go.Scatter(x=SA_curva, y=r_vec, name="S_A (Ahorro)", line=dict(color=C_GREEN, width=3)))
            fig_a.add_trace(go.Scatter(x=IA_curva, y=r_vec, name="I_A (Inversión)", line=dict(color=C_BLUE, width=3)))
            fig_a.add_hline(y=r_star, line_dash="dash", line_color=COLOR_TEXTO, annotation_text=f"r* = {r_star*100:.1f}%", annotation_position="top left")

            if abs(CC_A) > 0.1:
                color_b = "rgba(220, 38, 38, 0.2)" if CC_A < 0 else "rgba(21, 128, 61, 0.2)"
                fig_a.add_shape(type="rect", x0=min(S_A_eq, I_A_eq), x1=max(S_A_eq, I_A_eq), y0=r_star-0.005, y1=r_star+0.005, fillcolor=color_b, line_width=0)
                fig_a.add_annotation(x=(S_A_eq+I_A_eq)/2, y=r_star+0.015, text="Déficit CC" if CC_A < 0 else "Superávit CC", showarrow=False, font=dict(color=COLOR_TEXTO, size=11))

            fig_a.update_layout(
                title=dict(text="Mercado País GRANDE (90% del mundo)", font=dict(color=COLOR_TEXTO, size=16)),
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=dict(color=COLOR_TEXTO, family="Arial", size=14),
                legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.9)", bordercolor="black", borderwidth=1), 
                margin=dict(l=20, r=20, t=40, b=20), height=450
            )
            fig_a.update_xaxes(title_text="Fondos (S_A, I_A)", range=[200, 1100], **eje_formato)
            fig_a.update_yaxes(title_text="Tasa de Interés Mundial (r*)", range=[0, 0.20], tickformat=".0%", **eje_formato)
            st.plotly_chart(fig_a, use_container_width=True, theme=None)

        # GRÁFICO PAÍS B (PEQUEÑO)
        with col_b:
            fig_b = go.Figure()
            if "0." not in escenario_2p and ("PEQUEÑO" in escenario_2p):
                fig_b.add_trace(go.Scatter(x=S0_B_base + sr_B * r_vec, y=r_vec, name="S₀ (Inicial)", line=dict(color=C_GREEN, width=1.5, dash='dot')))
                fig_b.add_trace(go.Scatter(x=I0_B_base - ir_B * r_vec, y=r_vec, name="I₀ (Inicial)", line=dict(color=C_BLUE, width=1.5, dash='dot')))

            fig_b.add_trace(go.Scatter(x=SB_curva, y=r_vec, name="S_B (Ahorro)", line=dict(color=C_GREEN, width=3)))
            fig_b.add_trace(go.Scatter(x=IB_curva, y=r_vec, name="I_B (Inversión)", line=dict(color=C_BLUE, width=3)))
            fig_b.add_hline(y=r_star, line_dash="dash", line_color=COLOR_TEXTO, annotation_text=f"r* = {r_star*100:.1f}%", annotation_position="top left")

            if abs(CC_B) > 0.1:
                color_b = "rgba(220, 38, 38, 0.2)" if CC_B < 0 else "rgba(21, 128, 61, 0.2)"
                fig_b.add_shape(type="rect", x0=min(S_B_eq, I_B_eq), x1=max(S_B_eq, I_B_eq), y0=r_star-0.005, y1=r_star+0.005, fillcolor=color_b, line_width=0)
                fig_b.add_annotation(x=(S_B_eq+I_B_eq)/2, y=r_star+0.015, text="Déficit CC" if CC_B < 0 else "Superávit CC", showarrow=False, font=dict(color=COLOR_TEXTO, size=11))

            fig_b.update_layout(
                title=dict(text="Mercado País PEQUEÑO (10% del mundo)", font=dict(color=COLOR_TEXTO, size=16)),
                template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=dict(color=COLOR_TEXTO, family="Arial", size=14),
                legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.9)", bordercolor="black", borderwidth=1), 
                margin=dict(l=20, r=20, t=40, b=20), height=450
            )
            fig_b.update_xaxes(title_text="Fondos (S_B, I_B)", range=[0, 180], **eje_formato)
            fig_b.update_yaxes(title_text="Tasa de Interés Mundial (r*)", range=[0, 0.20], tickformat=".0%", **eje_formato)
            st.plotly_chart(fig_b, use_container_width=True, theme=None)

        # TEXTO PEDAGÓGICO M2 (Compacto)
        txt_2p = ""
        if "0." in escenario_2p:
            txt_2p = "Ambos países arrancan con un equilibrio interno donde la tasa autárquica de cada uno es exactamente del 10%. Al abrirse al comercio, la tasa mundial se mantiene en 10% y las Cuentas Corrientes están en perfecto equilibrio nulo."
        elif "1." in escenario_2p or "3." in escenario_2p:
            txt_2p = "🌍 **Efecto Arrastre Global:** El país Grande sufre un déficit interno de fondos (ya sea por Boom de Inversión o por Gasto Público). Como este país representa la mayor parte de la demanda mundial, **arrastra la tasa de interés global hacia arriba** (sube al 15%).\n\n"
            txt_2p += "🚢 **El ajuste en el Pequeño:** El país Pequeño no hizo absolutamente nada, pero sufre el encarecimiento del crédito. La alta tasa mundial frena su inversión local y estimula su ahorro, forzándolo a generar un **Superávit de Cuenta Corriente** que el país Grande absorberá."
        elif "2." in escenario_2p or "4." in escenario_2p:
            txt_2p = "🌍 **Insignificancia Sistémica:** El país Pequeño sufre un shock interno gigantesco. Sin embargo, al ser tan chico en el mercado global de capitales, **la tasa de interés mundial apenas se inmuta** (pasa del 10% al 11% aproximadamente).\n\n"
            txt_2p += "🚢 **Absorción Interna:** Como la tasa no sube lo suficiente para frenar la demanda, el país Pequeño absorbe todo el impacto incurriendo en un **masivo Déficit de Cuenta Corriente**. El país Grande financia este déficit sin apenas sentirlo (genera un superávit minúsculo en sus proporciones)."

        st.success(f"""### 🎓 Análisis del Ajuste Distribuido
{txt_2p}""")
