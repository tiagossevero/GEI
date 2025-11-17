"""
Pacote de Componentes Visuais e Insights
"""

from .visual import *
from .insights import *

__all__ = [
    # Visual
    'criar_kpi',
    'criar_grid_kpis',
    'criar_kpi_colorido',
    'criar_histograma',
    'criar_boxplot',
    'criar_grafico_barras',
    'criar_grafico_pizza',
    'criar_grafico_linha',
    'criar_grafico_dispersao',
    'criar_heatmap',
    'criar_matriz_correlacao',
    'criar_dispersao_3d',
    'criar_gauge',
    'exibir_tabela_formatada',
    'criar_grafico_rede',
    # Insights
    'gerar_insights_grupo',
    'gerar_insights_gerais',
    'calcular_correlacoes',
    'identificar_outliers',
    'testar_normalidade',
    'calcular_tendencia',
    'exibir_insights'
]
