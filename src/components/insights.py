"""
Módulo de Insights Automáticos e Análises Estatísticas
Gera insights automáticos baseados em análise de dados e regras de negócio
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy import stats
from datetime import datetime

from ..config.settings import NIVEIS_RISCO, formatar_moeda, formatar_numero, formatar_percentual

# =============================================================================
# GERAÇÃO DE INSIGHTS AUTOMÁTICOS
# =============================================================================

def gerar_insights_grupo(dados_grupo: pd.Series, dossie: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    """
    Gera insights automáticos para um grupo específico

    Args:
        dados_grupo: Série com dados principais do grupo
        dossie: Dicionário com dados completos do dossiê

    Returns:
        Lista de dicionários com insights {'tipo': str, 'titulo': str, 'descricao': str, 'severidade': str}
    """
    insights = []

    # Insight 1: Score de Risco
    score = dados_grupo.get('score_final_percent', 0)
    nivel_risco = dados_grupo.get('nivel_risco_final', 'INDETERMINADO')

    if score >= 80:
        insights.append({
            'tipo': 'risco',
            'titulo': '🔴 Grupo de Risco Crítico',
            'descricao': f'Score de risco de {score:.1f}% indica necessidade de investigação urgente. '
                        f'Este grupo apresenta múltiplos indicadores de risco fiscal.',
            'severidade': 'critico'
        })
    elif score >= 60:
        insights.append({
            'tipo': 'risco',
            'titulo': '🟠 Grupo de Alto Risco',
            'descricao': f'Score de risco de {score:.1f}% requer monitoramento próximo e análise detalhada.',
            'severidade': 'alto'
        })

    # Insight 2: Quantidade de CNPJs
    qtd_cnpjs = dados_grupo.get('qtd_cnpjs', 0)
    if qtd_cnpjs >= 10:
        insights.append({
            'tipo': 'estrutura',
            'titulo': '🏢 Grupo Econômico Extenso',
            'descricao': f'Grupo possui {qtd_cnpjs} CNPJs, indicando estrutura organizacional complexa '
                        f'que pode facilitar planejamento tributário abusivo.',
            'severidade': 'medio'
        })

    # Insight 3: Sócios Compartilhados
    socios_comp = dados_grupo.get('socios_compartilhados', 0)
    indice_interconexao = dados_grupo.get('indice_interconexao', 0)

    if socios_comp >= 5 and indice_interconexao >= 0.7:
        insights.append({
            'tipo': 'vinculos',
            'titulo': '👥 Alta Interconexão Societária',
            'descricao': f'{socios_comp} sócios compartilhados com índice de interconexão de {indice_interconexao:.1%}. '
                        f'Forte indício de grupo econômico coordenado.',
            'severidade': 'alto'
        })

    # Insight 4: Dados Cadastrais Idênticos
    razao_identica = dados_grupo.get('razao_social_identica', 0)
    fantasia_identica = dados_grupo.get('fantasia_identica', 0)
    endereco_identico = dados_grupo.get('endereco_identico', 0)

    total_identicos = razao_identica + fantasia_identica + endereco_identico
    if total_identicos >= 2:
        insights.append({
            'tipo': 'cadastro',
            'titulo': '📋 Anomalia Cadastral',
            'descricao': f'Múltiplas empresas compartilham dados cadastrais idênticos '
                        f'(razão social: {razao_identica}, fantasia: {fantasia_identica}, endereço: {endereco_identico}). '
                        f'Possível confusão patrimonial.',
            'severidade': 'alto'
        })

    # Insight 5: Limite Simples Nacional
    acima_limite = dados_grupo.get('acima_limite_sn', 0)
    receita_maxima = dados_grupo.get('receita_maxima', 0)

    if acima_limite > 0 and qtd_cnpjs >= 3:
        insights.append({
            'tipo': 'financeiro',
            'titulo': '💰 Possível Pulverização de Receita',
            'descricao': f'{acima_limite} empresas acima do limite do Simples Nacional com receita máxima de {formatar_moeda(receita_maxima)}. '
                        f'Indício de estratégia para manter-se no regime simplificado.',
            'severidade': 'critico'
        })

    # Insight 6: Convênio 115
    c115_risco = dados_grupo.get('indice_risco_c115', 0)
    c115_nivel = dados_grupo.get('nivel_risco_c115', 'BAIXO')

    if c115_nivel in ['ALTO', 'CRÍTICO']:
        insights.append({
            'tipo': 'c115',
            'titulo': '📊 Risco Elevado no Convênio 115',
            'descricao': f'Índice de risco de {c115_risco:.1%} no Convênio 115. '
                        f'Múltiplos tomadores compartilhados entre empresas do grupo.',
            'severidade': 'alto'
        })

    # Insight 7: Contas Compartilhadas (CCS)
    contas_comp = dados_grupo.get('contas_compartilhadas', 0)
    ccs_risco = dados_grupo.get('indice_risco_ccs', 0)

    if contas_comp >= 3:
        insights.append({
            'tipo': 'ccs',
            'titulo': '🏦 Contas Bancárias Compartilhadas',
            'descricao': f'{contas_comp} contas bancárias compartilhadas entre empresas. '
                        f'Forte indício de confusão patrimonial e movimentação financeira coordenada.',
            'severidade': 'critico'
        })

    # Insight 8: Indícios Fiscais
    total_indicios = dados_grupo.get('total_indicios', 0)

    if total_indicios >= 10:
        insights.append({
            'tipo': 'indicios',
            'titulo': '⚠️ Múltiplos Indícios Fiscais',
            'descricao': f'{total_indicios} indícios fiscais identificados. '
                        f'Padrão consistente sugere coordenação entre empresas.',
            'severidade': 'alto'
        })

    # Insight 9: Inconsistências NFe
    score_nfe = dados_grupo.get('score_inconsistencias_nfe', 0)

    if score_nfe >= 50:
        insights.append({
            'tipo': 'nfe',
            'titulo': '📄 Inconsistências em Notas Fiscais',
            'descricao': f'Score de inconsistências NFe de {score_nfe:.1f} pontos. '
                        f'Dados duplicados ou anômalos em documentos fiscais eletrônicos.',
            'severidade': 'medio'
        })

    # Insight 10: Pagamentos a Sócios
    if not dossie.get('pagamentos', pd.DataFrame()).empty:
        pagamentos_socios = dossie['pagamentos'].get('valor_meios_pagamento_socios', [0])[0]
        if pagamentos_socios > 0:
            insights.append({
                'tipo': 'pagamentos',
                'titulo': '💳 Pagamentos a Sócios Detectados',
                'descricao': f'Valor de {formatar_moeda(pagamentos_socios)} em meios de pagamento vinculados a sócios. '
                            f'Possível confusão entre patrimônio pessoal e empresarial.',
                'severidade': 'medio'
            })

    return insights

def gerar_insights_gerais(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Gera insights sobre o dataset completo

    Args:
        df: DataFrame com dados de todos os grupos

    Returns:
        Lista de insights gerais
    """
    insights = []

    if df.empty:
        return insights

    # Estatísticas gerais
    total_grupos = len(df)
    grupos_criticos = len(df[df['score_final_percent'] >= 80])
    grupos_alto = len(df[(df['score_final_percent'] >= 60) & (df['score_final_percent'] < 80)])
    score_medio = df['score_final_percent'].mean()

    # Insight 1: Distribuição de Risco
    perc_criticos = (grupos_criticos / total_grupos) * 100
    if perc_criticos > 10:
        insights.append({
            'tipo': 'distribuicao',
            'titulo': '📈 Alta Concentração de Grupos Críticos',
            'descricao': f'{perc_criticos:.1f}% dos grupos ({grupos_criticos} de {total_grupos}) '
                        f'apresentam risco crítico. Necessária priorização para fiscalização.',
            'severidade': 'alto'
        })

    # Insight 2: Score Médio
    if score_medio >= 50:
        insights.append({
            'tipo': 'score',
            'titulo': '⚠️ Score Médio Elevado',
            'descricao': f'Score médio de risco de {score_medio:.1f}% indica padrão sistêmico '
                        f'de irregularidades nos grupos econômicos monitorados.',
            'severidade': 'medio'
        })

    # Insight 3: Tendências
    if 'receita_maxima' in df.columns:
        receita_total = df['receita_maxima'].sum()
        insights.append({
            'tipo': 'financeiro',
            'titulo': '💵 Movimentação Financeira Significativa',
            'descricao': f'Receita total agregada de {formatar_moeda(receita_total)} '
                        f'nos grupos monitorados.',
            'severidade': 'info'
        })

    # Insight 4: CNPJs
    if 'qtd_cnpjs' in df.columns:
        total_cnpjs = df['qtd_cnpjs'].sum()
        media_cnpjs = df['qtd_cnpjs'].mean()
        insights.append({
            'tipo': 'estrutura',
            'titulo': '🏢 Abrangência da Base',
            'descricao': f'{formatar_numero(total_cnpjs)} CNPJs monitorados em {total_grupos} grupos. '
                        f'Média de {media_cnpjs:.1f} CNPJs por grupo.',
            'severidade': 'info'
        })

    return insights

# =============================================================================
# ANÁLISES ESTATÍSTICAS AVANÇADAS
# =============================================================================

def calcular_correlacoes(df: pd.DataFrame, colunas: List[str]) -> pd.DataFrame:
    """
    Calcula matriz de correlação entre colunas

    Args:
        df: DataFrame com dados
        colunas: Lista de colunas numéricas

    Returns:
        DataFrame com matriz de correlação
    """
    return df[colunas].corr(method='pearson')

def identificar_outliers(df: pd.DataFrame, coluna: str, metodo: str = 'iqr') -> Tuple[pd.DataFrame, Dict]:
    """
    Identifica outliers em uma coluna

    Args:
        df: DataFrame com dados
        coluna: Nome da coluna
        metodo: 'iqr' (Interquartile Range) ou 'zscore'

    Returns:
        Tupla (DataFrame com outliers, dicionário com estatísticas)
    """
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

def testar_normalidade(df: pd.DataFrame, coluna: str) -> Dict:
    """
    Testa normalidade de distribuição usando Shapiro-Wilk

    Args:
        df: DataFrame com dados
        coluna: Nome da coluna

    Returns:
        Dicionário com resultados do teste
    """
    dados = df[coluna].dropna()

    # Limitar amostra para performance (Shapiro-Wilk limitado a 5000 obs)
    if len(dados) > 5000:
        dados = dados.sample(5000, random_state=42)

    statistic, p_value = stats.shapiro(dados)

    return {
        'teste': 'Shapiro-Wilk',
        'estatistica': statistic,
        'p_valor': p_value,
        'normal': p_value > 0.05,
        'interpretacao': 'Distribuição normal' if p_value > 0.05 else 'Distribuição não-normal'
    }

def calcular_tendencia(df: pd.DataFrame, coluna_x: str, coluna_y: str) -> Dict:
    """
    Calcula tendência linear entre duas variáveis

    Args:
        df: DataFrame com dados
        coluna_x: Coluna para eixo X
        coluna_y: Coluna para eixo Y

    Returns:
        Dicionário com parâmetros da regressão
    """
    df_clean = df[[coluna_x, coluna_y]].dropna()

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df_clean[coluna_x],
        df_clean[coluna_y]
    )

    return {
        'inclinacao': slope,
        'intercepto': intercept,
        'r_squared': r_value ** 2,
        'p_valor': p_value,
        'erro_padrao': std_err,
        'significativo': p_value < 0.05,
        'interpretacao': f"{'Tendência positiva' if slope > 0 else 'Tendência negativa'} "
                        f"{'significativa' if p_value < 0.05 else 'não significativa'}"
    }

def segmentar_grupos(df: pd.DataFrame, coluna: str, n_bins: int = 4) -> Tuple[pd.DataFrame, List[str]]:
    """
    Segmenta dados em grupos (quartis, decis, etc.)

    Args:
        df: DataFrame com dados
        coluna: Coluna para segmentar
        n_bins: Número de segmentos

    Returns:
        Tupla (DataFrame com coluna de segmento, lista de labels)
    """
    df_seg = df.copy()

    labels = [f'Segmento {i+1}' for i in range(n_bins)]

    df_seg[f'{coluna}_segmento'] = pd.qcut(
        df_seg[coluna],
        q=n_bins,
        labels=labels,
        duplicates='drop'
    )

    return df_seg, labels

def calcular_metricas_comparativas(df: pd.DataFrame, coluna_grupo: str, coluna_metrica: str) -> pd.DataFrame:
    """
    Calcula métricas comparativas entre grupos

    Args:
        df: DataFrame com dados
        coluna_grupo: Coluna de agrupamento
        coluna_metrica: Coluna da métrica a comparar

    Returns:
        DataFrame com métricas comparativas
    """
    resultado = df.groupby(coluna_grupo)[coluna_metrica].agg([
        ('media', 'mean'),
        ('mediana', 'median'),
        ('desvio_padrao', 'std'),
        ('minimo', 'min'),
        ('maximo', 'max'),
        ('q1', lambda x: x.quantile(0.25)),
        ('q3', lambda x: x.quantile(0.75)),
        ('contagem', 'count')
    ]).reset_index()

    # Adicionar ranking
    resultado['ranking'] = resultado['media'].rank(ascending=False)

    # Adicionar percentil vs média geral
    media_geral = df[coluna_metrica].mean()
    resultado['vs_media_geral'] = ((resultado['media'] / media_geral) - 1) * 100

    return resultado

# =============================================================================
# ANÁLISE DE PADRÕES TEMPORAIS
# =============================================================================

def detectar_sazonalidade(df: pd.DataFrame, coluna_data: str, coluna_valor: str) -> Dict:
    """
    Detecta padrões sazonais em série temporal

    Args:
        df: DataFrame com dados
        coluna_data: Coluna com datas
        coluna_valor: Coluna com valores

    Returns:
        Dicionário com análise de sazonalidade
    """
    df_temp = df.copy()
    df_temp[coluna_data] = pd.to_datetime(df_temp[coluna_data])
    df_temp = df_temp.sort_values(coluna_data)

    # Agrupar por mês
    df_temp['mes'] = df_temp[coluna_data].dt.month
    df_temp['ano'] = df_temp[coluna_data].dt.year

    media_por_mes = df_temp.groupby('mes')[coluna_valor].mean()

    return {
        'media_por_mes': media_por_mes.to_dict(),
        'mes_maior': int(media_por_mes.idxmax()),
        'mes_menor': int(media_por_mes.idxmin()),
        'variacao': ((media_por_mes.max() - media_por_mes.min()) / media_por_mes.mean()) * 100
    }

# =============================================================================
# FORMATAÇÃO DE INSIGHTS PARA EXIBIÇÃO
# =============================================================================

def formatar_insight_html(insight: Dict) -> str:
    """
    Formata insight como HTML para exibição

    Args:
        insight: Dicionário com dados do insight

    Returns:
        String HTML formatada
    """
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
    """
    Exibe lista de insights formatados

    Args:
        insights: Lista de insights
    """
    if not insights:
        st.info("ℹ️ Nenhum insight específico identificado para este grupo.")
        return

    st.markdown("### 💡 Insights Automáticos")

    for insight in insights:
        st.markdown(formatar_insight_html(insight), unsafe_allow_html=True)
