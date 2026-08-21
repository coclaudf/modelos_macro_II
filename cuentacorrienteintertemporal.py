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
        title_font=dict(color=COLOR_TEXTO, size=15, family="Arial")
    )

    # --- BARRA LATERAL ---
    st.sidebar.header("🛠️ Entorno Institucional")
    regimen = st.sidebar.radio("1. Régimen de Apertura:", [
        "A. Pequeña Economía Abierta (r dada)",
        "B. Economía Cerrada / Controles de Capital (CC=0)",
        "C. Gran Economía Abierta (Impacto en r mundial)"
    ])

    st.sidebar.subheader("⚡ Escenarios Macroeconómicos")
    st.sidebar.caption("Seleccione un shock para ver la transición desde el equilibrio inicial.")
    escenario = st.sidebar.selectbox("2. Shock Aplicado:", [
        "0. Situación Inicial (Equilibrio base)",
        "1. Auge Exportador Transitorio (Suba de Ingreso Corriente)",
        "2. Boom de Inversión ('Animal Spirits' / Mgn. Eficiencia)",
        "3. Aumento del Gasto Público Transitorio (Déficit)",
        "4. Equivalencia Ricardiana (Baja T financiada con deuda)",
        "5. Shock Externo Global (Sube r* mundial)",
        "6. Trampa de Liquidez (Colapso de Inversión)"
    ])

    # =============================================================================
    # MOTOR MATEMÁTICO DEL MODELO
    # =============================================================================
    # Funciones Base: S(r) = S0 + sr*r  |  I(r) = I0 - ir*r
    # Equilibrio autárquico inicial: r = 10%, S = 150, I = 150
    sr, ir = 500.0, 500.0
    S0_base, I0_base = 100.0, 200.0
    r_world_base = 0.10

    # Variables reactivas
    S0, I0, r_world = S0_base, I0_base, r_world_base
    show_ricardian = False

    # APLICACIÓN DE SHOCKS A LOS PARÁMETROS AUTÓNOMOS
    if escenario == "1. Auge Exportador Transitorio (Suba de Ingreso Corriente)":
        S0 = S0_base + 50.0  
    
    elif escenario == "2. Boom de Inversión ('Animal Spirits' / Mgn. Eficiencia)":
        I0 = I0_base + 50.0  
    
    elif escenario == "3. Aumento del Gasto Público Transitorio (Déficit)":
        S0 = S0_base - 50.0  
    
    elif escenario == "4. Equivalencia Ricardiana (Baja T financiada con deuda)":
        show_ricardian = True
        S0 = S0_base 
    
    elif escenario == "5. Shock Externo Global (Sube r* mundial)":
        r_world = 0.15 
    
    elif escenario == "6. Trampa de Liquidez (Colapso de Inversión)":
        I0 = I0_base - 140.0 

    # CÁLCULO DE LA TASA DE INTERÉS DE EQUILIBRIO (r_eq) SEGÚN RÉGIMEN
    r_autarky = (I0 - S0) / (sr + ir)
    ZLB_activa = False

    if regimen == "B. Economía Cerrada / Controles de Capital (CC=0)":
        r_eq = r_autarky
        if r_eq < 0.0:
            r_eq = 0.0
            ZLB_activa = True
    elif regimen == "A. Pequeña Economía Abierta (r dada)":
        r_eq = r_world
    else: 
        r_eq = r_world_base + 0.40 * (r_autarky - r_world_base)
        if escenario == "5. Shock Externo Global (Sube r* mundial)":
            r_eq = 0.15 
        if r_eq < 0.0: r_eq = 0.0

    # CÁLCULOS FINALES EN EL PUNTO DE EQUILIBRIO
    S_eq = S0 + sr * r_eq
    I_eq = I0 - ir * r_eq
    CC_eq = S_eq - I_eq

    if ZLB_activa and regimen == "B. Economía Cerrada / Controles de Capital (CC=0)":
        CC_eq = 0.0 
        S_efectivo = I_eq
    else:
        S_efectivo = S_eq

    # Vectores para trazar curvas (Rango de tasas de 0% a 25%)
    r_vec = np.linspace(0.0, 0.25, 200)
    S_curva = S0 + sr * r_vec
    I_curva = I0 - ir * r_vec
    CC_curva = S_curva - I_curva

    # =============================================================================
    # PANEL DE MÉTRICAS (DASHBOARD)
    # =============================================================================
    st.subheader("📋 Equilibrio Macroeconómico Resultante")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tasa de Interés (r)", f"{r_eq*100:.1f}%", "- ZLB Activa" if ZLB_activa else None, delta_color="off")
    m2.metric("Ahorro Nacional (S)", f"{S_efectivo:.1f}")
    m3.metric("Inversión Nacional (I)", f"{I_eq:.1f}")
    m4.metric("Cuenta Corriente (CC)", f"{CC_eq:.1f}", "Déficit" if CC_eq < -0.1 else ("Superávit" if CC_eq > 0.1 else "Equilibrio"), delta_color="inverse" if CC_eq < 0 else "normal")

    # =============================================================================
    # GENERACIÓN DE GRÁFICOS
    # =============================================================================
    col_g1, col_g2 = st.columns(2)

    # --- GRÁFICO 1: MERCADO DE FONDOS PRESTABLES (S e I) ---
    with col_g1:
        fig_si = go.Figure()

        if escenario != "0. Situación Inicial (Equilibrio base)":
            S_base_curva = S0_base + sr * r_vec
            I_base_curva = I0_base - ir * r_vec
            fig_si.add_trace(go.Scatter(x=S_base_curva, y=r_vec, name="S₀ (Ahorro Inicial)", line=dict(color=C_GREEN, width=1.5, dash='dot')))
            fig_si.add_trace(go.Scatter(x=I_base_curva, y=r_vec, name="I₀ (Inversión Inicial)", line=dict(color=C_BLUE, width=1.5, dash='dot')))

        fig_si.add_trace(go.Scatter(x=S_curva, y=r_vec, name="S₁ (Ahorro Nacional)", line=dict(color=C_GREEN, width=3)))
        fig_si.add_trace(go.Scatter(x=I_curva, y=r_vec, name="I₁ (Inversión Nacional)", line=dict(color=C_BLUE, width=3)))

        if show_ricardian:
            Spriv_curva = (S0 + 40) + sr * r_vec 
            Spub_curva = np.full(len(r_vec), -40) 
            fig_si.add_trace(go.Scatter(x=Spriv_curva, y=r_vec, name="S_priv (Ahorro Privado)", line=dict(color='#86EFAC', width=2, dash='dash')))
            fig_si.add_trace(go.Scatter(x=Spub_curva, y=r_vec, name="S_pub (Ahorro Público)", line=dict(color='#FCA5A5', width=2, dash='dash')))
            fig_si.add_annotation(x=200, y=0.20, text="S_Total no se mueve<br>(Spriv compensa Spub)", showarrow=False, font=dict(color=COLOR_TEXTO, size=12), bgcolor="#F3F4F6")

        fig_si.add_hline(y=r_eq, line_dash="dash", line_color=COLOR_TEXTO, annotation_text=f"r = {r_eq*100:.1f}%", annotation_position="top left")

        if abs(CC_eq) > 0.1 and not (ZLB_activa and regimen == "B. Economía Cerrada / Controles de Capital (CC=0)"):
            color_banda = "rgba(220, 38, 38, 0.2)" if CC_eq < 0 else "rgba(21, 128, 61, 0.2)" 
            texto_banda = "Déficit CC" if CC_eq < 0 else "Superávit CC"
            fig_si.add_shape(type="rect", x0=min(S_eq, I_eq), x1=max(S_eq, I_eq), y0=r_eq-0.005, y1=r_eq+0.005, fillcolor=color_banda, line_width=0)
            fig_si.add_annotation(x=(S_eq+I_eq)/2, y=r_eq+0.015, text=texto_banda, showarrow=False, font=dict(color=COLOR_TEXTO, size=11))

        if ZLB_activa and regimen == "B. Economía Cerrada / Controles de Capital (CC=0)":
            fig_si.add_shape(type="rect", x0=I_eq, x1=S_eq, y0=-0.005, y1=0.005, fillcolor="rgba(107, 114, 128, 0.3)", line_width=0)
            fig_si.add_annotation(x=(S_eq+I_eq)/2, y=0.015, text="Exceso de Ahorro<br>(Brecha Recesiva)", showarrow=False, font=dict(color=C_RED, size=11))

        fig_si.update_layout(
            title=dict(text="Mercado de Fondos (Ahorro e Inversión)", font=dict(color=COLOR_TEXTO, size=16)),
            template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', font=dict(color=COLOR_TEXTO, family="Arial", size=14),
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.9)", bordercolor="black", borderwidth=1), 
            margin=dict(l=20, r=20, t=40, b=20), height=450
        )
        fig_si.update_xaxes(title_text="Fondos (S, I)", range=[-50, 300], **eje_formato)
        fig_si.update_yaxes(title_text="Tasa de Interés Real (r)", range=[0, 0.25], tickformat=".0%", **eje_formato)
        st.plotly_chart(fig_si, use_container_width=True, theme=None)

    # --- GRÁFICO 2: FUNCIÓN DE CUENTA CORRIENTE ---
    with col_g2:
        fig_cc = go.Figure()

        if escenario != "0. Situación Inicial (Equilibrio base)":
            CC_base_curva = (S0_base - I0_base) + (sr + ir) * r_vec
            fig_cc.add_trace(go.Scatter(x=CC_base_curva, y=r_vec, name="CC₀ (Base)", line=dict(color=C_PURPLE, width=1.5, dash='dot')))

        fig_cc.add_trace(go.Scatter(x=CC_curva, y=r_vec, name="CC₁ (Cuenta Corriente)", line=dict(color=C_PURPLE, width=3)))

        fig_cc.add_hline(y=r_eq, line_dash="dash", line_color=COLOR_TEXTO)
        fig_cc.add_vline(x=0, line_dash="solid", line_color="black", line_width=1) 

        if not (ZLB_activa and regimen == "B. Economía Cerrada / Controles de Capital (CC=0)"):
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

    # =============================================================================
    # TEXTO PEDAGÓGICO ADAPTATIVO A MÚLTIPLES DIMENSIONES
    # =============================================================================
    
    st.success(f"### 🎓 Análisis del Escenario: {escenario.split('.')[1].strip()}")
    
    # Explicación del Régimen
    if regimen == "B. Economía Cerrada / Controles de Capital (CC=0)":
        st.write("🌍 **Régimen Institucional:** Al tener la Cuenta Corriente bloqueada (Economía Cerrada), el país no puede importar ni exportar ahorro. La tasa de interés interna ($r$) debe ajustar obligatoriamente para forzar que el Ahorro iguale a la Inversión ($S=I$).")
    elif regimen == "A. Pequeña Economía Abierta (r dada)":
        st.write("🌍 **Régimen Institucional:** Es una economía tomadora de precios. La tasa interna está anclada a la mundial ($r = r^*$). Cualquier descalce entre $S$ e $I$ se resuelve exportando fondos (Superávit) o importando capitales (Déficit).")
    else:
        st.write("🌍 **Régimen Institucional:** Al ser un país Grande (ej. EE.UU. o China), sus propios shocks internos tienen el volumen suficiente para modificar la oferta/demanda global de fondos, alterando parcialmente la tasa de interés mundial ($r^*$).")

    st.markdown("---")

    # Explicación del Shock
    if escenario == "0. Situación Inicial (Equilibrio base)":
        st.write("La economía se encuentra en su punto de equilibrio natural. Al 10% de tasa de interés, el Ahorro Nacional financia exactamente la Inversión local, resultando en un saldo de Cuenta Corriente nulo.")
        
    elif escenario == "1. Auge Exportador Transitorio (Suba de Ingreso Corriente)":
        st.write("💡 **Dinámica de Curvas:** El incremento del ingreso presente induce a las familias a ahorrar la mayor parte del excedente para suavizar consumo futuro. La curva $S$ se desplaza a la derecha, desplazando también la función de Cuenta Corriente ($CC$).")
        if "Cerrada" in regimen:
            st.write("📉 **Resultado:** Como no se pueden exportar esos capitales, la abundancia de ahorro desploma la tasa de interés interna (cae $r$) hasta que la Inversión se expande y absorbe los fondos.")
        else:
            st.write("🚢 **Resultado:** A la tasa internacional, se genera un exceso de ahorro doméstico ($S > I$). Ese excedente sale del país buscando rentabilidad, generando un **Superávit de Cuenta Corriente** (Acumulación de activos externos).")

    elif escenario == "2. Boom de Inversión ('Animal Spirits' / Mgn. Eficiencia)":
        st.write("💡 **Dinámica de Curvas:** Mejoran las expectativas de rentabilidad futura del capital. Las empresas demandan más fondos prestables, desplazando la curva de Inversión ($I$) a la derecha. Esto empuja la curva $CC$ a la izquierda.")
        if "Cerrada" in regimen:
            st.write("📈 **Resultado:** La mayor competencia por fondos empuja la tasa de interés hacia arriba ($r$ sube) para racionar el crédito y estimular más ahorro interno, manteniendo $CC=0$.")
        else:
            st.write("🚢 **Resultado:** Para financiar los nuevos proyectos sin subir drásticamente la tasa, el país recurre al ahorro externo ($I > S$). Entran flujos de capital, lo que se refleja especularmente como un **Déficit de Cuenta Corriente**.")

    elif escenario == "3. Aumento del Gasto Público Transitorio (Déficit)":
        st.write("💡 **Dinámica de Curvas:** El gobierno gasta más sin subir impuestos hoy, reduciendo el Ahorro Público. La curva de Ahorro Nacional ($S$) retrocede a la izquierda, arrastrando a la $CC$ con ella.")
        if "Abierta" in regimen:
            st.write("👯‍♂️ **Déficits Gemelos:** Es el clásico caso de libro. El déficit fiscal reduce los fondos disponibles. Para mantener la inversión doméstica, se importa ahorro del exterior, generando un **Déficit de Cuenta Corriente**.")

    elif escenario == "4. Equivalencia Ricardiana (Baja T financiada con deuda)":
        st.write("💡 **Teorema de Barro-Ricardo:** El gobierno redujo los impuestos ($T$) hoy, emitiendo deuda pública para cubrir el agujero (Cae el Ahorro Público). Sin embargo, los agentes racionales anticipan que esa deuda significa **mayores impuestos en el futuro**. Por ende, no gastan ese 'ingreso extra' de hoy, sino que lo ahorran por completo (Sube el Ahorro Privado).")
        st.write("🛡️ **Resultado:** Como podés ver en el gráfico, el salto del $S_{priv}$ compensa exactamente la caída del $S_{pub}$. La curva de Ahorro Nacional total ($S$) **queda inalterada**. La tasa de interés y la Cuenta Corriente no sufren ningún cambio. ¡Se rompe la hipótesis de déficits gemelos!")

    elif escenario == "5. Shock Externo Global (Sube r* mundial)":
        st.write("💡 **Dinámica:** Un encarecimiento del crédito en el mundo (ej. la Reserva Federal sube la tasa). **No hay desplazamientos de curvas**, sino un movimiento *a lo largo* de las mismas.")
        if "Cerrada" in regimen:
            st.write("🛡️ **Resultado:** La economía cerrada está blindada a este shock financiero externo porque su tasa se rige por factores puramente domésticos.")
        else:
            st.write("⚠️ **Ajuste Recesivo:** La alta tasa mundial frena los proyectos productivos (Cae la Inversión a lo largo de su curva) e incentiva el ahorro (Cae el Consumo a lo largo de su curva). Esta fuerte contracción interna genera un excedente de fondos que mejora forzosamente la Cuenta Corriente hacia el superávit.")

    elif escenario == "6. Trampa de Liquidez (Colapso de Inversión)":
        st.write("💡 **Dinámica de Curvas:** El peor escenario ('*Pesimismo extremo*'). La expectativa de rentabilidad colapsa y la curva de Inversión ($I$) sufre una retracción masiva a la izquierda.")
        if "Cerrada" in regimen:
            st.write("🚨 **Límite Cero (Zero Lower Bound):** Para igualar $S$ e $I$, la tasa de interés debería ser negativa. Como el límite nominal inferior es 0%, la tasa 'choca' contra el piso. En $r=0$, el Ahorro deseado supera ampliamente a la Inversión. Al no poder exportar ese ahorro ($CC=0$), la única forma de volver al equilibrio es vía **recesión**: el Ingreso Nacional caerá (desplazando a $S$ a la izquierda por empobrecimiento) hasta que se cierren las brechas. Es la cruz keynesiana en acción.")
        else:
            st.write("🚢 **La Válvula de Escape Abierta:** Al estar en una economía abierta, la 'trampa' local se desactiva. El brutal exceso de fondos (Ahorro estancado vs Inversión destruida) simplemente abandona el país buscando rendimientos a la tasa $r^*$. Esto genera una colosal salida de capitales y un consecuente **Superávit masivo de Cuenta Corriente**.")
