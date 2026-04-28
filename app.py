import streamlit as st
import pandas as pd
import plotly.express as px
import os


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
    st.dataframe(df_lpa)


# TAB 2

with tab2:
    st.subheader("Tabla Hallazgos")
    st.dataframe(df_hallazgos)


# TAB 3 DASHBOARD

with tab3:


    # 🔴 HALLAZGOS CRÍTICOS

    st.subheader("🚨 Hallazgos Críticos (En progreso - vencida)")

    if not df_hall_crit.empty:

        # Etiqueta en 3 líneas
        df_hall_crit["Etiqueta"] = (
            df_hall_crit["Ubicación"].astype(str) + "<br>" +
            df_hall_crit["Parte responsable"].astype(str) + "<br>" +
            df_hall_crit["Fecha de vencimiento"].astype(str)
        )

        fig_hall = px.bar(
            df_hall_crit,
            x="Etiqueta",
            y=[1]*len(df_hall_crit),
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
        st.dataframe(df_hall_crit)

    else:
        st.success("No hay hallazgos críticos")


    # 🔴 LPA CRÍTICOS

    st.subheader("📉 LPA Críticos (Sin realizar)")

    if not df_lpa_crit.empty:

        # Etiqueta en 3 líneas
        df_lpa_crit["Etiqueta"] = (
            df_lpa_crit["Ubicación"].astype(str) + "<br>" +
            df_lpa_crit["Asesor"].astype(str) + "<br>" +
            df_lpa_crit["Fecha de vencimiento"].astype(str)
        )

        fig_lpa = px.bar(
            df_lpa_crit,
            x="Etiqueta",
            y=[1]*len(df_lpa_crit),
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
        st.dataframe(df_lpa_crit)

    else:
        st.success("No hay LPA críticos")


    # EXTRA

    st.subheader("📊 Hallazgos por Ubicación")

    data_hall = df_hallazgos.groupby("Ubicación").size().reset_index(name="Cantidad")

    fig_extra = px.bar(
        data_hall,
        x="Ubicación",
        y="Cantidad",
        title="Hallazgos por Ubicación"
    )

    st.plotly_chart(fig_extra, use_container_width=True)