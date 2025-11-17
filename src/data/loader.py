"""
Módulo de Carregamento de Dados
Gerencia carregamento e cache de dados do sistema GEI
"""

import streamlit as st
import pandas as pd
from typing import Dict, Optional
from ..config.settings import (
    TABELAS_PRINCIPAIS, CACHE_TTL_DADOS_PRINCIPAIS,
    CACHE_TTL_DOSSIE, DATABASE, MENSAGENS
)
from ..config.database import executar_query, Queries

# =============================================================================
# CARREGAMENTO DE DADOS PRINCIPAIS
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_DADOS_PRINCIPAIS, show_spinner="⏳ Carregando dados principais...")
def carregar_todos_os_dados(_engine) -> Dict[str, pd.DataFrame]:
    """
    Carrega todos os datasets principais do sistema GEI

    Args:
        _engine: Engine SQLAlchemy (com _ para não fazer hash no cache)

    Returns:
        Dicionário com DataFrames de todas as tabelas principais
    """
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

@st.cache_data(ttl=CACHE_TTL_DADOS_PRINCIPAIS)
def carregar_tabela(_engine, nome_tabela: str, limit: Optional[int] = None) -> pd.DataFrame:
    """
    Carrega uma tabela específica do banco

    Args:
        _engine: Engine SQLAlchemy
        nome_tabela: Nome da tabela
        limit: Limite de registros (opcional)

    Returns:
        DataFrame com dados da tabela
    """
    if _engine is None:
        return pd.DataFrame()

    try:
        if limit:
            query = f"SELECT * FROM {DATABASE}.{nome_tabela} LIMIT {limit}"
        else:
            query = f"SELECT * FROM {DATABASE}.{nome_tabela}"

        return executar_query(_engine, query)

    except Exception as e:
        st.error(f"Erro ao carregar {nome_tabela}: {e}")
        return pd.DataFrame()

# =============================================================================
# CARREGAMENTO DE DOSSIÊ COMPLETO
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_DOSSIE, show_spinner="📋 Carregando dossiê completo...")
def carregar_dossie_completo(_engine, num_grupo: str) -> Dict[str, pd.DataFrame]:
    """
    Carrega todos os dados de um grupo específico para o dossiê

    Args:
        _engine: Engine SQLAlchemy
        num_grupo: Número do grupo

    Returns:
        Dicionário com DataFrames de todas as análises do grupo
    """
    dossie = {}
    num_grupo_str = str(num_grupo)

    # 1. Dados Principais
    dossie['principal'] = executar_query(
        _engine,
        Queries.get_dados_grupo(num_grupo_str),
        show_error=False
    )

    # 2. CNPJs do Grupo
    dossie['cnpjs'] = executar_query(
        _engine,
        Queries.get_cnpjs_grupo(num_grupo_str),
        show_error=False
    )

    # 3. Sócios Compartilhados
    dossie['socios'] = executar_query(
        _engine,
        Queries.get_socios_compartilhados(num_grupo_str),
        show_error=False
    )

    # 4. Indícios Fiscais
    dossie['indicios'] = executar_query(
        _engine,
        Queries.get_indicios(num_grupo_str),
        show_error=False
    )

    # 5. Funcionários
    query_func = f"""
    SELECT num_grupo, total_funcionarios, cnpjs_com_funcionarios
    FROM {DATABASE}.gei_funcionarios_metricas_grupo
    WHERE num_grupo = '{num_grupo_str}'
    """
    dossie['funcionarios'] = executar_query(_engine, query_func, show_error=False)

    # 6. Pagamentos
    query_pag = f"""
    SELECT num_grupo, valor_meios_pagamento_empresas, valor_meios_pagamento_socios
    FROM {DATABASE}.gei_pagamentos_metricas_grupo
    WHERE num_grupo = '{num_grupo_str}'
    """
    dossie['pagamentos'] = executar_query(_engine, query_pag, show_error=False)

    # 7. Convênio 115
    dossie['c115'] = executar_query(
        _engine,
        Queries.get_c115_ranking(num_grupo_str),
        show_error=False
    )

    # 8. CCS - Contas Compartilhadas
    dossie['ccs_compartilhadas'] = executar_query(
        _engine,
        Queries.get_ccs_compartilhadas(num_grupo_str),
        show_error=False
    )

    # 9. CCS - Sobreposições
    query_sobreposicoes = f"""
    SELECT nr_cpf, cnpj1, cnpj2, nm_responsavel,
           inicio1, fim1, inicio2, fim2, dias_sobreposicao
    FROM {DATABASE}.gei_ccs_sobreposicao_responsaveis
    WHERE num_grupo = '{num_grupo_str}'
    ORDER BY dias_sobreposicao DESC
    LIMIT 50
    """
    dossie['ccs_sobreposicoes'] = executar_query(_engine, query_sobreposicoes, show_error=False)

    # 10. CCS - Padrões Coordenados
    query_padroes = f"""
    SELECT tipo_evento, dt_evento, qtd_cnpjs, qtd_contas, qtd_cpfs_distintos
    FROM {DATABASE}.gei_ccs_padroes_coordenados
    WHERE num_grupo = '{num_grupo_str}'
    ORDER BY dt_evento DESC
    LIMIT 50
    """
    dossie['ccs_padroes'] = executar_query(_engine, query_padroes, show_error=False)

    # 11. Inconsistências NFe
    dossie['inconsistencias'] = executar_query(
        _engine,
        Queries.get_inconsistencias_nfe(num_grupo_str),
        show_error=False
    )

    return dossie

# =============================================================================
# CARREGAMENTO DE ANÁLISES ESPECÍFICAS
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_DADOS_PRINCIPAIS)
def carregar_ranking_geral(_engine, limit: int = 100) -> pd.DataFrame:
    """
    Carrega ranking geral de grupos por risco

    Args:
        _engine: Engine SQLAlchemy
        limit: Número de grupos no ranking

    Returns:
        DataFrame com ranking
    """
    return executar_query(_engine, Queries.get_ranking_geral(limit))

@st.cache_data(ttl=CACHE_TTL_DADOS_PRINCIPAIS)
def carregar_estatisticas_gerais(_engine) -> Dict[str, any]:
    """
    Carrega estatísticas gerais do sistema

    Args:
        _engine: Engine SQLAlchemy

    Returns:
        Dicionário com estatísticas
    """
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
def carregar_distribuicao_cnae(_engine) -> pd.DataFrame:
    """
    Carrega distribuição de grupos por CNAE

    Args:
        _engine: Engine SQLAlchemy

    Returns:
        DataFrame com distribuição por CNAE
    """
    return executar_query(_engine, Queries.get_distribuicao_por_cnae())

@st.cache_data(ttl=CACHE_TTL_DADOS_PRINCIPAIS)
def buscar_grupo_por_cnpj(_engine, cnpj: str) -> Optional[str]:
    """
    Busca número do grupo a partir de um CNPJ

    Args:
        _engine: Engine SQLAlchemy
        cnpj: CNPJ a buscar

    Returns:
        Número do grupo ou None se não encontrado
    """
    query = f"""
    SELECT num_grupo
    FROM {DATABASE}.gei_cnpj
    WHERE cnpj = '{cnpj}'
    LIMIT 1
    """

    df = executar_query(_engine, query, show_error=False)

    if not df.empty:
        return str(df.iloc[0]['num_grupo'])

    return None

@st.cache_data(ttl=CACHE_TTL_DADOS_PRINCIPAIS)
def buscar_cnpjs_por_grupo(_engine, num_grupo: str) -> list:
    """
    Busca lista de CNPJs de um grupo

    Args:
        _engine: Engine SQLAlchemy
        num_grupo: Número do grupo

    Returns:
        Lista de CNPJs
    """
    query = f"""
    SELECT cnpj
    FROM {DATABASE}.gei_cnpj
    WHERE num_grupo = '{num_grupo}'
    """

    df = executar_query(_engine, query, show_error=False)

    if not df.empty:
        return df['cnpj'].tolist()

    return []

# =============================================================================
# FUNÇÕES DE FILTRAGEM
# =============================================================================

def aplicar_filtros(df: pd.DataFrame, filtros: Dict) -> pd.DataFrame:
    """
    Aplica filtros a um DataFrame

    Args:
        df: DataFrame a filtrar
        filtros: Dicionário com filtros {coluna: valor ou lista de valores}

    Returns:
        DataFrame filtrado
    """
    if df.empty:
        return df

    df_filtrado = df.copy()

    for coluna, valor in filtros.items():
        if coluna not in df_filtrado.columns:
            continue

        if valor is None or valor == [] or valor == '':
            continue

        if isinstance(valor, list):
            df_filtrado = df_filtrado[df_filtrado[coluna].isin(valor)]
        else:
            df_filtrado = df_filtrado[df_filtrado[coluna] == valor]

    return df_filtrado

def filtrar_por_score(df: pd.DataFrame, score_min: float, score_max: float, coluna_score: str = 'score_final') -> pd.DataFrame:
    """
    Filtra DataFrame por faixa de score

    Args:
        df: DataFrame a filtrar
        score_min: Score mínimo
        score_max: Score máximo
        coluna_score: Nome da coluna de score

    Returns:
        DataFrame filtrado
    """
    if df.empty or coluna_score not in df.columns:
        return df

    return df[(df[coluna_score] >= score_min) & (df[coluna_score] <= score_max)]

def filtrar_por_nivel_risco(df: pd.DataFrame, niveis: list, coluna_nivel: str = 'nivel_risco_final') -> pd.DataFrame:
    """
    Filtra DataFrame por níveis de risco

    Args:
        df: DataFrame a filtrar
        niveis: Lista de níveis de risco (ex: ['CRÍTICO', 'ALTO'])
        coluna_nivel: Nome da coluna de nível de risco

    Returns:
        DataFrame filtrado
    """
    if df.empty or coluna_nivel not in df.columns or not niveis:
        return df

    return df[df[coluna_nivel].isin(niveis)]

# =============================================================================
# FUNÇÕES DE AGREGAÇÃO
# =============================================================================

def agregar_por_coluna(df: pd.DataFrame, coluna_agrupamento: str, colunas_agregacao: Dict[str, str]) -> pd.DataFrame:
    """
    Agrega DataFrame por uma coluna

    Args:
        df: DataFrame a agregar
        coluna_agrupamento: Coluna para agrupar
        colunas_agregacao: Dicionário {coluna: operação} (ex: {'score': 'mean', 'qtd': 'sum'})

    Returns:
        DataFrame agregado
    """
    if df.empty or coluna_agrupamento not in df.columns:
        return pd.DataFrame()

    return df.groupby(coluna_agrupamento).agg(colunas_agregacao).reset_index()

def calcular_estatisticas(df: pd.DataFrame, coluna: str) -> Dict[str, float]:
    """
    Calcula estatísticas descritivas de uma coluna

    Args:
        df: DataFrame
        coluna: Nome da coluna

    Returns:
        Dicionário com estatísticas
    """
    if df.empty or coluna not in df.columns:
        return {}

    serie = df[coluna].dropna()

    return {
        'media': serie.mean(),
        'mediana': serie.median(),
        'desvio_padrao': serie.std(),
        'minimo': serie.min(),
        'maximo': serie.max(),
        'q1': serie.quantile(0.25),
        'q3': serie.quantile(0.75)
    }
