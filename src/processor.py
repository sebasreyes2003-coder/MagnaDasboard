import pandas as pd

class QualityProcessor:
    def __init__(self, lpa_path, findings_path):
        # Cargamos los CSV
        self.df_lpa = pd.read_csv(lpa_path)
        self.df_hallazgos = pd.read_csv(findings_path)

    def get_stats_bar(self):
        # Columna correcta: 'Ubicación'
        return self.df_hallazgos.groupby('Ubicación').size().reset_index(name='Cantidad')

    def get_stats_pie(self):
        # Columna correcta: 'Estado'
        return self.df_lpa['Estado'].value_counts().reset_index()

    def get_stats_line(self):
        # Columna correcta: 'Fecha de vencimiento'
        # Convertimos a datetime para asegurar que el gráfico de línea funcione bien
        self.df_lpa['Fecha de vencimiento'] = pd.to_datetime(self.df_lpa['Fecha de vencimiento'])
        return self.df_lpa.groupby('Fecha de vencimiento').size().reset_index(name='Registros')