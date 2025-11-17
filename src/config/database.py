"""
Módulo de Conexão com Banco de Dados
Gerencia conexões com o Impala e execução de queries
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import ssl
from typing import Optional, Dict, Any
from .settings import (
    IMPALA_HOST, IMPALA_PORT, DATABASE,
    get_credentials, MENSAGENS
)

# =============================================================================
# CONFIGURAÇÃO SSL
# =============================================================================

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# =============================================================================
# CONEXÃO COM BANCO DE DADOS
# =============================================================================

@st.cache_resource
def get_impala_engine():
    """
    Cria e retorna engine de conexão com Impala

    Returns:
        Engine SQLAlchemy ou None em caso de erro
    """
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

        # Testa conexão
        connection = engine.connect()
        connection.close()

        return engine

    except Exception as e:
        st.error(f"{MENSAGENS['erro_conexao']}\n\nDetalhes: {str(e)}")
        return None

# =============================================================================
# EXECUÇÃO DE QUERIES
# =============================================================================

def executar_query(
    engine,
    query: str,
    params: Optional[Dict[str, Any]] = None,
    show_error: bool = True
) -> pd.DataFrame:
    """
    Executa uma query SQL e retorna DataFrame

    Args:
        engine: Engine SQLAlchemy
        query: Query SQL a ser executada
        params: Parâmetros da query (opcional)
        show_error: Se True, exibe erros na interface

    Returns:
        DataFrame com resultados ou DataFrame vazio em caso de erro
    """
    if engine is None:
        if show_error:
            st.error(MENSAGENS['erro_conexao'])
        return pd.DataFrame()

    try:
        df = pd.read_sql(query, engine, params=params)

        # Normaliza nomes das colunas para minúsculas
        df.columns = [col.lower() for col in df.columns]

        return df

    except Exception as e:
        if show_error:
            st.error(f"{MENSAGENS['erro_query']}\n\nDetalhes: {str(e)}")
        return pd.DataFrame()

def executar_query_com_cache(
    engine,
    cache_key: str,
    query: str,
    ttl: int = 3600,
    params: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Executa query com cache do Streamlit

    Args:
        engine: Engine SQLAlchemy
        cache_key: Chave única para o cache
        query: Query SQL
        ttl: Tempo de vida do cache em segundos
        params: Parâmetros da query

    Returns:
        DataFrame com resultados
    """
    @st.cache_data(ttl=ttl, show_spinner=f"Carregando {cache_key}...")
    def _query_cached(_engine, _query, _params):
        return executar_query(_engine, _query, _params)

    return _query_cached(engine, query, params)

# =============================================================================
# QUERIES PRÉ-DEFINIDAS
# =============================================================================

class Queries:
    """Classe com queries SQL pré-definidas do sistema"""

    @staticmethod
    def get_dados_grupo(num_grupo: str) -> str:
        """Query para obter dados principais de um grupo"""
        return f"""
        SELECT *
        FROM {DATABASE}.gei_percent
        WHERE num_grupo = '{num_grupo}'
        """

    @staticmethod
    def get_cnpjs_grupo(num_grupo: str, limit: Optional[int] = None) -> str:
        """Query para obter CNPJs de um grupo"""
        limit_clause = f"LIMIT {limit}" if limit else ""
        return f"""
        SELECT
            g.cnpj,
            c.nm_razao_social,
            c.nm_fantasia,
            c.cd_cnae,
            c.nm_reg_apuracao,
            c.dt_constituicao_empresa,
            c.nm_munic as nm_municipio,
            c.nm_contador
        FROM {DATABASE}.gei_cnpj g
        LEFT JOIN usr_sat_ods.vw_ods_contrib c ON g.cnpj = c.nu_cnpj
        WHERE g.num_grupo = '{num_grupo}'
        {limit_clause}
        """

    @staticmethod
    def get_socios_compartilhados(num_grupo: str) -> str:
        """Query para obter sócios compartilhados"""
        return f"""
        SELECT
            cpf_socio,
            qtd_empresas
        FROM {DATABASE}.gei_socios_compartilhados
        WHERE num_grupo = '{num_grupo}'
        ORDER BY qtd_empresas DESC
        """

    @staticmethod
    def get_indicios(num_grupo: str) -> str:
        """Query para obter indícios fiscais"""
        return f"""
        SELECT
            tx_descricao_indicio,
            cnpj,
            tx_descricao_complemento
        FROM {DATABASE}.gei_indicios
        WHERE num_grupo = '{num_grupo}'
        """

    @staticmethod
    def get_c115_ranking(num_grupo: str) -> str:
        """Query para obter dados do Convênio 115"""
        return f"""
        SELECT
            num_grupo,
            ranking_risco,
            nivel_risco_grupo_economico,
            indice_risco_grupo_economico,
            qtd_cnpjs_relacionados,
            perc_cnpjs_relacionados,
            total_tomadores,
            tomadores_com_compartilhamento,
            total_compartilhamentos
        FROM {DATABASE}.gei_c115_ranking_risco_grupo_economico
        WHERE num_grupo = '{num_grupo}'
        """

    @staticmethod
    def get_ccs_compartilhadas(num_grupo: str, limit: int = 50) -> str:
        """Query para obter contas compartilhadas"""
        return f"""
        SELECT
            nr_cpf,
            nm_banco,
            cd_agencia,
            nr_conta,
            qtd_cnpjs_usando_conta,
            qtd_vinculos_ativos,
            status_conta
        FROM {DATABASE}.gei_ccs_cpf_compartilhado
        WHERE num_grupo = '{num_grupo}'
        ORDER BY qtd_cnpjs_usando_conta DESC
        LIMIT {limit}
        """

    @staticmethod
    def get_inconsistencias_nfe(num_grupo: str, limit: int = 1000) -> str:
        """Query para obter inconsistências NFe"""
        return f"""
        SELECT
            nfe_nu_chave_acesso,
            nfe_dt_emissao,
            nfe_cnpj_cpf_emit,
            nfe_cnpj_cpf_dest,
            nfe_dest_email,
            nfe_dest_telefone,
            nfe_emit_telefone,
            nfe_cd_produto,
            nfe_de_produto,
            nfe_emit_end_completo,
            nfe_dest_end_completo,
            nfe_ip_transmissao,
            cliente_incons,
            email_incons,
            tel_dest_incons,
            tel_emit_incons,
            codigo_produto_incons,
            fornecedor_incons,
            end_emit_incons,
            end_dest_incons,
            descricao_produto_incons,
            ip_transmissao_incons
        FROM {DATABASE}.gei_nfe_completo
        WHERE grupo_emit = '{num_grupo}' OR grupo_dest = '{num_grupo}'
        LIMIT {limit}
        """

    @staticmethod
    def get_ranking_geral(limit: int = 100) -> str:
        """Query para obter ranking geral de grupos"""
        return f"""
        SELECT
            num_grupo,
            qtd_cnpjs,
            score_final_percent as score_final,
            nivel_risco_final,
            receita_maxima,
            indice_risco_c115,
            total_indicios,
            contas_compartilhadas
        FROM {DATABASE}.gei_percent
        ORDER BY score_final_percent DESC
        LIMIT {limit}
        """

    @staticmethod
    def get_distribuicao_por_cnae() -> str:
        """Query para distribuição por CNAE"""
        return f"""
        SELECT
            cd_cnae,
            COUNT(DISTINCT num_grupo) as qtd_grupos,
            COUNT(DISTINCT cnpj) as qtd_cnpjs,
            AVG(score_final_percent) as score_medio
        FROM {DATABASE}.gei_percent p
        JOIN {DATABASE}.gei_cadastro c ON p.num_grupo = c.num_grupo
        GROUP BY cd_cnae
        ORDER BY qtd_grupos DESC
        """

    @staticmethod
    def get_estatisticas_gerais() -> str:
        """Query para estatísticas gerais do sistema"""
        return f"""
        SELECT
            COUNT(DISTINCT num_grupo) as total_grupos,
            COUNT(DISTINCT num_grupo) FILTER (WHERE score_final_percent >= 80) as grupos_criticos,
            COUNT(DISTINCT num_grupo) FILTER (WHERE score_final_percent >= 60 AND score_final_percent < 80) as grupos_alto_risco,
            AVG(score_final_percent) as score_medio,
            MAX(score_final_percent) as score_maximo,
            SUM(qtd_cnpjs) as total_cnpjs,
            AVG(qtd_cnpjs) as media_cnpjs_por_grupo
        FROM {DATABASE}.gei_percent
        """

# =============================================================================
# FUNÇÕES DE VALIDAÇÃO
# =============================================================================

def validar_conexao(engine) -> bool:
    """
    Valida se a conexão com o banco está ativa

    Args:
        engine: Engine SQLAlchemy

    Returns:
        True se conexão está ativa, False caso contrário
    """
    if engine is None:
        return False

    try:
        connection = engine.connect()
        connection.close()
        return True
    except:
        return False

def testar_query(engine, query: str) -> tuple[bool, str]:
    """
    Testa uma query sem executá-la completamente

    Args:
        engine: Engine SQLAlchemy
        query: Query a ser testada

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        # Adiciona LIMIT 1 para testar sintaxe
        test_query = f"SELECT * FROM ({query}) AS test LIMIT 1"
        executar_query(engine, test_query, show_error=False)
        return True, "Query válida"
    except Exception as e:
        return False, str(e)
