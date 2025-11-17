"""
Módulo de Configurações do Sistema GEI
Contém todas as configurações e constantes do sistema
"""

import streamlit as st
from typing import Dict, Any

# =============================================================================
# CONFIGURAÇÕES DE CONEXÃO COM BANCO DE DADOS
# =============================================================================

IMPALA_HOST = 'bdaworkernode02.sef.sc.gov.br'
IMPALA_PORT = 21050
DATABASE = 'gessimples'

# =============================================================================
# CONFIGURAÇÕES DE AUTENTICAÇÃO
# =============================================================================

SENHA_DASHBOARD = "tsevero654"  # ALTERE para produção

# =============================================================================
# CONFIGURAÇÕES DE CACHE
# =============================================================================

CACHE_TTL_DADOS_PRINCIPAIS = 3600  # 1 hora
CACHE_TTL_DOSSIE = 300  # 5 minutos
CACHE_TTL_ANALISES = 1800  # 30 minutos

# =============================================================================
# LIMITES DE QUERIES
# =============================================================================

LIMIT_CNPJ = 50000
LIMIT_SOCIOS = 30000
LIMIT_INCONSISTENCIAS = 1000
LIMIT_CCS = 50

# =============================================================================
# TABELAS DO BANCO DE DADOS
# =============================================================================

TABELAS_PRINCIPAIS = {
    'percent': ('gei_percent', None),
    'cnpj': ('gei_cnpj', LIMIT_CNPJ),
    'cadastro': ('gei_cadastro', LIMIT_CNPJ),
    'contador': ('gei_contador', None),
    'socios_compartilhados': ('gei_socios_compartilhados', LIMIT_SOCIOS),
    'c115_ranking': ('gei_c115_ranking_risco_grupo_economico', None),
    'funcionarios_metricas': ('gei_funcionarios_metricas_grupo', None),
    'pagamentos_metricas': ('gei_pagamentos_metricas_grupo', None),
    'c115_metricas': ('gei_c115_metricas_grupos', None),
    'ccs_metricas': ('gei_ccs_metricas_grupo', None),
    'ccs_ranking': ('gei_ccs_ranking_risco', None)
}

# =============================================================================
# CONFIGURAÇÕES DE SCORE E RISCO
# =============================================================================

# Dimensões do Score de Risco (total: 50 pontos)
DIMENSOES_SCORE = {
    'cadastro': {
        'peso': 10,
        'descricao': 'Similaridade cadastral',
        'campos': ['razao_social', 'fantasia', 'cnae', 'contador', 'endereco']
    },
    'socios': {
        'peso': 8,
        'descricao': 'Vínculos societários',
        'campos': ['socios_compartilhados', 'indice_interconexao']
    },
    'financeiro': {
        'peso': 7,
        'descricao': 'Aspectos financeiros',
        'campos': ['receita_maxima', 'acima_limite_sn']
    },
    'c115': {
        'peso': 5,
        'descricao': 'Convênio 115',
        'campos': ['indice_risco_c115', 'nivel_risco_c115']
    },
    'indicios': {
        'peso': 5,
        'descricao': 'Indícios fiscais',
        'campos': ['total_indicios', 'indice_risco_indicios']
    },
    'ccs': {
        'peso': 5,
        'descricao': 'Contas compartilhadas',
        'campos': ['contas_compartilhadas', 'indice_risco_ccs']
    },
    'nfe': {
        'peso': 5,
        'descricao': 'Inconsistências NFe',
        'campos': ['score_inconsistencias_nfe']
    },
    'pagamentos': {
        'peso': 3,
        'descricao': 'Meios de pagamento',
        'campos': ['indice_risco_pagamentos']
    },
    'funcionarios': {
        'peso': 2,
        'descricao': 'Proporção funcionários',
        'campos': ['indice_risco_fat_func']
    }
}

# Classificação de Risco
NIVEIS_RISCO = {
    'CRÍTICO': {'min': 80, 'max': 100, 'cor': '#d32f2f', 'valor_num': 3},
    'ALTO': {'min': 60, 'max': 79.99, 'cor': '#f57c00', 'valor_num': 2},
    'MÉDIO': {'min': 40, 'max': 59.99, 'cor': '#fbc02d', 'valor_num': 1},
    'BAIXO': {'min': 0, 'max': 39.99, 'cor': '#388e3c', 'valor_num': 0}
}

# =============================================================================
# CONFIGURAÇÕES DE MACHINE LEARNING
# =============================================================================

ML_FEATURES = [
    'qtd_cnpjs',
    'razao_social_identica', 'fantasia_identica', 'cnae_identico',
    'contador_identico', 'endereco_identico',
    'socios_compartilhados', 'indice_interconexao', 'perc_cnpjs_com_socios',
    'receita_maxima', 'acima_limite_sn',
    'indice_risco_c115', 'nivel_risco_c115_num',
    'total_indicios', 'indice_risco_indicios',
    'contas_compartilhadas', 'indice_risco_ccs', 'nivel_risco_ccs_num',
    'score_inconsistencias_nfe',
    'indice_risco_pagamentos', 'indice_risco_fat_func'
]

ML_ALGORITHMS = {
    'kmeans': {
        'nome': 'K-Means',
        'descricao': 'Agrupamento baseado em centróides',
        'params': {'n_clusters': [2, 3, 4, 5]}
    },
    'dbscan': {
        'nome': 'DBSCAN',
        'descricao': 'Agrupamento baseado em densidade',
        'params': {'eps': [0.5, 1.0, 1.5], 'min_samples': [3, 5, 10]}
    },
    'isolation_forest': {
        'nome': 'Isolation Forest',
        'descricao': 'Detecção de anomalias',
        'params': {'contamination': [0.1, 0.2, 0.3]}
    }
}

# =============================================================================
# CONFIGURAÇÕES DE VISUALIZAÇÃO
# =============================================================================

# Cores do tema
CORES = {
    'primaria': '#1f77b4',
    'secundaria': '#ff7f0e',
    'sucesso': '#2ca02c',
    'perigo': '#d62728',
    'aviso': '#ff9800',
    'info': '#17a2b8',
    'neutro': '#7f7f7f'
}

# Paletas de cores para gráficos
PALETAS = {
    'risco': ['#388e3c', '#fbc02d', '#f57c00', '#d32f2f'],  # Verde -> Vermelho
    'divergente': ['#d32f2f', '#f57c00', '#fbc02d', '#388e3c'],  # Vermelho -> Verde
    'categorica': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
    'sequencial': ['#084594', '#2171b5', '#4292c6', '#6baed6', '#9ecae1', '#c6dbef']
}

# Configurações de gráficos Plotly
PLOTLY_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'gei_grafico',
        'height': 800,
        'width': 1200,
        'scale': 2
    }
}

PLOTLY_LAYOUT = {
    'template': 'plotly_white',
    'font': {'family': 'Arial, sans-serif', 'size': 12},
    'hovermode': 'closest',
    'margin': {'l': 50, 'r': 50, 't': 80, 'b': 50}
}

# =============================================================================
# TIPOS DE INDÍCIOS FISCAIS
# =============================================================================

TIPOS_INDICIOS = {
    'cliente_identico': 'Cliente Idêntico',
    'email_identico': 'E-mail Idêntico',
    'telefone_identico': 'Telefone Idêntico',
    'endereco_identico': 'Endereço Idêntico',
    'ip_identico': 'IP Idêntico',
    'contador_identico': 'Contador Idêntico',
    'socio_comum': 'Sócio em Comum',
    'cnae_identico': 'CNAE Idêntico',
    'fornecedor_identico': 'Fornecedor Idêntico',
    'data_abertura_proxima': 'Datas de Abertura Próximas'
}

# =============================================================================
# CONFIGURAÇÕES DE RELATÓRIOS
# =============================================================================

PDF_CONFIG = {
    'pagesize': 'A4',
    'margin': 50,
    'title_font_size': 16,
    'header_font_size': 14,
    'body_font_size': 10,
    'table_font_size': 8
}

EXCEL_CONFIG = {
    'engine': 'openpyxl',
    'freeze_panes': (1, 0),
    'column_width': 15
}

# =============================================================================
# MENSAGENS E TEXTOS
# =============================================================================

MENSAGENS = {
    'erro_conexao': "❌ Erro ao conectar ao banco de dados. Verifique as credenciais.",
    'erro_query': "❌ Erro ao executar consulta no banco de dados.",
    'sem_dados': "⚠️ Nenhum dado encontrado para os filtros selecionados.",
    'carregando': "⏳ Carregando dados...",
    'processando': "⏳ Processando análise...",
    'sucesso': "✅ Operação concluída com sucesso!",
    'aviso_limite': "⚠️ Resultados limitados. Use filtros para refinar a busca."
}

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_credentials() -> Dict[str, str]:
    """Obtém credenciais do Impala do secrets.toml"""
    try:
        return {
            'user': st.secrets["impala_credentials"]["user"],
            'password': st.secrets["impala_credentials"]["password"]
        }
    except Exception as e:
        st.error("Configure as credenciais no arquivo .streamlit/secrets.toml")
        st.stop()

def classificar_risco(score: float) -> Dict[str, Any]:
    """Classifica o nível de risco baseado no score"""
    for nivel, config in NIVEIS_RISCO.items():
        if config['min'] <= score <= config['max']:
            return {
                'nivel': nivel,
                'cor': config['cor'],
                'valor_num': config['valor_num']
            }
    return {
        'nivel': 'INDETERMINADO',
        'cor': '#999999',
        'valor_num': -1
    }

def formatar_moeda(valor: float) -> str:
    """Formata valor como moeda brasileira"""
    if pd.isna(valor) or valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

def formatar_numero(valor: float, casas_decimais: int = 0) -> str:
    """Formata número com separadores de milhares"""
    if pd.isna(valor) or valor is None:
        return "0"
    if casas_decimais > 0:
        return f"{valor:,.{casas_decimais}f}".replace(',', '_').replace('.', ',').replace('_', '.')
    return f"{int(valor):,}".replace(',', '.')

def formatar_percentual(valor: float, casas_decimais: int = 2) -> str:
    """Formata valor como percentual"""
    if pd.isna(valor) or valor is None:
        return "0,00%"
    return f"{valor:.{casas_decimais}f}%".replace('.', ',')

# Importações necessárias
import pandas as pd
import numpy as np
