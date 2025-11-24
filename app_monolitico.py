"""
Sistema GEI - Gestão Estratégica de Informações
Dashboard de Monitoramento Fiscal v4.0 - Versão Monolítica
Receita Estadual de Santa Catarina

ARQUIVO MONOLÍTICO - Todas as funcionalidades consolidadas
Para executar: streamlit run app_monolitico.py
"""

# =============================================================================
# IMPORTS
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import ssl
import hashlib
from io import BytesIO
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from scipy import stats

# Imports para Machine Learning
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.neighbors import LocalOutlierFactor

# Imports para exportação
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# =============================================================================
# CONFIGURAÇÕES GLOBAIS
# =============================================================================

# Configuração SSL
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Configurações de Conexão com Banco de Dados
IMPALA_HOST = 'bdaworkernode02.sef.sc.gov.br'
IMPALA_PORT = 21050
DATABASE = 'gessimples'

# Configurações de Autenticação
SENHA_DASHBOARD = "tsevero654"  # ALTERE para produção

# Configurações de Cache
CACHE_TTL_DADOS_PRINCIPAIS = 3600  # 1 hora
CACHE_TTL_DOSSIE = 300  # 5 minutos
CACHE_TTL_ANALISES = 1800  # 30 minutos

# Limites de Queries
LIMIT_CNPJ = 50000
LIMIT_SOCIOS = 30000
LIMIT_INCONSISTENCIAS = 1000
LIMIT_CCS = 50

# Tabelas do Banco de Dados
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

# Dimensões do Score de Risco
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

# Features para Machine Learning
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

# Cores do Tema
CORES = {
    'primaria': '#1f77b4',
    'secundaria': '#ff7f0e',
    'sucesso': '#2ca02c',
    'perigo': '#d62728',
    'aviso': '#ff9800',
    'info': '#17a2b8',
    'neutro': '#7f7f7f'
}

# Paletas de Cores
PALETAS = {
    'risco': ['#388e3c', '#fbc02d', '#f57c00', '#d32f2f'],
    'divergente': ['#d32f2f', '#f57c00', '#fbc02d', '#388e3c'],
    'categorica': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
    'sequencial': ['#084594', '#2171b5', '#4292c6', '#6baed6', '#9ecae1', '#c6dbef']
}

# Configurações de Gráficos Plotly
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

# Mensagens do Sistema
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
# FUNÇÕES AUXILIARES DE FORMATAÇÃO
# =============================================================================

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

# =============================================================================
# FUNÇÕES DE AUTENTICAÇÃO
# =============================================================================

def check_password() -> bool:
    """Verifica autenticação do usuário"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        _exibir_tela_login()
        return False

    return True

def _exibir_tela_login():
    """Exibe tela de login"""
    st.markdown(
        "<div style='text-align: center; padding: 50px;'>"
        "<h1>🔐 Acesso Restrito</h1>"
        "<p style='color: #666; font-size: 1.1em;'>"
        "Sistema GEI - Gestão Estratégica de Informações<br>"
        "Receita Estadual de Santa Catarina"
        "</p>"
        "</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_input = st.text_input(
            "Digite a senha:",
            type="password",
            key="pwd_input",
            placeholder="Senha de acesso"
        )

        if st.button("🔓 Entrar", use_container_width=True, type="primary"):
            if senha_input == SENHA_DASHBOARD:
                st.session_state.authenticated = True
                st.success("✅ Autenticação realizada com sucesso!")
                st.rerun()
            else:
                st.error("❌ Senha incorreta. Tente novamente.")

    st.stop()

def logout():
    """Realiza logout do usuário"""
    st.session_state.authenticated = False
    st.rerun()

# =============================================================================
# FUNÇÕES DE CONEXÃO COM BANCO DE DADOS
# =============================================================================

@st.cache_resource
def get_impala_engine():
    """Cria e retorna engine de conexão com Impala"""
    try:
        credentials = get_credentials()

        engine = create_engine(
            f'impala://{IMPALA_HOST}:{IMPALA_PORT}/{DATABASE}',
            connect_args={
                'user': credentials['user'],
                'password': credentials['password'],
                'auth_mechanism': 'LDAP',
                'use_ssl': True
            }
        )

        connection = engine.connect()
        connection.close()

        return engine

    except Exception as e:
        st.error(f"{MENSAGENS['erro_conexao']}\n\nDetalhes: {str(e)}")
        return None

def executar_query(engine, query: str, params: Optional[Dict[str, Any]] = None, show_error: bool = True) -> pd.DataFrame:
    """Executa uma query SQL e retorna DataFrame"""
    if engine is None:
        if show_error:
            st.error(MENSAGENS['erro_conexao'])
        return pd.DataFrame()

    try:
        df = pd.read_sql(query, engine, params=params)
        df.columns = [col.lower() for col in df.columns]
        return df

    except Exception as e:
        if show_error:
            st.error(f"{MENSAGENS['erro_query']}\n\nDetalhes: {str(e)}")
        return pd.DataFrame()

# =============================================================================
# QUERIES PRÉ-DEFINIDAS
# =============================================================================

class Queries:
    """Classe com queries SQL pré-definidas do sistema"""

    @staticmethod
    def get_dados_grupo(num_grupo: str) -> str:
        return f"SELECT * FROM {DATABASE}.gei_percent WHERE num_grupo = '{num_grupo}'"

    @staticmethod
    def get_cnpjs_grupo(num_grupo: str, limit: Optional[int] = None) -> str:
        limit_clause = f"LIMIT {limit}" if limit else ""
        return f"""
        SELECT g.cnpj, c.nm_razao_social, c.nm_fantasia, c.cd_cnae,
               c.nm_reg_apuracao, c.dt_constituicao_empresa, c.nm_munic as nm_municipio, c.nm_contador
        FROM {DATABASE}.gei_cnpj g
        LEFT JOIN usr_sat_ods.vw_ods_contrib c ON g.cnpj = c.nu_cnpj
        WHERE g.num_grupo = '{num_grupo}'
        {limit_clause}
        """

    @staticmethod
    def get_socios_compartilhados(num_grupo: str) -> str:
        return f"""
        SELECT cpf_socio, qtd_empresas
        FROM {DATABASE}.gei_socios_compartilhados
        WHERE num_grupo = '{num_grupo}'
        ORDER BY qtd_empresas DESC
        """

    @staticmethod
    def get_indicios(num_grupo: str) -> str:
        return f"""
        SELECT tx_descricao_indicio, cnpj, tx_descricao_complemento
        FROM {DATABASE}.gei_indicios
        WHERE num_grupo = '{num_grupo}'
        """

    @staticmethod
    def get_c115_ranking(num_grupo: str) -> str:
        return f"""
        SELECT *
        FROM {DATABASE}.gei_c115_ranking_risco_grupo_economico
        WHERE num_grupo = '{num_grupo}'
        """

    @staticmethod
    def get_ccs_compartilhadas(num_grupo: str, limit: int = 50) -> str:
        return f"""
        SELECT nr_cpf, nm_banco, cd_agencia, nr_conta, qtd_cnpjs_usando_conta,
               qtd_vinculos_ativos, status_conta
        FROM {DATABASE}.gei_ccs_cpf_compartilhado
        WHERE num_grupo = '{num_grupo}'
        ORDER BY qtd_cnpjs_usando_conta DESC
        LIMIT {limit}
        """

    @staticmethod
    def get_inconsistencias_nfe(num_grupo: str, limit: int = 1000) -> str:
        return f"""
        SELECT *
        FROM {DATABASE}.gei_nfe_completo
        WHERE grupo_emit = '{num_grupo}' OR grupo_dest = '{num_grupo}'
        LIMIT {limit}
        """

    @staticmethod
    def get_ranking_geral(limit: int = 100) -> str:
        return f"""
        SELECT num_grupo, qtd_cnpjs, score_final_percent as score_final,
               nivel_risco_final, receita_maxima, indice_risco_c115,
               total_indicios, contas_compartilhadas
        FROM {DATABASE}.gei_percent
        ORDER BY score_final_percent DESC
        LIMIT {limit}
        """

    @staticmethod
    def get_estatisticas_gerais() -> str:
        return f"""
        SELECT COUNT(DISTINCT num_grupo) as total_grupos,
               COUNT(DISTINCT num_grupo) FILTER (WHERE score_final_percent >= 80) as grupos_criticos,
               COUNT(DISTINCT num_grupo) FILTER (WHERE score_final_percent >= 60 AND score_final_percent < 80) as grupos_alto_risco,
               AVG(score_final_percent) as score_medio,
               MAX(score_final_percent) as score_maximo,
               SUM(qtd_cnpjs) as total_cnpjs,
               AVG(qtd_cnpjs) as media_cnpjs_por_grupo
        FROM {DATABASE}.gei_percent
        """

# =============================================================================
# FUNÇÕES DE CARREGAMENTO DE DADOS
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_DADOS_PRINCIPAIS, show_spinner="⏳ Carregando dados principais...")
def carregar_todos_os_dados(_engine) -> Dict[str, pd.DataFrame]:
    """Carrega todos os datasets principais do sistema GEI"""
    dados = {}

    if _engine is None:
        return dados

    with st.sidebar:
        st.write("**📊 Status do Carregamento:**")
        progress_bar = st.progress(0)
        status_text = st.empty()

        total_tabelas = len(TABELAS_PRINCIPAIS)

        for idx, (key, (tablename, limit)) in enumerate(TABELAS_PRINCIPAIS.items(), 1):
            try:
                status_text.write(f"⏳ Carregando {tablename}...")

                if limit:
                    query = f"SELECT * FROM {DATABASE}.{tablename} LIMIT {limit}"
                else:
                    query = f"SELECT * FROM {DATABASE}.{tablename}"

                df = executar_query(_engine, query, show_error=False)

                if not df.empty:
                    dados[key] = df
                    st.success(f"✅ {tablename} ({len(df):,} registros)")
                else:
                    dados[key] = pd.DataFrame()
                    st.warning(f"⚠️ {tablename} (vazio)")

            except Exception as e:
                st.warning(f"⚠️ {tablename}: {str(e)[:50]}")
                dados[key] = pd.DataFrame()

            finally:
                progress_bar.progress(idx / total_tabelas)

        status_text.success("✅ Carregamento concluído!")

    return dados

@st.cache_data(ttl=CACHE_TTL_DOSSIE, show_spinner="📋 Carregando dossiê completo...")
def carregar_dossie_completo(_engine, num_grupo: str) -> Dict[str, pd.DataFrame]:
    """Carrega todos os dados de um grupo específico para o dossiê"""
    dossie = {}
    num_grupo_str = str(num_grupo)

    # Dados Principais
    dossie['principal'] = executar_query(_engine, Queries.get_dados_grupo(num_grupo_str), show_error=False)

    # CNPJs do Grupo
    dossie['cnpjs'] = executar_query(_engine, Queries.get_cnpjs_grupo(num_grupo_str), show_error=False)

    # Sócios Compartilhados
    dossie['socios'] = executar_query(_engine, Queries.get_socios_compartilhados(num_grupo_str), show_error=False)

    # Indícios Fiscais
    dossie['indicios'] = executar_query(_engine, Queries.get_indicios(num_grupo_str), show_error=False)

    # Funcionários
    query_func = f"SELECT num_grupo, total_funcionarios, cnpjs_com_funcionarios FROM {DATABASE}.gei_funcionarios_metricas_grupo WHERE num_grupo = '{num_grupo_str}'"
    dossie['funcionarios'] = executar_query(_engine, query_func, show_error=False)

    # Pagamentos
    query_pag = f"SELECT num_grupo, valor_meios_pagamento_empresas, valor_meios_pagamento_socios FROM {DATABASE}.gei_pagamentos_metricas_grupo WHERE num_grupo = '{num_grupo_str}'"
    dossie['pagamentos'] = executar_query(_engine, query_pag, show_error=False)

    # Convênio 115
    dossie['c115'] = executar_query(_engine, Queries.get_c115_ranking(num_grupo_str), show_error=False)

    # CCS - Contas Compartilhadas
    dossie['ccs_compartilhadas'] = executar_query(_engine, Queries.get_ccs_compartilhadas(num_grupo_str), show_error=False)

    # Inconsistências NFe
    dossie['inconsistencias'] = executar_query(_engine, Queries.get_inconsistencias_nfe(num_grupo_str), show_error=False)

    return dossie

@st.cache_data(ttl=CACHE_TTL_DADOS_PRINCIPAIS)
def carregar_estatisticas_gerais(_engine) -> Dict[str, any]:
    """Carrega estatísticas gerais do sistema"""
    df = executar_query(_engine, Queries.get_estatisticas_gerais())

    if df.empty:
        return {
            'total_grupos': 0,
            'grupos_criticos': 0,
            'grupos_alto_risco': 0,
            'score_medio': 0,
            'score_maximo': 0,
            'total_cnpjs': 0,
            'media_cnpjs_por_grupo': 0
        }

    return df.iloc[0].to_dict()

@st.cache_data(ttl=CACHE_TTL_DADOS_PRINCIPAIS)
def buscar_grupo_por_cnpj(_engine, cnpj: str) -> Optional[str]:
    """Busca número do grupo a partir de um CNPJ"""
    query = f"SELECT num_grupo FROM {DATABASE}.gei_cnpj WHERE cnpj = '{cnpj}' LIMIT 1"
    df = executar_query(_engine, query, show_error=False)

    if not df.empty:
        return str(df.iloc[0]['num_grupo'])

    return None

def filtrar_por_score(df: pd.DataFrame, score_min: float, score_max: float, coluna_score: str = 'score_final') -> pd.DataFrame:
    """Filtra DataFrame por faixa de score"""
    if df.empty or coluna_score not in df.columns:
        return df
    return df[(df[coluna_score] >= score_min) & (df[coluna_score] <= score_max)]

def filtrar_por_nivel_risco(df: pd.DataFrame, niveis: list, coluna_nivel: str = 'nivel_risco_final') -> pd.DataFrame:
    """Filtra DataFrame por níveis de risco"""
    if df.empty or coluna_nivel not in df.columns or not niveis:
        return df
    return df[df[coluna_nivel].isin(niveis)]

# =============================================================================
# FUNÇÕES DE COMPONENTES VISUAIS
# =============================================================================

def criar_kpi(label: str, valor: Any, delta: Optional[str] = None, help_text: Optional[str] = None, formato: str = 'numero') -> None:
    """Cria um KPI (métrica) formatado"""
    if formato == 'moeda':
        valor_formatado = formatar_moeda(valor)
    elif formato == 'percentual':
        valor_formatado = formatar_percentual(valor)
    elif formato == 'numero':
        valor_formatado = formatar_numero(valor)
    else:
        valor_formatado = str(valor)

    st.metric(label=label, value=valor_formatado, delta=delta, help=help_text)

def criar_grid_kpis(kpis: List[Dict], colunas: int = 4) -> None:
    """Cria um grid de KPIs"""
    cols = st.columns(colunas)

    for idx, kpi in enumerate(kpis):
        col_idx = idx % colunas
        with cols[col_idx]:
            criar_kpi(
                label=kpi.get('label', ''),
                valor=kpi.get('valor', 0),
                delta=kpi.get('delta'),
                help_text=kpi.get('help'),
                formato=kpi.get('formato', 'numero')
            )

def criar_histograma(df: pd.DataFrame, coluna: str, titulo: str, bins: int = 30, cor: str = CORES['primaria'], mostrar_estatisticas: bool = True) -> go.Figure:
    """Cria um histograma"""
    fig = px.histogram(df, x=coluna, nbins=bins, title=titulo, color_discrete_sequence=[cor])

    if mostrar_estatisticas and not df[coluna].isna().all():
        media = df[coluna].mean()
        mediana = df[coluna].median()
        fig.add_vline(x=media, line_dash="dash", line_color="red", annotation_text=f"Média: {media:.2f}")
        fig.add_vline(x=mediana, line_dash="dash", line_color="green", annotation_text=f"Mediana: {mediana:.2f}")

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def criar_boxplot(df: pd.DataFrame, coluna_y: str, coluna_x: Optional[str] = None, titulo: str = "", cor: str = CORES['primaria']) -> go.Figure:
    """Cria um boxplot"""
    if coluna_x:
        fig = px.box(df, x=coluna_x, y=coluna_y, title=titulo, color_discrete_sequence=[cor])
    else:
        fig = px.box(df, y=coluna_y, title=titulo, color_discrete_sequence=[cor])

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def criar_grafico_barras(df: pd.DataFrame, x: str, y: str, titulo: str, orientacao: str = 'v', cor: Optional[str] = None, cor_coluna: Optional[str] = None, top_n: Optional[int] = None) -> go.Figure:
    """Cria um gráfico de barras"""
    df_plot = df.copy()

    if top_n:
        df_plot = df_plot.nlargest(top_n, y)

    if cor_coluna:
        fig = px.bar(df_plot, x=x, y=y, title=titulo, orientation=orientacao, color=cor_coluna, color_continuous_scale=PALETAS['sequencial'])
    else:
        cor_final = cor or CORES['primaria']
        fig = px.bar(df_plot, x=x, y=y, title=titulo, orientation=orientacao, color_discrete_sequence=[cor_final])

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def criar_grafico_pizza(df: pd.DataFrame, values: str, names: str, titulo: str, hole: float = 0, mostrar_percentual: bool = True) -> go.Figure:
    """Cria gráfico de pizza ou donut"""
    fig = px.pie(df, values=values, names=names, title=titulo, hole=hole, color_discrete_sequence=PALETAS['categorica'])

    if mostrar_percentual:
        fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def criar_grafico_linha(df: pd.DataFrame, x: str, y, titulo: str, marcadores: bool = True, area: bool = False) -> go.Figure:
    """Cria gráfico de linha"""
    if isinstance(y, str):
        y = [y]

    fig = go.Figure()

    for idx, coluna in enumerate(y):
        if area:
            fig.add_trace(go.Scatter(
                x=df[x], y=df[coluna], name=coluna,
                mode='lines+markers' if marcadores else 'lines',
                fill='tonexty' if idx > 0 else 'tozeroy',
                line=dict(color=PALETAS['categorica'][idx % len(PALETAS['categorica'])])
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df[x], y=df[coluna], name=coluna,
                mode='lines+markers' if marcadores else 'lines',
                line=dict(color=PALETAS['categorica'][idx % len(PALETAS['categorica'])])
            ))

    fig.update_layout(title=titulo, **PLOTLY_LAYOUT)
    return fig

def criar_grafico_dispersao(df: pd.DataFrame, x: str, y: str, titulo: str, cor_coluna: Optional[str] = None, tamanho_coluna: Optional[str] = None, texto_hover: Optional[str] = None, linha_tendencia: bool = False) -> go.Figure:
    """Cria gráfico de dispersão"""
    kwargs = {'data_frame': df, 'x': x, 'y': y, 'title': titulo}

    if cor_coluna:
        kwargs['color'] = cor_coluna
        kwargs['color_continuous_scale'] = PALETAS['sequencial']

    if tamanho_coluna:
        kwargs['size'] = tamanho_coluna

    if texto_hover:
        kwargs['hover_name'] = texto_hover

    if linha_tendencia:
        kwargs['trendline'] = 'ols'

    fig = px.scatter(**kwargs)
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def criar_heatmap(df: pd.DataFrame, titulo: str, anotacoes: bool = True, colorscale: str = 'RdBu_r') -> go.Figure:
    """Cria heatmap"""
    fig = go.Figure(data=go.Heatmap(
        z=df.values, x=df.columns, y=df.index, colorscale=colorscale,
        text=df.values if anotacoes else None,
        texttemplate='%{text:.2f}' if anotacoes else None,
        textfont={"size": 10}
    ))

    fig.update_layout(title=titulo, **PLOTLY_LAYOUT)
    return fig

def criar_matriz_correlacao(df: pd.DataFrame, colunas: Optional[List[str]] = None, titulo: str = "Matriz de Correlação", metodo: str = 'pearson') -> go.Figure:
    """Cria matriz de correlação"""
    if colunas is None:
        df_corr = df.select_dtypes(include=[np.number]).corr(method=metodo)
    else:
        df_corr = df[colunas].corr(method=metodo)

    return criar_heatmap(df_corr, titulo, anotacoes=True, colorscale='RdBu_r')

def criar_dispersao_3d(df: pd.DataFrame, x: str, y: str, z: str, titulo: str, cor_coluna: Optional[str] = None, tamanho: int = 5) -> go.Figure:
    """Cria gráfico de dispersão 3D"""
    if cor_coluna:
        fig = px.scatter_3d(df, x=x, y=y, z=z, color=cor_coluna, title=titulo)
    else:
        fig = px.scatter_3d(df, x=x, y=y, z=z, title=titulo)

    fig.update_traces(marker=dict(size=tamanho))
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def criar_gauge(valor: float, titulo: str, max_valor: float = 100, cor_baixo: str = "#2ca02c", cor_medio: str = "#ff9800", cor_alto: str = "#d62728") -> go.Figure:
    """Cria gráfico gauge (velocímetro)"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': titulo},
        gauge={
            'axis': {'range': [None, max_valor]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, max_valor * 0.4], 'color': cor_baixo},
                {'range': [max_valor * 0.4, max_valor * 0.8], 'color': cor_medio},
                {'range': [max_valor * 0.8, max_valor], 'color': cor_alto}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_valor * 0.9
            }
        }
    ))

    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

def exibir_tabela_formatada(df: pd.DataFrame, colunas_moeda: Optional[List[str]] = None, colunas_percentual: Optional[List[str]] = None, altura: int = 400) -> None:
    """Exibe DataFrame com formatação"""
    df_exibir = df.copy()

    if colunas_moeda:
        for col in colunas_moeda:
            if col in df_exibir.columns:
                df_exibir[col] = df_exibir[col].apply(formatar_moeda)

    if colunas_percentual:
        for col in colunas_percentual:
            if col in df_exibir.columns:
                df_exibir[col] = df_exibir[col].apply(formatar_percentual)

    st.dataframe(df_exibir, height=altura, use_container_width=True)

def criar_grafico_rede(nos: List[Dict], arestas: List[Dict], titulo: str) -> go.Figure:
    """Cria gráfico de rede (network graph)"""
    n_nos = len(nos)
    posicoes = {}
    for i, no in enumerate(nos):
        angulo = 2 * np.pi * i / n_nos
        posicoes[no['id']] = (np.cos(angulo), np.sin(angulo))

    edge_traces = []
    for aresta in arestas:
        x0, y0 = posicoes[aresta['source']]
        x1, y1 = posicoes[aresta['target']]

        edge_trace = go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode='lines',
            line=dict(width=aresta.get('value', 1), color='#888'),
            hoverinfo='none', showlegend=False
        )
        edge_traces.append(edge_trace)

    node_x = [posicoes[no['id']][0] for no in nos]
    node_y = [posicoes[no['id']][1] for no in nos]
    node_text = [no['label'] for no in nos]
    node_size = [no.get('value', 10) for no in nos]

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(size=node_size, color=CORES['primaria'], line=dict(width=2, color='white')),
        showlegend=False
    )

    fig = go.Figure(data=edge_traces + [node_trace])

    fig.update_layout(
        title=titulo,
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        **PLOTLY_LAYOUT
    )

    return fig

# =============================================================================
# FUNÇÕES DE INSIGHTS AUTOMÁTICOS
# =============================================================================

def gerar_insights_grupo(dados_grupo: pd.Series, dossie: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    """Gera insights automáticos para um grupo específico"""
    insights = []

    score = dados_grupo.get('score_final_percent', 0)
    nivel_risco = dados_grupo.get('nivel_risco_final', 'INDETERMINADO')

    if score >= 80:
        insights.append({
            'tipo': 'risco',
            'titulo': '🔴 Grupo de Risco Crítico',
            'descricao': f'Score de risco de {score:.1f}% indica necessidade de investigação urgente. Este grupo apresenta múltiplos indicadores de risco fiscal.',
            'severidade': 'critico'
        })
    elif score >= 60:
        insights.append({
            'tipo': 'risco',
            'titulo': '🟠 Grupo de Alto Risco',
            'descricao': f'Score de risco de {score:.1f}% requer monitoramento próximo e análise detalhada.',
            'severidade': 'alto'
        })

    qtd_cnpjs = dados_grupo.get('qtd_cnpjs', 0)
    if qtd_cnpjs >= 10:
        insights.append({
            'tipo': 'estrutura',
            'titulo': '🏢 Grupo Econômico Extenso',
            'descricao': f'Grupo possui {qtd_cnpjs} CNPJs, indicando estrutura organizacional complexa que pode facilitar planejamento tributário abusivo.',
            'severidade': 'medio'
        })

    socios_comp = dados_grupo.get('socios_compartilhados', 0)
    indice_interconexao = dados_grupo.get('indice_interconexao', 0)

    if socios_comp >= 5 and indice_interconexao >= 0.7:
        insights.append({
            'tipo': 'vinculos',
            'titulo': '👥 Alta Interconexão Societária',
            'descricao': f'{socios_comp} sócios compartilhados com índice de interconexão de {indice_interconexao:.1%}. Forte indício de grupo econômico coordenado.',
            'severidade': 'alto'
        })

    razao_identica = dados_grupo.get('razao_social_identica', 0)
    fantasia_identica = dados_grupo.get('fantasia_identica', 0)
    endereco_identico = dados_grupo.get('endereco_identico', 0)

    total_identicos = razao_identica + fantasia_identica + endereco_identico
    if total_identicos >= 2:
        insights.append({
            'tipo': 'cadastro',
            'titulo': '📋 Anomalia Cadastral',
            'descricao': f'Múltiplas empresas compartilham dados cadastrais idênticos (razão social: {razao_identica}, fantasia: {fantasia_identica}, endereço: {endereco_identico}). Possível confusão patrimonial.',
            'severidade': 'alto'
        })

    acima_limite = dados_grupo.get('acima_limite_sn', 0)
    receita_maxima = dados_grupo.get('receita_maxima', 0)

    if acima_limite > 0 and qtd_cnpjs >= 3:
        insights.append({
            'tipo': 'financeiro',
            'titulo': '💰 Possível Pulverização de Receita',
            'descricao': f'{acima_limite} empresas acima do limite do Simples Nacional com receita máxima de {formatar_moeda(receita_maxima)}. Indício de estratégia para manter-se no regime simplificado.',
            'severidade': 'critico'
        })

    contas_comp = dados_grupo.get('contas_compartilhadas', 0)
    if contas_comp >= 3:
        insights.append({
            'tipo': 'ccs',
            'titulo': '🏦 Contas Bancárias Compartilhadas',
            'descricao': f'{contas_comp} contas bancárias compartilhadas entre empresas. Forte indício de confusão patrimonial e movimentação financeira coordenada.',
            'severidade': 'critico'
        })

    total_indicios = dados_grupo.get('total_indicios', 0)
    if total_indicios >= 10:
        insights.append({
            'tipo': 'indicios',
            'titulo': '⚠️ Múltiplos Indícios Fiscais',
            'descricao': f'{total_indicios} indícios fiscais identificados. Padrão consistente sugere coordenação entre empresas.',
            'severidade': 'alto'
        })

    return insights

def gerar_insights_gerais(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Gera insights sobre o dataset completo"""
    insights = []

    if df.empty:
        return insights

    total_grupos = len(df)
    grupos_criticos = len(df[df['score_final_percent'] >= 80])
    grupos_alto = len(df[(df['score_final_percent'] >= 60) & (df['score_final_percent'] < 80)])
    score_medio = df['score_final_percent'].mean()

    perc_criticos = (grupos_criticos / total_grupos) * 100
    if perc_criticos > 10:
        insights.append({
            'tipo': 'distribuicao',
            'titulo': '📈 Alta Concentração de Grupos Críticos',
            'descricao': f'{perc_criticos:.1f}% dos grupos ({grupos_criticos} de {total_grupos}) apresentam risco crítico. Necessária priorização para fiscalização.',
            'severidade': 'alto'
        })

    if score_medio >= 50:
        insights.append({
            'tipo': 'score',
            'titulo': '⚠️ Score Médio Elevado',
            'descricao': f'Score médio de risco de {score_medio:.1f}% indica padrão sistêmico de irregularidades nos grupos econômicos monitorados.',
            'severidade': 'medio'
        })

    if 'receita_maxima' in df.columns:
        receita_total = df['receita_maxima'].sum()
        insights.append({
            'tipo': 'financeiro',
            'titulo': '💵 Movimentação Financeira Significativa',
            'descricao': f'Receita total agregada de {formatar_moeda(receita_total)} nos grupos monitorados.',
            'severidade': 'info'
        })

    if 'qtd_cnpjs' in df.columns:
        total_cnpjs = df['qtd_cnpjs'].sum()
        media_cnpjs = df['qtd_cnpjs'].mean()
        insights.append({
            'tipo': 'estrutura',
            'titulo': '🏢 Abrangência da Base',
            'descricao': f'{formatar_numero(total_cnpjs)} CNPJs monitorados em {total_grupos} grupos. Média de {media_cnpjs:.1f} CNPJs por grupo.',
            'severidade': 'info'
        })

    return insights

def formatar_insight_html(insight: Dict) -> str:
    """Formata insight como HTML para exibição"""
    cores_severidade = {
        'critico': '#d32f2f',
        'alto': '#f57c00',
        'medio': '#fbc02d',
        'baixo': '#388e3c',
        'info': '#1976d2'
    }

    cor = cores_severidade.get(insight['severidade'], '#666666')

    return f"""
    <div style="
        background: linear-gradient(135deg, {cor}15 0%, {cor}30 100%);
        border-left: 4px solid {cor};
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    ">
        <div style="font-size: 1.1em; font-weight: bold; color: {cor}; margin-bottom: 8px;">
            {insight['titulo']}
        </div>
        <div style="color: #333; line-height: 1.6;">
            {insight['descricao']}
        </div>
    </div>
    """

def exibir_insights(insights: List[Dict]) -> None:
    """Exibe lista de insights formatados"""
    if not insights:
        st.info("ℹ️ Nenhum insight específico identificado.")
        return

    for insight in insights:
        st.markdown(formatar_insight_html(insight), unsafe_allow_html=True)

def calcular_correlacoes(df: pd.DataFrame, colunas: List[str]) -> pd.DataFrame:
    """Calcula matriz de correlação entre colunas"""
    return df[colunas].corr(method='pearson')

def identificar_outliers(df: pd.DataFrame, coluna: str, metodo: str = 'iqr') -> Tuple[pd.DataFrame, Dict]:
    """Identifica outliers em uma coluna"""
    if metodo == 'iqr':
        Q1 = df[coluna].quantile(0.25)
        Q3 = df[coluna].quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR

        outliers = df[(df[coluna] < limite_inferior) | (df[coluna] > limite_superior)]

        stats_dict = {
            'metodo': 'IQR',
            'q1': Q1,
            'q3': Q3,
            'iqr': IQR,
            'limite_inferior': limite_inferior,
            'limite_superior': limite_superior,
            'num_outliers': len(outliers),
            'perc_outliers': (len(outliers) / len(df)) * 100
        }

    else:  # zscore
        z_scores = np.abs(stats.zscore(df[coluna].dropna()))
        outliers = df[z_scores > 3]

        stats_dict = {
            'metodo': 'Z-Score',
            'threshold': 3,
            'num_outliers': len(outliers),
            'perc_outliers': (len(outliers) / len(df)) * 100
        }

    return outliers, stats_dict

# =============================================================================
# FUNÇÕES DE MACHINE LEARNING
# =============================================================================

def preparar_dados_ml(df: pd.DataFrame, features: Optional[List[str]] = None) -> Tuple[pd.DataFrame, np.ndarray, StandardScaler]:
    """Prepara dados para Machine Learning"""
    if features is None:
        features = [f for f in ML_FEATURES if f in df.columns]

    df_clean = df[features].dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_clean)

    return df_clean, X_scaled, scaler

def aplicar_pca(X: np.ndarray, n_components: int = 2) -> Tuple[np.ndarray, PCA, float]:
    """Aplica PCA para redução de dimensionalidade"""
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X)

    variancia_explicada = sum(pca.explained_variance_ratio_) * 100

    return X_pca, pca, variancia_explicada

def kmeans_clustering(X: np.ndarray, n_clusters: int = 3, random_state: int = 42) -> Tuple[np.ndarray, KMeans, Dict[str, float]]:
    """Aplica algoritmo K-Means"""
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = model.fit_predict(X)

    metricas = {
        'silhouette': silhouette_score(X, labels),
        'davies_bouldin': davies_bouldin_score(X, labels),
        'calinski_harabasz': calinski_harabasz_score(X, labels),
        'inertia': model.inertia_,
        'n_clusters': n_clusters
    }

    return labels, model, metricas

def dbscan_clustering(X: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> Tuple[np.ndarray, DBSCAN, Dict[str, any]]:
    """Aplica algoritmo DBSCAN"""
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(X)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_outliers = list(labels).count(-1)

    metricas = {
        'n_clusters': n_clusters,
        'n_outliers': n_outliers,
        'perc_outliers': (n_outliers / len(labels)) * 100
    }

    if n_clusters > 1:
        mask = labels != -1
        if mask.sum() > 0:
            metricas['silhouette'] = silhouette_score(X[mask], labels[mask])

    return labels, model, metricas

def hierarchical_clustering(X: np.ndarray, n_clusters: int = 3, linkage: str = 'ward') -> Tuple[np.ndarray, AgglomerativeClustering, Dict[str, float]]:
    """Aplica clustering hierárquico"""
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
    labels = model.fit_predict(X)

    metricas = {
        'silhouette': silhouette_score(X, labels),
        'davies_bouldin': davies_bouldin_score(X, labels),
        'calinski_harabasz': calinski_harabasz_score(X, labels),
        'n_clusters': n_clusters
    }

    return labels, model, metricas

def isolation_forest_anomalies(X: np.ndarray, contamination: float = 0.1, random_state: int = 42) -> Tuple[np.ndarray, IsolationForest, Dict[str, any]]:
    """Detecta anomalias usando Isolation Forest"""
    model = IsolationForest(contamination=contamination, random_state=random_state)
    labels = model.fit_predict(X)

    n_anomalias = list(labels).count(-1)

    metricas = {
        'n_anomalias': n_anomalias,
        'perc_anomalias': (n_anomalias / len(labels)) * 100,
        'scores': model.score_samples(X)
    }

    return labels, model, metricas

def executar_consenso(X: np.ndarray, n_clusters: int = 3, eps: float = 0.5, contamination: float = 0.1) -> Dict[str, any]:
    """Executa múltiplos algoritmos e compara resultados (consenso)"""
    resultados = {}

    with st.spinner("Executando K-Means..."):
        labels_km, model_km, metricas_km = kmeans_clustering(X, n_clusters)
        resultados['kmeans'] = {
            'labels': labels_km,
            'model': model_km,
            'metricas': metricas_km,
            'nome': 'K-Means'
        }

    with st.spinner("Executando DBSCAN..."):
        labels_db, model_db, metricas_db = dbscan_clustering(X, eps)
        resultados['dbscan'] = {
            'labels': labels_db,
            'model': model_db,
            'metricas': metricas_db,
            'nome': 'DBSCAN'
        }

    with st.spinner("Executando Clustering Hierárquico..."):
        labels_hc, model_hc, metricas_hc = hierarchical_clustering(X, n_clusters)
        resultados['hierarchical'] = {
            'labels': labels_hc,
            'model': model_hc,
            'metricas': metricas_hc,
            'nome': 'Hierárquico'
        }

    with st.spinner("Executando Isolation Forest..."):
        labels_if, model_if, metricas_if = isolation_forest_anomalies(X, contamination)
        resultados['isolation_forest'] = {
            'labels': labels_if,
            'model': model_if,
            'metricas': metricas_if,
            'nome': 'Isolation Forest'
        }

    return resultados

def encontrar_melhor_k(X: np.ndarray, k_range: range = range(2, 11)) -> Tuple[int, Dict]:
    """Encontra melhor número de clusters usando método do cotovelo e silhouette"""
    metricas_por_k = {}

    for k in k_range:
        labels, model, metricas = kmeans_clustering(X, k)

        metricas_por_k[k] = {
            'inertia': metricas['inertia'],
            'silhouette': metricas['silhouette'],
            'davies_bouldin': metricas['davies_bouldin'],
            'calinski_harabasz': metricas['calinski_harabasz']
        }

    melhor_k = max(metricas_por_k.keys(), key=lambda k: metricas_por_k[k]['silhouette'])

    return melhor_k, metricas_por_k

def visualizar_clusters_2d(X_pca: np.ndarray, labels: np.ndarray, df_original: pd.DataFrame, titulo: str = "Visualização de Clusters") -> go.Figure:
    """Visualiza clusters em 2D após PCA"""
    df_plot = pd.DataFrame({
        'PC1': X_pca[:, 0],
        'PC2': X_pca[:, 1],
        'Cluster': labels.astype(str)
    })

    if 'num_grupo' in df_original.columns:
        df_plot['num_grupo'] = df_original['num_grupo'].values

    fig = px.scatter(
        df_plot, x='PC1', y='PC2', color='Cluster', title=titulo,
        hover_data=['num_grupo'] if 'num_grupo' in df_plot.columns else None,
        color_discrete_sequence=PALETAS['categorica']
    )

    fig.update_traces(marker=dict(size=8, line=dict(width=1, color='white')))
    fig.update_layout(template='plotly_white')

    return fig

def visualizar_clusters_3d(X_pca: np.ndarray, labels: np.ndarray, df_original: pd.DataFrame, titulo: str = "Visualização 3D de Clusters") -> go.Figure:
    """Visualiza clusters em 3D após PCA"""
    df_plot = pd.DataFrame({
        'PC1': X_pca[:, 0],
        'PC2': X_pca[:, 1],
        'PC3': X_pca[:, 2] if X_pca.shape[1] > 2 else 0,
        'Cluster': labels.astype(str)
    })

    if 'num_grupo' in df_original.columns:
        df_plot['num_grupo'] = df_original['num_grupo'].values

    fig = px.scatter_3d(
        df_plot, x='PC1', y='PC2', z='PC3', color='Cluster', title=titulo,
        hover_data=['num_grupo'] if 'num_grupo' in df_plot.columns else None,
        color_discrete_sequence=PALETAS['categorica']
    )

    fig.update_traces(marker=dict(size=5, line=dict(width=0.5, color='white')))
    fig.update_layout(template='plotly_white')

    return fig

def grafico_elbow(metricas_por_k: Dict) -> go.Figure:
    """Cria gráfico do método do cotovelo"""
    k_values = sorted(metricas_por_k.keys())
    inertias = [metricas_por_k[k]['inertia'] for k in k_values]
    silhouettes = [metricas_por_k[k]['silhouette'] for k in k_values]

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=k_values, y=inertias, name='Inércia', mode='lines+markers', yaxis='y'))
    fig.add_trace(go.Scatter(x=k_values, y=silhouettes, name='Silhouette Score', mode='lines+markers', yaxis='y2'))

    fig.update_layout(
        title='Método do Cotovelo - Seleção de K',
        xaxis=dict(title='Número de Clusters (K)'),
        yaxis=dict(title='Inércia', side='left'),
        yaxis2=dict(title='Silhouette Score', overlaying='y', side='right'),
        template='plotly_white'
    )

    return fig

def comparar_algoritmos(resultados_consenso: Dict, X_pca: np.ndarray) -> go.Figure:
    """Cria visualização comparativa de múltiplos algoritmos"""
    from plotly.subplots import make_subplots

    n_algoritmos = len(resultados_consenso)
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[res['nome'] for res in resultados_consenso.values()]
    )

    cores = PALETAS['categorica']

    for idx, (nome, resultado) in enumerate(resultados_consenso.items()):
        row = idx // 2 + 1
        col = idx % 2 + 1

        labels = resultado['labels']
        unique_labels = np.unique(labels)

        for label_idx, label in enumerate(unique_labels):
            mask = labels == label
            fig.add_trace(
                go.Scatter(
                    x=X_pca[mask, 0], y=X_pca[mask, 1],
                    mode='markers', name=f'Cluster {label}',
                    marker=dict(size=6, color=cores[label_idx % len(cores)], line=dict(width=0.5, color='white')),
                    showlegend=(idx == 0)
                ),
                row=row, col=col
            )

    fig.update_layout(
        title_text='Comparação de Algoritmos de Clustering',
        template='plotly_white',
        height=800
    )

    return fig

# =============================================================================
# FUNÇÕES DE EXPORTAÇÃO
# =============================================================================

def exportar_para_excel(dados: Dict[str, pd.DataFrame], nome_arquivo: str = "relatorio_gei") -> BytesIO:
    """Exporta múltiplas tabelas para Excel com formatação"""
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for nome_aba, df in dados.items():
            nome_aba_clean = nome_aba[:31]
            df.to_excel(writer, sheet_name=nome_aba_clean, index=False)

            workbook = writer.book
            worksheet = writer.sheets[nome_aba_clean]

            header_fill = PatternFill(start_color='1F77B4', end_color='1F77B4', fill_type='solid')
            header_font = Font(bold=True, color='FFFFFF')

            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')

            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            worksheet.freeze_panes = 'A2'

    output.seek(0)
    return output

def criar_botao_download_excel(dados: Dict[str, pd.DataFrame], nome_arquivo: str = "relatorio_gei", label: str = "📥 Download Excel") -> None:
    """Cria botão de download para Excel"""
    excel_data = exportar_para_excel(dados, nome_arquivo)

    st.download_button(
        label=label,
        data=excel_data,
        file_name=f"{nome_arquivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def exportar_para_csv(df: pd.DataFrame) -> BytesIO:
    """Exporta DataFrame para CSV"""
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig', sep=';')
    output.seek(0)
    return output

def criar_botao_download_csv(df: pd.DataFrame, nome_arquivo: str = "dados", label: str = "📥 Download CSV") -> None:
    """Cria botão de download para CSV"""
    csv_data = exportar_para_csv(df)

    st.download_button(
        label=label,
        data=csv_data,
        file_name=f"{nome_arquivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

class PDFDossie:
    """Classe para geração de dossiê em PDF"""

    def __init__(self, num_grupo: str):
        self.num_grupo = num_grupo
        self.story = []
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()

    def _configurar_estilos(self):
        self.styles.add(ParagraphStyle(
            name='TituloCustom',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1F77B4'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SubtituloCustom',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=10,
            spaceBefore=10
        ))

        self.styles.add(ParagraphStyle(
            name='NormalCustom',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))

    def adicionar_titulo_principal(self, titulo: str):
        self.story.append(Paragraph(titulo, self.styles['TituloCustom']))
        self.story.append(Spacer(1, 0.3*inch))

    def adicionar_secao(self, titulo: str):
        self.story.append(Paragraph(titulo, self.styles['SubtituloCustom']))
        self.story.append(Spacer(1, 0.1*inch))

    def adicionar_paragrafo(self, texto: str):
        self.story.append(Paragraph(texto, self.styles['NormalCustom']))

    def adicionar_tabela(self, dados: List[List], larguras: Optional[List] = None):
        if not dados:
            return

        tabela = Table(dados, colWidths=larguras)

        estilo = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F77B4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ])

        tabela.setStyle(estilo)
        self.story.append(tabela)
        self.story.append(Spacer(1, 0.2*inch))

    def adicionar_kpis(self, kpis: Dict[str, str]):
        dados = [['Métrica', 'Valor']]
        dados.extend([[k, v] for k, v in kpis.items()])
        self.adicionar_tabela(dados, larguras=[3*inch, 3*inch])

    def adicionar_quebra_pagina(self):
        self.story.append(PageBreak())

    def gerar_pdf(self, dados_grupo: pd.Series, dossie: Dict[str, pd.DataFrame]) -> BytesIO:
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)

        self.adicionar_titulo_principal(f"DOSSIÊ DO GRUPO ECONÔMICO {self.num_grupo}")

        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.adicionar_paragrafo(f"<b>Data de Geração:</b> {data_atual}")
        self.adicionar_paragrafo("<b>Sistema GEI - Gestão Estratégica de Informações</b>")
        self.adicionar_paragrafo("<b>Receita Estadual de Santa Catarina</b>")
        self.story.append(Spacer(1, 0.3*inch))

        self.adicionar_secao("1. RESUMO EXECUTIVO")

        kpis_resumo = {
            'Número do Grupo': str(self.num_grupo),
            'Quantidade de CNPJs': formatar_numero(dados_grupo.get('qtd_cnpjs', 0)),
            'Score de Risco': f"{dados_grupo.get('score_final_percent', 0):.1f}%",
            'Nível de Risco': dados_grupo.get('nivel_risco_final', 'N/A'),
            'Receita Máxima': formatar_moeda(dados_grupo.get('receita_maxima', 0))
        }

        self.adicionar_kpis(kpis_resumo)

        self.adicionar_secao("2. CNPJs DO GRUPO")

        if not dossie.get('cnpjs', pd.DataFrame()).empty:
            df_cnpjs = dossie['cnpjs'].head(20)

            dados_tabela = [['CNPJ', 'Razão Social', 'Município']]
            for _, row in df_cnpjs.iterrows():
                dados_tabela.append([
                    str(row.get('cnpj', ''))[:18],
                    str(row.get('nm_razao_social', ''))[:40],
                    str(row.get('nm_municipio', ''))[:20]
                ])

            self.adicionar_tabela(dados_tabela, larguras=[1.5*inch, 3*inch, 1.5*inch])
        else:
            self.adicionar_paragrafo("Nenhum CNPJ encontrado.")

        self.adicionar_quebra_pagina()

        self.adicionar_secao("3. ANÁLISE DE RISCO MULTIDIMENSIONAL")

        kpis_risco = {
            'Score Cadastral': f"{dados_grupo.get('razao_social_identica', 0) + dados_grupo.get('fantasia_identica', 0)}",
            'Sócios Compartilhados': formatar_numero(dados_grupo.get('socios_compartilhados', 0)),
            'Contas Compartilhadas': formatar_numero(dados_grupo.get('contas_compartilhadas', 0)),
            'Total de Indícios': formatar_numero(dados_grupo.get('total_indicios', 0)),
            'Risco C115': dados_grupo.get('nivel_risco_c115', 'N/A')
        }

        self.adicionar_kpis(kpis_risco)

        if not dossie.get('socios', pd.DataFrame()).empty:
            self.adicionar_secao("4. SÓCIOS COMPARTILHADOS")

            df_socios = dossie['socios'].head(15)
            dados_socios = [['CPF Sócio', 'Qtd Empresas']]

            for _, row in df_socios.iterrows():
                dados_socios.append([
                    str(row.get('cpf_socio', '')),
                    formatar_numero(row.get('qtd_empresas', 0))
                ])

            self.adicionar_tabela(dados_socios, larguras=[3*inch, 2*inch])

        self.adicionar_quebra_pagina()
        self.adicionar_secao("5. OBSERVAÇÕES E RECOMENDAÇÕES")

        score = dados_grupo.get('score_final_percent', 0)
        if score >= 80:
            recomendacao = "GRUPO DE RISCO CRÍTICO - Recomenda-se investigação fiscal urgente e detalhada."
        elif score >= 60:
            recomendacao = "GRUPO DE ALTO RISCO - Recomenda-se monitoramento próximo e análise aprofundada."
        elif score >= 40:
            recomendacao = "GRUPO DE MÉDIO RISCO - Recomenda-se acompanhamento periódico."
        else:
            recomendacao = "GRUPO DE BAIXO RISCO - Manter em monitoramento padrão."

        self.adicionar_paragrafo(f"<b>Recomendação:</b> {recomendacao}")

        self.story.append(Spacer(1, 0.5*inch))
        self.adicionar_paragrafo("<i>Este documento foi gerado automaticamente pelo Sistema GEI.</i>")
        self.adicionar_paragrafo("<i>As informações contidas neste dossiê são confidenciais e de uso exclusivo da Receita Estadual.</i>")

        doc.build(self.story)
        output.seek(0)

        return output

def gerar_dossie_pdf(num_grupo: str, dados_grupo: pd.Series, dossie: Dict[str, pd.DataFrame]) -> BytesIO:
    """Função wrapper para gerar dossiê em PDF"""
    gerador = PDFDossie(num_grupo)
    return gerador.gerar_pdf(dados_grupo, dossie)

def criar_botao_download_pdf(num_grupo: str, dados_grupo: pd.Series, dossie: Dict[str, pd.DataFrame], label: str = "📥 Download PDF") -> None:
    """Cria botão de download para PDF do dossiê"""
    pdf_data = gerar_dossie_pdf(num_grupo, dados_grupo, dossie)

    st.download_button(
        label=label,
        data=pdf_data,
        file_name=f"dossie_grupo_{num_grupo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="GEI - Monitoramento Fiscal v4.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }

    div[data-testid="stPlotlyChart"] {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        background-color: #ffffff;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 2px solid #2c3e50;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# AUTENTICAÇÃO
# =============================================================================

if not check_password():
    st.stop()

# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

engine = get_impala_engine()

if engine is None:
    st.error("❌ Não foi possível conectar ao banco de dados. Verifique as configurações.")
    st.stop()

dados = carregar_todos_os_dados(engine)

if not dados or dados.get('percent', pd.DataFrame()).empty:
    st.error("❌ Não foi possível carregar os dados do sistema.")
    st.stop()

# =============================================================================
# SIDEBAR - NAVEGAÇÃO E FILTROS
# =============================================================================

with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1F77B4/FFFFFF?text=GEI+v4.0", use_container_width=True)

    st.markdown("### 🔐 Usuário Autenticado")
    if st.button("🚪 Sair", use_container_width=True):
        logout()

    st.markdown("---")

    st.markdown("### 📋 Navegação")

    pagina = st.radio(
        "Selecione a página:",
        [
            "📊 Dashboard Executivo",
            "🎯 Análise Pontual",
            "📈 Ranking de Grupos",
            "🤖 Machine Learning",
            "🔗 Análise de Redes",
            "📐 Análise Multidimensional",
            "💡 Insights Automáticos",
            "📋 Dossiê Completo",
            "⚙️ Configurações"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("### 🔍 Filtros Globais")

    score_range = st.slider(
        "Score de Risco (%)",
        0, 100, (0, 100),
        help="Filtrar grupos por faixa de score"
    )

    niveis_selecionados = st.multiselect(
        "Níveis de Risco",
        options=['CRÍTICO', 'ALTO', 'MÉDIO', 'BAIXO'],
        default=['CRÍTICO', 'ALTO'],
        help="Filtrar por níveis de risco"
    )

    df_filtrado = dados['percent'].copy()
    if 'score_final_percent' in df_filtrado.columns:
        df_filtrado = filtrar_por_score(df_filtrado, score_range[0], score_range[1], 'score_final_percent')
    if 'nivel_risco_final' in df_filtrado.columns and niveis_selecionados:
        df_filtrado = filtrar_por_nivel_risco(df_filtrado, niveis_selecionados, 'nivel_risco_final')

# =============================================================================
# PÁGINA 1: DASHBOARD EXECUTIVO
# =============================================================================

if pagina == "📊 Dashboard Executivo":
    st.markdown("<h1 class='main-header'>📊 Dashboard Executivo</h1>", unsafe_allow_html=True)

    stats = carregar_estatisticas_gerais(engine)

    st.markdown("### 📌 Indicadores Principais")

    kpis = [
        {
            'label': 'Total de Grupos',
            'valor': stats.get('total_grupos', 0),
            'formato': 'numero',
            'help': 'Total de grupos econômicos monitorados'
        },
        {
            'label': 'Grupos Críticos',
            'valor': stats.get('grupos_criticos', 0),
            'formato': 'numero',
            'help': 'Grupos com score >= 80%'
        },
        {
            'label': 'Score Médio',
            'valor': stats.get('score_medio', 0),
            'formato': 'numero',
            'help': 'Score médio de risco de todos os grupos'
        },
        {
            'label': 'Total CNPJs',
            'valor': stats.get('total_cnpjs', 0),
            'formato': 'numero',
            'help': 'Total de CNPJs monitorados'
        }
    ]

    criar_grid_kpis(kpis, colunas=4)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Distribuição de Score de Risco")
        if not df_filtrado.empty and 'score_final_percent' in df_filtrado.columns:
            fig_hist = criar_histograma(
                df_filtrado,
                'score_final_percent',
                'Distribuição de Score de Risco',
                bins=30,
                cor=CORES['primaria'],
                mostrar_estatisticas=True
            )
            st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': True})
        else:
            st.info("Dados não disponíveis")

    with col2:
        st.markdown("### 🎯 Grupos por Nível de Risco")
        if not df_filtrado.empty and 'nivel_risco_final' in df_filtrado.columns:
            dist_risco = df_filtrado['nivel_risco_final'].value_counts().reset_index()
            dist_risco.columns = ['Nível', 'Quantidade']

            fig_pizza = criar_grafico_pizza(
                dist_risco,
                values='Quantidade',
                names='Nível',
                titulo='Distribuição por Nível de Risco',
                hole=0.4,
                mostrar_percentual=True
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.info("Dados não disponíveis")

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 💰 Top 15 Grupos por Receita")
        if not df_filtrado.empty and 'receita_maxima' in df_filtrado.columns:
            top_receita = df_filtrado.nlargest(15, 'receita_maxima')[['num_grupo', 'receita_maxima', 'score_final_percent']]

            fig_barras = criar_grafico_barras(
                top_receita,
                x='num_grupo',
                y='receita_maxima',
                titulo='Top 15 Grupos por Receita Máxima',
                orientacao='v',
                cor=CORES['secundaria']
            )
            st.plotly_chart(fig_barras, use_container_width=True)
        else:
            st.info("Dados não disponíveis")

    with col4:
        st.markdown("### 🏢 Top 15 Grupos por Quantidade de CNPJs")
        if not df_filtrado.empty and 'qtd_cnpjs' in df_filtrado.columns:
            top_cnpjs = df_filtrado.nlargest(15, 'qtd_cnpjs')[['num_grupo', 'qtd_cnpjs', 'score_final_percent']]

            fig_barras_cnpj = criar_grafico_barras(
                top_cnpjs,
                x='num_grupo',
                y='qtd_cnpjs',
                titulo='Top 15 Grupos por Quantidade de CNPJs',
                orientacao='v',
                cor=CORES['sucesso']
            )
            st.plotly_chart(fig_barras_cnpj, use_container_width=True)
        else:
            st.info("Dados não disponíveis")

    st.markdown("---")

    st.markdown("### 💡 Insights Gerais do Sistema")
    insights_gerais = gerar_insights_gerais(df_filtrado)
    exibir_insights(insights_gerais)

    st.markdown("---")
    st.markdown("### 📥 Exportar Dados")

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        criar_botao_download_excel(
            {'Dashboard': df_filtrado.head(1000)},
            nome_arquivo='dashboard_executivo',
            label='📥 Download Dashboard (Excel)'
        )

    with col_exp2:
        criar_botao_download_csv(
            df_filtrado.head(1000),
            nome_arquivo='dashboard_executivo',
            label='📥 Download Dashboard (CSV)'
        )

# =============================================================================
# PÁGINA 2: ANÁLISE PONTUAL
# =============================================================================

elif pagina == "🎯 Análise Pontual":
    st.markdown("<h1 class='main-header'>🎯 Análise Pontual de Grupo</h1>", unsafe_allow_html=True)

    st.markdown("### 🔍 Buscar Grupo")

    col_busca1, col_busca2 = st.columns(2)

    with col_busca1:
        num_grupo_input = st.text_input(
            "Número do Grupo",
            placeholder="Digite o número do grupo",
            help="Informe o número do grupo econômico"
        )

    with col_busca2:
        cnpj_input = st.text_input(
            "ou CNPJ",
            placeholder="Digite o CNPJ",
            help="Informe um CNPJ para buscar seu grupo"
        )

    num_grupo_buscar = None

    if cnpj_input:
        with st.spinner("Buscando grupo do CNPJ..."):
            num_grupo_buscar = buscar_grupo_por_cnpj(engine, cnpj_input)
            if num_grupo_buscar:
                st.success(f"✅ CNPJ encontrado no grupo {num_grupo_buscar}")
            else:
                st.error("❌ CNPJ não encontrado na base de dados")
    elif num_grupo_input:
        num_grupo_buscar = num_grupo_input

    if num_grupo_buscar:
        with st.spinner("Carregando dados do grupo..."):
            dados_grupo = dados['percent'][dados['percent']['num_grupo'] == num_grupo_buscar]

            if dados_grupo.empty:
                st.error(f"❌ Grupo {num_grupo_buscar} não encontrado")
            else:
                grupo_serie = dados_grupo.iloc[0]

                dossie = carregar_dossie_completo(engine, num_grupo_buscar)

                st.markdown("---")

                st.markdown("### 📌 Resumo do Grupo")

                kpis_grupo = [
                    {'label': 'Número do Grupo', 'valor': num_grupo_buscar, 'formato': 'texto'},
                    {'label': 'CNPJs', 'valor': grupo_serie.get('qtd_cnpjs', 0), 'formato': 'numero'},
                    {'label': 'Score', 'valor': grupo_serie.get('score_final_percent', 0), 'formato': 'numero'},
                    {'label': 'Nível', 'valor': grupo_serie.get('nivel_risco_final', 'N/A'), 'formato': 'texto'}
                ]

                cols_kpi = st.columns(4)
                for idx, kpi_info in enumerate(kpis_grupo):
                    with cols_kpi[idx]:
                        if kpi_info['formato'] == 'numero':
                            criar_kpi(kpi_info['label'], kpi_info['valor'], formato='numero')
                        else:
                            st.metric(kpi_info['label'], kpi_info['valor'])

                st.markdown("---")

                col_gauge, col_detalhes = st.columns([1, 2])

                with col_gauge:
                    st.markdown("### 🎯 Medidor de Risco")
                    score = grupo_serie.get('score_final_percent', 0)
                    fig_gauge = criar_gauge(
                        valor=score,
                        titulo="Score de Risco",
                        max_valor=100,
                        cor_baixo="#2ca02c",
                        cor_medio="#ff9800",
                        cor_alto="#d62728"
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with col_detalhes:
                    st.markdown("### 📋 Detalhes de Risco")

                    detalhes_risco = {
                        'Sócios Compartilhados': formatar_numero(grupo_serie.get('socios_compartilhados', 0)),
                        'Contas Compartilhadas': formatar_numero(grupo_serie.get('contas_compartilhadas', 0)),
                        'Total de Indícios': formatar_numero(grupo_serie.get('total_indicios', 0)),
                        'Receita Máxima': formatar_moeda(grupo_serie.get('receita_maxima', 0)),
                        'Risco C115': grupo_serie.get('nivel_risco_c115', 'N/A')
                    }

                    for label, valor in detalhes_risco.items():
                        st.markdown(f"**{label}:** {valor}")

                st.markdown("---")

                st.markdown("### 💡 Insights Automáticos")
                insights = gerar_insights_grupo(grupo_serie, dossie)
                exibir_insights(insights)

                st.markdown("---")

                st.markdown("### 🏢 CNPJs do Grupo")
                if not dossie.get('cnpjs', pd.DataFrame()).empty:
                    exibir_tabela_formatada(
                        dossie['cnpjs'][['cnpj', 'nm_razao_social', 'nm_fantasia', 'nm_municipio']].head(50),
                        altura=300
                    )
                else:
                    st.info("Nenhum CNPJ encontrado")

                st.markdown("---")

                st.markdown("### 📥 Exportar Dossiê")

                col_pdf, col_excel = st.columns(2)

                with col_pdf:
                    criar_botao_download_pdf(
                        num_grupo_buscar,
                        grupo_serie,
                        dossie,
                        label='📄 Download Dossiê (PDF)'
                    )

                with col_excel:
                    dados_export = {
                        'Dados Principais': pd.DataFrame([grupo_serie]),
                        'CNPJs': dossie.get('cnpjs', pd.DataFrame()),
                        'Sócios': dossie.get('socios', pd.DataFrame()),
                        'Indícios': dossie.get('indicios', pd.DataFrame())
                    }

                    criar_botao_download_excel(
                        dados_export,
                        nome_arquivo=f'dossie_grupo_{num_grupo_buscar}',
                        label='📊 Download Dossiê (Excel)'
                    )

# =============================================================================
# PÁGINA 3: RANKING
# =============================================================================

elif pagina == "📈 Ranking de Grupos":
    st.markdown("<h1 class='main-header'>📈 Ranking de Grupos por Risco</h1>", unsafe_allow_html=True)

    st.markdown("### 🏆 Top Grupos de Maior Risco")

    top_n = st.slider("Quantidade de grupos no ranking", 10, 100, 30, step=10)

    if not df_filtrado.empty and 'score_final_percent' in df_filtrado.columns:
        top_grupos = df_filtrado.nlargest(top_n, 'score_final_percent')

        top_grupos['ranking'] = range(1, len(top_grupos) + 1)

        colunas_exibir = ['ranking', 'num_grupo', 'qtd_cnpjs', 'score_final_percent',
                         'nivel_risco_final', 'receita_maxima', 'socios_compartilhados',
                         'contas_compartilhadas', 'total_indicios']

        colunas_disponiveis = [col for col in colunas_exibir if col in top_grupos.columns]

        exibir_tabela_formatada(
            top_grupos[colunas_disponiveis],
            colunas_moeda=['receita_maxima'] if 'receita_maxima' in colunas_disponiveis else None,
            altura=600
        )

        st.markdown("---")
        st.markdown("### 📊 Visualização do Ranking")

        fig_ranking = criar_grafico_barras(
            top_grupos.head(20),
            x='num_grupo',
            y='score_final_percent',
            titulo=f'Top 20 Grupos por Score de Risco',
            orientacao='v',
            cor=CORES['perigo']
        )

        st.plotly_chart(fig_ranking, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📥 Exportar Ranking")

        col_rank1, col_rank2 = st.columns(2)

        with col_rank1:
            criar_botao_download_excel(
                {'Ranking': top_grupos},
                nome_arquivo='ranking_grupos',
                label='📥 Download Ranking (Excel)'
            )

        with col_rank2:
            criar_botao_download_csv(
                top_grupos,
                nome_arquivo='ranking_grupos',
                label='📥 Download Ranking (CSV)'
            )

    else:
        st.info("Dados não disponíveis para gerar ranking")

# =============================================================================
# PÁGINA 4: MACHINE LEARNING
# =============================================================================

elif pagina == "🤖 Machine Learning":
    st.markdown("<h1 class='main-header'>🤖 Análise de Machine Learning</h1>", unsafe_allow_html=True)

    st.markdown("""
    Esta página permite aplicar algoritmos de **Machine Learning** para identificar padrões
    e anomalias nos grupos econômicos monitorados.
    """)

    st.markdown("---")

    st.markdown("### ⚙️ Configurações")

    col_ml1, col_ml2, col_ml3 = st.columns(3)

    with col_ml1:
        n_clusters = st.slider("Número de Clusters (K-Means)", 2, 10, 3)

    with col_ml2:
        eps_dbscan = st.slider("EPS (DBSCAN)", 0.1, 2.0, 0.5, step=0.1)

    with col_ml3:
        contamination = st.slider("Contaminação (Isolation Forest)", 0.05, 0.5, 0.1, step=0.05)

    if st.button("🚀 Executar Análise de ML", type="primary"):
        with st.spinner("Preparando dados..."):
            df_clean, X_scaled, scaler = preparar_dados_ml(df_filtrado)

            if len(df_clean) < 10:
                st.error("Dados insuficientes para análise de ML (mínimo 10 registros)")
            else:
                st.markdown("---")
                st.markdown("### 📐 Redução de Dimensionalidade (PCA)")

                X_pca, pca_model, var_explicada = aplicar_pca(X_scaled, n_components=3)

                st.success(f"✅ PCA aplicado com sucesso! Variância explicada: {var_explicada:.2f}%")

                st.markdown("---")
                st.markdown("### 🔬 Análise de Consenso - Múltiplos Algoritmos")

                resultados = executar_consenso(X_scaled, n_clusters, eps_dbscan, contamination)

                st.markdown("#### 📊 Métricas de Qualidade")

                metricas_df = pd.DataFrame({
                    'Algoritmo': [res['nome'] for res in resultados.values()],
                    'Silhouette': [res['metricas'].get('silhouette', 'N/A') for res in resultados.values()],
                    'Davies-Bouldin': [res['metricas'].get('davies_bouldin', 'N/A') for res in resultados.values()],
                    'N Clusters/Anomalias': [
                        res['metricas'].get('n_clusters', res['metricas'].get('n_anomalias', 'N/A'))
                        for res in resultados.values()
                    ]
                })

                st.dataframe(metricas_df, use_container_width=True)

                st.markdown("---")
                st.markdown("### 📊 Visualização Comparativa")

                fig_comp = comparar_algoritmos(resultados, X_pca)
                st.plotly_chart(fig_comp, use_container_width=True)

                st.markdown("---")
                st.markdown("### 🎨 Visualização 3D (K-Means)")

                labels_km = resultados['kmeans']['labels']
                fig_3d = visualizar_clusters_3d(X_pca, labels_km, df_clean, "Clusters K-Means em 3D")
                st.plotly_chart(fig_3d, use_container_width=True)

    else:
        st.info("👆 Configure os parâmetros e clique em 'Executar Análise de ML' para começar")

# =============================================================================
# PÁGINA 5: ANÁLISE DE REDES
# =============================================================================

elif pagina == "🔗 Análise de Redes":
    st.markdown("<h1 class='main-header'>🔗 Análise de Redes Societárias</h1>", unsafe_allow_html=True)

    st.markdown("""
    Visualize as conexões entre grupos econômicos através de sócios compartilhados
    e outras relações societárias.
    """)

    st.markdown("---")

    num_grupo_rede = st.text_input(
        "Número do Grupo para Análise de Rede",
        placeholder="Digite o número do grupo"
    )

    if num_grupo_rede:
        with st.spinner("Carregando dados da rede..."):
            if not dados.get('socios_compartilhados', pd.DataFrame()).empty:
                df_socios = dados['socios_compartilhados'][
                    dados['socios_compartilhados']['num_grupo'] == num_grupo_rede
                ]

                if not df_socios.empty:
                    nos = []
                    arestas = []

                    nos.append({
                        'id': f'grupo_{num_grupo_rede}',
                        'label': f'Grupo {num_grupo_rede}',
                        'value': 20
                    })

                    for idx, row in df_socios.iterrows():
                        cpf = row['cpf_socio']
                        qtd = row['qtd_empresas']

                        nos.append({
                            'id': f'socio_{cpf}',
                            'label': f'CPF {cpf[:6]}...',
                            'value': min(qtd * 2, 15)
                        })

                        arestas.append({
                            'source': f'grupo_{num_grupo_rede}',
                            'target': f'socio_{cpf}',
                            'value': min(qtd, 5)
                        })

                    fig_rede = criar_grafico_rede(
                        nos,
                        arestas,
                        f'Rede de Sócios do Grupo {num_grupo_rede}'
                    )

                    st.plotly_chart(fig_rede, use_container_width=True)

                    st.markdown("---")
                    st.markdown("### 👥 Sócios Compartilhados")

                    exibir_tabela_formatada(df_socios, altura=400)

                else:
                    st.info("Nenhum sócio compartilhado encontrado para este grupo")
            else:
                st.warning("Dados de sócios não disponíveis")
    else:
        st.info("Digite o número de um grupo para visualizar sua rede societária")

# =============================================================================
# PÁGINA 6: ANÁLISE MULTIDIMENSIONAL
# =============================================================================

elif pagina == "📐 Análise Multidimensional":
    st.markdown("<h1 class='main-header'>📐 Análise Multidimensional</h1>", unsafe_allow_html=True)

    st.markdown("""
    Explore correlações e padrões multidimensionais entre diferentes métricas de risco.
    """)

    st.markdown("---")

    colunas_numericas = df_filtrado.select_dtypes(include=[np.number]).columns.tolist()

    colunas_selecionadas = st.multiselect(
        "Selecione as métricas para análise",
        options=colunas_numericas,
        default=colunas_numericas[:min(6, len(colunas_numericas))],
        help="Selecione até 10 métricas"
    )

    if len(colunas_selecionadas) >= 2:
        st.markdown("### 🔥 Matriz de Correlação")

        fig_corr = criar_matriz_correlacao(
            df_filtrado,
            colunas=colunas_selecionadas,
            titulo="Matriz de Correlação entre Métricas",
            metodo='pearson'
        )

        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("---")

        if len(colunas_selecionadas) <= 5:
            st.markdown("### 📊 Scatter Matrix")

            fig_scatter = px.scatter_matrix(
                df_filtrado,
                dimensions=colunas_selecionadas,
                title="Matriz de Dispersão"
            )

            fig_scatter.update_traces(diagonal_visible=False)
            st.plotly_chart(fig_scatter, use_container_width=True)

    else:
        st.info("Selecione pelo menos 2 métricas para análise")

# =============================================================================
# PÁGINA 7: INSIGHTS AUTOMÁTICOS
# =============================================================================

elif pagina == "💡 Insights Automáticos":
    st.markdown("<h1 class='main-header'>💡 Insights Automáticos</h1>", unsafe_allow_html=True)

    st.markdown("""
    Insights gerados automaticamente pelo sistema com base em análise de padrões e regras de negócio.
    """)

    st.markdown("---")

    st.markdown("### 🌐 Insights Gerais do Sistema")

    insights_sistema = gerar_insights_gerais(df_filtrado)
    exibir_insights(insights_sistema)

    st.markdown("---")

    st.markdown("### 🔝 Grupos Prioritários para Investigação")

    if not df_filtrado.empty and 'score_final_percent' in df_filtrado.columns:
        top_investigacao = df_filtrado.nlargest(10, 'score_final_percent')

        for idx, (_, grupo) in enumerate(top_investigacao.iterrows(), 1):
            with st.expander(f"#{idx} - Grupo {grupo['num_grupo']} (Score: {grupo['score_final_percent']:.1f}%)"):
                dossie_resumo = {'cnpjs': pd.DataFrame(), 'socios': pd.DataFrame()}

                insights_grupo = gerar_insights_grupo(grupo, dossie_resumo)
                exibir_insights(insights_grupo)

# =============================================================================
# PÁGINA 8: DOSSIÊ COMPLETO
# =============================================================================

elif pagina == "📋 Dossiê Completo":
    st.markdown("<h1 class='main-header'>📋 Gerador de Dossiê Completo</h1>", unsafe_allow_html=True)

    st.markdown("""
    Gere um dossiê completo e detalhado de um grupo econômico com todas as informações disponíveis.
    """)

    st.markdown("---")

    num_grupo_dossie = st.text_input(
        "Número do Grupo",
        placeholder="Digite o número do grupo para gerar o dossiê"
    )

    if num_grupo_dossie and st.button("📄 Gerar Dossiê Completo", type="primary"):
        with st.spinner("Gerando dossiê completo..."):
            dados_grupo_dossie = dados['percent'][dados['percent']['num_grupo'] == num_grupo_dossie]

            if dados_grupo_dossie.empty:
                st.error(f"Grupo {num_grupo_dossie} não encontrado")
            else:
                grupo_dossie_serie = dados_grupo_dossie.iloc[0]
                dossie_completo = carregar_dossie_completo(engine, num_grupo_dossie)

                st.success("✅ Dossiê gerado com sucesso!")

                criar_botao_download_pdf(
                    num_grupo_dossie,
                    grupo_dossie_serie,
                    dossie_completo,
                    label='📥 Download Dossiê Completo (PDF)'
                )

# =============================================================================
# PÁGINA 9: CONFIGURAÇÕES
# =============================================================================

elif pagina == "⚙️ Configurações":
    st.markdown("<h1 class='main-header'>⚙️ Configurações do Sistema</h1>", unsafe_allow_html=True)

    st.markdown("### ℹ️ Informações do Sistema")

    st.info("""
    **Sistema:** GEI - Gestão Estratégica de Informações v4.0
    **Desenvolvido para:** Receita Estadual de Santa Catarina
    **Última Atualização:** 2025
    """)

    st.markdown("---")

    st.markdown("### 📊 Estatísticas de Cache")

    if st.button("🔄 Limpar Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("✅ Cache limpo com sucesso!")
        st.rerun()

    st.markdown("---")

    st.markdown("### 📚 Sobre o Sistema")

    with st.expander("ℹ️ Funcionalidades"):
        st.markdown("""
        - **Dashboard Executivo:** Visão geral com KPIs e gráficos
        - **Análise Pontual:** Análise detalhada de grupos específicos
        - **Ranking:** Top grupos por risco
        - **Machine Learning:** Clustering e detecção de anomalias
        - **Análise de Redes:** Visualização de vínculos societários
        - **Análise Multidimensional:** Correlações entre métricas
        - **Insights Automáticos:** Geração automática de insights
        - **Dossiê Completo:** Relatórios em PDF
        """)

    with st.expander("🔧 Tecnologias Utilizadas"):
        st.markdown("""
        - **Framework:** Streamlit
        - **Visualização:** Plotly
        - **Machine Learning:** scikit-learn
        - **Banco de Dados:** Impala
        - **Relatórios:** ReportLab, openpyxl
        """)

# =============================================================================
# RODAPÉ
# =============================================================================

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
    "© 2025 Sistema GEI - Receita Estadual de Santa Catarina | v4.0"
    "</div>",
    unsafe_allow_html=True
)
