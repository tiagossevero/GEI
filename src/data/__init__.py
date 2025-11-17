"""
Pacote de Gerenciamento de Dados
"""

from .loader import (
    carregar_todos_os_dados,
    carregar_tabela,
    carregar_dossie_completo,
    carregar_ranking_geral,
    carregar_estatisticas_gerais,
    carregar_distribuicao_cnae,
    buscar_grupo_por_cnpj,
    buscar_cnpjs_por_grupo,
    aplicar_filtros,
    filtrar_por_score,
    filtrar_por_nivel_risco,
    agregar_por_coluna,
    calcular_estatisticas
)

__all__ = [
    'carregar_todos_os_dados',
    'carregar_tabela',
    'carregar_dossie_completo',
    'carregar_ranking_geral',
    'carregar_estatisticas_gerais',
    'carregar_distribuicao_cnae',
    'buscar_grupo_por_cnpj',
    'buscar_cnpjs_por_grupo',
    'aplicar_filtros',
    'filtrar_por_score',
    'filtrar_por_nivel_risco',
    'agregar_por_coluna',
    'calcular_estatisticas'
]
