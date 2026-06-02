
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


# CONVERSIÓN DE FECHAS PARA FILTRADO
# Diccionario para homologar los meses en español al formato estándar de pandas
meses_es = {
    'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 
    'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug', 
    'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
}

def formatear_fecha(df_col):
    # Reemplaza los meses en español por inglés para que pd.to_datetime no falle
    fecha_aux = df_col.astype(str).str.lower()
    for es, en in meses_es.items():
        fecha_aux = fecha_aux.str.replace(es, en, regex=False)
    return pd.to_datetime(fecha_aux, format='%d %b %Y', errors='coerce').dt.date

# Creamos columnas datetime ocultas solo para el comportamiento del filtro
df_lpa['Fecha_DT'] = formatear_fecha(df_lpa['Fecha de vencimiento'])
df_hallazgos['Fecha_DT'] = formatear_fecha(df_hallazgos['Fecha de vencimiento'])


# KPI

total = len(df_lpa)
completados = df_lpa['Estado'].str.contains("Completada", case=False, na=False).sum()
cumplimiento = (completados / total) * 100 if total > 0 else 0

st.metric("Cumplimiento (%)", f"{cumplimiento:.2f}%")


# FILTROS CORRECTOS


# 🔴 LPA → SOLO "Sin realizar"
df_lpa_crit = df_lpa[
    df_lpa['Estado'].str.contains("Sin realizar", case=False, na=False)
].copy()

# 🔴 Hallazgos → SOLO "En progreso - vencida"
df_hall_crit = df_hallazgos[
    df_hallazgos['Estado'].str.contains("En progreso - vencida", case=False, na=False)
].copy()


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
    
    # Obtener las fechas mínimas y máximas disponibles entre ambos archivos para inicializar el filtro
    fechas_todas = pd.concat([df_lpa['Fecha_DT'].dropna(), df_hallazgos['Fecha_DT'].dropna()])
    min_date = fechas_todas.min() if not fechas_todas.empty else pd.Timestamp.now().date()
    max_date = fechas_todas.max() if not fechas_todas.empty else pd.Timestamp.now().date()

    # Componente visual para seleccionar el rango
    rango_fechas = st.date_input(
        "Selecciona el período de vencimiento:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Validar que el usuario haya seleccionado ambas fechas (Inicio y Fin) antes de filtrar
    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        start_date, end_date = rango_fechas
        
        # Aplicamos el filtro de fecha a los dataframes que usan las gráficas
        df_hall_crit_fil = df_hall_crit[(df_hall_crit['Fecha_DT'] >= start_date) & (df_hall_crit['Fecha_DT'] <= end_date)]
        df_lpa_crit_fil = df_lpa_crit[(df_lpa_crit['Fecha_DT'] >= start_date) & (df_lpa_crit['Fecha_DT'] <= end_date)]
        df_hallazgos_fil = df_hallazgos[(df_hallazgos['Fecha_DT'] >= start_date) & (df_hallazgos['Fecha_DT'] <= end_date)]
    else:
        # Si está incompleto el rango, mostramos los datos completos provisionalmente
        df_hall_crit_fil = df_hall_crit
        df_lpa_crit_fil = df_lpa_crit
        df_hallazgos_fil = df_hallazgos


    # 🔴 HALLAZGOS CRÍTICOS

    st.subheader("🚨 Hallazgos Críticos (En progreso - vencida)")

    if not df_hall_crit_fil.empty:

        # Etiqueta en 3 líneas
        df_hall_crit_fil["Etiqueta"] = (
            df_hall_crit_fil["Ubicación"].astype(str) + "<br>" +
            df_hall_crit_fil["Parte responsable"].astype(str) + "<br>" +
            df_hall_crit_fil["Fecha de vencimiento"].astype(str)
        )

        fig_hall = px.bar(
            df_hall_crit_fil,
            x="Etiqueta",
            y=[1]*len(df_hall_crit_fil),
            title="🔴 HALLAZGOS CRÍTICOS"
        )

        fig_hall.update_traces(
            marker_color="red",
            hovertemplate=(
                "Ubicación: %{x}<br>" +
                "Estado: En progreso - vencida<extra></extra>"
            )
        )

        fig_hall.update_layout(
            xaxis_title="",
            yaxis_title="Cantidad",
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(tickangle=0, tickfont=dict(size=10)),
            yaxis=dict(gridcolor="lightgray"),
            height=500
        )

        st.plotly_chart(fig_hall, use_container_width=True)
        st.dataframe(df_hall_crit_fil.drop(columns=['Fecha_DT', 'Etiqueta']))

    else:
        st.success("No hay hallazgos críticos en el rango seleccionado")


    # 🔴 LPA CRÍTICOS

    st.subheader("📉 LPA Críticos (Sin realizar)")

    if not df_lpa_crit_fil.empty:

        # Etiqueta en 3 líneas
        df_lpa_crit_fil["Etiqueta"] = (
            df_lpa_crit_fil["Ubicación"].astype(str) + "<br>" +
            df_lpa_crit_fil["Asesor"].astype(str) + "<br>" +
            df_lpa_crit_fil["Fecha de vencimiento"].astype(str)
        )

        fig_lpa = px.bar(
            df_lpa_crit_fil,
            x="Etiqueta",
            y=[1]*len(df_lpa_crit_fil),
            title="🔴 LPA CRÍTICOS - SIN REALIZAR"
        )

        fig_lpa.update_traces(
            marker_color="red",
            hovertemplate=(
                "Ubicación: %{x}<br>" +
                "Estado: Sin realizar<extra></extra>"
            )
        )

        fig_lpa.update_layout(
            xaxis_title="",
            yaxis_title="Cantidad",
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(tickangle=0, tickfont=dict(size=10)),
            yaxis=dict(gridcolor="lightgray"),
            height=500
        )

        st.plotly_chart(fig_lpa, use_container_width=True)
        st.dataframe(df_lpa_crit_fil.drop(columns=['Fecha_DT', 'Etiqueta']))

    else:
        st.success("No hay LPA críticos en el rango seleccionado")


    # EXTRA

    st.subheader("📊 Hallazgos por Ubicación")

    if not df_hallazgos_fil.empty:
        data_hall = df_hallazgos_fil.groupby("Ubicación").size().reset_index(name="Cantidad")

        fig_extra = px.bar(
            data_hall,
            x="Ubicación",
            y="Cantidad",
            title="Hallazgos por Ubicación"
        )

        st.plotly_chart(fig_extra, use_container_width=True)
    else:
        st.info("No hay datos de ubicación para el rango seleccionado")
