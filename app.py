
import plotly.express as px
import os
import streamlit as st
import pandas as pd


# CONFIG

st.set_page_config(page_title="Dashboard Magna", layout="wide")
st.title("📊 Dashboard de Calidad Magna")


# RUTAS

base_path = os.path.dirname(os.path.abspath(__file__))
lpa_path = os.path.join(base_path, "data", "lpa.csv")
hallazgos_path = os.path.join(base_path, "data", "hallazgos.csv")


# CARGA

df_lpa = pd.read_csv(lpa_path)
df_hallazgos = pd.read_csv(hallazgos_path)


# CONVERSIÓN DE FECHAS FLEXIBLE (Soporta AAAA-MM-DD y DD mes AAAA)
meses_es = {
    'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 
    'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug', 
    'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
}

def formatear_fecha(df_col):
    fechas_transformadas = pd.to_datetime(df_col, errors='coerce')
    vacias = fechas_transformadas.isna()
    if vacias.any():
        fecha_aux = df_col[vacias].astype(str).str.lower()
        for es, en in meses_es.items():
            fecha_aux = fecha_aux.str.replace(es, en, regex=False)
        fechas_transformadas[vacias] = pd.to_datetime(fecha_aux, format='%d %b %Y', errors='coerce')
    return fechas_transformadas

# Creamos columnas datetime ocultas solo para el comportamiento del filtro
df_lpa['Fecha_DT'] = formatear_fecha(df_lpa['Fecha de vencimiento'])
df_hallazgos['Fecha_DT'] = formatear_fecha(df_hallazgos['Fecha de vencimiento'])


# KPI

total = len(df_lpa)
completados = df_lpa['Estado'].str.contains("Completada", case=False, na=False).sum()
cumplimiento = (completados / total) * 100 if total > 0 else 0

st.metric("Cumplimiento (%)", f"{cumplimiento:.2f}%")


# FILTROS CORRECTOS POR ESTADO (DataFrames Base)

# 🔴 LPA
df_lpa_sin_realizar = df_lpa[df_lpa['Estado'].str.contains("Sin realizar", case=False, na=False)].copy()
df_lpa_vencida = df_lpa[df_lpa['Estado'].str.contains("En progreso - vencida", case=False, na=False)].copy()

# 🔴 Hallazgos
df_hall_vencida = df_hallazgos[df_hallazgos['Estado'].str.contains("En progreso - vencida", case=False, na=False)].copy()
df_hall_a_tiempo = df_hallazgos[df_hallazgos['Estado'].str.contains("En progreso - a tiempo", case=False, na=False)].copy()


# TABS

tab1, tab2, tab3 = st.tabs(["📋 LPA", "🚨 Hallazgos", "📊 Dashboard"])


# TAB 1

with tab1:
    st.subheader("Tabla LPA")
    st.dataframe(df_lpa.drop(columns=['Fecha_DT']))


# TAB 2

with tab2:
    st.subheader("Tabla Hallazgos")
    st.dataframe(df_hallazgos.drop(columns=['Fecha_DT']))


# TAB 3 DASHBOARD

with tab3:

    # --- SECCIÓN DE FILTRO DE FECHAS ---
    st.subheader("📅 Filtrar Dashboard por Rango de Fechas")
    
    fechas_todas = pd.concat([df_lpa['Fecha_DT'].dropna(), df_hallazgos['Fecha_DT'].dropna()])
    min_date = fechas_todas.min().date() if not fechas_todas.empty else pd.Timestamp.now().date()
    max_date = fechas_todas.max().date() if not fechas_todas.empty else pd.Timestamp.now().date()

    rango_fechas = st.date_input(
        "Selecciona el período de vencimiento:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        start_date = pd.Timestamp(rango_fechas[0])
        end_date = pd.Timestamp(rango_fechas[1])
        
        # Aplicación de filtros por rango de fecha seleccionado
        df_lpa_sr_fil = df_lpa_sin_realizar[(df_lpa_sin_realizar['Fecha_DT'] >= start_date) & (df_lpa_sin_realizar['Fecha_DT'] <= end_date)]
        df_lpa_ven_fil = df_lpa_vencida[(df_lpa_vencida['Fecha_DT'] >= start_date) & (df_lpa_vencida['Fecha_DT'] <= end_date)]
        
        df_hall_ven_fil = df_hall_vencida[(df_hall_vencida['Fecha_DT'] >= start_date) & (df_hall_vencida['Fecha_DT'] <= end_date)]
        df_hall_at_fil = df_hall_a_tiempo[(df_hall_a_tiempo['Fecha_DT'] >= start_date) & (df_hall_a_tiempo['Fecha_DT'] <= end_date)]
        
        df_hallazgos_fil = df_hallazgos[(df_hallazgos['Fecha_DT'] >= start_date) & (df_hallazgos['Fecha_DT'] <= end_date)]
        df_lpa_fil = df_lpa[(df_lpa['Fecha_DT'] >= start_date) & (df_lpa['Fecha_DT'] <= end_date)]
    else:
        df_lpa_sr_fil = df_lpa_sin_realizar
        df_lpa_ven_fil = df_lpa_vencida
        df_hall_ven_fil = df_hall_vencida
        df_hall_at_fil = df_hall_a_tiempo
        df_hallazgos_fil = df_hallazgos
        df_lpa_fil = df_lpa


    # =========================================================
    # 🚨 SECCIÓN 1: SEGUIMIENTO DE HALLAZGOS
    # =========================================================
    st.markdown("---")
    st.header("🚨 Análisis de Hallazgos")

    # Gráfico 1: Hallazgos Críticos (En progreso - Vencida)
    st.subheader("🔴 Hallazgos Críticos (En progreso - vencida)")
    if not df_hall_ven_fil.empty:
        df_hall_ven_fil["Etiqueta"] = (
            df_hall_ven_fil["Ubicación"].astype(str) + "<br>" +
            df_hall_ven_fil["Parte responsable"].astype(str) + "<br>" +
            df_hall_ven_fil["Fecha de vencimiento"].astype(str)
        )
        fig_hall_ven = px.bar(df_hall_ven_fil, x="Etiqueta", y=[1]*len(df_hall_ven_fil), title="🔴 VENCIDAS")
        fig_hall_ven.update_traces(marker_color="red", hovertemplate="Ubicación: %{x}<br>Estado: Vencida<extra></extra>")
        fig_hall_ven.update_layout(xaxis_title="", yaxis_title="Cantidad", plot_bgcolor="white", paper_bgcolor="white", yaxis=dict(gridcolor="lightgray"), height=400)
        st.plotly_chart(fig_hall_ven, use_container_width=True)
    else:
        st.success("No hay hallazgos vencidos en el rango seleccionado")

    # Gráfico 2: Hallazgos A Tiempo (En progreso - A tiempo)
    st.subheader("🟡 Hallazgos de Atención Obligatoria (En progreso - a tiempo)")
    if not df_hall_at_fil.empty:
        df_hall_at_fil["Etiqueta"] = (
            df_hall_at_fil["Ubicación"].astype(str) + "<br>" +
            df_hall_at_fil["Parte responsable"].astype(str) + "<br>" +
            df_hall_at_fil["Fecha de vencimiento"].astype(str)
        )
        fig_hall_at = px.bar(df_hall_at_fil, x="Etiqueta", y=[1]*len(df_hall_at_fil), title="🟡 EN PROGRESO - A TIEMPO")
        fig_hall_at.update_traces(marker_color="orange", hovertemplate="Ubicación: %{x}<br>Estado: A tiempo<extra></extra>")
        fig_hall_at.update_layout(xaxis_title="", yaxis_title="Cantidad", plot_bgcolor="white", paper_bgcolor="white", yaxis=dict(gridcolor="lightgray"), height=400)
        st.plotly_chart(fig_hall_at, use_container_width=True)
    else:
        st.info("No hay hallazgos activos 'A tiempo' en este rango")


    # =========================================================
    # 📉 SECCIÓN 2: SEGUIMIENTO DE LPA
    # =========================================================
    st.markdown("---")
    st.header("📉 Análisis de Auditorías LPA")

    # Gráfico 1: LPA Críticos (Sin realizar)
    st.subheader("🔴 LPA Críticos (Sin realizar)")
    if not df_lpa_sr_fil.empty:
        df_lpa_sr_fil["Etiqueta"] = (
            df_lpa_sr_fil["Ubicación"].astype(str) + "<br>" +
            df_lpa_sr_fil["Asesor"].astype(str) + "<br>" +
            df_lpa_sr_fil["Fecha de vencimiento"].astype(str)
        )
        fig_lpa_sr = px.bar(df_lpa_sr_fil, x="Etiqueta", y=[1]*len(df_lpa_sr_fil), title="🔴 SIN REALIZAR")
        fig_lpa_sr.update_traces(marker_color="crimson", hovertemplate="Ubicación: %{x}<br>Estado: Sin realizar<extra></extra>")
        fig_lpa_sr.update_layout(xaxis_title="", yaxis_title="Cantidad", plot_bgcolor="white", paper_bgcolor="white", yaxis=dict(gridcolor="lightgray"), height=400)
        st.plotly_chart(fig_lpa_sr, use_container_width=True)
    else:
        st.success("No hay auditorías en estatus 'Sin realizar'")

    # Gráfico 2: LPA En progreso - vencida
    st.subheader("📉 LPA Retrasadas (En progreso - vencida)")
    if not df_lpa_ven_fil.empty:
        df_lpa_ven_fil["Etiqueta"] = (
            df_lpa_ven_fil["Ubicación"].astype(str) + "<br>" +
            df_lpa_ven_fil["Asesor"].astype(str) + "<br>" +
            df_lpa_ven_fil["Fecha de vencimiento"].astype(str)
        )
        fig_lpa_ven = px.bar(df_lpa_ven_fil, x="Etiqueta", y=[1]*len(df_lpa_ven_fil), title="🔴 EN PROGRESO - VENCIDA")
        fig_lpa_ven.update_traces(marker_color="darkred", hovertemplate="Ubicación: %{x}<br>Estado: Vencida<extra></extra>")
        fig_lpa_ven.update_layout(xaxis_title="", yaxis_title="Cantidad", plot_bgcolor="white", paper_bgcolor="white", yaxis=dict(gridcolor="lightgray"), height=400)
        st.plotly_chart(fig_lpa_ven, use_container_width=True)
    else:
        st.success("No hay auditorías vencidas en proceso")


    # =========================================================
    # 📊 SECCIÓN 3: UBICACIONES Y PASTELES GLOBALES
    # =========================================================
    st.markdown("---")
    st.header("🏢 Distribución y Cumplimiento de Objetivos")

    # Histograma por ubicaciones
    st.subheader("📊 Cantidad de Hallazgos por Ubicación")
    if not df_hallazgos_fil.empty:
        data_hall = df_hallazgos_fil.groupby("Ubicación").size().reset_index(name="Cantidad")
        fig_extra = px.bar(data_hall, x="Ubicación", y="Cantidad", title="Hallazgos totales por Área")
        fig_extra.update_traces(marker_color="#3366cc")
        st.plotly_chart(fig_extra, use_container_width=True)
    else:
        st.info("Sin registros de ubicación en este rango")

    # Distribución en Gráficas de Pastel (Completadas A Tiempo vs Críticas/Otras)
    st.subheader("🍕 Balance de Efectividad de Calidad")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Distribución General de Hallazgos")
        if not df_hallazgos_fil.empty:
            # Categorizamos los estados para simplificar el pastel de cara a calidad
            def categorizar_hall(estado):
                est = str(estado).lower()
                if "completada - a tiempo" in est: return "🟢 Completadas a tiempo"
                elif "vencida" in est: return "🔴 Vencidas (Crítico)"
                elif "a tiempo" in est: return "🟡 En Progreso (A tiempo)"
                return "Otros Estados"
            
            df_hallazgos_fil["Categoría Estatus"] = df_hallazgos_fil["Estado"].apply(categorizar_hall)
            data_pie_hall = df_hallazgos_fil.groupby("Categoría Estatus").size().reset_index(name="Total")
            
            fig_pie_hall = px.pie(
                data_pie_hall, values="Total", names="Categoría Estatus",
                color="Categoría Estatus",
                color_discrete_map={
                    "🟢 Completadas a tiempo": "#2ca02c",
                    "🔴 Vencidas (Crítico)": "#d62728",
                    "🟡 En Progreso (A tiempo)": "#ff7f0e",
                    "Otros Estados": "#7f7f7f"
                }
            )
            st.plotly_chart(fig_pie_hall, use_container_width=True)
        else:
            st.info("No hay datos suficientes para generar el balance de Hallazgos.")

    with col2:
        st.markdown("##### Distribución General de LPA")
        if not df_lpa_fil.empty:
            def categorizar_lpa(estado):
                est = str(estado).lower()
                if "completada - a tiempo" in est or "completada" in est: return "🟢 Completadas a tiempo"
                elif "sin realizar" in est: return "🔴 Sin Realizar (Crítico)"
                elif "vencida" in est: return "🟤 En Progreso Vencidas"
                return "Otros Estados"
            
            df_lpa_fil["Categoría Estatus"] = df_lpa_fil["Estado"].apply(categorizar_lpa)
            data_pie_lpa = df_lpa_fil.groupby("Categoría Estatus").size().reset_index(name="Total")
            
            fig_pie_lpa = px.pie(
                data_pie_lpa, values="Total", names="Categoría Estatus",
                color="Categoría Estatus",
                color_discrete_map={
                    "🟢 Completadas a tiempo": "#2ca02c",
                    "🔴 Sin Realizar (Crítico)": "#b22222",
                    "🟤 En Progreso Vencidas": "#8b4513",
                    "Otros Estados": "#7f7f7f"
                }
            )
            st.plotly_chart(fig_pie_lpa, use_container_width=True)
        else:
            st.info("No hay datos suficientes para generar el balance de LPA.")
