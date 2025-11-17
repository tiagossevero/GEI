"""
Script para geração automática de data-schemas do projeto GEI.
Gera DESCRIBE FORMATTED e SELECT * LIMIT 10 para todas as tabelas.

Autor: Sistema GEI
Data: 2025-11-17
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Adicionar paths necessários (ajustar conforme seu ambiente)
# sys.path.append("/home/tsevero/notebooks/SAT_BIG_DATA/data-pipeline/batch/poc")
# sys.path.append("/home/tsevero/notebooks/SAT_BIG_DATA/data-pipeline/batch/plugins")
# sys.path.append("/home/tsevero/notebooks/SAT_BIG_DATA/data-pipeline/batch/dags")

# Import libs python
from pyspark.sql.types import *
from pyspark.sql.functions import *

# Import libs internas (descomentar se disponível)
# from utils import spark_utils_session as utils
# import poc_helper
# poc_helper.load_env("PROD")


# =============================================================================
# CONFIGURAÇÃO DAS TABELAS
# =============================================================================

TABELAS_ORIGINAIS = [
    ("usr_sat_ods", "vw_ods_contrib", "Dados cadastrais de contribuintes (ODS)"),
    ("usr_sat_ods", "vw_cad_vinculo", "Vínculos cadastrais (sócios/responsáveis)"),
    ("usr_sat_ods", "sna_pgdasd_estabelecimento_raw", "Dados brutos PGDAS-D"),
    ("nfe", "nfe", "Notas Fiscais Eletrônicas"),
    ("c115", "c115_dados_cadastrais_dest", "Convênio 115"),
    ("usr_sat_fsn", "fsn_conta_bancaria", "Contas bancárias"),
    ("rais_caged", "vw_rais_vinculos", "Vínculos empregatícios RAIS/CAGED"),
    ("usr_sat_admcc", "acc_r66_totalestab", "Meios de pagamento"),
    ("neaf", "empresa_indicio", "Indícios fiscais NEAF"),
]

TABELAS_INTERMEDIARIAS = [
    # Principais
    ("gessimples", "gei_percent", "Tabela principal com scores e níveis de risco"),
    ("gessimples", "gei_cnpj", "Relação CNPJ ↔ Grupo Econômico"),
    ("gessimples", "gei_cadastro", "Dados cadastrais consolidados"),
    ("gessimples", "gei_contador", "Contadores dos grupos"),
    ("gessimples", "gei_socios_compartilhados", "Sócios em múltiplas empresas"),
    ("gessimples", "gei_c115_ranking_risco_grupo_economico", "Ranking de risco C115"),
    ("gessimples", "gei_funcionarios_metricas_grupo", "Métricas RAIS/CAGED"),
    ("gessimples", "gei_pagamentos_metricas_grupo", "Métricas de meios de pagamento"),
    ("gessimples", "gei_c115_metricas_grupos", "Métricas C115 adicionais"),
    ("gessimples", "gei_ccs_metricas_grupo", "Métricas de contas compartilhadas"),
    ("gessimples", "gei_ccs_ranking_risco", "Ranking de risco CCS"),

    # Detalhadas CCS
    ("gessimples", "gei_ccs_cpf_compartilhado", "CPFs com contas em múltiplos CNPJs"),
    ("gessimples", "gei_ccs_sobreposicao_responsaveis", "Responsáveis com períodos sobrepostos"),
    ("gessimples", "gei_ccs_padroes_coordenados", "Eventos coordenados"),

    # Inconsistências
    ("gessimples", "gei_indicios", "Indícios fiscais catalogados"),
    ("gessimples", "gei_nfe_completo", "NFe com inconsistências detectadas"),
    ("gessimples", "gei_pgdas", "Dados PGDAS mensais"),
]


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def criar_diretorios():
    """Cria estrutura de diretórios para os data-schemas."""
    base_dir = Path("data-schemas")
    originais_dir = base_dir / "originais"
    intermediarias_dir = base_dir / "intermediarias"

    originais_dir.mkdir(parents=True, exist_ok=True)
    intermediarias_dir.mkdir(parents=True, exist_ok=True)

    print(f"✅ Diretórios criados:")
    print(f"   - {originais_dir}")
    print(f"   - {intermediarias_dir}")

    return originais_dir, intermediarias_dir


def salvar_resultado(conteudo: str, caminho: Path):
    """Salva o resultado em um arquivo."""
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print(f"   ✅ Salvo: {caminho}")


def processar_tabela(spark, schema: str, tabela: str, descricao: str, diretorio: Path):
    """
    Processa uma tabela: executa DESCRIBE FORMATTED e SELECT LIMIT 10.
    Salva os resultados em arquivos separados.
    """
    tabela_completa = f"{schema}.{tabela}"
    print(f"\n{'='*80}")
    print(f"🔄 Processando: {tabela_completa}")
    print(f"   Descrição: {descricao}")
    print(f"{'='*80}")

    # Nome base do arquivo
    nome_arquivo_base = f"{schema}__{tabela}"

    # =========================================================================
    # 1. DESCRIBE FORMATTED
    # =========================================================================
    try:
        print(f"\n📋 Executando DESCRIBE FORMATTED {tabela_completa}...")
        describe_df = spark.sql(f"DESCRIBE FORMATTED {tabela_completa}")

        # Converte para string formatada
        describe_output = []
        describe_output.append(f"# DESCRIBE FORMATTED: {tabela_completa}\n")
        describe_output.append(f"# Descrição: {descricao}\n")
        describe_output.append(f"# Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        describe_output.append("\n" + "="*80 + "\n\n")

        # Coleta os dados
        rows = describe_df.collect()
        for row in rows:
            linha = " | ".join([str(col) if col is not None else "" for col in row])
            describe_output.append(linha + "\n")

        # Salva o DESCRIBE FORMATTED
        describe_path = diretorio / f"{nome_arquivo_base}__describe.txt"
        salvar_resultado(''.join(describe_output), describe_path)

    except Exception as e:
        print(f"   ❌ ERRO ao executar DESCRIBE FORMATTED: {e}")
        describe_output = [f"ERRO: {e}\n"]
        describe_path = diretorio / f"{nome_arquivo_base}__describe.txt"
        salvar_resultado(''.join(describe_output), describe_path)

    # =========================================================================
    # 2. SELECT * LIMIT 10
    # =========================================================================
    try:
        print(f"\n📊 Executando SELECT * FROM {tabela_completa} LIMIT 10...")
        select_df = spark.sql(f"SELECT * FROM {tabela_completa} LIMIT 10")

        # Converte para string formatada
        select_output = []
        select_output.append(f"# SELECT * FROM {tabela_completa} LIMIT 10\n")
        select_output.append(f"# Descrição: {descricao}\n")
        select_output.append(f"# Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        select_output.append("\n" + "="*80 + "\n\n")

        # Adiciona o schema
        select_output.append("## SCHEMA:\n\n")
        for field in select_df.schema.fields:
            select_output.append(f"{field.name} | {field.dataType} | {field.nullable}\n")

        select_output.append("\n" + "="*80 + "\n\n")
        select_output.append("## DADOS (primeiras 10 linhas):\n\n")

        # Coleta os dados em formato string
        # Usa show() capturado como string
        select_output.append(select_df._jdf.showString(10, 20, False))

        # Salva o SELECT
        select_path = diretorio / f"{nome_arquivo_base}__sample.txt"
        salvar_resultado(''.join(select_output), select_path)

    except Exception as e:
        print(f"   ❌ ERRO ao executar SELECT: {e}")
        select_output = [f"ERRO: {e}\n"]
        select_path = diretorio / f"{nome_arquivo_base}__sample.txt"
        salvar_resultado(''.join(select_output), select_path)

    print(f"\n✅ Tabela {tabela_completa} processada com sucesso!")


# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main(spark):
    """Função principal que processa todas as tabelas."""

    print("\n" + "="*80)
    print("GERADOR DE DATA-SCHEMAS - PROJETO GEI")
    print("="*80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total de tabelas a processar: {len(TABELAS_ORIGINAIS) + len(TABELAS_INTERMEDIARIAS)}")
    print("="*80 + "\n")

    # Cria estrutura de diretórios
    dir_originais, dir_intermediarias = criar_diretorios()

    # Contadores
    total_sucesso = 0
    total_erro = 0

    # =========================================================================
    # Processar TABELAS ORIGINAIS
    # =========================================================================
    print("\n" + "🔵"*40)
    print("PROCESSANDO TABELAS ORIGINAIS (Fontes de Dados)")
    print("🔵"*40 + "\n")

    for schema, tabela, descricao in TABELAS_ORIGINAIS:
        try:
            processar_tabela(spark, schema, tabela, descricao, dir_originais)
            total_sucesso += 1
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao processar {schema}.{tabela}: {e}")
            total_erro += 1

    # =========================================================================
    # Processar TABELAS INTERMEDIÁRIAS
    # =========================================================================
    print("\n" + "🟢"*40)
    print("PROCESSANDO TABELAS INTERMEDIÁRIAS (Tabelas GEI)")
    print("🟢"*40 + "\n")

    for schema, tabela, descricao in TABELAS_INTERMEDIARIAS:
        try:
            processar_tabela(spark, schema, tabela, descricao, dir_intermediarias)
            total_sucesso += 1
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao processar {schema}.{tabela}: {e}")
            total_erro += 1

    # =========================================================================
    # RELATÓRIO FINAL
    # =========================================================================
    print("\n" + "="*80)
    print("RELATÓRIO FINAL")
    print("="*80)
    print(f"✅ Tabelas processadas com sucesso: {total_sucesso}")
    print(f"❌ Tabelas com erro: {total_erro}")
    print(f"📁 Arquivos salvos em: data-schemas/")
    print(f"   - Originais: {len(TABELAS_ORIGINAIS) * 2} arquivos")
    print(f"   - Intermediárias: {len(TABELAS_INTERMEDIARIAS) * 2} arquivos")
    print(f"   - Total: {(len(TABELAS_ORIGINAIS) + len(TABELAS_INTERMEDIARIAS)) * 2} arquivos")
    print(f"\nFim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║                  GERADOR DE DATA-SCHEMAS - GEI                         ║
    ║                                                                        ║
    ║  Este script gera automaticamente a documentação de schema para       ║
    ║  todas as tabelas do projeto GEI (originais e intermediárias).        ║
    ║                                                                        ║
    ║  Para cada tabela, serão gerados 2 arquivos:                          ║
    ║    1. {schema}__{tabela}__describe.txt (DESCRIBE FORMATTED)           ║
    ║    2. {schema}__{tabela}__sample.txt (SELECT * LIMIT 10)              ║
    ║                                                                        ║
    ║  IMPORTANTE: Execute este script em um ambiente com:                  ║
    ║    - Sessão Spark ativa                                               ║
    ║    - Acesso ao banco de dados Impala                                  ║
    ║    - Permissões de leitura nas tabelas                                ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)

    # Verifica se spark está disponível
    try:
        # Opção 1: Se estiver em notebook Jupyter com sessão já criada
        if 'spark' in dir():
            print("✅ Usando sessão Spark existente do notebook.")
            main(spark)

        # Opção 2: Se tiver a função get_session do notebook
        elif 'session' in dir():
            print("✅ Usando session.sparkSession do notebook.")
            spark = session.sparkSession
            main(spark)

        # Opção 3: Criar nova sessão (descomentar e ajustar)
        else:
            print("⚠️  Nenhuma sessão Spark encontrada.")
            print("    Por favor, execute este script em um notebook Jupyter")
            print("    com uma sessão Spark já inicializada, ou descomente")
            print("    o código abaixo para criar uma nova sessão.")
            print("\n    Exemplo de uso no notebook:")
            print("    >>> exec(open('scripts/generate_data_schemas.py').read())")

            # Descomentar para criar nova sessão
            # from utils import spark_utils_session as utils
            # def get_session(profile: str) -> utils.DBASparkAppSession:
            #     app_name = "gei_data_schema_generator"
            #     return (utils.DBASparkAppSession
            #            .builder
            #            .setAppName(app_name)
            #            .usingProcessProfile(profile)
            #            .autoResourceManagement()
            #            .build())
            #
            # session = get_session(profile='efd_t2')
            # spark = session.sparkSession
            # main(spark)

    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        print("\nPor favor, verifique:")
        print("  1. A sessão Spark está ativa?")
        print("  2. Você tem acesso ao banco de dados?")
        print("  3. As bibliotecas necessárias estão instaladas?")
