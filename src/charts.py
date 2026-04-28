import plotly.express as px
import plotly.express as px
import flet as ft


def get_charts(proc):
    # Gráfico 1: Barras (Hallazgos por Ubicación)
    df_bar = proc.get_stats_bar()
    fig1 = px.bar(df_bar, x='Ubicación', y='Cantidad', title="Hallazgos por Ubicación")

    # Gráfico 2: Pastel (Distribución de Estados en LPA)
    df_pie = proc.get_stats_pie()
    # Cambiamos el nombre de las columnas al renombrar para que plotly lo entienda
    df_pie.columns = ['Estado', 'Total']
    fig2 = px.pie(df_pie, values='Total', names='Estado', title="Estado de Auditorías LPA")

    # Gráfico 3: Línea (Tendencia en LPA)
    df_line = proc.get_stats_line()
    fig3 = px.line(df_line, x='Fecha de vencimiento', y='Registros', title="Tendencia de Vencimientos LPA")

    return [ft.PlotlyChart(fig1, expand=True),
            ft.PlotlyChart(fig2, expand=True),
            ft.PlotlyChart(fig3, expand=True)]